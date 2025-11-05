from classes.db_manager import DBManager
from datetime import datetime, timedelta


class Delivery:
    """
    Handles scheduling and tracking of deliveries associated with orders.
    """

    @classmethod
    def ensure_table(cls):
        """Create the deliveries table if it doesn't already exist."""
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

    def calculate_cost(self, distance_km=10.0):
        """
        Delivery cost = base fee + per-km fee + GST
        (kept very simple but realistic enough)
        """
        self.delivery_cost = (5.00 + distance_km * 1.00) * 1.10
        return self.delivery_cost

    def schedule(self):
        """
        Creates a delivery entry for the order.
        """
        self.tracking_number = f"DEL{self.order_id}"
        self.calculate_cost()

        # Delivery ETA = 2 days at 3:00pm
        eta = datetime.now() + timedelta(days=2)
        self.estimated_delivery = eta.strftime("%Y-%m-%d 15:00")

        self.db.execute("""
            INSERT INTO deliveries (order_id, name, address, phone, status, tracking_number, delivery_cost, estimated_delivery)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            self.order_id, self.name, self.address, self.phone,
            self.status, self.tracking_number, self.delivery_cost, self.estimated_delivery
        ), commit=True)

        print(f"\nDelivery Scheduled:")
        print(f" Tracking #: {self.tracking_number}")
        print(f" ETA: {self.estimated_delivery}")
        print(f" Cost: ${self.delivery_cost:.2f}\n")

    def cancel(self):
        """Cancel delivery for this specific instance."""
        self.status = "cancelled"
        self.db.execute("""
            UPDATE deliveries SET status='cancelled' WHERE order_id = ?
        """, (self.order_id,), commit=True)

    @staticmethod
    def cancel_by_order_id(order_id):
        """Cancel delivery when order is cancelled without Delivery object."""
        db = DBManager()
        db.execute("UPDATE deliveries SET status='cancelled' WHERE order_id = ?", (order_id,), commit=True)

    @staticmethod
    def list_all():
        """
        Returns all delivery records.
        """
        db = DBManager()
        return db.execute("""
            SELECT delivery_id, order_id, name, address, phone, status, tracking_number, delivery_cost, estimated_delivery
            FROM deliveries
            ORDER BY delivery_id DESC
        """).fetchall()
