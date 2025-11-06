# Hawthorn Express (CLI Application)

Hawthorn Express is a command-line grocery ordering system that supports customer ordering, staff inventory management, payment processing, delivery scheduling, and sales reporting. It uses Python and SQLite for persistent storage.

---

## Features

### Customer
- Register / Login (passwords hashed)
- Browse items (all, food only, alcohol only)
- Add / remove items from cart
- Checkout with delivery details
- Choose payment method (simulated)
- View past orders and order totals

### Staff
- View and update inventory
- Add new items with category (food/alcohol)
- View all registered users
- View sales reports and revenue summaries
- View all deliveries and their status

---

## System Structure

main.py
classes/
├─ Account.py (login/register + role control)
├─ Inventory.py (view & modify items)
├─ ItemHolder.py (database item + stock manager)
├─ Cart.py (customer cart)
├─ Order.py (checkout process)
├─ Payment.py (simulated payments)
├─ Delivery.py (delivery scheduling & tracking)
├─ SalesReport.py (staff reporting tools)
├─ Food.py / Alcohol.py
└─ db_manager.py (shared SQLite connection)


Database is stored automatically as `inventory_database.db`.

---

## Running the Application

### Requirements
- Python 3.8+
- No additional packages needed

### Run
```bash
python3 main.py
```

### Default Accounts (Auto-Created)

| Role     | Username  | Password    |
|---------|-----------|-------------|
| Staff    | **staff**    | **staff123**   |
| Customer | **customer** | **customer123** |

---

### Default Inventory
A small starter set of items is automatically inserted on first run.

---

### Notes & Assumptions
- Payment and delivery are simulated (no external APIs).
- Delivery ETA = current date + 2 days.
- CLI UI chosen to match assignment scope.
