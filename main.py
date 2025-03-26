from tkinter import Tk
from login import login
from dashboard import open_dashboard

def main():
    root = Tk()
    root.geometry("600x400")
    root.title("Login")

    success = login(root)  # Show login first
    root.destroy()  # Close login window after successful login

    if success:  # If login is successful, open the dashboard
        open_dashboard()  # Call dashboard function in a new window

if __name__ == "__main__":
    main()
