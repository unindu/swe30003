import re
import hashlib
from classes.db_manager import DBManager

class Account:
    """
    Manages user registration and login with basic validation and password hashing.
    """

    def __init__(self):
        self.db = DBManager()
        self._create_table()
        self.seed_default_staff()

    def _create_table(self):
        """
        Ensures the accounts table exists.
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

    # ----------------- Helpers ----------------- #

    def _hash(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def _valid_email(self, email):
        return re.match(r"[^@]+@[^@]+\.[^@]+", email)

    # ----------------- Core Features ----------------- #

    def register(self, username, email, password, role="customer"):
        """
        Register a new user with validation.
        """
        # --- Validation --- #
        if len(username.strip()) < 3:
            print("Username must be at least 3 characters.")
            return

        if not self._valid_email(email):
            print("Invalid email format. Example: name@example.com")
            return

        if len(password) < 5:
            print("Password must be at least 5 characters.")
            return

        hashed_pw = self._hash(password)

        try:
            self.db.execute("""
                INSERT INTO accounts (username, email, password, role)
                VALUES (?, ?, ?, ?)
            """, (username.strip(), email.strip(), hashed_pw, role), commit=True)

            print(f"Account created for {username}")

        except Exception as e:
            if "UNIQUE constraint" in str(e):
                print("Username or Email already exists.")
            else:
                print(f"Registration failed: {e}")

    def login(self, username, password):
        """
        Authenticate user and return session dict.
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

    # ----------------- Staff Seeding ----------------- #

    def seed_default_staff(self):
        """
        Ensures a staff account exists.
        """
        existing = self.db.fetchone("SELECT * FROM accounts WHERE role='staff'")
        if not existing:
            hashed_pw = self._hash("staff123")
            self.db.execute("""
                INSERT INTO accounts (username, email, password, role)
                VALUES (?, ?, ?, ?)
            """, ("staff", "staff@hexpress.com", hashed_pw, "staff"), commit=True)
            print("[INFO] Default staff account created (username: staff | password: staff123)")


# ----------------- Utility: View all Users (Staff Only) ----------------- #

def view_all_users():
    db = DBManager()
    users = db.execute("SELECT * FROM accounts").fetchall()
    print("\n---- Registered Users ----")
    print("ID | Username        | Email                        | Role")
    print("-------------------------------------------------------------")
    for account_id, username, email, pw, role in users:
        print(f"{account_id:<3}| {username:<15}| {email:<28}| {role}")
