# classes/Order.py
from classes.ItemHolder import ItemHolder
from classes.Payment import Payment
from classes.Delivery import Delivery
from classes.SalesReport import SalesReport
from classes.db_manager import DBManager
from datetime import datetime   # used for timestamp for _create_order_

# Order class inherits from ItemHolder class and orchestrates the order process
class Order(ItemHolder):

    # initialise the order class
    def __init__(self, user_id):

        super().__init__()
        
        self.user_id = user_id  # user_id is the id of the user who is placing the order
        self.cart_location = f"{user_id}_cart"
        self.order_location = f"{user_id}_order"
        self.payment = None     
        self.delivery = None    
        self.sales_report = SalesReport()
        self.db = DBManager()
        self._create_orders_table()
    
    # create the orders table if it doesn't exist
    def _create_orders_table(self):

        self.db.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                total REAL NOT NULL,
                date TEXT NOT NULL,
                status TEXT DEFAULT 'pending'
            )
        """, commit=True)

    # flow of the checkout process, cart -> order -> payment -> delivery -> confirmation
    def checkout(self, name, address, phone, payment_method="credit_card"):

        # Get cart total cost
        total = self._get_cart_total()
        if not total:
            print("Cart is empty.")
            return False
        
        # Create order
        order_id = self._create_order(total)
        
        # Process payment, if failed payment (false), exit
        if not self._process_payment(order_id, total, payment_method):
            return False   
        
        # Move items from cart to order (location updated in single query)
        self._move_cart_to_order(order_id)
        
        # Schedule delivery
        self._schedule_delivery(order_id, name, address, phone)
        
        # Generate order confirmation
        self.generate_confirmation(order_id)
        
        return True

    # used within the checkout process to get the total cost of the cart
    def _get_cart_total(self):

        result = self.db.execute("""
            SELECT SUM(items.price * stock.quantity)
            FROM stock
            JOIN items ON stock.id = items.id
            WHERE stock.location = ?
        """, (self.cart_location,)).fetchone()[0]   # one row (first) is returned because SUM
        
        return result or 0  # if no SUM because no items in cart, then 0
    
    # used within the checkout process to create a new order 
    def _create_order(self, total):

        date_str = datetime.now().strftime("%Y-%m-%d %H:%M")    # datetime YYYY-MM-DD HH:MM

        cursor = self.db.execute("""
            INSERT INTO orders (user_id, total, date)
            VALUES (?, ?, ?)
        """, (self.user_id, total, date_str), commit=True)

        return cursor.lastrowid    # the latest order has the order_id
    

    # used within the checkout process to process the payment (default is credit card, hardcoded, see line 38)
    def _process_payment(self, order_id, total, payment_method):

        self.payment = Payment(order_id, total)  # create a Payment object
        
        success = self.payment.process(payment_method)  # process the payment and return True if successful
        
        # delete order if failed payment
        if not success:
            self.db.execute("DELETE FROM orders WHERE order_id = ?", (order_id,), commit=True)
        
        return success # return True if successful, or False
    
    # used within the checkout process to move items from cart to order
    def _move_cart_to_order(self, order_id):
        
        # select items from cart
        items = self.db.execute("""
            SELECT stock.id, stock.quantity, items.name, items.price
            FROM stock
            JOIN items ON stock.id = items.id
            WHERE stock.location = ?
        """, (self.cart_location,)).fetchall()

        # move items in cart to order table
        self.db.execute("""
            UPDATE stock 
            SET location = ?,
                order_id = ?
            WHERE location = ?  
        """, (self.order_location, order_id, self.cart_location), commit=True)

        self.db.execute("UPDATE orders SET status = 'complete' WHERE order_id = ?", (order_id,), commit=True)

    # used to schedule delivery after order is completed
    def _schedule_delivery(self, order_id, name, address, phone):
        # Create delivery with values from console input
        self.delivery = Delivery(order_id, name, address, phone)
        self.delivery.schedule()
    
    # used to cancel successfully completed orders
    def cancel(self, order_id):
        
        # get order_id and total cost
        order_info = self.db.execute("""
            SELECT total, user_id FROM orders WHERE order_id = ?
        """, (order_id,)).fetchone()
        
        # validate ownership, order_info = [total cost, user_id]
        if not order_info or order_info[1] != self.user_id:
            print("Cannot cancel order.")
            return False
        
        # refund payment
        if self.payment:
            self.payment.refund()
        else:
            payment = Payment(order_id, order_info[0])
            payment.refund()
        
        # cancel delivery
        if self.delivery:
            self.delivery.cancel()
        else:
            Delivery.cancel_by_order_id(order_id)
        
        # set order status to cancelled
        self.db.execute("UPDATE orders SET status = 'cancelled' WHERE order_id = ?", (order_id,), commit=True)
        
        print(f"Order #{order_id} cancelled.")
        return True
    
    # generates an order confirmation
    def generate_confirmation(self, order_id):

        # Get total cost and date of order
        order_info = self.db.execute("""
            SELECT total, date FROM orders WHERE order_id = ?
        """, (order_id,)).fetchone()
        
        # Get items information in order
        items = self.db.execute("""
            SELECT items.name, items.price, stock.quantity
            FROM stock
            JOIN items ON stock.id = items.id
            WHERE stock.location = ?
        """, (self.order_location,)).fetchall()
        
        # Print order confirmation
        print(f"\nORDER CONFIRMATION #{order_id}")
        print(f"Date: {order_info[1]}")
        print(f"\nItems:")
        
        for (item_name, price, qty) in items:
            total = price * qty
            print(f"  {item_name} - Qty: {qty} - ${price:.2f} each - Total: ${total:.2f}")
        
        print(f"\nTotal: ${order_info[0]:.2f}\n")


def view_user_orders(userId: int):
    db = DBManager()
    user_orders = db.execute("""
    SELECT * FROM orders 
    WHERE user_id = ? 
    ORDER BY date DESC
    """, (userId,)).fetchall()
    r = "\033[0m"  # This is the colour key to reset the colour
    # Do some nice formating with every order, from earliest to latest
    for order in user_orders:
        row = 1
        # First, print the order info
        order_id, user_id, total, date, status = order
        print(f"{"\033[48;2;60;60;60m"}{f"Order #{order_id:} - Date: {date} - Status: {status}":<73}{r}")
        items = db.execute("""
            SELECT items.name, items.price, stock.quantity FROM stock
            JOIN items ON stock.id = items.id
            WHERE stock.order_id = ?
        """, (order_id,)).fetchall()
        print(f"{"\033[48;2;25;25;25m"}------ {"\033[38;2;144;238;144m"}Item Name{r}{"\033[48;2;25;25;25m"} ---------------- {"\033[38;2;216;191;216m"}Quantity{r}{"\033[48;2;25;25;25m"} -- {"\033[38;2;255;204;153m"}Price{r}{"\033[48;2;25;25;25m"} --- {"\033[38;2;255;160;122m"}Total{r}{"\033[48;2;25;25;25m"} -----------{r}")
        for item in items:
            # Sm cool ANSI formatting: https://ansi.tools/
            if row % 2 == 0:
                rowBG = "\033[48;2;25;25;25m"
            else:
                rowBG = "\033[48;2;40;40;40m"
            row += 1
            name, price, qty = item
            # Bunch of formats bcs I can't convert to a string inside
            # the formatting and don't want dashes right after a value
            formatted_price = f"{price:.2f}"
            formatted_qty = f"{qty}"
            formatted_total = f"{price * qty:.2f}"
            # Basically, interchanging bg colours for rows, and coloured text for columns!
            # It is a bit messy code wise tho...
            # \033[ command follows, ;2 RGB values, ;144;238;144 (values), m end of seq.
            print(f"{rowBG}-----> {"\033[38;2;144;238;144m"}{name + " ":<25}{r}{rowBG}-"+
                f" {"\033[38;2;216;191;216m"}{formatted_qty + " ":<10}{r}{rowBG}-" +
                f"{"\033[38;2;255;204;153m"} ${formatted_price + " ":<7}{r}{rowBG}-"+
                f"{"\033[38;2;255;160;122m"} ${formatted_total + " ":<16}{r}")

if __name__ == "__main__":
    view_user_orders(1)


