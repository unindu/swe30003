from classes.db_manager import DBManager

def print_as_table(title, headers, rows):
    print(f"\n=== {title} ===\n")
    if not rows:
        print("No data available.\n")
        return
    
    # Header row
    print(" | ".join(f"{h:<20}" for h in headers))
    print("-" * (len(headers) * 23))

    # Data rows
    for row in rows:
        print(" | ".join(f"{str(col):<20}" for col in row))
    print()

class SalesReport:
    """
    Generates basic sales analytics using the existing schema:
    - items
    - stock
    - orders
    """
    def __init__(self):
        self.db = DBManager()

    def item_statistics(self):
        """
        Returns total sold per item and revenue generated.
        Only counts stock tied to completed orders (order_id != -1)
        """
        return self.db.execute("""
            SELECT items.id, items.name, items.price, 
                   SUM(stock.quantity) AS qty_sold,
                   (items.price * SUM(stock.quantity)) AS revenue
            FROM stock
            JOIN items ON stock.id = items.id
            WHERE stock.order_id != -1
            GROUP BY items.id
            ORDER BY revenue DESC
        """).fetchall()

    def items_on_date(self, date):
        return self.db.execute("""
            SELECT items.id, items.name, items.price,
                   SUM(stock.quantity) AS qty_sold,
                   items.price * SUM(stock.quantity) AS revenue
            FROM stock
            JOIN items ON stock.id = items.id
            JOIN orders ON stock.order_id = orders.order_id
            WHERE stock.order_id != -1
              AND DATE(orders.date) = DATE(?)
            GROUP BY items.id
            ORDER BY qty_sold DESC
        """, (date,)).fetchall()

    def stats_by_item(self, item_name):
        return self.db.execute("""
            SELECT orders.order_id, orders.date, items.price, stock.quantity,
                   (items.price * stock.quantity) AS revenue
            FROM stock
            JOIN items ON stock.id = items.id
            JOIN orders ON stock.order_id = orders.order_id
            WHERE stock.order_id != -1 AND items.name = ?
            ORDER BY orders.date DESC
        """, (item_name,)).fetchall()

    def orders_summary(self):
        """
        Returns every order and total price.
        """
        return self.db.execute("""
            SELECT order_id, date, total
            FROM orders
            WHERE order_id != -1
            ORDER BY date DESC
        """).fetchall()

    def user_orders(self, user_id):
        """
        Returns all orders placed by a specific user.
        """
        return self.db.execute("""
            SELECT order_id, date, total, status
            FROM orders
            WHERE user_id = ?
            ORDER BY date DESC
        """, (user_id,)).fetchall()


def sales_report_menu():
    report = SalesReport()

    while True:
        print("""
=== SALES REPORT MENU ===
1. Item Statistics (All Time)
2. Item Sales on a Specific Date
3. Sales for a Specific Item
4. All Orders Summary
5. Orders by User
6. Back
""")
        choice = input("> ").strip()

        match choice:
            case "1":
                data = report.item_statistics()
                print_as_table("Item Sales (All Time)", ["ID", "Name", "Price", "Qty Sold", "Revenue"], data)

            case "2":
                date = input("Enter date (YYYY-MM-DD): ").strip()
                data = report.items_on_date(date)
                print_as_table(f"Sales on {date}", ["ID", "Name", "Price", "Qty Sold", "Revenue"], data)

            case "3":
                item = input("Item Name: ").strip()
                data = report.stats_by_item(item)
                print_as_table(f"Sales for {item}", ["Order ID", "Date", "Price", "Qty", "Revenue"], data)

            case "4":
                data = report.orders_summary()
                print_as_table("All Orders", ["Order ID", "Date", "Total Price"], data)

            case "5":
                user = input("Enter User ID: ").strip()
                data = report.user_orders(user)
                print_as_table(f"Orders by User #{user}", ["Order ID", "Date", "Total", "Status"], data)

            case "6":
                break

            case _:
                print("Invalid option.\n")
