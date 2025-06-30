import time
from tkinter import *
from tkinter import messagebox
from PIL import ImageTk
import pymysql

from files import email_pass


class Login_System:
    def __init__(self,root):
        self.root=root
        self.root.title("Login System")
        self.root.geometry('1450x700+0+0')
        self.root.config(bg="#e6f7ff")
        self.bg_cover = Frame(self.root, bg="#e6f7ff")
        self.bg_cover.place(x=0, y=0, relwidth=1,relheight = 1)
        self.otp=''

        #============image======

        self.phone_image = PhotoImage(file="../images/phone.png")
        self.lbl_Phone_image=Label(self.root,image=self.phone_image,bd=0).place(x=200,y=50)

        #=========LOGINFRAME=========================
        self.employee_id = StringVar()
        self.password = StringVar()

        login_frame = Frame(self.root,bd=2,relief=RIDGE,bg="white",highlightbackground='#dce1e6',
                 highlightthickness=2)
        login_frame.place(x=650,y=90,width=350,height=460)

        title=Label(login_frame,text="Login System",font=("Elephant",30,"bold"),bg="white").place(x=0,y=30,relwidth=1)
        lbl_user=Label(login_frame,text="Employee ID",font=("Andalus",15),bg="white",fg="#767171").place(x=50,y=100)

        txt_employee_id=Entry(login_frame,textvariable=self.employee_id,font=("times new roman",15),bg="#ECECEC").place(x=50,y=140,width=250)

        lbl_pass = Label(login_frame, text="Password", font=("Andalus", 15), bg="white", fg="#767171").place(x=50,y=200)
        txt_pass = Entry(login_frame,textvariable=self.password, font=("times new roman", 15), bg="#ECECEC",show="*").place(x=50, y=240, width=250)

        btn_login = Button(login_frame,command=self.login, text ="Log In",font=("Arial Rounded MT Bold",15),bg="#007BFF",activebackground="#0056B3",fg="white",activeforeground="white",cursor="hand2").place(x=50,y=300,width=250,height=35)
        hr=Label(login_frame,bg="lightgray").place(x=50,y=370,width=250,height=2)
        or_lbl=Label(login_frame,text="OR",bg="white",fg="lightgray",font=("times new roman",15,"bold")).place(x=150, y=355)

        btn_forget=Button(login_frame,text="Forget Password?",font=("times new roman",13),bg="white",fg="#00759E",bd=0,activebackground="white",activeforeground="#00759E",command=self.forget_window).place(x=100,y=390)
        #=========frame2===================
        #register_frame = Frame(self.root, bd=2, relief=RIDGE, bg="white")
        #register_frame.place(x=650, y=570, width=350, height=60)

        #lbl_reg = Label(register_frame, text = "SUBSCRIBE|LIKE|SHARE", font=("times new roman", 13), bg = "white").place(x=0, y=20,relwidth=1)
        self.im1=ImageTk.PhotoImage(file="../images/im1.png")
        self.im2 = ImageTk.PhotoImage(file="../images/im2.png")
        self.im3 = ImageTk.PhotoImage(file="../images/im3.png")


        self.lbl_change_image=Label(self.root,bg=self.root['bg'])
        self.lbl_change_image.place(x=367,y=153,width=240,height=428)
        self.animate()
