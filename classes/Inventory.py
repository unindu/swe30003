# classes/Inventory.py
from classes.ItemHolder import ItemHolder

class Inventory(ItemHolder):
    def __init__(self):
        super().__init__()

    def list_items(self):
        rows = self.cursor.execute("""
            SELECT i.name, i.desc, i.price, s.quantity
            FROM items i
            JOIN stock s ON i.id = s.id
            WHERE s.order_id = -1 
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

if __name__ == "__main__":
    inventory = Inventory()
    inventory.list_items()