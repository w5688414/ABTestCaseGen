from vllm import LLM, SamplingParams
import json
import argparse
from transformers import AutoTokenizer
from data_util import read_json, read_jsonl
# model_name = "/workspace/verl/models/Qwen2.5-1.5B-Instruct"
# model_name = "/workspace/verl/models/Qwen3-1.7B"
# prompt="""You are an expert software tester. Given the following competitive programming problem description and a Python solution, generate a valid, challenging test case (both input and expected output) to verify its correctness.\n\nProblem:\nProblem description.\nVipul is a hardworking super-hero who maintains the bracket ratio of all the strings in the world. Recently he indulged himself in saving the string population so much that he lost his ability for checking brackets (luckily, not permanently ).Being his super-hero friend\xa0help him in his time of hardship. \n\nInput\n\nThe first line of the input contains an integer T denoting the number of test cases. The description of T test cases follows.\nThe first line of each test case contains a single string S denoting the string to be checked.\n\n\nOutput\n\nFor each test case, output a single line printing "YES" or "NO" (without " " and in uppercase only) , denoting if the brackets in the given string is balanced or not .\n\n\nConstraints\n\n1 ≤ T ≤ 10\n1 ≤ length of S ≤ 60\n\n\nExample\nInput:\n3\n((()))\n(())()\n()(()\n\nOutput:\nYES\nYES\nNO\n\n\xa0\n\nExplanation\nExample is self-explanatory.\n\nSolution Code:\nfor _ in range(input()):\n    try:\n        eval(raw_input())\n        print \'YES\'\n    except TypeError:\n        print \'YES\'\n    except:\n        print \'NO\'\n\nPlease output your test case inside <testcase>...</testcase> tags.
# """

# prompts = [
#         [                
#             {
#                 "role": "user",
#                 "content": prompt
#             }
#         ]
# ]

parser = argparse.ArgumentParser(description="A simple greeting script")
parser.add_argument("--model_name", help="The model path",default="/workspace/verl/Agent-RL/verl/checkpoints/llm/leetcode_testgen_grpo/global_step_400/actor/huggingface")
parser.add_argument("--output_file", help="The ouput data path",default="./outputs/python3_apps_test_checkpoint_500.jsonl")
parser.add_argument("-v", "--verbose", action="store_true", help="Increase output verbosity")



prompt = """Please write a test method given the following program under test and function description. Your answer should only contain one test input with assert.

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

def write_to_json(data_list, output_path):
    with open(output_path, 'w') as f:
        for item in data_list:
            json.dump(item, f)
            f.write('\n')

if __name__=="__main__":
    args = parser.parse_args()

    # 4. Use the arguments
    if args.verbose:
        print(f"Verbose mode enabled. Preparing to greet {args.name}...")

    # print(f"Hello, {args.name}!")
    

    # model_name = "/workspace/verl/Agent-RL/verl/checkpoints/llm/leetcode_testgen_grpo/global_step_400/actor/huggingface"
    model_name = args.model_name
    output_path = args.output_file
    # model_name = "/workspace/verl/models/Qwen3-1.7B"
    # model_name = "/workspace/verl/models/Qwen2.5-1.5B-Instruct"
    sampling_params = SamplingParams(max_tokens=2048, temperature=0.1, top_p=0.95)
    # data_list = read_jsonl('/workspace/verl/Agent-RL/verl/data/python3_cases_format_python_test_0_1000.jsonl')
    # data_list += read_jsonl('/workspace/verl/Agent-RL/verl/data/python3_cases_format_python_test_1000_3000.jsonl')
    # data_list = read_jsonl('/workspace/verl/Agent-RL/verl/data/python3_cases_format_python_0_1000_clean_main.jsonl')
    data_list = read_json("/workspace/verl/Agent-RL/UnLeakedTestBench/datasets/PLT.jsonl")

    llm = LLM(model=model_name,gpu_memory_utilization=0.5)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    messages = []
    for item in data_list:
        if "solutions" in item:
            prompt_text = prompt.format(program=item["solutions"][0], description=item['question'].split("-----Examples-----")[0].split('-----Example-----'))
        else:
            prompt_text = prompt.format(program=item["code"], description=item['prompt'])
            # breakpoint()
        message = [{"role": "system", "content": system_message},
                   {"role": "user", "content": prompt_text}
                ]
        messages.append(message)

    outputs = llm.chat(messages=messages, sampling_params=sampling_params)

    for i, output in enumerate(outputs):
        
        prompt_token_ids = output.prompt_token_ids
        decoded_text = tokenizer.decode(prompt_token_ids)
        generated_text = output.outputs[0].text
        if i<3:
            print(f"Prompt: {decoded_text!r}, Generated text: {generated_text!r}")
        data_list[i]['output']=generated_text

    write_to_json(data_list, output_path)
    

