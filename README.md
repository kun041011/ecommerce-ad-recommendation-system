# 基于社区数据反馈的电商广告推荐系统

## 项目概述

本项目设计并实现了一个创新的在线电商广告推荐系统，区别于传统电商平台，本系统在基本电商业务和广告推荐业务的基础上，引入了用户社区子系统，通过基于社区数据反馈的频控组件，根据用户活跃度得分动态调整广告推送频率，在提升用户总体留存率的同时实现商业化盈利的最大化。

## 系统架构

### 整体架构图

```
┌─────────────────────────────────────────────────────┐
│                    前端展示层                         │
│           Vue 3 + Element Plus + ECharts             │
└──────────────────────┬──────────────────────────────┘
                       │ HTTP/REST API
┌──────────────────────┴──────────────────────────────┐
│                   后端服务层 (FastAPI)                │
│  ┌──────────┐  ┌──────────┐  ┌────────────────┐    │
│  │ 电商模块  │  │ 社区模块  │  │  推荐引擎模块   │    │
│  │ 商品/订单 │  │ 评价/问答 │  │ 召回→排序→重排  │    │
│  └──────────┘  └──────────┘  └────────────────┘    │
│  ┌──────────────────┐  ┌──────────────────────┐    │
│  │    广告引擎模块    │  │    活跃度引擎模块     │    │
│  │ 竞价/频控/计费    │  │  评分/等级/调频       │    │
│  └──────────────────┘  └──────────────────────┘    │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────┐
│                    数据存储层                         │
│         SQLite (持久化)  +  Redis (缓存)             │
└─────────────────────────────────────────────────────┘
```

### 技术栈

| 层次 | 技术 | 用途 |
|------|------|------|
| 前端 | Vue 3 + TypeScript | 单页应用框架 |
| UI组件 | Element Plus | 企业级UI组件库 |
| 可视化 | ECharts | 数据统计图表 |
| 状态管理 | Pinia | 响应式状态管理 |
| 后端框架 | FastAPI | 高性能异步Web框架 |
| ORM | SQLAlchemy 2.0 | 数据库对象映射 |
| 数据验证 | Pydantic v2 | 请求/响应模型验证 |
| 认证 | JWT (python-jose) | 无状态身份认证 |
| 推荐算法 | scikit-learn | 协同过滤/矩阵分解 |
| 深度学习 | PyTorch | DeepFM/DIN排序模型 |
| 数据库 | SQLite | 轻量级关系型数据库 |
| 缓存 | Redis | 频控计数/推荐缓存 |
| 容器化 | Docker Compose | 一键部署 |
| 测试 | pytest | 单元/集成/性能测试 |

## 核心功能模块

### 1. 电商业务模块

- **用户系统**: 注册、登录、JWT认证、角色管理（消费者/商家/管理员）
- **商品管理**: 商品CRUD、分类管理、多条件搜索（关键词、价格区间、品类）
- **订单系统**: 购物车、下单、库存校验与自动扣减、订单状态管理
- **行为追踪**: 实时记录用户浏览、点击、加购、购买、搜索等行为

### 2. 社区子系统

- **商品评价**: 1-5星评分、文字评价、"有用"点赞机制
- **问答系统**: 用户提问、商家/其他用户回答
- **社区数据反馈**: 评价和问答行为作为活跃度信号，反哺推荐和频控决策

### 3. 推荐引擎

采用业界标准的**多阶段漏斗架构**：

```
全量商品池 → 召回层(数百) → 粗排层(数十) → 精排层(十几) → 重排层(最终展示)
```

#### 召回层算法

| 算法 | 原理 | 实现方式 |
|------|------|---------|
| UserCF | 基于用户的协同过滤，找到相似用户喜欢的商品 | 用户-商品评分矩阵 + 余弦相似度 |
| ItemCF | 基于物品的协同过滤，找到与历史行为相似的商品 | 物品-用户共现矩阵 + 余弦相似度 |
| Content-Based | 基于内容的推荐，利用商品标签和描述匹配用户偏好 | TF-IDF向量化 + 余弦相似度 |
| ALS | 矩阵分解，学习用户和商品的隐向量表示 | NMF非负矩阵分解 |
| Hot | 热门召回，基于销量和浏览量排行 | Redis ZSet排行榜 |

