"""种子数据生成脚本

自动生成测试用的模拟数据，包括用户、分类、商品、行为日志、评价、订单和广告。
用于开发和测试环境的数据初始化，运行后会创建包含完整示例数据的SQLite数据库。
"""

import os
import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# 将项目根目录加入Python路径，确保可以导入app模块
backend_dir = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, backend_dir)
os.chdir(backend_dir)

# 创建数据目录并设置数据库路径
data_dir = os.path.join(backend_dir, "data")
os.makedirs(data_dir, exist_ok=True)
SEED_DB_PATH = os.path.join(data_dir, "ecommerce.db")
os.environ["DATABASE_URL"] = "sqlite:///" + SEED_DB_PATH.replace("\\", "/")

from app.database import Base, engine
from sqlalchemy.orm import sessionmaker

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
from app.models import (
    Ad, AdFrequencyLevel, BehaviorType, BidType, Category,
    Order, OrderItem, Product, Review, User, UserBehavior, UserRole,
)
from app.services.auth_service import hash_password

# 商品分类列表（10个一级分类）
CATEGORIES = ["电子产品", "服装鞋帽", "图书音像", "家居家装", "食品饮料", "运动户外", "玩具母婴", "美妆个护", "汽车用品", "园艺花卉"]

# 商品名称修饰词（与品类名词组合生成商品名）
PRODUCT_ADJECTIVES = ["精选", "经典", "豪华", "简约", "智能", "复古", "时尚", "环保", "专业", "旗舰"]

# 各分类下的商品名词，每个分类10个
PRODUCT_NOUNS = {
    "电子产品": ["手机", "笔记本电脑", "平板电脑", "耳机", "相机", "音箱", "智能手表", "显示器", "键盘", "鼠标"],
    "服装鞋帽": ["T恤", "牛仔裤", "夹克", "连衣裙", "运动鞋", "帽子", "围巾", "手套", "袜子", "皮带"],
    "图书音像": ["小说", "教材", "菜谱", "传记", "指南", "手册", "漫画", "词典", "地图册", "日记本"],
    "家居家装": ["台灯", "椅子", "桌子", "地毯", "抱枕", "窗帘", "书架", "时钟", "花瓶", "镜子"],
    "食品饮料": ["咖啡", "茶叶", "巧克力", "坚果", "麦片", "意面", "酱料", "香料", "蜂蜜", "果酱"],
    "运动户外": ["篮球", "球拍", "瑜伽垫", "哑铃", "水壶", "运动包", "跑鞋", "运动手套", "球衣", "运动帽"],
    "玩具母婴": ["拼图", "桌游", "玩偶", "遥控车", "积木", "机器人", "风筝", "溜溜球", "手办", "毛绒玩具"],
    "美妆个护": ["面霜", "精华液", "洗发水", "口红", "香水", "面膜", "乳液", "护发油", "香皂", "化妆刷"],
    "汽车用品": ["车载充电器", "手机支架", "座椅套", "清洁剂", "工具箱", "车灯", "行车记录仪", "香薰", "脚垫", "收纳箱"],
    "园艺花卉": ["种子", "花盆", "铲子", "水管", "园艺手套", "太阳能灯", "围栏", "营养土", "肥料", "洒水器"],
}

# 评价模板，随机选取作为商品评价内容
REVIEW_TEMPLATES = [
    "非常好的产品，正是我需要的！",
    "性价比很高，质量不错。",
    "一般般，还有改进空间。",
    "和预期不太一样，有点失望。",
    "太棒了！还会回购的。",
    "中规中矩，没什么特别的。",
    "包装有点破损，物流需要改进。",
    "爱了爱了！强烈推荐给大家。",
    "使用效果不错，发货也快。",
    "还可以吧，价格公道。",
    "做工精细，手感很好，超出预期。",
    "买给家人的，他们很喜欢。",
    "第二次购买了，一如既往的好。",
    "颜色比图片稍深一点，但总体满意。",
    "客服态度很好，问题解决得很快。",
]


