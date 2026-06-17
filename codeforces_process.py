from datasets import load_dataset
import ast
import json
from tqdm import tqdm 
from data_util import write_to_jsonl

def is_python3(code: str) -> bool:
    try:
        ast.parse(code)
        return True
    except SyntaxError as e:
        # print(code, e)
        return False

if __name__=="__main__":
    
    split='test'
    codeforces = load_dataset("MatrixStudio/Codeforces-Python-Submissions", split=split, trust_remote_code=True)
    count=0
    list_data = []
    for item in tqdm(codeforces):
        score = item["score"]
        verdict = item["verdict"]
        if verdict!="OK":
            continue
        description = item["problem-description"] 
        code = item["code"]
        if is_python3(code):
            count+=1
            list_data.append(item)
    print(f"Total cases: {len(codeforces)}, Python 3 cases: {count}, Ratio: {count/len(codeforces):.2%}")
    write_to_jsonl("python3_codeforces_cases_{split}.jsonl", list_data)