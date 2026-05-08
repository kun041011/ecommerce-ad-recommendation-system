import os
import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import tempfile

backend_dir = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, backend_dir)
os.chdir(backend_dir)

# Use Windows temp dir for SQLite (WSL mounts don't support SQLite locking)
SEED_DB_PATH = os.path.join(tempfile.gettempdir(), "ecommerce_seed.db")
os.environ["DATABASE_URL"] = "sqlite:///" + SEED_DB_PATH.replace("\\", "/")

from app.database import Base, engine
from sqlalchemy.orm import sessionmaker

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
from app.models import (
    Ad, AdFrequencyLevel, BehaviorType, BidType, Category,
    Order, OrderItem, Product, Review, User, UserBehavior, UserRole,
)
from app.services.auth_service import hash_password

CATEGORIES = ["Electronics", "Clothing", "Books", "Home", "Food", "Sports", "Toys", "Beauty", "Auto", "Garden"]
PRODUCT_ADJECTIVES = ["Premium", "Budget", "Luxury", "Classic", "Modern", "Vintage", "Smart", "Eco", "Pro", "Ultra"]
PRODUCT_NOUNS = {
    "Electronics": ["Phone", "Laptop", "Tablet", "Headphones", "Camera", "Speaker", "Watch", "Monitor", "Keyboard", "Mouse"],
    "Clothing": ["T-Shirt", "Jeans", "Jacket", "Dress", "Sneakers", "Hat", "Scarf", "Gloves", "Socks", "Belt"],
    "Books": ["Novel", "Textbook", "Cookbook", "Biography", "Guide", "Manual", "Comic", "Dictionary", "Atlas", "Journal"],
    "Home": ["Lamp", "Chair", "Table", "Rug", "Pillow", "Curtain", "Shelf", "Clock", "Vase", "Mirror"],
    "Food": ["Coffee", "Tea", "Chocolate", "Snack Bar", "Cereal", "Pasta", "Sauce", "Spice", "Honey", "Jam"],
    "Sports": ["Ball", "Racket", "Mat", "Weights", "Bottle", "Bag", "Shoes", "Gloves", "Jersey", "Cap"],
    "Toys": ["Puzzle", "Board Game", "Doll", "Car", "Blocks", "Robot", "Kite", "Yo-Yo", "Figurine", "Plush"],
    "Beauty": ["Cream", "Serum", "Shampoo", "Lipstick", "Perfume", "Mask", "Lotion", "Oil", "Soap", "Brush"],
    "Auto": ["Charger", "Mount", "Cover", "Cleaner", "Tool Kit", "Light", "Camera", "Freshener", "Mat", "Organizer"],
    "Garden": ["Seeds", "Pot", "Shovel", "Hose", "Gloves", "Light", "Fence", "Soil", "Fertilizer", "Sprinkler"],
}
REVIEW_TEMPLATES = [
    "Great product, exactly what I needed!",
    "Good quality for the price.",
    "Decent, but could be better.",
    "Not what I expected, disappointing.",
    "Excellent! Would buy again.",
    "Average product, nothing special.",
    "Arrived damaged, poor packaging.",
    "Love it! Highly recommend.",
    "Works well, fast delivery.",
    "Okay product, fair price.",
]


