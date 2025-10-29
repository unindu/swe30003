# main.py
from classes.Account import Account
from classes.Inventory import Inventory
from classes.Cart import Cart
from classes.Order import Order, view_user_orders

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
    inventory = Inventory()
    while True:
        print("\n=== Staff Menu ===")
        print("1. View Inventory")
        print("2. Add Item")
        print("3. Remove Item")
        print("4. Adjust Stock")
        print("5. View Users")
        print("6. View Orders of User")
        print("7. Cancel/Refund Order")
        print("8. Logout")
        choice = input("> ")

        match choice:
            case "1":
                inventory.list_items()
            case "2":
                name = input("Item name: ")
                price = float(input("Price: "))
                qty = int(input("Quantity: "))
                inventory.add_item(name, price, qty)
            case "3":
                name = input("Item name: ")
                inventory.remove_item(name)
            case "4":
                name = input("Item name: ")
                qty = int(input("Quantity: "))
                inventory.update_stock(name, qty, "Inventory")
            case "5":
                pass
            case "6":
                user_id = input("User ID: ")
                if int(user_id) == user_id:
                    print("Invalid user ID")
                    continue
                view_user_orders(int(user_id))
            case "7":
                user_id = input("User ID: ")
                if int(user_id) == user_id:
                    print("Invalid user ID")
                    continue
                order = Order(user_id)
                order_id = input("Order ID: ")
                # TODO, how to cancel order ?
                order.cancel(order_id)
            case "8":
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
        print("1. Browse")
        print("2. Add to Cart")
        print("3. View Cart")
        print("4. Remove from Cart")
        print("5. Checkout")
        print("6. Logout")
        choice = input("> ")

        if choice == "1":
            inventory.list_items()

        elif choice == "2":
            item = input("Item name: ")
            qty = int(input("Quantity: "))
            cart.add_to_cart(item, qty)

        elif choice == "3":
            cart.view_cart()

        elif choice == "4":
            item = input("Item name: ")
            qty = int(input("Quantity: "))
            cart.remove_from_cart(item, qty)

        elif choice == "5":
            # The only way a user could have a pending order is via crash
            # or exit, so if they have a pending one, delete it.
            print("\nEnter delivery details:")
            name = input("Name: ")
            address = input("Address: ")
            phone = input("Phone: ")
            order.checkout(name, address, phone)

        elif choice == "6":
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