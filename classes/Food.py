from classes.Item import Item

class Food(Item):
    def __init__(self, name, desc, price, best_before, imagePath=""):
        super().__init__(name, desc, price, category="food", extra=best_before, imagePath=imagePath)

