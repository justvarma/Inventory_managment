# ############################################################################
# #            SINGLE FILE - INVENTORY MANAGEMENT SYSTEM                     #
# ############################################################################

import time
import pymysql
from tkinter import *
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
# from numpy.core.records import record # Check if numpy is truly needed, imported in original supplier.py but unused
# from scripts.regsetup import description # Imported in original supplier.py but unused

# --- Global Variables ---
current_main_frame = None   # Tracks the currently displayed form (employee, product, etc.)
dashboard_update_id = None  # Stores the .after() id for the dashboard update loop
main_dashboard_frame = None

# ############################################################################
# #                      DATABASE CONNECTION & SETUP                         #
# ############################################################################

def connect_database():
    """Establishes connection to the MySQL database."""
    try:
        # !!! IMPORTANT: Replace with your actual MySQL password !!!
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='Adityavarma@123' # <-- YOUR MYSQL PASSWORD HERE
        )
        cursor = connection.cursor()
        # Create database and tables if they don't exist
        cursor.execute('CREATE DATABASE IF NOT EXISTS inventory_systems')
        cursor.execute('USE inventory_systems')
        # --- Ensure all tables exist ---
        # Employee login table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS employee (
                emp_id VARCHAR(50) PRIMARY KEY,
                password VARCHAR(255) NOT NULL
            )''')
        # Employee details table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS employee_data (
                empid VARCHAR(50) PRIMARY KEY,
                name VARCHAR(100),
                email VARCHAR(100),
                gender VARCHAR(50),
                dob VARCHAR(30),
                contact VARCHAR(30),
                employment_type VARCHAR(50),
                education VARCHAR(50),
                work_shift VARCHAR(50),
                address TEXT,
                doj VARCHAR(30),
                salary VARCHAR(50),
                user_type VARCHAR(50),
                password VARCHAR(255)
            )''') # Increased password length
        # Supplier table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS supplier_data (
                invoice VARCHAR(50) PRIMARY KEY,
                name VARCHAR(100),
                contact VARCHAR(15),
                description TEXT
            )''') # Use VARCHAR for invoice if it can be non-numeric
        # Category table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS category_data (
                id VARCHAR(50) PRIMARY KEY,
                name VARCHAR(100),
                description TEXT
            )''') # Use VARCHAR for id if it can be non-numeric
        # Product table (Review this carefully for correctness)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS product_data (
                id INT AUTO_INCREMENT PRIMARY KEY,
                category VARCHAR(100),
                supplier VARCHAR(100),
                name VARCHAR(100),
                price DECIMAL(10, 2),
                discount INT DEFAULT 0,
                discounted_price DECIMAL(10, 2),
                quantity INT,
                status VARCHAR(50)
            )''')
        # Tax table
        cursor.execute('''
             CREATE TABLE IF NOT EXISTS tax_table (
                 id INT PRIMARY KEY,
                 tax DECIMAL(5, 2)
             )''')
        connection.commit() # Commit table creations

    except pymysql.Error as e:
        messagebox.showerror('Database Error', f'Database connection/setup failed: {e}\nPlease ensure MySQL is running and credentials are correct.')
        return None, None
    except Exception as e:
         messagebox.showerror('Error', f'An unexpected error occurred during DB setup: {e}')
         return None, None

    return cursor, connection

# --- Initial Database/Table Check ---
# Call once at the start to ensure DB and tables exist before login/dashboard loads fully
# connect_database() # Optional: Can call here or let first DB operation handle it

# ############################################################################
# #                      HELPER & UTILITY FUNCTIONS                          #
# ############################################################################

def on_close(window):
    """Handles window closing gracefully."""
    global dashboard_update_id
    if messagebox.askokcancel("Quit", "Do you really want to quit?", parent=window):
        print("Closing application.")
        if dashboard_update_id:
            try:
                window.after_cancel(dashboard_update_id) # Stop the update loop
            except TclError:
                pass # Ignore error if already cancelled or window destroyed
        window.quit()
        window.destroy()
        exit(0)

# ############################################################################
# #                      LOGIN FUNCTIONALITY                                 #
# ############################################################################

def login(window):
    """Displays the login screen."""
    global current_main_frame, dashboard_update_id, main_dashboard_frame

    # --- NEW: Destroy only the main dashboard frame if it exists ---
    if main_dashboard_frame and main_dashboard_frame.winfo_exists():
        # print("DEBUG: Destroying main_dashboard_frame from login()") # Debug
        main_dashboard_frame.destroy()
        main_dashboard_frame = None
    # --- End NEW ---

    # Clear any remaining popups or specific frames if necessary, but avoid general clear
    # for widget in window.winfo_children(): # Avoid this general loop if possible
    #     widget.destroy()

    # Cancel any lingering dashboard updates (belt-and-suspenders)
    if dashboard_update_id:
        try:
            window.after_cancel(dashboard_update_id)
            dashboard_update_id = None
            # print("DEBUG: Cancelled dashboard update from login()") # Debug
        except Exception: # Use generic Exception as TclError might occur here too
            pass

    window.title("Inventory Management - Login")
    # Reset to login size/position
    win_width = 600
    win_height = 450
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x_pos = (screen_width // 2) - (win_width // 2)
    y_pos = (screen_height // 2) - (win_height // 2) - 30
    window.geometry(f'{win_width}x{win_height}+{x_pos}+{y_pos}')
    window.minsize(win_width, win_height)
    window.configure(bg='white')

    # Define login_frame HERE
    login_frame = Frame(window, width=400, height=350, bg='white')
    login_frame.place(relx=0.5, rely=0.5, anchor=CENTER)

    # Inside the login function:
    def authenticate():
        emp_id = emp_id_entry.get()
        password = password_entry.get()
        if not emp_id or not password:
            messagebox.showerror('Error', 'All fields are required', parent=window)
            return

        cursor = None
        connection = None
        user = None  # <--- Initialize user to None HERE

        try:
            cursor, connection = connect_database()
            if not cursor or not connection:
                # Error message shown in connect_database or handled if it returns None
                # Ensure we don't proceed if connection failed
                return

            cursor.execute('USE inventory_systems')
            # WARNING: Store hashed passwords in production!
            query = 'SELECT * FROM employee WHERE emp_id=%s AND password=%s'
            # print(f"DEBUG: Auth Query: {query} with params ({emp_id}, *****)") # Debug
            cursor.execute(query, (emp_id, password))
            user = cursor.fetchone()  # Assign result here

            # --- Keep the login success/failure logic INSIDE the try block ---
            # --- This ensures it only runs if the query succeeded       ---
            if user:
                # print(f"DEBUG: Login successful for {emp_id}") # Debug
                messagebox.showinfo('Success', 'Login Successful', parent=window)
                # Destroy ONLY the login frame
                if login_frame.winfo_exists():
                    login_frame.destroy()
                # Call show_dashboard
                show_dashboard(window)  # Transition to dashboard
            else:
                # print(f"DEBUG: Login failed for {emp_id}") # Debug
                messagebox.showerror('Error', 'Invalid Employee ID or Password', parent=window)
            # --- End logic inside try ---

        except pymysql.Error as db_err:
            # Specific DB errors
            messagebox.showerror('Database Error', f'Login failed: {db_err}', parent=window)
        except Exception as e:
            # Other unexpected errors
            messagebox.showerror('Error', f'An unexpected error occurred during login: {e}', parent=window)
        finally:
            # print("DEBUG: Closing DB connection in authenticate") # Debug
            if cursor: cursor.close()
            if connection: connection.close()

        # --- Remove the 'if user:' check from outside the try block ---
        # It's now handled correctly within the try block after the query runs.

    # ... (rest of the login function, including create_account, layout, etc.) ...

    def create_account():
        # ... (create_account logic remains the same) ...
        pass # Keep your existing logic

    # --- Login Frame Setup (using login_frame defined above) ---
    Label(login_frame, text='Employee Login', font=('times new roman', 20, 'bold'), bg='white').pack(pady=20)
    # ... (rest of login frame widgets: labels, entries, buttons) ...
    Label(login_frame, text='Employee ID', font=('times new roman', 14), bg='white').pack(pady=(10,0))
    emp_id_entry = Entry(login_frame, font=('times new roman', 14), bg='lightgray', width=25)
    emp_id_entry.pack(pady=5)
    emp_id_entry.focus_set()

    Label(login_frame, text='Password', font=('times new roman', 14), bg='white').pack(pady=(10,0))
    password_entry = Entry(login_frame, font=('times new roman', 14), bg='lightgray', show='*', width=25)
    password_entry.pack(pady=5)

    password_entry.bind('<Return>', lambda event=None: authenticate())
    emp_id_entry.bind('<Return>', lambda event=None: password_entry.focus_set())

    Button(login_frame, text='Login', font=('times new roman', 14, 'bold'), bg='#0F4D7D', fg='white', relief=GROOVE, width=15, command=authenticate).pack(pady=20)
    Button(login_frame, text='Create New Account', font=('times new roman', 12), bg='white', fg='#0F4D7D', bd=0, activebackground='white', activeforeground='#0F4D7D', command=create_account).pack()


    window.protocol("WM_DELETE_WINDOW", lambda: on_close(window))


# ############################################################################
# #                      DASHBOARD FUNCTIONALITY                             #
# ############################################################################

def show_dashboard(window):
    """Displays the main dashboard interface."""
    global current_main_frame, dashboard_update_id, main_dashboard_frame

    # --- NEW: Create a single top-level frame for ALL dashboard content ---
    # Destroy previous if exists (e.g., from a failed load)
    if main_dashboard_frame and main_dashboard_frame.winfo_exists():
        main_dashboard_frame.destroy()

    main_dashboard_frame = Frame(window, bg='#F0F0F0')
    main_dashboard_frame.pack(fill=BOTH, expand=True) # Make it fill the window
    # --- End NEW ---

    # Reset window properties for dashboard
    window.title('Inventory Management Dashboard')
    window.geometry('1270x675+0+0')
    window.minsize(1270, 675)
    # window.configure(bg='#F0F0F0') # Background set on main_dashboard_frame now

    # --- Dashboard Specific Functions ---
    # --- Inside show_dashboard function ---
    def perform_logout():
        global dashboard_update_id, main_dashboard_frame, current_main_frame
        print("DEBUG: Performing logout...")  # Debug

        # 1. Cancel the update loop FIRST
        update_cancelled = False
        if dashboard_update_id:
            try:
                # Use the window as the master for cancelling
                window.after_cancel(dashboard_update_id)
                dashboard_update_id = None
                update_cancelled = True
                print("DEBUG: Cancelled dashboard update successfully.")  # Debug
            except Exception as e:
                print(f"DEBUG: Error cancelling dashboard update: {e}")
                # Continue anyway, but log the failure
                pass
        else:
            print("DEBUG: No dashboard update ID to cancel.")

        # --- NEW: Explicitly destroy the currently displayed FORM frame first ---
        # This might help if the form itself has problematic bindings or widgets
        if current_main_frame and current_main_frame.winfo_exists():
            try:
                print(f"DEBUG: Destroying current form frame: {current_main_frame}")  # Debug
                current_main_frame.destroy()
                current_main_frame = None
            except Exception as e:
                print(f"DEBUG: Error destroying current_main_frame: {e}")
                # Continue logout even if this fails

        # --- NEW: Update Tkinter's event loop to process pending events ---
        # This gives Tkinter a chance to handle the cancellation or other cleanup
        # before we destroy the main container.
        # print("DEBUG: Updating Tkinter event loop...") # Debug
        window.update_idletasks()
        # window.update() # More forceful update, use if idletasks isn't enough

        # 2. Destroy the main dashboard frame
        if main_dashboard_frame and main_dashboard_frame.winfo_exists():
            try:
                print("DEBUG: Destroying main_dashboard_frame")  # Debug
                main_dashboard_frame.destroy()
                main_dashboard_frame = None  # Reset global var
            except Exception as e:
                print(f"ERROR during main_dashboard_frame destruction: {e}")  # Log error
                # If destruction fails here, the TclError might still occur later
                # We might need to simply hide it instead of destroying if this persists:
                # main_dashboard_frame.pack_forget() # Alternative to destroy
        else:
            print("DEBUG: main_dashboard_frame does not exist or already destroyed.")

        # --- NEW: Another update after destruction ---
        # print("DEBUG: Updating Tkinter event loop again...") # Debug
        window.update_idletasks()

        # 3. Call login to show the login screen
        print("DEBUG: Calling login()...")  # Debug
        login(window)
        print("DEBUG: Returned from login().")  # Debug

    def update_dashboard_info():
        """Updates time and dashboard counts."""
        global dashboard_update_id
        # Make sure the label still exists before configuring or scheduling .after
        if not (subtitleLabel and subtitleLabel.winfo_exists()):
             # print("DEBUG: subtitleLabel does not exist, stopping update loop.") # Debug
             dashboard_update_id = None # Ensure ID is cleared
             return # Stop the loop if the label is gone

        # ... (rest of the update_dashboard_info logic: database queries, label config) ...
        cursor = None
        connection = None
        try:
            cursor, connection = connect_database()
            if not cursor or not connection:
                print("Update Error: Could not connect to DB")
                # Optionally update labels to show connection error state
                total_emp_count_label.config(text='DB Err')
                total_sup_count_label.config(text='DB Err')
                total_cat_count_label.config(text='DB Err')
                total_prod_count_label.config(text='DB Err')
                return

            cursor.execute('USE inventory_systems')

            emp_count, sup_count, cat_count, prod_count = "-", "-", "-", "-" # Defaults
            try: cursor.execute('SELECT count(*) FROM employee_data'); emp_count = cursor.fetchone()[0]
            except Exception as e: print(f"Warn: Failed getting employee count - {e}")
            try: cursor.execute('SELECT count(*) FROM supplier_data'); sup_count = cursor.fetchone()[0]
            except Exception as e: print(f"Warn: Failed getting supplier count - {e}")
            try: cursor.execute('SELECT count(*) FROM category_data'); cat_count = cursor.fetchone()[0]
            except Exception as e: print(f"Warn: Failed getting category count - {e}")
            try: cursor.execute('SELECT count(*) FROM product_data'); prod_count = cursor.fetchone()[0]
            except Exception as e: print(f"Warn: Failed getting product count - {e}")

            # Check if labels still exist before configuring
            if total_emp_count_label and total_emp_count_label.winfo_exists(): total_emp_count_label.config(text=str(emp_count))
            if total_sup_count_label and total_sup_count_label.winfo_exists(): total_sup_count_label.config(text=str(sup_count))
            if total_cat_count_label and total_cat_count_label.winfo_exists(): total_cat_count_label.config(text=str(cat_count))
            if total_prod_count_label and total_prod_count_label.winfo_exists(): total_prod_count_label.config(text=str(prod_count))

        except pymysql.Error as e:
            print(f"DB Error during dashboard update: {e}")
            # Update labels only if they exist
            if total_emp_count_label and total_emp_count_label.winfo_exists(): total_emp_count_label.config(text='DB Err')
            # ... etc for other labels
        except Exception as e:
            print(f"Unexpected Error during dashboard update: {e}")
            # Update labels only if they exist
            if total_emp_count_label and total_emp_count_label.winfo_exists(): total_emp_count_label.config(text='Err')
            # ... etc for other labels
        finally:
            if cursor: cursor.close()
            if connection: connection.close()

        # Update time/date only if label exists
        if subtitleLabel and subtitleLabel.winfo_exists():
            current_time = time.strftime('%I:%M:%S %p')
            current_date = time.strftime('%d/%m/%Y')
            subtitleLabel.config(text=f'Welcome Admin\t\t Date: {current_date}\t\t Time: {current_time}')
            # Schedule next update using the label's .after method
            dashboard_update_id = subtitleLabel.after(1000, update_dashboard_info)
        else:
            dashboard_update_id = None # Stop loop if label is gone

    def tax_window():
        # ... (tax_window logic remains the same, ensure parent is window or main_dashboard_frame) ...
        # Make sure to use `parent=main_dashboard_frame` in messageboxes inside tax_window
        pass # Keep existing logic

    def show_form_in_content_area(form_function):
        """Displays the selected form, hiding stats."""
        global current_main_frame
        # print(f"DEBUG: Showing form: {form_function.__name__}") # Debug
        if current_main_frame and current_main_frame.winfo_exists():
            current_main_frame.destroy()
        set_dashboard_stats_visibility(False) # Hide stats

        try:
            # Pass the content area frame AND the callback
            new_frame = form_function(content_area_frame, back_callback=show_dashboard_stats)

            if isinstance(new_frame, Frame):
                current_main_frame = new_frame
                # Form function should pack/place itself within content_area_frame
            else:
                 raise ValueError(f"{form_function.__name__} did not return a valid Frame.")
        except Exception as e:
             print(f"ERROR loading form {form_function.__name__}: {e}") # Log error
             # Display error within content area
             if content_area_frame.winfo_exists():
                 Label(content_area_frame, text=f"Error loading form:\n{e}", bg='white', fg='red', wraplength=content_area_frame.winfo_width()-40).pack(pady=20)
             # Optionally show stats again on error
             # show_dashboard_stats()

    def show_dashboard_stats():
        """Shows dashboard stats, hiding any active form."""
        global current_main_frame
        # print("DEBUG: Showing dashboard stats...") # Debug
        if current_main_frame and current_main_frame.winfo_exists():
            current_main_frame.destroy()
            current_main_frame = None
        set_dashboard_stats_visibility(True) # Show stats

    def set_dashboard_stats_visibility(visible):
        """Shows or hides the four main stat frames."""
        frames_to_toggle = [emp_frame, sup_frame, cat_frame, prod_frame] # Add sales_frame if used
        # print(f"DEBUG: Setting stats visibility: {visible}") # Debug
        # Check if parent frame exists before placing/forgetting children
        if not (main_dashboard_frame and main_dashboard_frame.winfo_exists()):
            # print("DEBUG: Main dashboard frame doesn't exist, cannot toggle stats.") # Debug
            return

        if visible:
            # Use place to show them at their designated spots
            # Ensure coordinates are relative to main_dashboard_frame if needed, or use absolute if parent is window
            emp_frame.place(in_=main_dashboard_frame, x=250, y=150, height=170, width=280)
            sup_frame.place(in_=main_dashboard_frame, x=550, y=150, height=170, width=280)
            cat_frame.place(in_=main_dashboard_frame, x=250, y=350, height=170, width=280)
            prod_frame.place(in_=main_dashboard_frame, x=550, y=350, height=170, width=280)
            for frame in frames_to_toggle:
                 if frame and frame.winfo_exists(): frame.lift()
        else:
            # Hide them
            for frame in frames_to_toggle:
                if frame and frame.winfo_exists(): frame.place_forget()


    # --- Load Assets (remains the same) ---
    assets = {}
    # ... (asset loading logic) ...
    asset_files = [
        'inventory', 'logo', 'employee', 'supplier', 'category',
        'product', 'tax', 'exit', 'back', 'total_emp', 'total_sup',
        'total_cat', 'total_prod', 'product_category'
    ]
    icons_loaded = True
    for name in asset_files:
        try:
            assets[name + '_icon'] = PhotoImage(file=f'assets/{name}.png')
        except TclError as e:
            print(f"Warning: Failed to load asset 'assets/{name}.png': {e}")
            assets[name + '_icon'] = None
            icons_loaded = False


    # --- Dashboard Layout (widgets are now children of main_dashboard_frame) ---

    titleLabel = Label(main_dashboard_frame, image=assets.get('inventory_icon'), compound=LEFT, text='   Inventory Management System',
                       font=('times new roman', 35, 'bold'), bg='#010c48', fg='white', anchor='w', padx=20)
    if assets.get('inventory_icon'): titleLabel.image = assets.get('inventory_icon')
    # Use place relative to main_dashboard_frame
    titleLabel.place(x=0, y=0, relwidth=1, height=70)

    logoutButton = Button(main_dashboard_frame, text='Logout', font=('times new roman', 16, 'bold'), bg='#E74C3C', fg='white', relief=GROOVE, command=perform_logout, cursor="hand2")
    # Adjust x based on dashboard width (1270)
    logoutButton.place(x=1150, y=15, width=100, height=40)

    subtitleLabel = Label(main_dashboard_frame, text='Loading...', font=('times new roman', 14), bg='#4d636d', fg='white', anchor='w', padx=10)
    subtitleLabel.place(x=0, y=70, relwidth=1, height=30)

    # Left Menu Frame (child of main_dashboard_frame)
    leftFrame = Frame(main_dashboard_frame, bg='#009688')
    # Place relative to main_dashboard_frame
    leftFrame.place(x=0, y=100, width=200, relheight=1, height=-100)

    if assets.get('logo_icon'):
        imageLabel = Label(leftFrame, image=assets.get('logo_icon'), bg='#009688')
        imageLabel.image = assets.get('logo_icon')
        imageLabel.pack(pady=(10, 5))

    # --- Menu Buttons (children of leftFrame) ---
    btn_font = ('times new roman', 16, 'bold')
    btn_bg = '#009688'; btn_fg = 'white'; btn_active_bg = '#007A6E'
    btn_padx = 15; btn_anchor = 'w'; btn_relief = FLAT; btn_cursor = "hand2"

    def create_menu_button(icon_name, text, command):
        # ... (create_menu_button function remains the same, parent is leftFrame) ...
        icon = assets.get(icon_name)
        btn = Button(leftFrame, image=icon, compound=LEFT, text=text, font=btn_font, bg=btn_bg, fg=btn_fg,
                     activebackground=btn_active_bg, activeforeground=btn_fg,
                     anchor=btn_anchor, relief=btn_relief, padx=btn_padx, cursor=btn_cursor,
                     command=command)
        if icon: btn.image = icon
        btn.pack(fill=X, pady=2)
        return btn

    create_menu_button(None, ' Dashboard', show_dashboard_stats)
    create_menu_button('employee_icon', ' Employees', lambda: show_form_in_content_area(employee_form))
    create_menu_button('supplier_icon', ' Supplier', lambda: show_form_in_content_area(supplier_form))
    create_menu_button('category_icon', ' Category', lambda: show_form_in_content_area(category_form))
    create_menu_button('product_icon', ' Product', lambda: show_form_in_content_area(product_form))
    create_menu_button('tax_icon', ' Tax', tax_window)
    create_menu_button('exit_icon', ' Exit', lambda: on_close(window))


    # --- Main Content Area (child of main_dashboard_frame) ---
    content_area_frame = Frame(main_dashboard_frame, bg='white')
    content_area_frame.place(x=200, y=100, relwidth=1, width=-200, relheight=1, height=-100)


    # --- Dashboard Stats Widgets (children of main_dashboard_frame, placed within it) ---
    stat_font_h = ('times new roman', 15, 'bold')
    stat_font_c = ('times new roman', 30, 'bold')
    stat_pady = 5

    def create_stat_frame(parent, color, icon_name, text): # Removed x, y - will be placed by set_visibility
        frame = Frame(parent, bg=color, bd=3, relief=RIDGE)
        # Don't place here initially, place in set_dashboard_stats_visibility
        icon = assets.get(icon_name)
        if icon:
            icon_label = Label(frame, image=icon, bg=color)
            icon_label.image = icon
            icon_label.pack(pady=stat_pady)
        Label(frame, text=text, bg=color, fg='white', font=stat_font_h).pack()
        count_label = Label(frame, text='-', bg=color, fg='white', font=stat_font_c)
        count_label.pack()
        return frame, count_label

    # Create frames as children of main_dashboard_frame
    emp_frame, total_emp_count_label = create_stat_frame(main_dashboard_frame, '#2C3E50', 'total_emp_icon', 'Total Employees')
    sup_frame, total_sup_count_label = create_stat_frame(main_dashboard_frame, '#8E44AD', 'total_sup_icon', 'Total Suppliers')
    cat_frame, total_cat_count_label = create_stat_frame(main_dashboard_frame, '#27AE60', 'total_cat_icon', 'Total Categories')
    prod_frame, total_prod_count_label = create_stat_frame(main_dashboard_frame, '#2980B9', 'total_prod_icon', 'Total Products')


    # --- Final Dashboard Setup ---
    show_dashboard_stats() # Place stats initially
    # Start update loop only if subtitleLabel was created successfully
    if subtitleLabel and subtitleLabel.winfo_exists():
        update_dashboard_info()
    else:
        print("ERROR: Subtitle label failed to create, cannot start dashboard update.")

    window.protocol("WM_DELETE_WINDOW", lambda: on_close(window))


# ... (Keep the form functions: employee_form, supplier_form, category_form, product_form) ...
# ... (Make sure messageboxes inside these forms use parent=the_form_frame) ...


# ############################################################################
# #                      EMPLOYEE FORM FUNCTIONALITY                         #
# ############################################################################

def employee_form(parent_frame, back_callback):
    """Creates and places the Employee Management form."""

    # --- Local Helper Functions for Employee Form ---
    def employee_treeview_data(treeview):
        cursor, conn = None, None
        try:
            cursor, conn = connect_database()
            if not cursor or not conn: return
            cursor.execute('USE inventory_systems')
            cursor.execute('SELECT empid, name, email, gender, dob, contact, employment_type, education, work_shift, address, doj, salary, user_type FROM employee_data') # Exclude password from view
            records = cursor.fetchall()
            treeview.delete(*treeview.get_children())
            for record in records:
                treeview.insert('', END, values=record)
        except pymysql.Error as e:
            messagebox.showerror('DB Error', f'Failed to fetch employee data: {e}', parent=employee_frame)
        except Exception as e:
             messagebox.showerror('Error', f'An unexpected error occurred: {e}', parent=employee_frame)
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def select_data(event): # Pass widgets implicitly from outer scope
        index = employee_treeview.selection()
        if not index: return # No selection
        content = employee_treeview.item(index)
        row = content['values']
        # Clear fields first
        clear_fields(False) # False means don't clear treeview selection
        # Populate fields (assuming row order matches treeview columns)
        try:
            empid_entry.config(state=NORMAL) # Allow editing ID temporarily for display
            empid_entry.delete(0, END); empid_entry.insert(0, row[0])
            empid_entry.config(state=DISABLED) # Disable ID field again

            name_entry.delete(0, END); name_entry.insert(0, row[1])
            email_entry.delete(0, END); email_entry.insert(0, row[2])
            gender_combobox.set(row[3])
            try: dob_date_entry.set_date(row[4]) # Handle potential date format issues
            except: dob_date_entry.set_date(time.strftime('%d/%m/%Y')) # Default on error
            contact_entry.delete(0, END); contact_entry.insert(0, row[5])
            employment_type_combobox.set(row[6])
            education_combobox.set(row[7])
            work_shift_combobox.set(row[8])
            address_text.delete(1.0, END); address_text.insert(1.0, row[9])
            try: doj_date_entry.set_date(row[10])
            except: doj_date_entry.set_date(time.strftime('%d/%m/%Y'))
            salary_entry.delete(0, END); salary_entry.insert(0, row[11])
            usertype_combobox.set(row[12])
            # Password field is generally NOT populated back for security
            password_entry.delete(0, END)
        except IndexError:
            messagebox.showerror("Error", "Selected row data is incomplete or incorrect.", parent=employee_frame)
        except Exception as e:
             messagebox.showerror("Error", f"Failed to load data: {e}", parent=employee_frame)

    def add_employee_local():
        # Get all values from entries/widgets
        empid = empid_entry_add.get() # Use the separate entry for adding
        name = name_entry.get()
        email = email_entry.get()
        gender = gender_combobox.get()
        dob = dob_date_entry.get()
        contact = contact_entry.get()
        employment_type = employment_type_combobox.get()
        education = education_combobox.get()
        work_shift = work_shift_combobox.get()
        address = address_text.get(1.0, END).strip() # Get text content correctly
        doj = doj_date_entry.get()
        salary = salary_entry.get()
        user_type = usertype_combobox.get()
        password = password_entry.get() # Plain text (insecure)

        # Validation
        if (not empid or not name or not email or gender == 'Select Gender' or not contact or
            employment_type == 'Select Type' or education == 'Select Education' or
            work_shift == 'Select Work Shift' or not address or not salary or
            user_type == 'Select User Type' or not password):
            messagebox.showerror('Error', 'All fields are required for adding', parent=employee_frame)
            return

        cursor, conn = None, None
        try:
            cursor, conn = connect_database()
            if not cursor or not conn: return
            cursor.execute('USE inventory_systems')

            cursor.execute('SELECT empid FROM employee_data WHERE empid=%s', (empid,))
            if cursor.fetchone():
                messagebox.showerror('Error', 'Employee ID already exists in details table.', parent=employee_frame)
                return
            # Also check the login table
            cursor.execute('SELECT emp_id FROM employee WHERE emp_id=%s', (empid,))
            if cursor.fetchone():
                 messagebox.showerror('Error', 'Employee ID already exists in login table. Cannot reuse.', parent=employee_frame)
                 return


            # WARNING: Hash password before storing!
            # import bcrypt
            # hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            # Insert into employee_data
            cursor.execute('''INSERT INTO employee_data
                           (empid, name, email, gender, dob, contact, employment_type, education, work_shift, address, doj, salary, user_type, password)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                           (empid, name, email, gender, dob, contact, employment_type, education, work_shift, address, doj, salary, user_type, password)) # Store plain password

            # ALSO Insert into login table (employee)
            cursor.execute('''INSERT INTO employee (emp_id, password) VALUES (%s, %s)''', (empid, password)) # Store plain password

            conn.commit()
            employee_treeview_data(employee_treeview) # Refresh treeview
            messagebox.showinfo('Success', 'Employee added successfully to both tables.', parent=employee_frame)
            clear_fields(True) # Clear fields and selection

        except pymysql.Error as e:
            messagebox.showerror('Database Error', f'Failed to add employee: {e}', parent=employee_frame)
            if conn: conn.rollback()
        except Exception as e:
             messagebox.showerror('Error', f'An unexpected error occurred: {e}', parent=employee_frame)
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def clear_fields(clear_selection=True):
        # Clear all entry fields and reset comboboxes/dates
        empid_entry_add.delete(0, END) # Clear the add-specific ID field
        empid_entry.config(state=NORMAL); empid_entry.delete(0, END); empid_entry.config(state=DISABLED) # Clear display ID
        name_entry.delete(0, END)
        email_entry.delete(0, END)
        try: dob_date_entry.set_date(time.strftime('%d/%m/%Y'))
        except: pass # Ignore if DateEntry is not valid yet
        gender_combobox.set('Select Gender')
        contact_entry.delete(0, END)
        employment_type_combobox.set('Select Employment Type')
        education_combobox.set('Select Education')
        work_shift_combobox.set('Select Work Shift')
        address_text.delete(1.0, END)
        try: doj_date_entry.set_date(time.strftime('%d/%m/%Y'))
        except: pass
        salary_entry.delete(0, END)
        usertype_combobox.set('Select User Type')
        password_entry.delete(0, END)
        if clear_selection and employee_treeview.selection():
            employee_treeview.selection_remove(employee_treeview.selection())

    def update_employee_local():
        selected = employee_treeview.selection()
        if not selected:
            messagebox.showerror('Error', 'Please select an employee from the list to update.', parent=employee_frame)
            return

        # Get ID from the disabled display field (set during selection)
        empid = empid_entry.get()
        if not empid: # Should not happen if selection worked, but check anyway
             messagebox.showerror('Error', 'Cannot identify selected employee ID.', parent=employee_frame)
             return

        # Get other values
        name = name_entry.get()
        email = email_entry.get()
        gender = gender_combobox.get()
        dob = dob_date_entry.get()
        contact = contact_entry.get()
        employment_type = employment_type_combobox.get()
        education = education_combobox.get()
        work_shift = work_shift_combobox.get()
        address = address_text.get(1.0, END).strip()
        doj = doj_date_entry.get()
        salary = salary_entry.get()
        user_type = usertype_combobox.get()
        password = password_entry.get() # Get potentially new password

         # Validation (similar to add, but ID is fixed)
        if (not name or not email or gender == 'Select Gender' or not contact or
            employment_type == 'Select Type' or education == 'Select Education' or
            work_shift == 'Select Work Shift' or not address or not salary or
            user_type == 'Select User Type'):
            # Password can be optional for update if not changing
            messagebox.showerror('Error', 'All fields (except possibly password) are required for update', parent=employee_frame)
            return

        cursor, conn = None, None
        try:
            cursor, conn = connect_database()
            if not cursor or not conn: return
            cursor.execute('USE inventory_systems')

            # Fetch current data to compare (optional, but good practice)
            # cursor.execute('SELECT name, email, gender, dob, contact, employment_type, education, work_shift, address, doj, salary, user_type FROM employee_data WHERE empid=%s', (empid,))
            # current_data = cursor.fetchone() # Compare if needed

            # Prepare update query parts
            update_fields = []
            update_values = []

            # Update employee_data table
            update_fields_data = []
            update_values_data = []

            # Check which fields to update (Example for password)
            # WARNING: Hash password if provided
            if password:
                # import bcrypt
                # hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                update_fields_data.append("password=%s")
                update_values_data.append(password) # Store plain text (insecure)


            update_query_data = f'''UPDATE employee_data SET
                                name=%s, email=%s, gender=%s, dob=%s, contact=%s,
                                employment_type=%s, education=%s, work_shift=%s,
                                address=%s, doj=%s, salary=%s, user_type=%s
                                {", " + ", ".join(update_fields_data) if update_fields_data else ""}
                                WHERE empid=%s'''
            update_params_data = (name, email, gender, dob, contact, employment_type,
                                  education, work_shift, address, doj, salary, user_type,
                                  *update_values_data, empid)

            cursor.execute(update_query_data, update_params_data)


            # ALSO Update login table (employee) IF password changed
            if password:
                 update_query_login = "UPDATE employee SET password=%s WHERE emp_id=%s"
                 cursor.execute(update_query_login, (password, empid)) # Store plain text (insecure)


            conn.commit()
            employee_treeview_data(employee_treeview) # Refresh
            messagebox.showinfo('Success', 'Employee data updated successfully.', parent=employee_frame)
            clear_fields(True)

        except pymysql.Error as e:
            messagebox.showerror('Database Error', f'Failed to update employee: {e}', parent=employee_frame)
            if conn: conn.rollback()
        except Exception as e:
             messagebox.showerror('Error', f'An unexpected error occurred: {e}', parent=employee_frame)
        finally:
            if cursor: cursor.close()
            if conn: conn.close()


    def delete_employee_local():
        selected = employee_treeview.selection()
        if not selected:
            messagebox.showerror('Error', 'Please select an employee to delete.', parent=employee_frame)
            return

        empid = empid_entry.get() # Get ID from the display field
        if not empid:
             messagebox.showerror('Error', 'Cannot identify selected employee ID.', parent=employee_frame)
             return

        if messagebox.askyesno('Confirm Delete', f'Are you sure you want to delete employee ID {empid}?\nThis will remove data from BOTH details and login tables.', parent=employee_frame):
            cursor, conn = None, None
            try:
                cursor, conn = connect_database()
                if not cursor or not conn: return
                cursor.execute('USE inventory_systems')

                # Delete from employee_data
                cursor.execute('DELETE FROM employee_data WHERE empid=%s', (empid,))
                rows_deleted_data = cursor.rowcount

                 # Delete from employee (login table)
                cursor.execute('DELETE FROM employee WHERE emp_id=%s', (empid,))
                rows_deleted_login = cursor.rowcount

                conn.commit()

                if rows_deleted_data > 0 or rows_deleted_login > 0:
                    employee_treeview_data(employee_treeview) # Refresh
                    messagebox.showinfo('Success', f'Employee ID {empid} deleted successfully.', parent=employee_frame)
                    clear_fields(True)
                else:
                     messagebox.showwarning('Not Found', f'Employee ID {empid} not found for deletion.', parent=employee_frame)


            except pymysql.Error as e:
                messagebox.showerror('Database Error', f'Failed to delete employee: {e}', parent=employee_frame)
                if conn: conn.rollback()
            except Exception as e:
                 messagebox.showerror('Error', f'An unexpected error occurred: {e}', parent=employee_frame)
            finally:
                if cursor: cursor.close()
                if conn: conn.close()


    def search_employee_local():
        search_option = search_combobox.get()
        value = search_entry.get()

        if search_option == 'Search By':
            messagebox.showerror('Error', 'Please select a search criteria.', parent=employee_frame)
        elif not value:
            messagebox.showerror('Error', 'Please enter a value to search.', parent=employee_frame)
        else:
            cursor, conn = None, None
            try:
                cursor, conn = connect_database()
                if not cursor or not conn: return
                cursor.execute('USE inventory_systems')

                # Use LIKE for partial matching, adjust column name if needed
                # Make sure search_option is a valid column name to prevent SQL injection if values were dynamic
                valid_search_options = {'EmpID': 'empid', 'Name': 'name', 'Email': 'email'}
                if search_option not in valid_search_options:
                    messagebox.showerror('Error', 'Invalid search option selected.', parent=employee_frame)
                    return
                db_column = valid_search_options[search_option]

                query = f'SELECT empid, name, email, gender, dob, contact, employment_type, education, work_shift, address, doj, salary, user_type FROM employee_data WHERE {db_column} LIKE %s'
                cursor.execute(query, (f'%{value}%',))
                records = cursor.fetchall()

                employee_treeview.delete(*employee_treeview.get_children()) # Clear existing results
                if not records:
                    messagebox.showinfo('Not Found', 'No matching employee records found.', parent=employee_frame)
                else:
                    for record in records:
                        employee_treeview.insert('', END, values=record)

            except pymysql.Error as e:
                messagebox.showerror('Database Error', f'Failed to search employees: {e}', parent=employee_frame)
            except Exception as e:
                 messagebox.showerror('Error', f'An unexpected error occurred: {e}', parent=employee_frame)
            finally:
                if cursor: cursor.close()
                if conn: conn.close()

    def show_all_local():
        employee_treeview_data(employee_treeview)
        search_entry.delete(0, END)
        search_combobox.set('Search By')
        clear_fields(True)

    # --- Employee Form Layout ---
    employee_frame = Frame(parent_frame, bg='white')
    employee_frame.pack(fill=BOTH, expand=True) # Fill the content area

    heading_label = Label(employee_frame, text='Manage Employee Details', font=('times new roman', 16, 'bold'), bg='#0F4D7D', fg='white')
    heading_label.place(x=0, y=0, relwidth=1, height=30) # Place heading within frame

    # Back Button using the callback
    try:
        back_icon = PhotoImage(file='../assets/back.png')
        back_button = Button(employee_frame, image=back_icon, bd=0, cursor='hand2', bg='white', command=back_callback)
        back_button.image = back_icon # Keep reference
        back_button.place(x=5, y=2)
    except TclError:
         # Fallback if icon fails
         back_button = Button(employee_frame, text="< Back", bd=1, cursor='hand2', command=back_callback)
         back_button.place(x=5, y=2)


    # Top Frame for Search and Treeview
    top_frame = Frame(employee_frame, bg='white')
    top_frame.place(x=0, y=30, relwidth=1, height=245) # Adjust height

    search_frame = Frame(top_frame, bg='white')
    search_frame.pack(pady=5) # Pack search at the top

    search_combobox = ttk.Combobox(search_frame, values=('EmpID', 'Name', 'Email'), font=('times new roman', 12), state='readonly', justify=CENTER, width=15)
    search_combobox.set('Search By')
    search_combobox.grid(row=0, column=0, padx=10)
    search_entry = Entry(search_frame, font=('times new roman', 12), bg='lightyellow', width=20)
    search_entry.grid(row=0, column=1, padx=5)
    search_button = Button(search_frame, text='Search', font=('times new roman', 12, 'bold'), width=8, cursor='hand2', fg='white', bg='#0F4D7D', command=search_employee_local)
    search_button.grid(row=0, column=2, padx=5)
    show_button = Button(search_frame, text='Show All', font=('times new roman', 12, 'bold'), width=8, cursor='hand2', fg='white', bg='#0F4D7D', command=show_all_local)
    show_button.grid(row=0, column=3, padx=10)

    # Treeview Frame
    tree_frame = Frame(top_frame)
    tree_frame.pack(fill=BOTH, expand=True, padx=10, pady=(0,5))

    horizontal_scrollbar = Scrollbar(tree_frame, orient=HORIZONTAL)
    vertical_scrollbar = Scrollbar(tree_frame, orient=VERTICAL)

    employee_treeview = ttk.Treeview(tree_frame, columns=(
        'empid', 'name', 'email', 'gender', 'dob', 'contact', 'employment_type', 'education', 'work_shift', 'address',
        'doj', 'salary', 'usertype'), show='headings', yscrollcommand=vertical_scrollbar.set,
                                     xscrollcommand=horizontal_scrollbar.set, height=7) # Adjust height

    horizontal_scrollbar.pack(side=BOTTOM, fill=X)
    vertical_scrollbar.pack(side=RIGHT, fill=Y)
    horizontal_scrollbar.config(command=employee_treeview.xview)
    vertical_scrollbar.config(command=employee_treeview.yview)
    employee_treeview.pack(fill=BOTH, expand=True)

    # Define headings and columns (adjust widths as needed)
    cols = { 'empid': ('EmpID', 60), 'name': ('Name', 120), 'email': ('Email', 160), 'gender': ('Gender', 70),
             'dob': ('D.O.B', 90), 'contact': ('Contact', 100), 'employment_type': ('Emp Type', 110),
             'education': ('Education', 100), 'work_shift': ('Shift', 80), 'address': ('Address', 180),
             'doj': ('D.O.J', 90), 'salary': ('Salary', 90), 'usertype': ('User Type', 80) }
    for col_id, (text, width) in cols.items():
        employee_treeview.heading(col_id, text=text)
        employee_treeview.column(col_id, width=width, anchor=W)

    # Detail Frame for Entry Fields
    detail_frame = Frame(employee_frame, bg='white')
    detail_frame.place(x=10, y=280, relwidth=1, width=-20, relheight=1, height=-320) # Adjust position/size

    # --- Row 0 ---
    # Use a separate ID field for adding, make display ID read-only
    empid_label_add = Label(detail_frame, text='EmpID (Add New)', font=('times new roman', 12), bg='white')
    empid_label_add.grid(row=0, column=0, padx=10, pady=5, sticky='w')
    empid_entry_add = Entry(detail_frame, font=('times new roman', 12), bg='lightyellow', width=20)
    empid_entry_add.grid(row=0, column=1, padx=5, pady=5)

    name_label = Label(detail_frame, text='Name', font=('times new roman', 12), bg='white')
    name_label.grid(row=0, column=2, padx=10, pady=5, sticky='w')
    name_entry = Entry(detail_frame, font=('times new roman', 12), bg='lightyellow', width=20)
    name_entry.grid(row=0, column=3, padx=5, pady=5)

    email_label = Label(detail_frame, text='Email', font=('times new roman', 12), bg='white')
    email_label.grid(row=0, column=4, padx=10, pady=5, sticky='w')
    email_entry = Entry(detail_frame, font=('times new roman', 12), bg='lightyellow', width=20)
    email_entry.grid(row=0, column=5, padx=5, pady=5)

    # --- Row 1 ---
    gender_label = Label(detail_frame, text='Gender', font=('times new roman', 12), bg='white')
    gender_label.grid(row=1, column=0, padx=10, pady=5, sticky='w')
    gender_combobox = ttk.Combobox(detail_frame, values=('Male', 'Female', 'Other'), font=('times new roman', 12), width=18, state='readonly')
    gender_combobox.set('Select Gender')
    gender_combobox.grid(row=1, column=1, padx=5, pady=5)

    dob_label = Label(detail_frame, text='Date of Birth', font=('times new roman', 12), bg='white')
    dob_label.grid(row=1, column=2, padx=10, pady=5, sticky='w')
    dob_date_entry = DateEntry(detail_frame, width=18, font=('times new roman', 12), state='readonly', date_pattern='dd/MM/yyyy', background='darkblue', foreground='white', borderwidth=2)
    dob_date_entry.grid(row=1, column=3, padx=5, pady=5)

    contact_label = Label(detail_frame, text='Contact', font=('times new roman', 12), bg='white')
    contact_label.grid(row=1, column=4, padx=10, pady=5, sticky='w')
    contact_entry = Entry(detail_frame, font=('times new roman', 12), bg='lightyellow', width=20)
    contact_entry.grid(row=1, column=5, padx=5, pady=5)

    # --- Row 2 ---
    employment_type_label = Label(detail_frame, text='Emp Type', font=('times new roman', 12), bg='white')
    employment_type_label.grid(row=2, column=0, padx=10, pady=5, sticky='w')
    employment_type_combobox = ttk.Combobox(detail_frame, values=('Full-Time', 'Part-Time', 'Contract'), font=('times new roman', 12), width=18, state='readonly')
    employment_type_combobox.set('Select Type')
    employment_type_combobox.grid(row=2, column=1, padx=5, pady=5)

    education_label = Label(detail_frame, text='Education', font=('times new roman', 12), bg='white')
    education_label.grid(row=2, column=2, padx=10, pady=5, sticky='w')
    education_options = ['High School', 'Diploma', 'Associate Degree', 'Bachelor Degree', 'Master Degree', 'Doctorate']
    education_combobox = ttk.Combobox(detail_frame, values=education_options, font=('times new roman', 12), width=18, state='readonly')
    education_combobox.set('Select Education')
    education_combobox.grid(row=2, column=3, padx=5, pady=5)

    work_shift_label = Label(detail_frame, text='Work Shift', font=('times new roman', 12), bg='white')
    work_shift_label.grid(row=2, column=4, padx=10, pady=5, sticky='w')
    work_shift_combobox = ttk.Combobox(detail_frame, values=('Morning', 'Afternoon', 'Night'), font=('times new roman', 12), width=18, state='readonly')
    work_shift_combobox.set('Select Work Shift')
    work_shift_combobox.grid(row=2, column=5, padx=5, pady=5)

    # --- Row 3 & 4 (Address spans 2 rows) ---
    address_label = Label(detail_frame, text='Address', font=('times new roman', 12), bg='white')
    address_label.grid(row=3, column=0, padx=10, pady=5, sticky='nw')
    address_text = Text(detail_frame, font=('times new roman', 12), bg='lightyellow', height=3, width=20, bd=1, relief=SOLID)
    address_text.grid(row=3, column=1, padx=5, pady=5, rowspan=2, sticky='we') # Span 2 rows

    doj_label = Label(detail_frame, text='Date of Joining', font=('times new roman', 12), bg='white')
    doj_label.grid(row=3, column=2, padx=10, pady=5, sticky='w')
    doj_date_entry = DateEntry(detail_frame, width=18, font=('times new roman', 12), state='readonly', date_pattern='dd/MM/yyyy', background='darkblue', foreground='white', borderwidth=2)
    doj_date_entry.grid(row=3, column=3, padx=5, pady=5)

    salary_label = Label(detail_frame, text='Salary', font=('times new roman', 12), bg='white')
    salary_label.grid(row=3, column=4, padx=10, pady=5, sticky='w')
    salary_entry = Entry(detail_frame, font=('times new roman', 12), bg='lightyellow', width=20)
    salary_entry.grid(row=3, column=5, padx=5, pady=5)

    # --- Row 4 ---
    usertype_label = Label(detail_frame, text='User Type', font=('times new roman', 12), bg='white')
    usertype_label.grid(row=4, column=2, padx=10, pady=5, sticky='w')
    usertype_combobox = ttk.Combobox(detail_frame, values=('Admin', 'Employee'), font=('times new roman', 12), width=18, state='readonly')
    usertype_combobox.set('Select User Type')
    usertype_combobox.grid(row=4, column=3, padx=5, pady=5)

    password_label = Label(detail_frame, text='Password', font=('times new roman', 12), bg='white')
    password_label.grid(row=4, column=4, padx=10, pady=5, sticky='w')
    password_entry = Entry(detail_frame, font=('times new roman', 12), bg='lightyellow', width=20, show='*') # Show '*' for password
    password_entry.grid(row=4, column=5, padx=5, pady=5)

    # Display-only ID field (row 5, column 0) - disabled
    empid_label_display = Label(detail_frame, text='Selected EmpID', font=('times new roman', 12), bg='white')
    empid_label_display.grid(row=5, column=0, padx=10, pady=5, sticky='w')
    empid_entry = Entry(detail_frame, font=('times new roman', 12), bg='lightgrey', width=20, state=DISABLED) # Disabled
    empid_entry.grid(row=5, column=1, padx=5, pady=5)


    # --- Button Frame ---
    button_frame = Frame(employee_frame, bg='white')
    # Adjust y position based on detail_frame placement
    button_frame.place(x=0, y=520, relwidth=1, height=45)

    btn_font_small = ('times new roman', 12, 'bold')
    btn_width = 10

    add_button = Button(button_frame, text='Add', font=btn_font_small, width=btn_width, cursor='hand2', fg='white', bg='#0F4D7D', command=add_employee_local)
    update_button = Button(button_frame, text='Update', font=btn_font_small, width=btn_width, cursor='hand2', fg='white', bg='#0F4D7D', command=update_employee_local)
    delete_button = Button(button_frame, text='Delete', font=btn_font_small, width=btn_width, cursor='hand2', fg='white', bg='#DC3545', command=delete_employee_local)
    clear_button = Button(button_frame, text='Clear', font=btn_font_small, width=btn_width, cursor='hand2', fg='white', bg='#6C757D', command=lambda: clear_fields(True))

    # Pack buttons centrally
    button_frame.pack_propagate(False) # Prevent resizing
    add_button.pack(side=LEFT, padx=(200, 10), pady=5) # Add more left padding
    update_button.pack(side=LEFT, padx=10, pady=5)
    delete_button.pack(side=LEFT, padx=10, pady=5)
    clear_button.pack(side=LEFT, padx=(10, 20), pady=5)


    # --- Initial Data Load and Bindings ---
    employee_treeview_data(employee_treeview)
    employee_treeview.bind('<ButtonRelease-1>', select_data)

    return employee_frame # Return the main frame for this form

