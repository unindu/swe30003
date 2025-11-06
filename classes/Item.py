class Item:
    """
    Base item model used by all product types.
    """

    def __init__(self, name, desc, price, category="food", extra=None, imagePath=""):
        self.name = name            # Item name (e.g., "Apples")
        self.desc = desc            # Simple text description
        self.price = price          # Price per unit
        self.category = category    # "food" or "alcohol"
        self.extra = extra          # e.g., best-before (food) or %ABV (alcohol)
        self.imagePath = imagePath  # Reserved for UI use (unused in CLI)
