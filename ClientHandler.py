from marshaller import *
from enums import DataType

cache = {}

def client_msg_handle(msg,addr):
    msg_dict = unmarshal_str(msg)
    msg_dict["code"] = bool(msg_dict["code"])
    # 无论是更新操作 还是 查看订阅的消息，都是最新的消息，因此都要更新cache
    if msg_dict['data_type'] == str(DataType.Base64str) :
        msg_dict['data'] = str2bytes(msg_dict['data'])
        if msg_dict["code"] ==True:
            cache[msg_dict["file_path"]] = msg_dict["data"]
    if  msg_dict['data_type'] == str(DataType.insertSuccess):
        # 插入成功的时候先删缓存
        if cache.get(msg_dict["file_path"]) is not None:
            del cache[msg_dict["file_path"]]
    print(f"Received: {msg_dict},from:{addr}")



