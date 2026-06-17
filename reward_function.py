# reward_function.py
import re
import subprocess
import tempfile

def extract_testcase(response_text):
    """从模型输出中提取测试用例"""
    match = re.search(r'<testcase>(.*?)</testcase>', response_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None

def compute_execution_score(testcase_str, solution_code):    
    score = 0.0
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=True) as code_file:
        code_file.write(solution_code)
        code_file.flush()
        
        try:
            # 运行目标代码，喂入生成的测试用例
            result = subprocess.run(
                ['python3', code_file.name],
                input=testcase_str,
                text=True,
                capture_output=True,
                timeout=2.0 # 严格控制超时
            )
            
            if result.returncode == 0:
                # 执行成功，给予基础分。
                # 进阶玩法：如果生成的测试用例触发了高代码覆盖率，或者成功让 Buggy 代码崩溃，则给予高分。
                score = 1.0 
            else:
                # 语法错误或执行异常
                score = -0.5
        except subprocess.TimeoutExpired:
            score = -1.0 # 超时惩罚
            
    return score

def codeforces_testcase_reward(data_source, solution_str, ground_truth, extra_info):
    reward = 0.0

    # print('model response:', solution_str)
    # print('ground truth', ground_truth)
    testcase = extract_testcase(solution_str)
    if not testcase:
        return -2.0
    reward = compute_execution_score(testcase, ground_truth)
    # print(""" Reward: {}""".format(reward))
    # print("""generated testcase: {}, Reward: {}""".format(testcase, reward))
    return reward

        
