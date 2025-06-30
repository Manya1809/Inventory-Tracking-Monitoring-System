from tkinter import*
from PIL import Image,ImageTk
from tkinter import ttk,messagebox
import pymysql
import time
import os
import tempfile

def connect_database():
    try:
        connection = pymysql.connect(host="localhost", user="root", password="1234")
        cursor = connection.cursor()
    except:
        messagebox.showerror("Error", "Database connectivity issue try again, please open mysql command line client")
        return None, None
    return cursor, connection


def create_database_table():
    try:
        cursor, connection = connect_database()
        cursor.execute('CREATE DATABASE IF NOT EXISTS inventory_system')
        cursor.execute('USE inventory_system')
        cursor.execute('CREATE TABLE customer(customer_id INT PRIMARY KEY AUTO_INCREMENT,customer_name VARCHAR(255) NOT NULL,contact_number VARCHAR(10) NOT NULL)')

        cursor.execute('CREATE TABLE billing (bill_number INT PRIMARY KEY AUTO_INCREMENT,customer_id INT,bill_date DATE,bill_amount DECIMAL(10, 2),discount DECIMAL(10, 2),net_pay DECIMAL(10, 2),FOREIGN KEY (customer_id) REFERENCES customer(customer_id)')
        connection.commit()
        connection.close()
        print("Tables created successfully")

    except pymysql.err.Error as e:
        print("Error creating tables: ", e)


