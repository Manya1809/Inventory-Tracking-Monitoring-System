from tkinter import *
from tkinter import ttk
import re
from datetime import datetime
from pymysql import connect
from tkcalendar import Calendar, DateEntry
from tkinter import messagebox
import pymysql

def customize_treeview():
    style = ttk.Style()
    style.theme_use('default')
    style.configure("Custom.Treeview")
    style.map('Custom.Treeview', background=[('selected', '#f7b2b7')])


def validate_gmail(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9_.+-]+@gmail\.com$"
    if re.match(pattern, email):
        return True
    return False

def validate_phone_number(phone_number: str) -> bool:
    pattern = r"^[6-9]\d{9}$"
    if re.match(pattern, phone_number):
        return True
    return False

def validate_salary(salary: str) -> bool:
    try:
        salary = float(salary)
        if salary <= 0:
            return False
        return True
    except ValueError:
        return False

def validate_password(password: str) -> bool:
    pattern = r"^\d{4}$"
    if re.match(pattern, password):
        return True
    return False


def connect_database():
    try:
        connection = pymysql.connect(host="localhost", user="root", password="1234")
        cursor = connection.cursor()
    except:
        messagebox.showerror("Error", "Database connectivity issue try again, please open mysql command line client")
        return None, None
    return cursor, connection


def create_database_table():
    cursor, connection = connect_database()
    cursor.execute('CREATE DATABASE IF NOT EXISTS inventory_system')
    cursor.execute('USE inventory_system')
    cursor.execute('CREATE TABLE IF NOT EXISTS employee_data(empid INT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(100),email VARCHAR(100),gender VARCHAR(50),dob VARCHAR(30),contact VARCHAR(12),employment_type VARCHAR(50),'
        'education VARCHAR(100),work_shift VARCHAR(50),address VARCHAR(100),doj VARCHAR(30),salary VARCHAR(50),usertype VARCHAR(50),password VARCHAR(50))')

def treeview_data():
    cursor, connection = connect_database()
    if not cursor or not connection:
        return
    cursor.execute('use inventory_system')
    try:
        cursor.execute('SELECT * from employee_data')
        employee_records = cursor.fetchall()
        employee_treeview.delete(*employee_treeview.get_children())
        for record in employee_records:
            employee_treeview.insert('', END, values=record)
    except Exception as e:
        messagebox.showerror('Error', f'Error due to {e}')
    finally:
        cursor.close()
        connection.close()


def select_data(event, empid_entry, name_entry, email_entry,
                gender_combobox, dob_entry, contact_entry, employment_type_combobox, education_combobox,
                work_shift_combobox, adress_text, doj_date_entry, salary_entry, usertype_combobox, password_entry):
    index = employee_treeview.selection()
    content = employee_treeview.item(index)
    row = content['values']
    clear_fields(empid_entry, name_entry, email_entry,
                 gender_combobox, dob_entry, contact_entry, employment_type_combobox, education_combobox,
                 work_shift_combobox, adress_text, doj_date_entry, salary_entry, usertype_combobox, password_entry,
                 False)
    empid_entry.insert(0, row[0])
    name_entry.insert(0, row[1])
    email_entry.insert(0, row[2])
    gender_combobox.set(row[3])
    dob_entry.set_date(row[4])
    contact_entry.insert(0, row[5])
    employment_type_combobox.set(row[6])
    education_combobox.set(row[7])
    work_shift_combobox.set(row[8])
    adress_text.insert(1.0, row[9])
    doj_date_entry.insert(0, row[10])
    salary_entry.insert(0, row[11])
    usertype_combobox.set(row[12])
    password_entry.insert(0, row[13])

