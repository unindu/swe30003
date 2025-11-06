from classes.Item import Item

class Alcohol(Item):
    """
    Represents an alcohol item in the inventory.
    Extends Item by specifying alcohol content as the extra field.
    """

    def __init__(self, name, desc, price, alcohol_content, imagePath=""):
        super().__init__(
            name=name,
            desc=desc,
            price=price,
            category="alcohol",
            extra=alcohol_content,   # stored as ABV/percentage
            imagePath=imagePath
        )
