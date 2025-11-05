from classes.db_manager import DBManager

class ItemHolder:
    """
    Base class that provides DB access and item/stock manipulation.
    All inventory, cart, and order operations rely on this shared setup.
    """

    def __init__(self):
        self.db = DBManager()
        self.conn = self.db.conn
        self.cursor = self.db.cursor

    def setup_db(self):
        """Creates all tables required for items, stock, carts and orders."""

        # Users table (needed before orders & carts)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                account_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'customer'
            );
        """)

        # Items metadata
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                desc TEXT NOT NULL,
                price REAL NOT NULL,
                category TEXT NOT NULL,
                extra TEXT,
                imagePath TEXT
            );
        """)

        # Orders table (must exist before stock)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                total REAL NOT NULL,
                date TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                FOREIGN KEY(user_id) REFERENCES accounts(account_id)
            );
        """)

        # Stock table (order_id = -1 means "Inventory")
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock (
                stock_id INTEGER PRIMARY KEY AUTOINCREMENT,
                id INTEGER,
                quantity INTEGER NOT NULL,
                order_id INTEGER DEFAULT -1,
                FOREIGN KEY(id) REFERENCES items(id) ON DELETE CASCADE,
                UNIQUE(id, order_id)
            );
        """)

        # Cart storage per user
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS carts (
                cart_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                FOREIGN KEY(item_id) REFERENCES items(id),
                FOREIGN KEY(user_id) REFERENCES accounts(account_id),
                UNIQUE(item_id, user_id)
            );
        """)

        self.conn.commit()

    def add_item(self, name, desc, price, qty, image_path="assets/images/none.png", category="food", extra=None):
        """
        Adds or updates an item and ensures inventory stock exists (order_id = -1).
        """
        # Insert or update item metadata
        self.cursor.execute("""
            INSERT INTO items (name, desc, price, category, extra, imagePath)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                desc = excluded.desc,
                price = excluded.price,
                category = excluded.category,
                extra = excluded.extra,
                imagePath = excluded.imagePath;
        """, (name, desc, price, category, extra, image_path))

        # Insert stock for inventory (-1) if not present
        self.cursor.execute("""
            INSERT OR IGNORE INTO stock (id, quantity, order_id)
            SELECT id, ?, -1 FROM items WHERE name = ?;
        """, (qty, name))

        self.conn.commit()

    def update_stock(self, item_name, change, order_id=-1):
        """
        Adjusts stock levels for an item at a specific order_id (default = inventory).
        change can be positive (add) or negative (reduce).
        """
        item_id = self.cursor.execute("SELECT id FROM items WHERE name=?", (item_name,)).fetchone()

        if not item_id:
            print("Item does not exist.")
            return False

        item_id = item_id[0]

        self.cursor.execute("""
            INSERT INTO stock (id, quantity, order_id)
            VALUES (?, ?, ?)
            ON CONFLICT(id, order_id)
            DO UPDATE SET quantity = quantity + excluded.quantity;
        """, (item_id, change, order_id))

        self.conn.commit()
        return True

    def remove_item(self, item_name):
        """Deletes an item and cascades remove from carts/stock."""
        self.cursor.execute("DELETE FROM items WHERE name=?", (item_name,))
        self.conn.commit()


if __name__ == "__main__":
    holder = ItemHolder()
    holder.setup_db()
    print("Database setup complete.")
