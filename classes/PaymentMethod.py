"""
Mock payment gateway used by the Payment class.
No real transactions occur, only simulates success/failure responses.
"""

import time

class PaymentMethod:
    """
    Represents a simple third-party payment processor.
    Supports credit/debit card, AMEX, and PayPal-like options.
    """

    def __init__(self):
        self.methods = ["credit_card", "debit_card", "AMEX", "paypal"]

    def pay(self, amount, method="credit_card"):
        """
        Attempt to process payment.
        Returns success if method is supported.
        """
        if method not in self.methods:
            return {"success": False, "error": "Unsupported payment method"}

        # Fake transaction ID
        txn = f"TN{int(time.time() * 100)}"

        return {"success": True, "transaction_id": txn, "gateway": method}

    def add_method(self, method):
        """
        Adds a new payment option.
        """
        if method not in self.methods:
            self.methods.append(method)
            return True
        return False

    def remove_method(self, method):
        """
        Removes a payment option.
        """
        if method in self.methods:
            self.methods.remove(method)
            return True
        return False

    def refund(self, transaction_id, amount):
        """
        Mock refund action.
        Always succeeds for simplicity.
        """
        refund_id = f"REF{int(time.time() * 100)}"
        return {"success": True, "refund_id": refund_id, "amount_refunded": amount}
