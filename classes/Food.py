from classes.Item import Item

class Food(Item):
    """
    Represents a food item (e.g., produce, snacks).
    Stores a best-before date in the `extra` field.
    """

    def __init__(self, name, desc, price, best_before, imagePath=""):
        super().__init__(
            name=name,
            desc=desc,
            price=price,
            category="food",
            extra=best_before,   # best before date
            imagePath=imagePath
        )
