from datasets import load_dataset
from tqdm import tqdm
import random


def load_codeforces():
    SEED = 42
    random.seed(SEED)# 1. 加载APPS数据集（论文取3000问题子集的核心源数据）# split="all"：加载训练+测试集；trust_remote_code=True：适配数据集自定义格式
    # apps = load_dataset("codeparrot/apps", split="all", trust_remote_code=True)
    codeforces = load_dataset("MatrixStudio/Codeforces-Python-Submissions", split="train")
    print(codeforces[0]['prompt'])
    print(codeforces[0]['response'])
    print(codeforces[0]['code'])
    print(type(codeforces[0]), codeforces[0].keys())
    for k,v in codeforces[0].items():
        print(f"{k}: {v}")

if __name__=="__main__":
    # Load the full dataset
    # dataset = load_dataset("caijanfeng/CodeContests-O")

    # # Access different splits
    # train_data = dataset["train"]
    # test_data = dataset["test"]
    # valid_data = dataset["valid"]

    # # Example: Access a single problem
    # problem = train_data[0]
    # print(f"Problem: {problem['name']}")
    # print(f"Number of test cases: {len(problem['corner_cases'])}")
    # print(f"Number of iterations: {len(problem['results'])}")
    # print(problem.keys())
    load_codeforces()