
def read_file_content(file_path, offset, num_bytes) ->(bool,bytes,str):
    try:
        with open(file_path, 'rb') as file:
            file.seek(offset)  # 将文件指针移动到指定的偏移量
            content = file.read(num_bytes)  # 读取指定数量的字节
            return True,content,f"文件{file_path}读取成功"
    except Exception as e:
        return  False,b"",f"文件读取错误,原因:{e}"  # 返回空bytes



def insert_content_into_file(file_path, offset, content_to_insert:str) -> (bool, str):
    try:
        # 打开文件并读取原始内容
        with open(file_path, 'rb') as file:
            original_content = file.read()

        # 确保偏移量不超过文件长度
        if offset > len(original_content):
            return False, "Offset exceeds file length"

        # 将字符串编码为字节流
        content_bytes = content_to_insert.encode('utf-8')

        # 插入新内容到原始内容中
        updated_content = (
            original_content[:offset] + content_bytes + original_content[offset:]
        )

        # 将更新后的内容写回文件
        with open(file_path, 'wb') as file:
            file.write(updated_content)

        return True, "Content inserted successfully"
    except FileNotFoundError:
        return False, "File not found"
    except Exception as e:
        return False, "Error inserting content into the file"

def get_file_length(file_path)->(int,str):
    try:
        # 打开文件并获取其长度
        with open(file_path, 'rb') as file:
            file_length = len(file.read())
        return file_length,"get file len successfully"
    except FileNotFoundError:
        return -1 ,"get file len:file not found" # 文件不存在时返回-1
    except Exception as e:
        return -1 ,f"get file len:{str(e)}" # 发生其他错误时返回-2

def create_file(file_name, file_content="")->(bool,str):
    try:
        # 打开文件以写入模式（'w'），如果文件不存在则创建它
        with open(file_name, 'w') as file:
            # 写入文件内容
            file.write(file_content)
        return True, "File created successfully"
    except Exception as e:
        return False, str(e)