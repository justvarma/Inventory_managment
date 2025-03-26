from logging import currentframe
from tkinter import *
from employees import employee_form
from supplier import supplier_form
from category import category_form
from products import product_form

current_frame = None


def show_form(form_function):
    global current_frame
    if current_frame:
        current_frame.place_forget()
    current_frame = form_function(window)


# GUI
window = Tk()

window.title('Dashboard')
window.geometry('1270x668+0+0')
window.resizable(0, 0)
window.config(bg='white')

bg_image = PhotoImage(file=r'assets\inventory.png')
titleLabel = Label(window, image=bg_image, compound=LEFT, text='   Inventory Management System',
                   font=('times new roman', 40, 'bold'), bg='#010c48', fg='white', anchor='w', padx=20)
titleLabel.place(x=0, y=0, relwidth=1)

logoutButton = Button(window, text='Logout', font=('times new roman', 20, 'bold'), fg='#010c48')
logoutButton.place(x=1100, y=10)

subtitleLabel = Label(window, text='Welcome Admin\t\t Date: 14-12-24\t\t Time: 16:36:15 pm',
                      font=('times new roman', 15), bg='#4d636d', fg='white')
subtitleLabel.place(x=0, y=70, relwidth=1)

leftFrame = Frame(window)
leftFrame.place(x=0, y=102, width=200, height=555)

logoImage = PhotoImage(file=r'assets\logo.png')
imageLabel = Label(leftFrame, image=logoImage)
imageLabel.pack()
# imageLabel.grid(row=0, column=0)

menuLabel = Label(leftFrame, text='Menu', font=('times new roman', 20), bg='#009688')
menuLabel.pack(fill=X)

employee_icon = PhotoImage(file=r'assets\employee.png')
employee_button = Button(leftFrame, image=employee_icon, compound=LEFT, text=' Employees',
                         font=('times new roman', 20, 'bold'), anchor='w', padx=10,
                         command=lambda: show_form(employee_form))
employee_button.pack(fill=X)

supplier_icon = PhotoImage(file=r'assets\supplier.png')
supplier_button = Button(leftFrame, image=supplier_icon, compound=LEFT, text=' Supplier',
                         font=('times new roman', 20, 'bold'), anchor='w', padx=10,
                         command=lambda: show_form(supplier_form))
supplier_button.pack(fill=X)

category_icon = PhotoImage(file=r'assets\category.png')
category_button = Button(leftFrame, image=category_icon, compound=LEFT, text=' Category',
                         font=('times new roman', 20, 'bold'), anchor='w', padx=10,
                         command=lambda: show_form(category_form))
category_button.pack(fill=X)

product_icon = PhotoImage(file=r'assets\product.png')
product_button = Button(leftFrame, image=product_icon, compound=LEFT, text=' Product',
                        font=('times new roman', 20, 'bold'), anchor='w', padx=10, command=lambda: show_form(product_form))
product_button.pack(fill=X)

sales_icon = PhotoImage(file=r'assets\sales.png')
sales_button = Button(leftFrame, image=sales_icon, compound=LEFT, text=' Sales', font=('times new roman', 20, 'bold'),
                      anchor='w', padx=10)
sales_button.pack(fill=X)

exit_icon = PhotoImage(file=r'assets\exit.png')
exit_button = Button(leftFrame, image=exit_icon, compound=LEFT, text=' Exit', font=('times new roman', 20, 'bold'),
                     anchor='w', padx=10)
exit_button.pack(fill=X)

emp_frame = Frame(window, bg='#2C3E50', bd=3, relief=RIDGE)
emp_frame.place(x=400, y=125, height=170, width=280)
total_emp_icon = PhotoImage(file=r'assets\total_emp.png')
total_emp_icon_label = Label(emp_frame, image=total_emp_icon, bg='#2C3E50')
total_emp_icon_label.pack(pady=10)

total_emp_label = Label(emp_frame, text='Total Employees', bg='#2C3E50', fg='white',
                        font=('times new roman', 15, 'bold'))
total_emp_label.pack()

total_emp_count_label = Label(emp_frame, text='0', bg='#2C3E50', fg='white', font=('times new roman', 30, 'bold'))
total_emp_count_label.pack()

sup_frame = Frame(window, bg='#8E44AD', bd=3, relief=RIDGE)
sup_frame.place(x=800, y=125, height=170, width=280)
total_sup_icon = PhotoImage(file=r'assets\total_sup.png')
total_sup_icon_label = Label(sup_frame, image=total_sup_icon, bg='#8E44AD')
total_sup_icon_label.pack(pady=10)

total_sup_label = Label(sup_frame, text='Total Suppliers', bg='#8E44AD', fg='white',
                        font=('times new roman', 15, 'bold'))
total_sup_label.pack()

total_sup_count_label = Label(sup_frame, text='0', bg='#8E44AD', fg='white', font=('times new roman', 30, 'bold'))
total_sup_count_label.pack()

cat_frame = Frame(window, bg='#27AE60', bd=3, relief=RIDGE)
cat_frame.place(x=400, y=310, height=170, width=280)
total_cat_icon = PhotoImage(file=r'assets\total_cat.png')
total_cat_icon_label = Label(cat_frame, image=total_cat_icon, bg='#27AE60')
total_cat_icon_label.pack(pady=10)

total_cat_label = Label(cat_frame, text='Total Categories', bg='#27AE60', fg='white',
                        font=('times new roman', 15, 'bold'))
total_cat_label.pack()

total_cat_count_label = Label(cat_frame, text='0', bg='#27AE60', fg='white', font=('times new roman', 30, 'bold'))
total_cat_count_label.pack()

prod_frame = Frame(window, bg='#2C3E50', bd=3, relief=RIDGE)
prod_frame.place(x=800, y=310, height=170, width=280)
total_prod_icon = PhotoImage(file=r'assets\total_prod.png')
total_prod_icon_label = Label(prod_frame, image=total_prod_icon, bg='#2C3E50')
total_prod_icon_label.pack(pady=10)

total_prod_label = Label(prod_frame, text='Total Products', bg='#2C3E50', fg='white',
                         font=('times new roman', 15, 'bold'))
total_prod_label.pack()

total_prod_count_label = Label(prod_frame, text='0', bg='#2C3E50', fg='white', font=('times new roman', 30, 'bold'))
total_prod_count_label.pack()

sales_frame = Frame(window, bg='#E74C3C', bd=3, relief=RIDGE)
sales_frame.place(x=600, y=495, height=170, width=280)
total_sales_icon = PhotoImage(file=r'assets\total_sales.png')
total_sales_icon_label = Label(sales_frame, image=total_sales_icon, bg='#E74C3C')
total_sales_icon_label.pack(pady=10)

total_sales_label = Label(sales_frame, text='Total Sales', bg='#E74C3C', fg='white',
                          font=('times new roman', 15, 'bold'))
total_sales_label.pack()

total_sales_count_label = Label(sales_frame, text='0', bg='#E74C3C', fg='white', font=('times new roman', 30, 'bold'))
total_sales_count_label.pack()

window.mainloop()
