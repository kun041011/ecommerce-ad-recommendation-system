# 电商广告推荐系统设计文档

## 1. 项目概述

### 1.1 目标

构建一个完整的在线电商广告推荐系统，集成电商业务、推荐引擎、广告投放、社区评价和智能频控功能。系统通过基于社区数据反馈的频控组件，根据用户活跃度动态调整广告推送频率，在提升用户留存率的同时实现商业化盈利最大化。

### 1.2 技术栈

- **后端**: FastAPI + SQLAlchemy + Pydantic
- **数据库**: SQLite（持久化） + Redis（缓存/会话/实时计数）
- **推荐算法**: scikit-learn + PyTorch
- **前端**: Vue 3 + Element Plus + Pinia + Axios
- **测试**: pytest + httpx（后端）, Vitest（前端）
- **部署**: Docker Compose 本地运行

### 1.3 规模定位

学习/演示项目，可本地运行，专注架构设计和算法实现的完整性。

---

## 2. 整体架构

### 2.1 架构风格

单体分层架构，模块间通过代码分层隔离。

```
Vue 3 前端 (Element Plus)
       ↓ HTTP/REST
FastAPI 单体服务 (分模块)
  ├── 电商模块 (商品/订单/用户)
  ├── 社区模块 (评价/评分/问答)
  ├── 推荐引擎 (召回→粗排→精排→重排)
  ├── 广告系统 (投放/频控/计费)
  └── 活跃度引擎 (评分/调频)
       ↓
SQLite + Redis
```

### 2.2 项目目录结构

```
ecommerce-ad-system/
├── backend/
│   ├── app/
│   │   ├── main.py                  # 应用入口，FastAPI 实例
│   │   ├── config.py                # 配置管理
│   │   ├── database.py              # SQLAlchemy 引擎和会话
│   │   ├── models/                  # SQLAlchemy ORM 模型
│   │   │   ├── user.py
│   │   │   ├── product.py
│   │   │   ├── order.py
│   │   │   ├── ad.py
│   │   │   └── community.py
│   │   ├── schemas/                 # Pydantic 请求/响应模型
│   │   │   ├── user.py
│   │   │   ├── product.py
│   │   │   ├── order.py
│   │   │   ├── ad.py
│   │   │   └── community.py
│   │   ├── api/                     # API 路由层
│   │   │   ├── auth.py
│   │   │   ├── products.py
│   │   │   ├── orders.py
│   │   │   ├── ads.py
│   │   │   ├── community.py
│   │   │   └── recommend.py
│   │   ├── services/                # 业务逻辑层
│   │   │   ├── user_service.py
│   │   │   ├── product_service.py
│   │   │   ├── order_service.py
│   │   │   ├── ad_service.py
│   │   │   └── community_service.py
│   │   ├── recommendation/          # 推荐引擎
│   │   │   ├── recall/
│   │   │   │   ├── user_cf.py       # 基于用户的协同过滤
│   │   │   │   ├── item_cf.py       # 基于物品的协同过滤
│   │   │   │   ├── content_based.py # 基于内容的推荐
│   │   │   │   ├── als.py           # 矩阵分解
│   │   │   │   └── hot.py           # 热门召回（冷启动兜底）
│   │   │   ├── ranking/
│   │   │   │   ├── deepfm.py        # DeepFM 模型
│   │   │   │   ├── din.py           # DIN 模型
│   │   │   │   └── features.py      # 特征工程
│   │   │   ├── rerank/
│   │   │   │   ├── diversity.py     # 多样性重排 (MMR)
│   │   │   │   └── rules.py         # 业务规则过滤
│   │   │   └── pipeline.py          # 推荐流水线编排
│   │   ├── ad_engine/               # 广告引擎
│   │   │   ├── bidding.py           # 竞价排序
│   │   │   ├── frequency.py         # 频控组件
│   │   │   └── billing.py           # 计费模块
│   │   └── activity/                # 活跃度引擎
│   │       ├── scorer.py            # 活跃度评分计算
│   │       └── adjuster.py          # 广告频率调整器
│   ├── tests/
│   │   ├── test_recommendation/
│   │   ├── test_ad_engine/
│   │   ├── test_activity/
│   │   ├── test_api/
│   │   └── conftest.py
│   ├── scripts/
│   │   ├── seed_data.py             # 种子数据生成
│   │   └── train_models.py          # 模型训练脚本
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.vue
│   │   ├── main.ts
│   │   ├── views/
│   │   │   ├── Home.vue             # 首页（推荐流+广告）
│   │   │   ├── ProductDetail.vue    # 商品详情
│   │   │   ├── Search.vue           # 搜索结果
│   │   │   ├── Cart.vue             # 购物车
│   │   │   ├── Orders.vue           # 订单列表
│   │   │   ├── Profile.vue          # 用户中心
│   │   │   ├── MerchantDashboard.vue # 商家后台
│   │   │   └── AdminDashboard.vue   # 管理后台
│   │   ├── components/
│   │   │   ├── ProductCard.vue
│   │   │   ├── AdBanner.vue
│   │   │   ├── ReviewSection.vue
│   │   │   ├── QASection.vue
│   │   │   └── ActivityScore.vue
│   │   ├── stores/                  # Pinia 状态管理
│   │   ├── api/                     # Axios API 调用
│   │   └── router/                  # Vue Router
│   ├── package.json
│   └── vite.config.ts
├── data/                            # 种子数据
├── docs/                            # 文档
└── docker-compose.yml
```

