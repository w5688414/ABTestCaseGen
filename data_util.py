import json
import ast

def read_jsonl(path):
    data=[]
    with open(path,'r') as f:
        for line in f:
            data.append(json.loads(line))
    return data


def write_to_jsonl(file_path, list_data, mode='w'):
    with open(file_path, mode, encoding='utf-8') as f:
        for item in list_data:
            json_string = json.dumps(item, ensure_ascii=False)
            f.write(json_string + '\n')


def check_assert(code_content):
    try:    
        tree = ast.parse(code_content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assert):
                return True
        return False
    except Exception:
        return False