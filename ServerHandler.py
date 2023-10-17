from marshaller import *
from RUDPSender import RUDPSender
import FileHandler 
from datetime import datetime, timedelta
from enums import DataType,Response
subscriptions = {}  # 存储订阅更新的addr的字典

def server_msg_handle(msg, addr):
    msg_dict = unmarshal_str(msg)
    print(f"Received: {msg_dict} from {addr}")  # 在try块内部打印

    msg_type_handlers = {
        "hello": hello_handle,
        "read": read_handle,
        "insert": insert_handle,
        "subscribe": subscribe_handle,
        "getFileLen": getFileLen_handle,
        "createFile":createFile_handle
    }

    msg_type = msg_dict.get("type")
    handler = msg_type_handlers.get(msg_type, other_handle)
    
    try:
        handler(msg_dict, addr)
    except Exception as e:
        print(e)


def hello_handle(msg_dict,addr):
    sender = RUDPSender(addr[0],addr[1])
    response = Response(
        code="True",
        message=f"hi, I got your msg, hello client{addr}",
    )
    responce = {"code":"True","data":"","message":f"hi,I got your msg,hello client{addr}","data_type":str(DataType.Normalstr)}
    sender.reliable_send(marshal_dict(response.to_dict()))

def other_handle(msg_dict,addr):
    sender = RUDPSender(addr[0],addr[1])
    response = Response(
        code="True",
        message="hi,I got your msg,but wrong msg type",
    )
    
    sender.reliable_send(marshal_dict(response.to_dict()))

def read_handle(msg_dict,addr):
    file_path = msg_dict["file_path"]
    offset = int(msg_dict["offset"])
    num_bytes = int(msg_dict["num_bytes"])
    flag,content,msg = FileHandler.read_file_content(file_path,offset,num_bytes)
    response = Response(
        code=str(flag),
        data=bytes2str(content),
        message=msg,
        data_type=DataType.Base64str,
        file_path=file_path
    )
    sender = RUDPSender(addr[0],addr[1])
    sender.reliable_send(marshal_dict(response.to_dict()))

def insert_handle(msg_dict,addr):
    file_path = msg_dict["file_path"]
    offset = int(msg_dict["offset"])
    content_to_insert = msg_dict["content_to_insert"]
    flag,msg = FileHandler.insert_content_into_file(file_path,offset,content_to_insert)
    response = Response(
        code=str(flag),
        message=msg,
        file_path=file_path,
        data_type=DataType.insertSuccess
    )
    
    sender = RUDPSender(addr[0],addr[1])
    sender.reliable_send(marshal_dict(response.to_dict()))

    # 遍历subscriptions，检查是否有过期订阅
    print(f"subscriptions:{subscriptions}")

    current_time = datetime.now()

    for sub_addr, (sub_file_path, expired_time) in subscriptions.items():
        # 向过期的订阅发送消息
        if current_time >= expired_time:
            response = Response(
                code=str(flag),
                message=msg,
            )
            expired_response= Response(
                code=str(True),
                message=f"订阅的文件{sub_file_path}已过期",
            )
            sender = RUDPSender(sub_addr[0], sub_addr[1])
            sender.reliable_send(marshal_dict(expired_response.to_dict()))
            del subscriptions[sub_addr]
            continue
        # 如果没过期，且是当前更新的文件
        if sub_file_path == file_path and current_time < expired_time:
            len,msg = FileHandler.get_file_length(file_path)
            if len == -1:
                response = Response(
                    code = "False",
                    data= f"{len}",
                    message= msg
                )
            else:
                flag, content, msg = FileHandler.read_file_content(file_path, offset, len)
                response = Response(
                    code = str(flag),
                    data= bytes2str(content),
                    message= msg,
                    data_type=DataType.Base64str,
                    file_path=file_path
                )
            sender = RUDPSender(sub_addr[0], sub_addr[1])
            sender.reliable_send(marshal_dict(response.to_dict()))

    

def subscribe_handle(msg_dict,addr):
    file_path = msg_dict["file_path"]
    monitor_interval = int(msg_dict["monitor_interval"])
    # 获取当前时间
    current_time = datetime.now()

    # 将monitor_interval转换为timedelta对象
    interval = timedelta(seconds=monitor_interval)

    # 将interval与当前时间相加，得到可比较的时间对象
    expired_time = current_time + interval
    subscriptions[addr] = (file_path,expired_time)
    expired_time_str = expired_time.strftime("%Y-%m-%d %H:%M:%S")
    response = Response(
        code="True",
        message=f"订阅文件{file_path}成功,过期时间为{expired_time_str}",
    )
    sender = RUDPSender(addr[0],addr[1])
    sender.reliable_send(marshal_dict(response.to_dict()))

def getFileLen_handle(msg_dict,addr):
    file_path = msg_dict["file_path"]
    len,msg = FileHandler.get_file_length(file_path)
    flag = True if len != -1 else False
    response = Response(
        code="True",
        data= str(len),
        message=msg,
    )
    sender = RUDPSender(addr[0],addr[1])
    sender.reliable_send(marshal_dict(response.to_dict()))


def createFile_handle(msg_dict,addr):
    file_path = msg_dict["file_path"]
    file_content = msg_dict["file_content"]
    flag,msg = FileHandler.create_file(file_path,file_content)
    response = Response(
        code=str(flag),
        message=msg,
    )
    sender = RUDPSender(addr[0],addr[1])
    sender.reliable_send(marshal_dict(response.to_dict()))

    