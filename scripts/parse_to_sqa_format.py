'''
Author: Qiguang Chen
LastEditors: Qiguang Chen
Date: 2023-12-10 14:55:25
LastEditTime: 2023-12-10 14:56:11
Description: 

'''
from utils.data import M3CoT


data = M3CoT()
data.save_as_scienceqa_format("sqa_format_m3qa")