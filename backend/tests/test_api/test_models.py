from app.models import User, Product, Category, Order, OrderItem, UserRole


def test_create_user(db):
    user = User(username="testuser", email="test@test.com", hashed_password="hashed")
    db.add(user)
    db.commit()
    db.refresh(user)
    assert user.id is not None
    assert user.role == UserRole.consumer
    assert user.activity_score == 0.0


def test_create_product_with_category(db):
    user = User(username="merchant1", email="m@test.com", hashed_password="hashed", role=UserRole.merchant)
    cat = Category(name="Electronics")
    db.add_all([user, cat])
    db.commit()

    product = Product(name="Phone", price=999.0, category_id=cat.id, merchant_id=user.id, stock=10)
    db.add(product)
    db.commit()
    db.refresh(product)
    assert product.id is not None
    assert product.category.name == "Electronics"


def test_create_order_with_items(db):
    user = User(username="buyer", email="b@test.com", hashed_password="hashed")
    cat = Category(name="Books")
    db.add_all([user, cat])
    db.commit()

    product = Product(name="Book", price=29.99, category_id=cat.id, merchant_id=user.id, stock=5)
    db.add(product)
    db.commit()

    order = Order(user_id=user.id, total_amount=29.99)
    db.add(order)
    db.commit()

    item = OrderItem(order_id=order.id, product_id=product.id, quantity=1, price=29.99)
    db.add(item)
    db.commit()

    db.refresh(order)
    assert len(order.items) == 1
    assert order.items[0].product.name == "Book"
