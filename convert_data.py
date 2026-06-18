# prepare_data.py
import pandas as pd
from datasets import load_dataset
import os
import ast
from tqdm import tqdm 

def format_prompt(problem_description, solution_code):
    """
    构造供 Actor 学习的 Prompt。
    为了增加难度和针对性，可以同时提供题目描述和一段待测试的代码（例如正确的或有Bug的代码）。
    """
    prompt = (
        f"You are an expert software tester. "
        f"Given the following competitive programming problem description and a Python solution, "
        f"generate a valid, challenging test case (both input and expected output) to verify its correctness.\n\n"
        f"Problem:\n{problem_description}\n\n"
        f"Solution Code:\n{solution_code}\n\n"
        f"Please output your test case inside <testcase>...</testcase> tags."
    )
    return prompt


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

def main():
    # 假设使用 HuggingFace 上的类似 Codeforces 数据集
    # 这里以结构类似的数据集为例，你需要根据具体的 dataset splits 调整
    # dataset = load_dataset("deepmind/code_contests", split="train") # 仅做示例
    dataset = load_dataset("MatrixStudio/Codeforces-Python-Submissions", split="train")
    
    data_list = []
    for item in tqdm(dataset):
        # 提取题目描述和某个 Python 提交
        desc = item['description']
        
        # 假设我们取第一个正确的 Python 解决方案作为上下文
        if len(item['solutions']['solution']) > 0 and item['solutions']['language'][0] == 1:
            # breakpoint()
            sol = item['solutions']['solution'][0]
            name = item['name']
            data_source='Codeforces-Python-Submissions'
            if not is_python3(sol):
                print(f'{name} not a valid python3 code, skip')
                continue
            prompt = format_prompt(desc, sol)
            if len(prompt)>4096:
                print("skip, prompt lenght:", len(prompt))
                # breakpoint()
                continue
                
            # print("promot:", prompt)
            # print("solution:", sol)
            data_list.append({
                "data_source": data_source,
                "prompt": [{
                        "role": "user",
                        "content": prompt
                    }],
                # "problem_id": item['name'],
                "reward_model": {
                    "style": "rule",
                    "ground_truth": sol
                },
                "extra_info": {
                    # 'split': split,
                    'index': item['name']
                }
            })
    print(f"total data num: {len(data_list)}")
    df = pd.DataFrame(data_list)
    
    # 划分 train 和 test，并保存为 verl 需要的 parquet 格式
    train_df = df.sample(frac=0.9, random_state=42)
    test_df = df.drop(train_df.index)
    
    os.makedirs("./data/codeforces_testgen", exist_ok=True)
    train_df.to_parquet("./data/codeforces_testgen/train.parquet")
    test_df.to_parquet("./data/codeforces_testgen/test.parquet")
    print("Data processing complete. Saved to Parquet.")

if __name__ == "__main__":
    main()