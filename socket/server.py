from socket import AF_INET, socket, SOCK_STREAM
import socket as sk
from threading import Thread
import tkinter as tk
from tkinter import messagebox
import json
import server_components as svc
import pickle
import time
from datetime import datetime

api_connection = True
clients = {}
funcLogin = 'login'
funcSignup = 'sign up'
filenameuser = 'data_login.json'

def accept_incoming_connections():
    '''Sets up handling for incoming clients'''
    try:
        while True:
            # Lấy thông tin kết nối của client
            try:
                client, client_address = SERVER.accept()
            except:
                print("Error")

            # In thông tin của client lên màn hình console và màn hình giao diện của server
            client_connected = "%s: %s has connected." % client_address        
            server_app.insertMsg(client_connected)

            # Bắt đầu tiến trình giao tiếp với client
            Thread(target=handle_client, args=(client,client_address)).start()
    except:
        # Trường hợp server bị lỗi
        msg = "   ERROR" 
        # Chèn message vào Listbox tkinter
        server_app.insertMsg(msg)


def login(client):
    '''hàm kiểm tra đăng nhập'''
    # nhận username, password từ client và kiểm tra
    username = client.recv(BUFSIZ).decode(FORMAT)
    client.send(bytes(username, FORMAT))
    password = client.recv(BUFSIZ).decode(FORMAT)
    client.send(bytes(password, FORMAT))
    msg = 'no'
    # mở file dữ liệu, đọc và kiểm tra thông tin đăng nhập
    with open(filenameuser,'r+') as file:
        data = json.load(file)
    for person in data['user']:
        data_username=person['username']
        data_pass = person['password']
        if data_username==username and data_pass==password:
            msg = 'yes'
            data_name = person['name']
    # trả kết quả về client
    client.send(bytes(msg,FORMAT))
    if msg=='yes':
        return data_name
    else:
        return ''

def signup(client):
    '''hàm đăng ký'''
    # nhận thông tin đăng kí từ client
    name = client.recv(BUFSIZ).decode(FORMAT)
    client.send(bytes(name, FORMAT))
    username = client.recv(BUFSIZ).decode(FORMAT)
    client.send(bytes(username, FORMAT))
    password = client.recv(BUFSIZ).decode(FORMAT)
    client.send(bytes(password, FORMAT))
    msg = 'no'
    
    # kiểm tra tài khoản đã tồn tại chưa
    with open(filenameuser, 'r+') as file:
        data = json.load(file)
    for person in data["user"]:
        data_name = person["username"]
        if data_name == username:
            msg = 'yes'
    client.send(bytes(msg, FORMAT))
    # lưu tài khoản vào file dữ liệu
    if msg == 'no':
        with open(filenameuser, 'r+') as file:
            datauser = json.load(file)
        datauser["user"].append(
            {
                "name": name,
                "username": username,
                "password": password
            }
        )
        with open(filenameuser, 'r+') as file:
            json.dump(datauser, file, indent=4)

def handle_client(client,client_address):
    '''Handles a single client connection'''
    global api_connection  
    name=''
    # Khởi tạo biến {date} để lưu ngày tháng hiện tại làm giá trị default
    # Công dụng biến này dùng để biết user đang chọn ngày tháng nào để trích xuất dữ liệu
    date = datetime.now().strftime("%d/%m/%Y")
    
    try:
        while True:
            # Nhận tin nhắn từ client
            msg = client.recv(BUFSIZ).decode(FORMAT)
            if msg == funcLogin:
                name=login(client)
                if name!= '':# Nếu đăng nhập thành công, gởi welcome message tới client.
                    welcome = '    Welcome %s! Please read the Instruction and tell me your requests' % name
                    client.send(bytes(welcome, FORMAT))
                    clients[client] = name
                continue
            elif msg == funcSignup:
                signup(client)
                continue
            
            # Kiểm tra tin nhắn vừa nhận có phải là ngày tháng ko
            # Nếu có thì {date = msg} và gửi tin nhắn tới client
            if (svc.is_date(msg)):
                date = msg
                set_date_msg = "   Set date: %s" %date
                client.send(bytes(set_date_msg, FORMAT))
                continue
            
            
            # Tạo độ delay cho server để cho giống một đoạn chat thật
            time.sleep(0.7)

            # Kiểm tra tin nhắn vừa được gửi tới có phải là "history" ko
            if msg.lower() == "history":
                # Nếu có thì gửi tin nhắn này tới client
                # để cho client chuẩn bị nhận thông tin lịch sử người dùng
                client.send(bytes("yrotsih", FORMAT))

                # Tìm kiếm lịch sử người dùng thông qua tên người dùng {name}
                history_data = svc.findUserHistory(name)

                # {history_data} có kiểu list bao gồm nhiều list khác nhau
                # Vd: history_data = [[data1, data2, data3], [data4, data5, data6], [data7, data8, data9]]
                
                # Kiểm tra nếu không có lịch sử của user (do user là người dùng mới)
                if history_data == []:
                    client.send(bytes("Empty", FORMAT))
                    continue

                # Bắt đầu gửi user history data tới client
                for item in history_data:
                    # Dùng pickle để gửi data kiểu list tới người dùng
                    data_send = pickle.dumps(item)
                    client.send(data_send)
                    
                    # Nhận tin nhắn từ client để biết đã gửi thành công và tránh lỗi xảy ra
                    client.recv(BUFSIZ).decode(FORMAT)
                # Gửi tới client tin nhắn thông báo kết thúc quá trình
                client.send(bytes("end", FORMAT))

            else:
                # Tìm dữ liệu trong thời điểm mà user yêu cầu thông qua biến {date}
                # và {msg}, trong đó msg nếu như đúng là mã tiền tệ (ex: USD) còn
                # date là ngày tháng
                reply_dict = svc.find_currency(msg, date)
                
                # Thông báo với client là server không kết nối với api được nếu {api_connection = False}
                if api_connection == False:
                    client.send(bytes("   Unable to connect to API from server :(", FORMAT))
                    continue
                
                # Kiểm tra nếu như không có dữ liệu thì gửi tin nhắn như dưới tới client
                if (reply_dict == {}):
                    client.send(bytes("   Sorry, I can't fulfill this request :(", FORMAT))

                # Trường hợp có dữ liệu
                elif (reply_dict):
                    # Gửi tin nhắn này tới client để cho client chuẩn bị nhận thông tin user yêu cầu
                    client.send(bytes("tsillist", FORMAT))

                    #Chuyển đổi từ dạng dictionary sang list để có thể gửi tới client
                    # {reply_dict} có kiểu dictionary
                    # {reply} có kiểu list
                    reply = svc.dictToDataSendClient(reply_dict)

                    # Kiểm tra, có thể xoá khi hoàn thành
                    # print(reply)

                    # Lưu data vừa lấy được vào lịch sử người dùng
                    svc.saveUserHistory(name, reply_dict)

                    # Gửi data tới client
                    data_send = pickle.dumps(reply)
                    client.send(data_send)
                else:
                    # Trường hợp xảy ra lỗi ngoài ý muốn
                    client.send(bytes("   Something went wrong!", FORMAT))
    except:
        '''Phát hiện client ngắt kết nối tới server'''
        msg = "%s: %s has disconnected." % client_address
        for sock in clients:
            if sock == client:
                del clients[sock]
                break
        # Chèn message vào Listbox tkinter
        server_app.insertMsg(msg)

    # Client đóng
    print("close")
    client.close()

