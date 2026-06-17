from datasets import load_dataset

# 3. Construct the prompt requesting unit tests
prompt = f"""
Please write complete test cases to check the correctness of the following code.
You must use the unittest library in Python and create a comprehensive test class.

Code Context:
{sample_task['prompt']}
{sample_task['canonical_solution']}
"""

if __name__=="__main__":
    # 1. Load the HumanEval dataset from Hugging Face
    dataset = load_dataset("openai_humaneval", split="test")
    sample_task = dataset[0]  # Grab the first coding problem
    print(sample_task)