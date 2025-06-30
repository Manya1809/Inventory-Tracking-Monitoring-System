from tkinter import *
from files.employee import employee_form
from files.supplier import supplier_form
from files.category import category_form
from files.product import product_form
from files.employee import connect_database
from tkinter import messagebox
from files.sle import sales_form
from files.audit import show_audit_logs
import time

def logout():
    window.destroy()

def exit():
    window.destroy()
def update():
    cursor,connection = connect_database()
    if not cursor or not connection:
        return
    try:
        cursor.execute('Use inventory_system')
        cursor.execute('SELECT * from employee_data')
        emp_records = cursor.fetchall()
        total_emp_count_label.config(text=len(emp_records))
        cursor.execute('SELECT * from supplier_data')
        sup_records= cursor.fetchall()
        total_sup_count_label.config(text=len(sup_records))

        cursor.execute('SELECT * from category_data')
        cat_records = cursor.fetchall()
        total_cat_count_label.config(text=len(cat_records))

        cursor.execute('SELECT * from product_data')
        prod_records = cursor.fetchall()
        total_prod_count_label.config(text=len(prod_records))

        cursor.execute('SELECT * from sales_data')
        prod_records = cursor.fetchall()
        total_sales_count_label.config(text=len(prod_records))


        date_time=time.strftime('%I:%M:%S %p on %A, %B %d,%Y')
        subtitleLabel.config(text=f'Welcome Admin \t\t\t\t\t\t\t {date_time}')
        subtitleLabel.after(1000,update)
    except Exception as e:
        messagebox.showerror("Error", f"Error in dashboard update: {e}")
def check_low_stock():
    try:
        cursor, connection = connect_database()
        if not cursor or not connection:
            return
        cursor.execute('USE inventory_system')
        cursor.execute('SELECT name, quantity FROM product_data WHERE quantity < 10')
        low_stock_items = cursor.fetchall()

        if low_stock_items:
            alert_msg = "Low Stock Alert!\n\n"
            for name, qty in low_stock_items:
                alert_msg += f"{name}: {qty} left\n"
            messagebox.showwarning("Low Stock Warning", alert_msg)

    except Exception as e:
        print(f"Low stock check failed: {e}")

    subtitleLabel.after(300000, check_low_stock)  # Repeat every 5 minutes


def tax_window():
    def save_tax():
        value= tax_count.get()
        cursor,connection = connect_database()
        if not cursor or not connection:
            return
        cursor.execute('Use inventory_system')
        cursor.execute('CREATE TABLE IF NOT EXISTS tax_table(id INT PRIMARY KEY, tax DECIMAL(5,2))')
        cursor.execute('Select id from tax_table where id=1')
        if cursor.fetchone():
            cursor.execute('UPDATE tax_table SET tax=%s where id =1',value)
        else:
            cursor.execute('INSERT INTO tax_table(id,tax) VALUES(1,%s)',value)
        connection.commit()
        messagebox.showinfo('Success',f'Tax is set to {value}% and saved successfully.',parent=tax_root)

    global tax_count
    tax_root=Toplevel()
    tax_root.title('Tax Window')
    tax_root.geometry('300x200')
    tax_root.config(bg='#FFE5B4')
    tax_root.grab_set()
    tax_percentage=Label(tax_root,text="Enter Tax Percentage(%)",font=('Times New Roman',13),bg='#2c3e50',fg="white")
    tax_percentage.pack(pady=10)
    tax_count=Spinbox(tax_root,from_=0,to=100,font=('Times New Roman',12))
    tax_count.pack(pady=10)
    save_button = Button(tax_root, text='Save', font=("times new roman", 20, 'bold'),bg='#4d636d',fg='white',width=10,command=save_tax)
    save_button.pack(pady=20)

current_frame=None
def show_form(form_function):
    global current_frame
    if current_frame:
        current_frame.place_forget()
    current_frame=form_function(window)

window = Tk()
window.title("Dashboard")
window.geometry("1375x780")
window.resizable(0,0)
window.config(bg='#FFE5B4')

bg_Image=PhotoImage(file="../images/icon.png")
titleLabel =Label(window,image=bg_Image,compound=LEFT,text="Inventory Tracking & Monitoring System",font=('times new roman',40,'bold'),bg='#FFE5B4',fg="#2c3e50",anchor='w')
titleLabel.place(x=0,y=0,relwidth=1)

logoutButton = Button(window,text="Logout",font=('times new roman',20,'bold'),fg='#010c48',command=lambda:logout())
logoutButton.place(x=1220,y=10)

subtitleLabel =Label(window, text ='Welcome Admin\t\t Date:08-07-2024\t\t Time:12:36:27pm',font=('times new roman',15,'bold'),bg="#4d636d",fg="white")
subtitleLabel.place(x=0,y=70,relwidth=1)

leftFrame = Frame(window,bg="#87ceeb")
leftFrame.place(x=0,y=102,width=200,height=630)

logoImage=PhotoImage(file='../images/logo.png')
imageLabel = Label(leftFrame,image=logoImage)
imageLabel.pack()

employee_icon=PhotoImage(file="../images/employee.png")
employee_button = Button(leftFrame,image=employee_icon,bg='#FFE5B4', fg='BLACK', activebackground='#3CB371',compound=LEFT,text='Employees',font=("times new roman",21,'bold'),command= lambda :show_form(employee_form))
employee_button.pack(fill=X)


