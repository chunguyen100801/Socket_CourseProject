from socket import socket
import tkinter as tk
from tkinter import messagebox
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import pickle
from tkcalendar import DateEntry


funcLogin = 'login'
funcSignup = 'sign up'

server_disconnect = False

class ChatPage(tk.Frame):
    '''Màn hình chat của client'''
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        
        # Background của giao diện
        bg = "aliceblue"

        # For the messages to be sent.
        self.my_msg = tk.StringVar()  
        self.my_msg.set("Type your messages here.")
        
        # Frame bên trái màn hình
        left_frame = tk.Frame(self, width=440, bg = bg)
        left_frame.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)

        # Frame bên phải màn hình
        right_frame = tk.Frame(self, width=260, bg = bg)
        right_frame.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
        
        # Frame phần khung chat
        msg_frame = tk.Frame(left_frame)
        msg_frame.pack(fill=tk.BOTH, expand=True)
        
        # Ô hiện tin nhắn và thanh trượt
        scrollbar = tk.Scrollbar(msg_frame, orient="vertical")
        self.msg_list = tk.Listbox(msg_frame, width=50, height=20, bg='light yellow', yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.msg_list.yview)

        scrollbar.pack(side= tk.RIGHT, fill=tk.Y)
        self.msg_list.pack(side=tk.LEFT, fill= tk.BOTH, expand=True)
        
        # Ô chat tin nhắn
        entry_field = tk.Entry(left_frame, textvariable=self.my_msg)
        entry_field.pack(fill=tk.BOTH, pady=2, padx=3)
        
        # Nút gửi tin nhắn
        send_button = tk.Button(left_frame, text="Send", command=self.send, background= "cornflowerblue", fg = "ghostwhite")
        send_button.pack(fill=tk.BOTH, pady=2, padx=3)
        
        # Phần Date picker
        date_label = tk.Label(right_frame, text= "Date picker", foreground="navy", bg = bg)
        self.cal = DateEntry(right_frame, width= 16, background= "cornflowerblue", foreground= "ghostwhite",bd=2, date_pattern='dd/mm/y')
        date_label.pack(pady=5)
        date_label.config(font=("Arial", 12))
        self.cal.pack(pady=1)
        tk.Button(right_frame, text = "Get Date", bg = "cornflowerblue", fg = "ghostwhite", command = self.grad_date).pack(pady=(5, 25))
        
        # Phần Instruction
        instruction_label = tk.Label(right_frame, text= "Instruction", foreground="navy", bg=bg)

        instruction_text = "- Enter the currency code you want to\nexchange to VND (ex: USD, JPY, AUD,...)\n\n- Enter \"history\" if you want to see your\nrequests history\n\n-To find the exchange rate of a particular\ndate, you need to change the date in Date\npicker section and press the \"Get Date\"\nbutton. The default date value is today"

        instruction_label.pack(fill=tk.BOTH)
        instruction_label.config(font=("Arial", 12))
        tk.Label(right_frame, text=instruction_text, anchor='w', justify= tk.LEFT, bg = bg).pack()
        
        # Nút thoat chương trình
        tk.Button(right_frame, text = "Quit", command = self.on_closing, bg="red", fg="white").pack(anchor="se", side=tk.BOTTOM, pady=2, padx=2)


    def grad_date(self):
        '''Gửi ngày tháng tới server'''
        date = self.cal.get_date().strftime("%d/%m/%Y")
        client_socket.send(bytes(date, "utf8"))

    # event is passed by binders.
    def send(self):  
        """Handles sending of messages."""
        global server_disconnect
        msg = self.my_msg.get()

        # Clears input field.
        self.my_msg.set("") 
        self.msg_list.insert(tk.END, " [YOU]: %s" %msg)

        if (server_disconnect == False):
            try:
                client_socket.send(bytes(msg, FORMAT))
            except:
                # Client không thể gửi tin nhắn tới server
                self.msg_list.insert(tk.END, " [SERVER]: ")
                self.msg_list.insert(tk.END, "      Server disconnected!")
                server_disconnect == True
            
            
    def on_closing(self):
        """This function is to be called when the window is closed."""
        # client_socket.send(bytes("{quit}", FORMAT))
        client_socket.close()
        self.quit()
        quit()

    def receive(self):
        """Handles receiving of messages."""
        while True:
            try:
                # Nhận tin nhắn từ server
                msg = client_socket.recv(BUFSIZ).decode(FORMAT)
                
                # Phát hiện server đang muốn gửi thông tin user history
                if msg == "yrotsih":
                    # Chèn vào khung chat
                    self.msg_list.insert(tk.END, " [SERVER]: ")
                    while True:
                        # Nhận tin nhắn từ server
                        msg = client_socket.recv(BUFSIZ)

                        if (msg == b'Empty'):
                            self.msg_list.insert(tk.END, "   Empty :v")
                            break

                        # Phát hiện kết thúc
                        if (msg == b'end'):
                            break

                        # Chuyển đổi data bằng pickle và chèn lên khung chat
                        data_recv = pickle.loads(msg)
                        for item in data_recv:
                            self.msg_list.insert(tk.END, item)
                        client_socket.send(bytes("sc", FORMAT))
                    continue
                
                # Phát hiện server đang muốn gửi thông tin currency code user yêu cầu
                if msg == "tsillist":
                    # Nhận tin nhắn từ server
                    msg = client_socket.recv(BUFSIZ)

                    # Chuyển đổi data bằng pickle và chèn lên khung chat
                    data_recv = pickle.loads(msg)
                    self.msg_list.insert(tk.END, " [SERVER]: ")
                    for item in data_recv:
                        self.msg_list.insert(tk.END, item)
                elif msg == 'disconnect':
                    global server_disconnect
                    self.msg_list.insert(tk.END, " [SERVER]: ")
                    self.msg_list.insert(tk.END, "      Server disconnect!")
                    server_disconnect = True
                    client_socket.close()

                # Trường hợp khác
                else:
                    # print("Msg: ", msg)
                    self.msg_list.insert(tk.END, " [SERVER]: ")
                    self.msg_list.insert(tk.END, msg)

            # Possibly client has left the chat.
            except OSError:  
                break


