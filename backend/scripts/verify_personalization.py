# -*- coding: utf-8 -*-
"""Verify the recommendation engine personalizes per user on the real dataset.

Builds the user-item interaction matrix from the seeded DB, fits the
RecommendationPipeline (UserCF+ItemCF+content+hot), runs it for several
representative users with distinct interest profiles, and measures:
  - relevance: share of each user's Top-10 recs that fall in categories the
    user has actually interacted with (personal-interest alignment);
  - diversity across users: average pairwise overlap of the Top-10 lists
    (low overlap => results are user-specific, i.e. personalized).
"""
import io
import os
import sys
from collections import defaultdict, Counter
from itertools import combinations
from pathlib import Path

import numpy as np

# 在仓库任意位置均可运行：python backend/scripts/verify_personalization.py
backend_dir = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, backend_dir)
db_file = os.path.join(backend_dir, "data", "ecommerce.db")
os.environ["DATABASE_URL"] = "sqlite:///" + db_file.replace("\\", "/")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Product, User, UserBehavior, UserRole, BehaviorType
from app.recommendation.pipeline import RecommendationPipeline

eng = create_engine(os.environ["DATABASE_URL"], connect_args={"check_same_thread": False})
db = sessionmaker(bind=eng)()

WEIGHT = {"purchase": 5, "review": 4, "cart": 3, "view": 1, "click": 1, "search": 0, "login": 0}

# ordered products / consumers
products = db.query(Product).order_by(Product.id).all()
pid_list = [p.id for p in products]
pid_idx = {p.id: i for i, p in enumerate(products)}
cat_of = {p.id: p.category_id for p in products}
texts = [(p.name or "") + " " + (p.description or "") for p in products]
views = {p.id: float(p.sales_count or 0) for p in products}

consumers = db.query(User).filter(User.role == UserRole.consumer).order_by(User.id).all()
uid_list = [u.id for u in consumers]
uid_idx = {u.id: i for i, u in enumerate(consumers)}

# interaction matrix + per-user historical categories
M = np.zeros((len(consumers), len(products)), dtype=float)
user_hist_cats = defaultdict(Counter)
behs = db.query(UserBehavior).filter(UserBehavior.product_id.isnot(None)).all()
for b in behs:
    if b.user_id in uid_idx and b.product_id in pid_idx:
        w = WEIGHT.get(b.behavior_type.value, 1)
        if w:
            M[uid_idx[b.user_id], pid_idx[b.product_id]] += w
            user_hist_cats[b.user_id][cat_of[b.product_id]] += 1

pipe = RecommendationPipeline()
pipe.fit(M, texts, views)

# pick representative users: enough history, distinct dominant categories
cand = []
for u in consumers:
    hc = user_hist_cats[u.id]
    if sum(hc.values()) >= 5 and hc:
        cand.append((u, hc.most_common(1)[0][0]))
seen_cat, picks = set(), []
for u, dom in cand:
    if dom not in seen_cat:
        seen_cat.add(dom)
        picks.append((u, dom))
    if len(picks) >= 6:
        break

cat_name = {p.category_id: None for p in products}
from app.models import Category
for c in db.query(Category).all():
    cat_name[c.id] = c.name

out = io.open("verify_personalization.txt", "w", encoding="utf-8")
rec_lists = {}
rows = []
for u, dom in picks:
    idxs = pipe.recommend(uid_idx[u.id], n=10, product_ids=pid_list)
    rec_ids = [pid_list[i] for i in idxs if i < len(pid_list)]
    rec_lists[u.id] = set(rec_ids)
    rec_cats = [cat_of[i] for i in rec_ids]
    hist_cats = set(user_hist_cats[u.id])
    aligned = sum(1 for c in rec_cats if c in hist_cats)
    rate = aligned / len(rec_cats) if rec_cats else 0
    rows.append((u.username, cat_name[dom], len(rec_ids), round(rate * 100), Counter(rec_cats)))
    out.write("用户 %s | 历史主兴趣品类: %s | 推荐%d项 | 命中历史兴趣品类: %d%%\n"
              % (u.username[:14], cat_name[dom], len(rec_ids), round(rate * 100)))
    top = Counter(cat_name[c] for c in rec_cats).most_common(3)
    out.write("    推荐品类分布(前3): %s\n" % top)

# pairwise overlap of Top-10 lists across users
ov = []
for (a, sa), (b, sb) in combinations(rec_lists.items(), 2):
    if sa and sb:
        ov.append(len(sa & sb) / len(sa | sb))
mean_overlap = round(np.mean(ov) * 100, 1) if ov else 0
mean_align = round(np.mean([r[3] for r in rows]), 1) if rows else 0

# ---- 留一法命中率 (leave-one-out Hit@K)：隐藏用户最强偏好项，看引擎能否召回 ----
from sklearn.metrics.pairwise import cosine_similarity
h10 = h20 = ntest = 0
for u in consumers:
    r = M[uid_idx[u.id]]
    inter = np.where(r > 0)[0]
    if len(inter) < 4:
        continue
    held = int(inter[np.argmax(r[inter])])      # 强度最高的交互项作为留出项
    row = r.copy(); row[held] = 0
    sims = cosine_similarity(row.reshape(1, -1), M)[0]
    sims[uid_idx[u.id]] = 0
    scores = sims @ M
    scores[row > 0] = -1e9                        # 排除其余已交互项，但保留留出项可被召回
    order = np.argsort(scores)[::-1]
    rank = int(np.where(order == held)[0][0])
    ntest += 1
    if rank < 10:
        h10 += 1
    if rank < 20:
        h20 += 1
hit10 = round(100 * h10 / ntest, 1) if ntest else 0
hit20 = round(100 * h20 / ntest, 1) if ntest else 0
baseline = round(100 * 10 / len(products), 2)

out.write("\n聚合指标：\n")
out.write("  代表用户数: %d\n" % len(rows))
out.write("  平均“推荐命中个人历史兴趣品类”比例: %.1f%%\n" % mean_align)
out.write("  用户两两推荐列表平均重合度(Jaccard): %.1f%%\n" % mean_overlap)
out.write("  留一法测试用户数: %d\n" % ntest)
out.write("  留一法 Hit@10: %.1f%%（随机基线约 %.2f%%）\n" % (hit10, baseline))
out.write("  留一法 Hit@20: %.1f%%\n" % hit20)
out.close()
print("done; users=%d align=%.1f%% overlap=%.1f%% loo_n=%d hit@10=%.1f%% hit@20=%.1f%% base=%.2f%%"
      % (len(rows), mean_align, mean_overlap, ntest, hit10, hit20, baseline))
