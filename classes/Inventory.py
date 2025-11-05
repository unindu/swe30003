# classes/Inventory.py
from classes.ItemHolder import ItemHolder

class Inventory(ItemHolder):
    def __init__(self):
        super().__init__()

    def list_items(self):
        rows = self.cursor.execute("""
            SELECT i.name, i.desc, i.price, s.quantity, i.category, i.extra
            FROM items i
            JOIN stock s ON i.id = s.id
            WHERE s.order_id = -1
        """).fetchall()

        if not rows:
            print("\nInventory is empty.\n")
            return

        print("\n--- INVENTORY ---")
        print(f"{'Name':<15} {'Qty':<5} {'Price':<8} {'Category':<8} Details")
        print("-" * 75)
        for name, desc, price, qty, category, extra in rows:
            detail = extra if extra else desc
            print(f"{name:<15} {qty:<5} ${price:<8.2f} {category:<8} {detail}")
        print()

    def list_items_by_category(self, category):
        rows = self.cursor.execute("""
            SELECT i.name, i.desc, i.price, s.quantity, i.category, i.extra
            FROM items i
            JOIN stock s ON i.id = s.id
            WHERE s.order_id = -1 AND i.category = ?
         """, (category,)).fetchall()

        if not rows:
            print(f"\nNo {category} items available.\n")
            return

        print(f"\n--- {category.upper()} ---")
        for name, desc, price, qty, _, extra in rows:
            detail = extra if extra else desc
            print(f"{name:<15} x{qty:<3} ${price:.2f} - {detail}")
        print()


if __name__ == "__main__":
    inventory = Inventory()
    inventory.list_items()