audit_button=Button(leftFrame,image=employee_icon,bg='#FFE5B4', fg='BLACK', activebackground='#3CB371',compound=LEFT,text='Audit Logs',font=("times new roman",21,'bold'),command= lambda :show_form(show_audit_logs))
audit_button.pack(fill=X)

supplier_icon=PhotoImage(file="../images/supplier.png")
supplier_button = Button(leftFrame,image=supplier_icon,bg='#FFE5B4', activebackground='#3CB371',compound=LEFT,text='Suppliers',font=("times new roman",21,'bold'),command= lambda :show_form(supplier_form))
supplier_button.pack(fill=X)

category_icon=PhotoImage(file="../images/category.png")
category_button = Button(leftFrame,image=category_icon,bg='#FFE5B4', activebackground='#3CB371',compound=LEFT,text='Category',font=("times new roman",21,'bold'),command= lambda :show_form(category_form))
category_button.pack(fill=X)

Product_icon=PhotoImage(file="../images/product.png")
Product_button = Button(leftFrame,image=Product_icon,bg='#FFE5B4', activebackground='#3CB371',compound=LEFT,text='Prodcuts',font=("times new roman",21,'bold'),command= lambda :show_form(product_form))
Product_button.pack(fill=X)

sales_icon=PhotoImage(file="../images/sales.png")
sales_button = Button(leftFrame,image=sales_icon,bg='#FFE5B4', activebackground='#3CB371',compound=LEFT,text='Sales',font=("times new roman",21,'bold'),command= lambda :show_form(sales_form))
sales_button.pack(fill=X)

tax_icon=PhotoImage(file="../images/taxes.png")
tax_button = Button(leftFrame,image=tax_icon,bg='#FFE5B4',compound=LEFT,text='Tax',font=("times new roman",21,'bold'),command=tax_window)
tax_button.pack(fill=X)

exit_icon=PhotoImage(file="../images/exit.png")
exit_button = Button(leftFrame,image=exit_icon,bg='#FFE5B4', activebackground='#3CB371',compound=LEFT,text='Exit',font=("times new roman",21,'bold'),command=lambda:exit())
exit_button.pack(fill=X)

emp_frame = Frame(window,bg='#3498DB',bd=3,relief="ridge")
emp_frame.place(x=400,y=125,height=170,width=280)
total_emp_icon=PhotoImage(file='../images/total_emp.png')
total_emp_icon_label=Label(emp_frame,image=total_emp_icon,bg='#3498DB')
total_emp_icon_label.pack(pady=10)
total_emp_label=Label(emp_frame,text="Total Employees",bg='#3498DB',fg="white",font=("times new roman",15,'bold'))
total_emp_label.pack()
total_emp_count_label=Label(emp_frame,text="0",bg='#3498DB',fg="white",font=("times new roman",30,'bold'))
total_emp_count_label.pack()

sup_frame = Frame(window,bg='#9B59B6',bd=3,relief="ridge")
sup_frame.place(x=800,y=125,height=170,width=280)
total_sup_icon=PhotoImage(file='../images/total_sup.png')
total_sup_icon_label=Label(sup_frame,image=total_sup_icon,bg='#9B59B6')
total_sup_icon_label.pack(pady=10)

total_sup_label=Label(sup_frame,text="Total Suppliers",bg='#9B59B6',fg="white",font=("times new roman",15,'bold'))
total_sup_label.pack()
total_sup_count_label=Label(sup_frame,text="0",bg='#9B59B6',fg="white",font=("times new roman",30,'bold'))
total_sup_count_label.pack()

cat_frame = Frame(window,bg='#1ABC9C',bd=3,relief="ridge")
cat_frame.place(x=400,y=340,height=170,width=280)
total_cat_icon=PhotoImage(file='../images/total_cat.png')
total_cat_icon_label=Label(cat_frame,image=total_cat_icon,bg='#1ABC9C')
total_cat_icon_label.pack(pady=10)
total_cat_label=Label(cat_frame,text="Total Category",bg='#1ABC9C',fg="white",font=("times new roman",15,'bold'))
total_cat_label.pack()
total_cat_count_label=Label(cat_frame,text="0",bg='#1ABC9C',fg="white",font=("times new roman",30,'bold'))
total_cat_count_label.pack()

prod_frame = Frame(window,bg='#298089',bd=3,relief="ridge")
prod_frame.place(x=800,y=340,height=170,width=280)
total_prod_icon=PhotoImage(file='../images/total_prod.png')
total_prod_icon_label=Label(prod_frame,image=total_prod_icon,bg='#298089')
total_prod_icon_label.pack(pady=10)
total_prod_label=Label(prod_frame,text="Total Products",bg='#298089',fg="white",font=("times new roman",15,'bold'))
total_prod_label.pack()
total_prod_count_label=Label(prod_frame,text="0",bg='#298089',fg="white",font=("times new roman",30,'bold'))
total_prod_count_label.pack()

sales_frame = Frame(window,bg='#E74C3C',bd=3,relief="ridge")
sales_frame.place(x=600,y=525,height=170,width=280)
total_sales_icon=PhotoImage(file='../images/total_sales.png')
total_sales_icon_label=Label(sales_frame,image=total_sales_icon,bg='#E74C3C')
total_sales_icon_label.pack(pady=10)
total_sales_label=Label(sales_frame,text="Total Sales",bg='#E74C3C',fg="white",font=("times new roman",15,'bold'))
total_sales_label.pack()
total_sales_count_label=Label(sales_frame,text="0",bg='#E74C3C',fg="white",font=("times new roman",30,'bold'))
total_sales_count_label.pack()
update()
check_low_stock()
window.mainloop()