def countdown(t):
    '''Hàm đếm thời gian'''
    while t:  # while t > 0 for clarity
        time.sleep(1)
        t -= 1


def updateData():
    '''Upadate data mới sau mỗi 30 phút'''
    global api_connection
    # Lúc bắt đầu khởi động, lấy data về
    while True:
        # Kiểm tra có thể lấy data mới được không
        check = svc.getDataFromAPI()

        if (check == False):
            break

        # Đếm ngược 30 phút
        countdown(1800)

    # Gán biến {api_connection} bằng False
    api_connection = False

class ServerApp(tk.Tk):
    '''
    Server application: Giao diện server sử dụng tkinter
    Hiện lên các thông báo về kết nối của client
    '''

    def __init__(self):
        tk.Tk.__init__(self)

        # Khởi tạo khung của cửa sổ server
        self.title("Server")
        self.geometry("400x600")
        self.resizable(width=False, height=False)

        # Lấy thông tin {hostname} và {ip_address} của thiết bị sử dụng làm server
        hostname = sk.gethostname()
        ip_address = sk.gethostbyname(hostname)

        # In ra màn hình giao diện của server
        hostname_label = tk.Label(self, text=f"Hostname: {hostname}")
        ip_address_label = tk.Label(self, text=f"IP Address: {ip_address}")
        hostname_label.pack()
        ip_address_label.pack()

        tk.Button(self, text = "Disconnect to all clients", command = self.disconnect_clients,font=('Times New Roman', 10), bg="crimson", fg="white").pack(pady=15)

        # Khởi tạo Listbox hiển thị thông tin client thông qua {server_list}
        scrollbar = tk.Scrollbar(self, orient="vertical")
        self.server_list = tk.Listbox(self, yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.server_list.yview)

        scrollbar.pack(side= tk.RIGHT, fill=tk.Y)
        self.server_list.pack(side=tk.LEFT, fill= tk.BOTH, expand=True)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    # Nhận {msg} làm argument
    # {msg} là một string message
    def insertMsg(self, msg):
        '''Chèn {msg} vào Listbox'''
        self.server_list.insert(tk.END, msg)
    
    # Handle nút ngừng kết nối tới tất cả clients
    def disconnect_clients(self):
        if clients == {}:
            self.server_list.insert(tk.END, "No clients available")
            return

        for sock in clients.keys():
            sock.send(bytes("disconnect", FORMAT))

    def on_closing(self):
        if messagebox.askokcancel("Quit server", "Do you want to quit?"):
            for sock in clients.keys():
                sock.send(bytes("disconnect", FORMAT))
            # self.destroy()
            # sys.exit()
            self.quit()
            quit()
            


# --------------------------------------------MAIN---------------------------------------------------
if __name__ == "__main__":
    # Khởi tạo các biến cần thiết
    HOST = ''
    PORT = 33000
    BUFSIZ = 1024
    ADDR = (HOST, PORT)
    FORMAT = "utf8"
    ip_address = ""

    # Khởi động server
    SERVER = socket(AF_INET, SOCK_STREAM)
    SERVER.bind(ADDR)
    SERVER.listen(5)

    DATA_THREAD = Thread(target=updateData)
    DATA_THREAD.daemon = True
    DATA_THREAD.start()

    ACCEPT_THREAD = Thread(target=accept_incoming_connections)
    ACCEPT_THREAD.daemon = True
    ACCEPT_THREAD.start()

    # Khởi động giao diện server
    server_app = ServerApp()
    server_app.mainloop()

    SERVER.close()