class billClass:

    def validate_contact(self):
        contact = self.var_contact.get()
        if contact == "":
            messagebox.showerror("Error", "Contact number is required")
            return False
        elif not contact.isdigit():
            messagebox.showerror("Error", "Contact number should be digits only")
            return False
        elif len(contact) != 10:
            messagebox.showerror("Error", "Contact number should be 10 digits")
            return False
        return True



    def __init__(self,root):
        self.root=root
        self.root.geometry("1375x780+0+0")
        self.root.title("Inventory Tracking & Monitoring")
        self.root.resizable(False,False)
        self.root.config(bg="white")
        self.cart_list=[]
        self.chk_print=0

        self.icon_title = PhotoImage(file="../images/logo1.png")
        title = Label(self.root, text="Inventory Tracking & Monitoring", image=self.icon_title, compound=LEFT,
                      font=("times new roman", 40, "bold"), bg="#010c48", fg="white", anchor="w", padx=20).place(x=0,y=0,relwidth=1,height=70)

        btn_log_out = Button(self.root, text="Logout", command=self.logout,font=("times new roman", 15, "bold"), bg="yellow",cursor="hand2").place(x=1150, y=10, height=50, width=150)

        self.label_clock = Label(self.root,text="Inventory Tracking & Monitoring\t\t Date: DD:MM:YYYY\t\t Time: HH:MM:SS",
                               font=("times new roman", 15), bg="#4d636d", fg="white")
        self.label_clock.place(x=0, y=70, relwidth=1, height=30)

        label_footer = Label(self.root,text="IMS-Inventory Management System \nFor any Technical Issues Contact: 8299126801",font=("times new roman", 10), bg="#4d636d", fg="white").pack(side=BOTTOM, fill=X)

        ProductFrame1 = Frame(self.root, bd=4, relief=RIDGE, bg="white")
        ProductFrame1.place(x=6, y=110, width=410, height=550)

        proTitle = Label(ProductFrame1, text="All Products", font=("goudy old style", 20, "bold"), bg="#262626",
                       fg="white").pack(side=TOP, fill=X)

        self.var_search = StringVar()

        ProductFrame2 = Frame(ProductFrame1, bd=2, relief=RIDGE, bg="white")
        ProductFrame2.place(x=2, y=42, width=398, height=90)

        label_search = Label(ProductFrame2, text="Search Product | By Name", font=("times new roman", 15, "bold"),
                           bg="white", fg="green").place(x=2, y=5)

        label_search = Label(ProductFrame2, text="Product Name", font=("times new roman", 15, "bold"), bg="white").place(
            x=2, y=45)
        text_search = Entry(ProductFrame2, textvariable=self.var_search, font=("times new roman", 15),
                           bg="lightyellow").place(x=128, y=47, width=150, height=22)
        button_search = Button(ProductFrame2, text="Search", command=self.search, font=("goudy old style", 15),
                            bg="#2196f3", fg="white", cursor="hand2").place(x=285, y=45, width=100, height=25)
        button_show_all = Button(ProductFrame2, text="Show All", command=self.show, font=("goudy old style", 15),
                              bg="#083531", fg="white", cursor="hand2").place(x=285, y=10, width=100, height=25)

        ProductFrame3 = Frame(ProductFrame1, bd=3, relief=RIDGE)
        ProductFrame3.place(x=2, y=140, width=398, height=375)

        scrolly = Scrollbar(ProductFrame3, orient=VERTICAL)
        scrollx = Scrollbar(ProductFrame3, orient=HORIZONTAL)

        self.prod_Table = ttk.Treeview(ProductFrame3, columns=("pid", "name", "price", "qty", "status","discount"),
                                          yscrollcommand=scrolly.set, xscrollcommand=scrollx.set)
        scrolly.pack(side=RIGHT, fill=Y)
        scrolly.config(command=self.prod_Table.yview)
        scrollx.pack(side=BOTTOM, fill=X)
        scrollx.config(command=self.prod_Table.xview)
        self.prod_Table.pack(fill=BOTH, expand=1)

        self.prod_Table.heading("pid", text="P ID")
        self.prod_Table.heading("name", text="Name")
        self.prod_Table.heading("price", text="Price")
        self.prod_Table.heading("qty", text="Quantity")
        self.prod_Table.heading("status", text="Status")
        self.prod_Table.heading("discount", text="Discount")
        self.prod_Table["show"] = "headings"
        self.prod_Table.column("pid", width=40)
        self.prod_Table.column("name", width=140)
        self.prod_Table.column("price", width=100)
        self.prod_Table.column("qty", width=70)
        self.prod_Table.column("status", width=90)
        self.prod_Table.column("discount", width=90)
        self.prod_Table.bind("<ButtonRelease-1>", self.get_data)
        self.show()

        label_note = Label(ProductFrame1, text="Note: 'Enter 0 Quantity to remove product from the Cart'",font=("goudy old style", 12), anchor="w", bg="white", fg="red").pack(side=BOTTOM, fill=X)

        self.var_cname = StringVar()
        self.var_contact = StringVar()

        CustomerFrame = Frame(self.root, bd=4, relief=RIDGE, bg="white")
        CustomerFrame.place(x=420, y=110, width=530, height=70)

        cust_Title = Label(CustomerFrame, text="Customer Details", font=("goudy old style", 15), bg="lightgray").pack(side=TOP, fill=X)

        label_name = Label(CustomerFrame, text="Name", font=("times new roman", 15), bg="white").place(x=5, y=35)
        text_name = Entry(CustomerFrame, textvariable=self.var_cname, font=("times new roman", 13),bg="lightyellow").place(x=80, y=35, width=180)

        label_contact = Label(CustomerFrame, text="Contact No.", font=("times new roman", 15), bg="white").place(x=270,y=35)
        text_contact = Entry(CustomerFrame, textvariable=self.var_contact, font=("times new roman", 15),bg="lightyellow").place(x=380, y=35, width=140)

        Cal_Cart_Frame = Frame(self.root, bd=2, relief=RIDGE, bg="white")
        Cal_Cart_Frame.place(x=420, y=190, width=530, height=360)

        self.var_cal_input = StringVar()

        Cal_Frame = Frame(Cal_Cart_Frame, bd=9, relief=RIDGE, bg="white")
        Cal_Frame.place(x=5, y=10, width=268, height=340)

        self.text_cal_input = Entry(Cal_Frame, textvariable=self.var_cal_input, font=('arial', 15, 'bold'), width=21,
                                   bd=10, relief=GROOVE, state='readonly', justify=RIGHT)
        self.text_cal_input.grid(row=0, columnspan=4)

        buttn_7 = Button(Cal_Frame, text=7, font=('arial', 15, 'bold'), command=lambda: self.get_input(7), bd=5, width=4,
                       pady=10, cursor="hand2").grid(row=1, column=0)
        buttn_8 = Button(Cal_Frame, text=8, font=('arial', 15, 'bold'), command=lambda: self.get_input(8), bd=5, width=4,
                       pady=10, cursor="hand2").grid(row=1, column=1)
        buttn_9 = Button(Cal_Frame, text=9, font=('arial', 15, 'bold'), command=lambda: self.get_input(9), bd=5, width=4,
                       pady=10, cursor="hand2").grid(row=1, column=2)
        buttn_sum = Button(Cal_Frame, text="+", font=('arial', 15, 'bold'), command=lambda: self.get_input('+'), bd=5,
                         width=4, pady=10, cursor="hand2").grid(row=1, column=3)

        buttn_4 = Button(Cal_Frame, text=4, font=('arial', 15, 'bold'), command=lambda: self.get_input(4), bd=5, width=4,
                       pady=10, cursor="hand2").grid(row=2, column=0)
        buttn_5 = Button(Cal_Frame, text=5, font=('arial', 15, 'bold'), command=lambda: self.get_input(5), bd=5, width=4,
                       pady=10, cursor="hand2").grid(row=2, column=1)
        buttn_6 = Button(Cal_Frame, text=6, font=('arial', 15, 'bold'), command=lambda: self.get_input(6), bd=5, width=4,
                       pady=10, cursor="hand2").grid(row=2, column=2)
        buttn_sub = Button(Cal_Frame, text="-", font=('arial', 15, 'bold'), command=lambda: self.get_input('-'), bd=5,
                         width=4, pady=10, cursor="hand2").grid(row=2, column=3)

        buttn_1 = Button(Cal_Frame, text=1, font=('arial', 15, 'bold'), command=lambda: self.get_input(1), bd=5, width=4,
                       pady=10, cursor="hand2").grid(row=3, column=0)
        buttn_2 = Button(Cal_Frame, text=2, font=('arial', 15, 'bold'), command=lambda: self.get_input(2), bd=5, width=4,
                       pady=10, cursor="hand2").grid(row=3, column=1)
        buttn_3 = Button(Cal_Frame, text=3, font=('arial', 15, 'bold'), command=lambda: self.get_input(3), bd=5, width=4,
                       pady=10, cursor="hand2").grid(row=3, column=2)
        buttn_mul = Button(Cal_Frame, text="*", font=('arial', 15, 'bold'), command=lambda: self.get_input('*'), bd=5,
                         width=4, pady=10, cursor="hand2").grid(row=3, column=3)

        buttn_0 = Button(Cal_Frame, text=0, font=('arial', 15, 'bold'), command=lambda: self.get_input(0), bd=5, width=4,
                       pady=15, cursor="hand2").grid(row=4, column=0)
        buttn_c = Button(Cal_Frame, text="C", font=('arial', 15, 'bold'), command=self.clear_cal, bd=5, width=4, pady=15,
                       cursor="hand2").grid(row=4, column=1)
        buttn_eq = Button(Cal_Frame, text="=", font=('arial', 15, 'bold'), command=self.perform_cal, bd=5, width=4,
                        pady=15, cursor="hand2").grid(row=4, column=2)
        buttn_div = Button(Cal_Frame, text="/", font=('arial', 15, 'bold'), command=lambda: self.get_input('/'), bd=5,
                         width=4, pady=15, cursor="hand2").grid(row=4, column=3)
        #======CART FRAME=======
        Cart_Frame = Frame(Cal_Cart_Frame, bd=3, relief=RIDGE)
        Cart_Frame.place(x=280, y=8, width=245, height=342)
        self.cartTitle = Label(Cart_Frame, text="Cart \t Total Products: [0]", font=("goudy old style", 15),
                               bg="lightgray")
        self.cartTitle.pack(side=TOP, fill=X)

        scrolly = Scrollbar(Cart_Frame, orient=VERTICAL)
        scrollx = Scrollbar(Cart_Frame, orient=HORIZONTAL)

        self.CartTable = ttk.Treeview(Cart_Frame, columns=("pid", "name", "price", "qty"),
                                              yscrollcommand=scrolly.set, xscrollcommand=scrollx.set)
        scrollx.pack(side=BOTTOM, fill=X)
        scrolly.pack(side=RIGHT, fill=Y)
        scrollx.config(command=self.CartTable.xview)
        scrolly.config(command=self.CartTable.yview)
        self.CartTable.heading("pid", text="P ID")
        self.CartTable.heading("name", text="Name")
        self.CartTable.heading("price", text="Price")
        self.CartTable.heading("qty", text="Quantity")
        self.CartTable["show"] = "headings"
        self.CartTable.column("pid", width=40)
        self.CartTable.column("name", width=100)
        self.CartTable.column("price", width=90)
        self.CartTable.column("qty", width=70)
        self.CartTable.pack(fill=BOTH, expand=1)
        self.CartTable.bind("<ButtonRelease-1>", self.get_data_cart)

        # -------------- add cart widgets frame ---------------
        self.var_pid = StringVar()
        self.var_pname = StringVar()
        self.var_price = StringVar()
        self.var_qty = StringVar()
        self.var_stock = StringVar()

        Add_CartWidgets_Frame = Frame(self.root, bd=2, relief=RIDGE, bg="white")
        Add_CartWidgets_Frame.place(x=420, y=550, width=530, height=110)

        label_p_name = Label(Add_CartWidgets_Frame, text="Product Name", font=("times new roman", 15), bg="white").place(
            x=5, y=5)
        text_p_name = Entry(Add_CartWidgets_Frame, textvariable=self.var_pname, font=("times new roman", 15),
                           bg="lightyellow", state='readonly').place(x=5, y=35, width=190, height=22)

        label_p_price = Label(Add_CartWidgets_Frame, text="Price Per Qty", font=("times new roman", 15),
                            bg="white").place(x=230, y=5)
        text_p_price = Entry(Add_CartWidgets_Frame, textvariable=self.var_price, font=("times new roman", 15),
                            bg="lightyellow", state='readonly').place(x=230, y=35, width=150, height=22)

        label_p_qty = Label(Add_CartWidgets_Frame, text="Quantity", font=("times new roman", 15), bg="white").place(x=390,
                                                                                                                  y=5)
        text_p_qty = Entry(Add_CartWidgets_Frame, textvariable=self.var_qty, font=("times new roman", 15),
                          bg="lightyellow").place(x=390, y=35, width=120, height=22)

        self.lbl_inStock = Label(Add_CartWidgets_Frame, text="In Stock", font=("times new roman", 15), bg="white")
        self.lbl_inStock.place(x=5, y=70)

        bttn_clear_cart = Button(Add_CartWidgets_Frame, command=self.clear_cart, text="Clear",
                                font=("times new roman", 15, "bold"), bg="lightgray", cursor="hand2").place(x=180, y=70,
                                                                                                            width=150,
                                                                                                            height=30)
        bttn_add_cart = Button(Add_CartWidgets_Frame, command=self.add_update_cart, text="Add | Update",
                              font=("times new roman", 15, "bold"), bg="orange", cursor="hand2").place(x=340, y=70,
                                                                                                       width=180,
                                                                                                       height=30)

        # ------------------- billing area -------------------
        billFrame = Frame(self.root, bd=2, relief=RIDGE, bg="white")
        billFrame.place(x=953, y=110, width=400, height=410)

        B_Title = Label(billFrame, text="Customer Bill Area", font=("goudy old style", 20, "bold"), bg="#262626",
                       fg="white").pack(side=TOP, fill=X)
        scrolly = Scrollbar(billFrame, orient=VERTICAL)
        scrolly.pack(side=RIGHT, fill=Y)

        self.txt_bill_area = Text(billFrame, yscrollcommand=scrolly.set)
        self.txt_bill_area.pack(fill=BOTH, expand=1)
        scrolly.config(command=self.txt_bill_area.yview)

        # ---------------- billing buttons -------------------
        billMenuFrame = Frame(self.root, bd=2, relief=RIDGE, bg="white")
        billMenuFrame.place(x=953, y=520, width=400, height=140)

        self.lbl_ammnt = Label(billMenuFrame, text="Bill Amount\n[0]", font=("goudy old style", 15, "bold"),
                              bg="#3f51b5", fg="white")
        self.lbl_ammnt.place(x=2, y=5, width=120, height=70)

        self.label_discount = Label(billMenuFrame, text="Discount", font=("goudy old style", 15, "bold"),
                                  bg="#8bc34a", fg="white")
        self.label_discount.place(x=124, y=5, width=120, height=70)

        self.label_net_pay = Label(billMenuFrame, text="Net Pay\n[0]", font=("goudy old style", 15, "bold"), bg="#607d8b",
                                 fg="white")
        self.label_net_pay.place(x=246, y=5, width=160, height=70)

        bttn_print = Button(billMenuFrame, text="Print", command=self.print_bill, cursor="hand2",
                           font=("goudy old style", 15, "bold"), bg="lightgreen", fg="white")
        bttn_print.place(x=2, y=80, width=120, height=50)

        bttn_clear_all = Button(billMenuFrame, text="Clear All", command=self.clear_all, cursor="hand2",
                               font=("goudy old style", 15, "bold"), bg="gray", fg="white")
        bttn_clear_all.place(x=124, y=80, width=120, height=50)

        bttn_generate = Button(billMenuFrame, text="Generate Bill", command=self.generate_bill, cursor="hand2",
                              font=("goudy old style", 15, "bold"), bg="#009688", fg="white")
        bttn_generate.place(x=246, y=80, width=160, height=50)

        self.show()
        # self.bill_top()
        self.update_date_time()

