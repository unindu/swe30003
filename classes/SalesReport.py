"""
Generates sales and order analytics for staff users.
Output is formatted using the coloured print_as_table renderer.
"""

from classes.db_manager import DBManager

def print_as_table(title, keys, data, size = 100):
    r = "\033[0m"
    dg = "\033[48;2;25;25;25m"
    lg = "\033[48;2;40;40;40m"
    dw = "\033[48;2;60;60;60m"
    lw = "\033[48;2;100;100;100m"
    gr = "\033[38;2;144;238;144m"
    bl = "\033[38;2;173;216;230m"
    yl = "\033[38;2;255;255;179m"
    pk = "\033[38;2;255;182;193m"
    pr = "\033[38;2;216;191;216m"
    ora = "\033[38;2;255;204;153m"
    cy = "\033[38;2;180;255;255m"
    colour_list = [gr, bl, yl, pk, pr, ora, cy]

    if not data:
        print(f"{lw}{f'- {title} -':#^{size}}{r}")
        print("No data to display.")
        return

    col_count = len(data[0])
    print(f"{lw}{f'- {title} -':#^{size}}{r}")

    num_keys = len(keys)
    key_string = f"{dw}-----"
    key_space = (size - 30) // num_keys
    key_spacing = (size - 30) % num_keys
    spare_space = size - (10 + (key_space * num_keys) + (key_spacing * num_keys - 1) + (num_keys * 2) + (num_keys - 1))

    for i, key in enumerate(keys):
        key_string += f"{colour_list[i % len(colour_list)]} {key:^{key_space}.{key_space}} {r}"
        if i != num_keys - 1:
            key_string += f"{dw}{'-' + '-' * key_spacing}"
    key_string += f"{dw}-{'-' * spare_space}----{r}"
    print(f"{key_string:<{size}}{r}")

    for row_i, row in enumerate(data):
        bg = dg if row_i % 2 == 0 else lg
        row_string = f"{bg}-----"
        for col, item in enumerate(row):
            if "price" in keys[col].lower() or "total" in keys[col].lower() or "revenue" in keys[col].lower():
                item = f"${item:.2f}"
            row_string += f"{colour_list[col % len(colour_list)]} {item:<{key_space}} {r}"
            if col != col_count - 1:
                row_string += f"{bg}{'-' + '-' * key_spacing}"
        row_string += f"{bg}-{'-' * spare_space}----{r}"
        print(row_string)


# ====== REPORT LOGIC ======

class SalesReport:
    """
    Fetches aggregated sales/order data for reporting screens.
    Used in the staff dashboard (sales_report_menu).
    """
    def __init__(self):
        self.db = DBManager()

    def item_statistics(self):
        """Total units sold & total revenue per item."""
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

    def stats_by_item(self, item_name):
        """Sales history for a specific item across orders."""
        return self.db.execute("""
            SELECT orders.order_id, orders.date,
                   items.price, stock.quantity,
                   (items.price * stock.quantity) AS revenue
            FROM stock
            JOIN items ON stock.id = items.id
            JOIN orders ON stock.order_id = orders.order_id
            WHERE stock.order_id != -1 AND items.name = ?
            ORDER BY orders.date DESC
        """, (item_name,)).fetchall()

    def items_on_date(self, date):
        """Items sold on a selected date."""
        return self.db.execute("""
            SELECT items.id, items.name, items.price,
                   SUM(stock.quantity) AS qty_sold,
                   items.price * SUM(stock.quantity) AS revenue
            FROM stock
            JOIN items ON stock.id = items.id
            JOIN orders ON stock.order_id = orders.order_id
            WHERE stock.order_id != -1 AND DATE(orders.date) = DATE(?)
            GROUP BY items.id
            ORDER BY qty_sold DESC
        """, (date,)).fetchall()

    def orders_summary(self):
        """All completed orders."""
        return self.db.execute("""
            SELECT order_id, date, total
            FROM orders
            WHERE order_id != -1
            ORDER BY date DESC
        """).fetchall()

    def user_orders(self, user_id):
        """Orders placed by a specific user."""
        return self.db.execute("""
            SELECT order_id, date, total, status
            FROM orders
            WHERE user_id = ?
            ORDER BY date DESC
        """, (user_id,)).fetchall()


def sales_report_menu():
    """
    CLI menu for staff to navigate sales reports.
    """
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
                print_as_table("Item Sales (All Time)",
                               ["Item ID", "Name", "Unit Price", "Qty Sold", "Revenue"],
                               report.item_statistics())

            case "2":
                date = input("Enter date (YYYY-MM-DD): ").strip()
                print_as_table(f"Sales on {date}",
                               ["Item ID", "Name", "Unit Price", "Qty Sold", "Revenue"],
                               report.items_on_date(date))

            case "3":
                item = input("Item Name: ").strip()
                print_as_table(f"Sales for {item}",
                               ["Order ID", "Date", "Unit Price", "Qty", "Revenue"],
                               report.stats_by_item(item))

            case "4":
                print_as_table("All Orders",
                               ["Order ID", "Date", "Total Price"],
                               report.orders_summary())

            case "5":
                user = input("Enter User ID: ").strip()
                print_as_table(f"Orders by User #{user}",
                               ["Order ID", "Date", "Total", "Status"],
                               report.user_orders(user))

            case "6":
                break

            case _:
                print("Invalid option.\n")
