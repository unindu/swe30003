from classes.Item import Item

class Alcohol(Item):
    def __init__(self, name, desc, price, alcohol_content, imagePath=""):
        super().__init__(name, desc, price, category="alcohol", extra=alcohol_content, imagePath=imagePath)