# ############################################################################
# #                    SUPPLIER FORM FUNCTIONALITY                           #
# ############################################################################

def supplier_form(parent_frame, back_callback):
    """Creates and places the Supplier Management form."""

    # --- Local Helper Functions for Supplier Form ---
    def supplier_treeview_data(treeview):
        cursor, conn = None, None
        try:
            cursor, conn = connect_database()
            if not cursor or not conn: return
            cursor.execute('USE inventory_systems')
            cursor.execute('SELECT * FROM supplier_data')
            records = cursor.fetchall()
            treeview.delete(*treeview.get_children())
            for record in records:
                treeview.insert('', END, values=record)
        except pymysql.Error as e:
            messagebox.showerror('DB Error', f'Failed to fetch supplier data: {e}', parent=supplier_frame)
        except Exception as e:
             messagebox.showerror('Error', f'An unexpected error occurred: {e}', parent=supplier_frame)
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def select_data(event): # Widgets from outer scope
        index = supplier_treeview.selection()
        if not index: return
        content = supplier_treeview.item(index)
        actual_content = content['values']
        clear_supplier(False) # Don't clear selection
        try:
            invoice_entry.config(state=NORMAL)
            invoice_entry.delete(0, END); invoice_entry.insert(0, actual_content[0])
            invoice_entry.config(state=DISABLED)
            name_entry.delete(0, END); name_entry.insert(0, actual_content[1])
            contact_entry.delete(0, END); contact_entry.insert(0, actual_content[2])
            description_text.delete(1.0, END); description_text.insert(1.0, actual_content[3])
        except IndexError:
             messagebox.showerror("Error", "Selected row data is incomplete.", parent=supplier_frame)
        except Exception as e:
             messagebox.showerror("Error", f"Failed to load data: {e}", parent=supplier_frame)

    def add_supplier_local():
        invoice = invoice_entry_add.get() # Use add-specific field
        name = name_entry.get()
        contact = contact_entry.get()
        description = description_text.get(1.0, END).strip()

        if not invoice or not name or not contact or not description:
            messagebox.showerror('Error', 'All fields are required', parent=supplier_frame)
            return

        cursor, conn = None, None
        try:
            cursor, conn = connect_database()
            if not cursor or not conn: return
            cursor.execute('USE inventory_systems')
            # Table creation in connect_database

            cursor.execute('SELECT invoice FROM supplier_data WHERE invoice=%s', (invoice,))
            if cursor.fetchone():
                messagebox.showerror('Error', 'Invoice No. already exists', parent=supplier_frame)
                return

            cursor.execute('INSERT INTO supplier_data VALUES (%s, %s, %s, %s)', (invoice, name, contact, description))
            conn.commit()
            supplier_treeview_data(supplier_treeview)
            messagebox.showinfo('Success', 'Supplier added successfully', parent=supplier_frame)
            clear_supplier(True)

        except pymysql.Error as e:
            messagebox.showerror('Database Error', f'Failed to add supplier: {e}', parent=supplier_frame)
            if conn: conn.rollback()
        except Exception as e:
             messagebox.showerror('Error', f'An unexpected error occurred: {e}', parent=supplier_frame)
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def update_supplier_local():
        selected = supplier_treeview.selection()
        if not selected:
            messagebox.showerror('Error', 'Please select a supplier to update.', parent=supplier_frame)
            return
        invoice = invoice_entry.get() # Get from disabled field
        name = name_entry.get()
        contact = contact_entry.get()
        description = description_text.get(1.0, END).strip()

        if not invoice or not name or not contact or not description:
            messagebox.showerror('Error', 'All fields are required for update.', parent=supplier_frame)
            return

        cursor, conn = None, None
        try:
            cursor, conn = connect_database()
            if not cursor or not conn: return
            cursor.execute('USE inventory_systems')

            # Optional: Compare with current data before updating
            cursor.execute('UPDATE supplier_data SET name=%s, contact=%s, description=%s WHERE invoice=%s',
                           (name, contact, description, invoice))
            if cursor.rowcount == 0:
                 messagebox.showinfo('Info', 'No changes detected or supplier not found.', parent=supplier_frame)
            else:
                 conn.commit()
                 supplier_treeview_data(supplier_treeview)
                 messagebox.showinfo('Success', 'Supplier updated successfully', parent=supplier_frame)
                 clear_supplier(True)

        except pymysql.Error as e:
            messagebox.showerror('Database Error', f'Failed to update supplier: {e}', parent=supplier_frame)
            if conn: conn.rollback()
        except Exception as e:
             messagebox.showerror('Error', f'An unexpected error occurred: {e}', parent=supplier_frame)
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def delete_supplier_local():
        selected = supplier_treeview.selection()
        if not selected:
            messagebox.showerror('Error', 'Please select a supplier to delete.', parent=supplier_frame)
            return
        invoice = invoice_entry.get() # Get from disabled field
        if not invoice:
             messagebox.showerror('Error', 'Cannot identify selected supplier invoice.', parent=supplier_frame)
             return

        if messagebox.askyesno('Confirm Delete', f'Are you sure you want to delete supplier with Invoice No. {invoice}?', parent=supplier_frame):
            cursor, conn = None, None
            try:
                cursor, conn = connect_database()
                if not cursor or not conn: return
                cursor.execute('USE inventory_systems')
                cursor.execute('DELETE FROM supplier_data WHERE invoice=%s', (invoice,))
                if cursor.rowcount > 0:
                    conn.commit()
                    supplier_treeview_data(supplier_treeview)
                    messagebox.showinfo('Success', f'Supplier {invoice} deleted successfully.', parent=supplier_frame)
                    clear_supplier(True)
                else:
                    messagebox.showwarning('Not Found', f'Supplier with Invoice No. {invoice} not found.', parent=supplier_frame)

            except pymysql.Error as e:
                # Check for foreign key constraints if supplier is linked elsewhere (e.g., products)
                if e.args[0] == 1451: # Foreign key constraint error code
                     messagebox.showerror('Deletion Failed', f'Cannot delete supplier {invoice}.\nIt is likely linked to existing products.\nPlease update or delete related products first.', parent=supplier_frame)
                else:
                     messagebox.showerror('Database Error', f'Failed to delete supplier: {e}', parent=supplier_frame)
                if conn: conn.rollback()
            except Exception as e:
                 messagebox.showerror('Error', f'An unexpected error occurred: {e}', parent=supplier_frame)
            finally:
                if cursor: cursor.close()
                if conn: conn.close()

    def clear_supplier(clear_selection=True):
        invoice_entry_add.delete(0, END)
        invoice_entry.config(state=NORMAL); invoice_entry.delete(0, END); invoice_entry.config(state=DISABLED)
        name_entry.delete(0, END)
        contact_entry.delete(0, END)
        description_text.delete(1.0, END)
        if clear_selection and supplier_treeview.selection():
            supplier_treeview.selection_remove(supplier_treeview.selection())

    def search_supplier_local():
        search_value = search_entry.get()
        if not search_value:
            messagebox.showerror('Error', 'Please enter an Invoice No. to search.', parent=supplier_frame)
            return

        cursor, conn = None, None
        try:
            cursor, conn = connect_database()
            if not cursor or not conn: return
            cursor.execute('USE inventory_systems')
            cursor.execute('SELECT * FROM supplier_data WHERE invoice=%s', (search_value,))
            records = cursor.fetchall() # Fetch all matching, though invoice should be unique

            supplier_treeview.delete(*supplier_treeview.get_children())
            if not records:
                messagebox.showinfo('Not Found', 'No supplier found with that Invoice No.', parent=supplier_frame)
            else:
                for record in records:
                    supplier_treeview.insert('', END, values=record)

        except pymysql.Error as e:
            messagebox.showerror('Database Error', f'Failed to search supplier: {e}', parent=supplier_frame)
        except Exception as e:
             messagebox.showerror('Error', f'An unexpected error occurred: {e}', parent=supplier_frame)
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def show_all_local():
        supplier_treeview_data(supplier_treeview)
        search_entry.delete(0, END)
        clear_supplier(True)


    # --- Supplier Form Layout ---
    supplier_frame = Frame(parent_frame, bg='white')
    supplier_frame.pack(fill=BOTH, expand=True)

    heading_label = Label(supplier_frame, text='Manage Supplier Details', font=('times new roman', 16, 'bold'), bg='#0F4D7D', fg='white')
    heading_label.place(x=0, y=0, relwidth=1, height=30)

    # Back Button
    try:
        back_icon_supp = PhotoImage(file='../assets/back.png')
        back_button = Button(supplier_frame, image=back_icon_supp, bd=0, cursor='hand2', bg='white', command=back_callback)
        back_button.image = back_icon_supp
        back_button.place(x=5, y=2)
    except TclError:
        back_button = Button(supplier_frame, text="< Back", bd=1, cursor='hand2', command=back_callback)
        back_button.place(x=5, y=2)

    # Left Frame for Entry Fields
    left_frame = Frame(supplier_frame, bg='white', bd=1, relief=SOLID)
    left_frame.place(x=10, y=40, width=480, height=510) # Adjusted size/pos

    Label(left_frame, text='Supplier Information', font=('times new roman', 14, 'bold'), bg='lightgrey', fg='black').pack(fill=X, pady=(0, 10))

    # Use grid within left_frame for better alignment
    entry_frame = Frame(left_frame, bg='white')
    entry_frame.pack(pady=10, padx=10)

    # Add New Invoice
    invoice_label_add = Label(entry_frame, text='Invoice No (Add)', font=('times new roman', 12), bg='white')
    invoice_label_add.grid(row=0, column=0, padx=5, pady=10, sticky='w')
    invoice_entry_add = Entry(entry_frame, font=('times new roman', 12), bg='lightyellow', width=25)
    invoice_entry_add.grid(row=0, column=1, padx=5, pady=10)

    # Display Selected Invoice
    invoice_label = Label(entry_frame, text='Selected Invoice', font=('times new roman', 12), bg='white')
    invoice_label.grid(row=1, column=0, padx=5, pady=10, sticky='w')
    invoice_entry = Entry(entry_frame, font=('times new roman', 12), bg='lightgrey', width=25, state=DISABLED)
    invoice_entry.grid(row=1, column=1, padx=5, pady=10)

    name_label = Label(entry_frame, text='Supplier Name', font=('times new roman', 12), bg='white')
    name_label.grid(row=2, column=0, padx=5, pady=10, sticky='w')
    name_entry = Entry(entry_frame, font=('times new roman', 12), bg='lightyellow', width=25)
    name_entry.grid(row=2, column=1, padx=5, pady=10)

    contact_label = Label(entry_frame, text='Contact', font=('times new roman', 12), bg='white')
    contact_label.grid(row=3, column=0, padx=5, pady=10, sticky='w')
    contact_entry = Entry(entry_frame, font=('times new roman', 12), bg='lightyellow', width=25)
    contact_entry.grid(row=3, column=1, padx=5, pady=10)

    description_label = Label(entry_frame, text='Description', font=('times new roman', 12), bg='white')
    description_label.grid(row=4, column=0, padx=5, pady=10, sticky='nw')
    desc_frame = Frame(entry_frame, bd=1, relief=SOLID) # Frame for text widget border
    desc_frame.grid(row=4, column=1, padx=5, pady=10, sticky='we')
    description_text = Text(desc_frame, font=('times new roman', 12), bg='lightyellow', height=5, width=25, bd=0)
    description_text.pack()

    # Button Frame
    button_frame = Frame(left_frame, bg='white')
    button_frame.pack(pady=20)

    btn_font_s = ('times new roman', 12, 'bold')
    btn_width_s = 8

    add_button = Button(button_frame, text='Add', font=btn_font_s, width=btn_width_s, cursor='hand2', fg='white', bg='#0F4D7D', command=add_supplier_local)
    add_button.grid(row=0, column=0, padx=10)
    update_button = Button(button_frame, text='Update', font=btn_font_s, width=btn_width_s, cursor='hand2', fg='white', bg='#0F4D7D', command=update_supplier_local)
    update_button.grid(row=0, column=1, padx=10)
    delete_button = Button(button_frame, text='Delete', font=btn_font_s, width=btn_width_s, cursor='hand2', fg='white', bg='#DC3545', command=delete_supplier_local)
    delete_button.grid(row=0, column=2, padx=10)
    clear_button = Button(button_frame, text='Clear', font=btn_font_s, width=btn_width_s, cursor='hand2', fg='white', bg='#6C757D', command=lambda: clear_supplier(True))
    clear_button.grid(row=0, column=3, padx=10)

    # Right Frame for Search and Treeview
    right_frame = Frame(supplier_frame, bg='white', bd=1, relief=SOLID)
    right_frame.place(x=500, y=40, width=560, height=510) # Adjusted size/pos

    search_frame = Frame(right_frame, bg='white')
    search_frame.pack(pady=10)

    num_label = Label(search_frame, text='Search Invoice No:', font=('times new roman', 12, 'bold'), bg='white')
    num_label.grid(row=0, column=0, padx=5, sticky='w')
    search_entry = Entry(search_frame, font=('times new roman', 12), bg='lightyellow', width=15)
    search_entry.grid(row=0, column=1, padx=5)
    search_button = Button(search_frame, text='Search', font=btn_font_s, width=btn_width_s, cursor='hand2', fg='white', bg='#0F4D7D', command=search_supplier_local)
    search_button.grid(row=0, column=2, padx=5)
    show_button = Button(search_frame, text='Show All', font=btn_font_s, width=btn_width_s, cursor='hand2', fg='white', bg='#0F4D7D', command=show_all_local)
    show_button.grid(row=0, column=3, padx=5)

    # Treeview Frame
    tree_view_frame = Frame(right_frame)
    tree_view_frame.pack(fill=BOTH, expand=True, padx=10, pady=(0, 10))

    scrolly = Scrollbar(tree_view_frame, orient=VERTICAL)
    scrollx = Scrollbar(tree_view_frame, orient=HORIZONTAL)
    supplier_treeview = ttk.Treeview(tree_view_frame, columns=('invoice', 'name', 'contact', 'description'), show='headings',
                                     yscrollcommand=scrolly.set, xscrollcommand=scrollx.set, height=18) # Adjusted height
    scrolly.pack(side=RIGHT, fill=Y)
    scrollx.pack(side=BOTTOM, fill=X)
    scrolly.config(command=supplier_treeview.yview)
    scrollx.config(command=supplier_treeview.xview)
    supplier_treeview.pack(fill=BOTH, expand=1)

    supplier_treeview.heading('invoice', text='Invoice No.')
    supplier_treeview.heading('name', text='Supplier Name')
    supplier_treeview.heading('contact', text='Contact')
    supplier_treeview.heading('description', text='Description')

    supplier_treeview.column('invoice', width=80, anchor=W)
    supplier_treeview.column('name', width=150, anchor=W)
    supplier_treeview.column('contact', width=100, anchor=W)
    supplier_treeview.column('description', width=200, anchor=W)

    # Initial data load and binding
    supplier_treeview_data(supplier_treeview)
    supplier_treeview.bind('<ButtonRelease-1>', select_data)

    return supplier_frame

