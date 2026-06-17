# prepare_data.py
import pandas as pd
from datasets import load_dataset
import os
import ast
from tqdm import tqdm 
import json

def read_jsonl(path):
    data=[]
    with open(path,'r') as f:
        for line in f:
            data.append(json.loads(line))
    return data


prompt = """Please write a test method given the following program under test and function description. Your answer should only at least one test input with assert statement.

Program under test:
----
{program}
----

Function description:
----
{description}
----

Your test method should begin with:
```python
def test_solution():
    solution=Solution()
    ...
```
"""
system_message="You are a professional who writes Python3 test methods."  

def is_python3(code: str) -> bool:
    """
    检查代码是否符合当前 Python 3 解释器的语法。
    （注：运行此函数的环境必须是 Python 3）
    """
    try:
        ast.parse(code)
        return True
    except SyntaxError:
        # 如果代码中包含 Python 2 独有的语法（如 print "hello"），
        # 或者本身就有语法错误，就会在这里被拦截。
        return False

def load_leetcode(dataset):
    data_list = []
    for i, item in tqdm(enumerate(dataset)):
        # 提取题目描述和某个 Python 提交
        desc = item['description']
        
   
        data_source='leetcode'  
        example = {
            "data_source": data_source,
            "prompt": [
                    {"role": "system", "content": system_message},
                    {
                    "role": "user",
                    "content": prompt.format(program=item['python_solution'],
                            description=item['description']
                            )
                    }
                ],
            "reward_model": {
                "style": "rule",
                "ground_truth": {
                    'code': item["python_solution"],
                    'func_name': item['func_name'],
                    'target_lines': item['target_lines']
                }
            },
            "extra_info": {
                # 'split': split,
                'name': item['task_title'],
                'index': i
            }
        }
        # breakpoint()
        data_list.append(example)
    return data_list

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

def main():
    apps_data = read_jsonl('/workspace/verl/Agent-RL/verl/data/python3_cases_format_python_0_1000_clean_main.jsonl')
    apps_data += read_jsonl('/workspace/verl/Agent-RL/verl/data/python3_cases_format_python_train_1000_3000_clean_main.jsonl')
    apps_data += read_jsonl('/workspace/verl/Agent-RL/verl/data/python3_cases_format_python_train_3000_-1_clean_main.jsonl')
    leetcode_data=read_jsonl('/workspace/verl/Agent-RL/TestEval/data/leetcode-py-all.jsonl')
    print(apps_data[0].keys())
    data_list = []
    data_list +=load_apps(apps_data)
    data_list +=load_leetcode(leetcode_data)
    print(f"total data num: {len(data_list)}")
    df = pd.DataFrame(data_list)
    
    # 划分 train 和 test，并保存为 verl 需要的 parquet 格式
    train_df = df.sample(frac=0.9, random_state=42)
    test_df = df.drop(train_df.index)
    
    os.makedirs("./data/mix_data", exist_ok=True)
    train_df.to_parquet("./data/mix_data/train.parquet")
    test_df.to_parquet("./data/mix_data/test.parquet")
    print("Data processing complete. Saved to Parquet.")

if __name__ == "__main__":
    main()