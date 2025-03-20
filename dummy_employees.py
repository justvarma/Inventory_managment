from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import DateEntry
import pymysql


def connect_database():
    try:
        connection = pymysql.connect(host='localhost', user='root', password='Adityavarma@123',
                                     database='inventory_systems')
        cursor = connection.cursor()
        return cursor, connection
    except Exception as e:
        messagebox.showerror('Error', f'Database connectivity issue: {e}')
        return None, None


def create_database_table():
    cursor, connection = connect_database()
    if not cursor or not connection:
        return
    try:
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS employee_data (
                empid INT PRIMARY KEY, 
                name VARCHAR(100), 
                email VARCHAR(100), 
                gender VARCHAR(50),
                dob VARCHAR(30), 
                contact VARCHAR(30), 
                employment_type VARCHAR(50), 
                education VARCHAR(30), 
                work_shift VARCHAR(50), 
                address VARCHAR(100),
                doj VARCHAR(30), 
                salary VARCHAR(50), 
                user_type VARCHAR(50), 
                password VARCHAR(50)
            )'''
        )
        connection.commit()
    except Exception as e:
        messagebox.showerror('Error', f'Error due to {e}')
    finally:
        cursor.close()
        connection.close()


def treeview_data():
    cursor, connection = connect_database()
    if not cursor or not connection:
        return
    try:
        cursor.execute('SELECT * FROM employee_data')
        employee_records = cursor.fetchall()
        employee_treeview.delete(*employee_treeview.get_children())
        for record in employee_records:
            employee_treeview.insert('', END, values=record)
    except Exception as e:
        messagebox.showerror('Error', f'Error due to {e}')
    finally:
        cursor.close()
        connection.close()


def select_data(event, empid_entry, name_entry, email_entry, gender_combobox, dob_date_entry, contact_entry,
                employment_type_combobox, education_combobox, work_shift_combobox, address_text, doj_date_entry,
                salary_entry, usertype_combobox, password_entry):
    try:
        index = employee_treeview.selection()
        if not index:
            return
        content = employee_treeview.item(index)
        row = content['values']

        clear_fields(empid_entry, name_entry, email_entry, gender_combobox, dob_date_entry, contact_entry,
                     employment_type_combobox, education_combobox, work_shift_combobox, address_text,
                     doj_date_entry, salary_entry, usertype_combobox, password_entry, False)

        empid_entry.insert(0, row[0])
        name_entry.insert(0, row[1])
        email_entry.insert(0, row[2])
        gender_combobox.set(row[3])
        dob_date_entry.set_date(row[4])
        contact_entry.insert(0, row[5])
        employment_type_combobox.set(row[6])
        education_combobox.set(row[7])
        work_shift_combobox.set(row[8])
        address_text.insert(1.0, row[9])
        doj_date_entry.set_date(row[10])
        salary_entry.insert(0, row[11])
        usertype_combobox.set(row[12])
        password_entry.insert(0, row[13])
    except IndexError:
        pass


def add_employee(empid, name, email, gender, dob, contact, employment_type, education, work_shift, address,
                 doj, salary, user_type, password):
    if not all([empid, name, email, gender, dob, contact, employment_type, education, work_shift, address.strip(), doj,
                salary, user_type, password]):
        messagebox.showerror('Error', 'All fields are required')
        return

    cursor, connection = connect_database()
    if not cursor or not connection:
        return
    try:
        cursor.execute('SELECT empid FROM employee_data WHERE empid=%s', (empid,))
        if cursor.fetchone():
            messagebox.showerror('Error', 'ID already exists')
            return

        cursor.execute('INSERT INTO employee_data VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                       (empid, name, email, gender, dob, contact, employment_type, education, work_shift,
                        address.strip(), doj, salary, user_type, password))
        connection.commit()
        treeview_data()
        messagebox.showinfo('Success', 'Data inserted successfully')
    except Exception as e:
        messagebox.showerror('Error', f'Error due to {e}')
    finally:
        cursor.close()
        connection.close()


def delete_employee(empid):
    selected = employee_treeview.selection()
    if not selected:
        messagebox.showerror('Error', 'No row is selected')
        return

    result = messagebox.askyesno('Confirm', 'Do you really want to delete the record?')
    if result:
        cursor, connection = connect_database()
        if not cursor or not connection:
            return
        try:
            cursor.execute('DELETE FROM employee_data WHERE empid=%s', (empid,))
            connection.commit()
            treeview_data()
            messagebox.showinfo('Success', 'Record deleted successfully')
        except Exception as e:
            messagebox.showerror('Error', f'Error due to {e}')
        finally:
            cursor.close()
            connection.close()


def search_employee(search_option, value):
    if search_option == 'Search By' or not value:
        messagebox.showerror('Error', 'Please select a valid option and enter a search value')
        return

    cursor, connection = connect_database()
    if not cursor or not connection:
        return
    try:
        cursor.execute(f'SELECT * FROM employee_data WHERE {search_option.lower()} LIKE %s', (f'%{value}%',))
        records = cursor.fetchall()
        if not records:
            messagebox.showerror('Error', 'No record found')
            return
        employee_treeview.delete(*employee_treeview.get_children())
        for record in records:
            employee_treeview.insert('', END, values=record)
    except Exception as e:
        messagebox.showerror('Error', f'Error due to {e}')
    finally:
        cursor.close()
        connection.close()


def clear_fields(empid_entry, name_entry, email_entry, gender_combobox, dob_date_entry, contact_entry,
                 employment_type_combobox, education_combobox, work_shift_combobox, address_text, doj_date_entry,
                 salary_entry, usertype_combobox, password_entry, clear_selection=True):
    empid_entry.delete(0, END)
    name_entry.delete(0, END)
    email_entry.delete(0, END)
    dob_date_entry.set_date('')
    gender_combobox.set('Select Gender')
    contact_entry.delete(0, END)
    employment_type_combobox.set('Select Type')
    education_combobox.set('Select Education')
    work_shift_combobox.set('Select Work Shift')
    address_text.delete(1.0, END)
    doj_date_entry.set_date('')
    salary_entry.delete(0, END)
    usertype_combobox.set('Select User Type')
    password_entry.delete(0, END)
    if clear_selection:
        employee_treeview.selection_remove(employee_treeview.selection())


def show_all(search_entry, search_combobox):
    treeview_data()
    search_entry.delete(0, END)
    search_combobox.set('Search By')
