'''
Author: Qiguang Chen
LastEditors: Qiguang Chen
Date: 2023-12-18 14:54:57
LastEditTime: 2024-05-23 15:51:27
Description: 

'''
import json

import asyncio
import os
import random
import time
import PIL.Image
import textwrap
from IPython.display import Markdown
import base64
import fire

from tqdm import tqdm
from utils.common_tool import read_jsonl

from utils.data import M3QA


def retry_with_exponential_backoff(
    func,
    initial_delay: float = 1,
    exponential_base: float = 2,
    jitter: bool = True,
    max_retries: int = 10,
    errors: tuple = (Exception,),
    # errors: tuple = (openai.error.RateLimitError,),
):
    """Retry a function with exponential backoff."""
 
    def wrapper(*args, **kwargs):
        # Initialize variables
        num_retries = 0
        delay = initial_delay
 
        # Loop until a successful response or max_retries is hit or an exception is raised
        while True:
            try:
                return func(*args, **kwargs)
 
            # Retry on specific errors
            except errors as e:
                # Increment retries
                num_retries += 1
 
                # Check if max retries has been reached
                if num_retries > max_retries:
                    raise Exception(
                        f"Maximum number of retries ({max_retries}) exceeded."
                    )
                else:
                    print(e)
                    if "response.prompt_feedback" in str(e) or "list index out of range" in str(e) or "An internal error has occurred" in str(e):
                        return "REJECT"
                    print("Retrying\t\t", args, kwargs)
                # Increment the delay
                delay *= exponential_base * (1 + jitter * random.random())
 
                # Sleep for the delay
                time.sleep(delay)
 
            # Raise exceptions for any errors not specified
            except Exception as e:
                raise e
 
    return wrapper


def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

import google.generativeai as genai

class MMRequestor:
    def __init__(self,
                 model_type="gpt4-v",
                 model_name="gemini-pro-vision",
                 api_key="YOUR_API_KEY",
                 enable_multi_turn=False) -> None:
        self.model_type = model_type
        self.model_name = model_name
        self.enable_multi_turn = enable_multi_turn
        if model_type == "gpt4-v":
            from openai import OpenAI
            client = OpenAI(api_key=api_key, api_base="https://lonlie.plus7.plus/v1")
            self.requestor = client
            if enable_multi_turn:
                self.chat = []
        elif model_type == "gemini-v":
            genai.configure(api_key=api_key)
            self.requestor = genai.GenerativeModel(model_name)
            if enable_multi_turn:
                raise ValueError("Multiple turn dialog is not supported for Gemini-v")
            # self.chat = self.requestor.start_chat(history=[])
        else:
            raise ValueError("Not Supported other model besides ['gpt4-v', 'gemini-v']")
    
    @retry_with_exponential_backoff
    def request(self, prompt, image_path):
        if self.model_type == "gpt4-v":
            # "gpt-4-vision-preview"
            base64_image = encode_image(image_path)
            self.chat.append({
                "role": "user",
                "content": [{
                        "type": "text",
                        "text": prompt,
                    }, {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    }, ],
            })
            response = self.requestor.chat.completions.create(
                model=self.model_name,
                messages=self.chat,
                max_tokens=300,
                )
            if self.enable_multi_turn:
                self.chat.append({
                    "role": "assistant",
                    "content": [{
                        "type": "text",
                        "text": response.choices[0],
                    }]
                })
            else:
                self.chat = []
            return response.choices[0]
        elif self.model_type == "gemini-v":
            img = PIL.Image.open(image_path)
            response = self.requestor.generate_content([prompt, img])
            return response.text

    
    @retry_with_exponential_backoff
    def request_dsp(self, prompt, image_path):
        req_1 = prompt+"\nDescribe the image information relevant to the question. Do not answer the choice question directly. [Description]"
        if self.model_type == "gpt4-v":
            # "gpt-4-vision-preview"
            base64_image = encode_image(image_path)
            self.chat.append({
                "role": "user",
                "content": [{
                        "type": "text",
                        "text": req_1,
                    }, {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    }, ],
            })
            response = self.requestor.chat.completions.create(
                model=self.model_name,
                messages=self.chat,
                max_tokens=300,
                )
            if self.enable_multi_turn:
                self.chat.append({
                    "role": "assistant",
                    "content": [{
                        "type": "text",
                        "text": response.choices[0],
                    }]
                })
            else:
                self.chat = []
            return response.choices[0]
        elif self.model_type == "gemini-v":
            img = PIL.Image.open(image_path)
            response = self.requestor.generate_content([req_1, img])
            message = [["USER", prompt], ["ASSISTANT", response.text]]
            req_2 = prompt + f"\n[Description] {response.text}"
            req_2 += f"\n\nProvide your answer. Note, you must choose from the given options."
            response = genai.GenerativeModel("gemini-pro").generate_content([req_2])
            return message + [["USER", req_2], ["ASSISTANT", response.text]]

    @retry_with_exponential_backoff
    def request_ccot(self, prompt, image_path):
        req_1 = prompt+"""\n\n\nFor the provided image and its associated question, generate a scene graph in JSON format that includes the following:
1.Objects that are relevant to answering the question.
2.Object attributes that are relevant to answering the question.
3.Object relationships that are relevant to answering the question.

[Scene Graph]"""
        if self.model_type == "gpt4-v":
            # "gpt-4-vision-preview"
            base64_image = encode_image(image_path)
            self.chat.append({
                "role": "user",
                "content": [{
                        "type": "text",
                        "text": req_1,
                    }, {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    }, ],
            })
            response = self.requestor.chat.completions.create(
                model=self.model_name,
                messages=self.chat,
                max_tokens=300,
                )
            if self.enable_multi_turn:
                self.chat.append({
                    "role": "assistant",
                    "content": [{
                        "type": "text",
                        "text": response.choices[0],
                    }]
                })
            else:
                self.chat = []
            return response.choices[0]
        elif self.model_type == "gemini-v":
            img = PIL.Image.open(image_path)
            response = self.requestor.generate_content([req_1, img])
            message = [["USER", req_1], ["ASSISTANT", response.text]]
            req_2 = f"[Scene Graph]\n{response.text}\n\nUse the image and scene graph as context and answer the following question:\n\n"+ prompt + f"\n\nAnswer with the option's letter from the given choices directly."
            response = genai.GenerativeModel("gemini-pro").generate_content([req_2])
            return message + [["USER", req_2], ["ASSISTANT", response.text]]

