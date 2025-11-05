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
            SELECT orders.order_id, orders.date, items.name, SUM(items.price)
            FROM orders
            JOIN stock ON stock.order_id = orders.order_id
            JOIN items ON items.id = stock.id
            WHERE stock.order_id != -1
            GROUP BY orders.order_id
        """).fetchall()
        return item_stat

    # Call and print all of the above
    def generate_report(self):
        pass


if __name__ == "__main__":
    report = SalesReport()
    print(report.items_by_order())