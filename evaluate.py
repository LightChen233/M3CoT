'''
Author: Qiguang Chen
LastEditors: Qiguang Chen
Date: 2023-10-31 19:05:13
LastEditTime: 2024-05-26 11:00:31
Description: 

'''
import os

import fire
from prettytable import PrettyTable
from utils.data import M3CoT
from utils.metric import MetricData

class MetricSetting():
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.setting_dict = {
            "zero-shot": {
                "kosmos-2": ["direct", "cot", "ccot", "dsp"],
                "cogvlm": ["direct", "cot", "ccot", "dsp"],
                "gemini": ["direct", "cot", "ccot", "dsp"],
                "gpt4v": ["direct", "cot", "ccot", "dsp"],
                "instruct-blip-7b": ["direct", "cot"],
                "instruct-blip-13b": ["direct", "cot", "ccot", "dsp"],
                "llava-7b": ["direct", "cot", "ccot", "dsp"],
                "llava-13b": ["direct", "cot", "ccot", "dsp"],
                "openflamingo": ["cot"]
            },
            "few-shot": {
                "gpt4v": ["image-few-shot", "text-few-shot"],
                "llava-7b": ["image-few-shot", "text-few-shot"],
                "llava-13b": ["image-few-shot", "text-few-shot"],
                "openflamingo": ["image-few-shot"]
            },
            "tool-usage": [
                "chameleon", "hugginggpt", "visualchatgpt", "idealgpt"
            ]
        }
    def get_dir(self, setting, model, prompt):
        if setting not in self.setting_dict:
            raise ValueError(f"Unkown setting '{setting}'. Setting are not in " + str(list(self.setting_dict.keys())))
        
        if setting == "tool-usage":
            if model not in self.setting_dict[setting]:
                raise ValueError(f"Unkown model '{model}'. Model are not in " + str(self.setting_dict[setting]))
            setting_path = f"{self.base_dir}/{setting}/{model}"
        else:
            if model not in self.setting_dict[setting]:
                raise ValueError(f"Unkown model '{model}'. Model are not in " + str(list(self.setting_dict[setting].keys())))
            if prompt not in self.setting_dict[setting][model]:
                raise ValueError(f"Unkown prompt '{prompt}'. Prompt are not in " + str(self.setting_dict[setting][model]))
            setting_path = f"{self.base_dir}/{setting}/{model}/{prompt}"
        
        return setting_path
def run(setting, model, prompt, print_latex_format=False,
        metric_by= "topic", # ["topic", "domain", "all"]
        metric_path=None
        ):
    dataset = datasets.load_dataset("data/m3cot.py")
    m3cot = M3CoT(dataset=dataset)
    if setting == "custom":
        if metric_path is None:
            ValueError("No evaluation path has been specified yet. Please use `--metric_path` to specify the path")
        metric_data = MetricData(metric_path, None)
    else:
        metric_setting = MetricSetting("experiment")
        metric_path = metric_setting.get_dir(setting, model, prompt)
        metric_data = MetricData(metric_path +".jsonl")

    m3cot.select_by_split("test")
    res = metric_data.metric(by=metric_by, map=m3cot)
    res_str = ""
    print(res)
    if metric_by == "topic":
        tb = PrettyTable(["domain", "topic", "Acc"])
        for domain in res.keys():
            for topic in res[domain]:
                # print(f'{domain}/{topic}\t Acc: {res[domain][topic]["acc"]*100.0:.2f}%')
                tb.add_row([domain, topic, f"{res[domain][topic]['acc']*100.0:.2f}"])
                res_str += f"{res[domain][topic]['acc']*100.0:.2f} & "
        print(tb)
    elif metric_by == "domain":
        tb = PrettyTable(["domain", "Acc"])
        for domain in res.keys():
            tb.add_row([domain, f"{res[domain]['acc']*100.0:.2f}"])
            res_str += f"{res[domain]['acc']*100.0:.2f} & "
        print(tb)
    res = metric_data.metric(by="all", map=m3cot)["total"]
    res_str += f'{res["acc"]*100.0:.2f}'
    if print_latex_format:
        print(res_str.strip(","))
    print(f'Total: {res["total"]}, Correct: {res["acc"]*100.0:.2f}%')
    
"""
python evaluate.py --setting zero-shot \
                   --model gpt4v \
                   --prompt cot \
                   --metric_by topic

"""
if __name__ == "__main__":
    fire.Fire(run)
