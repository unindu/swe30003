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
        self.location = f"{user_id}_cart"  # unique cart stock location per user

    def add_to_cart(self, item_name, qty):

        available = self.cursor.execute("""
            SELECT quantity FROM stock 
            JOIN items ON stock.id = items.id
            WHERE items.name=? AND location='Inventory'
        """, (item_name,)).fetchone()

        if not available or available[0] < qty:
            print(f"Not enough stock. Available: {available[0] if available else 0}")
            return False

        self.cursor.execute("""
            INSERT INTO stock (id, quantity, location)
            SELECT id, ?, ? FROM items WHERE name=?
            ON CONFLICT(id, location)
            DO UPDATE SET quantity = quantity + excluded.quantity
        """, (qty, self.location, item_name))

        self.cursor.execute("""
            UPDATE stock SET quantity = quantity - ? 
            WHERE id=(SELECT id FROM items WHERE name=?) AND location='Inventory'
        """, (qty, item_name))

        self.conn.commit()
        print(f"Added {qty}x {item_name} to your cart.")
        return True

    def remove_from_cart(self, item_name, qty):

        available = self.cursor.execute("""
            SELECT quantity FROM stock
            JOIN items ON stock.id = items.id
            WHERE items.name=? AND location=?
        """, (item_name, self.location)).fetchone()

        if not available or available[0] < qty:
            print("You don't have that many in your cart.")
            return False

        self.cursor.execute("""
            UPDATE stock SET quantity = quantity - ?
            WHERE id=(SELECT id FROM items WHERE name=?) AND location=?
        """, (qty, item_name, self.location))

        self.cursor.execute("""
            INSERT INTO stock (id, quantity, location)
            SELECT id, ?, 'Inventory' FROM items WHERE name=?
            ON CONFLICT(id, location)
            DO UPDATE SET quantity = quantity + excluded.quantity
        """, (qty, item_name))

        self.conn.commit()
        print(f"Returned {qty}x {item_name} to Inventory.")
        return True

    def view_cart(self):

        items = self.cursor.execute("""
            SELECT i.name, i.price, s.quantity
            FROM stock s
            JOIN items i ON s.id = i.id
            WHERE s.location = ?
        """, (self.location,)).fetchall()

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