#==========ALL FUNCTIONS =======================================
    def animate(self):
        self.im=self.im1
        self.im1=self.im2
        self.im2=self.im3
        self.im3=self.im
        self.lbl_change_image.config(image=self.im)
        self.lbl_change_image.after(900,self.animate)

    def login(self):
        try:
            connection = pymysql.connect(host="localhost", user="root", password="1234")
            cursor = connection.cursor()
            if not cursor or not connection:
                return
            cursor.execute('use inventory_system')
            try:
                if self.employee_id.get()=="" or self.password.get()=="":
                    messagebox.showerror("ERROR","All Fields Are Required",parent=self.root)

                else:
                    cursor.execute('SELECT usertype from employee_data where empid=%s AND password=%s',(self.employee_id.get(),self.password.get()))
                    user = cursor.fetchone()
                    if user==None:
                        messagebox.showerror("ERROR", "Invalid username or password", parent=self.root)
                    else:
                        if user[0] =="Admin":
                            self.root.destroy()
                            import os
                            os.system('python Dashboard.py')
                            emp_id = self.employee_id.get()

                            try:
                                con = pymysql.connect(host="localhost", user="root", password="1234",
                                                       database="inventory_system")
                                cur = con.cursor()

                            # Optional: Fetch employee name
                                cur.execute("SELECT name FROM employee_data WHERE empid = %s", (emp_id,))
                                emp = cur.fetchone()
                                emp_name = emp[0] if emp else "Unknown"

                                # Insert audit log
                                cur.execute(
                                    "INSERT INTO audit_log (user, action_type, module, description) VALUES (%s, %s, %s, %s)",
                                    (f"({emp_id})", "login", "Authentication",
                                     f"Employee {emp_name} (ID {emp_id}) logged in."))
                                con.commit()
                                con.close()
                            except Exception as e:
                                messagebox.showerror('Error', f'Error due to {e}')
                        else:
                            self.root.destroy()
                            import os
                            os.system('python Billing.py')



            except Exception as e:
                messagebox.showerror('Error', f'Error due to {e}')
            finally:
                cursor.close()
                connection.close()
        except:
            messagebox.showerror("Error", "Database connectivity issue try again, please open mysql command line client")
            return None, None
        return cursor, connection
    def forget_window(self):
        connection = pymysql.connect(host="localhost", user="root", password="1234")
        cursor = connection.cursor()
        if not cursor or not connection:
            return
        cursor.execute('use inventory_system')
        try:
            if self.employee_id.get()=="":
                messagebox.showerror("Error","Employee Id is required")
            else:
                cursor.execute('SELECT email from employee_data where empid=%s',
                               (self.employee_id.get(),))
                email = cursor.fetchone()
                if email == None:
                    messagebox.showerror("ERROR", "Invalid Employee Id", parent=self.root)
                else:
                    #=====NEW=====FORGET=====WINDOW=======
                    self.var_otp=StringVar()
                    self.var_new_pass=StringVar()
                    self.var_con_pass = StringVar()
                    #callin send_email_function()
                    chk=self.send_email(email[0])
                    if chk=='Failed':
                        messagebox.showerror("Error","Connection Error, try again", parent=self.root)
                    else:

                        self.forget_win=Toplevel(self.root)
                        self.forget_win.title("Reset Password")
                        self.forget_win.geometry('450x400+500+100')
                        self.forget_win.focus_force()
                        title=Label(self.forget_win,text='RESET PASSWORD',font=("goudy old style",15,'bold'),bg="maroon",fg="white").pack(side=TOP,fill=X)
                        lbl_reset=Label(self.forget_win,text="Enter OTP sent on registered Email",font=("times new roman",15)).place(x=20,y=80)
                        text_reset=Entry(self.forget_win,textvariable=self.var_otp,font=("times new roman",15),bg='lightyellow').place(x=20,y=120,width=250,height=30)
                        self.button_reset=Button(self.forget_win,text="SUBMIT",font=("times new roman",15),bg='lightblue',command=self.validate_OTP)
                        self.button_reset.place(x=290,y=120,width=100,height=30)

                        lbl_new_pass = Label(self.forget_win, text="New Password",
                                          font=("times new roman", 15)).place(x=20, y=189)
                        text_new_pass = Entry(self.forget_win, textvariable=self.var_new_pass, font=("times new roman", 15),
                                           bg='lightyellow').place(x=20, y=229, width=250, height=30)

                        lbl_conf_pass = Label(self.forget_win, text="Confirm Password",
                                             font=("times new roman", 15)).place(x=20, y=274)
                        text_conf_pass = Entry(self.forget_win, textvariable=self.var_con_pass, font=("times new roman", 15),
                                              bg='lightyellow').place(x=20, y=314, width=250, height=30)

                        self.button_fin_update = Button(self.forget_win, text="UPDATE", state=DISABLED,font=("times new roman", 15),
                                                   bg='lightblue',command=self.update_pass)
                        self.button_fin_update.place(x=290, y=314, width=100, height=30)

        except Exception as e:
            messagebox.showerror('Error', f'Error due to {e}')

    def update_pass(self):
        if self.var_new_pass.get()=="" or self.var_con_pass.get()=="":
            messagebox.showerror("Error","Password cannot be empty", parent=self.forget_win)
        elif self.var_new_pass.get()!=self.var_con_pass.get():
            messagebox.showerror("Error", "New Password and Confirm Password must be same", parent=self.forget_win)
        else:
            connection = pymysql.connect(host="localhost", user="root", password="1234")
            cursor = connection.cursor()
            if not cursor or not connection:
                return
            cursor.execute('use inventory_system')
            try:
                cursor.execute("Update employee_data SET password=%s where empid=%s",(self.var_new_pass.get(),self.employee_id.get()))
                connection.commit()
                messagebox.showinfo("Success","Password Updated Successfully",parent=self.forget_win)
                self.forget_win.destroy()
            except Exception as e:
                messagebox.showerror('Error', f'Error due to {e}')

    def validate_OTP(self):
        if int(self.otp)==int(self.var_otp.get()):
            self.button_fin_update.config(state=NORMAL)
            self.button_reset.config(state=DISABLED)
        else:
            messagebox.showerror('Error',"Invalid OTP , Try again",parent=self.forget_win)


    def send_email(self, to_):
        import smtplib
        sm = smtplib.SMTP('smtp.gmail.com', 587)
        sm.starttls()
        email_ = email_pass.email_
        password_ = email_pass.pass_
        sm.login(email_, password_)
        self.otp = int(time.strftime("%H%S%M")) + int(time.strftime("%S"))

        subject='Inventory Reset Password OTP'
        message=f'Dear Sir/Madam ,\n\nYour Reset OTP is {str(self.otp)}.\n\nWith Regards,\nInventory Management Team'
        message="Subject:{}\n\n{}".format(subject,message)
        sm.sendmail(email_,to_,message)
        check=sm.ehlo()
        if check[0]==250:
            return 'Success'
        else:
            return 'Failed'



root=Tk()
obj=Login_System(root)
root.mainloop()