class EnterIpPage(tk.Frame):
    '''Màn hình nhập Ip của server'''

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        # Khởi tạo dòng chữ "ENTER IP SERVER"
        label_nameApp = tk.Label(self, text='EXCHANGE RATE', fg='brown', font=('Times New Roman', 35)).pack(pady=10)
        label_title = tk.Label(self, text="ENTER IP SERVER", font=("Times New Roman", 20))

        # Khởi tạo ô để nhập Ip
        self.entry_IP = tk.Entry(self, width=20, bg='palegoldenrod')
        # tạo thông báo khi nhap IP sai
        self.label_notice = tk.Label(self, text='', fg='red',font=("Times New Roman",12))
        # Khởi tạo Nút Enter
        enterIP_button = tk.Button( self, text="Enter", width=10,fg='white', bg = 'darkblue',font=("Times New Roman", 11), command=self.connectToServer)
        
        label_title.pack(pady=5)
        self.entry_IP.pack()
        self.label_notice.pack()
        enterIP_button.pack()

    def connectToServer(self):
        try:
            #nhận địa chỉ IP từ ô nhập IP
            msg = self.entry_IP.get()
            client_socket.connect((msg, 33000))
        except:
            '''Trường hợp không kết nối được tới server'''
            #thay doi dong canh bao 
            self.label_notice['text'] = 'Unable to connect to server'
            return
        # Nếu kết nối thành công hiện màn hình log in
        client_app.showLogin()

class loginPage(tk.Frame):
    '''màn hinh đăng nhâp'''
    def __init__(self, parent, appController):
        tk.Frame.__init__(self, parent)
        label_title = tk.Label(self, text="LOG IN",font=("Times New Roman", 30),fg='brown')
        label_title.pack()

        # tạo và in "user name", ô nhập username
        tk.Label(self, text="Username",font=("Times New Roman", 13)).pack()
        self.entry_Name = tk.Entry(self, width=20, bg='palegoldenrod')
        self.entry_Name.pack(pady=5)

        # tạo và in "password", ô nhập password
        tk.Label(self, text="Password",font=("Times New Roman", 13)).pack()
        self.entry_pass = tk.Entry(self, width=20, bg='palegoldenrod',show ='*')
        self.entry_pass.pack(pady=5)

        # thong bao khi tai khoan bi sai
        self.label_notice = tk.Label(self, text="", fg='red',font=("Times New Roman", 12))
        self.label_notice.pack()
        # tạo và in nút đăng nhập
        tk.Button(
            self, text="Log in",bg='darkblue',fg='white', font=("Times New Roman", 11),width=10,command=self.login).pack(pady=5)

        # tạo và in nút đăng ký
        tk.Button(self, text="Sign up",fg = 'darkblue',font=("Times New Roman", 11),width=10, command=lambda: appController.showSignup()).pack()

    def login(self):
        try:
            '''chức năng đăng nhập'''
            # lay username, password từ ô nhập
            username = self.entry_Name.get()
            password = self.entry_pass.get()
            #kiểm tra username và password có trống không
            if username == "" or password == "":
                self.label_notice['text'] = "All information must not be empty!"
                return
            # client gửi đi thao tác đăng nhâp
            client_socket.send(bytes(funcLogin, FORMAT))
            # client gửi lần lượt username và password cho server
            list = [username, password]
            for i in list:
                client_socket.send(bytes(i, FORMAT))
                client_socket.recv(BUFSIZ)
            # client nhận kết quả đăng nhâp từ server
            check = client_socket.recv(BUFSIZ).decode(FORMAT)
            if check == 'yes':
                client_app.showChatPage()
            if check == 'no':
                self.label_notice['text'] = "Username or password is wrong!"
        except:
            # trường hợp server bị lỗi hoặc tắt
            UnableToConnectToServerPage()


