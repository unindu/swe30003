import datetime

from classes import Item
from classes.db_manager import DBManager


class SalesReport:

    def __init__(self):
        self.db = DBManager()

    def print_as_table(self, data, columns):
        """
        Data is the data
        Columns should be an int list, listing the indexes the columns should appear in
        """
        col_count = len(data[0])

        pass

    # Count of all items sold ever
    def item_statistics(self):
        # Want to look in orders to get all the items
        # WIth all those orders, look at the items

        # The sql query handily sums up all the stock for each item
        item_stats = self.db.execute("""
            SELECT items.id, items.name, items.price, SUM(stock.quantity) as item_quantity
            FROM items
            JOIN stock ON items.id = stock.id
            WHERE stock.order_id != -1
            GROUP BY items.id
        """).fetchall()

        return item_stats

    # Return the stats for one item specifically.
    def stats_by_items(self, item):
        item_stat = self.db.execute("""
            SELECT orders.order_id, orders.date, items.id, items.name, items.price, stock.quantity
            FROM orders
            JOIN stock ON orders.order_id = stock.order_id
            JOIN items ON items.id = stock.id
            WHERE stock.order_id != -1 AND items.name = ?
        """, (item,)).fetchall()

        return item_stat

    # Show all the items sold *sorted by* date
    def items_by_date(self):
        item_stat = self.db.execute("""
            SELECT items.id, date(orders.date) AS date, items.name, SUM(stock.quantity)
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
        """
        item_stat = self.db.execute("""
            SELECT items.id, date(orders.date) AS date, items.name, SUM(stock.quantity)
            FROM orders
            JOIN stock ON stock.order_id = orders.order_id
            JOIN items ON items.id = stock.id
            WHERE stock.order_id != -1 AND date(orders.date) = date(?)
            GROUP BY date(orders.date), items.id
            ORDER BY date(orders.date) DESC
        """, (date,)).fetchall()
        return item_stat


    def orders(self):
        item_stat = self.db.execute("""
            SELECT stock.order_id, orders.date, orders.total
            FROM items 
            JOIN stock on items.id = stock.id
            JOIN orders on stock.order_id = orders.order_id
            WHERE orders.order_id != -1
        """).fetchall()
        return item_stat

    def view_user_orders(userId: int):
        db = DBManager()
        user_orders = db.execute("""
                                 SELECT *
                                 FROM orders
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


if __name__ == "__main__":
    report = SalesReport()
    print(report.orders())