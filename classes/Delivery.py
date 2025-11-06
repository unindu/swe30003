from classes.db_manager import DBManager
from datetime import datetime, timedelta


class Delivery:
    """
    Handles scheduling, cost calculation, and status updates for deliveries.
    Each delivery is linked to an order.
    """

    @classmethod
    def ensure_table(cls):
        """
        Create the deliveries table if it does not already exist.
        Called once during system setup (main.py).
        """
        db = DBManager()
        db.execute("""
            CREATE TABLE IF NOT EXISTS deliveries (
                delivery_id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                address TEXT NOT NULL,
                phone TEXT NOT NULL,
                status TEXT NOT NULL,
                tracking_number TEXT,
                delivery_cost REAL NOT NULL,
                estimated_delivery TEXT,
                FOREIGN KEY(order_id) REFERENCES orders(order_id) ON DELETE CASCADE
            )
        """, commit=True)

    def __init__(self, order_id, name, address, phone):
        self.order_id = order_id
        self.name = name
        self.address = address
        self.phone = phone
        self.status = "pending"
        self.tracking_number = None
        self.delivery_cost = 0.0
        self.estimated_delivery = None
        self.db = DBManager()

    # ---------------- Delivery Processing ---------------- #

    def calculate_cost(self, distance_km=10):
        """
        Compute delivery cost using a simple model:
        base fee + per km + 10% GST.
        """
        self.delivery_cost = (5 + distance_km * 1) * 1.10
        return self.delivery_cost

    def schedule(self):
        """
        Records a new delivery entry for the associated order.
        """
        self.tracking_number = f"DEL{self.order_id}"
        self.calculate_cost()

        eta = datetime.now() + timedelta(days=2)
        self.estimated_delivery = eta.strftime("%Y-%m-%d 15:00")

        self.db.execute("""
            INSERT INTO deliveries (order_id, name, address, phone, status, tracking_number, delivery_cost, estimated_delivery)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            self.order_id, self.name, self.address, self.phone,
            self.status, self.tracking_number, self.delivery_cost, self.estimated_delivery
        ), commit=True)

        print(f"\nDelivery scheduled:")
        print(f"  Tracking #: {self.tracking_number}")
        print(f"  ETA: {self.estimated_delivery}")
        print(f"  Cost: ${self.delivery_cost:.2f}\n")

    def cancel(self):
        """
        Mark delivery as cancelled for this instance.
        """
        self.status = "cancelled"
        self.db.execute("""
            UPDATE deliveries SET status='cancelled' WHERE order_id = ?
        """, (self.order_id,), commit=True)

    @staticmethod
    def cancel_by_order_id(order_id):
        """
        Cancel delivery without needing a Delivery object (used in Order.cancel()).
        """
        db = DBManager()
        db.execute("""
            UPDATE deliveries SET status='cancelled' WHERE order_id = ?
        """, (order_id,), commit=True)

    @staticmethod
    def list_all():
        """
        Retrieve all deliveries (used in staff menu).
        """
        db = DBManager()
        return db.execute("""
            SELECT delivery_id, order_id, name, address, phone, status, tracking_number, delivery_cost, estimated_delivery
            FROM deliveries
            ORDER BY delivery_id DESC
        """).fetchall()
