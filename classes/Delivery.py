from classes.db_manager import DBManager
from datetime import datetime, timedelta

# Delivery class handles the delivery process
class Delivery:
    
    # initialise the Delivery class
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
        self._create_deliveries_table()
    
    # create the deliveries table if it doesn't exist
    def _create_deliveries_table(self):
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS deliveries (
                delivery_id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                address TEXT NOT NULL,
                phone TEXT NOT NULL,
                status TEXT NOT NULL,
                tracking_number TEXT,
                delivery_cost REAL NOT NULL,
                estimated_delivery TEXT
            )
        """, commit=True)

    # calculate the delivery cost based on the distance (hardcoded 10km)
    def calculate_delivery_cost(self, distance_km=10.0):
        self.delivery_cost = (5.00 + distance_km * 1.00) * 1.10  # base cost + $(2dp) per km + 10% GST
        return self.delivery_cost

    # deliver the order, called when order is created from Order class
    def schedule(self):
        
        # min address length is 10 char
        if not self.address or len(self.address) <= 10:
            print("Address is invalid, minimum of 10 characters")
            print("The order may still be completed")
            return

        self.status = "pending"
        self.tracking_number = f"DEL{self.order_id}"
        self.calculate_delivery_cost()
        
        # Calculate estimated delivery: 2 days from now at 3pm
        delivery_date = datetime.now() + timedelta(days=2)
        self.estimated_delivery = delivery_date.strftime("%Y-%m-%d 15:00")
        
        self._save_to_db()
    
    # insert order_id, name, address, contact_phone, status, tracking_number, delivery_cost, estimated_delivery into the deliveries table
    def _save_to_db(self):
        self.db.execute("""
            INSERT INTO deliveries (order_id, name, address, phone, status, tracking_number, delivery_cost, estimated_delivery)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (self.order_id, self.name, self.address, self.phone, self.status, self.tracking_number, self.delivery_cost, self.estimated_delivery), commit=True)
    
    # cancel the delivery by changing the status to cancelled with delivery object, used by Order.cancel()
    def cancel(self):
        self.status = "cancelled"
        self.db.execute("""
            UPDATE deliveries SET status = 'cancelled' WHERE order_id = ?
        """, (self.order_id,), commit=True)
    
    # cancel the delivery by changing the status to cancelled, no delivery object, used by Order.cancel()
    @staticmethod
    def cancel_by_order_id(order_id):
        db = DBManager()
        db.execute("UPDATE deliveries SET status = 'cancelled' WHERE order_id = ?", (order_id,), commit=True)