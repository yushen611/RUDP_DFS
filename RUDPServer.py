import socket
import ServerHandler


class RUDPServer:
    def __init__(self, server_ip='127.0.0.1', server_port=12345, buffer_size=1024,timeout=2):
        self.server_ip = server_ip
        self.server_port = server_port
        self.buffer_size = buffer_size
        self.timeout = timeout #默认超时时间
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(timeout)  # 设置超时时间
        self.sock.bind((self.server_ip, self.server_port))
        self.received_data = {}
        self.ishandle_data = {}
        


    def send_ack(self, seq_num, addr, dataid):
        ack_message = f"ACK:{seq_num}:{dataid}"
        self.sock.sendto(ack_message.encode(), addr)

    def reliable_receive(self):
        while True:
            try:
                data, addr = self.sock.recvfrom(self.buffer_size)
                seq_num, dataid, total_segments, segment_num, message = data.decode().split(':', 4)
                seq_num, total_segments, segment_num = map(int, [seq_num, total_segments, segment_num])
                
                if dataid not in self.received_data:
                    self.received_data[dataid] = [None] * total_segments
                if dataid not in self.ishandle_data:
                    self.ishandle_data[dataid] = False
                
                self.received_data[dataid][segment_num-1] = message
                self.send_ack(seq_num, addr, dataid)
                
                if all(segment is not None for segment in self.received_data[dataid]):
                    complete_message = ''.join(self.received_data[dataid])
                    # print(f"Received: {complete_message}")
                    #下面这个if else保证莫名其妙的情况下，同样消息id的数据只处理一次
                    if self.ishandle_data[dataid]==False:
                        ServerHandler.server_msg_handle(complete_message,addr) # 处理接收到的消息的逻辑
                        self.ishandle_data[dataid]=True
                        del self.received_data[dataid]
                        
                    else:
                        del self.received_data[dataid]
            except socket.timeout:
                # print(f"{self.timeout}秒没有收到消息了，服务端不想等了退出")
                # exit()
                pass 
            except KeyboardInterrupt:
                exit()
            except SystemExit:
                exit()
            except ConnectionResetError:
                print("客户端关闭连接")
                continue  # 继续监听

# 定义一些常量
SERVER_IP = '127.0.0.1'
SERVER_PORT = 12345
BUFFER_SIZE = 1024

# 使用示例
server = RUDPServer(SERVER_IP,SERVER_PORT,BUFFER_SIZE)
server.reliable_receive()

