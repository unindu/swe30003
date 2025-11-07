# Hawthorn Express (CLI Application) Testing



## Tests
### Customer Registration
This test ensures that a user can be created and that our database properly stores the hashed password securely.

### Add Item
This test ensures that items can be correctly added to the SQLite database through our own functions and, by extension, staff using the TUI.

### Adjust Stock
This test ensures that stock can be adjusted by staff, both decreasing the stock in the DB and increasing it.

### Staff and Customer Login
This test ensures that a username is correctly found and the password they entered is correctly compared to the hash of their password that we store.

### Cart
This tests adding items to the cart, and removing a specific quantity of them

### Ordering
This test asserts that an order made indeed contains the item and quantity that was in the cart, and that an order can properly be created with a correct email and address.
