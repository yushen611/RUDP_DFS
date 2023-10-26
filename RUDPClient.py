from RUDPSender import RUDPSender
from marshaller import *
import socket
import threading     
from ClientHandler import *



class RUDPClient:
    def __init__(self, server_ip='127.0.0.1', server_port=12345, buffer_size=1024, timeout=2) -> None:
        self.sender = RUDPSender(server_ip,server_port,buffer_size,timeout)
        self.sender.sock.setblocking(True)
        # self.sender.sock.settimeout(timeout)  # 设置超时时间5s
        self.received_data = {}
        pass
    def send_ack(self, seq_num, addr, dataid):
        ack_message = f"ACK:{seq_num}:{dataid}"
        self.sender.sock.sendto(ack_message.encode(), addr)

    def reliable_receive(self):
        while True:
            try:
                data, addr = self.sender.sock.recvfrom(self.sender.buffer_size)
                seq_num, dataid, total_segments, segment_num, message = data.decode().split(':', 4)
                seq_num, total_segments, segment_num = map(int, [seq_num, total_segments, segment_num])
                
                if dataid not in self.received_data:
                    self.received_data[dataid] = [None] * total_segments
                
                self.received_data[dataid][segment_num-1] = message
                self.send_ack(seq_num, addr, dataid)
                
                if all(segment is not None for segment in self.received_data[dataid]):
                    complete_message = ''.join(self.received_data[dataid])
                    
                    client_msg_handle(complete_message,addr) # 处理接收到的消息的逻辑
                    del self.received_data[dataid]
            except socket.timeout:
                print(f"{self.timeout}秒没有收到消息了，客户端不想等了退出")
                return
                ...
            except (KeyboardInterrupt, SystemExit):
                return
            except ValueError as e:
                pass  # ignore
            except ConnectionResetError:
                return
    def reliable_send(self,data):
        return self.sender.reliable_send(data)


def receive_data(client):
    client.reliable_receive()



def send_read_request(client):
    while True:
        try:
            file_path = input("Enter file path, e.g., test.txt: ")
            offset = int(input("Enter offset: "))
            num_bytes = int(input("Enter num_bytes: "))
            break  # 如果没有异常，跳出循环
        except ValueError:
            print("Invalid input. Please enter valid values for offset and num_bytes.")
    # 读每次先读缓存
    if cache.get(file_path) is not None:
        print(f"file:{file_path} is in cache,content is {cache[file_path]}")
        return 
    request = {"type": "read", "file_path": file_path, "offset": str(offset), "num_bytes": str(num_bytes)}
    if client.reliable_send(marshal_dict(request)):
        print("client发送read成功")

def send_insert_request(client):
    while True:
        try:
            file_path = input("Enter file path,eg:test.txt : ")
            offset =  int(input("Enter offset: "))
            content_to_insert = input("input insert content: ")
            break
        except ValueError:
            print("Invalid input. Please enter valid values for offset.")

    request = {"type": "insert", "file_path":file_path, "offset": str(offset), "content_to_insert": content_to_insert}
    flag = client.reliable_send(marshal_dict(request))
    if flag:
        print("client发送insert成功")

def send_subscribe_request(client):
    while True:
        try:
            file_path = input("Enter file path,eg:test.txt : ")
            monitor_interval =  int(input("Enter monitor_interval second: "))
            break
        except ValueError:
            print("Invalid input. Please enter valid values for monitor_interval.")
    request = {"type": "subscribe", "file_path": file_path, "monitor_interval": str(monitor_interval)}
    flag = client.reliable_send(marshal_dict(request))
    if flag:
        print("client发送subscribe成功")

def send_get_file_len_request(client):
    file_path = input("Enter file path,eg:test.txt : ")
    request = {"type": "getFileLen", "file_path": file_path}
    flag = client.reliable_send(marshal_dict(request))
    if flag:
        print("client发送getFileLen成功")

def send_create_file_request(client):
    file_path = input("Enter create file path,eg:test1.txt : ")
    file_content = input("Enter file_content,eg:I LOVE NTU CREATE : ")
    request = {"type": "createFile", "file_path": file_path, "file_content": file_content}
    flag = client.reliable_send(marshal_dict(request))
    if flag:
        print("client发送createFile成功")

def input_thread(client):
    options = {
        '1': send_read_request,
        '2': send_insert_request,
        '3': send_subscribe_request,
        '4': send_get_file_len_request,
        '5': send_create_file_request,
        'e': exit
    }

    while True:
        user_input = input(
            "\nEnter 'e' to exit,\n "
            "\n'1' for read request, \n"
            "\n'2' for insert request,\n "
            "\n'3' for subscribe request,\n "
            "\n'4' for getFileLen request,\n "
            "\n'5' for createFile request:\n "
        )
        handler = options.get(user_input)
        if handler:
            handler(client)
        else:
            print("Invalid input. Please enter a valid option.")


if __name__ == "__main__":
    SERVER_IP = '127.0.0.1'
    # SERVER_IP = '172.20.10.5'
    SERVER_PORT = 12345
    BUFFER_SIZE = 1024
    TIMEOUT = 2

    client = RUDPClient(SERVER_IP, SERVER_PORT, BUFFER_SIZE, TIMEOUT)
    requesthello = {"type":"hello"}
    if client.reliable_send(marshal_dict(requesthello)):
        print("\nclient发送hello成功\n")
    
    
    # 创建一个独立的线程来执行客户端的接收逻辑
    client_receiver_thread = threading.Thread(target=receive_data, args=(client,))
    client_receiver_thread.daemon = True  # 将线程设置为守护线程，这样当主线程退出时，守护线程会自动退出。
    client_receiver_thread.start()
    
    
    # 在主线程中处理输入
    input_thread(client)