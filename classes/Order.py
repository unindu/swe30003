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
        # Should solve the pending issues
        self.db.execute("""
            DELETE FROM orders 
            WHERE status = 'pending' AND user_id = ?
        """, (self.user_id,), commit=True)
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
            SELECT SUM(items.price * carts.quantity)
            FROM carts
            JOIN items ON carts.item_id = items.id
            WHERE carts.user_id = ?
        """, (self.user_id,)).fetchone()[0]   # one row (first) is returned because SUM
        
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
        

        # Insert into the stock table under order id
        self.db.execute("""
            INSERT INTO stock (id, quantity, order_id)
            SELECT item_id, quantity, ? FROM carts WHERE user_id = ?
        """, (order_id, self.user_id), commit=True)

        # Delete from the cart table
        self.db.execute("DELETE FROM carts WHERE user_id = ?", (self.user_id,), commit=True)

        # Mark order as complete, for debugging mostly...
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
            WHERE stock.order_id = ?
        """, (order_id,)).fetchall()
        
        # Print order confirmation
        print(f"\nORDER CONFIRMATION #{order_id}")
        print(f"Date: {order_info[1]}")
        print(f"\nItems:")
        
        for (item_name, price, qty) in items:
            total = price * qty
            print(f"  {item_name} - Qty: {qty} - ${price:.2f} each - Total: ${total:.2f}")
        
        print(f"\nTotal: ${order_info[0]:.2f}\n")




