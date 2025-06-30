from tkinter import *
from tkinter import ttk
from tkinter import messagebox

from unicodedata import category

from employee import connect_database, select_data
import pymysql

def customize_treeview():
    style = ttk.Style()
    style.theme_use('default')
    style.configure("Custom.Treeview")
    style.map('Custom.Treeview', background=[('selected', '#f7b2b7')])

def delete_category(treeview):
    selected = treeview.selection()
    content=treeview.item(selected)
    row=content['values']
    id=row[0]
    if not selected:
        messagebox.showerror('Error', "No row is selected")
    else:
        result = messagebox.askyesno('Confirm', 'Do you really want to delete the record?')
        if result:
            cursor, connection = connect_database()
            if not cursor or not connection:
                return
            try:
                cursor.execute('use inventory_system')
                cursor.execute('DELETE FROM category_data WHERE id=%s', id)
                connection.commit()
                treeview_data(treeview)
                messagebox.showinfo('Success', 'Record is Deleted Successfully')
            except Exception as e:
                messagebox.showerror('Error', f'Error due to {e}')
            try:
                con = pymysql.connect(host="localhost", user="root", password="1234", database="inventory_system")
                cur = con.cursor()
                cur.execute("INSERT INTO audit_log (user, action_type, module, description) VALUES (%s, %s, %s, %s)",
                            ("Admin", "Delete", "Category", f"Deleted category '{category_name_entry.get()}'"))
                con.commit()
                con.close()
            except Exception as e:
                messagebox.showerror('Error', f'Error due to{e}')
            finally:
                cursor.close()
                connection.close()


def clear(id_entry,category_name_entry,description_text):
    id_entry.delete(0,END)
    category_name_entry.delete(0,END)
    description_text.delete(1.0,END)

def treeview_data(treeview):
    cursor,connection=connect_database()
    if not cursor or not connection:
        return
    cursor.execute('use inventory_system')
    try:
        cursor.execute('SELECT * from category_data')
        records=cursor.fetchall()
        treeview.delete(*treeview.get_children())
        for record in records:
            treeview.insert('',END,values=record)
    except Exception as e:
        messagebox.showerror('Error', f'Error due to {e}')
    finally:
        cursor.close()
        connection.close()

def add_category(id,name,description,treeview):
    if id=='' or name=='' or description=='':
        messagebox.showerror('Error','ALl fields are required')
    else:
        cursor, connection = connect_database()
        if not cursor or not connection:
            return
        try:
            cursor.execute('Use inventory_system')
            cursor.execute(
                'CREATE TABLE IF NOT EXISTS category_data(id INT PRIMARY KEY,name VARCHAR(15),description TEXT)')
            cursor.execute('SELECT * from category_data where id=%s', id)
            if cursor.fetchone():
                messagebox.showerror('Error', "Id already exists")
                return
            cursor.execute('INSERT INTO category_data VALUES(%s,%s,%s)', (id, name,description))
            connection.commit()
            messagebox.showinfo('Info', 'Data is added successfully.')
            treeview_data(treeview)
        except Exception as e:
            messagebox.showerror('Error', f'Error due to {e}')
        try:
            con = pymysql.connect(host="localhost", user="root", password="1234", database="inventory_system")
            cur = con.cursor()
            cur.execute("INSERT INTO audit_log (user, action_type, module, description) VALUES (%s, %s, %s, %s)",
                    ("Admin", "Insert", "Category", f"Inserted Category '{category_name_entry.get()}'"))
            con.commit()
            con.close()
        except Exception as e:
            messagebox.showerror('Error', f'Error due to{e}')
        finally:
            cursor.close()
            connection.close()


def category_form(window):
    global back_image , logo , category_name_entry
    category_frame = Frame(window, width=1160, height=630,background='#FFE5B4')
    category_frame.place(x=200, y=100)
    heading_label = Label(category_frame, text='Manage Category Details', font=('Times new roman', 16, 'bold'),
                          bg='#2c3e50', fg='white')
    heading_label.place(x=0, y=0, relwidth=1)
    back_image = PhotoImage(file="../images/back.png")
    back_button = Button(category_frame, image=back_image, bd=0, cursor='hand2',
                         command=lambda: category_frame.place_forget())
    back_button.place(x=10, y=30)
    logo = PhotoImage(file="../images/product_categoryr.png")
    label=Label(category_frame,image=logo,background='#FFE5B4')
    label.place(x=30,y=100)

    details_frame=Frame(category_frame, bg='#ffe0a3')
    details_frame.place(x=500,y=60)

    id_label = Label(details_frame, text='Id', font=('Times new roman', 14, 'bold'), bg='white')
    id_label.grid(row=0, column=0, padx=20, sticky='w',pady=20)
    id_entry = Entry(details_frame, font=('Times new roman', 14, 'bold'), bg='lightyellow')
    id_entry.grid(row=0, column=1,pady=20)

    category_name_label = Label(details_frame, text='Category Name', font=('Times new roman', 14, 'bold'), bg='white')
    category_name_label.grid(row=1, column=0, padx=20, sticky='w')
    category_name_entry = Entry(details_frame, font=('Times new roman', 14, 'bold'), bg='lightyellow')
    category_name_entry.grid(row=1, column=1,pady=20, padx=20)

    description_label = Label(details_frame, text='Description', font=('Times new roman', 14, 'bold'), bg='white')
    description_label.grid(row=2, column=0, padx=20, sticky='nw')
    description_text = Text(details_frame, width=25, height=6, bd=2, bg='lightyellow')
    description_text.grid(row=2, column=1, padx=20)

    button_frame = Frame(category_frame,background='#ffe0a3')
    button_frame.place(x=500, y=295,width=422)

    add_button = Button(button_frame, text='Add', font=('times new roman', 14), width=8, cursor='hand2',
                        fg='white', bg='#0f4d7d',command=lambda :add_category(id_entry.get(),category_name_entry.get(),description_text.get(1.0,END).strip(),treeview))
    add_button.grid(row=0, column=0, padx=20)

    delete_button = Button(button_frame, text='Delete', font=('times new roman', 12), width=8, cursor='hand2',
                           fg='white', bg='#0f4d7d',command=lambda :delete_category(treeview))
    delete_button.grid(row=0, column=1, padx=20)

    clear_button = Button(button_frame, text='Clear', font=('times new roman', 12), width=8, cursor='hand2',
                           fg='white', bg='#0f4d7d',command=lambda:clear(id_entry,category_name_entry,description_text))
    clear_button.grid(row=0, column=2, padx=20)

    treeview_frame = Frame(category_frame, bg="yellow")
    treeview_frame.place(x=530, y=360,height=200,width=500)

    scrolly = Scrollbar(treeview_frame, orient=VERTICAL)
    scrollx = Scrollbar(treeview_frame, orient=HORIZONTAL)
    customize_treeview()
    treeview = ttk.Treeview(treeview_frame, columns=('id', 'name','description'),style="Custom.Treeview" ,show='headings',
                            yscrollcommand=scrolly.set, xscrollcommand=scrollx.set)
    scrolly.pack(side=RIGHT, fill=Y)
    scrollx.pack(side=BOTTOM, fill=X)
    scrollx.config(command=treeview.xview)
    scrolly.config(command=treeview.yview)
    treeview.pack(fill=BOTH, expand=1)

    treeview.heading('id',text='Id')
    treeview.heading('name', text='Category Name')
    treeview.heading('description', text='Description')

    treeview.column('id', width=80)
    treeview.column('name', width=140)
    treeview.column('description', width=300)
    treeview_data(treeview)
    return category_frame