---

## 3. 数据模型设计

### 3.1 用户模型 (User)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 自增主键 |
| username | String(50) unique | 用户名 |
| email | String(120) unique | 邮箱 |
| hashed_password | String(255) | bcrypt 加密密码 |
| avatar_url | String(255) nullable | 头像 |
| role | Enum(consumer/merchant/admin) | 角色 |
| activity_score | Float default=0 | 活跃度评分 0-100 |
| ad_frequency_level | Enum(low/normal/high) | 广告频率等级 |
| created_at | DateTime | 注册时间 |
| last_active_at | DateTime | 最后活跃时间 |

### 3.2 商品模型 (Product)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 自增主键 |
| name | String(200) | 商品名 |
| description | Text | 描述 |
| price | Float | 价格 |
| category_id | Integer FK→Category | 所属分类 |
| merchant_id | Integer FK→User | 商家 |
| stock | Integer | 库存 |
| sales_count | Integer default=0 | 销量 |
| tags | JSON | 标签数组，用于内容推荐 |
| embedding | BLOB nullable | 预计算商品向量 |
| created_at | DateTime | 创建时间 |

### 3.3 分类模型 (Category)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 自增主键 |
| name | String(50) | 分类名 |
| parent_id | Integer FK→self nullable | 父分类（支持层级） |

### 3.4 订单模型 (Order + OrderItem)

**Order:**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 自增主键 |
| user_id | Integer FK→User | 下单用户 |
| total_amount | Float | 总金额 |
| status | Enum(pending/paid/shipped/completed/cancelled) | 状态 |
| created_at | DateTime | 下单时间 |

**OrderItem:**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 自增主键 |
| order_id | Integer FK→Order | 所属订单 |
| product_id | Integer FK→Product | 商品 |
| quantity | Integer | 数量 |
| price | Float | 下单时价格 |

### 3.5 广告模型 (Ad + AdImpression)

**Ad:**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 自增主键 |
| advertiser_id | Integer FK→User | 广告主（商家） |
| title | String(200) | 广告标题 |
| content | Text | 广告内容 |
| image_url | String(255) | 广告图片 |
| target_url | String(255) | 点击跳转链接 |
| bid_amount | Float | 出价 |
| bid_type | Enum(CPC/CPM) | 计费模式 |
| daily_budget | Float | 日预算 |
| total_budget | Float | 总预算 |
| spent_amount | Float default=0 | 已消耗 |
| target_tags | JSON | 定向标签 |
| status | Enum(active/paused/exhausted) | 状态 |
| created_at | DateTime | 创建时间 |

**AdImpression:**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 自增主键 |
| ad_id | Integer FK→Ad | 广告 |
| user_id | Integer FK→User | 用户 |
| impression_type | Enum(show/click/convert) | 展示/点击/转化 |
| context | JSON | 上下文（页面、位置） |
| created_at | DateTime | 时间 |

### 3.6 社区模型 (Review + QA)

**Review:**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 自增主键 |
| user_id | Integer FK→User | 评价用户 |
| product_id | Integer FK→Product | 评价商品 |
| rating | Integer (1-5) | 评分 |
| content | Text | 评价内容 |
| helpful_count | Integer default=0 | 有用数 |
| created_at | DateTime | 评价时间 |

