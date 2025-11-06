import re
import hashlib
from classes.db_manager import DBManager

class Account:
    """
    Handles account creation, secure password storage, and user authentication.
    Provides basic validation and seeds a default staff account for system access.
    """

    def __init__(self):
        self.db = DBManager()
        self._create_table()
        self.seed_default_staff()

    def _create_table(self):
        """Creates the accounts table if it does not already exist."""
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                account_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'customer'
            )
        """, commit=True)

    # -------- Password + Input Validation -------- #

    def _hash(self, password):
        """Returns a secure SHA-256 hash of the password."""
        return hashlib.sha256(password.encode()).hexdigest()

    def _valid_email(self, email):
        """Checks for a valid email format."""
        return re.match(r"[^@]+@[^@]+\.[^@]+", email)

    # -------- Registration + Login -------- #

    def register(self, username, email, password, role="customer"):
        """
        Creates a new user account with field validation.
        """
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
            if "UNIQUE" in str(e):
                print("Username or Email already exists.")
            else:
                print(f"Registration failed: {e}")

    def login(self, username, password):
        """
        Validates username + password and returns a user session dictionary.
        """
        hashed_pw = self._hash(password)

        record = self.db.fetchone("""
            SELECT account_id, username, role
            FROM accounts
            WHERE username=? AND password=?
        """, (username, hashed_pw))

        if record:
            print(f"Welcome back, {record[1]}! (role: {record[2]})")
            return {"user_id": record[0], "username": record[1], "role": record[2]}

        print("Invalid username or password.")
        return None

    # -------- Default System Accounts -------- #

    def seed_default_staff(self):
        """Creates a staff account if none exists (ensures admin access)."""
        existing = self.db.fetchone("SELECT 1 FROM accounts WHERE role='staff'")
        if not existing:
            hashed_pw = self._hash("staff123")
            self.db.execute("""
                INSERT INTO accounts (username, email, password, role)
                VALUES (?, ?, ?, ?)
            """, ("staff", "staff@hexpress.com", hashed_pw, "staff"), commit=True)
            print("[INFO] Default staff account created (staff / staff123)")

    def seed_default_customer(self):
        """Creates a quick-login demo customer if not present."""
        existing = self.db.fetchone("SELECT 1 FROM accounts WHERE username='customer'")
        if not existing:
            hashed_pw = self._hash("customer123")
            self.db.execute("""
                INSERT INTO accounts (username, email, password, role)
                VALUES (?, ?, ?, ?)
            """, ("customer", "customer@example.com", hashed_pw, "customer"), commit=True)
            print("[INFO] Default customer created (customer / customer123)")


# -------- Staff Utility: List All Users -------- #

def view_all_users():
    """Displays all registered user accounts (staff use only)."""
    db = DBManager()
    users = db.execute("SELECT * FROM accounts").fetchall()

    print("\n---- Registered Users ----")
    print("ID | Username        | Email                        | Role")
    print("-------------------------------------------------------------")
    for account_id, username, email, pw, role in users:
        print(f"{account_id:<3}| {username:<15}| {email:<28}| {role}")
