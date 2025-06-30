from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from files.employee import connect_database, select_data
import re
import pymysql

def customize_treeview():
    style = ttk.Style()
    style.theme_use('default')
    style.configure("Custom.Treeview")
    style.map('Custom.Treeview', background=[('selected', '#f7b2b7')])

def validate_phone_number(phone_number: str) -> bool:
    pattern = r"^[6-9]\d{9}$"
    if re.match(pattern, phone_number):
        return True
    return False
def search_supplier(invoice,treeview):
    if invoice=='':
        messagebox.showerror('ERROR','Please enter invoice no.')
    else:
        cursor, connection = connect_database()
        if not cursor or not connection:
            return
        try:
            cursor.execute('Use inventory_system')
            cursor.execute('SELECT * from supplier_data WHERE invoice=%s',invoice)
            record=cursor.fetchone()
            if not record:
                messagebox.showerror('ERROR','No Record Found.')
                return
            treeview.delete(*treeview.get_children())
            treeview.insert('',END,value=record)
        except Exception as e:
            messagebox.showerror('Error', f'Error due to {e}')
        finally:
            cursor.close()
            connection.close()

def show_all(treeview,num_entry):
    treeview_data(treeview)
    num_entry.delete(0,END)



def delete_supplier(invoice,treeview):
    selected = treeview.selection()
    if not selected:
        messagebox.showerror('Error', "No row is selected")
    else:
        result=messagebox.askyesno('Confirm','Do you really want to delete the record?')
        if result:
            cursor, connection = connect_database()
            if not cursor or not connection:
                return
            try:
                cursor.execute('use inventory_system')
                cursor.execute('DELETE FROM supplier_data WHERE invoice=%s',invoice)
                connection.commit()
                treeview_data(treeview)
                messagebox.showinfo('Success','Record is Deleted Successfully')
            except Exception as e:
                messagebox.showerror('Error', f'Error due to {e}')
            try:
                con = pymysql.connect(host="localhost", user="root", password="1234", database="inventory_system")
                cur = con.cursor()
                cur.execute("INSERT INTO audit_log (user, action_type, module, description) VALUES (%s, %s, %s, %s)",
                            ("Admin", "Delete", "Supplier", f"Updated Succesfully '{name_entry.get()}'"))
                con.commit()
                con.close()
            except Exception as e:
                messagebox.showerror('Error', f'Error due to {e}')

            finally:
                cursor.close()
                connection.close()
def clear(invoice_entry,name_entry,contact_entry,description_text,treeview):
    invoice_entry.delete(0,END)
    name_entry.delete(0,END)
    contact_entry.delete(0,END)
    description_text.delete(1.0,END)
    treeview.selection_remove(treeview.selection())

def update_supplier(invoice,name,contact,description,treeview):
    index = treeview.selection()
    if not index:
        messagebox.showerror('ERROR',"No Row is Selected")
        return
    elif not validate_phone_number(contact):
        messagebox.showerror("Invalid Phone Number", "Please enter a valid 10-digit phone number.")
    else:
        cursor, connection = connect_database()
        if not cursor or not connection:
            return
        try:
            cursor.execute('use inventory_system')
            cursor.execute('SELECT * from supplier_data WHERE invoice=%s',invoice)
            current_data=cursor.fetchone()
            current_data = current_data[1:]
            new_data = (name,contact,description)
            if current_data==new_data:
                messagebox.showinfo('Information',"No changes detected")
                return
            else:
                cursor.execute('use inventory_system')
                cursor.execute('UPDATE supplier_data SET name=%s,contact=%s,description=%s WHERE invoice=%s',(name,contact,description,invoice))
                connection.commit()
                treeview_data(treeview)
                messagebox.showinfo('INFO','Data is updated')
        except Exception as e:
            messagebox.showerror('Error', f'Error due to {e}')
        try:
            con = pymysql.connect(host="localhost", user="root", password="1234", database="inventory_system")
            cur = con.cursor()
            cur.execute("INSERT INTO audit_log (user, action_type, module, description) VALUES (%s, %s, %s, %s)",
                        ("Admin", "Update", "Supplier", f"Updated product '{name_entry.get()}'"))
            con.commit()
            con.close()
        except Exception as e:
            messagebox.showerror('Error', f'Error due to {e}')

        finally:
            cursor.close()
            connection.close()