#### 排序层算法

| 算法 | 原理 | 特点 |
|------|------|------|
| DeepFM | FM层捕获低阶特征交叉 + DNN层捕获高阶特征交叉 | Wide&Deep架构，同时建模显式和隐式特征交互 |
| DIN | 基于Attention机制动态建模用户兴趣 | 根据候选商品自适应聚合用户历史行为序列 |

#### 特征工程

```
用户特征: user_id(embedding), 注册天数, 历史购买数, 平均客单价, 活跃度评分, 偏好品类(top-3)
商品特征: product_id(embedding), 价格(分桶), 品类(embedding), 销量, 评分均值, 标签(multi-hot)
交叉特征: 用户对该品类的购买次数, 用户对该价格区间的偏好度
上下文特征: 时间段(morning/afternoon/evening/night), 星期几(weekday/weekend)
```

#### 重排层

- **MMR多样性重排**: 在相关性和多样性之间取平衡，避免推荐结果品类过于集中
- **业务规则过滤**: 已购商品过滤、短期曝光去重
- **广告混排**: 按频控策略在推荐结果中插入竞价广告

### 4. 广告系统

#### 投放流程

```
广告请求 → 定向匹配 → eCPM竞价排序 → 频控过滤 → 展示 → 计费
```

- **定向匹配**: 广告target_tags与用户画像/当前浏览品类匹配
- **竞价排序**: eCPM = bid × pCTR，pCTR由推荐模型预估
- **计费模式**:
  - CPC (按点击付费): GSP广义第二价格扣费，charge = next_eCPM / current_pCTR / 1000 + 0.01
  - CPM (按展示付费): 千次展示计费，charge = bid / 1000

#### 预算控制

- 日预算耗尽自动暂停当日投放
- 总预算耗尽标记为exhausted状态

### 5. 频控组件（核心创新点）

**核心理念**: 活跃用户对广告容忍度高，可适当增加广告密度以提升收入；低活跃用户容易流失，减少广告打扰以保留存。通过社区行为（评价、问答、点赞）作为活跃度的增强信号，激励用户参与社区。

#### 频控策略矩阵

| 活跃度等级 | 每页广告数 | 最小间隔(秒) | 每日上限 |
|-----------|-----------|-------------|---------|
| 高活跃 (≥60分) | 3 | 60 | 50 |
| 普通 (20-60分) | 2 | 120 | 30 |
| 低活跃 (<20分) | 1 | 300 | 10 |

#### 频控判断流程

```
1. 获取用户活跃度等级 → 确定频控参数
2. 查询今日已展示次数 → 检查日上限
3. 查询上次展示时间 → 检查最小间隔
4. 综合判断: 是否展示广告 + 展示几条
5. 展示后更新计数器
```

### 6. 活跃度引擎

#### 评分公式

```
activity_score = min(100, Σ(weight_i × count_i × decay(days_ago_i)))
```

#### 行为权重表

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

#### 时间衰减函数

```
decay(days_ago) = e^(-0.1 × days_ago)
```

| 时间 | 衰减系数 |
|------|---------|
| 今天 | 1.00 |
| 3天前 | 0.74 |
| 7天前 | 0.50 |
| 14天前 | 0.25 |
| 30天前 | 0.05 |

#### 等级划分与更新机制

- score ≥ 60 → 高活跃（可多推广告）
- 20 ≤ score < 60 → 普通（标准频率）
- score < 20 → 低活跃（减少打扰）
- **实时更新**: 用户行为发生时增量更新缓存
- **批量更新**: 每小时定时任务全量重算并持久化

## 数据库设计

### E-R关系图

