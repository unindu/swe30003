import sqlite3
import os

class DBManager:
    """
    Handles a single shared connection to the SQLite database.
    Provides helper methods for executing queries and retrieving results.
    """

    def __init__(self):
        # Locate project root (parent of /classes/)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(base_dir, "inventory_database.db")

        # Establish connection (foreign key support enabled)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.cursor = self.conn.cursor()

    # ----------------- Query Helpers ----------------- #

    def execute(self, query, params=(), commit=False):
        """
        Execute a SQL statement.
        Set commit=True if the operation modifies data.
        """
        result = self.cursor.execute(query, params)
        if commit:
            self.conn.commit()
        return result

    def fetchone(self, query, params=()):
        """
        Return a single result row or None.
        """
        return self.cursor.execute(query, params).fetchone()

    def fetchall(self, query, params=()):
        """
        Return all result rows as a list.
        """
        return self.cursor.execute(query, params).fetchall()