def add_employee(empid, name, email, gender, dob, contact, employment_type, education,
                 work_shift, address, doj, salary, user_type, password):
    if (
            empid == '' or name == '' or email == '' or gender == 'Select Gender' or contact == '' or employment_type == "Select Education"
            or work_shift == "Select Shift" or address == '\n' or salary == '' or user_type == "Select User Type" or password == ""):
        messagebox.showerror("Error", "All Fields are required")
    elif not validate_gmail(email):
        messagebox.showerror("Invalid Gmail", "Please enter a valid Gmail address.")
    elif not validate_phone_number(contact):
        messagebox.showerror("Invalid Phone Number", "Please enter a valid 10-digit phone number.")
    elif not validate_salary(salary):
        messagebox.showerror("Invalid Salary", "Please enter a valid salary amount.")
    elif not validate_password(password):
        messagebox.showerror("Invalid Password", "Please enter a 4-digit password.")

    else:
        cursor, connection = connect_database()
        if not cursor or not connection:
            return
        cursor.execute('use inventory_system')
        try:
            cursor.execute('SELECT empid from employee_data where empid=%s', (empid))
            if cursor.fetchone():
                messagebox.showerror('Error', "Id already exists")
                return
            address=address.strip()

            cursor.execute('INSERT INTO employee_data VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                           (empid, name, email, gender, dob, contact, employment_type, education,
                            work_shift, address, doj, salary, user_type, password))
            connection.commit()
            try:
                con = pymysql.connect(host="localhost", user="root", password="1234", database="inventory_system")
                cur = con.cursor()
                cur.execute("INSERT INTO audit_log (user, action_type, module, description) VALUES (%s, %s, %s, %s)",
                            ("Admin", "Insert", "Employee", f"Inserted Employee '{name_entry.get()}'"))
                con.commit()
                con.close()
            except Exception as e:
                messagebox.showerror('Error', f'Error due to{e}')
            treeview_data()
            messagebox.showinfo("Success", "Data is inserted successfully")
        except Exception as e:
            messagebox.showerror('Error', f'Error due to {e}')

        finally:
            cursor.close()
            connection.close()


def clear_fields(empid_entry, name_entry, email_entry,
                 gender_combobox, dob_entry, contact_entry, employment_type_combobox,
                 education_combobox, work_shift_combobox, adress_text,
                 doj_date_entry, salary_entry, usertype_combobox, password_entry, check):
    empid_entry.delete(0, END)
    name_entry.delete(0, END)
    email_entry.delete(0, END)
    from datetime import date
    dob_entry.set_date(date.today())
    gender_combobox.set('Select Gender')
    contact_entry.delete(0, END)
    employment_type_combobox.set("Select Type")
    education_combobox.set("Select Education")
    work_shift_combobox.set("Select Work Shift")
    adress_text.delete(1.0, END)
    doj_date_entry.set_date(date.today())
    salary_entry.delete(0, END)
    usertype_combobox.set('Select User Type')
    password_entry.delete(0, END)
    if check:
        employee_treeview.selection_remove(employee_treeview.selection())


def update_employee(empid, name, email, gender, dob, contact, employment_type, education,
                    work_shift, address, doj, salary, user_type, password):
    selected = employee_treeview.selection()
    if not selected:
        messagebox.showerror('Error', "No row is selected")
    else:
        cursor, connection = connect_database()
        if not cursor or not connection:
            return
        try:
            cursor.execute('use inventory_system')
            cursor.execute('SELECT * from employee_data WHERE empid=%s',(empid,))
            current_data=cursor.fetchone()
            current_data = current_data[1:]
            address=address.strip()
            new_data = (name, email, gender, dob, contact, employment_type, education,
                        work_shift, address, doj, salary, user_type, password)
            if current_data==new_data:
                messagebox.showinfo('Information',"No changes detected")
                return
            elif not validate_gmail(email):
                messagebox.showerror("Invalid Gmail", "Please enter a valid Gmail address.")
            elif not validate_phone_number(contact):
                messagebox.showerror("Invalid Phone Number", "Please enter a valid 10-digit phone number.")
            elif not validate_salary(salary):
                messagebox.showerror("Invalid Salary", "Please enter a valid salary amount.")
            elif not validate_password(password):
                messagebox.showerror("Invalid Password", "Please enter a 4-digit password.")
            else:
                cursor.execute(
                    "UPDATE employee_data SET name=%s,email=%s,gender=%s,dob=%s,contact=%s,employment_type=%s,"
                    "education=%s,work_shift=%s,address=%s,doj=%s,salary=%s,usertype=%s,password=%s WHERE empid=%s",
                    (name, email, gender, dob, contact, employment_type, education,
                     work_shift, address, doj, salary, user_type, password, empid))
                connection.commit()
                try:
                    con = pymysql.connect(host="localhost", user="root", password="1234", database="inventory_system")
                    cur = con.cursor()
                    cur.execute(
                        "INSERT INTO audit_log (user, action_type, module, description) VALUES (%s, %s, %s, %s)",
                        ("Admin", "Update", "Employee", f"Updated Employee '{name_entry.get()}'"))
                    con.commit()
                    con.close()
                except Exception as e:
                    messagebox.showerror('Error', f'Error due to {e}')
                treeview_data()
                messagebox.showinfo("Success", "Data is updated successfully")

        except Exception as e:
            messagebox.showerror('Error', f'Error due to {e}')
        finally:
            cursor.close()
            connection.close()

