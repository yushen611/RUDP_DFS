import base64
def encode_string(s):
    """
    Encode the string to escape special characters.
    """
    s = s.replace("\\", "\\\\")
    s = s.replace(":", "\\:")
    s = s.replace("|", "\\|")
    return s

def decode_string(s):
    """
    Decode the string to revert the escaped special characters.
    """
    s = s.replace("\\|", "|")
    s = s.replace("\\:", ":")
    s = s.replace("\\\\", "\\")
    return s

def marshal_dict(input_dict):
    """
    Serialize the dictionary into a custom format string.
    """
    try:
        pairs = [f"{encode_string(key)}::{encode_string(value)}" for key, value in input_dict.items()]
        marshalled_str = "||".join(pairs)
        return marshalled_str
    except Exception as e:
        print(f"Error: Unable to serialize the input. {e}")
        return None

def unmarshal_str(input_str):
    """
    Deserialize the custom format string back into a dictionary.
    """
    try:
        output_dict = {}
        pairs = input_str.split("||")
        for pair in pairs:
            key, value = pair.split("::")
            output_dict[decode_string(key)] = decode_string(value)
        return output_dict
    except Exception as e:
        print(f"Error: Unable to deserialize the input string. {e}")
        return None
def bytes2str(bytes) ->str:
    return base64.b64encode(bytes).decode('utf-8')

def str2bytes(encoded_str)->bytes:
    return base64.b64decode(encoded_str.encode('utf-8'))

def testmarshalling():
    # Test the functions
    dict_to_marshal = {"key1": "value1", "key_with::colon": "value_with||pipe"}

    # Marshalling
    marshalled_str = marshal_dict(dict_to_marshal)
    print(f"Marshalled String: {marshalled_str}")

    # Unmarshalling
    unmarshalled_dict = unmarshal_str(marshalled_str)
    print(f"Unmarshalled Dictionary: {unmarshalled_dict}")

# testmarshalling()