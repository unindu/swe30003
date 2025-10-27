# PaymentMethod class handles the third-party payment (this is a mock, no actual implementation)
class PaymentMethod:

    # initialise the PaymentMethod class
    def __init__(self):
        self.paymentMethods = ["credit_card", "debit_card", "AMEX", "paypal"]
    
    # called when payment is processed from Payment class
    def pay(self, amount, method="credit_card"):

        # check if method is valid
        if method not in self.paymentMethods:
            return {"success": False, "error": "Method not supported"}
        
        # payment always succeeds if method is valid
        return {
            "success": True,
            "transaction_id": f"TN{int(__import__('time').time() * 100)}",
            "gateway": method
        }
    
    # add a new payment method
    def addMethod(self, method):
        
        if method not in self.paymentMethods:
            self.paymentMethods.append(method)
            return True

        return False  # already exists
    
    # remove a payment method
    def removeMethod(self, method):

        if method in self.paymentMethods:
            self.paymentMethods.remove(method)
            return True

        return False  # not found
    
    # refund payment, called when payment is refunded from Payment class
    def refund(self, transaction_id, amount):

        return {
            "success": True, # always succeeds
            "refund_id": f"REF{int(__import__('time').time() * 100)}",
            "amount_refunded": amount
        }