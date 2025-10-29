from classes.db_manager import DBManager    # used for database connection
from classes.PaymentMethod import PaymentMethod

from datetime import datetime # used for timestamp for payment_date

# Payment class handles the payment process
class Payment:
    
    # initialise the Payment class
    def __init__(self, order_id, cost):
        self.order_id = order_id
        self.cost = cost
        self.status = "pending"
        self.transaction_id = None
        self.payment_date = None
        self.payment = None  # Third party payment gateway (PaymentMethod)
        self.db = DBManager() # database connection
        self._create_payments_table()
    
    # creates the payments table if it doesn't exist
    def _create_payments_table(self):
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                status TEXT NOT NULL,
                transaction_id TEXT,
                payment_date TEXT
            )
        """, commit=True)
    
    # payment using gateway
    def process(self, payment_method="credit_card"):
        
        self.status = "processing" 
        
        # Use payment gateway to process payment
        self.payment = PaymentMethod()  # Store gateway reference
        result = self.payment.pay(self.cost, payment_method)
        
        if result["success"]:
            self.status = "completed"
            self.transaction_id = result.get("transaction_id", f"TN{self.order_id}")
            self.payment_date = datetime.now().strftime("%Y-%m-%d %H:%M")
            self._save_to_db()
            return True
        else:
            self.status = "failed"
            self._save_to_db()
            return False
    
    # generate invoice (print) for the payment
    def generateInvoice(self):
        print(f"\nPAYMENT INVOICE")
        print(f"Order ID: {self.order_id}")
        print(f"Date: {self.payment_date}")
        print(f"Cost: ${self.cost:.2f}")
        print(f"Status: {self.status}")
        print(f"Transaction ID: {self.transaction_id}")
        print()
    
    # create payment record in the database
    def _save_to_db(self):

        # insert order_id, amount, status, transaction_id, payment_date
        self.db.execute("""
            INSERT INTO payments (order_id, amount, status, transaction_id, payment_date)
            VALUES (?, ?, ?, ?, ?)
        """, (self.order_id, self.cost, self.status, self.transaction_id, self.payment_date), commit=True)
    
    # refund payment, called when order is cancelled from Order class
    def refund(self):

        # check if payment is completed
        if self.status != "completed":
            return False
        
        # Call the payment gateway to process refund
        if not self.payment:
            self.payment = PaymentMethod()
        result = self.payment.refund(self.transaction_id, self.cost)
        
        if result["success"]:
            self.status = "refunded"
            self.db.execute("""
                UPDATE payments SET status = ? WHERE order_id = ?
            """, (self.status, self.order_id), commit=True)
            return True

        return False # if refund is not successful