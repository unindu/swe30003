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


db = DBManager()
# Setup
ItemHolder().setup_db()
ItemHolder().seed_default_items()
Account().seed_default_staff()
Account().seed_default_customer()
Delivery.ensure_table()

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
        """, ("test_item",)).fetchone() == ["test_item", "test_description", 100, 10]

@pytest.mark.order(4)
def test_adjust_stock():
    Inventory().update_stock("test_item", -5)
    assert db.execute("""
        SELECT stock.quantity
        FROM items
        JOIN stock on items.id = stock.id
        WHERE name = ? 
        """, ("test_item",)).fetchone() == [5]

    Inventory().update_stock("test_item", 95)
    assert db.execute("""
        SELECT stock.quantity
        FROM items
        JOIN stock on items.id = stock.id
        WHERE name = ?
        """, ("test_item",)).fetchone() == [100]


@pytest.mark.order(2)
def test_register_customer():
    import hashlib
    account = Account()
    account.register("test_username", "test_email", "test_password")
    db_answer = db.execute("""
        SELECT username, email, password
        FROM accounts
        WHERE username = ?
        """, ("test_username",)).fetchone()
    hashed_password = hashlib.sha256("test_password".encode()).hexdigest()
    assert db_answer == ["test_username", "test_email", hashed_password]

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

    cart = Cart({"user_id" : user_id})
    cart.add_to_cart("test_item", 5)
    assert db.execute("""
        SELECT carts.quantity, items.name
        FROM carts
        JOIN items on carts.item_id = items.id
        WHERE user_id = ?
    """, (user_id,)) == [(5, "test_item")]
    cart.remove_from_cart("test_item", 3)
    assert db.execute("""
        SELECT carts.quantity, items.name
        FROM carts
        JOIN items on carts.item_id = items.id
        WHERE user_id = ?
    """, (user_id,)) == [(2 , "test_item")]


@pytest.mark.order(7)
def test_create_order():
    user_id = db.execute("""
         SELECT account_id
         FROM accounts
         WHERE username = ?
         """, ("test_username",)).fetchone()[0]
    order = Order(user_id)
    order.checkout("test_name", "test_address", "0123456789")
    assert db.execute("""
        SELECT items.name, stock.quantity, orders.status
        FROM orders
        JOIN stock ON stock.order_id = orders.order_id
        JOIN items ON stock.id = items.id
        WHERE orders.user_id = ?
    """, (user_id,)) == ["test_item", 2, "complete"]
