from classes.db_manager import DBManager
from classes.PaymentMethod import PaymentMethod
from datetime import datetime


class Payment:
    """
    Handles processing and recording of payments for orders.
    Works with PaymentMethod (mock gateway) and stores results in DB.
    """

    def __init__(self, order_id, amount):
        self.order_id = order_id
        self.amount = amount
        self.status = "pending"
        self.transaction_id = None
        self.payment_date = None
        self.gateway = None
        self.db = DBManager()
        self._create_table()

    def _create_table(self):
        """Ensures the payments table exists."""
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                status TEXT NOT NULL,
                transaction_id TEXT,
                payment_date TEXT,
                FOREIGN KEY(order_id) REFERENCES orders(order_id)
            );
        """, commit=True)

    # ---------------- Processing ---------------- #

    def process(self, method="credit_card"):
        """Processes the payment using a mock payment gateway."""
        self.status = "processing"
        self.gateway = PaymentMethod()

        result = self.gateway.pay(self.amount, method)

        if result.get("success"):
            self.status = "completed"
            self.transaction_id = result.get("transaction_id", f"TX{self.order_id}")
            self.payment_date = datetime.now().strftime("%Y-%m-%d %H:%M")
        else:
            self.status = "failed"

        self._save()
        return self.status == "completed"

    # ---------------- Refund ---------------- #

    def refund(self):
        """Attempts to refund a completed payment."""
        if self.status != "completed":
            return False

        if not self.gateway:
            self.gateway = PaymentMethod()

        result = self.gateway.refund(self.transaction_id, self.amount)

        if result.get("success"):
            self.status = "refunded"
            self.db.execute("""
                UPDATE payments SET status=? WHERE order_id=?
            """, (self.status, self.order_id), commit=True)
            return True

        return False

    # ---------------- DB Storage ---------------- #

    def _save(self):
        """Stores payment result in the database."""
        self.db.execute("""
            INSERT INTO payments (order_id, amount, status, transaction_id, payment_date)
            VALUES (?, ?, ?, ?, ?)
        """, (self.order_id, self.amount, self.status, self.transaction_id, self.payment_date), commit=True)

    # ---------------- Utility ---------------- #

    def generate_invoice(self):
        """Prints a plain-text invoice."""
        print("\nPAYMENT INVOICE")
        print(f"Order ID: {self.order_id}")
        print(f"Amount:   ${self.amount:.2f}")
        print(f"Status:   {self.status}")
        print(f"Trans ID: {self.transaction_id}")
        print(f"Date:     {self.payment_date}\n")


if __name__ == "__main__":
    Payment(1, 50).process()
