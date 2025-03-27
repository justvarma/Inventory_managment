import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import time
import random  # For generating bill numbers

# --- Placeholder for database connection ---
# Assume you have a function like this in another file (e.g., database_utils.py or employees.py)
# from database_utils import connect_database
# Placeholder implementation:
def connect_database():
    """Placeholder: Replace with your actual database connection logic."""
    print("Placeholder: connect_database() called. Implement connection.")
    # Example using pymysql (ensure it's installed: pip install pymysql)
    try:
        import pymysql
        connection = pymysql.connect(
            host="localhost",
            user="root",
            password="Adityavarma@123", # Replace with your password
            database="inventory_systems",
            cursorclass=pymysql.cursors.DictCursor # Use DictCursor for easier data access by column name
        )
        cursor = connection.cursor()
        print("Placeholder: Database connection attempt successful (using pymysql).")
        return cursor, connection
    except Exception as e:
        print(f"Placeholder: Database connection failed: {e}")
        messagebox.showerror("DB Error", f"Placeholder: Could not connect to database.\n{e}")
        return None, None

# --- Database Interaction Functions (Implement These) ---

def load_products_from_db(search_term=""):
    """Fetches products from DB. Implement filtering by search_term."""
    print(f"Placeholder: load_products_from_db(search='{search_term}') called.")
    cursor, connection = connect_database()
    if not cursor:
        return []
    products = []
    try:
        cursor.execute("USE inventory_systems")
        # ***** CHANGED TABLE NAME HERE *****
        base_query = "SELECT product_id, name, price, quantity FROM product_data WHERE quantity > 0" # Only show items in stock
        params = ()
        if search_term:
            base_query += " AND name LIKE %s"
            params = (f"%{search_term}%",)

        # Check if columns product_id, name, price, quantity actually exist in product_data
        # You might need to adjust these column names based on DESCRIBE product_data;
        cursor.execute(base_query + " ORDER BY name", params)
        products = cursor.fetchall() # Returns list of dictionaries if DictCursor is used
        print(f"Placeholder: Found {len(products)} products.")
    except Exception as e:
        print(f"Placeholder DB Error fetching products: {e}")
        messagebox.showerror("DB Error", f"Error fetching products:\n{e}")
    finally:
        if cursor: cursor.close()
        if connection: connection.close()
    return products if products else []

def get_tax_rate_from_db():
    """Fetches the current tax rate from the database."""
    print("Placeholder: get_tax_rate_from_db() called.")
    cursor, connection = connect_database()
    if not cursor:
        return 0.0 # Default tax if DB fails

    tax_rate = 0.0
    try:
        cursor.execute("USE inventory_systems")
        cursor.execute("SELECT tax FROM tax_table WHERE id = 1")
        result = cursor.fetchone()
        if result and 'tax' in result:
            tax_rate = float(result['tax'])
            print(f"Placeholder: Fetched tax rate: {tax_rate}%")
        else:
            print("Placeholder: Tax rate not found in DB, using 0.0.")
    except Exception as e:
        print(f"Placeholder DB Error fetching tax rate: {e}")
        messagebox.showerror("DB Error", f"Error fetching tax rate:\n{e}")
    finally:
        if cursor: cursor.close()
        if connection: connection.close()
    return tax_rate

def save_bill_to_db(bill_data):
    """Saves the bill details and items to the database."""
    print("Placeholder: save_bill_to_db() called with data:", bill_data)
    # Implementation needed:
    # 1. Connect to DB.
    # 2. Start a transaction.
    # 3. Insert into a 'bills' table (bill_no, customer_name, customer_phone, date, sub_total, tax_amount, net_total). Get the new bill_id.
    # 4. Loop through bill_data['items']:
    #    - Insert into a 'bill_items' table (bill_id, product_id, quantity, price_per_unit, total_price).
    # 5. Commit transaction.
    # 6. Handle errors and rollback if necessary.
    # 7. Return True on success, False on failure.
    messagebox.showinfo("Save Bill", "Placeholder: Bill details would be saved to the database here.", parent=bill_data.get("parent_window"))
    return True # Placeholder success