def delete_employee(empid,):
    selected = employee_treeview.selection()
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
                cursor.execute('DELETE FROM employee_data WHERE empid=%s',(empid,))
                connection.commit()
                treeview_data()
                messagebox.showinfo('Success','Record is Deleted Successfully')
            except Exception as e:
                messagebox.showerror('Error', f'Error due to {e}')
            try:
                con = pymysql.connect(host="localhost", user="root", password="1234", database="inventory_system")
                cur = con.cursor()
                cur.execute("INSERT INTO audit_log (user, action_type, module, description) VALUES (%s, %s, %s, %s)",
                            ("Admin", "Delete", "Employee", f"Deleted Employee '{name_entry.get()}'"))
                con.commit()
                con.close()
            except Exception as e:
                messagebox.showerror('Error', f'Error due to{e}')
            finally:
                cursor.close()
                connection.close()
def search_employee(search_option,value):
    if search_option=="Search By":
        messagebox.showerror('Error','No Option is selected')
    elif value=="":
        messagebox.showerror('Error','Enter the value')
    else:
        search_option=search_option.replace(' ','_')
        cursor, connection = connect_database()
        if not cursor or not connection:
            return
        try:
            cursor.execute('Use inventory_system')
            cursor.execute(f'SELECT * from employee_data WHERE {search_option} LIKE %s',f'%{value}%')
            records=cursor.fetchall()
            employee_treeview.delete(*employee_treeview.get_children())
            for record in records:
                employee_treeview.insert('',END,value=record)
        except Exception as e:
            messagebox.showerror('Error', f'Error due to {e}')
        finally:
            cursor.close()
            connection.close()

def show_all(search_entry,search_combobox):
    treeview_data()
    search_entry.delete(0,END)
    search_combobox.set("Search By")


