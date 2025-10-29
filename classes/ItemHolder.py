"""
Note for Adam:

This file was updated to use DBManager instead of creating its own sqlite connection.
No functional logic has changed.

The stock update query now uses `ON CONFLICT DO UPDATE SET quantity = quantity + excluded.quantity`.
This prevents duplicate stock rows across locations and ensures Cart/Order operations stay consistent.
No changes required from Item as this is purely a stability improvement.


"""

from classes.db_manager import DBManager

class ItemHolder:
    def __init__(self):
        self.db = DBManager()
        self.conn = self.db.conn
        self.cursor = self.db.cursor


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
                FOREIGN KEY(id) REFERENCES items(id) ON DELETE CASCADE,
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


    # change must be a positive or negative integer
    def update_stock(self, item_name, change, location):
        """
        item_name: str - name of the item
        change: int - positive or negative integer
        location: str - name of location
        Location is MOST important, updating stock for "inventory" will not work, it must be "Inventory"
        Convention for user itemHolders is <user_id>_cart or <user_id>_order
        """
        item_id = self.cursor.execute(
            """
            SELECT id FROM items WHERE name = ?
            """, (item_name,)
        ).fetchone()[0]

        # Try and insert this new stock, *but* if it already exists
        # (I.e. there is a conflict with the id, location unique rule)
        # Then update the quantity
        self.cursor.execute(
        """
        INSERT INTO stock (id, quantity, location)
        VALUES (?, ?, ?)
        ON CONFLICT(id, location)
        DO UPDATE SET quantity = quantity + excluded.quantity
        """, (item_id, change, location)
        )   

        self.conn.commit()

    def remove_item(self, item_name):
        self.cursor.execute(
            """
            DELETE FROM items WHERE name = ?;
            """, (item_name,)
        )

        self.conn.commit()


if __name__ == "__main__":
    # Just to test making the table
    holder = ItemHolder()
    holder.setup_db()

