from classes.db_manager import DBManager

class SalesReport:
    """
    Provides data retrieval for sales analytics.
    UI formatting (CLI or Flask) will be done separately.
    """
    def __init__(self):
        self.db = DBManager()

    def total_revenue(self):
        result = self.db.execute("""
            SELECT SUM(total)
            FROM orders
            WHERE status = 'complete'
        """).fetchone()[0]
        return result or 0

    def top_selling_items(self, limit=5):
        return self.db.execute("""
            SELECT items.name, SUM(stock.quantity) AS total_sold
            FROM stock
            JOIN items ON stock.id = items.id
            JOIN orders ON stock.order_id = orders.order_id
            WHERE orders.status = 'complete'
            GROUP BY items.name
            ORDER BY total_sold DESC
            LIMIT ?
        """, (limit,)).fetchall()

    def revenue_by_category(self):
        return self.db.execute("""
            SELECT items.category, SUM(stock.quantity * items.price) AS revenue
            FROM stock
            JOIN items ON stock.id = items.id
            JOIN orders ON stock.order_id = orders.order_id
            WHERE orders.status = 'complete'
            GROUP BY items.category
        """).fetchall()
