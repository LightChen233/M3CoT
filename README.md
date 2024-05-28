<!--
 * @Author: Qiguang Chen
 * @LastEditors: Qiguang Chen
 * @Date: 2024-05-23 20:24:16
 * @LastEditTime: 2024-05-26 18:09:00
 * @Description: 
 * 
-->

<p align="center">
<h1 align="center"> <img src="image/unicorn.svg" alt="SVG Image"> M<sup>3</sup>CoT: A Novel Benchmark for Multi-Domain Multi-step Multi-modal Chain-of-Thought</h1>
</p>
<p align="center">
  	<a href="https://img.shields.io/badge/version-v0.0.1-blue">
      <img alt="version" src="https://img.shields.io/badge/version-v0.0.1-blue?color=FF8000?color=009922" />
    </a>
    <a >
       <img alt="PRs-Welcome" src="https://img.shields.io/badge/PRs-Welcome-blue" />
  	</a>
   	<a href="https://github.com/LightChen233/M3CoT/stargazers">
       <img alt="stars" src="https://img.shields.io/github/stars/LightChen233/M3CoT" />
  	</a>
  	<a href="https://github.com/LightChen233/M3CoT/network/members">
       <img alt="FORK" src="https://img.shields.io/github/forks/LightChen233/M3CoT?color=FF8000" />
  	</a>
    <a href="https://github.com/LightChen233/M3CoT/issues">
      <img alt="Issues" src="https://img.shields.io/github/issues/LightChen233/M3CoT?color=0088ff"/>
    </a>
    <br />
</p>

<p align="center">
  	<b>
    [<a href="https://xxx">ArXiv</a>] | [<a href="https://huggingface.co/datasets/LightChen2333/M3CoT">🤗HuggingFace</a>] | [<a href="https://lightchen233.github.io/m3cot.github.io/">Website</a>]
    </b>
    <br />
</p>

🌟 Any contributions via PRs, issues, emails or other methods are greatly appreciated.

