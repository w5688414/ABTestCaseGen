import os
import subprocess
import json
import tempfile
import uuid
import shutil
import re
import random
import ast


def extract_code_block(solution_str: str) -> str:
    """从 LLM 生成的回复中提取 Python 代码块"""
    if "```python" in solution_str:
        return solution_str.split("```python")[1].split("```")[0].strip()
    elif "```" in solution_str:
        return solution_str.split("```")[1].split("```")[0].strip()
    return solution_str.strip()


def check_assert(code_content):
    try:    
        tree = ast.parse(code_content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assert):
                return True
        return False
    except Exception:
        return False


def compute_reward(data_source, solution_str, ground_truth, extra_info) -> float:
    """
    Verl Reward 函数
    """
    target_line = int(ground_truth.get('target_line', -1))
    func_name = ground_truth.get('func_name', 'solve')
    source_code = ground_truth.get('code', '')
    
    testcase_code = extract_code_block(solution_str)
    if random.random() < 0.1:  # 10% 的概率打印原始解决方案和提取的测试代码，帮助调试
        print(f"Raw solution: {solution_str} Extracted Test Code:\n{testcase_code}\n")
    if not testcase_code or not check_assert(testcase_code):  # 简单检查是否包含 assert 语句
        return 0.0

    # 1. 语法检查 (Syntax Check)
    # try:
    #     compile(testcase_code, '<string>', 'exec')
    # except SyntaxError:
    #     return 0.0

    # 创建线程安全的独立临时目录，避免 RL 并发评估时发生冲突
    tmp_dir = os.path.join(tempfile.gettempdir(), f"verl_eval_{uuid.uuid4().hex}")
    os.makedirs(tmp_dir, exist_ok=True)
    
    try:
        # 写入被测代码
        under_test_path = os.path.join(tmp_dir, 'under_test.py')
        with open(under_test_path, 'w') as f:
            f.write(source_code)
            
        # 根据你的原始逻辑，构建导入语句
        test_import_simple = 'from under_test import Solution\n'
        test_code_exec = f"{test_import_simple}\n{testcase_code}\ntest_{func_name}()"
            
        # 3. 覆盖率检查 (Coverage Check)
        test_file_path = os.path.join(tmp_dir, 'test_target.py')
        with open(test_file_path, 'w') as f:
            f.write(f"{test_import_simple}\n{testcase_code}")
            
        # 生成一个基础的 .coveragerc 确保 branch coverage
        coveragerc_path = os.path.join(tmp_dir, '.coveragerc')
        with open(coveragerc_path, 'w') as f:
            f.write("[run]\nbranch = True\n")
            
        env = os.environ.copy()
        env['PYTHONPATH'] = tmp_dir
        cov_command = [
            'pytest', 
            '--cov=under_test', 
            '--cov-branch', 
            # '--cov-report=json:coverage.json',
            '--json-report',
            '--json-report-file=report.json',
            f'--cov-report=json:{os.path.join(tmp_dir, "coverage.json")}',
            'test_target.py'
        ]
        try:
            result = subprocess.run(
                cov_command, 
                cwd=tmp_dir, 
                capture_output=True, 
                env=env, # 传入环境变量
                timeout=5  # 代替原来的 TimeoutHandler
            )
        except subprocess.TimeoutExpired:
            return 0.05 # 运行超时
        
        
        cov_json_path = os.path.join(tmp_dir, 'coverage.json')
        report_json_path = os.path.join(tmp_dir, 'report.json')
        if not os.path.exists(cov_json_path) or not os.path.exists(report_json_path):
            return 0.3 # 执行成功，但覆盖率/报告生成失败 (防崩底线)
            
        with open(cov_json_path, 'r') as f:
            cov_report = json.load(f)
        
        with open(report_json_path, 'r') as f:
            test_report = json.load(f)

        summary = test_report.get('summary', {})
        passed = summary.get('passed', 0)
        total = summary.get('total', 0)
        # 只有在至少有一个测试用例且全部通过时才给正确分
        correct_score = 0.5 if (total > 0 and passed == total) else 0.0 # 全部测试通过才给基础分

        total_stmt=cov_report['totals']['num_statements']
        covered_stmt=cov_report['totals']['covered_lines']
        line_cov=covered_stmt/total_stmt
        total_branch=cov_report['totals']['num_branches']
        covered_branch=cov_report['totals']['covered_branches']
        branch_cov = covered_branch / total_branch if total_branch > 0 else 1.0
        print(f"Line Coverage: {line_cov:.2%}, Branch Coverage: {branch_cov:.2%}")
        return correct_score + 0.5 * (line_cov * 0.7 + branch_cov * 0.3) # 综合行覆盖率,分支覆盖率,case正确率给出奖励

    finally:
        # 无论评估成功与否，强制清理临时文件以释放磁盘空间
        shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__=="__main__":
    input_data = {
        "data_source": "leetcode",
        "solution_str":"def test_isMatch():\n    solution = Solution()\n    assert solution.isMatch('aa', 'a*') == True",
        "ground_truth":{
            "code": "import math\nimport itertools\nimport bisect\nimport collections\nimport string\nimport heapq\nimport functools\nimport sortedcontainers\nfrom typing import List, Dict, Tuple, Iterator\n\nclass Solution:\n  def isMatch(self, s: str, p: str) -> bool:\n    m = len(s)\n    n = len(p)\n    dp = [[False] * (n + 1) for _ in range(m + 1)]\n    dp[0][0] = True\n\n    def isMatch(i: int, j: int) -> bool:\n      return j >= 0 and p[j] == '.' or s[i] == p[j]\n\n    for j, c in enumerate(p):\n      if c == '*' and dp[0][j - 1]:\n        dp[0][j + 1] = True\n\n    for i in range(m):\n      for j in range(n):\n        if p[j] == '*':\n          noRepeat = dp[i + 1][j - 1]\n          doRepeat = isMatch(i, j - 1) and dp[i][j + 1]\n          dp[i + 1][j + 1] = noRepeat or doRepeat\n        elif isMatch(i, j):\n          dp[i + 1][j + 1] = dp[i][j]\n\n    return dp[m][n]\n",
            "func_name": "isMatch",
            "target_line": 6
        },
        "extra_info": {}
    }
    res = compute_reward(**input_data)
    print(res)