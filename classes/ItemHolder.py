import sqlite3


class ItemHolder:
    def __init__(self):
        self.conn = sqlite3.connect("items.db")
        self.cursor = self.conn.cursor()

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS items (
            name text,
            desc text,
            price real,
            imagePath text  
        )""")

    def setup_db(self):

        # This creates the table for items and their descriptions
        # It just holds item info basically
        self.cursor.execute(
            """
            CREATE TABLE items (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                desc TEXT NOT NULL
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
            CREATE TABLE stock (
                stock_id INTEGER PRIMARY KEY,
                id INTEGER,
                quantity INTEGER NOT NULL,
                location TEXT NOT NULL,
                FOREIGN KEY(id) REFERENCES items(id)
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
        self.conn.commit()



if __name__ == "__main__":
    # Just to test making the table
    holder = ItemHolder()
    holder.setup_db()
    holder.add_item("Test item", "This is a test item", 10.00)
    holder.add_item("Silly item", "This is a silly item", 7.57)