def seed():
    """生成全部种子数据的主函数

    执行流程：删除旧数据库 -> 建表 -> 依次生成分类、用户、商品、行为、评价、订单、广告。
    """
    # 如果已有数据库文件，先删除以确保数据干净
    if os.path.exists(SEED_DB_PATH):
        os.remove(SEED_DB_PATH)
    from sqlalchemy import create_engine as ce
    fresh_engine = ce("sqlite:///" + SEED_DB_PATH.replace("\\", "/"), connect_args={"check_same_thread": False})
    FreshSession = sessionmaker(autocommit=False, autoflush=False, bind=fresh_engine)
    Base.metadata.create_all(bind=fresh_engine)  # 创建所有表
    db = FreshSession()

    # ---- 生成分类（10个一级分类） ----
    print("正在生成分类...")
    cats = {}
    for name in CATEGORIES:
        cat = Category(name=name)
        db.add(cat)
        db.flush()
        cats[name] = cat.id

    # ---- 生成用户（1个管理员 + 10个商家 + 89个消费者 = 100个用户） ----
    print("正在生成用户 (100)...")
    users = []
    admin = User(username="admin", email="admin@example.com", hashed_password=hash_password("admin123"), role=UserRole.admin)
    db.add(admin)
    users.append(admin)

    for i in range(10):
        merchant = User(
            username="merchant_%d" % i, email="merchant_%d@example.com" % i,
            hashed_password=hash_password("merchant123"), role=UserRole.merchant,
        )
        db.add(merchant)
        users.append(merchant)

    for i in range(89):
        consumer = User(
            username="user_%d" % i, email="user_%d@example.com" % i,
            hashed_password=hash_password("user123"), role=UserRole.consumer,
            activity_score=random.uniform(0, 100),  # 随机初始活跃度
            ad_frequency_level=random.choice(list(AdFrequencyLevel)),  # 随机频控等级
        )
        db.add(consumer)
        users.append(consumer)
    db.flush()

    merchants = [u for u in users if u.role == UserRole.merchant]   # 商家列表
    consumers = [u for u in users if u.role == UserRole.consumer]   # 消费者列表

    # ---- 生成商品（10分类 x 10修饰词 x 10名词 = 1000件商品） ----
    print("正在生成商品 (1000+)...")
    products = []
    for cat_name, cat_id in cats.items():
        nouns = PRODUCT_NOUNS[cat_name]
        for adj in PRODUCT_ADJECTIVES:
            for noun in nouns:
                p = Product(
                    name="%s%s" % (adj, noun),
                    description="一款%s%s，属于%s品类，品质优良，值得购买。" % (adj, noun, cat_name),
                    price=round(random.uniform(9.9, 2999.0), 2),  # 随机价格
                    category_id=cat_id,
                    merchant_id=random.choice(merchants).id,       # 随机分配商家
                    stock=random.randint(10, 500),                 # 随机库存
                    sales_count=random.randint(0, 500),            # 随机销量
                    tags=[cat_name, adj, noun],                    # 标签：分类+修饰词+名词
                )
                db.add(p)
                products.append(p)
    db.flush()
    print("  已创建 %d 件商品" % len(products))

    # ---- 生成用户行为日志（12000条，按权重分配行为类型） ----
    print("正在生成用户行为 (12000+)...")
    now = datetime.now(timezone.utc)
    behavior_types = [BehaviorType.view, BehaviorType.click, BehaviorType.cart, BehaviorType.purchase, BehaviorType.search]
    for _ in range(12000):
        user = random.choice(consumers)
        product = random.choice(products)
        # 行为类型权重：浏览40%、点击25%、加购15%、购买10%、搜索10%
        btype = random.choices(behavior_types, weights=[40, 25, 15, 10, 10])[0]
        days_ago = random.uniform(0, 30)  # 最近30天内的随机时间
        db.add(UserBehavior(
            user_id=user.id, product_id=product.id, behavior_type=btype,
            created_at=now - timedelta(days=days_ago),
        ))
    db.flush()

    # ---- 生成商品评价（600条，随机评分和评价内容） ----
    print("正在生成评价 (600+)...")
    for _ in range(600):
        user = random.choice(consumers)
        product = random.choice(products)
        db.add(Review(
            user_id=user.id, product_id=product.id,
            rating=random.randint(1, 5),              # 1-5星随机评分
            content=random.choice(REVIEW_TEMPLATES),   # 随机选取评价模板
            helpful_count=random.randint(0, 50),       # 随机"有帮助"数
            created_at=now - timedelta(days=random.uniform(0, 60)),  # 最近60天
        ))
    db.flush()

    # ---- 生成订单（350单，每单包含1-4件商品） ----
    print("正在生成订单 (350+)...")
    for _ in range(350):
        user = random.choice(consumers)
        items = random.sample(products, k=random.randint(1, 4))  # 随机选取1-4件商品
        total = 0
        order = Order(user_id=user.id, total_amount=0, created_at=now - timedelta(days=random.uniform(0, 30)))
        db.add(order)
        db.flush()
        for product in items:
            qty = random.randint(1, 3)  # 每件商品购买1-3个
            total += product.price * qty
            db.add(OrderItem(order_id=order.id, product_id=product.id, quantity=qty, price=product.price))
        order.total_amount = round(total, 2)  # 计算订单总金额
    db.flush()

    # ---- 生成广告（20条，随机分配给商家） ----
    print("正在生成广告 (20)...")
    ad_titles = ["限时特惠！", "新品上市", "超值优惠", "限量发售", "热销爆款",
                 "人气单品", "必买清单", "省钱攻略", "品质之选", "独家特供"]
    for i in range(20):
        merchant = random.choice(merchants)
        cat_name = random.choice(CATEGORIES)
        db.add(Ad(
            advertiser_id=merchant.id,
            title="%s - %s" % (ad_titles[i % len(ad_titles)], cat_name),
            content="快来选购我们精选的%s商品，超多优惠等你来！" % cat_name,
            target_url="/search?category=%s" % cat_name,
            bid_amount=round(random.uniform(0.5, 5.0), 2),       # 随机竞价金额
            bid_type=random.choice([BidType.CPC, BidType.CPM]),   # 随机竞价类型
            daily_budget=round(random.uniform(50, 200), 2),       # 随机每日预算
            total_budget=round(random.uniform(500, 5000), 2),     # 随机总预算
            spent_amount=round(random.uniform(0, 100), 2),        # 随机已消耗金额
            target_tags=[cat_name],                               # 定向到对应分类
        ))
    db.flush()

    db.commit()  # 提交所有数据
    db.close()
    print("\n数据生成完毕！")
    print("数据库位置: %s" % SEED_DB_PATH)


if __name__ == "__main__":
    seed()
