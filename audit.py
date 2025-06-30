import pymysql
from tkinter import *
from tkinter import messagebox, ttk, Toplevel

def customize_treeview():
    style = ttk.Style()
    style.theme_use('default')
    style.configure("Custom.Treeview")
    style.map('Custom.Treeview', background=[('selected', '#f7b2b7')])

def insert_audit_log(user, action_type, module, description):
    try:
        con = pymysql.connect(host="localhost", user="root", password="1234", database="inventory_system")
        cur = con.cursor()
        cur.execute("INSERT INTO audit_log (user, action_type, module, description) VALUES (%s, %s, %s, %s)", (user, action_type, module, description))
        con.commit()
        con.close()
    except Exception as e:
        messagebox.showerror('Error', f'Error due to {e}')

def show_audit_logs(window):
    log_win=Toplevel(window)
    log_win.title("Audit Logs")
    log_win.geometry("1100x500")
    log_win.config(bg='#FFE5B4')

    treeview_frame = Frame(log_win, bg="yellow")
    treeview_frame.place(x=50, y=30, height=450, width=1000)
    tree = ttk.Treeview(treeview_frame, columns=("ID", "User", "Action", "Module", "Desc", "Time"), show='headings',style="Custom.Treeview")
    for col in tree["columns"]:
        tree.heading(col, text=col)
        tree.column(col, width=160)
    tree.pack(fill= BOTH,expand=True)

    try:
        con = pymysql.connect(host="localhost", user="root", password="1234", database="inventory_system")
        cur = con.cursor()
        cur.execute("SELECT * FROM audit_log ORDER BY id DESC LIMIT 100")
        rows = cur.fetchall()
        con.close()

        for row in rows:
            tree.insert('', END, values=row)

    except Exception as e:
        messagebox.showerror('Error', f'Error due to {e}')

