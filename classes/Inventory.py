# classes/Inventory.py
from classes.ItemHolder import ItemHolder

"""
    Inventory represents the shared stock available for all users.
    
    Note for Adam:
    
    The Item class is extended to distinguish Food vs Alcohol,
    so consider adding a 'category' column to the items table.
    
    Example:
        category TEXT CHECK(category IN ('food', 'alcohol'))
    
    This will allow:
    - Filtering items by type in the UI 
    - Enforcing age restrictions when adding to cart
    - Displaying food/alcohol differently in inventory lists
"""

class Inventory(ItemHolder):
    def __init__(self):
        super().__init__()

    def list_items(self):
        rows = self.cursor.execute("""
            SELECT i.name, i.desc, i.price, s.quantity
            FROM items i
            JOIN stock s ON i.id = s.id
            WHERE s.location = 'Inventory'
        """).fetchall()

        if not rows:
            print("\nInventory is empty.\n")
            return

        print("\n--- INVENTORY ---")
        print(f"{'Name':<15} {'Qty':<5} {'Price':<8} Description")
        print("-" * 60)
        for name, desc, price, qty in rows:
            print(f"{name:<15} {qty:<5} ${price:<8.2f} {desc}")
        print()