# ############################################################################
# #                    CATEGORY FORM FUNCTIONALITY                           #
# ############################################################################

def category_form(parent_frame, back_callback):
    """Creates and places the Category Management form."""

    # --- Local Helper Functions for Category Form ---
    def category_treeview_data(treeview):
        cursor, conn = None, None
        try:
            cursor, conn = connect_database()
            if not cursor or not conn: return
            cursor.execute('USE inventory_systems')
            cursor.execute('SELECT * FROM category_data')
            records = cursor.fetchall()
            treeview.delete(*treeview.get_children())
            for record in records:
                treeview.insert('', END, values=record)
        except pymysql.Error as e:
            messagebox.showerror('DB Error', f'Failed to fetch category data: {e}', parent=category_frame)
        except Exception as e:
             messagebox.showerror('Error', f'An unexpected error occurred: {e}', parent=category_frame)
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def select_data(event): # Widgets from outer scope
        index = category_treeview.selection()
        if not index: return
        content = category_treeview.item(index)
        actual_content = content['values']
        clear_category(False) # Don't clear selection
        try:
            id_entry.config(state=NORMAL)
            id_entry.delete(0, END); id_entry.insert(0, actual_content[0])
            id_entry.config(state=DISABLED)
            category_name_entry.delete(0, END); category_name_entry.insert(0, actual_content[1])
            description_text.delete(1.0, END); description_text.insert(1.0, actual_content[2])
        except IndexError:
             messagebox.showerror("Error", "Selected row data is incomplete.", parent=category_frame)
        except Exception as e:
             messagebox.showerror("Error", f"Failed to load data: {e}", parent=category_frame)


    def add_category_local():
        cat_id = id_entry_add.get() # Use add-specific field
        name = category_name_entry.get()
        description = description_text.get(1.0, END).strip()

        if not cat_id or not name or not description:
            messagebox.showerror('Error', 'All fields are required', parent=category_frame)
            return

        cursor, conn = None, None
        try:
            cursor, conn = connect_database()
            if not cursor or not conn: return
            cursor.execute('USE inventory_systems')
            # Table creation in connect_database

            cursor.execute('SELECT id FROM category_data WHERE id=%s', (cat_id,))
            if cursor.fetchone():
                messagebox.showerror('Error', 'Category ID already exists', parent=category_frame)
                return

            cursor.execute('INSERT INTO category_data VALUES (%s, %s, %s)', (cat_id, name, description))
            conn.commit()
            category_treeview_data(category_treeview)
            messagebox.showinfo('Success', 'Category added successfully', parent=category_frame)
            clear_category(True)

        except pymysql.Error as e:
            messagebox.showerror('Database Error', f'Failed to add category: {e}', parent=category_frame)
            if conn: conn.rollback()
        except Exception as e:
             messagebox.showerror('Error', f'An unexpected error occurred: {e}', parent=category_frame)
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    # Update category (Optional - was missing in original, adding basic structure)
    def update_category_local():
         selected = category_treeview.selection()
         if not selected:
             messagebox.showerror('Error', 'Please select a category to update.', parent=category_frame)
             return
         cat_id = id_entry.get() # Get from disabled field
         name = category_name_entry.get()
         description = description_text.get(1.0, END).strip()

         if not cat_id or not name or not description:
             messagebox.showerror('Error', 'All fields are required for update.', parent=category_frame)
             return

         cursor, conn = None, None
         try:
             cursor, conn = connect_database()
             if not cursor or not conn: return
             cursor.execute('USE inventory_systems')
             cursor.execute('UPDATE category_data SET name=%s, description=%s WHERE id=%s',
                            (name, description, cat_id))
             if cursor.rowcount == 0:
                 messagebox.showinfo('Info', 'No changes detected or category not found.', parent=category_frame)
             else:
                 conn.commit()
                 category_treeview_data(category_treeview)
                 messagebox.showinfo('Success', 'Category updated successfully', parent=category_frame)
                 clear_category(True)
         except pymysql.Error as e:
            messagebox.showerror('Database Error', f'Failed to update category: {e}', parent=category_frame)
            if conn: conn.rollback()
         except Exception as e:
             messagebox.showerror('Error', f'An unexpected error occurred: {e}', parent=category_frame)
         finally:
            if cursor: cursor.close()
            if conn: conn.close()


    def delete_category_local():
        selected = category_treeview.selection()
        if not selected:
            messagebox.showerror('Error', 'Please select a category to delete.', parent=category_frame)
            return
        cat_id = id_entry.get() # Get from disabled field
        if not cat_id:
             messagebox.showerror('Error', 'Cannot identify selected category ID.', parent=category_frame)
             return

        if messagebox.askyesno('Confirm Delete', f'Are you sure you want to delete category ID {cat_id}?', parent=category_frame):
            cursor, conn = None, None
            try:
                cursor, conn = connect_database()
                if not cursor or not conn: return
                cursor.execute('USE inventory_systems')
                cursor.execute('DELETE FROM category_data WHERE id=%s', (cat_id,))
                if cursor.rowcount > 0:
                    conn.commit()
                    category_treeview_data(category_treeview)
                    messagebox.showinfo('Success', f'Category {cat_id} deleted successfully.', parent=category_frame)
                    clear_category(True)
                else:
                    messagebox.showwarning('Not Found', f'Category ID {cat_id} not found.', parent=category_frame)

            except pymysql.Error as e:
                 # Check for foreign key constraints (e.g., if linked to products)
                if e.args[0] == 1451:
                     messagebox.showerror('Deletion Failed', f'Cannot delete category {cat_id}.\nIt is likely linked to existing products.', parent=category_frame)
                else:
                    messagebox.showerror('Database Error', f'Failed to delete category: {e}', parent=category_frame)
                if conn: conn.rollback()
            except Exception as e:
                 messagebox.showerror('Error', f'An unexpected error occurred: {e}', parent=category_frame)
            finally:
                if cursor: cursor.close()
                if conn: conn.close()

    def clear_category(clear_selection=True):
        id_entry_add.delete(0, END)
        id_entry.config(state=NORMAL); id_entry.delete(0, END); id_entry.config(state=DISABLED)
        category_name_entry.delete(0, END)
        description_text.delete(1.0, END)
        if clear_selection and category_treeview.selection():
            category_treeview.selection_remove(category_treeview.selection())

    # --- Category Form Layout ---
    category_frame = Frame(parent_frame, bg='white')
    category_frame.pack(fill=BOTH, expand=True)

    heading_label = Label(category_frame, text='Manage Category Details', font=('times new roman', 16, 'bold'), bg='#0F4D7D', fg='white')
    heading_label.place(x=0, y=0, relwidth=1, height=30)

    # Back Button
    try:
        back_icon_cat = PhotoImage(file='../assets/back.png')
        back_button = Button(category_frame, image=back_icon_cat, bd=0, cursor='hand2', bg='white', command=back_callback)
        back_button.image = back_icon_cat
        back_button.place(x=5, y=2)
    except TclError:
        back_button = Button(category_frame, text="< Back", bd=1, cursor='hand2', command=back_callback)
        back_button.place(x=5, y=2)

    # Use PanedWindow for resizable sections
    paned_window = PanedWindow(category_frame, orient=HORIZONTAL, sashrelief=RAISED, bg='white')
    paned_window.place(x=10, y=40, relwidth=1, width=-20, relheight=1, height=-50) # Fill area below heading

    # Left Pane (Image and Details)
    left_pane = Frame(paned_window, bg='white', bd=1, relief=SOLID)
    paned_window.add(left_pane, width=400) # Initial width

    try:
        logo_cat = PhotoImage(file='../assets/product_category.png')
        label = Label(left_pane, image=logo_cat, bg='white')
        label.image = logo_cat
        label.pack(pady=20)
    except TclError:
        Label(left_pane, text="Category Icon", bg='white').pack(pady=20)

    details_frame = Frame(left_pane, bg='white')
    details_frame.pack(pady=10, padx=10)

    # Add ID Entry
    id_label_add = Label(details_frame, text='Category ID (Add)', font=('times new roman', 12), bg='white')
    id_label_add.grid(row=0, column=0, padx=5, pady=10, sticky='w')
    id_entry_add = Entry(details_frame, font=('times new roman', 12), bg='lightyellow', width=25)
    id_entry_add.grid(row=0, column=1, padx=5, pady=10)

    # Display ID Entry
    id_label = Label(details_frame, text='Selected ID', font=('times new roman', 12), bg='white')
    id_label.grid(row=1, column=0, padx=5, pady=10, sticky='w')
    id_entry = Entry(details_frame, font=('times new roman', 12), bg='lightgrey', width=25, state=DISABLED)
    id_entry.grid(row=1, column=1, padx=5, pady=10)

    category_name_label = Label(details_frame, text='Category Name', font=('times new roman', 12), bg='white')
    category_name_label.grid(row=2, column=0, padx=5, pady=10, sticky='w')
    category_name_entry = Entry(details_frame, font=('times new roman', 12), bg='lightyellow', width=25)
    category_name_entry.grid(row=2, column=1, padx=5, pady=10)

    description_label = Label(details_frame, text='Description', font=('times new roman', 12), bg='white')
    description_label.grid(row=3, column=0, padx=5, pady=10, sticky='nw')
    desc_frame_cat = Frame(details_frame, bd=1, relief=SOLID)
    desc_frame_cat.grid(row=3, column=1, padx=5, pady=10, sticky='we')
    description_text = Text(desc_frame_cat, font=('times new roman', 12), bg='lightyellow', height=5, width=25, bd=0)
    description_text.pack()

    # Button Frame
    button_frame = Frame(left_pane, bg='white')
    button_frame.pack(pady=15)

    btn_font_c = ('times new roman', 12, 'bold')
    btn_width_c = 8

    add_button = Button(button_frame, text='Add', font=btn_font_c, width=btn_width_c, cursor='hand2', fg='white', bg='#0F4D7D', command=add_category_local)
    add_button.grid(row=0, column=0, padx=10)
    update_button = Button(button_frame, text='Update', font=btn_font_c, width=btn_width_c, cursor='hand2', fg='white', bg='#0F4D7D', command=update_category_local) # Added update
    update_button.grid(row=0, column=1, padx=10)
    delete_button = Button(button_frame, text='Delete', font=btn_font_c, width=btn_width_c, cursor='hand2', fg='white', bg='#DC3545', command=delete_category_local)
    delete_button.grid(row=0, column=2, padx=10)
    clear_button = Button(button_frame, text='Clear', font=btn_font_c, width=btn_width_c, cursor='hand2', fg='white', bg='#6C757D', command=lambda: clear_category(True))
    clear_button.grid(row=0, column=3, padx=10)


    # Right Pane (Treeview)
    right_pane = Frame(paned_window, bg='white', bd=1, relief=SOLID)
    paned_window.add(right_pane) # Takes remaining space

    Label(right_pane, text='Category List', font=('times new roman', 14, 'bold'), bg='lightgrey', fg='black').pack(fill=X)

    treeview_frame = Frame(right_pane)
    treeview_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

    scrolly = Scrollbar(treeview_frame, orient=VERTICAL)
    scrollx = Scrollbar(treeview_frame, orient=HORIZONTAL)
    category_treeview = ttk.Treeview(treeview_frame, columns=('id', 'name', 'description'), show='headings',
                                     yscrollcommand=scrolly.set, xscrollcommand=scrollx.set, height=20) # Adjust height
    scrolly.pack(side=RIGHT, fill=Y)
    scrollx.pack(side=BOTTOM, fill=X)
    scrolly.config(command=category_treeview.yview)
    scrollx.config(command=category_treeview.xview)
    category_treeview.pack(fill=BOTH, expand=1)

    category_treeview.heading('id', text='ID')
    category_treeview.heading('name', text='Category Name')
    category_treeview.heading('description', text='Description')

    category_treeview.column('id', width=80, anchor=W)
    category_treeview.column('name', width=150, anchor=W)
    category_treeview.column('description', width=300, anchor=W)

    # Initial data load and binding
    category_treeview_data(category_treeview)
    category_treeview.bind('<ButtonRelease-1>', select_data)

    return category_frame


