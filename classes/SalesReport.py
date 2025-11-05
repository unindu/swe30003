from classes.db_manager import DBManager


def print_as_table(title, keys, data, size = 100):
    """
    Data is the data
    Columns should be an int list, listing the indexes the columns should appear in
    """
    # List out the nice colours
    # Reset
    r = "\033[0m"
    # Dark black Grey
    dg = "\033[48;2;25;25;25m"
    # Light black Grey
    lg = "\033[48;2;40;40;40m"
    # Dark white-grey...
    dw = "\033[48;2;60;60;60m"
    # Light white-grey
    lw = "\033[48;2;100;100;100m"
    # Green
    gr = "\033[38;2;144;238;144m"
    # Blue
    bl = "\033[38;2;173;216;230m"
    # Yellow
    yl = "\033[38;2;255;255;179m"
    # Pink
    pk = "\033[38;2;255;182;193m"
    # Purple
    pr = "\033[38;2;216;191;216m"
    # Orange (or is a keyword)
    ora = "\033[38;2;255;204;153m"
    # Cyan
    cy = "\033[38;2;180;255;255m"
    # So I can refereance them in colour numbers
    # I don't think we will ever have more than 7 cols
    colour_list = [gr, bl, yl, pk, pr, ora, cy]

    col_count = len(data[0])

    # Line template:
    # print(f"{dw}{f"- {title} -":^80}{r}")
    # Print the title in the light grey, dark white?
    print(f"{lw}{f"- {title} -":#^{size}}{r}")
    # Print out the key, do some fun calculations to have them evenly spread
    num_keys = len(keys)
    key_string = f"{dw}-----"
    key_space = (size - 30) // num_keys
    key_spacing = (size - 30) % num_keys
    spare_space = size - (10 + (key_space * num_keys) + (key_spacing * num_keys - 1) + (num_keys * 2) + (num_keys - 1))
    for i, key in enumerate(keys):
        key_string += f"{colour_list[i % len(colour_list)]} {key:^{key_space}.{key_space}} {r}"
        if i != num_keys - 1:
            key_string += f"{dw}{'-' + '-' * key_spacing}"
    key_string += f"{dw}-{"-" * spare_space}----{r}"
    print(f"{key_string:<{size}}{r}")

    # Now for the actual data
    for row_i, row in enumerate(data):

        # Make the background colour to alternate
        if row_i % 2 == 0:
            bg = dg
        else:
            bg = lg

        row_string = f"{bg}-----"
        for col, item in enumerate(row):

            if "id" in keys[col].lower():
                item = "#" + str(item)
            elif "price" in keys[col].lower():
                item = f"${item:.2f}"
            elif "cost" in keys[col].lower():
                item = f"${item:.2f}"
            elif "revenue" in keys[col].lower():
                item = f"${item:.2f}"
            row_string += f"{colour_list[col % len(colour_list)]} {item:<{key_space}} {r}"
            if col != col_count - 1:
                row_string += f"{bg}{'-' + '-' * key_spacing}"
        row_string += f"{bg}-{"-" * spare_space}----{r}"
        print(row_string)