## 🔥News
- 🎖️ **Our work is accepted by ACL2024.**
- 🔥 **We have release benchmark on \[[🤗HuggingFace](https://huggingface.co/datasets/LightChen2333/M3CoT)\].**
- 🔥 **The paper is also available on \[[ArXiv](https://xxx)\].**

- 🔮 **Interactive benchmark website \& more exploration are available on \[[https://lightchen233.github.io/m3cot.github.io/](https://lightchen233.github.io/m3cot.github.io/)\].**
## 💡 Motivation
Multi-modal Chain-of-Thought (MCoT) requires models to leverage knowledge from both textual and visual modalities for step-by-step reasoning, which gains increasing attention. 
Nevertheless, the current MCoT benchmark still faces some challenges: (1) **absence of visual modal reasoning**, (2) **single-step visual modal reasoning**, and (3) **Domain missing**, thereby hindering the development of MCoT.	 
Motivated by this, we introduce a novel benchmark (M<sup>3</sup>CoT) to address the above challenges, advancing the multi-domain, multi-step, and multi-modal CoT.
Additionally, we conduct a thorough evaluation involving abundant MCoT approaches on Vision Large Language Models (VLLMs). 
In addition, we highlight that the current VLLMs still struggle to correctly reason in M<sup>3</sup>CoT and there remains a large gap between existing VLLMs and human performance in M<sup>3</sup>CoT, despite their superior results on previous MCoT benchmarks. 
To our knowledge, we take the first meaningful step toward the multi-domain, multi-step, and multi-modal scenario in MCoT.
We hope that M<sup>3</sup>CoT can serve as a valuable
resource, providing a pioneering foundation in multi-domain, multi-step, multi-modal chain-of-thought research.



## 🎯 Installation

### 1. Dataset Preparation
#### Load Dataset from Huggingface
```python 
import datasets
dataset = datasets.load_dataset("LightChen2333/M3CoT")
```

#### Load Dataset from Google Drive 
Please download the corresponding data set from [Here](https://drive.google.com/file/d/1v2ysvsKHJ8-ugnxwseaN28s6BZmHlpKN) and place the unzipped content in the `data` folder.

```python 
import datasets
dataset = datasets.load_dataset("data/m3cot.py")
```

In addition, we also hope that you will use our M3CoT class to better manage and analyze data. Our class supports two initialization formats:
```python 
import datasets
from utils.data import M3CoT
dataset = datasets.load_dataset("data/m3cot.py")
prepared_dataset = M3CoT(dataset=dataset)
```

And
```python 
from utils.data import M3CoT
prepared_dataset = M3CoT(data_path="data")
```
### 2. Install from git
M3CoT requires `Python>=3.10`, and `torch>=2.0`.
```bash 
git clone https://github.com/LightChen233/M3CoT.git && cd M3CoT/
pip install -r requirements.txt
```
### 3. Evaluation for reproduction
```bash
python evaluate.py --setting zero-shot \
                   --model gpt4v \
                   --prompt cot \
                   --metric_by topic
```
where `--setting` can be selected from `[zero-shot, few-shot, tool-usage]`. `--metric_by` can be selected from `[topic, domain, all]`

For `zero-shot` setting:
  - `--model` can be selected from `[kosmos-2, cogvlm, gemini, gpt4v, instruct-blip-7b, instruct-blip-13b, llava-7b, llava-13b, openflamingo]`
  - `--prompt` can be selected from `[direct, cot, ccot, dsp]`

<!-- For `few-shot` setting:
  - `--model` can be selected from `[gpt4v, llava-7b, llava-13b, openflamingo]`
  - `--prompt` can be selected from `[image-few-shot, text-few-shot]`

For `tool-usage` setting:
  - `--model` can be selected from `[chameleon, hugginggpt, visualchatgpt, idealgpt]`
  - `--prompt` is needless to be assigned -->

### 4. Evaluation for your results
```bash
python evaluate.py --setting custom \
                   --metric_path [JSONL_PATH]
```
Among them, each line of file in `jsonl` must meet the following format:
```json
{
  "id": "[ID]",
  "choices": ["[CHOICE1]", "[CHOICE2]", ...],
  "answer": "A/B/C/...",
  "domain": "[DOMAIN]",
  "topic": "[TOPIC]",
  "messages": [
    "[QUESTION]",
    "[ANSWER]"
  ]
}
```

## 🖨️File Structure

```yaml
root
├── data           # data folder where the dataset is loaded
├── experiment     # All experimental data
│   ├── zero-shot         # Experimental results under zero-shot setting. Subfolders are for each model, and each model folder contains the results of three prompts.
│   ├── few-shot          # Experimental results under few-shot setting.
│   └── tool-usage        # Experimental results under tool-usage setting.
├── utils          # Tool library folder
│   ├── common_tool.py    # Some common utility functions
│   ├── data.py           # Dataset loading class
│   ├── gemini_request.py # Gemini request tool
│   ├── image_tool.py     # Image processing function.
│   └── metric.py         # Indicator calculation tool.
├── scripts
│   ├── load_dataset.py   # Example script to load a dataset
│   └── parse_to_sqa_format.py   # Convert dataset to ScienceQA format
└── evaluate.py     # Evaluation script
```

<!-- ├── mmcot_code      # Modification of MM-CoT finetuning code on our data set. For specific test commands, please see the corresponding README.
├── zero_shot_code  # Script for zero-shot testing
│   ├── gpt4v              # gpt4v test script folder. For specific test commands, please see the corresponding README.
│   ├── llava              # llava test script folder. For specific test commands, please see the corresponding README. -->

## ✒️ Reference
If you find this project useful for your research, please consider citing the following paper:

```
@inproceedings{chen-etal-2024-m3cot,
    title = "M$^3$CoT: A Novel Benchmark for Multi-Domain Multi-step Multi-modal Chain-of-Thought",
    author = "Chen, Qiguang  and
      Qin, Libo  and
      Zhang, Jin  and
      Chen, Zhi  and
      Xu, Xiao  and
      Che, Wanxiang",
    booktitle = "Proc. of ACL",
    year = "2024",
}
```

## 📲 Contact

Please create Github issues here or email [Qiguang Chen](mailto:charleschen2333@gmail.com) if you have any questions or suggestions. 