#!/bin/bash

# Run this from the directory in which you saved your input images
# This script was written to run on Debian Linux. It may require updates
# to run on other platforms

# Test that the first image is present
# if [ ! -f "image0.jpeg" ]; then
#   echo "Could not find images in the current directory." >&2
#   exit 1
# fi

# API_KEY="YOUR_API_KEY"

def append_to_jsonl(data, filename: str) -> None:
    """Append a json payload to the end of a jsonl file."""
    json_string = json.dumps(data, ensure_ascii=False)
    with open(filename, "a", encoding="utf8") as f:
        f.write(json_string + "\n")
async def producer(queue, dataset, save_path, bar):
    if os.path.exists(save_path):
        last_request = [x["id"] for x in read_jsonl(save_path)]
    else:
        last_request = []
    for i, data in enumerate(dataset.data):
        if data["id"] in last_request:
            bar.update(1)
            continue
        if data['context'] != "":
            prompt = f"[Context]\n{data['context']}\n[Question]\n{data['question']}\n[Choices]\n"
        else:
            prompt = f"[Question]\n{data['question']}\n[Choices]\n"
        choices = ""
        for i in range(len(data["choices"])):
            choices += f"({chr(65+i)}) {data['choices'][i]}\n"
        prompt += choices
        # DSP
        
        print("Loaded\t\t#", data["id"])
        await queue.put({"index": i, "id": data["id"], "text": prompt, "image_path": data["image_path"]})
    # 所有项目都放入队列后，放入 None 表示完成
    print("Dataset Loaded.")
    await queue.put(None)


async def consumer(queue, save_path, bar):
    while True:
        # 从队列中获取项目
        item = await queue.get()
        if item is None:
            # None 表示没有更多的项目
            break
        text = item["text"]
        image_path = item["image_path"]
        model_type = "gemini-v"
        model_name = "gemini-pro-vision"
        api_key = "USER"
        enable_multi_turn = False
        print("Requesting\t\t#", item["id"])
        # await asyncio.sleep(5)  # 模拟异步操作
        requestor = MMRequestor(model_type=model_type,
                                model_name=model_name,
                                api_key=api_key,
                                enable_multi_turn=enable_multi_turn)
        result = requestor.request_dsp(
            prompt=text,
            image_path=image_path
        )
        append_to_jsonl({"id": item["id"], "prompt": text, "pred": result}, save_path)
        print("Saved\t\t#", item["id"])
        # 通知队列任务已完成
        bar.update(1)
        queue.task_done()


async def main(total, split=0):
    queue = asyncio.Queue(maxsize=20)  # 设置队列最大大小
    dataset = M3QA()
    dataset.select_by_split("test")
    save_path = "gemini/dsp.jsonl"
    step = int(len(dataset.data)/total)
    dataset.data = dataset.data[step*split:min(len(dataset.data), step*(split+1))]
    bar = tqdm(total=len(dataset.data), desc=f"Total: {total} Split: {split}")
    # 创建生产者和消费者任务
    producer_task = asyncio.create_task(producer(queue, dataset, save_path, bar))
    consumer_tasks = [asyncio.create_task(consumer(queue, save_path, bar)) for _ in range(15)]  # 创建5个消费者

    # 等待所有项目被处理
    await producer_task
    await queue.join()  # 等待队列被清空

    # 取消消费者任务
    for task in consumer_tasks:
        task.cancel()

def run(total=5, split=0):
    asyncio.run(main(total, split=split))

if __name__ == "__main__":
    fire.Fire(run)
    