def add_supplier(invoice,name,contact,description,treeview):
    if invoice=="" or name=='' or contact=='' or description =='':
        messagebox.showerror('Error','All fields are required.')
    elif not validate_phone_number(contact):
        messagebox.showerror("Invalid Phone Number", "Please enter a valid 10-digit phone number.")
    else:
        cursor,connection=connect_database()
        if not cursor or not connection:
            return
        try:
            cursor.execute('use inventory_system')

            cursor.execute('CREATE TABLE IF NOT EXISTS supplier_data(invoice INT PRIMARY KEY,name VARCHAR(100),contact VARCHAR(15),description TEXT)')
            cursor.execute('SELECT * from supplier_data where invoice=%s', (invoice))
            if cursor.fetchone():
                messagebox.showerror('Error', "Invoice No. already exists")
                return
            cursor.execute('INSERT INTO supplier_data VALUES(%s,%s,%s,%s)',(invoice,name,contact,description))
            connection.commit()
            messagebox.showinfo('Info','Data is added successfully.')
            treeview_data(treeview)
        except Exception as e:
            messagebox.showerror('Error', f'Error due to {e}')
        try:
            con = pymysql.connect(host="localhost", user="root", password="1234", database="inventory_system")
            cur = con.cursor()
            cur.execute("INSERT INTO audit_log (user, action_type, module, description) VALUES (%s, %s, %s, %s)",
                    ("Admin", "insert", "Supplier", f"Inserted Supplier '{name_entry.get()}'"))
            con.commit()
            con.close()
        except Exception as e:
            messagebox.showerror('Error', f'Error due to{e}')

        finally:
            cursor.close()
            connection.close()

def select_data(event,invoice_entry,name_entry,contact_entry,description_text,treeview):
    index=treeview.selection()
    content=treeview.item(index)
    actual_content= content['values']
    invoice_entry.delete(0,END)
    name_entry.delete(0,END)
    contact_entry.delete(0,END)
    description_text.delete(1.0,END)
    invoice_entry.insert(0,actual_content[0])
    name_entry.insert(1,actual_content[1])
    contact_entry.insert(2,actual_content[2])
    description_text.insert(1.0,actual_content[3])

def treeview_data(treeview):
    cursor,connection=connect_database()
    if not cursor or not connection:
        return
    cursor.execute('use inventory_system')
    try:
        cursor.execute('SELECT * from supplier_data')
        records=cursor.fetchall()
        treeview.delete(*treeview.get_children())
        for record in records:
            treeview.insert('',END,values=record)
    except Exception as e:
        messagebox.showerror('Error', f'Error due to {e}')
    finally:
        cursor.close()
        connection.close()


