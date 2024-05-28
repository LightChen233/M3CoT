'''
Author: Qiguang Chen
LastEditors: Qiguang Chen
Date: 2023-10-31 14:35:46
LastEditTime: 2024-05-24 17:38:25
Description: 

'''
import base64
from copy import deepcopy
import json
import os
import shutil

import PIL.Image
from tqdm import tqdm

from utils.common_tool import write_jsonl


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

class M3CoT():
    def __init__(self, data_path="data", enable_image_prepare=False, dataset=None) -> None:
        base_dir = data_path
        data_list = []
        if not os.path.exists("data/images"):
            os.makedirs("data/images", exist_ok=True)
        if dataset is None:
            for sp in ["train", "dev", "test"]:
                obj_list = read_jsonl(os.path.join(base_dir, f"{sp}.jsonl"))
                for obj in obj_list:
                    if isinstance(obj["image"], str):
                        obj["image_path"] = obj["image"]
                        if enable_image_prepare:
                            obj["image"] = PIL.Image.open(obj["image_path"]).convert("RGB")
                    else:
                        obj["image_path"] = os.makedirs(f"data/images/{obj['id']}.png")
                        obj["image"].save(f"data/images/{obj['id']}.png", 'PNG')
                    data_list.append(obj)
        else:
            for sp in ["train", "dev", "test"]:
                obj_list = dataset[sp]
                for obj in obj_list:
                    data_list.append(obj)
            
        self.data = data_list
        self.origin_data = data_list
        self.domains = list(set([data["domain"] for data in data_list]))
        ids = self.get_ids()
        assert len(ids) == len(set(ids))

    def get_domain(self):
        return self.domains
    
    def reset(self):
        self.data = self.origin_data
    
    def select_by_category(self, category_list):
        temp_data = []
        for data in self.data:
            if data["category"] in category_list:
                temp_data.append(data)
        self.data = temp_data
    
    def select_by_split(self, split):
        temp_data = []
        for data in self.data:
            if data["split"] == split:
                temp_data.append(data)
        self.data = temp_data
    
    def select_by_domain(self, domain):
        temp_data = []
        for data in self.data:
            if data["domain"] == domain:
                temp_data.append(data)
        self.data = temp_data
    
    def select_by_topic(self, topic):
        temp_data = []
        for data in self.data:
            if data["topic"] == topic:
                temp_data.append(data)
        self.data = temp_data
    
    def get_category(self, topic_list=None):
        if topic_list is None:
            return list(set([x["category"] for x in self.data]))
        else:
            return list(set([x["category"] for x in self.data if x["topic"] in topic_list]))
    
    def get_topic(self, domain_list=None):
        if domain_list is None:
            return list(set([x["topic"] for x in self.data]))
        else:
            return list(set([x["topic"] for x in self.data if x["domain"] in domain_list]))
    
    def get_ids(self):
        return [x["id"] for x in self.data]
    
    def save_as_scienceqa_format(self, save_dir):
        res_list = {}
        ANSWER_MAP = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5, "G": 6}
        if not os.path.exists(os.path.join(save_dir, "images")):
            os.makedirs(os.path.join(save_dir, "images"), exist_ok=True)
        splits = {}
        for data in self.data:
            data = deepcopy(data)
            if "image" in data:
                del data["image"]
            data["answer"] = ANSWER_MAP[data["answer"]]
            data["solution"] = data["rationale"]
            data.pop("rationale")
            data["hint"] = data["context"]
            data.pop("context")
            data["image"] = "image.png"
            data["task"] = "closed choice"
            temp_save_dir = os.path.join(save_dir, "images", data["id"])
            if not os.path.exists(temp_save_dir):
                os.makedirs(temp_save_dir, exist_ok=True)
            if not os.path.exists(os.path.join(temp_save_dir, "image.png")):
                shutil.copy(data["image_path"], os.path.join(temp_save_dir, "image.png"))
            res_list[data["id"]] = data
            if data["split"] not in splits:
                splits[data["split"]] = []
            splits[data["split"]].append(data["id"])
        with open(os.path.join(save_dir, "problems.json"), "w") as f:
            json.dump(res_list, f)
        with open(os.path.join(save_dir, "pid_splits.json"), "w") as f:
            json.dump(splits, f)
        
    def save_as_m3it_format(self, save_dir):
        ALPHA_MAP = ["A", "B", "C", "D", "E", "F", "G"]
        
        for split in ["train", "dev", "test"]:
            self.select_by_split(split)
            res_list = []
            for data in self.data:
                
                obj = {}
                with open(data["image_path"], "rb") as image_file:
                    if "image" in data:
                        del data["image"]
                    obj["image_str"] = base64.b64encode(image_file.read()).decode("utf-8")
                    if data["context"] != "":
                        inp = "[Context]\n" + data["context"] + "\n\n"
                    else:
                        inp = ""
                    inp += "[Question]\n" + data["question"] + "\n[Choices]\n"
                    for i, c in enumerate(data["choices"]):
                        inp += f"({ALPHA_MAP[i]}) {c}\n"
                    obj["input"] = inp
                    obj["outputs"] = data["rationale"]
                    obj["meta"] = {
                        "image_id": data["image_id"],
                        "instance_id": data["id"],
                        "split": data["split"]
                    }
                res_list.append(obj)
            write_jsonl(save_dir, f"{split}.jsonl", res_list)
            self.reset()
            
    def save_as_m3cot_format(self, save_dir):
        
        if not os.path.exists(os.path.join(save_dir, "images")):
            os.makedirs(os.path.join(save_dir, "images"), exist_ok=True)
        splits = {"train": [], "dev": [], "test": []}
        for data in tqdm(self.data):
            data = deepcopy(data)
            if "image" in data:
                del data["image"]
            temp_save_path = os.path.join(save_dir, "images", data["id"] +".png")
            shutil.copy(data["image_path"], temp_save_path)
            data["image_path"] = temp_save_path
            
            splits[data["split"]].append(data)
        for sp in ["train", "dev", "test"]:
            write_jsonl(save_dir, f"{sp}.jsonl", splits[sp])
            
    def save_as_preview_format(self, save_dir):
        res_list = []
        ANSWER_MAP = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5, "G": 6}
        if not os.path.exists(os.path.join(save_dir, "images")):
            os.makedirs(os.path.join(save_dir, "images"), exist_ok=True)
        for data in tqdm(self.data):
            data = deepcopy(data)
            if "image" in data:
                del data["image"]
            data["answer"] = ANSWER_MAP[data["answer"]]
            data["solution"] = data["rationale"]
            data.pop("rationale")
            data["hint"] = data["context"]
            data.pop("context")
            data["image"] = "image.png"
            data["task"] = "closed choice"
            data["path"] = f"https://cdn.jsdelivr.net/gh/LightChen233/blog-img/m3cot-image/{data['id']}.png"
            
            temp_save_dir = os.path.join(save_dir, "images")
            if not os.path.exists(os.path.join(temp_save_dir, f"{data['id']}.png")):
                shutil.copy(data["image_path"], os.path.join(temp_save_dir, f"{data['id']}.png"))
            res_list.append(data)
            
        with open(os.path.join(save_dir, "problems.js"), "w", encoding="utf8") as f:
            json.dump(res_list, f, ensure_ascii=False, indent=4)
        