def employee_form(window):
    global back_image, employee_treeview,name_entry
    employee_frame = Frame(window, width=1150, height=630,background='#FFE5B4')
    employee_frame.place(x=200, y=100)
    heading_Label = Label(employee_frame, text='Manage Employee Details', font=('times new roman', 16,'bold'),
                          bg='#2c3e50', fg='white')
    heading_Label.place(x=0, y=0, relwidth=1)

    back_image = PhotoImage(file="../images/back.png")

    top_frame = Frame(employee_frame, width=1360,background='#FFE5B4')
    top_frame.place(x=0, y=40, relwidth=1, height=235)
    back_button = Button(top_frame, image=back_image, bd=0, cursor='hand2',
                         command=lambda: employee_frame.place_forget())
    back_button.place(x=10, y=0)
    search_frame = Frame(top_frame,background='#FFE5B4')
    search_frame.pack()

    search_combobox = ttk.Combobox(search_frame, values=('EmpId', 'Name', 'Email','Employment Type','Education','Work Shift'), font=('times new roman', 12),
                                   state='readonly')
    search_combobox.set('Search By')
    search_combobox.grid(row=0, column=0, padx=20)
    search_entry = Entry(search_frame, font=('times new roman', 12), bg='lightyellow')
    search_entry.grid(row=0, column=1)
    search_button = Button(search_frame, text='Search', font=('times new roman', 12), width=10, cursor='hand2',
                           fg='white', bg='#2c3e50',command=lambda:search_employee(search_combobox.get(),search_entry.get()))
    search_button.grid(row=0, column=2, padx=20)
    show_button = Button(search_frame, text='Show All', font=('times new roman', 12), width=10, cursor='hand2',
                         fg='white', bg='#2c3e50',command=lambda:show_all(search_entry,search_combobox))
    show_button.grid(row=0, column=3, padx=20)

    horizontal_scrollbar = Scrollbar(top_frame, orient=HORIZONTAL)

    vertical_scrollbar = Scrollbar(top_frame, orient=VERTICAL)
    customize_treeview()
    employee_treeview = ttk.Treeview(top_frame,
                                     columns=('empid', 'name', 'email', 'gender', 'dob', 'contact', 'employment_type','education'
                                              , 'work_shift', 'adress','doj' , 'salary', 'usertype',
                                              'password'),
                                     show='headings',style="Custom.Treeview",
                                     yscrollcommand=vertical_scrollbar.set, xscrollcommand=horizontal_scrollbar.set)

    horizontal_scrollbar.pack(side=BOTTOM, fill=X)
    vertical_scrollbar.pack(side=RIGHT, fill=Y, pady=(10, 0))
    horizontal_scrollbar.config(command=employee_treeview.xview)
    vertical_scrollbar.config(command=employee_treeview.yview)

    employee_treeview.pack(pady=(10, 0))
    employee_treeview.heading('empid', text='Empid')
    employee_treeview.heading('name', text='Name')
    employee_treeview.heading('email', text='Email')
    employee_treeview.heading('gender', text='Gender')
    employee_treeview.heading('dob', text='DOB')
    employee_treeview.heading('contact', text='Contact')
    employee_treeview.heading('employment_type', text='Emp Type')
    employee_treeview.heading('education', text='Education')
    employee_treeview.heading('work_shift', text='Work Shift')
    employee_treeview.heading('adress', text='Address')
    employee_treeview.heading('doj', text='DOJ')
    employee_treeview.heading('salary', text='Salary')
    employee_treeview.heading('usertype', text='User Type')
    employee_treeview.heading('password', text='Password')

    employee_treeview.column('empid', width=60)
    employee_treeview.column('name', width=90)
    employee_treeview.column('email', width=140)
    employee_treeview.column('gender', width=50)
    employee_treeview.column('dob', width=50)
    employee_treeview.column('contact', width=80)
    employee_treeview.column('employment_type', width=110)
    employee_treeview.column('education', width=90)
    employee_treeview.column('work_shift', width=120)
    employee_treeview.column('adress', width=200)
    employee_treeview.column('doj', width=70)
    employee_treeview.column('salary', width=90)
    employee_treeview.column('usertype', width=120)
    employee_treeview.column('password', width=90)


    treeview_data()

    detail_frame = Frame(employee_frame, bg='#ffe0a3')
    detail_frame.place(x=60, y=290)

    empid_label = Label(detail_frame, text='EmpId', font=('times new roman', 12), bg='white')
    empid_label.grid(row=0, column=0, padx=20, pady=10, sticky='w')
    empid_entry = Entry(detail_frame, font=('times new roman', 12), bg='lightyellow')
    empid_entry.grid(row=0, column=1, padx=20, pady=10)

    name_label = Label(detail_frame, text='Name', font=('times new roman', 12), bg='white')
    name_label.grid(row=0, column=2, padx=20, pady=10, sticky='w')
    name_entry = Entry(detail_frame, font=('times new roman', 12), bg='lightyellow')
    name_entry.grid(row=0, column=3, padx=20, pady=10)

    email_label = Label(detail_frame, text='Email', font=('times new roman', 12), bg='white')
    email_label.grid(row=0, column=4, padx=20, pady=10, sticky='w')
    email_entry = Entry(detail_frame, font=('times new roman', 12), bg='lightyellow')
    email_entry.grid(row=0, column=5, padx=20, pady=10)

    gender_label = Label(detail_frame, text='Gender', font=('times new roman', 12), bg='white')
    gender_label.grid(row=1, column=0, padx=20, pady=10, sticky='w')
    gender_combobox = ttk.Combobox(detail_frame, values=('Male', 'Female'), font=('times new roman', 12), width=18,
                                   state='readonly')
    gender_combobox.set('Select Gender')
    gender_combobox.grid(row=1, column=1)

    dob_label = Label(detail_frame, text='Date of Birth', font=('times new roman', 12), bg='white')
    dob_label.grid(row=1, column=2, padx=20, pady=10, sticky='w')
    dob_entry = DateEntry(detail_frame, width=18, font=('times new roman', 12), state='readonly')
    dob_entry.grid(row=1, column=3)

    contact_label = Label(detail_frame, text='Contact', font=('times new roman', 12), bg='white')
    contact_label.grid(row=1, column=4, padx=20, pady=10, sticky='w')
    contact_entry = Entry(detail_frame, font=('times new roman', 12), bg='lightyellow')
    contact_entry.grid(row=1, column=5, padx=20, pady=10)

    employment_type_label = Label(detail_frame, text='Employment Type', font=('times new roman', 12), bg='white')
    employment_type_label.grid(row=2, column=0, padx=20, pady=10, sticky='w')
    employment_type_combobox = ttk.Combobox(detail_frame,
                                            values=('Full Time', 'Part Time', 'Casual', 'Contract', 'Intern'),
                                            font=('times new roman', 12), width=18, state='readonly')
    employment_type_combobox.set('Select Type')
    employment_type_combobox.grid(row=2, column=1, padx=20, pady=10)

    education_label = Label(detail_frame, text='Education', font=('times new roman', 12), bg='white')
    education_label.grid(row=3, column=2, padx=20, pady=10, sticky='w')
    education_options = ["B.Tech", "B.Com", "M.Tech", "M.Com", "B.Sc", "M.Sc", "BBA", "MBA", "LLB", "LLM", "B.Arch"]
    education_combobox = ttk.Combobox(detail_frame, values=education_options, font=('times new roman', 12), width=18,
                                      state='readonly')
    education_combobox.set('Select Education')
    education_combobox.grid(row=3, column=3, padx=20, pady=10)

    work_shift_label = Label(detail_frame, text='Work Shift', font=('times new roman', 12), bg='white')
    work_shift_label.grid(row=2, column=4, padx=20, pady=10, sticky='w')
    work_shift_combobox = ttk.Combobox(detail_frame, values=('Morning', 'Evening', 'Night'),
                                       font=('times new roman', 12), width=18,
                                       state='readonly')
    work_shift_combobox.set('Select Work Shift')
    work_shift_combobox.grid(row=2, column=5, padx=20, pady=10)

    adress_label = Label(detail_frame, text='Address', font=('times new roman', 12), bg='white')
    adress_label.grid(row=3, column=0, padx=20, pady=10, sticky='w')
    adress_text = Text(detail_frame, width=20, height=3, font=('times new roman', 12), bg='lightyellow')
    adress_text.grid(row=3, column=1, rowspan=2)

    doj_label = Label(detail_frame, text='Date of Joining', font=('times new roman', 12), bg='white')
    doj_label.grid(row=2, column=2, padx=20, pady=10, sticky='w')
    doj_date_entry = DateEntry(detail_frame, font=('times new roman', 12), width=18, state='readonly',
                               date_pattern='dd/mm/yyyy')
    doj_date_entry.grid(row=2, column=3, padx=20, pady=10)

    usertype_label = Label(detail_frame, text='User Type', font=('times new roman', 12), bg='white')
    usertype_label.grid(row=4, column=2, padx=20, pady=10, sticky='w')
    usertype_combobox = ttk.Combobox(detail_frame, values=('Admin', 'Employee'), font=('times new roman', 12), width=18,
                                     state='readonly')
    usertype_combobox.set('Select User Type')
    usertype_combobox.grid(row=4, column=3, padx=20, pady=10)

    salary_label = Label(detail_frame, text='Salary', font=('times new roman', 12), bg='white')
    salary_label.grid(row=3, column=4, padx=20, pady=10, sticky='w')
    salary_entry = Entry(detail_frame, font=('times new roman', 12), bg='lightyellow')
    salary_entry.grid(row=3, column=5, padx=20, pady=10)

    password_label = Label(detail_frame, text='Password', font=('times new roman', 12), bg='white')
    password_label.grid(row=4, column=4, padx=20, pady=10, sticky='w')
    password_entry = Entry(detail_frame, font=('times new roman', 12), bg='lightyellow')
    password_entry.grid(row=4, column=5, padx=20, pady=10)

    button_frame = Frame(employee_frame,background='#FFE5B4')
    button_frame.place(x=240, y=530)
    add_button = Button(button_frame, text='Add', font=('times new roman', 12), width=10, cursor='hand2',
                        fg='white', bg='#0f4d7d',
                        command=lambda: add_employee(empid_entry.get(), name_entry.get(), email_entry.get(),
                                                     gender_combobox.get(), dob_entry.get(), contact_entry.get(),
                                                     employment_type_combobox.get(),
                                                     education_combobox.get(), work_shift_combobox.get(),
                                                     adress_text.get(1.0, END),
                                                     doj_date_entry.get(), salary_entry.get(), usertype_combobox.get(),
                                                     password_entry.get()))
    add_button.grid(row=1, column=0, padx=20)

    update_button = Button(button_frame, text='Update', font=('times new roman', 12), width=10, cursor='hand2',
                           fg='white', bg='#0f4d7d',
                           command=lambda: update_employee(empid_entry.get(), name_entry.get(), email_entry.get(),
                                                           gender_combobox.get(), dob_entry.get(), contact_entry.get(),
                                                           employment_type_combobox.get(),
                                                           education_combobox.get(), work_shift_combobox.get(),
                                                           adress_text.get(1.0, END),
                                                           doj_date_entry.get(), salary_entry.get(),
                                                           usertype_combobox.get(), password_entry.get()))
    update_button.grid(row=1, column=1, padx=20)

    delete_button = Button(button_frame, text='Delete', font=('times new roman', 12), width=10, cursor='hand2',
                           fg='white', bg='#0f4d7d',command= lambda: delete_employee(empid_entry.get(),))
    delete_button.grid(row=1, column=2, padx=20)

    clear_button = Button(button_frame, text='Clear', font=('times new roman', 12), width=10, cursor='hand2',
                          fg='white', bg='#0f4d7d', command=lambda: clear_fields(empid_entry, name_entry, email_entry,
                                                                                 gender_combobox, dob_entry,
                                                                                 contact_entry,
                                                                                 employment_type_combobox,
                                                                                 education_combobox,
                                                                                 work_shift_combobox, adress_text,
                                                                                 doj_date_entry, salary_entry,
                                                                                 usertype_combobox, password_entry,
                                                                                 True))
    clear_button.grid(row=1, column=3, padx=20)
    employee_treeview.bind('<ButtonRelease-1>', lambda event: select_data(event, empid_entry, name_entry, email_entry,
                                                                          gender_combobox, dob_entry, contact_entry,
                                                                          employment_type_combobox, education_combobox,
                                                                          work_shift_combobox, adress_text,
                                                                          doj_date_entry, salary_entry,
                                                                          usertype_combobox, password_entry))
    return employee_frame

