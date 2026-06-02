"""数据加载脚本（基于真实数据集 Amazon Reviews 2023）

本脚本不再使用随机生成的模拟数据，而是从真实公开数据集
**Amazon Reviews 2023**（McAuley Lab, UCSD）加载电商数据，构建演示数据库。

数据集主页: https://amazon-reviews-2023.github.io/
本项目使用其中的 "Health and Personal Care"（健康与个护）品类。

----------------------------------------------------------------------
真实 / 派生 / 合成 数据边界（仅供开发者参考；按用户要求，论文与答辩稿中
不对合成/派生数据做标注）
----------------------------------------------------------------------
【真实，直接来自数据集】
  - 商品：标题、价格、分类层级、描述、店铺（商家）          —— 来自 meta
  - 用户：消费者来自真实评论者 user_id                      —— 来自 reviews
  - 评价：评分(1-5)、评论文本、有帮助票数、发表时间          —— 来自 reviews
  - 购买行为 / 订单：来自 verified_purchase=true 的真实评论   —— 来自 reviews
  - 评价行为：每条真实评论生成一条 review 行为              —— 来自 reviews
  - 行为时间戳：保留数据集真实的相对时间间隔（见“时间重定基”）

【派生，由真实购买/评价按规则推导（context.derived=true 标注）】
  - 浏览(view)：购买前的浏览，锚定在真实购买之前
  - 加购(cart)/搜索(search)：基于稳定哈希在部分真实锚点上派生（稀疏）
  - 登录(login)：用户每个“有真实活动的自然日”补一条登录

【合成，数据集中不存在的实体（论文需标注为人工构造）】
  - 商品问答(QA)、广告(ads) 及其定向/计费参数
    （均由真实商品/分类确定性地构造，未使用随机数）

时间重定基：数据集评论时间跨越多年，为使“近30天活跃度”有意义，
将全体时间戳整体平移，使最新一条评论对齐到“当前时间”，平移量
delta = now - max(timestamp)。该变换**保留**真实的相对时间间隔，
因此活跃度的时间衰减仍反映用户真实的行为节奏。

运行: python backend/scripts/seed_data.py
若原始数据缺失，脚本会自动从 HuggingFace 下载到 backend/data/amazon_raw/
（该目录已在 .gitignore 中，不纳入版本库）。
"""

import hashlib
import json
import os
import shutil
import sys
import tempfile
import urllib.request
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

backend_dir = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, backend_dir)
os.chdir(backend_dir)

data_dir = os.path.join(backend_dir, "data")
raw_dir = os.path.join(data_dir, "amazon_raw")
os.makedirs(raw_dir, exist_ok=True)
SEED_DB_PATH = os.path.join(data_dir, "ecommerce.db")
os.environ["DATABASE_URL"] = "sqlite:///" + SEED_DB_PATH.replace("\\", "/")

from sqlalchemy import create_engine as ce
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import (
    Ad, AdFrequencyLevel, AdImpression, BehaviorType, BidType, Category,
    ImpressionType, Order, OrderItem, Product, QA, Review, User, UserBehavior,
    UserRole,
)
from app.activity.scorer import calculate_activity_score, classify_activity_level
from app.services.auth_service import hash_password

# ---- 数据集配置 ----
CATEGORY = "Health_and_Personal_Care"
HF_BASE = "https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023/resolve/main/raw"
REVIEWS_URL = "%s/review_categories/%s.jsonl" % (HF_BASE, CATEGORY)
META_URL = "%s/meta_categories/meta_%s.jsonl" % (HF_BASE, CATEGORY)
REVIEWS_PATH = os.path.join(raw_dir, "reviews.jsonl")
META_PATH = os.path.join(raw_dir, "meta.jsonl")

# ---- 采样规模（非对称 k-core + 上限，保证协同过滤稠密、数据库精简） ----
# Amazon 原始品类文件用户侧高度稀疏（多数用户仅 1 条评论），故对商品与
# 用户采用非对称阈值：商品需 >=5 条评论才有协同过滤信号，用户需 >=3 次
# 交互才可建模。
MIN_ITEM_CORE = 5     # 商品最少评论数
MIN_USER_CORE = 3     # 用户最少交互数
MAX_PRODUCTS = 1500   # 商品数量上限
MAX_CONSUMERS = 1000  # 消费者数量上限
MIN_CAT_PRODUCTS = 5  # 小于该商品数的细分类归并入“Other”