def update_stock_in_db(cart_items):
    """Updates the product stock quantities in the database after a sale."""
    print("Placeholder: update_stock_in_db() called with items:", cart_items)
    cursor, connection = connect_database()
    if not cursor:
        messagebox.showerror("Stock Update Error", "Cannot connect to database to update stock.")
        return False

    success = True
    try:
        cursor.execute("USE inventory_systems")
        connection.begin() # Start transaction

        for item_id, item_data in cart_items.items():
            product_id_value = item_data['id'] # Renamed variable to avoid confusion
            sold_quantity = item_data['qty']

            # Check current stock again before updating (optional but safer)
            # ***** CHANGED TABLE NAME HERE *****
            # Make sure 'product_id' is the correct column name in 'product_data'
            cursor.execute("SELECT quantity FROM product_data WHERE product_id = %s FOR UPDATE", (product_id_value,))
            result = cursor.fetchone()

            # Check if result is None (product_id not found)
            if result is None:
                 raise ValueError(f"Product ID {product_id_value} not found in product_data table.")

            current_stock = result.get('quantity', 0) # Use .get() for safety

            if current_stock < sold_quantity:
                 raise ValueError(f"Stock changed for Product ID {product_id_value}. Only {current_stock} left.")

            # Update stock
            # ***** CHANGED TABLE NAME HERE *****
            # Make sure 'product_id' and 'quantity' are the correct column names
            cursor.execute(
                "UPDATE product_data SET quantity = quantity - %s WHERE product_id = %s AND quantity >= %s",
                (sold_quantity, product_id_value, sold_quantity) # Ensure quantity doesn't go negative
            )
            if cursor.rowcount == 0:
                # This means either product_id didn't exist or quantity was already too low after the check
                # (unlikely if FOR UPDATE was used correctly, but possible race condition without it)
                 raise ValueError(f"Failed to update stock for Product ID {product_id_value}. Could be concurrent update or insufficient stock.")
            print(f"Placeholder: Stock updated for {product_id_value}, reduced by {sold_quantity}.")

        connection.commit() # Commit transaction
        print("Placeholder: Stock updates committed.")

    except Exception as e:
        if connection: connection.rollback() # Rollback on error
        print(f"Placeholder DB Error updating stock: {e}")
        messagebox.showerror("Stock Update Error", f"Error updating stock:\n{e}\nTransaction rolled back.")
        success = False
    finally:
        if cursor: cursor.close()
        if connection: connection.close()

    return success


