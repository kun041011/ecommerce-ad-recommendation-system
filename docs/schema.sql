-- ============================================================
-- 基于社区数据反馈的电商广告推荐系统 - 数据库表定义
-- 数据库: SQLite
-- 共10张核心表
-- ============================================================

-- 1. 用户表
CREATE TABLE users (
    id              INTEGER     PRIMARY KEY AUTOINCREMENT,  -- 用户ID，自增主键
    username        VARCHAR(50) NOT NULL UNIQUE,             -- 用户名，唯一约束
    email           VARCHAR(120) NOT NULL UNIQUE,            -- 邮箱，唯一约束
    hashed_password VARCHAR(255) NOT NULL,                   -- bcrypt加密后的密码
    avatar_url      VARCHAR(255),                            -- 头像URL，可为空
    role            VARCHAR(10) NOT NULL DEFAULT 'consumer', -- 用户角色: consumer/merchant/admin
    activity_score  REAL        NOT NULL DEFAULT 0.0,        -- 活跃度评分（0-100），供频控组件读取
    ad_frequency_level VARCHAR(10) NOT NULL DEFAULT 'normal',-- 广告频控等级: high/normal/low
    created_at      DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP, -- 注册时间
    last_active_at  DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP  -- 最后活跃时间
);

-- 2. 商品分类表（支持父子层级结构）
CREATE TABLE categories (
    id              INTEGER     PRIMARY KEY AUTOINCREMENT,  -- 分类ID，自增主键
    name            VARCHAR(50) NOT NULL,                    -- 分类名称
    parent_id       INTEGER,                                 -- 父分类ID，顶级分类为NULL
    FOREIGN KEY (parent_id) REFERENCES categories(id)
);

-- 3. 商品表
CREATE TABLE products (
    id              INTEGER     PRIMARY KEY AUTOINCREMENT,  -- 商品ID，自增主键
    name            VARCHAR(200) NOT NULL,                   -- 商品名称
    description     TEXT        NOT NULL DEFAULT '',         -- 商品描述
    price           REAL        NOT NULL,                    -- 商品单价
    category_id     INTEGER     NOT NULL,                    -- 所属分类ID
    merchant_id     INTEGER     NOT NULL,                    -- 发布商家的用户ID
    stock           INTEGER     NOT NULL DEFAULT 0,          -- 库存数量
    sales_count     INTEGER     NOT NULL DEFAULT 0,          -- 累计销量
    tags            JSON,                                    -- 商品标签（JSON数组），用于推荐和广告定向
    embedding       BLOB,                                    -- 商品向量嵌入，用于相似度推荐
    created_at      DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP, -- 商品创建时间
    FOREIGN KEY (category_id) REFERENCES categories(id),
    FOREIGN KEY (merchant_id) REFERENCES users(id)
);

