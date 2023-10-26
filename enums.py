from enum import Enum

class DataType(Enum):
    Base64str = 1
    Normalstr = 2
    insertSuccess = 3
    

    def __str__(self):
        return str(self.value)

class Response:
    def __init__(self, code:str,  message:str, data_type:DataType=DataType.Normalstr,data:str="",file_path:str=""):
        self.code = code
        self.data = data
        self.message = message
        self.data_type = str(data_type)
        self.file_path = file_path

    def to_dict(self):
        return self.__dict__

