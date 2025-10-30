class Item:
    def __init__(self, name, desc, price, category="food", extra=None, imagePath=""):
        self.name = name
        self.desc = desc
        self.price = price
        self.category = category
        self.extra = extra
        self.imagePath = imagePath
