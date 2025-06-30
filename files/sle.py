from tkinter import *
from PIL import Image, ImageTk
from tkinter import ttk, messagebox,filedialog
import os
import matplotlib.pyplot as plt
from tkcalendar import DateEntry
import pymysql
from openpyxl import Workbook

def export_sales_to_excel():
    try:
        con = pymysql.connect(host="localhost", user="root", password="1234", database="inventory_system")
        cur = con.cursor()
        cur.execute("SELECT * FROM sales_data")  # Adjust column names as needed
        data = cur.fetchall()
        col_names = [i[0] for i in cur.description]
        con.close()

        if not data:
            messagebox.showinfo("No Data", "No sales records to export.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                                 filetypes=[("Excel files", "*.xlsx")],
                                                 title="Save Sales Report")
        if file_path:
            wb = Workbook()
            ws = wb.active
            ws.title = "Sales"

            ws.append(col_names)

            for row in data:
                ws.append(row)

            wb.save(file_path)
            messagebox.showinfo("Success", f"Sales data exported to {file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to export: {e}")


def sales_form(window):
    global back_image
    sales_frame = Frame(window, width=1175, height=1200,background='#FFE5B4')
    sales_frame.place(x=200, y=100)
    # Create sales form widgets here...
    lbl_title = Label(sales_frame, text="View Customer Bills", font=("goudy old style", 30), bg="#2c3e50", fg="white",
                      bd=3, relief=RIDGE)
    lbl_title.place(x=0, y=0, width=1170, height=60)
    back_image = PhotoImage(file="../images/back.png")
    back_button = Button(sales_frame, image=back_image, bd=0, cursor='hand2',
                         command=lambda: sales_frame.place_forget())
    back_button.place(x=10, y=70)
    # Invoice No.
    lbl_invoice = Label(sales_frame, text="Invoice No.", font=("times new roman", 15),background='#FFE5B4')
    lbl_invoice.place(x=50, y=100)
    var_invoice = StringVar()
    txt_invoice = Entry(sales_frame, textvariable=var_invoice, font=("times new roman", 15), bg="lightyellow")
    txt_invoice.place(x=160, y=100, width=180, height=28)

    def sales_report_section(window):
        report_win = Toplevel(window)
        report_win.title("Sales Reports")
        report_win.geometry("900x600")
        report_win.config(bg="#f4f4f4")
        report_win.grab_set()

        Label(report_win, text="Sales Reports", font=("Arial", 18, "bold"), bg="#f4f4f4").pack(pady=10)

        # Filters
        filter_frame = Frame(report_win, bg="#f4f4f4")
        filter_frame.pack(pady=10)

        Label(filter_frame, text="From:", font=("Arial", 12), bg="#f4f4f4").grid(row=0, column=0, padx=5)
        from_date = DateEntry(filter_frame, width=12, font=("Arial", 12))
        from_date.grid(row=0, column=1, padx=5)

        Label(filter_frame, text="To:", font=("Arial", 12), bg="#f4f4f4").grid(row=0, column=2, padx=5)
        to_date = DateEntry(filter_frame, width=12, font=("Arial", 12))
        to_date.grid(row=0, column=3, padx=5)

        def fetch_data():
            try:
                con = pymysql.connect(host="localhost", user="root", password="1234", database="inventory_system")
                cur = con.cursor()
                query = "SELECT invoice_no, product_name, category, quantity, total_price, sale_date FROM sales_data WHERE sale_date BETWEEN %s AND %s"
                cur.execute(query, (from_date.get_date(), to_date.get_date()))
                data = cur.fetchall()
                con.close()

                report_tree.delete(*report_tree.get_children())
                for row in data:
                    report_tree.insert('', END, values=row)

            except Exception as e:
                messagebox.showerror("Error", f"Failed to fetch report: {e}")

        def export_excel():
            try:
                file_path = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                                         filetypes=[("Excel files", "*.xlsx")],
                                                         title="Save Report File")
                if not file_path:
                    return
                wb = Workbook()
                ws = wb.active
                ws.title = "Sales Report"
                ws.append(["Invoice No", "Product Name", "Category", "Quantity", "Total Price", "Date"])

                for row in report_tree.get_children():
                    ws.append(report_tree.item(row)["values"])

                wb.save(file_path)
                messagebox.showinfo("Success", f"Report exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {e}")

        def show_charts():
            try:
                con = pymysql.connect(host="localhost", user="root", password="1234", database="inventory_system")
                cur = con.cursor()
                query = "SELECT category, SUM(quantity) FROM sales_data WHERE sale_date BETWEEN %s AND %s GROUP BY category"
                cur.execute(query, (from_date.get_date(), to_date.get_date()))
                data = cur.fetchall()
                con.close()

                if not data:
                    messagebox.showinfo("No Data", "No sales data found.")
                    return

                categories = [row[0] for row in data]
                totals = [row[1] for row in data]

                plt.figure(figsize=(8, 5))
                plt.bar(categories, totals, color="skyblue")
                plt.title("Sales by Category")
                plt.xlabel("Category")
                plt.ylabel("Total Sales (Quantity)")
                plt.tight_layout()
                plt.show()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to show chart: {e}")

        Button(filter_frame, text="Generate Report", font=("Arial", 12), bg="#3CB371", fg="white",
               command=fetch_data).grid(row=0, column=4, padx=10)
        Button(filter_frame, text="Export to Excel", font=("Arial", 12), bg="#2c3e50", fg="white",
               command=export_excel).grid(row=0, column=5, padx=10)
        Button(filter_frame, text="Show Report Chart", font=("Arial", 12), bg="#4682B4", fg="white",
               command=show_charts).grid(row=0, column=6, padx=10)

        # Report Table
        table_frame = Frame(report_win, bg="#f4f4f4")
        table_frame.pack(pady=10, fill=BOTH, expand=True)

        report_tree = ttk.Treeview(table_frame, columns=("Invoice", "Product", "Category", "Qty", "Total", "Date"),
                                   show='headings')
        report_tree.heading("Invoice", text="Invoice No")
        report_tree.heading("Product", text="Product Name")
        report_tree.heading("Category", text="Category")
        report_tree.heading("Qty", text="Quantity")
        report_tree.heading("Total", text="Total Price")
        report_tree.heading("Date", text="Date")

        report_tree.pack(fill=BOTH, expand=True)



    # Search and Clear buttons
    bill_list = []
    def search():
        global bill_list
        nonlocal var_invoice
        nonlocal bill_area

        if var_invoice.get() == "":
                messagebox.showerror("Error", "Invoice no. is  required")
        else:
            if var_invoice.get() + '.txt' in os.listdir('/bill'):
                fp = open(f'C:/Users/Dell/PycharmProjects/inventry system/bill/{var_invoice.get()}.txt', 'r')
                bill_area.delete('1.0', END)
                for i in fp:
                    bill_area.insert(END, i)
                fp.close()
            else:
                messagebox.showerror("Error", "Invalid Invoice No.")

    def clear():
        show(sales_list)
        bill_area.delete('1.0', END)

    def get_data(event,sales_list, bill_area):
        index_=sales_list.curselection()
        if index_:
            file_name = sales_list.get(index_)
            bill_area.delete('1.0', END)
            fp = open(f'C:/Users/Dell/PycharmProjects/inventry system/bill/{file_name}', 'r')
            for i in fp:
                bill_area.insert(END, i)
            fp.close()
    def show(sales_list):
        nonlocal bill_list
        sales_list.delete(0,END)
        for i in os.listdir('/bill'):
            if i.split('.')[-1]=='txt':
                sales_list.insert(END,i)
                bill_list.append(i.split('.')[0])

    btn_search = Button(sales_frame, text="Search", command=search, font=("times new roman", 15, "bold"), bg="#2c3e50",
                        fg="white", cursor="hand2")
    btn_search.place(x=360, y=100, width=120, height=28)
    btn_clear = Button(sales_frame, text="Clear", command=clear, font=("times new roman", 15, "bold"), bg="lightgray",
                       cursor="hand2")
    btn_clear.place(x=490, y=100, width=120, height=28)


    # Bill list and bill area
    salesb_Frame = Frame(sales_frame, bd=3, relief=RIDGE,background='#FFE5B4')
    salesb_Frame.place(x=50, y=140, width=200, height=330)
    scrolly = Scrollbar(salesb_Frame, orient=VERTICAL)
    sales_list = Listbox(salesb_Frame, font=("goudy old style", 15),background='#FFE0A3', yscrollcommand=scrolly.set)
    scrolly.pack(side=RIGHT, fill=Y)
    scrolly.config(command=sales_list.yview)
    sales_list.pack(fill=BOTH, expand=1)

    sales_button_Frame = Frame(sales_frame, background='#FFE5B4')
    sales_button_Frame.place(x=50, y=500, width=400, height=100)

    Button(sales_button_Frame, text='Export Sales', font=('times new roman', 15, 'bold'), bg="#2c3e50",
                        fg="white",activebackground='#3CB371', command=export_sales_to_excel).place(x=2,y=10)

    #from sales import sales_report_section

    sales_report_button = Button(sales_button_Frame, text='Sales Report', font=('times new roman', 15, 'bold'),
                                 bg="#2c3e50",fg="white", activebackground='#3CB371', command=lambda: sales_report_section(window))
    sales_report_button.place(x=150,y=10)

    bill_Frame = Frame(sales_frame, bd=3, relief=RIDGE,background='#FFE5B4')
    bill_Frame.place(x=280, y=140, width=410, height=330)
    lbl_title2 = Label(bill_Frame, text="Customer Bill Area", font=("goudy old style", 20), bg="orange")
    lbl_title2.pack(side=TOP, fill=X)
    scrolly2 = Scrollbar(bill_Frame, orient=VERTICAL)
    bill_area = Text(bill_Frame, bg="lightyellow", yscrollcommand=scrolly2.set)
    scrolly2.pack(side=RIGHT, fill=Y)
    scrolly2.config(command=bill_area.yview)
    bill_area.pack(fill=BOTH, expand=1)

    show(sales_list)
    sales_list.bind("<ButtonRelease-1>", lambda event: get_data(event, sales_list, bill_area))


    # Image
    image = Image.open("../images/cat2.png")
    image = image.resize((450, 300))
    bill_photo = ImageTk.PhotoImage(image)
    lbl_image = Label(sales_frame, image=bill_photo, bd=0,background='#FFE5B4')
    lbl_image.image = bill_photo
    lbl_image.place(x=700, y=150)