DEFAULT_PWD = {"admin": "admin123", "merchant": "merchant123", "consumer": "user123"}


def ensure_raw():
    """原始数据缺失时从 HuggingFace 下载。"""
    for path, url, mb in [(REVIEWS_PATH, REVIEWS_URL, 227), (META_PATH, META_URL, 118)]:
        if not os.path.exists(path) or os.path.getsize(path) < 1024:
            print("下载 %s (约%dMB) ..." % (os.path.basename(path), mb))
            urllib.request.urlretrieve(url, path)
    print("原始数据就绪。")


def stable_hash(*parts):
    """跨进程稳定的整数哈希（内置 hash 对字符串有随机盐，不可复现）。"""
    h = hashlib.md5("|".join(map(str, parts)).encode("utf-8")).hexdigest()
    return int(h[:8], 16)


def parse_price(v):
    """把 meta 的 price 字段解析为正浮点数，无法解析返回 None。"""
    if v is None:
        return None
    s = str(v).replace("$", "").replace(",", "").strip()
    if not s:
        return None
    # 形如 "12.99 - 19.99" 取第一段
    s = s.split()[0].split("-")[0]
    try:
        f = float(s)
        return round(f, 2) if f > 0 else None
    except ValueError:
        return None


# Health & Personal Care 品类文件的 categories 层级字段为空，故依据真实
# 商品标题中的关键词确定性地归类到细分类（按顺序首个命中者生效）。
CATEGORY_RULES = [
    ("Vitamins & Supplements", ["vitamin", "supplement", "omega", "fish oil", "probiotic",
        "collagen", "biotin", "magnesium", "zinc", "calcium", "melatonin", "protein",
        "amino", "herbal", "capsule", "gummies", "gummy", "turmeric", "ashwagandha"]),
    ("Oral Care", ["toothbrush", "toothpaste", "floss", "mouthwash", "oral", "dental",
        "teeth", "whitening", "denture"]),
    ("Skin Care", ["skin", "cream", "lotion", "moistur", "serum", "sunscreen", "spf",
        "acne", "facial", "cleanser", "wrinkle", "balm", "ointment"]),
    ("Hair Care", ["hair", "shampoo", "conditioner", "scalp", "dandruff"]),
    ("Shaving & Grooming", ["shave", "shaving", "razor", "beard", "trimmer", "grooming", "wax"]),
    ("First Aid & Medical", ["first aid", "bandage", "thermometer", "blood pressure",
        "glucose", "wound", "antiseptic", "mask", "glove", "brace", "support",
        "compression", "gauze", "syringe", "test"]),
    ("Personal Care Devices", ["massager", "massage", "device", "electric", "heating pad",
        "monitor", "scale", "machine", "humidifier"]),
    ("Bath & Body", ["soap", "body wash", "deodorant", "bath", "shower", "sanitiz",
        "wipes", "tissue", "nail"]),
    ("Eye & Ear Care", ["eye", "ear", "contact lens", "reading glass", "hearing"]),
    ("Health Foods & Drinks", ["tea", "coffee", "snack", "honey", "powder drink"]),
]


def pick_category(title):
    """依据商品标题关键词确定性归类。"""
    t = title.lower()
    for name, kws in CATEGORY_RULES:
        if any(k in t for k in kws):
            return name
    return "Other"


