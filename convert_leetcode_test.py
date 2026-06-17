import pandas as pd
from datasets import load_dataset
import os
import ast
from tqdm import tqdm 
import json

def load_apps(dataset):
    data_list = []
    for item in tqdm(dataset):
        desc = item['question']
        data_source='apps'  
        prompt_text = prompt.format(program=item["solutions"][0], description=item['question'].split("-----Example-----")[0])
        if not item["solutions"][0]:
            print(f'{item["problem_id"]} has no solution, skip')
            continue
        data_list.append({
            "data_source": data_source,
            "prompt": [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt_text}
                ],
            "reward_model": {
                "style": "rule",
                "ground_truth":{
                    "code": item["solutions"][0]
                } 
            },
            "extra_info": {
                # 'split': split,
                'index': item['problem_id']
            }
        })
    return data_list

def write_to_json(data_list, output_path):
    with open(output_path, 'w') as f:
        for item in data_list:
            json.dump(item, f)
            f.write('\n')

def main():
    apps_data = read_jsonl('/workspace/verl/Agent-RL/verl/data/python3_cases_format_python_test_0_1000.jsonl')
    print(apps_data[0].keys())
    data_list = []
    data_list +=load_apps(apps_data)
    write_to_json(data_list,'data/apps_test.jsonl')
    