#------------------ all functions ----------------------

    def get_input(self,num):
        xnum=self.var_cal_input.get()+str(num)
        self.var_cal_input.set(xnum)

    def clear_cal(self):
        self.var_cal_input.set('')

    def perform_cal(self):
        result=self.var_cal_input.get()
        self.var_cal_input.set(eval(result))

    def show(self):
        connection = pymysql.connect(host="localhost", user="root", password="1234")
        cursor = connection.cursor()
        if not cursor or not connection:
            return
        cursor.execute('use inventory_system')
        try:
            cursor.execute("select id,name,price,quantity,status,discount from product_data where status='Active'")
            rows=cursor.fetchall()
            self.prod_Table.delete(*self.prod_Table.get_children())
            for row in rows:
                self.prod_Table.insert('',END,values=row)
        except Exception as ex:
            messagebox.showerror("Error",f"Error due to : {str(ex)}")

    def search(self):
        connection = pymysql.connect(host="localhost", user="root", password="1234")
        cursor = connection.cursor()
        if not cursor or not connection:
            return
        cursor.execute('use inventory_system')
        try:
            if self.var_search.get()=="":
                messagebox.showerror("Error","Search input should be required",parent=self.root)
            else:
                cursor.execute("select id,name,price,quantity,status,discount from product_data where name LIKE '%"+self.var_search.get()+"%'")
                rows=cursor.fetchall()
                if len(rows)!=0:
                    self.prod_Table.delete(*self.prod_Table.get_children())
                    for row in rows:
                        self.prod_Table.insert('',END,values=row)
                else:
                    messagebox.showerror("Error","No record found!!!",parent=self.root)
        except Exception as ex:
            messagebox.showerror("Error",f"Error due to : {str(ex)}")

    def get_data(self,ev):
        f=self.prod_Table.focus()
        content=(self.prod_Table.item(f))
        row=content['values']
        self.var_pid.set(row[0])
        self.var_pname.set(row[1])
        self.var_price.set(row[2])
        self.lbl_inStock.config(text=f"In Stock [{str(row[3])}]")
        self.var_stock.set(row[3])
        self.var_qty.set('1')

    def get_data_cart(self,ev):
        f=self.CartTable.focus()
        content=(self.CartTable.item(f))
        row=content['values']
        self.var_pid.set(row[0])
        self.var_pname.set(row[1])
        self.var_price.set(row[2])
        self.var_qty.set(row[3])
        self.lbl_inStock.config(text=f"In Stock [{str(row[4])}]")
        self.var_stock.set(row[4])

    def add_update_cart(self):
        if self.var_pid.get()=="":
            messagebox.showerror("Error","Please select product from the list",parent=self.root)
        elif self.var_qty.get()=="":
            messagebox.showerror("Error","Quantity is required",parent=self.root)
        elif int(self.var_qty.get())>int(self.var_stock.get()):
            messagebox.showerror("Error","Invalid Quantity",parent=self.root)
        else:
            #price_cal=int(self.var_qty.get())*float(self.var_price.get())
            #price_cal=float(price_cal)
            price_cal=self.var_price.get()
            cart_data=[self.var_pid.get(),self.var_pname.get(),price_cal,self.var_qty.get(),self.var_stock.get()]
            #---------- update cart --------------
            present="no"
            index_=0
            for row in self.cart_list:
                if self.var_pid.get()==row[0]:
                    present="yes"
                    break
                index_+=1
            if present=="yes":
                op=messagebox.askyesno("Confirm","Product already present\nDo you want to Update|Remove from the Cart List",parent=self.root)
                if op==True:
                    if self.var_qty.get()=="0":
                        self.cart_list.pop(index_)
                    else:
                        #self.cart_list[index_][2]=price_cal
                        self.cart_list[index_][3]=self.var_qty.get()
            else:
                self.cart_list.append(cart_data)
            self.show_cart()
            self.bill_update()

    def bill_update(self):
        self.bill_amnt=0
        self.net_pay=0
        self.siscount=0
        for row in self.cart_list:
            self.bill_amnt=self.bill_amnt+(float(row[2])*int(row[3]))
        self.discount=(self.bill_amnt*5)/100
        self.net_pay=self.bill_amnt-self.discount
        self.lbl_ammnt.config(text=f"Bill Amnt\n{str(self.bill_amnt)}")
        self.label_net_pay.config(text=f"Net Pay\n{str(self.net_pay)}")
        self.cartTitle.config(text=f"Cart \t Total Products: [{str(len(self.cart_list))}]")

    def show_cart(self):
        try:
            self.CartTable.delete(*self.CartTable.get_children())
            for row in self.cart_list:
                self.CartTable.insert('', END, values=row)
        except Exception as ex:
            messagebox.showerror("Error", f"Error due to : {str(ex)}")

    def generate_bill(self):
        if self.var_cname.get() == "" or self.var_contact.get() == "":
            messagebox.showerror("Error", f"Customer Details are required", parent=self.root)
        elif len(self.cart_list) == 0:
            messagebox.showerror("Error", f"Please Add product to the Cart!!!", parent=self.root)

        elif self.validate_contact():

            # Insert customer details into the customer table
            connection = pymysql.connect(host="localhost", user="root", password="1234", db="inventory_system")
            cursor = connection.cursor()
            cursor.execute("INSERT INTO customer (customer_name, contact_number) VALUES (%s, %s)",
                           (self.var_cname.get(), self.var_contact.get()))
            customer_id = cursor.lastrowid
            connection.commit()

            # --------- bill top -----------------
            self.bill_top()
            # --------- bill middle --------------
            self.bill_middle()
            # --------- bill bottom --------------
            self.bill_bottom()

            # Insert billing details into the billing table
            cursor.execute(
                "INSERT INTO billing (customer_id, bill_date, bill_amount, discount, net_pay) VALUES (%s, %s, %s, %s, %s)",
                (customer_id, time.strftime("%Y-%m-%d"), self.bill_amnt, self.discount, self.net_pay))
            connection.commit()
            connection.close()

            fp = open(f'C:/Users/Dell/PycharmProjects/inventry system/bill/{str(self.invoice)}.txt', 'w')
            fp.write(self.txt_bill_area.get('1.0', END))
            fp.close()
            messagebox.showinfo("Saved", "Bill has been generated", parent=self.root)
            self.chk_print = 1
            try:
                con = pymysql.connect(host="localhost", user="root", password="1234", database="inventory_system")
                cur = con.cursor()
                for item in self.cart_list: pid = item[0]
                pname = item[1]
                price = float(item[2])
                qty = int(item[3])
                total = price * qty

                # Get category from product_data
                cur.execute("SELECT category FROM product_data WHERE id = %s", (pid,))
                cat_row = cur.fetchone()
                category = cat_row[0] if cat_row else "Unknown"

                cur.execute("""
                        INSERT INTO sales_data (invoice_no, product_name, category, quantity, price_per_unit, total_price)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (self.invoice, pname, category, qty, price, total))

                con.commit()
                con.close()

            except Exception as e: messagebox.showerror("Database Error", f"Could not save sales record:\n{str(e)}",
                                                        parent=self.root)
        else:
            return

    def bill_top(self):
        self.invoice=int(time.strftime("%H%M%S"))+int(time.strftime("%d%m%Y"))
        bill_top_temp=f'''
\t\tXYZ-Inventory
\t Phone No. 8299126801 , Delhi-110053
{str("="*46)}
 Customer Name: {self.var_cname.get()}
 Ph. no. : {self.var_contact.get()}
 Bill No. {str(self.invoice)}\t\t\tDate: {str(time.strftime("%d/%m/%Y"))}
{str("="*46)}
 Product Name\t\t\tQTY\tPrice
{str("="*46)}
'''
        self.txt_bill_area.delete('1.0',END)
        self.txt_bill_area.insert('1.0',bill_top_temp)

    def bill_bottom(self):
        bill_bottom_temp=f'''
{str("="*46)}
 Bill Amount\t\t\t\tRs.{self.bill_amnt}
 Discount\t\t\t\tRs.{self.discount}
 Net Pay\t\t\t\tRs.{self.net_pay}
{str("="*46)}\n
'''
        self.txt_bill_area.insert(END,bill_bottom_temp)

    def bill_middle(self):
        connection = pymysql.connect(host="localhost", user="root", password="1234")
        cursor = connection.cursor()
        if not cursor or not connection:
            return
        cursor.execute('use inventory_system')
        try:
            for row in self.cart_list:
                pid=row[0]
                name=row[1]
                qty=int(row[4])-int(row[3])
                if int(row[3])==int(row[4]):
                    status="Inactive"
                if int(row[3])!=int(row[4]):
                    status="Active"
                price=float(row[2])*int(row[3])
                price=str(price)
                self.txt_bill_area.insert(END,"\n "+name+"\t\t\t"+row[3]+"\tRs."+price)
                #------------- update qty in product table --------------
                cursor.execute("update product_data set quantity=%s,status=%s where id=%s",(
                    qty,
                    status,
                    pid
                ))
                connection.commit()
            connection.close()
            self.show()
        except Exception as ex:
            messagebox.showerror("Error",f"Error due to : {str(ex)}",parent=self.root)

    def clear_cart(self):
        self.var_pid.set("")
        self.var_pname.set("")
        self.var_price.set("")
        self.var_qty.set("")
        self.lbl_inStock.config(text=f"In Stock")
        self.var_stock.set("")

    def clear_all(self):
        del self.cart_list[:]
        self.clear_cart()
        self.show()
        self.show_cart()
        self.var_cname.set("")
        self.var_contact.set("")
        self.chk_print = 0
        self.txt_bill_area.delete('1.0', END)
        self.cartTitle.config(text=f"Cart \t Total Products: [0]")
        self.var_search.set("")

    def update_date_time(self):
        time_ = time.strftime("%I:%M:%S")
        date_ = time.strftime("%d-%m-%Y")
        self.label_clock.config(
            text=f"Welcome to Inventory Tracking & Monitoring\t\t Date: {str(date_)}\t\t Time: {str(time_)}")
        self.label_clock.after(200, self.update_date_time)

    def print_bill(self):
        if self.chk_print==1:
            messagebox.showinfo("Print","Please wait while printing",parent=self.root)
            new_file=tempfile.mktemp('.txt')
            open(new_file,'w').write(self.txt_bill_area.get('1.0',END))
            os.startfile(new_file,'print')
        else:
            messagebox.showinfo("Print","Please generate bill to print the receipt",parent=self.root)


    def logout(self):
        self.root.destroy()
        import login
if __name__=="__main__":
    root=Tk()
    obj=billClass(root)
    root.mainloop()