# ############################################################################
# #                     PRODUCT FORM FUNCTIONALITY                           #
# ############################################################################

def product_form(parent_frame, back_callback):
    """Creates and places the Product Management form."""

    # --- Local Helper Functions for Product Form ---
    def product_treeview_data(treeview):
        cursor, conn = None, None
        try:
            cursor, conn = connect_database()
            if not cursor or not conn: return
            cursor.execute('USE inventory_systems')
            # Ensure columns match the CREATE TABLE statement
            cursor.execute('SELECT id, category, supplier, name, price, discount, discounted_price, quantity, status FROM product_data')
            records = cursor.fetchall()
            treeview.delete(*treeview.get_children())
            for record in records:
                treeview.insert('', END, values=record)
        except pymysql.Error as e:
            messagebox.showerror('DB Error', f'Failed to fetch product data: {e}', parent=product_frame)
        except Exception as e:
             messagebox.showerror('Error', f'An unexpected error occurred: {e}', parent=product_frame)
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def fetch_supplier_category():
        category_option = ['Select']
        supplier_option = ['Select']
        cursor, conn = None, None
        try:
            cursor, conn = connect_database()
            if not cursor or not conn:
                 messagebox.showwarning("DB Warning", "Cannot fetch categories/suppliers.", parent=product_frame)
                 return

            cursor.execute('USE inventory_systems')
            # Fetch Categories
            try:
                cursor.execute('SELECT name FROM category_data ORDER BY name')
                cat_names = cursor.fetchall()
                if cat_names:
                    category_option.extend([name[0] for name in cat_names])
                else: category_option = ['(No Categories)'] # Placeholder
            except: category_option = ['(DB Error)'] # Error fetching

            # Fetch Suppliers
            try:
                cursor.execute('SELECT name FROM supplier_data ORDER BY name')
                sup_names = cursor.fetchall()
                if sup_names:
                    supplier_option.extend([name[0] for name in sup_names])
                else: supplier_option = ['(No Suppliers)']
            except: supplier_option = ['(DB Error)']

        except Exception as e:
            print(f"Error fetching categories/suppliers: {e}")
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

        category_combobox['values'] = category_option
        supplier_combobox['values'] = supplier_option
        if len(category_option) > 1 : category_combobox.set('Select')
        else: category_combobox.set(category_option[0]) # Set placeholder if none
        if len(supplier_option) > 1 : supplier_combobox.set('Select')
        else: supplier_combobox.set(supplier_option[0])

    # --- Corrected select_data function within product_form ---
    def select_data(event):  # Widgets from outer scope
        index = product_treeview.selection()
        if not index: return  # No selection

        # Clear fields *before* populating
        clear_product(False)  # False = Don't clear treeview selection

        content = product_treeview.item(index)
        row = content['values']
        # print(f"DEBUG: Selected row raw data: {row}") # Optional debug

        try:
            # Ensure row has enough elements before accessing indices
            if len(row) < 9:
                messagebox.showerror("Data Error", "Selected row has incomplete data.", parent=product_frame)
                product_frame.selected_product_id = None
                return

            # --- Populate fields with type conversion and error handling ---

            # Store ID (Index 0)
            product_frame.selected_product_id = row[0]

            # Category (Index 1) - String
            category_combobox.set(row[1] if row[1] is not None else 'Select')

            # Supplier (Index 2) - String
            supplier_combobox.set(row[2] if row[2] is not None else 'Select')

            # Name (Index 3) - String
            name_entry.insert(0, row[3] if row[3] is not None else "")

            # Price (Index 4) - *** Critical Fix Here ***
            try:
                # Convert to float first
                price_value = float(row[4])
                # Then format
                price_entry.insert(0, f"{price_value:.2f}")
            except (ValueError, TypeError, IndexError):
                # Handle cases where price is not a valid number (e.g., None, '', text)
                price_entry.insert(0,
                                   row[4] if row[4] is not None else "0.00")  # Insert original value or default "0.00"
                print(f"Warning: Could not format price '{row[4]}' as float.")  # Optional warning

            # Discount (Index 5) - Try converting to int
            try:
                discount_value = int(row[5])
                discount_spinbox.delete(0, END)
                discount_spinbox.insert(0, discount_value)
            except (ValueError, TypeError, IndexError):
                discount_spinbox.delete(0, END)
                discount_spinbox.insert(0, '0')  # Default to 0 on error
                print(f"Warning: Could not format discount '{row[5]}' as int, defaulting to 0.")

            # Discounted Price (Index 6) - Calculated, usually not loaded back into an entry

            # Quantity (Index 7) - Try converting to int
            try:
                quantity_value = int(row[7])
                quantity_entry.insert(0, quantity_value)
            except (ValueError, TypeError, IndexError):
                quantity_entry.insert(0, '0')  # Default to 0 on error
                print(f"Warning: Could not format quantity '{row[7]}' as int, defaulting to 0.")

            # Status (Index 8) - String
            status_combobox.set(row[8] if row[8] is not None else 'Select Status')

        except IndexError:
            # This handles cases where the 'row' tuple itself doesn't have enough items
            messagebox.showerror("Error", "Selected row data structure is incorrect.", parent=product_frame)
            product_frame.selected_product_id = None
            clear_product(True)  # Clear fields entirely on major error
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data into fields: {e}", parent=product_frame)
            product_frame.selected_product_id = None
            clear_product(True)  # Clear fields entirely on major error

    # --- End Corrected select_data ---

    def add_product_local():
        category = category_combobox.get()
        supplier = supplier_combobox.get()
        name = name_entry.get()
        price_str = price_entry.get()
        discount_str = discount_spinbox.get()
        quantity_str = quantity_entry.get()
        status = status_combobox.get()

        # Basic Validation
        if (category == 'Select' or category.startswith('(') or
            supplier == 'Select' or supplier.startswith('(') or
            not name or not price_str or not quantity_str or status == 'Select Status'):
            messagebox.showerror('Error', 'Please fill all required fields (Category, Supplier, Name, Price, Quantity, Status).', parent=product_frame)
            return

        try:
            price = float(price_str)
            discount = int(discount_str) if discount_str else 0
            quantity = int(quantity_str)
            if price < 0 or discount < 0 or quantity < 0:
                 raise ValueError("Price, Discount, and Quantity cannot be negative.")
            if not (0 <= discount <= 100):
                 raise ValueError("Discount must be between 0 and 100.")
        except ValueError as ve:
            messagebox.showerror('Invalid Input', f'{ve}', parent=product_frame)
            return

        cursor, conn = None, None
        try:
            cursor, conn = connect_database()
            if not cursor or not conn: return
            cursor.execute('USE inventory_systems')
            # Table creation in connect_database

            # Check if product (by name, category, supplier) already exists - adjust uniqueness criteria if needed
            cursor.execute('SELECT id FROM product_data WHERE category=%s AND supplier=%s AND name=%s',
                           (category, supplier, name))
            if cursor.fetchone():
                messagebox.showerror('Error', 'A product with the same name, category, and supplier already exists.', parent=product_frame)
                return

            # Calculate discounted price
            discounted_price = round(price * (1 - discount / 100.0), 2)

            cursor.execute(
                '''INSERT INTO product_data
                   (category, supplier, name, price, discount, discounted_price, quantity, status)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''',
                (category, supplier, name, price, discount, discounted_price, quantity, status))
            conn.commit()
            product_treeview_data(product_treeview)
            messagebox.showinfo('Success', 'Product added successfully.', parent=product_frame)
            clear_product(True)

        except pymysql.Error as e:
            messagebox.showerror('Database Error', f'Failed to add product: {e}', parent=product_frame)
            if conn: conn.rollback()
        except Exception as e:
             messagebox.showerror('Error', f'An unexpected error occurred: {e}', parent=product_frame)
        finally:
            if cursor: cursor.close()
            if conn: conn.close()


    def update_product_local():
        selected = product_treeview.selection()
        if not selected:
            messagebox.showerror('Error', 'Please select a product from the list to update.', parent=product_frame)
            return

        # Get the ID stored when the row was selected
        try:
            product_id = product_frame.selected_product_id
            if not product_id: raise AttributeError # Check if ID was stored
        except AttributeError:
             messagebox.showerror('Error', 'Cannot identify selected product ID. Please re-select the product.', parent=product_frame)
             return

        # Get current values from fields
        category = category_combobox.get()
        supplier = supplier_combobox.get()
        name = name_entry.get()
        price_str = price_entry.get()
        discount_str = discount_spinbox.get()
        quantity_str = quantity_entry.get()
        status = status_combobox.get()

        # Validation (similar to add)
        if (category == 'Select' or category.startswith('(') or
            supplier == 'Select' or supplier.startswith('(') or
            not name or not price_str or not quantity_str or status == 'Select Status'):
            messagebox.showerror('Error', 'Please fill all required fields for update.', parent=product_frame)
            return

        try:
            price = float(price_str)
            discount = int(discount_str) if discount_str else 0
            quantity = int(quantity_str)
            if price < 0 or discount < 0 or quantity < 0: raise ValueError("Values cannot be negative.")
            if not (0 <= discount <= 100): raise ValueError("Discount must be 0-100.")
        except ValueError as ve:
            messagebox.showerror('Invalid Input', f'{ve}', parent=product_frame)
            return

        cursor, conn = None, None
        try:
            cursor, conn = connect_database()
            if not cursor or not conn: return
            cursor.execute('USE inventory_systems')

            # Calculate new discounted price
            discounted_price = round(price * (1 - discount / 100.0), 2)

            # Optional: Compare with current DB values before updating

            cursor.execute(
                '''UPDATE product_data SET
                   category=%s, supplier=%s, name=%s, price=%s, discount=%s,
                   discounted_price=%s, quantity=%s, status=%s
                   WHERE id=%s''',
                (category, supplier, name, price, discount, discounted_price, quantity, status, product_id))

            if cursor.rowcount == 0:
                 messagebox.showinfo('Info', 'No changes detected or product not found.', parent=product_frame)
            else:
                 conn.commit()
                 product_treeview_data(product_treeview)
                 messagebox.showinfo('Success', 'Product updated successfully.', parent=product_frame)
                 clear_product(True)

        except pymysql.Error as e:
            messagebox.showerror('Database Error', f'Failed to update product: {e}', parent=product_frame)
            if conn: conn.rollback()
        except Exception as e:
             messagebox.showerror('Error', f'An unexpected error occurred: {e}', parent=product_frame)
        finally:
            if cursor: cursor.close()
            if conn: conn.close()


    def delete_product_local():
        selected = product_treeview.selection()
        if not selected:
            messagebox.showerror('Error', 'Please select a product to delete.', parent=product_frame)
            return

        try:
            product_id = product_frame.selected_product_id
            if not product_id: raise AttributeError
        except AttributeError:
             messagebox.showerror('Error', 'Cannot identify selected product ID. Please re-select the product.', parent=product_frame)
             return

        # Get product name for confirmation message
        name = name_entry.get() or f"ID {product_id}"

        if messagebox.askyesno('Confirm Delete', f'Are you sure you want to delete product "{name}"?', parent=product_frame):
            cursor, conn = None, None
            try:
                cursor, conn = connect_database()
                if not cursor or not conn: return
                cursor.execute('USE inventory_systems')
                cursor.execute('DELETE FROM product_data WHERE id=%s', (product_id,))

                if cursor.rowcount > 0:
                    conn.commit()
                    product_treeview_data(product_treeview)
                    messagebox.showinfo('Success', f'Product "{name}" deleted successfully.', parent=product_frame)
                    clear_product(True)
                    product_frame.selected_product_id = None # Clear stored ID
                else:
                    messagebox.showwarning('Not Found', f'Product ID {product_id} not found for deletion.', parent=product_frame)

            except pymysql.Error as e:
                messagebox.showerror('Database Error', f'Failed to delete product: {e}', parent=product_frame)
                if conn: conn.rollback()
            except Exception as e:
                 messagebox.showerror('Error', f'An unexpected error occurred: {e}', parent=product_frame)
            finally:
                if cursor: cursor.close()
                if conn: conn.close()

    def clear_product(clear_selection=True):
        # Clear entry fields, reset comboboxes/spinbox
        category_combobox.set('Select')
        supplier_combobox.set('Select')
        name_entry.delete(0, END)
        price_entry.delete(0, END)
        quantity_entry.delete(0, END)
        status_combobox.set('Select Status')
        discount_spinbox.delete(0, END)
        discount_spinbox.insert(0, '0') # Default discount to 0
        product_frame.selected_product_id = None # Clear stored ID

        if clear_selection and product_treeview.selection():
            product_treeview.selection_remove(product_treeview.selection())
        # Re-fetch dropdowns in case categories/suppliers were added/deleted
        fetch_supplier_category()


    def search_product_local():
        search_by = search_combobox.get()
        search_value = search_entry.get()

        if search_by == 'Search By':
            messagebox.showwarning('Warning', 'Please select a search criteria (Category, Supplier, Name, or Status).', parent=product_frame)
            return
        if not search_value:
            messagebox.showwarning('Warning', 'Please enter a value to search.', parent=product_frame)
            return

        # Map display names to DB column names
        column_map = {'Category': 'category', 'Supplier': 'supplier', 'Name': 'name', 'Status': 'status'}
        db_column = column_map.get(search_by)

        if not db_column:
             messagebox.showerror('Error', 'Invalid search option selected.', parent=product_frame)
             return

        cursor, conn = None, None
        try:
            cursor, conn = connect_database()
            if not cursor or not conn: return
            cursor.execute('USE inventory_systems')

            query = f'SELECT id, category, supplier, name, price, discount, discounted_price, quantity, status FROM product_data WHERE {db_column} LIKE %s'
            cursor.execute(query, (f'%{search_value}%',))
            records = cursor.fetchall()

            product_treeview.delete(*product_treeview.get_children())
            if not records:
                messagebox.showinfo('Not Found', 'No matching products found.', parent=product_frame)
            else:
                for record in records:
                    product_treeview.insert('', END, values=record)

        except pymysql.Error as e:
            messagebox.showerror('Database Error', f'Failed to search products: {e}', parent=product_frame)
        except Exception as e:
             messagebox.showerror('Error', f'An unexpected error occurred: {e}', parent=product_frame)
        finally:
            if cursor: cursor.close()
            if conn: conn.close()


    def show_all_local():
        product_treeview_data(product_treeview)
        search_combobox.set('Search By')
        search_entry.delete(0, END)
        clear_product(True)

    # --- Product Form Layout ---
    product_frame = Frame(parent_frame, bg='white')
    product_frame.pack(fill=BOTH, expand=True)
    product_frame.selected_product_id = None # Initialize storage for selected ID

    # Back Button
    try:
        back_icon_prod = PhotoImage(file='../assets/back.png')
        back_button = Button(product_frame, image=back_icon_prod, bd=0, cursor='hand2', bg='white', command=back_callback)
        back_button.image = back_icon_prod
        back_button.place(x=5, y=2)
    except TclError:
        back_button = Button(product_frame, text="< Back", bd=1, cursor='hand2', command=back_callback)
        back_button.place(x=5, y=2)

    # Left Frame for Entry Fields
    left_frame = Frame(product_frame, bg='white', bd=1, relief=SOLID)
    left_frame.place(x=10, y=10, width=420, height=545) # Adjusted size

    heading_label = Label(left_frame, text='Product Details', font=('times new roman', 15, 'bold'), bg='#0F4D7D', fg='white')
    heading_label.pack(fill=X)

    # Use grid within left_frame
    details_grid = Frame(left_frame, bg='white')
    details_grid.pack(pady=15, padx=10)

    row_num = 0
    pady_val = 8
    padx_val = 5
    sticky_val = 'w'
    entry_width = 22
    combo_width = 20
    lbl_font = ('times new roman', 12)
    entry_font = ('times new roman', 12)

    category_label = Label(details_grid, text='Category', font=lbl_font, bg='white')
    category_label.grid(row=row_num, column=0, padx=padx_val, pady=pady_val, sticky=sticky_val)
    category_combobox = ttk.Combobox(details_grid, font=entry_font, width=combo_width, state='readonly')
    category_combobox.grid(row=row_num, column=1, padx=padx_val, pady=pady_val)
    row_num += 1

    supplier_label = Label(details_grid, text='Supplier', font=lbl_font, bg='white')
    supplier_label.grid(row=row_num, column=0, padx=padx_val, pady=pady_val, sticky=sticky_val)
    supplier_combobox = ttk.Combobox(details_grid, font=entry_font, width=combo_width, state='readonly')
    supplier_combobox.grid(row=row_num, column=1, padx=padx_val, pady=pady_val)
    row_num += 1

    name_label = Label(details_grid, text='Product Name', font=lbl_font, bg='white')
    name_label.grid(row=row_num, column=0, padx=padx_val, pady=pady_val, sticky=sticky_val)
    name_entry = Entry(details_grid, font=entry_font, bg='lightyellow', width=entry_width)
    name_entry.grid(row=row_num, column=1, padx=padx_val, pady=pady_val)
    row_num += 1

    price_label = Label(details_grid, text='Price (₹)', font=lbl_font, bg='white')
    price_label.grid(row=row_num, column=0, padx=padx_val, pady=pady_val, sticky=sticky_val)
    price_entry = Entry(details_grid, font=entry_font, bg='lightyellow', width=entry_width)
    price_entry.grid(row=row_num, column=1, padx=padx_val, pady=pady_val)
    row_num += 1

    discount_label = Label(details_grid, text='Discount (%)', font=lbl_font, bg='white')
    discount_label.grid(row=row_num, column=0, padx=padx_val, pady=pady_val, sticky=sticky_val)
    discount_spinbox = Spinbox(details_grid, from_=0, to=100, font=entry_font, width=combo_width, justify=RIGHT)
    discount_spinbox.grid(row=row_num, column=1, padx=padx_val, pady=pady_val)
    row_num += 1

    quantity_label = Label(details_grid, text='Quantity', font=lbl_font, bg='white')
    quantity_label.grid(row=row_num, column=0, padx=padx_val, pady=pady_val, sticky=sticky_val)
    quantity_entry = Entry(details_grid, font=entry_font, bg='lightyellow', width=entry_width)
    quantity_entry.grid(row=row_num, column=1, padx=padx_val, pady=pady_val)
    row_num += 1

    status_label = Label(details_grid, text='Status', font=lbl_font, bg='white')
    status_label.grid(row=row_num, column=0, padx=padx_val, pady=pady_val, sticky=sticky_val)
    status_combobox = ttk.Combobox(details_grid, values=('Active', 'Inactive'), font=entry_font, width=combo_width, state='readonly')
    status_combobox.grid(row=row_num, column=1, padx=padx_val, pady=pady_val)
    status_combobox.set('Select Status')
    row_num += 1

    # Button Frame below details
    button_frame = Frame(left_frame, bg='white')
    button_frame.pack(pady=20)

    btn_font_p = ('times new roman', 12, 'bold')
    btn_width_p = 8

    add_button = Button(button_frame, text='Add', font=btn_font_p, width=btn_width_p, cursor='hand2', fg='white', bg='#0F4D7D', command=add_product_local)
    add_button.grid(row=0, column=0, padx=10)
    update_button = Button(button_frame, text='Update', font=btn_font_p, width=btn_width_p, cursor='hand2', fg='white', bg='#0F4D7D', command=update_product_local)
    update_button.grid(row=0, column=1, padx=10)
    delete_button = Button(button_frame, text='Delete', font=btn_font_p, width=btn_width_p, cursor='hand2', fg='white', bg='#DC3545', command=delete_product_local)
    delete_button.grid(row=0, column=2, padx=10)
    clear_button = Button(button_frame, text='Clear', font=btn_font_p, width=btn_width_p, cursor='hand2', fg='white', bg='#6C757D', command=lambda: clear_product(True))
    clear_button.grid(row=0, column=3, padx=10)


    # Right Frame for Search and Treeview
    right_frame = Frame(product_frame, bg='white', bd=1, relief=SOLID)
    right_frame.place(x=440, y=10, width=620, height=545) # Adjusted size/pos

    search_frame = LabelFrame(right_frame, text='Search Product', font=('times new roman', 12, 'bold'), bg='white', bd=1)
    search_frame.pack(pady=10, padx=10, fill=X)

    search_combobox = ttk.Combobox(search_frame, values=('Category', 'Supplier', 'Name', 'Status'), state='readonly', width=12, font=('times new roman', 11))
    search_combobox.grid(row=0, column=0, padx=5, pady=5)
    search_combobox.set('Search By')

    search_entry = Entry(search_frame, font=('times new roman', 11), bg='lightyellow', width=18)
    search_entry.grid(row=0, column=1, padx=5, pady=5)

    search_button = Button(search_frame, text='Search', font=('times new roman', 11, 'bold'), width=7, cursor='hand2', fg='white', bg='#0F4D7D', command=search_product_local)
    search_button.grid(row=0, column=2, padx=5, pady=5)

    show_button = Button(search_frame, text='Show All', font=('times new roman', 11, 'bold'), width=7, cursor='hand2', fg='white', bg='#0F4D7D', command=show_all_local)
    show_button.grid(row=0, column=3, padx=5, pady=5)

    # Treeview Frame
    treeview_frame = Frame(right_frame)
    treeview_frame.pack(pady=(0, 10), padx=10, fill=BOTH, expand=True)

    scrolly = Scrollbar(treeview_frame, orient=VERTICAL)
    scrollx = Scrollbar(treeview_frame, orient=HORIZONTAL)
    product_treeview = ttk.Treeview(treeview_frame, columns=(
                                'id', 'category', 'supplier', 'name', 'price', 'discount', 'discounted_price', 'quantity', 'status'),
                                show='headings', yscrollcommand=scrolly.set, xscrollcommand=scrollx.set, height=18) # Adjust height
    scrolly.pack(side=RIGHT, fill=Y)
    scrollx.pack(side=BOTTOM, fill=X)
    scrolly.config(command=product_treeview.yview)
    scrollx.config(command=product_treeview.xview)
    product_treeview.pack(fill=BOTH, expand=1)

    # Define headings and columns
    cols_prod = { 'id': ('ID', 40), 'category': ('Category', 100), 'supplier': ('Supplier', 100),
                  'name': ('Product Name', 120), 'price': ('Price', 70), 'discount': ('Disc%', 50),
                  'discounted_price': ('Disc Price', 80), 'quantity': ('Qty', 50), 'status': ('Status', 70) }
    for col_id, (text, width) in cols_prod.items():
        product_treeview.heading(col_id, text=text)
        product_treeview.column(col_id, width=width, anchor=W)


    # Initial data load and bindings
    fetch_supplier_category() # Populate dropdowns first
    product_treeview_data(product_treeview)
    product_treeview.bind('<ButtonRelease-1>', select_data)

    return product_frame

# ############################################################################
# #                       MAIN APPLICATION EXECUTION                         #
# ############################################################################

if __name__ == "__main__":
    root = Tk()
    # Start with login window size/position
    # ... (geometry setup as before) ...
    win_width = 600
    win_height = 450
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x_pos = (screen_width // 2) - (win_width // 2)
    y_pos = (screen_height // 2) - (win_height // 2) - 30
    root.geometry(f'{win_width}x{win_height}+{x_pos}+{y_pos}')
    root.minsize(win_width, win_height)

    # Initial DB check
    cursor, connection = connect_database()
    db_ok = bool(cursor and connection)
    if db_ok:
        cursor.close()
        connection.close()
        print("Database connection successful and tables checked/created.")
        login(root) # Start with login
        root.mainloop()
    else:
        print("Application cannot start due to database issues.")
        # Show error on the root window itself if DB fails early
        root.title("DB Connection Error")
        Label(root, text="Database Connection Failed!\nPlease ensure MySQL is running and\ncredentials in the script are correct.",
              fg="red", font=("Arial", 14)).pack(pady=50, padx=20)
        Button(root, text="Exit", command=root.quit).pack(pady=20)
        root.mainloop() # Keep window open to show error