**QA:**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 自增主键 |
| product_id | Integer FK→Product | 所属商品 |
| user_id | Integer FK→User | 提问用户 |
| question | Text | 问题 |
| answer | Text nullable | 回答 |
| answered_by | Integer FK→User nullable | 回答者 |
| created_at | DateTime | 创建时间 |

### 3.7 用户行为日志 (UserBehavior)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 自增主键 |
| user_id | Integer FK→User | 用户 |
| product_id | Integer FK→Product nullable | 商品 |
| behavior_type | Enum(view/click/cart/purchase/review/search/login) | 行为类型 |
| context | JSON | 上下文（来源页面、搜索词、停留时长） |
| created_at | DateTime | 行为时间 |

### 3.8 Redis 数据结构

| Key 模式 | 类型 | 说明 | TTL |
|----------|------|------|-----|
| `user:{uid}:activity` | String | 活跃度得分 | 2h |
| `user:{uid}:freq_level` | String | 频率等级 | 2h |
| `user:{uid}:ad_count:{date}` | String | 今日广告展示次数 | 到次日 |
| `user:{uid}:ad_last` | String | 上次广告展示时间戳 | 1h |
| `user:{uid}:session` | Hash | 会话信息 | 30min |
| `product:{pid}:views` | String | 商品浏览计数 | 永久 |
| `hot:products` | ZSet | 热门商品排行 | 1h |
| `rec:{uid}:cache` | List | 推荐结果缓存 | 30min |

---

## 4. 推荐引擎设计

### 4.1 多阶段漏斗架构

```
全量商品池 (N千)
    ↓
召回层 (Recall): 多路召回，缩小候选集 → 数百个
    ↓
粗排层 (Pre-ranking): 轻量模型快速打分 → 数十个
    ↓
精排层 (Ranking): 深度模型精细打分 → 十几个
    ↓
重排层 (Re-ranking): 业务规则 + 频控 + 多样性 → 最终展示
```

### 4.2 召回层算法

**UserCF (基于用户的协同过滤)**
- 实现: scikit-learn cosine_similarity
- 输入: 用户-商品评分矩阵（隐式评分：浏览=1，购买=5）
- 输出: 相似用户喜欢的商品
- 更新: 每日全量重算相似度矩阵

**ItemCF (基于物品的协同过滤)**
- 实现: scikit-learn cosine_similarity
- 输入: 商品-用户共现矩阵
- 输出: 与用户历史行为相似的商品
- 更新: 每日全量

**Content-Based (基于内容的推荐)**
- 实现: TF-IDF 向量化 + cosine_similarity
- 输入: 商品标签和描述
- 输出: 与用户偏好标签相似的商品
- 更新: 商品数据变更时

**ALS (交替最小二乘法矩阵分解)**
- 实现: scikit-learn NMF
- 输入: 用户-商品隐式反馈矩阵
- 输出: 用户和商品的隐向量，补全评分矩阵
- 更新: 每日

**Hot (热门召回)**
- 实现: Redis ZSet 排行榜
- 用途: 新用户冷启动兜底

### 4.3 排序层算法

**DeepFM**
- 框架: PyTorch 自实现
- 结构: FM 层（低阶特征交叉） + DNN 层（高阶特征交叉）
- 输入特征: 用户特征 + 商品特征 + 上下文特征
- 输出: 点击概率 pCTR
- 训练: 用户行为日志中的点击/未点击样本

**DIN (Deep Interest Network)**
- 框架: PyTorch 自实现
- 结构: Attention 层动态建模用户兴趣
- 输入: 用户行为序列 + 候选商品
- 输出: 点击概率
- 训练: 同 DeepFM

### 4.4 特征工程

```
用户特征:
  - user_id (embedding)
  - 注册天数
  - 历史购买数
  - 平均客单价
  - 活跃度评分
  - 偏好品类 (top-3)

商品特征:
  - product_id (embedding)
  - 价格（分桶）
  - 品类 (embedding)
  - 销量
  - 评分均值
  - 标签 (multi-hot)

交叉特征:
  - 用户对该品类的购买次数
  - 用户对该价格区间的偏好度

上下文特征:
  - 时间段 (morning/afternoon/evening/night)
  - 星期几 (weekday/weekend)
```

### 4.5 重排层

**MMR 多样性重排**: 在相关性和多样性之间取平衡，避免推荐结果品类过于集中。

**业务规则**:
- 已购商品过滤
- 已展示去重（短期内不重复推荐同一商品）
- 广告混排（按频控策略在推荐结果中插入广告）

---

## 5. 广告系统设计

### 5.1 广告投放流程