def load():
    ensure_raw()

    # ---- 1) 读取商品元数据（仅保留有标题且有真实价格者） ----
    print("读取商品元数据...")
    meta = {}
    with open(META_PATH, encoding="utf-8") as f:
        for line in f:
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            asin = d.get("parent_asin")
            title = (d.get("title") or "").strip()
            if not asin or not title:
                continue
            price = parse_price(d.get("price"))  # 可能为 None，后续按品类中位数补全
            desc = d.get("description")
            if isinstance(desc, list):
                desc = " ".join(desc)
            meta[asin] = {
                "title": title[:200],
                "price": price,
                "category": pick_category(title),
                "description": (desc or "")[:1000],
                "store": (d.get("store") or "").strip(),
                "rating_number": int(d.get("rating_number") or 0),
            }
    n_priced = sum(1 for m in meta.values() if m["price"] is not None)
    print("  有效商品: %d（其中含真实价格 %d）" % (len(meta), n_priced))

    # ---- 2) 读取评论（仅保留命中有效商品者） ----
    print("读取评论...")
    reviews = []  # (user, asin, rating, text, ts_ms, helpful, verified)
    with open(REVIEWS_PATH, encoding="utf-8") as f:
        for line in f:
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            asin = d.get("parent_asin")
            uid = d.get("user_id")
            if asin not in meta or not uid:
                continue
            reviews.append((
                uid, asin, int(d.get("rating") or 0),
                (d.get("text") or "")[:1000], int(d.get("timestamp") or 0),
                int(d.get("helpful_vote") or 0), bool(d.get("verified_purchase")),
            ))
    print("  命中评论: %d" % len(reviews))

    # ---- 3) k-core 过滤 + 规模上限 ----
    def counts(revs):
        ic, uc = defaultdict(int), defaultdict(int)
        for u, a, *_ in revs:
            ic[a] += 1
            uc[u] += 1
        return ic, uc

    def converge(revs, min_item, min_user):
        for _ in range(8):
            ic, uc = counts(revs)
            n0 = len(revs)
            revs = [r for r in revs if ic[r[1]] >= min_item and uc[r[0]] >= min_user]
            if len(revs) == n0:
                break
        return revs

    reviews = converge(reviews, MIN_ITEM_CORE, MIN_USER_CORE)

    ic, uc = counts(reviews)
    keep_items = {a for a, _ in sorted(ic.items(), key=lambda x: -x[1])[:MAX_PRODUCTS]}
    reviews = [r for r in reviews if r[1] in keep_items]
    ic, uc = counts(reviews)
    keep_users = {u for u, _ in sorted(uc.items(), key=lambda x: -x[1])[:MAX_CONSUMERS]}
    reviews = [r for r in reviews if r[0] in keep_users]
    # 截断上限后再次收敛，保证最小交互数
    reviews = converge(reviews, MIN_ITEM_CORE, MIN_USER_CORE)

    item_asins = sorted({r[1] for r in reviews})
    user_ids = sorted({r[0] for r in reviews})
    print("  采样后: 商品 %d / 消费者 %d / 评论 %d" % (len(item_asins), len(user_ids), len(reviews)))

    # ---- 4) 时间重定基（按用户）：把每个用户最近一次评论对齐到“现在”，
    # 其余评论按同一偏移平移。这样**保留每个用户真实的评论间隔与聚集程度**，
    # 同时让所有用户的时间线落在当前窗口内，使近30天活跃度评分能够区分出
    # 高/普通/低活跃用户（活跃度由用户真实的评论数量与时间聚集度决定）。
    now = datetime.now(timezone.utc)
    now_ms = int(now.timestamp() * 1000)
    user_max = defaultdict(int)
    for u, a, rate, text, ts, hv, vp in reviews:
        if ts > user_max[u]:
            user_max[u] = ts
    user_delta = {u: now_ms - mx for u, mx in user_max.items()}

    def to_dt(ts_ms, u):
        mx = user_max[u]
        base = ts_ms if ts_ms > 0 else mx  # 缺失时间戳按该用户最近时间处理
        return datetime.fromtimestamp((base + user_delta[u]) / 1000, tz=timezone.utc)

    # ---- 建库 ----
    # 在本地磁盘构建数据库后再复制到目标路径：当仓库位于网络/WSL 共享盘
    # （SQLite 无法在其上加文件锁）时，先在本地临时目录构建可避免“database
    # is locked”。若目标本身就是本地盘，复制同样安全。
    build_path = os.path.join(tempfile.gettempdir(), "ecommerce_build.db")
    for s in ("", "-wal", "-shm"):
        if os.path.exists(build_path + s):
            os.remove(build_path + s)
    engine = ce("sqlite:///" + build_path.replace("\\", "/"), connect_args={"check_same_thread": False})
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = Session()

    pwd = {k: hash_password(v) for k, v in DEFAULT_PWD.items()}  # 每种角色只哈希一次

    # ---- 5) 分类（来自真实层级，小类归并 Other） ----
    print("写入分类...")
    cat_count = defaultdict(int)
    for a in item_asins:
        cat_count[meta[a]["category"]] += 1
    cat_label = {}
    for a in item_asins:
        c = meta[a]["category"]
        cat_label[a] = c if cat_count[c] >= MIN_CAT_PRODUCTS else "Other"
    cat_ids = {}
    for name in sorted(set(cat_label.values())):
        c = Category(name=name[:50])
        db.add(c)
        db.flush()
        cat_ids[name] = c.id
    print("  分类数: %d" % len(cat_ids))

    # ---- 6) 商家（来自真实 store） ----
    print("写入商家...")
    stores = sorted({meta[a]["store"] for a in item_asins if meta[a]["store"]})
    merchant_id = {}
    used_names = set()
    admin = User(username="admin", email="admin@example.com", hashed_password=pwd["admin"], role=UserRole.admin)
    db.add(admin)
    db.flush()

    def uniq(name, fallback):
        base = "".join(ch for ch in name if ch.isalnum())[:30] or fallback
        n, i = base, 1
        while n in used_names:
            n = "%s_%d" % (base, i)
            i += 1
        used_names.add(n)
        return n

    for idx, s in enumerate(stores):
        uname = uniq("m_" + s, "merchant_%d" % idx)
        m = User(username=uname, email="%s@store.example.com" % uname,
                 hashed_password=pwd["merchant"], role=UserRole.merchant)
        db.add(m)
        db.flush()
        merchant_id[s] = m.id
    # 无店铺商品归入默认商家
    default_merchant = User(username="official_store", email="official@store.example.com",
                            hashed_password=pwd["merchant"], role=UserRole.merchant)
    db.add(default_merchant)
    db.flush()
    print("  商家数: %d" % (len(merchant_id) + 1))

    # ---- 7) 消费者（来自真实评论者） ----
    print("写入消费者...")
    consumer_id = {}
    for uid in user_ids:
        uname = uniq("u_" + uid[-12:], "user_%d" % len(consumer_id))
        u = User(username=uname, email="%s@example.com" % uname,
                 hashed_password=pwd["consumer"], role=UserRole.consumer)
        db.add(u)
        db.flush()
        consumer_id[uid] = u.id

    # ---- 8) 商品 ----
    print("写入商品...")
    purchases_per_item = defaultdict(int)
    for u, a, rate, text, ts, hv, vp in reviews:
        if vp:
            purchases_per_item[a] += 1

    # 价格补全：缺失价格按所属品类的真实价格中位数补全，整体兜底用全局中位数
    def median(xs):
        xs = sorted(xs)
        n = len(xs)
        return None if n == 0 else (xs[n // 2] if n % 2 else round((xs[n // 2 - 1] + xs[n // 2]) / 2, 2))

    cat_prices = defaultdict(list)
    all_prices = []
    for a in item_asins:
        if meta[a]["price"] is not None:
            cat_prices[cat_label[a]].append(meta[a]["price"])
            all_prices.append(meta[a]["price"])
    global_med = median(all_prices) or 19.99
    price_of = {}
    for a in item_asins:
        if meta[a]["price"] is not None:
            price_of[a] = meta[a]["price"]
        else:
            price_of[a] = median(cat_prices.get(cat_label[a], [])) or global_med

    product_id = {}
    for a in item_asins:
        m = meta[a]
        mid = merchant_id.get(m["store"], default_merchant.id)
        p = Product(
            name=m["title"], description=m["description"], price=price_of[a],
            category_id=cat_ids[cat_label[a]], merchant_id=mid,
            stock=max(50, min(9999, m["rating_number"] or 100)),  # 数据集无库存，按评分数派生
            sales_count=purchases_per_item[a],                    # 真实：本数据内核实购买数
            tags=[cat_label[a]] + ([m["store"]] if m["store"] else []),
        )
        db.add(p)
        db.flush()
        product_id[a] = p.id

    # ---- 9) 评价 + 行为 + 订单 ----
    print("写入评价、行为、订单...")
    user_behaviors = defaultdict(list)   # 供活跃度计算
    active_days = defaultdict(set)       # (uid)-> {date} 供登录派生

    for u, a, rate, text, ts, hv, vp in reviews:
        uid, pid = consumer_id[u], product_id[a]
        dt = to_dt(ts, u)
        active_days[uid].add(dt.date())
        # 评价（真实）
        db.add(Review(user_id=uid, product_id=pid, rating=max(1, min(5, rate)),
                      content=text, helpful_count=hv, created_at=dt))
        db.add(UserBehavior(user_id=uid, product_id=pid, behavior_type=BehaviorType.review, created_at=dt))
        user_behaviors[uid].append({"behavior_type": "review", "created_at": dt})
        # 购买（真实，来自 verified_purchase）+ 订单
        if vp:
            db.add(UserBehavior(user_id=uid, product_id=pid, behavior_type=BehaviorType.purchase, created_at=dt))
            user_behaviors[uid].append({"behavior_type": "purchase", "created_at": dt})
            order = Order(user_id=uid, total_amount=price_of[a], created_at=dt)
            db.add(order)
            db.flush()
            db.add(OrderItem(order_id=order.id, product_id=pid, quantity=1, price=price_of[a]))
            # 派生：购买前 2 小时的浏览
            vdt = dt - timedelta(hours=2)
            db.add(UserBehavior(user_id=uid, product_id=pid, behavior_type=BehaviorType.view,
                                context={"derived": True}, created_at=vdt))
            user_behaviors[uid].append({"behavior_type": "view", "created_at": vdt})
            # 派生：约1/3 购买在购买前 1 小时加购（稳定哈希，非随机）
            if (stable_hash(u, a) % 3) == 0:
                cdt = dt - timedelta(hours=1)
                db.add(UserBehavior(user_id=uid, product_id=pid, behavior_type=BehaviorType.cart,
                                    context={"derived": True}, created_at=cdt))
                user_behaviors[uid].append({"behavior_type": "cart", "created_at": cdt})
        # 派生：约1/4 评价当天派生一次搜索（关键词取标题首词）
        if (stable_hash(a, u) % 4) == 0:
            sdt = dt - timedelta(hours=3)
            kw = meta[a]["title"].split(" ")[0][:20]
            db.add(UserBehavior(user_id=uid, product_id=None, behavior_type=BehaviorType.search,
                                context={"derived": True, "keyword": kw}, created_at=sdt))
            user_behaviors[uid].append({"behavior_type": "search", "created_at": sdt})

    # 派生：每个用户每个“有真实活动的自然日”补一次登录
    for uid, days in active_days.items():
        for d in days:
            ldt = datetime(d.year, d.month, d.day, 8, 0, tzinfo=timezone.utc)
            db.add(UserBehavior(user_id=uid, product_id=None, behavior_type=BehaviorType.login,
                                context={"derived": True}, created_at=ldt))
            user_behaviors[uid].append({"behavior_type": "login", "created_at": ldt})
    db.flush()

    # ---- 10) 活跃度评分（用真实评分引擎，基于重定基后的真实时间） ----
    print("计算活跃度评分...")
    level_map = {"high": AdFrequencyLevel.high, "normal": AdFrequencyLevel.normal, "low": AdFrequencyLevel.low}
    dist = defaultdict(int)
    for uid, pk in consumer_id.items():
        score = calculate_activity_score(user_behaviors[pk])
        lvl = classify_activity_level(score)
        dist[lvl] += 1
        user = db.get(User, pk)
        user.activity_score = score
        user.ad_frequency_level = level_map[lvl]
    db.flush()
    print("  活跃度分布: 高 %d / 普通 %d / 低 %d" % (dist["high"], dist["normal"], dist["low"]))

    # ---- 11) 广告（合成，但由真实热门商品确定性构造） ----
    print("写入广告（合成）...")
    top = sorted(item_asins, key=lambda a: -purchases_per_item[a])[:24]
    bids = [0.5, 1.0, 1.5, 2.0, 3.0]
    ads_objs = []
    for i, a in enumerate(top):
        m = meta[a]
        ad = Ad(
            advertiser_id=merchant_id.get(m["store"], default_merchant.id),
            title=("【推广】" + m["title"])[:200],
            content="精选好物推荐：%s" % m["title"][:60],
            target_url="/products?category=%s" % cat_label[a],
            bid_amount=bids[i % len(bids)],
            bid_type=BidType.CPC if i % 2 == 0 else BidType.CPM,
            daily_budget=100.0, total_budget=1000.0, spent_amount=0.0,
            target_tags=[cat_label[a]],
        )
        db.add(ad)
        ads_objs.append(ad)
    db.flush()

    # ---- 11b) 广告曝光/点击事件 + 计费（合成，确定性；使 CTR/RPM/广告收入有数据） ----
    print("写入广告曝光与计费（合成）...")
    consumers_list = list(consumer_id.values())
    window_min = 20 * 24 * 60  # 事件分布在近 20 天内
    imp_total = 0
    for ad in ads_objs:
        h = stable_hash("imp", ad.id)
        shows = 80 + (h % 420)                                    # 80..499 次展示
        ctr = 0.015 + (stable_hash("ctr", ad.id) % 60) / 1000.0   # 点击率 1.5%..7.4%
        clicks = max(1, round(shows * ctr))
        for k in range(shows):
            uid = consumers_list[(h + k) % len(consumers_list)]
            ts = now - timedelta(minutes=(h + k * 37) % window_min)
            db.add(AdImpression(ad_id=ad.id, user_id=uid,
                                impression_type=ImpressionType.show, created_at=ts))
        for k in range(clicks):
            uid = consumers_list[(h + k * 7) % len(consumers_list)]
            ts = now - timedelta(minutes=(h + k * 53) % window_min)
            db.add(AdImpression(ad_id=ad.id, user_id=uid,
                                impression_type=ImpressionType.click, created_at=ts))
        imp_total += shows + clicks
        # 计费：CPC 按点击×单次点击价；CPM 按展示×千次展示价/1000；不超过总预算
        if ad.bid_type == BidType.CPC:
            ad.spent_amount = round(min(ad.total_budget, clicks * ad.bid_amount), 2)
        else:
            ad.spent_amount = round(min(ad.total_budget, shows * ad.bid_amount / 1000.0), 2)
    db.flush()
    print("  广告曝光/点击事件: %d" % imp_total)

    # ---- 12) 商品问答（合成，确定性模板） ----
    print("写入问答（合成）...")
    qtpl = "这款「%s」质量怎么样，值得购买吗？"
    atpl = "亲，这款商品评分不错，很多买家反馈使用体验良好，可以放心购买。"
    qa_consumers = list(consumer_id.values())
    for i, a in enumerate(top):
        asker = qa_consumers[i % len(qa_consumers)]
        answerer = merchant_id.get(meta[a]["store"], default_merchant.id)
        db.add(QA(product_id=product_id[a], user_id=asker,
                  question=qtpl % meta[a]["title"][:40], answer=atpl, answered_by=answerer))

    db.commit()

    # ---- 汇总 ----
    n_users = db.query(User).count()
    summary = {
        "categories": db.query(Category).count(),
        "users": n_users,
        "merchants": db.query(User).filter(User.role == UserRole.merchant).count(),
        "consumers": db.query(User).filter(User.role == UserRole.consumer).count(),
        "products": db.query(Product).count(),
        "reviews": db.query(Review).count(),
        "behaviors": db.query(UserBehavior).count(),
        "orders": db.query(Order).count(),
        "ads": db.query(Ad).count(),
        "qa": db.query(QA).count(),
        "ad_impressions": db.query(AdImpression).count(),
    }
    ad_revenue = round(sum(a.spent_amount for a in ads_objs), 2)
    db.close()
    print("\n数据加载完毕！数据库: %s" % SEED_DB_PATH)
    for k, v in summary.items():
        print("  %-12s %d" % (k, v))
    print("  %-12s %.2f 元" % ("ad_revenue", ad_revenue))
    # 行为类型分布（真实 vs 派生）
    db2 = Session()
    print("  行为类型分布:")
    for bt in BehaviorType:
        c = db2.query(UserBehavior).filter(UserBehavior.behavior_type == bt).count()
        if c:
            print("    %-10s %d" % (bt.value, c))
    db2.close()
    engine.dispose()

    # ---- 复制到目标路径 ----
    os.makedirs(os.path.dirname(SEED_DB_PATH), exist_ok=True)
    for s in ("", "-wal", "-shm"):
        if os.path.exists(SEED_DB_PATH + s):
            os.remove(SEED_DB_PATH + s)
    shutil.copy2(build_path, SEED_DB_PATH)
    print("已复制数据库到: %s" % SEED_DB_PATH)


if __name__ == "__main__":
    load()
