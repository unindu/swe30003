import sqlite3

class DBManager:
    _connection = None
    _cursor = None

    def __init__(self):
        if DBManager._connection is None:
            DBManager._connection = sqlite3.connect("inventory_database.db", check_same_thread=False)
            DBManager._connection.execute("PRAGMA foreign_keys = ON;")  # Always enable FKs
            DBManager._cursor = DBManager._connection.cursor()

        self.conn = DBManager._connection
        self.cursor = DBManager._cursor

    def execute(self, query, params=(), commit=False):
        result = self.cursor.execute(query, params)
        if commit:
            self.conn.commit()
        return result

    def fetchone(self, query, params=()):
        return self.cursor.execute(query, params).fetchone()

    def fetchall(self, query, params=()):
        return self.cursor.execute(query, params).fetchall()