-- 4. 订单表
CREATE TABLE orders (
    id              INTEGER     PRIMARY KEY AUTOINCREMENT,  -- 订单ID，自增主键
    user_id         INTEGER     NOT NULL,                    -- 下单用户ID
    total_amount    REAL        NOT NULL,                    -- 订单总金额
    status          VARCHAR(10) NOT NULL DEFAULT 'pending',  -- 订单状态: pending/paid/shipped/completed/cancelled
    created_at      DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP, -- 下单时间
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 5. 订单明细表（订单与商品的多对多关系）
CREATE TABLE order_items (
    id              INTEGER     PRIMARY KEY AUTOINCREMENT,  -- 明细ID，自增主键
    order_id        INTEGER     NOT NULL,                    -- 所属订单ID
    product_id      INTEGER     NOT NULL,                    -- 商品ID
    quantity        INTEGER     NOT NULL,                    -- 购买数量
    price           REAL        NOT NULL,                    -- 下单时的商品单价（价格快照）
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- 6. 广告表
CREATE TABLE ads (
    id              INTEGER     PRIMARY KEY AUTOINCREMENT,  -- 广告ID，自增主键
    advertiser_id   INTEGER     NOT NULL,                    -- 广告主（商家）用户ID
    title           VARCHAR(200) NOT NULL,                   -- 广告标题
    content         TEXT        NOT NULL DEFAULT '',         -- 广告文案内容
    image_url       VARCHAR(255) NOT NULL DEFAULT '',        -- 广告图片URL
    target_url      VARCHAR(255) NOT NULL DEFAULT '',        -- 点击跳转目标URL
    bid_amount      REAL        NOT NULL,                    -- 竞价金额（CPC为单次点击价，CPM为千次展示价）
    bid_type        VARCHAR(5)  NOT NULL DEFAULT 'CPC',      -- 竞价类型: CPC/CPM
    daily_budget    REAL        NOT NULL,                    -- 每日预算上限
    total_budget    REAL        NOT NULL,                    -- 总预算上限
    spent_amount    REAL        NOT NULL DEFAULT 0.0,        -- 已消耗金额
    target_tags     JSON,                                    -- 定向标签（JSON数组），匹配用户兴趣
    status          VARCHAR(10) NOT NULL DEFAULT 'active',   -- 广告状态: active/paused/exhausted
    created_at      DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP, -- 广告创建时间
    FOREIGN KEY (advertiser_id) REFERENCES users(id)
);

-- 7. 广告曝光记录表
CREATE TABLE ad_impressions (
    id              INTEGER     PRIMARY KEY AUTOINCREMENT,  -- 记录ID，自增主键
    ad_id           INTEGER     NOT NULL,                    -- 关联广告ID
    user_id         INTEGER     NOT NULL,                    -- 触发用户ID
    impression_type VARCHAR(10) NOT NULL,                    -- 事件类型: show/click/convert
    context         JSON,                                    -- 事件上下文（页面来源、设备信息等）
    created_at      DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP, -- 事件发生时间
    FOREIGN KEY (ad_id) REFERENCES ads(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 8. 商品评价表
CREATE TABLE reviews (
    id              INTEGER     PRIMARY KEY AUTOINCREMENT,  -- 评价ID，自增主键
    user_id         INTEGER     NOT NULL,                    -- 评价用户ID
    product_id      INTEGER     NOT NULL,                    -- 被评价的商品ID
    rating          INTEGER     NOT NULL,                    -- 评分（1-5星）
    content         TEXT        NOT NULL DEFAULT '',         -- 评价文字内容
    helpful_count   INTEGER     NOT NULL DEFAULT 0,          -- "有帮助"投票数
    created_at      DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP, -- 评价发布时间
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- 9. 商品问答表
CREATE TABLE qa (
    id              INTEGER     PRIMARY KEY AUTOINCREMENT,  -- 问答ID，自增主键
    product_id      INTEGER     NOT NULL,                    -- 关联商品ID
    user_id         INTEGER     NOT NULL,                    -- 提问用户ID
    question        TEXT        NOT NULL,                    -- 问题内容
    answer          TEXT,                                    -- 回答内容，未回答时为NULL
    answered_by     INTEGER,                                 -- 回答者用户ID
    created_at      DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP, -- 提问时间
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (answered_by) REFERENCES users(id)
);

-- 10. 用户行为日志表（推荐引擎和活跃度引擎的共同数据源）
CREATE TABLE user_behaviors (
    id              INTEGER     PRIMARY KEY AUTOINCREMENT,  -- 行为记录ID，自增主键
    user_id         INTEGER     NOT NULL,                    -- 行为用户ID
    product_id      INTEGER,                                 -- 关联商品ID（搜索、登录行为可为NULL）
    behavior_type   VARCHAR(10) NOT NULL,                    -- 行为类型: view/click/cart/purchase/review/search/login
    context         JSON,                                    -- 行为上下文（搜索关键词、页面来源等）
    created_at      DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP, -- 行为发生时间
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- ============================================================
-- 索引定义
-- ============================================================
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_merchant ON products(merchant_id);
CREATE INDEX idx_orders_user ON orders(user_id);
CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_ads_advertiser ON ads(advertiser_id);
CREATE INDEX idx_ad_impressions_ad ON ad_impressions(ad_id);
CREATE INDEX idx_ad_impressions_user ON ad_impressions(user_id);
CREATE INDEX idx_reviews_product ON reviews(product_id);
CREATE INDEX idx_reviews_user ON reviews(user_id);
CREATE INDEX idx_qa_product ON qa(product_id);
CREATE INDEX idx_behaviors_user ON user_behaviors(user_id);
CREATE INDEX idx_behaviors_type ON user_behaviors(behavior_type);
CREATE INDEX idx_behaviors_created ON user_behaviors(created_at);
