from classes.ItemHolder import ItemHolder

class Cart(ItemHolder):
    """
    Shopping cart for a user.
    Manages movement of item quantities between global inventory (stock table)
    and the user's cart (carts table).
    """

    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id

    # ----------------- Add to Cart ----------------- #
    def add_to_cart(self, item_name, qty):
        """
        Add an item to the user's cart if sufficient stock exists.
        Reduces available stock in the inventory.
        """
        try:
            item_id = self.cursor.execute(
                "SELECT id FROM items WHERE name=?",
                (item_name,)
            ).fetchone()[0]
        except TypeError:
            print("Item not found.")
            return False

        available = self.cursor.execute("""
            SELECT quantity FROM stock 
            WHERE id=? AND order_id=-1
        """, (item_id,)).fetchone()

        if not available or available[0] < qty:
            print(f"Not enough stock. Available: {available[0] if available else 0}")
            return False

        # Add to cart (increments if already present)
        self.cursor.execute("""
            INSERT INTO carts (item_id, quantity, user_id)
            VALUES (?, ?, ?)
            ON CONFLICT(item_id, user_id)
            DO UPDATE SET quantity = quantity + excluded.quantity
        """, (item_id, qty, self.user_id))

        # Reduce stock
        self.cursor.execute("""
            UPDATE stock SET quantity = quantity - ?
            WHERE id=? AND order_id=-1
        """, (qty, item_id))

        self.conn.commit()
        print(f"Added {qty}x {item_name} to your cart.")
        return True

    # ----------------- Remove from Cart ----------------- #
    def remove_from_cart(self, item_name, qty):
        """
        Remove quantity from cart and return it to inventory.
        """
        try:
            item_id = self.cursor.execute(
                "SELECT id FROM items WHERE name=?",
                (item_name,)
            ).fetchone()[0]
        except TypeError:
            print("Item not found.")
            return False

        owned = self.cursor.execute("""
            SELECT quantity FROM carts
            WHERE item_id=? AND user_id=?
        """, (item_id, self.user_id)).fetchone()

        if not owned or owned[0] < qty:
            print("You don't have that many in your cart.")
            return False

        self.cursor.execute("""
            UPDATE carts SET quantity = quantity - ?
            WHERE item_id=? AND user_id=?
        """, (qty, item_id, self.user_id))

        # Return items to inventory
        self.cursor.execute("""
            INSERT INTO stock (id, quantity, order_id)
            VALUES (?, ?, -1)
            ON CONFLICT(id, order_id)
            DO UPDATE SET quantity = quantity + excluded.quantity
        """, (item_id, qty))

        self.conn.commit()
        print(f"Returned {qty}x {item_name} to inventory.")
        return True

    # ----------------- View Cart ----------------- #
    def view_cart(self):
        """
        Display cart contents and return total cost.
        """
        items = self.cursor.execute("""
            SELECT items.name, items.price, carts.quantity
            FROM carts
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
