import os
import json

def read_jsonl(load_path):
    if not os.path.exists(load_path):
        print("Missing PATH: ", load_path)
        return []
    with open(load_path, "r", encoding="utf8") as f:
        res_list = []
        for i, line in enumerate(f):
            try:
                res_list.append(json.loads(line.strip()))
            except:
                print("Error in line :", i)
    return res_list

def write_jsonl(save_path, file_name, res_list):
    if not os.path.exists(save_path):
        os.makedirs(save_path, exist_ok=True)
    with open(os.path.join(save_path, file_name), "w", encoding="utf8") as f:
        for r in res_list:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            
            
class RecordWriter():
    def __init__(self,
                 save_dir,
                 file_name,
                 load_if_exists=True) -> None:
        if not os.path.exists(save_dir):
            os.makedirs(save_dir, exist_ok=True)
        self.save_path = os.path.join(save_dir, file_name)
        last_data = None
        if not load_if_exists:
            with open(self.save_path, "w", encoding="utf8") as f:
                pass
            last_idx = 0
        else:
            total_data = read_jsonl(self.save_path)
            if len(total_data) != 0:
                last_data = total_data[-1]
            last_idx = len(total_data)
        return last_idx, last_data
    
    def append_to_file(self, data):
        with open(self.save_path, "a", encoding="utf8") as f:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")
    
def sort_dict(a_dict,option="value"):
        '''
        对dict进行排序
        :param a_dict: 待排序的字典
        :param option: 有两种选择，一种是value代表根据value进行排序，一种是key代表根据key值进行排序
        :return: 排序后的新字典
        '''
        if option in ["value","key"]:
            result_dict={}
            if option=="key":
                temp_list=list(a_dict.keys())
                temp_list.sort()
                for item in temp_list:
                    result_dict[item]=a_dict[item]
            else:
                temp_value_list=list(a_dict.values())
                temp_key_list=list(a_dict.keys())
                for i in range(len(temp_key_list)):
                    for j in range(len(temp_key_list)-i-1):
                        if temp_value_list[j]>temp_value_list[j+1]:
                            temp=temp_key_list[j]
                            temp_key_list[j]=temp_key_list[j+1]
                            temp_key_list[j+1]=temp
                            temp=temp_value_list[j]
                            temp_value_list[j]=temp_value_list[j+1]
                            temp_value_list[j+1]=temp
                for key,value in zip(temp_key_list,temp_value_list):
                    result_dict[key]=value
            return result_dict
        raise ValueError(option+" is not in option list——[key,value]")

def sort_metric(a_dict):
    res_dict = {}
    res_dict["science"] = sort_dict(a_dict["science"], option="key")
    res_dict["commonsense"] = sort_dict(a_dict["commonsense"], option="key")
    res_dict["mathematics"] = sort_dict(a_dict["mathematics"], option="key")
    return res_dict