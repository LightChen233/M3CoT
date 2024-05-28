'''
Author: Qiguang Chen
LastEditors: Qiguang Chen
Date: 2023-10-31 16:11:37
LastEditTime: 2024-05-24 19:23:24
Description: 

'''
from collections import defaultdict
import re
import os
from utils.common_tool import sort_metric
from utils.data import M3CoT, read_jsonl
ALPHA_MAP = ["A", "B", "C", "D", "E", "F"]
def judge_answer(text, choices, answer):
    if isinstance(answer, int):
        answer = ALPHA_MAP[answer]
    if "[Answer]" in text:
        text = text.split("[Answer]")[-1].split("[Rationale]")[0].split("[Context]")[0]
    pattern = re.compile(r'\(([A-Za-z])\)')
    res = pattern.findall(text)
    if len(res) >= 1:
        pred = res[-1].upper()  # 'A', 'B', ...
    else:
        res = []
        for i, choice in enumerate(choices):
            if choice.lower() in text.lower():
                res.append(ALPHA_MAP[i])
        if len(res) >= 1:
            pred = res[-1]
        else:
            for i, choice in enumerate(choices):
                text = re.sub(r'[\n.,!?]', ' ', text)
                if ALPHA_MAP[i] in text.split(" "):
                    res.append(ALPHA_MAP[i])
            if len(res) >= 1:
                pred = res[-1]
            else:
                for i, choice in enumerate(choices):
                    text = re.sub(r'[\n.,!?]', ' ', text)
                    if ALPHA_MAP[i].lower() in text.split(" "):
                        res.append(ALPHA_MAP[i])
                if len(res) >= 1:
                    pred = res[-1]
                else:
                    pred = "FAILED"
    
    if pred == answer:
        return True
    else:
        return False
    
class MetricData():
    def __init__(self, base_dir, file_name=None) -> None:
        data_list = []
        if file_name is None or file_name == "":
            data_list = read_jsonl(base_dir)
        elif os.path.exists(os.path.join(base_dir, f"{file_name}")):
            data_list = read_jsonl(os.path.join(base_dir, f"{file_name}"))
        else:
            for domain in os.listdir(base_dir):
                for topic in os.listdir(os.path.join(base_dir, domain)):
                    obj_list = read_jsonl(os.path.join(base_dir, domain, topic, f"{file_name}"))
                    for obj in obj_list:
                        obj["domain"] = domain
                        obj["topic"] = topic
                        data_list.append(obj)
        self.data = data_list
        self.origin_data = data_list

    def select_by_ids(self, id_list):
        temp_data = []
        for data in self.data:
            if data["id"] in id_list:
                temp_data.append(data)
        self.data = temp_data
    
    def set_by_id(self, id, value):
        for i, d in enumerate(self.data):
            if d["id"] == id:
                self.data[i] = value
                break
        for i, d in enumerate(self.origin_data):
            if d["id"] == id:
                self.origin_data[i] = value
                break
        
    
    def reset(self):
        self.data = self.origin_data

    def metric(self,
               by="all",
               map:M3CoT=None):
        total = {}
        correct = {}
        if len(self.data) == 0:
            return 0
        idx_list = []
        for obj in self.data:
            if map is not None:
                if obj["id"] in idx_list:
                    continue
                else:
                    idx_list.append(obj["id"])
            if map is not None:
                flag = False
                for d in map.data:
                    if d["id"] == obj["id"]:
                        obj["domain"] = d["domain"]
                        obj["topic"] = d["topic"]
                        if "choices" not in obj:
                            obj["choices"] = d["choices"]
                        obj["answer"] = d["answer"]
                        flag = True
                        break
                if not flag:
                    continue
            
            pred_text = obj["messages"][-1]
            if obj["domain"] not in correct.keys():
                correct[obj["domain"]] = {}
            if obj["topic"] not in correct[obj["domain"]].keys():
                correct[obj["domain"]][obj["topic"]] = 0
            if obj["domain"] not in total.keys():
                total[obj["domain"]] = {}
            if obj["topic"] not in total[obj["domain"]].keys():
                total[obj["domain"]][obj["topic"]] = 0    
            
            if judge_answer(pred_text, obj["choices"], obj["answer"]):
                correct[obj["domain"]][obj["topic"]] += 1
            # elif obj["domain"] == "commonsense":
            #     print(obj)
            total[obj["domain"]][obj["topic"]] += 1
        if by == "all":
            _total = sum([total[key1][key2] for key1 in total for key2 in total[key1]])
            _correct = sum([correct[key1][key2] for key1 in total for key2 in correct[key1]])
            return {"total": {"acc": _correct * 1.0 / _total, "total": _total, "correct": _correct}}
        elif by == "domain":
            res_dict = {}
            for key1 in total:
                _total = sum([total[key1][key2] for key2 in total[key1]])
                _correct = sum([correct[key1][key2] for key2 in correct[key1]])
                res_dict[key1] = {"acc": _correct * 1.0 / _total, "total": _total, "correct": _correct}
            res_dict = sort_metric(res_dict)
            return res_dict
        elif by == "topic":
            res_dict = defaultdict(defaultdict)
            for key1 in total:
                for key2 in total[key1]:
                    _total = sum([total[key1][key2]])
                    _correct = sum([correct[key1][key2]])
                    res_dict[key1][key2] = {"acc": _correct * 1.0 / _total, "total": _total, "correct": _correct}
            res_dict = sort_metric(res_dict)
            return res_dict
        else:
            raise ValueError


