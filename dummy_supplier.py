from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from employees import connect_database

def delete_supplier(invoice, treeview):
    index = treeview.selection()
    if not index:
        messagebox.showerror('Error', 'No row is selected')
        return

    cursor, connection = connect_database()
    if not cursor or not connection:
        return

    try:
        cursor.execute('DELETE FROM supplier_data WHERE invoice=%s', (invoice,))
        connection.commit()
        treeview_data(treeview)
        messagebox.showinfo('Info', 'Record is deleted')
    except Exception as e:
        messagebox.showerror('Error', f'Error due to {e}')
    finally:
        cursor.close()
        connection.close()

def clear_supplier(invoice_entry, name_entry, contact_entry, description_text, treeview):
    invoice_entry.delete(0, END)
    name_entry.delete(0, END)
    contact_entry.delete(0, END)
    description_text.delete(1.0, END)
    treeview.selection_remove(treeview.selection())

def search_supplier(search_value, treeview):
    if search_value == '':
        messagebox.showerror('Error', 'Please enter invoice number.')
        return

    cursor, connection = connect_database()
    if not cursor or not connection:
        return

    try:
        cursor.execute('SELECT * FROM supplier_data WHERE invoice=%s', (search_value,))
        record = cursor.fetchone()
        if not record:
            messagebox.showerror('Error', 'No record found')
            return
        treeview.delete(*treeview.get_children())
        treeview.insert('', END, values=record)
    except Exception as e:
        messagebox.showerror('Error', f'Error due to {e}')
    finally:
        cursor.close()
        connection.close()

def show_all(treeview, search_entry):
    treeview_data(treeview)
    search_entry.delete(0, END)

def update_supplier(invoice, name, contact, description, treeview):
    index = treeview.selection()
    if not index:
        messagebox.showerror('Error', 'No row is selected')
        return

    cursor, connection = connect_database()
    if not cursor or not connection:
        return

    try:
        cursor.execute('SELECT name, contact, description FROM supplier_data WHERE invoice=%s', (invoice,))
        current_data = cursor.fetchone()

        if not current_data:
            messagebox.showerror('Error', 'Invoice not found')
            return

        new_data = (name, contact, description)

        if current_data == new_data:
            messagebox.showinfo('Info', 'No changes detected')
            return

        cursor.execute('UPDATE supplier_data SET name=%s, contact=%s, description=%s WHERE invoice=%s',
                       (name, contact, description, invoice))
        connection.commit()
        treeview_data(treeview)
        messagebox.showinfo('Info', 'Data is updated')
    except Exception as e:
        messagebox.showerror('Error', f'Error due to {e}')
    finally:
        cursor.close()
        connection.close()

def select_data(event, invoice_entry, name_entry, contact_entry, description_text, treeview):
    try:
        index = treeview.selection()
        if not index:
            return
        content = treeview.item(index)
        actual_content = content['values']

        invoice_entry.delete(0, END)
        name_entry.delete(0, END)
        contact_entry.delete(0, END)
        description_text.delete(1.0, END)

        invoice_entry.insert(0, actual_content[0])
        name_entry.insert(0, actual_content[1])
        contact_entry.insert(0, actual_content[2])
        description_text.insert(1.0, actual_content[3])
    except IndexError:
        pass

def treeview_data(treeview):
    cursor, connection = connect_database()
    if not cursor or not connection:
        return

    try:
        cursor.execute('SELECT * FROM supplier_data')
        records = cursor.fetchall()
        treeview.delete(*treeview.get_children())
        for record in records:
            treeview.insert('', END, values=record)
    except Exception as e:
        messagebox.showerror('Error', f'Error due to {e}')
    finally:
        cursor.close()
        connection.close()

def add_supplier(invoice, name, contact, description, treeview):
    if invoice == '' or name == '' or contact == '' or description == '':
        messagebox.showerror('Error', 'All fields are required')
        return

    cursor, connection = connect_database()
    if not cursor or not connection:
        return

    try:
        cursor.execute('SELECT * FROM supplier_data WHERE invoice=%s', (invoice,))
        if cursor.fetchone():
            messagebox.showerror('Error', 'Invoice ID already exists')
            return

        cursor.execute('INSERT INTO supplier_data (invoice, name, contact, description) VALUES (%s, %s, %s, %s)',
                       (invoice, name, contact, description))
        connection.commit()
        treeview_data(treeview)
        messagebox.showinfo('Info', 'Data is inserted')
    except Exception as e:
        messagebox.showerror('Error', f'Error due to {e}')
    finally:
        cursor.close()
        connection.close()
