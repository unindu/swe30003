import sqlite3

from classes.ItemHolder import ItemHolder


class Inventory(ItemHolder):
    def __init__(self):
        super().__init__()

if __name__ == "__main__":
    Inventory()