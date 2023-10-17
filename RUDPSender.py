import socket
import hashlib
import time
from marshaller import *
class RUDPSender:
    def __init__(self, server_ip='127.0.0.1', server_port=12345, buffer_size=1024, timeout=2):
        self.server_ip = server_ip
        self.server_port = server_port
        self.buffer_size = buffer_size
        self.timeout = timeout
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(self.timeout)
        
        
    
    # 用于计算一个消息的dataid = sha256(时间戳，data)
    def sha256_hash(self, data):
        timestamp = time.time() # 获取当前时间戳
        hash_object = hashlib.sha256() # 创建一个新的sha256 hash对象
        hash_object.update(f"{timestamp}:{data}".encode())  # 向数据添加时间戳并进行哈希
        return hash_object.hexdigest() # 获取十六进制表示的哈希值

    def send_data(self, data, seq_num, dataid, total_segments, segment_num):
        message = f"{seq_num}:{dataid}:{total_segments}:{segment_num}:{data}"
        self.sock.sendto(message.encode(), (self.server_ip, self.server_port))

    def receive_ack(self):
        try:
            ack, addr = self.sock.recvfrom(self.buffer_size)
            return ack.decode()
        except socket.timeout:
            return None
        
    #可靠传输，需要等待应答的那种
    def reliable_send(self, data, allowed_resend_max_times=10) ->bool:
        '''
        allowed_resend_max_times : 丢包后允许失败的最大次数
        '''
        seq_num = 0
        resend_time_count = 0
        dataid = self.sha256_hash(data)
        segments = [data[i:i+self.buffer_size] for i in range(0, len(data), self.buffer_size)]
        total_segments = len(segments)

        for segment_num, segment in enumerate(segments, start=1):
            self.send_data(segment, seq_num, dataid, total_segments, segment_num)
            ack = self.receive_ack()

            while ack != f"ACK:{seq_num}:{dataid}": # 等待正确的ACK
                if resend_time_count >= allowed_resend_max_times:
                    print("本次消息重传次数过多，发送失败")
                    return False
                self.send_data(segment, seq_num, dataid, total_segments, segment_num)  # 重传数据
                resend_time_count += 1 #传输失败了就加1
                ack = self.receive_ack()

            seq_num += 1 # 更新序列号
        return True




# # 定义一些常量
# SERVER_IP = '127.0.0.1'
# SERVER_PORT = 12345
# BUFFER_SIZE = 1024
# TIMEOUT = 2  # 超时时间

# sender = RUDPSender(SERVER_IP,SERVER_PORT,BUFFER_SIZE,TIMEOUT)
# request1 = {"type":"funcname","params1":"hi 1"}
# request2 = {"type":"funcname","params1":"hi 2"}
# request3 = {"type":"funcname","params1":"hi 3"}
# sender.reliable_send(marshal_dict(request1) )
# sender.reliable_send(marshal_dict(request2) )
# sender.reliable_send(marshal_dict(request3))