class SalesReport:

    def __init__(self):
        self.db = DBManager()

    # Count of all items sold ever
    def item_statistics(self):
        """
        :returns id, name, price, num sold, total price:
        """
        # Want to look in orders to get all the items
        # WIth all those orders, look at the items

        # The sql query handily sums up all the stock for each item
        item_stats = self.db.execute("""
            SELECT items.id, items.name, items.price, SUM(stock.quantity) as item_quantity, items.price * SUM(stock.quantity)
            FROM items
            JOIN stock ON items.id = stock.id
            WHERE stock.order_id != -1
            GROUP BY items.id
        """).fetchall()

        return item_stats

    # Return the stats for one item specifically.
    def stats_by_item(self, item):
        """
        :param item:
        :returns order_id, date, price, quantity, revenue:
        """
        item_stat = self.db.execute("""
            SELECT orders.order_id, orders.date, items.price, stock.quantity, items.price * stock.quantity
            FROM orders
            JOIN stock ON orders.order_id = stock.order_id
            JOIN items ON items.id = stock.id
            WHERE stock.order_id != -1 AND items.name = ?
        """, (item,)).fetchall()

        return item_stat

    # Show all the items sold *sorted by* date
    def items_by_date(self):
        """
        :return id, date, name, sum:
        """
        item_stat = self.db.execute("""
            SELECT date(orders.date) AS date, items.id, items.name, SUM(stock.quantity)
            FROM orders
            JOIN stock ON stock.order_id = orders.order_id
            JOIN items ON items.id = stock.id
            WHERE stock.order_id != -1
            GROUP BY date(orders.date), items.id
            ORDER BY date(orders.date) DESC 
        """).fetchall()

        return item_stat

    # Show all the items sold on a date
    def items_on_date(self, date = "2025-10-30"):
        """
        The date needs to be a perfect string as YYYY-MM-DD
        :returns id, name, amount, made:
        """
        item_stat = self.db.execute("""
            SELECT items.id, items.name, items.price, SUM(stock.quantity), items.price * SUM(stock.quantity)
            FROM orders
            JOIN stock ON stock.order_id = orders.order_id
            JOIN items ON items.id = stock.id
            WHERE stock.order_id != -1 AND date(orders.date) = date(?)
            GROUP BY date(orders.date), items.id
            ORDER BY date(orders.date) DESC
        """, (date,)).fetchall()
        return item_stat


    def orders(self):
        """
        :return order_id, date, total:
        """
        item_stat = self.db.execute("""
            SELECT stock.order_id, orders.date, orders.total
            FROM items 
            JOIN stock on items.id = stock.id
            JOIN orders on stock.order_id = orders.order_id
            WHERE orders.order_id != -1
            GROUP BY orders.order_id
            ORDER BY orders.order_id DESC 
        """).fetchall()
        return item_stat

    def view_user_orders(self, user_id: int = 0):
        user_orders = self.db.execute("""
             SELECT *
             FROM orders
             WHERE user_id = ?
             ORDER BY date DESC
                                 """, (user_id,)).fetchall()
        r = "\033[0m"  # This is the colour key to reset the colour
        # Do some nice formating with every order, from earliest to latest
        for order in user_orders:
            row = 1
            # First, print the order info
            order_id, user_id, total, date, status = order
            print(f"{"\033[48;2;60;60;60m"}{f"Order #{order_id:} - Date: {date} - Status: {status}":<73}{r}")
            items = self.db.execute("""
                               SELECT items.name, items.price, stock.quantity
                               FROM stock
                                        JOIN items ON stock.id = items.id
                               WHERE stock.order_id = ?
                               """, (order_id,)).fetchall()
            print(
                f"{"\033[48;2;25;25;25m"}------ {"\033[38;2;144;238;144m"}Item Name{r}{"\033[48;2;25;25;25m"} ---------------- {"\033[38;2;216;191;216m"}Quantity{r}{"\033[48;2;25;25;25m"} -- {"\033[38;2;255;204;153m"}Price{r}{"\033[48;2;25;25;25m"} --- {"\033[38;2;255;160;122m"}Total{r}{"\033[48;2;25;25;25m"} -----------{r}")
            for item in items:
                # Cool ANSI formatting: https://ansi.tools/
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
                print(f"{rowBG}-----> {"\033[38;2;144;238;144m"}{name + " ":<25}{r}{rowBG}-" +
                      f" {"\033[38;2;216;191;216m"}{formatted_qty + " ":<10}{r}{rowBG}-" +
                      f"{"\033[38;2;255;204;153m"} ${formatted_price + " ":<7}{r}{rowBG}-" +
                      f"{"\033[38;2;255;160;122m"} ${formatted_total + " ":<16}{r}")

def sales_report_menu():
    report = SalesReport()
    while True:
        print("""Please select what you would like to see
        1. Item Statistics for All Time
        2. Items Statistics for Date
        3. Specific Item Statistics
        4. All orders
        5. Specific User's Order
        6. Items ordered by date
        7. Exit""")
        answer = input("> ")
        match answer:
            case "1":
                data = report.item_statistics()
                keys = ["Item ID", "Item Name", "Unit Price", "Amount sold", "Revenue"]
                title = "Item Statistics for All Time"
                print_as_table(title, keys, data)

            case "2":
                date = input("Please enter date in YYYY-MM-DD format: ").strip()
                data = report.items_on_date(date)
                keys = ["Item ID", "Item Name", "Unit Price", "Amount sold", "Revenue"]
                title = f"Item Statistics for {date}"
                print_as_table(title, keys, data)

            case "3":
                item = input("Please enter an item's exact name: ").strip()
                data = report.stats_by_item(item)
                keys = ["Order ID", "Order Date", "Unit Price", "Amount sold", "Revenue"]
                title = f"All Orders"
                print_as_table(title, keys, data)

            case "4":
                data = report.orders()
                keys = ["Order ID", "Order Date", "Total Price"]
                title = f"All orders"
                print_as_table(title, keys, data)

            case "5":
                while True:
                    user = input("Please enter a user's id: ").strip()
                    try:
                        int(user)
                        break
                    except ValueError:
                        print("Please enter a number.")
                        continue
                report.view_user_orders(int(user))

            case "6":
                data = report.items_by_date()
                keys = ["Date", "Item ID", "Name", "Amount Sold"]
                title = f"All items ordered by date"
                print_as_table(title, keys, data)

            case "7":
                break

            case _:
                print("Invalid selection")

        input("Press ENTER when done")
        print()


if __name__ == "__main__":
    sales_report_menu()