def seed():
    if os.path.exists(SEED_DB_PATH):
        os.remove(SEED_DB_PATH)
    # Re-create engine after removing old DB
    from sqlalchemy import create_engine as ce
    fresh_engine = ce("sqlite:///" + SEED_DB_PATH.replace("\\", "/"), connect_args={"check_same_thread": False})
    FreshSession = sessionmaker(autocommit=False, autoflush=False, bind=fresh_engine)
    Base.metadata.create_all(bind=fresh_engine)
    db = FreshSession()

    print("Seeding categories...")
    cats = {}
    for name in CATEGORIES:
        cat = Category(name=name)
        db.add(cat)
        db.flush()
        cats[name] = cat.id

    print("Seeding users (100)...")
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
            activity_score=random.uniform(0, 100),
            ad_frequency_level=random.choice(list(AdFrequencyLevel)),
        )
        db.add(consumer)
        users.append(consumer)
    db.flush()

    merchants = [u for u in users if u.role == UserRole.merchant]
    consumers = [u for u in users if u.role == UserRole.consumer]

    print("Seeding products (1000+)...")
    products = []
    for cat_name, cat_id in cats.items():
        nouns = PRODUCT_NOUNS[cat_name]
        for adj in PRODUCT_ADJECTIVES:
            for noun in nouns:
                p = Product(
                    name="%s %s" % (adj, noun),
                    description="A %s %s in the %s category." % (adj.lower(), noun.lower(), cat_name.lower()),
                    price=round(random.uniform(5.0, 500.0), 2),
                    category_id=cat_id,
                    merchant_id=random.choice(merchants).id,
                    stock=random.randint(10, 500),
                    sales_count=random.randint(0, 200),
                    tags=[cat_name.lower(), adj.lower(), noun.lower()],
                )
                db.add(p)
                products.append(p)
    db.flush()
    print("  Created %d products" % len(products))

    print("Seeding behaviors (10000+)...")
    now = datetime.now(timezone.utc)
    behavior_types = [BehaviorType.view, BehaviorType.click, BehaviorType.cart, BehaviorType.purchase, BehaviorType.search]
    for _ in range(12000):
        user = random.choice(consumers)
        product = random.choice(products)
        btype = random.choices(behavior_types, weights=[40, 25, 15, 10, 10])[0]
        days_ago = random.uniform(0, 30)
        db.add(UserBehavior(
            user_id=user.id, product_id=product.id, behavior_type=btype,
            created_at=now - timedelta(days=days_ago),
        ))
    db.flush()

    print("Seeding reviews (500+)...")
    for _ in range(600):
        user = random.choice(consumers)
        product = random.choice(products)
        db.add(Review(
            user_id=user.id, product_id=product.id,
            rating=random.randint(1, 5),
            content=random.choice(REVIEW_TEMPLATES),
            helpful_count=random.randint(0, 20),
            created_at=now - timedelta(days=random.uniform(0, 60)),
        ))
    db.flush()

    print("Seeding orders (300+)...")
    for _ in range(350):
        user = random.choice(consumers)
        items = random.sample(products, k=random.randint(1, 4))
        total = 0
        order = Order(user_id=user.id, total_amount=0, created_at=now - timedelta(days=random.uniform(0, 30)))
        db.add(order)
        db.flush()
        for product in items:
            qty = random.randint(1, 3)
            total += product.price * qty
            db.add(OrderItem(order_id=order.id, product_id=product.id, quantity=qty, price=product.price))
        order.total_amount = round(total, 2)
    db.flush()

    print("Seeding ads (20)...")
    ad_titles = ["Flash Sale!", "New Arrival", "Best Deal", "Limited Offer", "Top Pick",
                 "Hot Item", "Must Have", "Save Big", "Premium Quality", "Exclusive"]
    for i in range(20):
        merchant = random.choice(merchants)
        cat_name = random.choice(CATEGORIES)
        db.add(Ad(
            advertiser_id=merchant.id,
            title="%s - %s" % (ad_titles[i % len(ad_titles)], cat_name),
            content="Check out our amazing %s deals!" % cat_name.lower(),
            target_url="/search?category=%s" % cat_name.lower(),
            bid_amount=round(random.uniform(0.5, 5.0), 2),
            bid_type=random.choice([BidType.CPC, BidType.CPM]),
            daily_budget=round(random.uniform(50, 200), 2),
            total_budget=round(random.uniform(500, 5000), 2),
            spent_amount=round(random.uniform(0, 100), 2),
            target_tags=[cat_name.lower()],
        ))
    db.flush()

    db.commit()
    db.close()
    print("Seed complete!")


if __name__ == "__main__":
    seed()
