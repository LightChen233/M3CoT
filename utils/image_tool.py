'''
Author: Qiguang Chen
LastEditors: Qiguang Chen
Date: 2023-10-31 14:41:20
LastEditTime: 2023-10-31 14:41:24
Description: 

'''
from PIL import Image
import imagehash
def judge_images_equal(image_path1, image_path2):
    # 打开两个图片文件
    image1 = Image.open(image_path1).convert("L")  # 转换为灰度图像
    image2 = Image.open(image_path2).convert("L")

    # 计算感知哈希值
    hash1 = imagehash.phash(image1)
    hash2 = imagehash.phash(image2)

    # 比较哈希值是否相等
    return hash1 == hash2