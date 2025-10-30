# classes/Cart.py
from classes.ItemHolder import ItemHolder

class Cart(ItemHolder):
    """
    Represents a user's shopping cart.
    Each cart is stored as a separate 'location' inside the stock table
    using the naming convention <user_id>_cart.
    
    The cart works by moving item quantities between:
      - Inventory (global stock pool)
      - <user_id>_cart (private cart location for that user)

    """

    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id

    def add_to_cart(self, item_name, qty):
        try:
            add_item_id = self.cursor.execute("SELECT id FROM items WHERE name=?", (item_name,)).fetchone()[0]
        except TypeError:
            print("Item not found.")
            return False
        available = self.cursor.execute("""
            SELECT quantity FROM stock 
            JOIN items ON stock.id = items.id
            WHERE items.id=? AND order_id = -1
        """, (add_item_id,)).fetchone()

        if not available or available[0] < qty:
            print(f"Not enough stock. Available: {available[0] if available else 0}")
            return False

        self.cursor.execute("""
            INSERT INTO carts (item_id, quantity, user_id)
            SELECT id, ?, ? FROM items WHERE id=?
            ON CONFLICT(item_id, user_id)
            DO UPDATE SET quantity = quantity + excluded.quantity
        """, (qty, self.user_id, add_item_id))

        self.cursor.execute("""
            UPDATE stock SET quantity = quantity - ? 
            WHERE id=? AND order_id = -1
        """, (qty, add_item_id))

        self.conn.commit()
        print(f"Added {qty}x {item_name} to your cart.")
        return True

    def remove_from_cart(self, item_name, qty):
        try:
            remove_item_id = self.cursor.execute("SELECT id FROM items WHERE name=?", (item_name,)).fetchone()[0]
        except TypeError:
            print("Item not found.")
            return False

        if remove_item_id is None:
            print("Item not found.")
            return False
        available = self.cursor.execute("""
            SELECT quantity FROM carts
            JOIN items ON carts.item_id = items.id
            WHERE items.id=? AND user_id=?
        """, (remove_item_id, self.user_id)).fetchone()

        if not available or available[0] < qty:
            print("You don't have that many in your cart.")
            return False

        self.cursor.execute("""
            UPDATE carts SET quantity = quantity - ?
            WHERE item_id=? AND user_id=?
        """, (qty, remove_item_id, self.user_id))

        self.cursor.execute("""
            INSERT INTO stock (id, quantity, order_id)
            SELECT id, ?, -1 FROM items WHERE id=?
            ON CONFLICT(id, order_id)
            DO UPDATE SET quantity = quantity + excluded.quantity
        """, (qty, remove_item_id))

        self.conn.commit()
        print(f"Returned {qty}x {item_name} to Inventory.")
        return True

    def view_cart(self):

        items = self.cursor.execute("""
            SELECT items.name, items.price, carts.quantity FROM carts
            JOIN items ON carts.item_id = items.id
            WHERE carts.user_id = ?
        """, (self.user_id,)).fetchall()

        if not items:
            print("Cart is empty.")
            return 0

        print("\n--- YOUR CART ---")
        total = 0
        for name, price, qty in items:
            subtotal = price * qty
            total += subtotal
            print(f"{name:<15} x{qty:<3} = ${subtotal:.2f}")

        print(f"TOTAL = ${total:.2f}\n")
        return total