```
User (1) ──── (N) Order ──── (N) OrderItem ──── (1) Product
  │                                                    │
  │ (1:N)                                         (1:N) │
  ├──── Review ────────────────────────────────────────┘
  ├──── QA
  ├──── UserBehavior
  ├──── Ad (as merchant/advertiser)
  └──── AdImpression
        │
        └──── (N:1) Ad
```

### 核心数据表

| 表名 | 说明 | 核心字段 |
|------|------|---------|
| users | 用户表 | username, email, role, activity_score, ad_frequency_level |
| products | 商品表 | name, price, category_id, tags, stock, sales_count, embedding |
| categories | 分类表 | name, parent_id（支持层级分类） |
| orders | 订单表 | user_id, total_amount, status |
| order_items | 订单项表 | order_id, product_id, quantity, price |
| ads | 广告表 | advertiser_id, bid_amount, bid_type, daily_budget, total_budget, target_tags, status |
| ad_impressions | 广告展示日志 | ad_id, user_id, impression_type(show/click/convert), context |
| reviews | 评价表 | user_id, product_id, rating(1-5), content, helpful_count |
| qa | 问答表 | product_id, user_id, question, answer, answered_by |
| user_behaviors | 行为日志表 | user_id, product_id, behavior_type, context, created_at |

### Redis缓存设计

| Key模式 | 类型 | 说明 | TTL |
|---------|------|------|-----|
| `user:{uid}:activity` | String | 活跃度得分 | 2h |
| `user:{uid}:freq_level` | String | 频率等级 | 2h |
| `user:{uid}:ad_count:{date}` | String | 今日广告展示次数 | 到次日 |
| `user:{uid}:ad_last` | String | 上次广告展示时间戳 | 1h |
| `hot:products` | ZSet | 热门商品排行 | 1h |
| `rec:{uid}:cache` | List | 推荐结果缓存 | 30min |

## API设计

系统提供RESTful API，共9个模块40+接口：

| 模块 | 路径前缀 | 核心接口 |
|------|---------|---------|
| 认证 | `/api/auth` | POST register, POST login, GET me |
| 商品 | `/api/products` | GET list, GET /{id}, GET /search, POST create, PUT update |
| 订单 | `/api/orders` | POST create, GET list, GET /{id} |
| 推荐 | `/api/recommend` | GET /home, GET /similar/{id}, GET /for-you |
| 广告 | `/api/ads` | GET /fetch(含频控), POST /impression, POST create, GET /my, GET /{id}/stats |
| 评价 | `/api/reviews` | POST create, GET /product/{id}, POST /{id}/helpful |
| 问答 | `/api/qa` | POST create, GET /product/{id}, POST /{id}/answer |
| 活跃度 | `/api/activity` | GET /my-score |
| 行为 | `/api/behavior` | POST /track |
| 分析 | `/api/analytics` | GET /dashboard, GET /activity-dist, GET /ad-performance |

## 前端页面

| 页面 | 路由 | 功能说明 |
|------|------|---------|
| 首页 | `/` | 推荐商品流 + 广告混排 + 搜索栏 |
| 商品详情 | `/product/:id` | 商品信息 + 评价 + 问答 + 相似推荐 |
| 搜索 | `/search` | 关键词搜索商品 |
| 购物车 | `/cart` | 购物车管理 + 一键结算 |
| 订单 | `/orders` | 订单列表与状态查看 |
| 个人中心 | `/profile` | 个人信息 + 活跃度仪表盘 |
| 商家后台 | `/merchant` | 广告投放创建与管理 |
| 管理后台 | `/admin` | 数据分析 + ECharts可视化图表(活跃度饼图、广告效果柱状图、频控策略对比图) |

## 测试方案

### 测试覆盖

