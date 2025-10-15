from classes.ItemHolder import ItemHolder

class Order(ItemHolder):
    def __init__(self):
        super().__init__()

    # Items should only be added to order
    # After payment and delivery are verified
    # Please do not use this function to update the Inventory locatio
    def update_stock(self, item_name, change, location):
        """
        Convention for location is <user-id>_order
        Amount can be positive or negative
        (putting into cart/taking out of cart)
        """
        super().update_stock(item_name, change, location)
        super().update_stock(item_name, -change, "Inventory")
        # TODO, discuss whether we keep orders in the db or drop them


    # TODO, sales report stuff, delivery and payment verification, refunds?


