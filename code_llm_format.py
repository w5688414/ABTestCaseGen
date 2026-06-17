from datasets import load_dataset
from openai import OpenAI
import re
import json
import time
from tqdm import tqdm 

# case_prompt="""Imagine you are a programmer.
# Please wrap the following code in a function, and then write the input as a parameter passing form.
# Generate the code ONLY. No other explanation or words attached!
# {solution}
# """

case_prompt="""you are a programmer. Please wrap the following code in a Solution class, and then write the input as a parameter passing form, output as the return value.
Generate the code ONLY. No other explanation or words attached!
{solution}
"""

def zhipu_gen(prompt):
    from zai import ZhipuAiClient
    client = ZhipuAiClient(api_key="7c817b420d84456f9ff6b05ace4ab261.TH0jmrhKFxrXkL2b")
    response = client.chat.completions.create(
        model="glm-5.1",
        messages=[
            # {
            #     "role": "system",
            #     "content": "你是一个有用的AI助手。"
            # },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.1
    )

    # 获取回复
    result = response.choices[0].message.content
    return result




def get_openai_gen(prompt):
    client = OpenAI(
        # base_url="http://10.133.32.190:2888/v1",
        base_url="https://ph8.co/openai/v1",
        api_key="sk-a7f9638e221249d396af43a995cf377c",
    )
    completion = client.chat.completions.create(
        # model="MiniMaxM25", # 必须与启动时的 model 名字一致
        model="gemma-4-26b-a4b-it",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,
        # max_tokens=512
    )

    model_output = completion.choices[0].message.content
    return model_output


def write_to_jsonl(file_path, list_data, mode='w'):
    with open(file_path, mode, encoding='utf-8') as f:
        for item in list_data:
            json_string = json.dumps(item, ensure_ascii=False)
            f.write(json_string + '\n')

def read_jsonl(file_path):
    """
    读取 jsonl 文件并返回一个对象列表。
    """
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            # 确保跳过空行
            if line.strip():
                data.append(json.loads(line))
    return data

def extract_python_code(python_str):
    match = re.search(r"```python\s*(.*?)\s*```", python_str, re.DOTALL)

    if match:
        python_code = match.group(1)
        return python_code

if __name__=="__main__":
    # apps = load_dataset("codeparrot/apps", split="all", trust_remote_code=True)
    start_idx=3000
    end_idx = -1
    data_path = "/workspace/verl/Agent-RL/data/python3_cases_train.jsonl"
    # data_path = "/workspace/verl/Agent-RL/data/python3_cases_test.jsonl"
    apps = read_jsonl(data_path)[start_idx:end_idx]

    list_data = []
    for item in tqdm(apps):
        question = item["question"] 
        try:
            if len(item["solutions"].strip())==0:
                continue
            solutions = eval(item["solutions"])
            prompt = case_prompt.format(solution=solutions[0])
            # result = zhipu_gen(prompt)
            time.sleep(0.5)
            result = get_openai_gen(prompt)
            python_code = extract_python_code(result)
            print(result)
            output = {}
            output.update(item)
            output['solutions']=[python_code]
            list_data.append(output)
            write_to_jsonl(f"data/python3_cases_format_python_train_{start_idx}_{end_idx}.jsonl", list_data, 'w')
            # print(len(solutions))
        except Exception as e:
            print(e)
            continue
        