class signupPage(tk.Frame):
    '''màn hình đăng ký'''
    def __init__(self,  parent, appController):
        tk.Frame.__init__(self, parent)
        
        # tao tieu de
        label_title = tk.Label(self, text="SIGN UP",font=("Times New Roman", 30),fg='brown')
        label_title.pack()
        
        # khởi tạo thông tin 'name' để client đăng kí
        tk.Label(self, text="Name",font=("Times New Roman", 13)).pack()
        self.entry_Name = tk.Entry(self, width=20, bg='palegoldenrod')
        self.entry_Name.pack(pady=5)
        
        # khởi tạo thông tin 'username' để client đăng kí
        tk.Label(self, text="Username",font=("Times New Roman", 13)).pack()
        self.entry_userName = tk.Entry(self, width=20, bg='palegoldenrod')
        self.entry_userName.pack(pady=5)
        
        # khởi tạo thông tin 'passwrd' để client đăng kí
        tk.Label(self, text="Password",font=("Times New Roman", 13)).pack()
        self.entry_pass = tk.Entry(self, width=20, bg="palegoldenrod")
        self.entry_pass.pack(pady=5)
        
        # khởi tạo thông báo khi tài khoản đăng kí bị trùng
        self.label_notice = tk.Label(self, text='', fg='red',font=("Times New Roman", 12))
        self.label_notice.pack()
        button_signup = tk.Button(
            self, text="Sign up",width=10,bg='darkblue',fg='white', command=self.sigup,font=("Times New Roman", 11)).pack(pady=5)
        # tạo và in nút đăng nhập
        button_back = tk.Button(self, text="Back",command=lambda: appController.showLogin(),width=10,fg = 'darkblue',font=("Times New Roman", 11)).pack()
        
    '''chức năng đăng ký'''
    def sigup(self):
        try:
            # nhận các thông tin từ các ô nhập
            name = self.entry_Name.get()
            username = self.entry_userName.get()
            password = self.entry_pass.get()
            
            # kiểm tra các thông tin không được trống
            if name == '' or username == '' or password == '':
                self.label_notice['text'] = "All information must not be empty!"
                self.label_notice['fg'] = 'red'
                return

            client_socket.send(bytes(funcSignup, FORMAT))
            list = [name, username, password]
            for i in list:
                client_socket.send(bytes(i, FORMAT))
                client_socket.recv(BUFSIZ)
            # client nhận kết quả kiểm tra đăng ký từ server
            check = client_socket.recv(BUFSIZ).decode(FORMAT)
            if check == 'yes':
                self.label_notice['text'] = "Account already exists, please create another account"
                self.label_notice['fg'] = 'red'
            if check == 'no':
                self.label_notice['text'] = "Successful account registration"
                self.label_notice['fg'] = 'green'

        except:
            #trường hợp server bị lỗi hoặc tắt
            UnableToConnectToServerPage()

# hàm thông báo khi bị mất kết nối với server
def UnableToConnectToServerPage():
   messagebox.showerror('Currency converter', 'Server disconnected')
    
class ClientApp(tk.Tk):
    '''
    Client application: Giao diện client sử dụng tkinter
    '''

    def __init__(self):
        tk.Tk.__init__(self)

        # Khởi tạo khung của cửa sổ client
        self.title("Exchange rate")
        self.geometry("700x400")
        self.resizable(width=False, height=False)

        self.container = tk.Frame()
        self.container.configure(bg="red")

        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def showEnterIpPage(self):
        '''Hiện lên màn hình nhập ip address'''
        frame = EnterIpPage(self.container)
        frame.grid(row=0, column=0, sticky="nsew")

    def showLogin(self):
        '''hiện màn hình đăng nhập'''
        frame = loginPage(self.container, self)
        frame.grid(row=0, column=0, sticky="nsew")

    def showSignup(self):
        '''hiện màn hình đăng ký'''
        frame = signupPage(self.container, self)
        frame.grid(row=0, column=0, sticky="nsew")

    def showChatPage(self):
        '''Hiện lên màn hình chat với server'''
        frame = ChatPage(self.container)
        frame.grid(row=0, column=0, sticky="nsew")

        # Bắt đầu nhận dữ liệu từ server
        receive_thread = Thread(target=frame.receive)
        receive_thread.start()

    def on_closing(self):
        if messagebox.askokcancel("Quit client", "Do you want to quit?"):
            client_socket.close()
            self.quit()
            quit()


# --------------------------------------------MAIN---------------------------------------------------
if __name__ == "__main__":
    # Khởi tạo các biến cần thiết
    FORMAT = "utf8"
    HOST = 0
    BUFSIZ = 1024
    ADDR = (HOST, 33000)

    # Khởi động client
    client_socket = socket(AF_INET, SOCK_STREAM)

    client_app = ClientApp()
    client_app.showEnterIpPage()
    client_app.mainloop()