| 测试类型 | 数量 | 覆盖范围 |
|---------|------|---------|
| 单元测试 | 48+ | 推荐算法(UserCF/ItemCF/Content/ALS/DeepFM/DIN)、活跃度评分、频控逻辑、竞价计费 |
| API测试 | 21+ | 所有API端点的正常/异常场景、JWT认证、权限控制 |
| 集成测试 | 6 | 完整购买流程、社区互动流程、广告频控流程、活跃度更新链路 |
| 性能测试 | 2 | 推荐接口响应时间基准、商品列表接口响应基准 |

### 测试结果

```
77 passed, 4 skipped in 27s
```

### 性能指标

- 推荐接口平均响应时间 < 500ms
- 商品列表接口平均响应时间 < 200ms

## 商业化指标体系

| 指标 | 计算方式 | 目标 |
|------|---------|------|
| RPM (千次展示收入) | 广告收入 / 展示次数 × 1000 | 最大化 |
| CTR (广告点击率) | 点击次数 / 展示次数 | > 2% |
| 1日留存率 | 次日登录用户 / 当日新增用户 | > 40% |
| 7日留存率 | 第7日登录用户 / 当日新增用户 | > 20% |
| 频控ROI | 频控调整后的留存变化 / 广告收入变化 | > 1 |
| 活跃用户占比 | 高活跃用户数 / 总用户数 | > 30% |

## 项目创新点

1. **社区驱动的频控机制**: 将社区行为（评价、问答、点赞）纳入活跃度计算，激励用户参与社区的同时优化广告策略，形成正向循环
2. **动态频控策略**: 根据用户实时活跃度自动调整广告推送频率，实现留存率和广告收入的帕累托最优
3. **多算法融合推荐**: 经典协同过滤(UserCF/ItemCF) + 内容推荐 + 矩阵分解(ALS) + 深度学习排序(DeepFM/DIN)的完整推荐流水线
4. **eCPM竞价机制**: 结合预估CTR和出价进行广告排序，采用GSP广义第二价格计费，最大化平台收益
5. **全链路数据追踪**: 从用户行为采集 → 活跃度评分 → 推荐生成 → 广告投放 → 频控调整的完整数据闭环

## 快速开始

### 环境要求

- Python 3.8+
- Node.js 16+
- Redis（可选，用于缓存加速）

### 安装与启动

```bash
# 克隆项目
git clone https://github.com/kun041011/ecommerce-ad-recommendation-system.git
cd ecommerce-ad-recommendation-system

# 启动后端
cd backend
pip install -r requirements.txt
python scripts/seed_data.py    # 生成种子数据（1000+商品、100用户、12000行为记录）
uvicorn app.main:app --port 8000

# 启动前端（新终端窗口）
cd frontend
npm install
npm run dev
# 访问 http://localhost:5173
```

### Docker一键部署

```bash
docker-compose up --build
# 前端访问 http://localhost
# API文档访问 http://localhost:8000/docs
```

### 运行测试

```bash
cd backend
python -m pytest tests/ -v
```

### 测试账号

| 角色 | 用户名 | 密码 | 权限 |
|------|--------|------|------|
| 管理员 | admin | admin123 | 管理后台、数据分析 |
| 商家 | merchant_0 ~ merchant_9 | merchant123 | 商品管理、广告投放 |
| 消费者 | user_0 ~ user_88 | user123 | 浏览购物、评价问答 |

## 目录结构

