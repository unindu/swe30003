from classes.Account import Account, view_all_users
from classes.Inventory import Inventory
from classes.Cart import Cart
from classes.Order import Order
from classes.SalesReport import SalesReport, sales_report_menu, print_as_table
from classes.ItemHolder import ItemHolder
from classes.Delivery import Delivery

# ===== CLI UI COLOURS =====
RESET = "\033[0m"
BOLD = "\033[1m"

BLUE = "\033[38;2;150;200;255m"
GREEN = "\033[38;2;144;238;144m"
YELLOW = "\033[38;2;255;255;179m"
RED = "\033[38;2;255;160;122m"
GREY_BG = "\033[48;2;40;40;40m"


def header(title):
    print(f"\n{GREY_BG}{BOLD}  {title}  {RESET}\n")


def success(msg):
    print(f"{GREEN}[✓] {msg}{RESET}")


def warning(msg):
    print(f"{YELLOW}[!] {msg}{RESET}")


def error(msg):
    print(f"{RED}[✗] {msg}{RESET}")


# === Setup DB & Default Data ===
ItemHolder().setup_db()
ItemHolder().seed_default_items()
Account().seed_default_staff()
Account().seed_default_customer()
Delivery.ensure_table()


# ===== LOGIN FLOW =====
def login_flow():
    account = Account()

    while True:
        header("Login / Register")
        print("1. Login")
        print("2. Register")
        print("3. Exit")

        choice = input("> ").strip()

        if choice == "1":
            username = input("Username: ")
            password = input("Password: ")
            user = account.login(username, password)
            if user:
                return user

        elif choice == "2":
            username = input("Create username: ")
            email = input("Email: ")
            password = input("Create password: ")
            account.register(username, email, password)

        elif choice == "3":
            print("\nGoodbye!\n")
            exit()

        else:
            error("Invalid selection")


# ===== STAFF MENU =====
def staff_menu(user):
    inventory = Inventory()

    while True:
        header(f"Hawthorn Express — Staff ({user['username']})")
        print("1. View Inventory")
        print("2. Add Item")
        print("3. Adjust Stock")
        print("4. View Users")
        print("5. Sales Reports")
        print("6. View Deliveries")
        print("7. Logout")

        choice = input("> ").strip()

        match choice:
            case "1":
                inventory.list_items()

            case "2":
                header("Add Item to Inventory")
                name = input("Item name: ")
                desc = input("Description: ")
                price = float(input("Price: "))
                qty = int(input("Quantity: "))

                category = input("Category (food/alcohol): ").strip().lower()
                extra = input("Best before date / Alcohol % (optional): ").strip() or None

                inventory.add_item(name, desc, price, qty, category=category, extra=extra)
                success("Item added successfully.")

            case "3":
                name = input("Item name: ")
                qty = int(input("Quantity change (+/-): "))
                inventory.update_stock(name, qty, -1)

            case "4":
                view_all_users()

            case "5":
                sales_report_menu()

            case "6":
                deliveries = Delivery.list_all()
                if not deliveries:
                    warning("No deliveries found.")
                else:
                    header("All Deliveries")
                    print(f"{'Del ID':<8} {'Order ID':<9} {'Name':<12} {'Status':<12} {'ETA':<18} {'Cost':<8}")
                    print("-" * 70)
                    for d in deliveries:
                        delivery_id, order_id, name, address, phone, status, tracking, cost, eta = d
                        print(f"{delivery_id:<8} {order_id:<9} {name[:12]:<12} {status:<12} {eta:<18} ${cost:<8.2f}")
                input("\nPress ENTER to continue...")

            case "7":
                return

            case _:
                error("Invalid selection")


# ===== CUSTOMER MENU =====
def main_menu(user):
    inventory = Inventory()
    cart = Cart(user["user_id"])
    order = Order(user["user_id"])

    while True:
        header(f"Hawthorn Express — {user['username']}")
        print("1. Browse All Items")
        print("2. Browse Food Only")
        print("3. Browse Alcohol Only")
        print("4. Add to Cart")
        print("5. View Cart")
        print("6. Remove from Cart")
        print("7. Checkout")
        print("8. Past Orders")
        print("9. Logout")

        choice = input("> ").strip()

        match choice:
            case "1":
                inventory.list_items()

            case "2":
                inventory.list_items_by_category("food")

            case "3":
                inventory.list_items_by_category("alcohol")

            case "4":
                item = input("Item name: ")
                qty = int(input("Quantity: "))
                cart.add_to_cart(item, qty)

            case "5":
                cart.view_cart()

            case "6":
                item = input("Item name: ")
                qty = int(input("Quantity: "))
                cart.remove_from_cart(item, qty)

            case "7":
                header("Checkout")
                name = input("Name for delivery: ")
                address = input("Address: ")
                phone = input("Phone: ")

                print("\nPayment Method:\n1. Credit Card\n2. Debit Card\n3. PayPal")
                method = input("> ").strip()
                method_map = {"1": "credit_card", "2": "debit_card", "3": "paypal"}

                order.checkout(name, address, phone, method_map.get(method, "credit_card"))

            case "8":
                sr = SalesReport()
                data = sr.user_orders(user["user_id"])
                print_as_table(f"Orders for {user['username']}", ["Order ID", "Date", "Total", "Status"], data)

            case "9":
                return

            case _:
                error("Invalid selection")


# ===== PROGRAM START =====
if __name__ == "__main__":
    while True:
        user = login_flow()
        if user['role'] == "customer":
            main_menu(user)
        elif user['role'] in ["staff", "admin"]:
            staff_menu(user)
        else:
            error("Invalid role.")