def supplier_form(window):
    global back_image , name_entry
    supplier_frame=Frame(window,width=1175,height=630,background='#FFE5B4')
    supplier_frame.place(x=200,y=100)

    heading_label=Label(supplier_frame,text='Manage Supplier Details',font=('Times new roman',16,'bold'),bg='#2c3e50',fg='white')

    heading_label.place(x=0,y=0,relwidth=1)
    back_image = PhotoImage(file="../images/back.png")
    back_button = Button(supplier_frame, image=back_image, bd=0, cursor='hand2',
                         command=lambda: supplier_frame.place_forget())
    back_button.place(x=10, y=30)

    left_frame=Frame(supplier_frame, bg='#ffe0a3')
    left_frame.place(x=10,y=100)

    invoice_label=Label(left_frame,text='Invoice No',font=('Times new roman',14,'bold'),bg='white')
    invoice_label.grid(row=0,column=0,padx=(20,40),pady=(20,10),sticky='w')
    invoice_entry=Entry(left_frame,font=('Times new roman',14,'bold'),bg='lightyellow')
    invoice_entry.grid(row=0,column=1,pady=(20,10),padx=(0,20))

    name_label = Label(left_frame, text='Supplier Name', font=('Times new roman', 14, 'bold'), bg='white')
    name_label.grid(row=1, column=0,padx=(20,40),pady=25,sticky='w')
    name_entry = Entry(left_frame, font=('Times new roman', 14, 'bold'), bg='lightyellow')
    name_entry.grid(row=1, column=1,padx=(0,20))

    contact_label = Label(left_frame, text='Supplier Contact', font=('Times new roman', 14, 'bold'), bg='white')
    contact_label.grid(row=2, column=0,padx=(20,40),sticky='w')
    contact_entry = Entry(left_frame, font=('Times new roman', 14, 'bold'), bg='lightyellow')
    contact_entry.grid(row=2, column=1,padx=(0,20))

    description_label = Label(left_frame, text='Description', font=('Times new roman', 14, 'bold'), bg='white')
    description_label.grid(row=3, column=0,padx=(20,40),sticky='nw',pady=25)
    description_text= Text(left_frame, width=25,height=6,bd=2,bg='lightyellow')
    description_text.grid(row=3, column=1,pady=25,padx=(0,20))

    button_frame=Frame(left_frame, bg='#ffe0a3')
    button_frame.grid(row=4,columnspan=2,pady=20)

    add_button = Button(button_frame, text='Add', font=('times new roman', 14), width=8, cursor='hand2',
                        fg='white', bg='#0f4d7d',command= lambda:add_supplier(invoice_entry.get(),name_entry.get(),contact_entry.get(),description_text.get(1.0,END).strip(),treeview))
    add_button.grid(row=0, column=0, padx=20)

    update_button = Button(button_frame, text='Update', font=('times new roman', 12), width=8, cursor='hand2',
                           fg='white', bg='#0f4d7d',command=lambda:update_supplier(invoice_entry.get(),name_entry.get(),contact_entry.get(),description_text.get(1.0,END).strip(),treeview))
    update_button.grid(row=0, column=1)

    delete_button = Button(button_frame, text='Delete', font=('times new roman', 12), width=8, cursor='hand2',fg='white', bg='#0f4d7d',command=lambda:delete_supplier(invoice_entry.get(),treeview))
    delete_button.grid(row=0, column=2, padx=20)

    clear_button = Button(button_frame, text='Clear', font=('times new roman', 12), width=8, cursor='hand2',
                          fg='white', bg='#0f4d7d',command=lambda:clear(invoice_entry,name_entry,contact_entry,description_text,treeview))
    clear_button.grid(row=0, column=3,padx=(0,20))


    right_frame=Frame(supplier_frame, bg='#ffe0a3')
    right_frame.place(x=520,y=95,width=500,height=350)

    search_frame=Frame(right_frame, bg='#ffe0a3')
    search_frame.pack(pady=(0,20))

    num_label = Label(search_frame, text='Invoice No', font=('Times new roman', 14, 'bold'), bg='#ffe0a3')
    num_label.grid(row=0, column=0, padx=(0,15),pady=(20,0), sticky='w')
    num_entry = Entry(search_frame, font=('Times new roman', 14, 'bold'), bg='lightyellow',width=12)
    num_entry.grid(row=0, column=1,pady=(20,0))

    search_button = Button(search_frame, text='Search', font=('times new roman', 12), width=8, cursor='hand2',
                           fg='white', bg='#2c3e50',command=lambda:search_supplier(num_entry.get(),treeview))
    search_button.grid(row=0, column=2,padx=15,pady=(20,0))

    show_button = Button(search_frame, text='Show All', font=('times new roman', 12), width=8, cursor='hand2',
                           fg='white', bg='#2c3e50',command=lambda:show_all(treeview,num_entry))
    show_button.grid(row=0, column=3,padx=10,pady=(20,0))

    scrolly=Scrollbar(right_frame,orient=VERTICAL)
    scrollx=Scrollbar(right_frame,orient=HORIZONTAL)

    treeview=ttk.Treeview(right_frame,columns=('invoice','name','contact','description'),style="Custom.Treeview",show='headings',
                          yscrollcommand=scrolly.set,xscrollcommand=scrollx.set)
    scrolly.pack(side=RIGHT,fill=Y)
    scrollx.pack(side=BOTTOM,fill=X)
    scrollx.config(command=treeview.xview)
    scrolly.config(command=treeview.yview)
    treeview.pack(fill=BOTH,expand=1)
    treeview.heading('invoice',text='Invoice Id')
    treeview.heading('name', text='Supplier Name')
    treeview.heading('contact', text='Supplier Contact')
    treeview.heading('description', text='Description')

    treeview.column('invoice',width=80)
    treeview.column('name', width=160)
    treeview.column('contact', width=120)
    treeview.column('description', width=310)

    treeview_data(treeview)
    treeview.bind('<ButtonRelease-1>',lambda event:select_data(event,invoice_entry,name_entry,contact_entry,description_text,treeview))
    return supplier_frame