```
广告请求 → 定向匹配 → 竞价排序 → 频控过滤 → 展示 → 计费
```

1. **定向匹配**: 广告 target_tags 与用户画像/当前浏览品类匹配
2. **竞价排序**: eCPM = bid × pCTR，pCTR 由推荐模型提供
3. **频控过滤**: 基于用户活跃度动态控制展示频率
4. **计费**: GSP (广义第二价格) 扣费

### 5.2 计费模式

- **CPC**: 用户点击广告时扣费，扣费金额 = 下一位 eCPM / 当前 pCTR + 0.01
- **CPM**: 每千次展示计费

### 5.3 预算控制

- 实时扣减 spent_amount
- 当 spent_amount >= daily_budget 时暂停当日投放
- 当 spent_amount >= total_budget 时标记 exhausted

---

## 6. 频控组件设计

### 6.1 核心理念

活跃用户对广告容忍度高，可适当增加广告密度以提升收入；低活跃用户容易流失，减少广告打扰以保留存。通过社区行为（评价、问答、点赞）作为活跃度的增强信号，激励用户参与社区。

### 6.2 频控策略矩阵

| 活跃度等级 | 每页广告数 | 最小间隔(秒) | 每日上限 |
|-----------|-----------|-------------|---------|
| high (score >= 60) | 3 | 60 | 50 |
| normal (20 <= score < 60) | 2 | 120 | 30 |
| low (score < 20) | 1 | 300 | 10 |

### 6.3 频控判断流程

```
1. 从 Redis 获取用户活跃度等级 → 确定频控参数
2. 从 Redis 获取今日已展示次数 → 检查日上限
3. 从 Redis 获取上次展示时间 → 检查最小间隔
4. 综合判断: 是否展示广告 + 展示几条
5. 展示后更新 Redis 计数器
```

---

## 7. 活跃度引擎设计

### 7.1 评分公式

```
activity_score = min(100, Σ(weight_i × count_i × decay(days_ago_i)))
```

### 7.2 行为权重表

| 行为 | 权重 | 来源 |
|------|------|------|
| 登录 | +2 | 电商 |
| 浏览商品 | +1 | 电商 |
| 搜索 | +1 | 电商 |
| 加入购物车 | +3 | 电商 |
| 购买 | +10 | 电商 |
| 发表评价 | +5 | 社区 |
| 回答问题 | +5 | 社区 |
| 点赞评价 | +2 | 社区 |

### 7.3 时间衰减函数

```
decay(days_ago) = exp(-0.1 × days_ago)
```
- 今天: 1.0
- 7 天前: ~0.50
- 14 天前: ~0.25
- 30 天前: ~0.05

### 7.4 等级划分

| 范围 | 等级 | 频控策略 |
|------|------|---------|
| score >= 60 | high_activity | 可多推广告 |
| 20 <= score < 60 | normal_activity | 标准频率 |
| score < 20 | low_activity | 减少打扰 |

### 7.5 更新机制

- 实时: 用户行为发生时，增量更新 Redis 中的活跃度缓存
- 批量: 每小时定时任务全量重算并持久化到 SQLite

---

## 8. 前端设计

### 8.1 页面规划

| 页面 | 路由 | 核心功能 |
|------|------|---------|
| 首页 | `/` | 推荐商品流 + 穿插广告 + 搜索栏 |
| 商品详情 | `/product/:id` | 详情 + 评价/问答 + 相关推荐 + 广告位 |
| 搜索结果 | `/search` | 搜索列表 + 搜索广告 |
| 购物车 | `/cart` | 购物车管理 |
| 订单列表 | `/orders` | 订单管理 |
| 用户中心 | `/profile` | 个人信息 + 我的评价 + 活跃度仪表盘 |
| 商家后台 | `/merchant` | 商品管理 + 广告投放 + 数据报表 |
| 管理后台 | `/admin` | 用户管理 + 系统监控 + 推荐效果 + 频控分析 |

### 8.2 核心交互

- 首页: 瀑布流商品卡片，广告以 "推广" 标记混排在推荐流中
- 商品详情页: 评价列表 + 评分分布 + 问答区 + 侧边广告
- 用户中心: 活跃度仪表盘（得分、等级、近期行为趋势图）
- 管理后台: 商业化指标仪表盘（RPM、CTR、留存率、活跃度分布）

---

## 9. API 设计

### 9.1 认证

