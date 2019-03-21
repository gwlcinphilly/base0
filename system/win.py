from winreg import HKEY_LOCAL_MACHINE, OpenKey, KEY_ALL_ACCESS, EnumKey,\
    EnumValue

def reg_path(path,key_=None):
    try:
        if key_ is None:  
            reg_key = OpenKey(HKEY_LOCAL_MACHINE, path, 0, KEY_ALL_ACCESS)
        else: 
            reg_key = OpenKey(path, key_, 0, KEY_ALL_ACCESS)
    except: 
#        print(f"registry key {path} is not exist")
        reg_key = None
    return reg_key
            
def reg_subkeys(reg_key, subkey=None):
    subkeys = []
    try: 
        index = 0 
        while True: 
            subkey_ = EnumKey(reg_key, index)
            subkeys.append(subkey_)
            index += 1
            if subkey is not None:
                if subkey == subkey_:
                    subkeys = reg_path(reg_key,subkey)
                    break
    except WindowsError:
        pass  
    return subkeys

def reg_subkey(reg_key, name=False):
    try:
        subkey = EnumKey(reg_key, 0)
        if not name: 
            subkey = reg_path(reg_key, subkey)
    except WindowsError:
        subkey = None 
    return subkey

def reg_value(reg_key):
    try: 
        value = EnumValue(reg_key, 0)
    except WindowsError:
        value = None
    return value

def reg_values(reg_key, value=None):
    values = []
    try: 
        index = 0
        while True:
            value_ = EnumValue(reg_key, index)
            values.append(value_)
            index += 1
            if value is not None:
                if value == value_[0]:
                    values = value_[1]
                    break
    except WindowsError:
        pass
    return values

def reg_get_values(reg_key, pairs, mapper_dict=None):
    returnvalue = {}
    for entry in pairs:
        key_ = entry[0]
        value_ = entry[1]
        subkey_ = reg_subkeys(reg_key, subkey=key_)
        if mapper_dict:
            name = mapper_dict[value_]
        else:
            name = value_
        returnvalue[name] = reg_values(subkey_, value_)
    return returnvalue