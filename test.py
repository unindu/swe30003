import sqlite3

import pytest
from classes.db_manager import DBManager
from classes.Account import Account, view_all_users
from classes.Inventory import Inventory
from classes.Cart import Cart
from classes.Order import Order
from classes.SalesReport import SalesReport, sales_report_menu, print_as_table
from classes.ItemHolder import ItemHolder
from classes.Delivery import Delivery

# Things to test:
# Register a user
# Logging in
# Get all items
# Add to cart
# Create an order
# View orders

# Staff login
# Add item
# Adjust stock
# View all users


# Setup

db = DBManager()

@pytest.fixture(scope="session", autouse=True)
def cleanup():
    print("Let the testing begin!")
    ItemHolder().setup_db()
    ItemHolder().seed_default_items()
    Account().seed_default_staff()
    Account().seed_default_customer()
    Delivery.ensure_table()

    yield # This does the tests

    # cleanup the db
    # Remove what was created
    db.execute("""
        DELETE FROM items
        WHERE name = ?
    """, ("test_item",), True)

    user_id = db.execute("""
        SELECT account_id
        FROM accounts
        WHERE username = ?
    """, ("test_username",), True).fetchone()[0]


    db.execute("""
        DELETE FROM carts
        WHERE user_id = ?
    """, (user_id,), True)

    db.execute("""
       DELETE
       FROM deliveries
       WHERE name = ?
       """, ("test_name",), True)

    db.execute("""
        DELETE
        FROM payments
        """)

    db.execute("""
        DELETE FROM orders
        WHERE user_id = ?
    """, (user_id,), True)

    db.execute("""
        DELETE FROM accounts
        WHERE username = ?
    """, ("test_username",), True)

    db.execute("""
        DELETE FROM stock
    """)

    ItemHolder().seed_default_items()



@pytest.mark.order(1)
def test_staff_login():
    assert Account().login("staff", "staff123")

@pytest.mark.order(3)
def test_add_item():
    Inventory().add_item("test_item", "test_description", 100, 10)
    assert db.execute("""
        SELECT name, desc, price, stock.quantity
        FROM items
        JOIN stock ON items.id = stock.id
        WHERE name = ?
        """, ("test_item",), True).fetchone() == ("test_item", "test_description", 100.0, 10)

@pytest.mark.order(4)
def test_adjust_stock():
    Inventory().update_stock("test_item", -5)
    assert db.execute("""
        SELECT stock.quantity
        FROM items
        JOIN stock on items.id = stock.id
        WHERE name = ? 
        """, ("test_item",), True).fetchone() == (5,)

    Inventory().update_stock("test_item", 95)
    assert db.execute("""
        SELECT stock.quantity
        FROM items
        JOIN stock on items.id = stock.id
        WHERE name = ?
        """, ("test_item",), True).fetchone() == (100,)


@pytest.mark.order(2)
def test_register_customer():
    import hashlib
    account = Account()
    account.register("test_username", "test@test_email.com", "test_password")
    db_answer = db.execute("""
        SELECT username, email, password
        FROM accounts
        WHERE username = ?
        """, ("test_username",), True).fetchone()
    hashed_password = hashlib.sha256("test_password".encode()).hexdigest()
    assert db_answer == ("test_username", "test@test_email.com", hashed_password)

@pytest.mark.order(5)
def test_logging_in():
    account = Account()
    assert account.login("test_username", "test_password")


@pytest.mark.order(6)
def test_cart():
    user_id = db.execute("""
        SELECT account_id
        FROM accounts
        WHERE username = ?
    """, ("test_username",)).fetchone()[0]

    cart = Cart(user_id)
    cart.add_to_cart("test_item", 5)
    assert db.execute("""
        SELECT carts.quantity, items.name
        FROM carts
        JOIN items on carts.item_id = items.id
        WHERE user_id = ?
    """, (user_id,), True).fetchone() == (5, "test_item")
    cart.remove_from_cart("test_item", 3)
    assert db.execute("""
        SELECT carts.quantity, items.name
        FROM carts
        JOIN items on carts.item_id = items.id
        WHERE user_id = ?
    """, (user_id,), True).fetchone() == (2 , "test_item")


@pytest.mark.order(7)
def test_create_order():
    user_id = db.execute("""
         SELECT account_id
         FROM accounts
         WHERE username = ?
         """, ("test_username",), True).fetchone()[0]
    order = Order(user_id)
    order.checkout("test_name", "test_address", "0123456789")
    assert db.execute("""
        SELECT items.name, stock.quantity, orders.status
        FROM orders
        JOIN stock ON stock.order_id = orders.order_id
        JOIN items ON stock.id = items.id
        WHERE orders.user_id = ?
    """, (user_id,), True).fetchone() == ("test_item", 2, "complete")