```
POST /api/auth/register    - 注册
POST /api/auth/login       - 登录（返回 JWT）
GET  /api/auth/me          - 当前用户信息
```

### 9.2 商品

```
GET  /api/products              - 商品列表（分页）
GET  /api/products/{id}         - 商品详情
GET  /api/products/search       - 搜索 (query, category, price_range)
POST /api/products              - 创建商品（商家）
PUT  /api/products/{id}         - 更新商品（商家）
```

### 9.3 订单

```
POST /api/orders                - 创建订单
GET  /api/orders                - 我的订单列表
GET  /api/orders/{id}           - 订单详情
PUT  /api/orders/{id}/status    - 更新订单状态
```

### 9.4 推荐

```
GET /api/recommend/home                 - 首页推荐
GET /api/recommend/similar/{product_id} - 相似商品推荐
GET /api/recommend/for-you              - 猜你喜欢
```

### 9.5 广告

```
GET  /api/ads/fetch             - 获取广告（含频控逻辑）
POST /api/ads/impression        - 上报展示/点击/转化
POST /api/ads                   - 创建广告（商家）
GET  /api/ads/my                - 我的广告列表（商家）
GET  /api/ads/{id}/stats        - 广告效果统计
```

### 9.6 社区

```
POST /api/reviews                      - 发表评价
GET  /api/reviews/product/{id}         - 商品评价列表
POST /api/reviews/{id}/helpful         - 点赞评价
POST /api/qa                           - 提问
GET  /api/qa/product/{id}              - 商品问答列表
POST /api/qa/{id}/answer               - 回答问题
```

### 9.7 活跃度

```
GET /api/activity/my-score             - 我的活跃度详情
```

### 9.8 数据分析（管理后台）

```
GET /api/analytics/dashboard           - 总览仪表盘
GET /api/analytics/retention           - 留存率数据
GET /api/analytics/ad-performance      - 广告效果数据
GET /api/analytics/activity-dist       - 活跃度分布
GET /api/analytics/frequency-effect    - 频控效果分析
```

### 9.9 行为上报

```
POST /api/behavior/track               - 上报用户行为（浏览、搜索等）
```

---

## 10. 测试方案

### 10.1 后端单元测试

**推荐算法测试:**
- UserCF/ItemCF 相似度计算正确性
- Content-Based TF-IDF 向量化和匹配
- ALS 矩阵分解收敛性
- DeepFM/DIN 模型前向传播和梯度
- Pipeline 编排：各阶段数据流正确传递

**活跃度引擎测试:**
- 评分计算公式正确性
- 时间衰减函数验证
- 等级划分边界值 (19.9→low, 20.0→normal, 59.9→normal, 60.0→high)
- 增量更新和全量重算一致性

**频控组件测试:**
- 各等级对应的频控参数正确
- 日上限达到后停止展示
- 最小间隔内不展示
- Redis 计数器更新正确

**广告系统测试:**
- 竞价排序 eCPM 计算
- CPC/CPM 计费正确性
- 预算耗尽后停止投放
- 定向匹配逻辑

### 10.2 后端集成测试

- 完整推荐流水线端到端
- 广告投放 → 展示 → 点击 → 计费完整流程
- 用户行为 → 活跃度更新 → 频控调整链路
- 订单创建 → 库存扣减 → 行为记录全流程

### 10.3 API 测试

- 所有 API 端点的正常和异常情况
- JWT 认证和权限控制
- 请求参数校验
- 分页和排序

### 10.4 性能测试

- 推荐接口响应时间 (目标 < 200ms)
- 并发请求 (50 并发下无错误)
- 模型推理延迟

### 10.5 前端测试

- 核心组件渲染测试
- 路由跳转测试
- API 调用 Mock 测试

### 10.6 数据验证

- 种子数据: 1000+ 商品, 100+ 用户, 10000+ 行为记录
- 推荐质量离线评估: Precision@K, Recall@K, NDCG@K

---

## 11. 商业化指标体系

| 指标 | 计算方式 | 目标 |
|------|---------|------|
| RPM | 广告收入 / 展示次数 × 1000 | 最大化 |
| CTR | 点击次数 / 展示次数 | > 2% |
| 1日留存率 | 次日登录用户 / 当日新增用户 | > 40% |
| 7日留存率 | 第7日登录用户 / 当日新增用户 | > 20% |
| 频控ROI | 频控调整后的留存变化 / 广告收入变化 | > 1 |
| 活跃用户占比 | high_activity 用户数 / 总用户数 | > 30% |
