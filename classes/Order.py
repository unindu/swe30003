from classes.ItemHolder import ItemHolder
from classes.Payment import Payment
from classes.Delivery import Delivery
from classes.db_manager import DBManager
from datetime import datetime


class Order(ItemHolder):
    """
    Handles checkout: creates orders, processes payment, moves cart items to stock,
    schedules delivery, and prints confirmation receipts.
    """

    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.payment = None
        self.delivery = None
        self.db = DBManager()
        self._create_orders_table()

    def _create_orders_table(self):
        """Ensures the orders table exists."""
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                total REAL NOT NULL,
                date TEXT NOT NULL,
                status TEXT DEFAULT 'pending'
            );
        """, commit=True)

    # ---------------- Checkout ---------------- #

    def checkout(self, name, address, phone, payment_method="credit_card"):
        """Runs full checkout workflow."""
        self.db.execute("""
            DELETE FROM orders WHERE status='pending' AND user_id=?
        """, (self.user_id,), commit=True)

        total = self._get_cart_total()
        if not total:
            print("Cart is empty.")
            return False

        order_id = self._create_order(total)

        if not self._process_payment(order_id, total, payment_method.lower()):
            return False

        self._move_cart_to_order(order_id)
        self._schedule_delivery(order_id, name, address, phone)
        self.generate_confirmation(order_id)
        return True

    # ---------------- Internals ---------------- #

    def _get_cart_total(self):
        result = self.db.execute("""
            SELECT SUM(items.price * carts.quantity)
            FROM carts
            JOIN items ON carts.item_id = items.id
            WHERE carts.user_id = ?
        """, (self.user_id,)).fetchone()[0]
        return result or 0

    def _create_order(self, total):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        cursor = self.db.execute("""
            INSERT INTO orders (user_id, total, date)
            VALUES (?, ?, ?)
        """, (self.user_id, total, timestamp), commit=True)
        return cursor.lastrowid

    def _process_payment(self, order_id, total, method):
        self.payment = Payment(order_id, total)
        success = self.payment.process(method)
        if not success:
            self.db.execute("DELETE FROM orders WHERE order_id=?", (order_id,), commit=True)
        return success

    def _move_cart_to_order(self, order_id):
        self.db.execute("""
            INSERT INTO stock (id, quantity, order_id)
            SELECT item_id, quantity, ? FROM carts WHERE user_id = ?
        """, (order_id, self.user_id), commit=True)

        self.db.execute("DELETE FROM carts WHERE user_id=?", (self.user_id,), commit=True)
        self.db.execute("UPDATE orders SET status='complete' WHERE order_id=?", (order_id,), commit=True)

    def _schedule_delivery(self, order_id, name, address, phone):
        self.delivery = Delivery(order_id, name, address, phone)
        self.delivery.schedule()

    # ---------------- Post-Order ---------------- #

    def cancel(self, order_id):
        """Cancels a completed order."""
        order = self.db.execute("""
            SELECT total, user_id FROM orders WHERE order_id=?
        """, (order_id,)).fetchone()

        if not order or order[1] != self.user_id:
            print("Cannot cancel this order.")
            return False

        Payment(order_id, order[0]).refund()
        Delivery.cancel_by_order_id(order_id)
        self.db.execute("UPDATE orders SET status='cancelled' WHERE order_id=?", (order_id,), commit=True)
        print(f"Order #{order_id} cancelled.")
        return True

    def generate_confirmation(self, order_id):
        """Prints a formatted receipt."""
        total, date = self.db.execute("""
            SELECT total, date FROM orders WHERE order_id=?
        """, (order_id,)).fetchone()

        items = self.db.execute("""
            SELECT items.name, items.price, stock.quantity
            FROM stock
            JOIN items ON stock.id = items.id
            WHERE stock.order_id = ?
        """, (order_id,)).fetchall()

        print(f"\nORDER CONFIRMATION #{order_id}")
        print(f"Date: {date}\n")
        for name, price, qty in items:
            print(f"{name:<15} x{qty:<3} @ ${price:.2f} = ${price * qty:.2f}")
        print(f"\nTotal: ${total:.2f}\n")
