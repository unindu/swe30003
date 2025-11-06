from classes.ItemHolder import ItemHolder

class Inventory(ItemHolder):
    """
    Access layer for viewing inventory items.
    Uses ItemHolder to interact with the items + stock tables.
    """

    def __init__(self):
        super().__init__()

    # ----------- Display Items ----------- #

    def list_items(self):
        """
        Display every item currently available (in stock where order_id = -1).
        """
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
        print(f"{'Name':<15} {'Qty':<5} {'Price':<8} {'Category':<10} Details")
        print("-" * 75)

        for name, desc, price, qty, category, extra in rows:
            detail = extra if extra else desc
            print(f"{name:<15} {qty:<5} ${price:<8.2f} {category:<10} {detail}")

        print()

    def list_items_by_category(self, category):
        """
        Display only items belonging to a specific category (e.g., 'food' or 'alcohol').
        """
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
        print(f"{'Name':<15} {'Qty':<5} {'Price':<8} Details")
        print("-" * 60)

        for name, desc, price, qty, _, extra in rows:
            detail = extra if extra else desc
            print(f"{name:<15} {qty:<5} ${price:<8.2f} {detail}")

        print()


# Manual test runner
if __name__ == "__main__":
    Inventory().list_items()
