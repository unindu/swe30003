"""
Note for Tony:

The checkout() method currently records the order total and moves items
from the user's cart to their order history. At this stage, the order is
considered "placed" but not "paid" or "scheduled for delivery".

Your work will extend this process by:
1. Adding a payment step BEFORE the order is finalised.
2. Creating a delivery record that links to order_id after payment success.

You can integrate your logic by modifying checkout() or by creating a
new method (e.g., process_payment_and_delivery(order_id)).
No changes to Inventory/Cart logic are required.
"""

# classes/Order.py
from classes.ItemHolder import ItemHolder
from datetime import datetime

class Order(ItemHolder):
    """
    Converts a user's cart into a recorded order and moves items from
    the cart location to a permanent order history location.
    
    """

    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        # Location identifiers stored in the stock table
        self.cart_location = f"{user_id}_cart"
        self.order_location = f"{user_id}_order"
        self._create_orders_table()

    def _create_orders_table(self):
        """
        Creates the orders table if it does not exist.
        Stores total cost and date for record-keeping.
        Does not store line items, item quantities remain in stock table
        under <user_id>_order location.
        """
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                total REAL NOT NULL,
                date TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def checkout(self):
        """
        Completes the purchase:
        - Verifies the cart is not empty
        - Calculates total order cost
        - Inserts a new order record into the orders table
        - Moves items from <user_id>_cart to <user_id>_order (persistent record)
        - Empties the cart

        This function does NOT handle payment or delivery logic.
        """

        # Retrieve all cart items (item_id, qty)
        items = self.cursor.execute("""
            SELECT id, quantity FROM stock
            WHERE location = ?
        """, (self.cart_location,)).fetchall()

        if not items:
            print("🛒 Your cart is empty — nothing to checkout.")
            return

        # Compute total cost from item prices
        total = self.cursor.execute("""
            SELECT SUM(i.price * s.quantity)
            FROM stock s
            JOIN items i ON s.id = i.id
            WHERE s.location = ?
        """, (self.cart_location,)).fetchone()[0]

        # Create order record with timestamp
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.cursor.execute("""
            INSERT INTO orders (user_id, total, date)
            VALUES (?, ?, ?)
        """, (self.user_id, total, date_str))
        order_id = self.cursor.lastrowid  

        # Move each item out of cart into long-term order history
        for (item_id, qty) in items:
            # ON CONFLICT prevents duplicate rows in case multiple orders contain same items
            self.cursor.execute("""
                INSERT INTO stock (id, quantity, location)
                VALUES (?, ?, ?)
                ON CONFLICT(id, location)
                DO UPDATE SET quantity = quantity + excluded.quantity
            """, (item_id, qty, self.order_location))

        # Clear the cart
        self.cursor.execute("""
            DELETE FROM stock WHERE location = ?
        """, (self.cart_location,))

        self.conn.commit()

        print(f"Order #{order_id} placed! Total: ${total:.2f}")
        print("Order ready for delivery.\n")