```
ecommerce-ad-recommendation-system/
├── backend/                         # 后端服务
│   ├── app/
│   │   ├── main.py                  # FastAPI应用入口
│   │   ├── config.py                # 配置管理（数据库、JWT、Redis）
│   │   ├── database.py              # SQLAlchemy引擎和会话管理
│   │   ├── models/                  # ORM数据模型
│   │   │   ├── user.py              # 用户模型（角色、活跃度、频率等级）
│   │   │   ├── product.py           # 商品和分类模型
│   │   │   ├── order.py             # 订单和订单项模型
│   │   │   ├── ad.py                # 广告和展示日志模型
│   │   │   ├── community.py         # 评价和问答模型
│   │   │   └── behavior.py          # 用户行为日志模型
│   │   ├── schemas/                 # Pydantic请求/响应验证模型
│   │   ├── api/                     # API路由层
│   │   │   ├── auth.py              # 认证接口
│   │   │   ├── products.py          # 商品接口
│   │   │   ├── orders.py            # 订单接口
│   │   │   ├── ads.py               # 广告接口（含频控）
│   │   │   ├── community.py         # 社区接口
│   │   │   ├── recommend.py         # 推荐接口
│   │   │   ├── activity.py          # 活跃度接口
│   │   │   ├── behavior.py          # 行为追踪接口
│   │   │   └── analytics.py         # 数据分析接口
│   │   ├── services/                # 业务逻辑层
│   │   ├── recommendation/          # 推荐引擎
│   │   │   ├── recall/              # 召回算法（UserCF/ItemCF/Content/ALS/Hot）
│   │   │   ├── ranking/             # 排序算法（DeepFM/DIN/特征工程）
│   │   │   ├── rerank/              # 重排策略（MMR多样性/业务规则）
│   │   │   └── pipeline.py          # 推荐流水线编排
│   │   ├── ad_engine/               # 广告引擎
│   │   │   ├── bidding.py           # eCPM竞价排序
│   │   │   ├── frequency.py         # 频控组件（核心创新）
│   │   │   └── billing.py           # CPC/CPM计费
│   │   └── activity/                # 活跃度引擎
│   │       └── scorer.py            # 活跃度评分与等级分类
│   ├── tests/                       # 测试用例（77个）
│   │   ├── test_api/                # API端点测试
│   │   ├── test_recommendation/     # 推荐算法测试
│   │   ├── test_ad_engine/          # 广告引擎测试
│   │   ├── test_activity/           # 活跃度测试
│   │   ├── test_integration.py      # 集成测试
│   │   └── test_performance.py      # 性能测试
│   ├── scripts/
│   │   └── seed_data.py             # 种子数据生成器
│   └── requirements.txt             # Python依赖
├── frontend/                        # Vue 3前端应用
│   ├── src/
│   │   ├── views/                   # 页面组件（8个页面）
│   │   ├── components/              # 通用组件（商品卡片、广告、评价、问答、活跃度）
│   │   ├── stores/                  # Pinia状态管理（用户、购物车）
│   │   ├── api/                     # Axios API调用封装
│   │   └── router/                  # Vue Router路由配置
│   └── package.json
├── docker-compose.yml               # Docker Compose编排文件
├── docs/                            # 设计文档和实现计划
│   └── superpowers/
│       ├── specs/                   # 系统设计规格说明
│       └── plans/                   # 实现计划
└── README.md                        # 项目说明文档
```

## 参考文献

1. Covington P, Adams J, Sargin E. Deep neural networks for youtube recommendations[C]. Proceedings of the 10th ACM Conference on Recommender Systems, 2016: 191-198.
2. Guo H, Tang R, Ye Y, et al. DeepFM: a factorization-machine based neural network for CTR prediction[C]. Proceedings of the 26th International Joint Conference on Artificial Intelligence (IJCAI), 2017: 1725-1731.
3. Zhou G, Zhu X, Song C, et al. Deep interest network for click-through rate prediction[C]. Proceedings of the 24th ACM SIGKDD International Conference on Knowledge Discovery & Data Mining, 2018: 1059-1068.
4. He X, Liao L, Zhang H, et al. Neural collaborative filtering[C]. Proceedings of the 26th International Conference on World Wide Web (WWW), 2017: 173-182.
5. Rendle S. Factorization machines[C]. Proceedings of the 10th IEEE International Conference on Data Mining (ICDM), 2010: 995-1000.
6. Koren Y, Bell R, Volinsky C. Matrix factorization techniques for recommender systems[J]. Computer, 2009, 42(8): 30-37.
7. Carbonell J, Goldstein J. The use of MMR, diversity-based reranking for reordering documents and producing summaries[C]. Proceedings of the 21st ACM SIGIR, 1998: 335-336.

## 许可证

MIT License
