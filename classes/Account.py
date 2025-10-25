# classes/Account.py
import hashlib
from classes.db_manager import DBManager

class Account:
    """
    Handles user account creation and authentication.

    """

    def __init__(self):
        # Shared database connection (no direct sqlite calls in this class)
        self.db = DBManager()
        self._create_table()

    def _create_table(self):
        """
        Creates the accounts table if it does not already exist.
        Includes UNIQUE constraints to prevent duplicate usernames or emails.
        """
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                account_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'customer'
            )
        """, commit=True)

    def _hash(self, password):
        """
        Returns a SHA-256 hash of the password.
        This prevents storing raw passwords in the database.
        """
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self, username, email, password, role="customer"):
        """
        Registers a new user with hashed password.
        If the username or email is already taken, the UNIQUE constraint will trigger an exception.
        """
        hashed_pw = self._hash(password)
        try:
            self.db.execute("""
                INSERT INTO accounts (username, email, password, role)
                VALUES (?, ?, ?, ?)
            """, (username, email, hashed_pw, role), commit=True)
            print(f"Account created for {username}")
        except Exception as e:
            print(f"Registration failed: {e}")

    def login(self, username, password):
        """
        Authenticates the user by verifying username and hashed password.
        Returns a user session dictionary if successful, otherwise None.
        """
        hashed_pw = self._hash(password)

        user = self.db.fetchone("""
            SELECT account_id, username, role
            FROM accounts
            WHERE username=? AND password=?
        """, (username, hashed_pw))

        if user:
            print(f"Welcome back, {user[1]}! (role: {user[2]})")
            return {"user_id": user[0], "username": user[1], "role": user[2]}

        print("Invalid username or password.")
        return None
