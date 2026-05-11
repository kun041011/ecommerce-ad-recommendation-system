# 论文流程图（Mermaid 源码）

以下为论文中需要插入的流程图的标准 Mermaid 格式源码。请使用 Visio 按照 Mermaid 逻辑绘制规范流程图，然后插入到 Word 文档对应的占位位置。

流程图规范要求：
- 开始/结束：圆角矩形（椭圆形）
- 处理步骤：矩形
- 判断/分支：菱形
- 箭头方向：从上到下或从左到右
- 连接线带箭头，分支标注条件文字

---

## 图3-1 系统整体架构图

```mermaid
graph TB
    subgraph 前端展示层
        A[Vue 3 + Element Plus + ECharts]
    end

    subgraph 后端服务层["后端服务层 (FastAPI)"]
        B[API路由层<br/>认证/商品/订单/推荐/广告/社区/活跃度/分析]
        C[业务逻辑层<br/>用户服务/商品服务/订单服务/社区服务/广告服务]
        subgraph 算法引擎层
            D[推荐引擎<br/>召回→排序→重排]
            E[广告引擎<br/>竞价/频控/计费]
            F[活跃度引擎<br/>评分/等级划分]
        end
    end

    subgraph 数据存储层
        G[(SQLite<br/>持久化存储)]
        H[(Redis<br/>缓存/计数)]
    end

    A -->|HTTP REST API| B
    B --> C
    C --> D
    C --> E
    C --> F
    E -->|读取活跃度| F
    D --> G
    E --> G
    F --> G
    D --> H
    E --> H
```

---

## 图3-2 推荐引擎数据流程图

```mermaid
flowchart TB
    Start([用户请求推荐]) --> A[读取用户行为日志]
    A --> B[构建用户画像特征]
    B --> C{用户是否有历史行为?}
    C -->|否| D[热门召回兜底]
    C -->|是| E[多路召回并行执行]
    
    E --> E1[UserCF召回]
    E --> E2[ItemCF召回]
    E --> E3[Content-Based召回]
    E --> E4[ALS矩阵分解召回]
    E --> E5[热门召回]
    
    E1 --> F[候选集合并去重<br/>数百个商品]
    E2 --> F
    E3 --> F
    E4 --> F
    E5 --> F
    
    F --> G[排序层精细打分<br/>DeepFM / DIN]
    G --> H[重排层处理<br/>数十个商品]
    H --> H1[MMR多样性重排]
    H1 --> H2[已购商品过滤]
    H2 --> H3[已展示去重]
    H3 --> I[广告混排<br/>按频控策略插入广告]
    D --> I
    I --> End([返回最终推荐列表<br/>10~20个商品+广告])
```

---

## 图3-3 广告投放与频控流程图

```mermaid
flowchart TB
    Start([页面请求广告]) --> A[获取当前用户信息]
    A --> B[查询用户行为日志]
    B --> C[计算活跃度评分<br/>score = Σ weight × decay]
    C --> D[划分活跃度等级]
    D --> E{等级判定}
    E -->|score ≥ 60| F1[高活跃<br/>每页3条/间隔60s/日限50]
    E -->|20 ≤ score < 60| F2[普通<br/>每页2条/间隔120s/日限30]
    E -->|score < 20| F3[低活跃<br/>每页1条/间隔300s/日限10]
    
    F1 --> G[获取频控参数]
    F2 --> G
    F3 --> G
    
    G --> H{今日展示数 ≥ 日上限?}
    H -->|是| X([返回空广告列表])
    H -->|否| I{距上次展示 < 最小间隔?}
    I -->|是| X
    I -->|否| J[查询active状态广告]
    J --> K[计算eCPM排序<br/>eCPM = bid × pCTR × 1000]
    K --> L[截取Top-N条广告<br/>N = min(每页数, 日限-已展示)]
    L --> M[返回广告列表]
    M --> N[前端展示广告]
    N --> O{用户点击?}
    O -->|是| P[上报click事件<br/>CPC扣费]
    O -->|否| Q[上报show事件<br/>CPM扣费]
    P --> R{预算是否耗尽?}
    Q --> R
    R -->|是| S[广告状态→exhausted]
    R -->|否| End([流程结束])
    S --> End
```

---

## 图3-4 活跃度反馈闭环流程图

