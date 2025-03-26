# File: login.py
from tkinter import *
from tkinter import messagebox
from employees import connect_database
# REMOVE: from dashboard import dashboard  # <--- REMOVE THIS TOP-LEVEL IMPORT

def login(window):
    def authenticate():
        emp_id = emp_id_entry.get()
        password = password_entry.get()
        if emp_id == '' or password == '':
            messagebox.showerror('Error', 'All fields are required')
            return

        # Ensure database connection variables are initialized even if connection fails
        cursor = None
        connection = None
        try:
            cursor, connection = connect_database()
            if not cursor or not connection:
                # connect_database should ideally raise an exception or return specific error
                messagebox.showerror('Error', 'Failed to connect to the database.')
                return

            cursor.execute('use inventory_systems')
            cursor.execute('SELECT * FROM employee WHERE emp_id=%s AND password=%s', (emp_id, password))
            user = cursor.fetchone()
            if user:
                messagebox.showinfo('Success', 'Login Successful')
                login_frame.destroy()  # Remove login frame

                # --- IMPORT DASHBOARD LOCALLY ---
                try:
                    from dashboard import dashboard # Import here, only when needed
                    dashboard(window)  # Open Dashboard
                except ImportError:
                    messagebox.showerror('Error', 'Could not load the dashboard module.')
                    # Optionally, bring back login or exit?
                    # login(window) # Or maybe just exit? Or show a critical error.
                    window.quit() # Exit if dashboard can't load

            else:
                messagebox.showerror('Error', 'Invalid Employee ID or Password')
        except Exception as e:
            messagebox.showerror('Error', f'Database query failed: {e}') # More specific error
        finally:
            # Ensure cursor and connection are closed if they were opened
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def create_account():
        emp_id = emp_id_entry.get()
        password = password_entry.get()
        if emp_id == '' or password == '':
            messagebox.showerror('Error', 'All fields are required')
            return

        # Ensure database connection variables are initialized
        cursor = None
        connection = None
        try:
            cursor, connection = connect_database()
            if not cursor or not connection:
                messagebox.showerror('Error', 'Failed to connect to the database.')
                return

            cursor.execute('use inventory_systems')
            # Check and Create Table (Consider doing this once at app startup if possible)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS employee (
                    emp_id VARCHAR(50) PRIMARY KEY,
                    password VARCHAR(255) NOT NULL
                )''') # Use VARCHAR for emp_id if it can contain non-digits, adjust length
                     # Use longer VARCHAR for password, especially if hashing
            connection.commit() # Commit table creation if it happened

            # Check if employee ID exists
            cursor.execute('SELECT emp_id FROM employee WHERE emp_id=%s', (emp_id,))
            if cursor.fetchone():
                messagebox.showerror('Error', 'Employee ID already exists')
                return

            # Insert new employee (Consider Hashing Passwords!)
            # WARNING: Storing plain text passwords is a major security risk.
            # You should use a library like bcrypt to hash passwords.
            # Example (conceptual - requires bcrypt library: pip install bcrypt):
            # import bcrypt
            # hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            # cursor.execute('INSERT INTO employee (emp_id, password) VALUES (%s, %s)', (emp_id, hashed_password.decode('utf-8')))

            # Using plain text for now as per original code:
            cursor.execute('INSERT INTO employee (emp_id, password) VALUES (%s, %s)', (emp_id, password))
            connection.commit() # Commit the insert
            messagebox.showinfo('Success', 'Account Created Successfully')

        except Exception as e:
            messagebox.showerror('Error', f'Account creation failed: {e}')
            if connection: # Rollback on error if necessary (though auto-commit might be default)
                connection.rollback()
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def on_close():
        """Immediately stops execution when the window is closed."""
        print("Window closed by user.") # Optional: for debugging
        window.quit() # Gracefully stops the Tkinter main loop
        window.destroy() # Destroys the window
        exit(0)  # Forcefully terminates the Python script process

    # --- Login Frame Setup ---
    # Destroy previous frame if it exists (useful if login is called again after logout)
    for widget in window.winfo_children():
        widget.destroy()

    login_frame = Frame(window, width=400, height=300, bg='white')
    login_frame.place(relx=0.5, rely=0.5, anchor=CENTER)

    Label(login_frame, text='Employee Login', font=('times new roman', 16, 'bold'), bg='white').pack(pady=10)
    Label(login_frame, text='Employee ID', font=('times new roman', 14), bg='white').pack()
    emp_id_entry = Entry(login_frame, font=('times new roman', 14), bg='lightgray')
    emp_id_entry.pack(pady=5)
    emp_id_entry.focus_set() # Set focus to the ID field initially

    Label(login_frame, text='Password', font=('times new roman', 14), bg='white').pack()
    password_entry = Entry(login_frame, font=('times new roman', 14), bg='lightgray', show='*')
    password_entry.pack(pady=5)

    # Allow login on Enter key press in password field
    password_entry.bind('<Return>', lambda event=None: authenticate())
    emp_id_entry.bind('<Return>', lambda event=None: password_entry.focus_set()) # Move focus on Enter

    Button(login_frame, text='Login', font=('times new roman', 14), bg='#0F4D7D', fg='white', relief=GROOVE,
           command=authenticate).pack(pady=10, ipadx=10) # Add some padding
    Button(login_frame, text='Create New Account', font=('times new roman', 12), bg='white', fg='#0F4D7D', bd=0,
           activebackground='white', activeforeground='#0F4D7D', # Nicer button look
           command=create_account).pack()

    # Override the close button
    window.protocol("WM_DELETE_WINDOW", on_close)

    # No need to return login_frame if we handle cleanup within the function

# --- Main Execution Block ---
if __name__ == "__main__":
    root = Tk()
    root.title("Inventory Management - Login")
    # Get screen width and height to center the window
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    win_width = 600 # Adjust desired window width
    win_height = 400 # Adjust desired window height
    x_pos = (screen_width // 2) - (win_width // 2)
    y_pos = (screen_height // 2) - (win_height // 2)
    root.geometry(f'{win_width}x{win_height}+{x_pos}+{y_pos}')
    root.configure(bg='white') # Set a base background for the window

    login(root)  # Start with the login screen

    root.mainloop()