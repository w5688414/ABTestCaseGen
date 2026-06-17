from openai import OpenAI
import ast
import json

base_url = "https://ph8.co/openai/v1" 
api_key = "sk-a7f9638e221249d396af43a995cf377c"

# base_url="http://10.133.0.138:12580/tingly/claude_code",
# api_key="tingly-box-eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbGllbnRfaWQiOiJ0aW5nbHktYm94IiwiZXhwIjoxNzcwOTc0MTYwLCJpYXQiOjE3NzA4ODc3NjB9.CFoNnoHB7QzQ7KPhBzrKSXL2yIRPTaYZGGmzmzdle7s", # vLLM 如果没设 key，随便填个字符串即可

client = OpenAI(
    # base_url="http://10.133.32.190:2888/v1",
    base_url=base_url,
    api_key=api_key
)

def is_python3(code: str) -> bool:
    """
    检查代码是否符合当前 Python 3 解释器的语法。
    （注：运行此函数的环境必须是 Python 3）
    """
    try:
        ast.parse(code)
        return True
    except SyntaxError as e:
        # 或者本身就有语法错误，就会在这里被拦截。
        print(code, e)
        # breakpoint()
        return False

def get_model_ouptut(prompt):

    completion = client.chat.completions.create(
        # model="MiniMaxM25", # 必须与启动时的 model 名字一致
        model="tingly/cc-haiku",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=512
    )

    model_output = completion.choices[0].message.content
    return model_output

case_prompt="""
Imagine you are a programmer that make mistakes in coding.
Generate a Python3 program for the problem.
Remember to contain the complete program including all the imports and function header in your response.
Generate the code ONLY. No other explanation or words attached!
{question}
"""

def write_to_jsonl(file_path, list_data):
    with open(file_path, 'w', encoding='utf-8') as f:
        for item in list_data:
            json_string = json.dumps(item, ensure_ascii=False)
            f.write(json_string + '\n')

if __name__=="__main__":
    from datasets import load_dataset
    split='test'
    apps = load_dataset("codeparrot/apps", split=split, trust_remote_code=True)
    count=0
    list_data = []
    for item in apps:
        question = item["question"] 
        try:
            if len(item["solutions"].strip())==0:
                continue
            solutions = eval(item["solutions"])
            print(len(solutions))
        except Exception as e:
            breakpoint()
        prompt = case_prompt.format(question=question)
        # print(prompt)
        # print(solutions)
        if is_python3(solutions[0]):
            count+=1
            list_data.append(item)
        # break
    print(f"Total cases: {len(apps)}, Python 3 cases: {count}, Ratio: {count/len(apps):.2%}")
    write_to_jsonl("python3_cases_{split}.jsonl", list_data)
    