# --- Main Customer Application Class ---
class CustomerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Customer Billing")
        # Adjust geometry as needed
        self.root.geometry("1350x730+0+0")
        self.root.config(bg="lightgrey")

        # --- Data Variables ---
        self.customer_name_var = tk.StringVar()
        self.customer_phone_var = tk.StringVar()
        self.search_product_var = tk.StringVar()
        self.selected_product_id = tk.StringVar()
        self.selected_product_name = tk.StringVar()
        self.selected_product_price = tk.StringVar()
        self.selected_product_stock = tk.StringVar()
        self.selected_product_qty = tk.IntVar(value=1)
        self.calculator_display_var = tk.StringVar()
        self.cart_items = {}  # Dictionary to store cart items {treeview_item_id: {id, name, qty, price}}
        self.bill_text_content = tk.StringVar()
        self.sub_total_var = tk.StringVar(value="0.00")
        self.tax_var = tk.StringVar(value="0.00")
        self.net_total_var = tk.StringVar(value="0.00")
        self.tax_rate = get_tax_rate_from_db() # Fetch tax rate on init

        # --- Setup UI ---
        self.create_widgets()
        self.load_all_products() # Load initial product list


    def create_widgets(self):
        # --- Main Frames ---
        left_frame = tk.Frame(self.root, bd=2, relief=tk.RIDGE, bg="white")
        left_frame.place(x=10, y=10, width=450, height=710)

        right_frame = tk.Frame(self.root, bd=2, relief=tk.RIDGE, bg="white")
        right_frame.place(x=470, y=10, width=870, height=710)

        # --- Left Frame Content ---
        self.create_customer_details_frame(left_frame)
        self.create_product_search_list_frame(left_frame)

        # --- Right Frame Content ---
        self.create_calculator_frame(right_frame)
        self.create_product_selection_frame(right_frame)
        self.create_cart_billing_frame(right_frame)


    # --- Widget Creation Sub-methods ---

    def create_customer_details_frame(self, parent):
        frame = tk.LabelFrame(parent, text="Customer Details", font=("Arial", 12, "bold"), bg="white", bd=2, relief=tk.GROOVE)
        frame.place(x=10, y=10, width=430, height=100)

        tk.Label(frame, text="Name:", font=("Arial", 11), bg="white").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        tk.Entry(frame, textvariable=self.customer_name_var, font=("Arial", 11), width=25).grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame, text="Phone:", font=("Arial", 11), bg="white").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        tk.Entry(frame, textvariable=self.customer_phone_var, font=("Arial", 11), width=25).grid(row=1, column=1, padx=5, pady=5)

    def create_product_search_list_frame(self, parent):
        frame = tk.LabelFrame(parent, text="Products", font=("Arial", 12, "bold"), bg="white", bd=2, relief=tk.GROOVE)
        frame.place(x=10, y=120, width=430, height=580)

        # Search Area
        tk.Label(frame, text="Search Product:", font=("Arial", 11), bg="white").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        tk.Entry(frame, textvariable=self.search_product_var, font=("Arial", 11), width=20).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        search_btn = ttk.Button(frame, text="Search", command=self.search_product)
        search_btn.grid(row=0, column=2, padx=5, pady=5)
        show_all_btn = ttk.Button(frame, text="Show All", command=self.load_all_products)
        show_all_btn.grid(row=0, column=3, padx=5, pady=5)

        # Product List Treeview
        list_frame = tk.Frame(frame, bd=1, relief=tk.SUNKEN)
        list_frame.place(x=10, y=45, width=410, height=520)

        scrollbar_y = tk.Scrollbar(list_frame, orient=tk.VERTICAL)
        scrollbar_x = tk.Scrollbar(list_frame, orient=tk.HORIZONTAL)

        self.product_tree = ttk.Treeview(list_frame, columns=("ID", "Name", "Price", "Stock"),
                                         yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set, selectmode="browse")

        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        scrollbar_y.config(command=self.product_tree.yview)
        scrollbar_x.config(command=self.product_tree.xview)

        self.product_tree.heading("ID", text="ID")
        self.product_tree.heading("Name", text="Name")
        self.product_tree.heading("Price", text="Price")
        self.product_tree.heading("Stock", text="Stock")

        self.product_tree['show'] = 'headings'

        self.product_tree.column("ID", width=50, anchor='center')
        self.product_tree.column("Name", width=180)
        self.product_tree.column("Price", width=70, anchor='e')
        self.product_tree.column("Stock", width=60, anchor='center')

        self.product_tree.pack(fill=tk.BOTH, expand=1)
        self.product_tree.bind("<<TreeviewSelect>>", self.on_product_select)

    def create_calculator_frame(self, parent):
        frame = tk.Frame(parent, bd=2, relief=tk.RIDGE, bg="lightgrey")
        frame.place(x=10, y=10, width=300, height=250) # Position top-right

        tk.Entry(frame, textvariable=self.calculator_display_var, font=('Arial', 16, 'bold'), bd=5, relief=tk.SUNKEN, justify='right').grid(row=0, column=0, columnspan=4, pady=5, padx=5, ipady=5)

        buttons = [
            '7', '8', '9', '/',
            '4', '5', '6', '*',
            '1', '2', '3', '-',
            '0', '.', '=', '+'
        ]
        row_val = 1
        col_val = 0
        for button in buttons:
            ttk.Button(frame, text=button, style="Calc.TButton", command=lambda b=button: self.calculator_click(b)).grid(row=row_val, column=col_val, padx=2, pady=2, ipadx=10, ipady=10)
            col_val += 1
            if col_val > 3:
                col_val = 0
                row_val += 1

        # Clear button
        ttk.Button(frame, text='C', style="Calc.TButton", command=self.calculator_clear).grid(row=row_val, column=0, columnspan=2, padx=2, pady=2, ipadx=30, ipady=10)
        # You might want to place '=' and '+' differently if needed

        # Style for calculator buttons
        style = ttk.Style()
        style.configure("Calc.TButton", font=('Arial', 12, 'bold'))


    def create_product_selection_frame(self, parent):
        frame = tk.LabelFrame(parent, text="Product Selection", font=("Arial", 12, "bold"), bg="white", bd=2, relief=tk.GROOVE)
        frame.place(x=320, y=10, width=540, height=250) # Position next to calculator

        row_pad = 8
        tk.Label(frame, text="Product Name:", font=("Arial", 11), bg="white").grid(row=0, column=0, padx=5, pady=row_pad, sticky="w")
        tk.Entry(frame, textvariable=self.selected_product_name, font=("Arial", 11), state='readonly', width=35).grid(row=0, column=1, columnspan=3, padx=5, pady=row_pad, sticky="w")

        tk.Label(frame, text="Price:", font=("Arial", 11), bg="white").grid(row=1, column=0, padx=5, pady=row_pad, sticky="w")
        tk.Entry(frame, textvariable=self.selected_product_price, font=("Arial", 11), state='readonly', width=15).grid(row=1, column=1, padx=5, pady=row_pad, sticky="w")

        tk.Label(frame, text="In Stock:", font=("Arial", 11), bg="white").grid(row=1, column=2, padx=5, pady=row_pad, sticky="w")
        tk.Entry(frame, textvariable=self.selected_product_stock, font=("Arial", 11, "bold"), fg="blue", state='readonly', width=8).grid(row=1, column=3, padx=5, pady=row_pad, sticky="w")

        tk.Label(frame, text="Quantity:", font=("Arial", 11), bg="white").grid(row=2, column=0, padx=5, pady=row_pad, sticky="w")
        tk.Spinbox(frame, from_=1, to=9999, textvariable=self.selected_product_qty, font=("Arial", 11), width=13).grid(row=2, column=1, padx=5, pady=row_pad, sticky="w")

        # Action Buttons
        btn_frame = tk.Frame(frame, bg="white")
        btn_frame.grid(row=3, column=0, columnspan=4, pady=20)

        add_cart_btn = ttk.Button(btn_frame, text="Add / Update Cart", width=20, command=self.add_update_cart)
        add_cart_btn.grid(row=0, column=0, padx=10, pady=5)

        clear_sel_btn = ttk.Button(btn_frame, text="Clear Selection", width=15, command=self.clear_selection_fields)
        clear_sel_btn.grid(row=0, column=1, padx=10, pady=5)

    def create_cart_billing_frame(self, parent):
        frame = tk.Frame(parent, bd=2, relief=tk.RIDGE, bg="lightgrey")
        frame.place(x=10, y=270, width=850, height=430)

        # Cart Area
        cart_frame = tk.LabelFrame(frame, text="Cart", font=("Arial", 12, "bold"), bg="white", bd=2, relief=tk.GROOVE)
        cart_frame.place(x=10, y=5, width=500, height=280)

        cart_list_frame = tk.Frame(cart_frame, bd=1, relief=tk.SUNKEN)
        cart_list_frame.place(x=5, y=5, width=485, height=265)

        cart_scrollbar_y = tk.Scrollbar(cart_list_frame, orient=tk.VERTICAL)
        cart_scrollbar_x = tk.Scrollbar(cart_list_frame, orient=tk.HORIZONTAL)

        self.cart_tree = ttk.Treeview(cart_list_frame, columns=("ID", "Name", "Qty", "Price", "Total"),
                                      yscrollcommand=cart_scrollbar_y.set, xscrollcommand=cart_scrollbar_x.set, selectmode="none")

        cart_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        cart_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        cart_scrollbar_y.config(command=self.cart_tree.yview)
        cart_scrollbar_x.config(command=self.cart_tree.xview)

        self.cart_tree.heading("ID", text="ID")
        self.cart_tree.heading("Name", text="Name")
        self.cart_tree.heading("Qty", text="Qty")
        self.cart_tree.heading("Price", text="Price")
        self.cart_tree.heading("Total", text="Total")
        self.cart_tree['show'] = 'headings'
        self.cart_tree.column("ID", width=40, anchor='center')
        self.cart_tree.column("Name", width=180)
        self.cart_tree.column("Qty", width=50, anchor='center')
        self.cart_tree.column("Price", width=80, anchor='e')
        self.cart_tree.column("Total", width=90, anchor='e')
        self.cart_tree.pack(fill=tk.BOTH, expand=1)
        # Add bind for delete/modify later if needed


        # Billing Area
        bill_frame = tk.LabelFrame(frame, text="Bill Area", font=("Arial", 12, "bold"), bg="white", bd=2, relief=tk.GROOVE)
        bill_frame.place(x=520, y=5, width=320, height=415) # Make bill area taller

        bill_text_frame = tk.Frame(bill_frame, bd=1, relief=tk.SUNKEN)
        bill_text_frame.place(x=5, y=5, width=305, height=400) # Adjust height

        bill_scrollbar_y = tk.Scrollbar(bill_text_frame, orient=tk.VERTICAL)
        self.bill_text_area = tk.Text(bill_text_frame, yscrollcommand=bill_scrollbar_y.set, font=("Courier New", 9), state='disabled', wrap='word') # Start disabled
        bill_scrollbar_y.config(command=self.bill_text_area.yview)
        bill_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.bill_text_area.pack(fill=tk.BOTH, expand=1)


        # Total & Action Button Area
        total_frame = tk.Frame(frame, bg="lightgrey")
        total_frame.place(x=10, y=290, width=500, height=130)

        tk.Label(total_frame, text="Sub Total:", font=("Arial", 12, "bold"), bg="lightgrey").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        tk.Label(total_frame, textvariable=self.sub_total_var, font=("Arial", 12, "bold"), bg="white", fg="black", width=15, relief=tk.SUNKEN, anchor="e").grid(row=0, column=1, padx=10, pady=5)

        tk.Label(total_frame, text=f"Tax ({self.tax_rate:.2f}%):", font=("Arial", 12, "bold"), bg="lightgrey").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        tk.Label(total_frame, textvariable=self.tax_var, font=("Arial", 12, "bold"), bg="white", fg="black", width=15, relief=tk.SUNKEN, anchor="e").grid(row=1, column=1, padx=10, pady=5)

        tk.Label(total_frame, text="Net Total:", font=("Arial", 14, "bold"), bg="lightgrey").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        tk.Label(total_frame, textvariable=self.net_total_var, font=("Arial", 14, "bold"), bg="lightblue", fg="black", width=15, relief=tk.SUNKEN, anchor="e").grid(row=2, column=1, padx=10, pady=5)

        # Bill Action Buttons
        bill_btn_frame = tk.Frame(total_frame, bg="lightgrey")
        bill_btn_frame.grid(row=0, column=2, rowspan=3, padx=20, sticky="ns")

        generate_bill_btn = ttk.Button(bill_btn_frame, text="Generate Bill", command=self.generate_bill)
        generate_bill_btn.pack(pady=4, fill=tk.X)

        # Save Bill Button - initially disabled
        self.save_bill_btn = ttk.Button(bill_btn_frame, text="Save Bill", command=self.save_bill, state='disabled')
        self.save_bill_btn.pack(pady=4, fill=tk.X)

        reset_btn = ttk.Button(bill_btn_frame, text="Reset All", command=self.reset_all)
        reset_btn.pack(pady=4, fill=tk.X)


    # --- Core Logic Methods ---

    def load_all_products(self):
        """Loads all products into the product Treeview."""
        self.search_product_var.set("") # Clear search bar
        products = load_products_from_db()
        self.update_product_tree(products)

    def search_product(self):
        """Filters products based on the search term."""
        search = self.search_product_var.get().strip()
        if not search:
            self.load_all_products()
            return
        products = load_products_from_db(search_term=search)
        self.update_product_tree(products)

    def update_product_tree(self, products):
        """Clears and refills the product Treeview."""
        # Clear existing items
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)
        # Insert new items
        for p in products:
            # Ensure required keys exist, handle potential None values
            pid = p.get('product_id', 'N/A')
            name = p.get('name', 'N/A')
            price = p.get('price', 0.0)
            qty = p.get('quantity', 0)
            # Format price nicely
            price_str = f"{float(price):.2f}" if price is not None else "0.00"
            self.product_tree.insert('', 'end', values=(pid, name, price_str, qty))
        self.clear_selection_fields() # Clear selection when list updates

    def on_product_select(self, event=None):
        """Handles selection of a product in the product Treeview."""
        selected_items = self.product_tree.selection()
        if not selected_items:
            self.clear_selection_fields()
            return

        item_iid = selected_items[0] # Get the first selected item
        item_data = self.product_tree.item(item_iid, 'values')

        if not item_data or len(item_data) < 4:
            messagebox.showerror("Error", "Could not retrieve product data.", parent=self.root)
            self.clear_selection_fields()
            return

        # Update selection fields
        self.selected_product_id.set(item_data[0])
        self.selected_product_name.set(item_data[1])
        self.selected_product_price.set(item_data[2])
        self.selected_product_stock.set(item_data[3])
        self.selected_product_qty.set(1) # Reset quantity to 1 on new selection

    def clear_selection_fields(self):
        """Clears the product selection area."""
        self.selected_product_id.set("")
        self.selected_product_name.set("")
        self.selected_product_price.set("")
        self.selected_product_stock.set("")
        self.selected_product_qty.set(1)
        # Deselect in product tree
        selection = self.product_tree.selection()
        if selection:
            self.product_tree.selection_remove(selection)

    def add_update_cart(self):
        """Adds or updates a product in the cart."""
        prod_id = self.selected_product_id.get()
        prod_name = self.selected_product_name.get()
        try:
            prod_price = float(self.selected_product_price.get())
            prod_stock = int(self.selected_product_stock.get())
            qty_to_add = self.selected_product_qty.get()
        except ValueError:
            messagebox.showerror("Input Error", "Invalid price, stock, or quantity.", parent=self.root)
            return

        if not prod_id:
            messagebox.showwarning("No Selection", "Please select a product first.", parent=self.root)
            return

        if qty_to_add <= 0:
            messagebox.showwarning("Input Error", "Quantity must be greater than zero.", parent=self.root)
            return

        # Check if item already in cart (using product_id as identifier)
        existing_cart_item_iid = None
        current_cart_qty = 0
        for iid, item_data in self.cart_items.items():
            if item_data['id'] == prod_id:
                existing_cart_item_iid = iid
                current_cart_qty = item_data['qty']
                break

        total_required_qty = current_cart_qty + qty_to_add if not existing_cart_item_iid else qty_to_add

        if total_required_qty > prod_stock:
            messagebox.showerror("Stock Error", f"Cannot add {qty_to_add}. Only {prod_stock - current_cart_qty} more available in stock.", parent=self.root)
            return

        # Add or Update logic
        if existing_cart_item_iid:
            # Update existing item's quantity
            self.cart_items[existing_cart_item_iid]['qty'] = qty_to_add # Update to the new quantity entered
            print(f"Cart Updated: {prod_name}, New Qty: {qty_to_add}")
        else:
            # Add new item
            # Generate a unique IID for the Treeview (can just be product ID if unique or use a counter)
            new_iid = f"item_{prod_id}" # Using product ID as IID base
            self.cart_items[new_iid] = {
                'id': prod_id,
                'name': prod_name,
                'qty': qty_to_add,
                'price': prod_price
            }
            print(f"Cart Added: {prod_name}, Qty: {qty_to_add}")

        self.update_cart_treeview()
        self.update_totals()
        self.clear_selection_fields() # Clear selection after adding

    def update_cart_treeview(self):
        """Clears and refills the cart Treeview based on self.cart_items."""
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)

        for iid, item_data in self.cart_items.items():
            item_total = item_data['qty'] * item_data['price']
            self.cart_tree.insert('', 'end', iid=iid, values=(
                item_data['id'],
                item_data['name'],
                item_data['qty'],
                f"{item_data['price']:.2f}",
                f"{item_total:.2f}"
            ))

    def update_totals(self):
        """Calculates and updates the subtotal, tax, and net total labels."""
        sub_total = 0.0
        for item_data in self.cart_items.values():
            sub_total += item_data['qty'] * item_data['price']

        tax_amount = (sub_total * self.tax_rate) / 100.0
        net_total = sub_total + tax_amount

        self.sub_total_var.set(f"{sub_total:.2f}")
        self.tax_var.set(f"{tax_amount:.2f}")
        self.net_total_var.set(f"{net_total:.2f}")

    def generate_bill(self):
        """Formats and displays the bill in the Text widget."""
        if not self.cart_items:
            messagebox.showwarning("Empty Cart", "Cannot generate bill. The cart is empty.", parent=self.root)
            return

        cust_name = self.customer_name_var.get().strip() or "Walk-in Customer"
        cust_phone = self.customer_phone_var.get().strip() or "N/A"

        # Generate a simple bill number
        bill_no = f"IMS-{random.randint(1000, 9999)}-{int(time.time())}"
        current_date = time.strftime("%Y-%m-%d %H:%M:%S")

        # --- Bill Formatting ---
        bill_content = f"{'Inventory Management System':^40}\n"
        bill_content += f"{'='*40}\n"
        bill_content += f"Bill No.: {bill_no}\n"
        bill_content += f"Date: {current_date}\n"
        bill_content += f"Customer: {cust_name}\n"
        bill_content += f"Phone: {cust_phone}\n"
        bill_content += f"{'='*40}\n"
        bill_content += f"{'Product':<20}{'Qty':>5}{'Price':>7}{'Total':>8}\n"
        bill_content += f"{'-'*40}\n"

        for item_data in self.cart_items.values():
            name = item_data['name'][:19] # Truncate long names
            qty = item_data['qty']
            price = item_data['price']
            total = qty * price
            bill_content += f"{name:<20}{qty:>5}{price:>7.2f}{total:>8.2f}\n"

        bill_content += f"{'-'*40}\n"
        bill_content += f"{'Sub Total:':>30} {self.sub_total_var.get():>8}\n"
        bill_content += f"{f'Tax ({self.tax_rate:.2f}%):':>30} {self.tax_var.get():>8}\n"
        bill_content += f"{'='*40}\n"
        bill_content += f"{'Net Total:':>30} {self.net_total_var.get():>8}\n"
        bill_content += f"{'='*40}\n"
        bill_content += f"{'Thank You!':^40}\n"

        # Display in Text widget
        self.bill_text_area.config(state='normal') # Enable writing
        self.bill_text_area.delete('1.0', tk.END)   # Clear previous bill
        self.bill_text_area.insert('1.0', bill_content)
        self.bill_text_area.config(state='disabled') # Disable editing

        # Enable Save Bill button
        self.save_bill_btn.config(state='normal')

        print("Bill Generated.") # Console message

    def save_bill(self):
        """Handles saving the bill (DB update and stock update)."""
        if not self.cart_items:
            messagebox.showerror("Error", "Cart is empty. Cannot save bill.", parent=self.root)
            return

        # Prepare data for saving
        bill_data = {
            "bill_no": self.bill_text_area.get("2.0", "2.end").split(":")[1].strip(), # Extract from generated bill text
            "customer_name": self.customer_name_var.get().strip() or "Walk-in Customer",
            "customer_phone": self.customer_phone_var.get().strip() or "N/A",
            "date": self.bill_text_area.get("3.0", "3.end").split(":", 1)[1].strip(),
            "items": list(self.cart_items.values()), # Pass a copy
            "sub_total": float(self.sub_total_var.get()),
            "tax_amount": float(self.tax_var.get()),
            "net_total": float(self.net_total_var.get()),
            "parent_window": self.root # Pass root window for messageboxes in DB function
        }

        # Confirmation
        confirm = messagebox.askyesno("Confirm Sale", f"Confirm sale and update stock?\nNet Total: {bill_data['net_total']:.2f}", parent=self.root)
        if not confirm:
            return

        # 1. Try to save bill details to DB
        bill_saved = save_bill_to_db(bill_data)

        if bill_saved:
            # 2. If bill saved successfully, try to update stock
            stock_updated = update_stock_in_db(self.cart_items)

            if stock_updated:
                messagebox.showinfo("Success", "Bill saved and stock updated successfully!", parent=self.root)
                # Reset everything for the next customer after successful save and stock update
                self.reset_all()
                # Reload products to reflect updated stock
                self.load_all_products()
            else:
                messagebox.showerror("Error", "Bill details saved, but FAILED to update stock levels in the database. Manual stock correction needed!", parent=self.root)
                # Decide what to do here. Maybe disable save button again?
                self.save_bill_btn.config(state='disabled') # Prevent resaving
        else:
            messagebox.showerror("Error", "Failed to save bill details to the database.", parent=self.root)
            # Don't update stock if bill saving failed


    def reset_all(self):
        """Clears all fields, cart, and bill area."""
        self.customer_name_var.set("")
        self.customer_phone_var.set("")
        self.search_product_var.set("")
        self.clear_selection_fields()
        self.cart_items.clear()
        self.update_cart_treeview()
        self.update_totals()
        self.calculator_display_var.set("")
        self.bill_text_area.config(state='normal')
        self.bill_text_area.delete('1.0', tk.END)
        self.bill_text_area.config(state='disabled')
        self.save_bill_btn.config(state='disabled') # Disable save button
        # Optionally reload all products if search was active
        # self.load_all_products()
        print("Interface Reset.")


    # --- Calculator Methods ---
    def calculator_click(self, button):
        current_display = self.calculator_display_var.get()
        if button == '=':
            try:
                # Evaluate the expression (Use with caution in real apps due to eval risks)
                result = eval(current_display)
                self.calculator_display_var.set(str(result))
            except Exception as e:
                self.calculator_display_var.set("Error")
        else:
            # Append the button clicked to the display
            self.calculator_display_var.set(current_display + button)

    def calculator_clear(self):
        self.calculator_display_var.set("")


# --- Function to be called from another module (e.g., dashboard) ---
def create_customer_window(parent_window):
    """Creates the customer billing window as a Toplevel."""
    customer_win = tk.Toplevel(parent_window)
    app = CustomerApp(customer_win)
    customer_win.grab_set() # Make it modal if needed
    customer_win.focus_force() # Bring to front


# --- Main Execution Block (for standalone testing) ---
if __name__ == "__main__":
    root = tk.Tk()
    app = CustomerApp(root)
    root.mainloop()