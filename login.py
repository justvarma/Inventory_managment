from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
import pymysql
import itertools

# Carousel Images (Add Your Image Paths Here)
image_paths = [
    r"assets/login_logo1.png",
    r"assets/login_logo2.png",
    r"assets/login_logo3.png",
    r"assets/login_logo4.png",
    r"assets/login_logo5.png"
]



class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Login")
        self.root.geometry("1000x600")
        self.root.configure(bg="white")

        self.top_bar = Frame(self.root, bg="#4A90E2", height=80)  # Increased height
        self.top_bar.pack(fill=X, pady=10)
        self.title_label = Label(self.top_bar, text="Inventory Management System",
                                 font=("Times New Roman", 33, "bold"), bg="#4A90E2", fg="white")
        self.title_label.pack(pady=20)

        # Carousel Frame
        self.carousel_frame = Frame(self.root, width=500, height=500, bg="white")
        self.carousel_frame.pack(side=LEFT, fill=BOTH, expand=TRUE)

        # Login Frame
        self.login_frame = Frame(self.root, width=420, height=480, bg="#D3D3D3")  # Adjusted background color
        self.login_frame.pack(side=RIGHT, padx=30, pady=40)

        # User Icon
        self.user_icon = Image.open(r'assets/login.png')  # Ensure this image exists
        self.user_icon = self.user_icon.resize((120, 120))
        self.user_icon = ImageTk.PhotoImage(self.user_icon)

        self.icon_label = Label(self.login_frame, image=self.user_icon, bg="#D3D3D3")
        self.icon_label.pack(pady=15)

        # Employee ID Entry
        Label(self.login_frame, text="Employee Id", font=("Times New Roman", 14, "bold"), bg="#D3D3D3").pack()
        self.emp_id_entry = Entry(self.login_frame, font=("Times New Roman", 13), width=30)
        self.emp_id_entry.pack(pady=5)

        # Password Entry
        Label(self.login_frame, text="Password", font=("Times New Roman", 14, "bold"), bg="#D3D3D3").pack()
        self.password_entry = Entry(self.login_frame, font=("Times New Roman", 13), width=30, show="*")
        self.password_entry.pack(pady=5)

        # Toggle Password Visibility
        self.show_password = False
        self.toggle_button = Button(self.login_frame, text="👁", command=self.toggle_password, bg="#D3D3D3",
                                    borderwidth=0)
        self.toggle_button.pack(pady=5)

        # Forgot Password
        self.forgot_password_label = Label(self.login_frame, text="Forgot Password?", fg="blue", bg="#D3D3D3",
                                           cursor="hand2")
        self.forgot_password_label.pack()

        # Login Button
        self.login_button = Button(self.login_frame, text="Login", font=("Times New Roman", 14, "bold"),
                                   bg="#4A90E2", fg="white", width=10, command=self.authenticate)
        self.login_button.pack(pady=20)

        # Start Image Carousel
        self.image_label = Label(self.carousel_frame, bg="white")
        self.image_label.pack(expand=TRUE)
        self.images = [ImageTk.PhotoImage(Image.open(img).resize((500, 500))) for img in image_paths]
        self.image_cycle = itertools.cycle(self.images)
        self.update_carousel()

    def toggle_password(self):
        if self.show_password:
            self.password_entry.config(show="*")
        else:
            self.password_entry.config(show="")
        self.show_password = not self.show_password

    def update_carousel(self):
        if self.root and self.root.winfo_exists():
            self.image_label.config(image=next(self.image_cycle))
            self.root.after_id = self.root.after(5000, self.update_carousel)  # Store after() ID

    def authenticate(self):
        emp_id = self.emp_id_entry.get()
        password = self.password_entry.get()

        if not emp_id or not password:
            messagebox.showerror("Error", "All fields are required", parent=self.root)
            return

        # 🔹 Initialize variables before `try` block
        cursor = None
        connection = None

        try:
            connection = pymysql.connect(host="localhost", user="root", password="Adityavarma@123", database="inventory_systems")
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM employee_data WHERE empid=%s AND password=%s", (emp_id, password))
            user = cursor.fetchone()

            if user:
                messagebox.showinfo("Success", "Login Successful", parent=self.root)
                self.root.destroy()  # Close login window
                self.open_dashboard()
            else:
                messagebox.showerror("Error", "Invalid Employee ID or Password", parent=self.root)

        except pymysql.Error as e:
            messagebox.showerror("Database Error", f"Error: {e}", parent=self.root)

        finally:
            # 🔹 Only close if cursor and connection exist
            if cursor is not None:
                cursor.close()
            if connection is not None:
                connection.close()

    def open_dashboard(self):
        from dashboard import DashboardApp  # Import dashboard class

        # Check if root exists before withdrawing or destroying
        if self.root and self.root.winfo_exists():
            self.root.after_cancel(self.root.after_id)  # Cancel carousel update
            self.root.withdraw()  # Hide login window

        # Open dashboard in a new window
        dashboard_root = Tk()
        app = DashboardApp(dashboard_root)
        dashboard_root.mainloop()

        # Restore login window only if it still exists
        if self.root and self.root.winfo_exists():
            self.root.deiconify()


if __name__ == "__main__":
    root = Tk()
    app = LoginApp(root)
    root.mainloop()