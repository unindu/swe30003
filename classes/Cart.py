from classes.ItemHolder import ItemHolder

class Cart(ItemHolder):
    def __init__(self):
        super().__init__()

    def update_stock(self, item_name, change, location):
        """
        Convention for location is <user-id>_order
        Amount can be positive or negative
        (putting into cart/taking out of cart)
        """
        super().update_stock(item_name, change, location)
        # TODO, feels like smth else should be here
