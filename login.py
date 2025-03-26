from tkinter import *
from tkinter import messagebox
from employees import connect_database
from dashboard import dashboard  # Import dashboard function

def login(window):
    def authenticate():
        emp_id = emp_id_entry.get()
        password = password_entry.get()
        if emp_id == '' or password == '':
            messagebox.showerror('Error', 'All fields are required')
            return
        cursor, connection = connect_database()
        if not cursor or not connection:
            return
        try:
            cursor.execute('use inventory_systems')
            cursor.execute('SELECT * FROM employee WHERE emp_id=%s AND password=%s', (emp_id, password))
            user = cursor.fetchone()
            if user:
                messagebox.showinfo('Success', 'Login Successful')
                login_frame.destroy()  # Remove login frame
                dashboard(window)  # Open Dashboard
            else:
                messagebox.showerror('Error', 'Invalid Employee ID or Password')
        except Exception as e:
            messagebox.showerror('Error', f'Error due to {e}')
        finally:
            cursor.close()
            connection.close()

    def create_account():
        emp_id = emp_id_entry.get()
        password = password_entry.get()
        if emp_id == '' or password == '':
            messagebox.showerror('Error', 'All fields are required')
            return
        cursor, connection = connect_database()
        if not cursor or not connection:
            return
        try:
            cursor.execute('use inventory_systems')
            cursor.execute('CREATE TABLE IF NOT EXISTS employee (emp_id INT PRIMARY KEY, password VARCHAR(100))')
            cursor.execute('SELECT * FROM employee WHERE emp_id=%s', (emp_id,))
            if cursor.fetchone():
                messagebox.showerror('Error', 'Employee ID already exists')
                return
            cursor.execute('INSERT INTO employee VALUES (%s, %s)', (emp_id, password))
            connection.commit()
            messagebox.showinfo('Success', 'Account Created Successfully')
        except Exception as e:
            messagebox.showerror('Error', f'Error due to {e}')
        finally:
            cursor.close()
            connection.close()

    def on_close():
        """Immediately stops execution when the window is closed."""
        exit(0)  # Completely terminates the program

    login_frame = Frame(window, width=400, height=300, bg='white')
    login_frame.place(relx=0.5, rely=0.5, anchor=CENTER)

    Label(login_frame, text='Employee Login', font=('times new roman', 16, 'bold'), bg='white').pack(pady=10)
    Label(login_frame, text='Employee ID', font=('times new roman', 14), bg='white').pack()
    emp_id_entry = Entry(login_frame, font=('times new roman', 14), bg='lightgray')
    emp_id_entry.pack(pady=5)

    Label(login_frame, text='Password', font=('times new roman', 14), bg='white').pack()
    password_entry = Entry(login_frame, font=('times new roman', 14), bg='lightgray', show='*')
    password_entry.pack(pady=5)

    Button(login_frame, text='Login', font=('times new roman', 14), bg='#0F4D7D', fg='white',
           command=authenticate).pack(pady=10)
    Button(login_frame, text='Create New Account', font=('times new roman', 12), bg='white', fg='#0F4D7D',
           command=create_account).pack()

    # Override the close button to forcefully exit the program
    window.protocol("WM_DELETE_WINDOW", on_close)

    return login_frame