```mermaid
flowchart TB
    subgraph 用户行为产生
        A1[浏览商品<br/>权重+1]
        A2[购买商品<br/>权重+10]
        A3[发表评价<br/>权重+5]
        A4[回答问题<br/>权重+5]
        A5[点赞评价<br/>权重+2]
    end

    A1 --> B[行为追踪模块<br/>写入user_behaviors表]
    A2 --> B
    A3 --> B
    A4 --> B
    A5 --> B

    B --> C[活跃度引擎<br/>读取近30天行为]
    C --> D[按权重 × 时间衰减<br/>加权求和计算评分]
    D --> E[划分活跃度等级<br/>高/普通/低]
    E --> F[频控组件<br/>确定广告策略参数]
    F --> G{活跃度等级}
    G -->|高活跃| H1[增加广告密度<br/>→ 提升收入]
    G -->|低活跃| H2[减少广告打扰<br/>→ 保护留存]
    H1 --> I[用户体验良好<br/>继续活跃使用]
    H2 --> I
    I -->|正向循环| A1
```

---

## 图4-1 多阶段推荐漏斗架构图

```mermaid
flowchart TB
    A[全量商品池<br/>1000+ 件商品] --> B[召回层<br/>5路并行召回]
    B --> C[候选集<br/>~200个商品]
    C --> D[排序层<br/>DeepFM / DIN 精细打分]
    D --> E[精排结果<br/>~50个商品]
    E --> F[重排层<br/>MMR多样性 + 业务规则]
    F --> G[最终结果<br/>10~20个商品]

    subgraph 召回层详情
        B1[UserCF<br/>相似用户偏好]
        B2[ItemCF<br/>相似物品推荐]
        B3[Content-Based<br/>TF-IDF标签匹配]
        B4[ALS<br/>矩阵分解补全]
        B5[Hot<br/>热门商品兜底]
    end

    B --> B1
    B --> B2
    B --> B3
    B --> B4
    B --> B5
```

---

## 图4-2 频控组件判断流程图

```mermaid
flowchart TB
    Start([开始频控判断]) --> A[输入: user_id, activity_level,<br/>today_count, last_shown_ts]
    A --> B[根据activity_level<br/>获取FrequencyPolicy]
    B --> C{today_count ≥ daily_cap?}
    C -->|是| D([返回: 不允许<br/>reason=daily_cap_reached])
    C -->|否| E[计算时间差<br/>elapsed = now - last_shown_ts]
    E --> F{elapsed < min_interval_sec?}
    F -->|是| G([返回: 不允许<br/>reason=min_interval_not_met])
    F -->|否| H[计算可展示数量<br/>max_ads = min(ads_per_page,<br/>daily_cap - today_count)]
    H --> I([返回: 允许<br/>max_ads=N])
```

---

## 图4-3 活跃度评分计算流程图

```mermaid
flowchart TB
    Start([开始计算活跃度]) --> A[输入: 用户行为列表]
    A --> B{行为列表是否为空?}
    B -->|是| C([返回 score = 0.0])
    B -->|否| D[初始化 score = 0.0]
    D --> E[遍历每条行为记录]
    E --> F[获取行为权重<br/>weight = BEHAVIOR_WEIGHTS.get(type)]
    F --> G[计算时间差<br/>days_ago = (now - created_at) / 86400]
    G --> H[计算衰减因子<br/>decay = e^(-0.1 × days_ago)]
    H --> I[累加得分<br/>score += weight × decay]
    I --> J{还有更多行为?}
    J -->|是| E
    J -->|否| K[封顶处理<br/>score = min(100, score)]
    K --> L[等级划分]
    L --> M{score ≥ 60?}
    M -->|是| N([返回 high])
    M -->|否| O{score ≥ 20?}
    O -->|是| P([返回 normal])
    O -->|否| Q([返回 low])
```

---

## 使用说明

1. 将以上 Mermaid 代码复制到 [Mermaid Live Editor](https://mermaid.live/) 中预览
2. 参照 Mermaid 图的逻辑结构，在 Visio 中绘制标准流程图
3. 流程图规范：开始/结束用椭圆形，处理步骤用矩形，判断用菱形，连接线带箭头
4. 导出为图片（PNG/EMF），插入到 Word 文档中对应的【此处插入流程图】占位位置
5. 在图片下方添加图号和标题（如"图3-1 系统整体架构图"）
