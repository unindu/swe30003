import sqlite3


class ItemHolder:
    def __init__(self):
        self.conn = sqlite3.connect("inventory_database.db")
        self.cursor = self.conn.cursor()


    def setup_db(self):

        # This creates the table for items and their descriptions
        # It just holds item info basically
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                desc TEXT NOT NULL,
                price REAL NOT NULL,
                imagePath TEXT NOT NULL
            )
            """
        )

        # This is a table for items and where they are
        # iirc stockId is basically useless? But we need itemid to appear more
        # than once in the table, so itemid can't be the primary key.
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS stock (
                stock_id INTEGER PRIMARY KEY,
                id INTEGER,
                quantity INTEGER NOT NULL,
                location TEXT NOT NULL,
                FOREIGN KEY(id) REFERENCES items(id),
                UNIQUE(id, location)
            )
            """
        )
        self.conn.commit()


    def add_item(self, name, desc, price, image_path = "assets/images/none.png"):
        self.cursor.execute(
            # Insert or ignore, it silently drops it if it already the name already exists
            # No two items should have the EXACT same name, so hopefully no duplicates
            """
            INSERT OR IGNORE INTO items (name, desc, price, imagePath)
            VALUES (?, ?, ?, ?)
            """, (name, desc, price, image_path)
        )

        item_id = self.cursor.execute(
            """
            SELECT id FROM items WHERE name = ?
            """, (name,)
        ).fetchone()[0]

        # Also add the item to the stock table ONLY IF IT ISN'T THERE ALREADY
        self.cursor.execute(
            """
            INSERT OR IGNORE INTO stock (id, quantity, location)
            VALUES (?, ?, ?)
            """, (item_id, 0, "Inventory")
        )

        self.conn.commit()

    def update_stock(self, item_name, change, location):

        item_id = self.cursor.execute(
            """
            SELECT id FROM items WHERE name = ?
            """, (item_name,)
        ).fetchone()[0]

        if item_id is None:
            raise ValueError(f"Item '{item_name}' does not exist in the database.")

        self.cursor.execute(
            """
            UPDATE stock SET quantity = quantity + ? WHERE id = ? AND location = ?
            """, (change, item_id, location)
        )
        self.conn.commit()

if __name__ == "__main__":
    # Just to test making the table
    holder = ItemHolder()

