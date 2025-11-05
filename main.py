# main.py
from classes.Account import Account, view_all_users
from classes.Inventory import Inventory
from classes.Cart import Cart
from classes.Order import Order
from classes.SalesReport import SalesReport, sales_report_menu
from classes.ItemHolder import ItemHolder
from classes.Delivery import Delivery

ItemHolder().setup_db()
Account().seed_default_staff()
Delivery.ensure_table()


"""
Main CLI controller for Hawthorn Express.

Acts as the presentation layer for Assignment 3:
- Handles all user interaction (input/output)
- Calls domain-layer classes (Account, Inventory, Cart, Order)
- Will later be replaced or extended by Flask routes for the web interface

"""

def login_flow():
    """
    Manages the login and registration loop for users.
    Uses Account class for authentication and registration.
    Returns a user session dict on successful login.
    """
    account = Account()

    while True:
        print("\n=== Login / Register ===")
        print("1. Login")
        print("2. Register")
        print("3. Exit")
        choice = input("> ")

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
            print("Goodbye!")
            exit()

        else:
            print("Invalid selection")

def staff_menu(user):
    print(f"\n=== Hawthorn Express (Logged in as {user['username']}) ===")
    inventory = Inventory()
    while True:
        print("\n=== Staff Menu ===")
        print("1. View Inventory")
        print("2. Add Item")
        print("3. Adjust Stock")
        print("4. View Users")
        print("5. View Sales Report")
        print("6. View Deliveries")
        print("7. Logout")
        choice = input("> ")

        match choice:
            case "1":
                inventory.list_items()
            case "2":
                name = input("Item name: ")
                desc = input("Description: ")
                price = float(input("Price: "))
                qty = int(input("Quantity: "))

                print("Category (food/alcohol): ", end="")
                category = input().strip().lower()

                extra = None
                if category == "food":
                    extra = input("Best before date (e.g., 2025-12-01): ")
                elif category == "alcohol":
                    extra = input("Alcohol % (e.g., 4.5%): ")

                inventory.add_item(name, desc, price, qty, category=category, extra=extra)

            case "3":
                name = input("Item name: ")
                qty = int(input("Quantity: "))
                inventory.update_stock(name, qty, -1)
            case "4":
                view_all_users()
            case "5":
                sales_report_menu()
            case "6":
                deliveries = Delivery.list_all()
                if not deliveries:
                    print("\nNo deliveries found.\n")
                else:
                    print("\n=== All Deliveries ===\n")
                    print(f"{'Del ID':<8} {'Order ID':<9} {'Name':<12} {'Status':<12} {'ETA':<18} {'Cost':<8}")
                    print("-" * 70)
                    for d in deliveries:
                        delivery_id, order_id, name, address, phone, status, tracking, cost, eta = d
                        print(f"{delivery_id:<8} {order_id:<9} {name[:12]:<12} {status:<12} {eta:<18} ${cost:<8.2f}")

                input("\nPress ENTER to continue...")
            case "7":
                break
            case _:
                print("Invalid selection")

def main_menu(user):
    """
    Displays the main CLI menu once a user is logged in.
    Delegates user actions to Inventory, Cart, and Order classes.
    
    """
    inventory = Inventory()
    cart = Cart(user["user_id"])
    order = Order(user["user_id"])

    while True:
        print(f"\n=== Hawthorn Express (Logged in as {user['username']}) ===")
        print("1. Browse All")
        print("2. Browse Food Only")
        print("3. Browse Alcohol Only")
        print("4. Add to Cart")
        print("5. View Cart")
        print("6. Remove from Cart")
        print("7. Checkout")
        print("8. Check past Orders")
        print("9. Logout")
        choice = input("> ")

        if choice == "1":
            inventory.list_items()

        elif choice == "2":
            inventory.list_items_by_category("food")

        elif choice == "3":
            inventory.list_items_by_category("alcohol")

        elif choice == "4":
            item = input("Item name: ")
            qty = int(input("Quantity: "))
            cart.add_to_cart(item, qty)

        elif choice == "5":
            cart.view_cart()

        elif choice == "6":
            item = input("Item name: ")
            qty = int(input("Quantity: "))
            cart.remove_from_cart(item, qty)

        elif choice == "7":
            # The only way a user could have a pending order is via crash
            # or exit, so if they have a pending one, delete it.
            print("\nEnter delivery details:")
            name = input("Name: ")
            address = input("Address: ")
            phone = input("Phone: ")

            print("\nSelect Payment Method:")
            print("1. Credit Card")
            print("2. Debit Card")
            print("3. PayPal")
            method = input("> ").strip()

            method_map = {
                "1": "credit_card",
                "2": "debit_card",
                "3": "paypal"
            }
            payment_method = method_map.get(method, "credit_card")  # fallback default

            order.checkout(name, address, phone, payment_method)


        elif choice == "8":
            sr = SalesReport()
            data = sr.user_orders(user["user_id"])
            from classes.SalesReport import print_as_table
            print_as_table(f"Orders for {user['username']}", ["Order ID", "Date", "Total", "Status"], data)

        elif choice == "9":
            break  # logout and return to login_flow()

        else:
            print("Invalid selection")


if __name__ == "__main__":
    """
    Entry point for the CLI version of the system.
    Future Flask version may import this logic but replace
    the input/output with HTTP routes and HTML templates.
    """
    while True:
        user = login_flow()   # login/register returns user dict
        # Check what system they should be logged into.
        if user['role'] == "customer":
            main_menu(user)
        elif user['role'] in ["staff", "admin"]:
            staff_menu(user)
        else:
            print("Invalid role, please contact support")