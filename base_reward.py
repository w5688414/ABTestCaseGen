import os
import time
import subprocess
import json
import tempfile
import uuid
import shutil
import re
import random
import ast

from test_case_cov_reward import extract_code_block, check_assert
from data_util import read_jsonl, write_to_jsonl


def compute_time_and_reward(solution_str, ground_truth) -> float:
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
        duration = float('inf')  # 初始化为无穷大，表示未成功执行
        try:
            start_time = time.perf_counter()
            result = subprocess.run(
                cov_command, 
                cwd=tmp_dir, 
                capture_output=True, 
                env=env, # 传入环境变量
                timeout=5  # 代替原来的 TimeoutHandler
            )
            end_time = time.perf_counter()
            duration = end_time - start_time
            # breakpoint()
        except subprocess.TimeoutExpired:
            return {"reward": 0.05, "duration": 5.0} # 超时直接给 0 分，持续时间记为 5 秒（超时时间）
        
        cov_json_path = os.path.join(tmp_dir, 'coverage.json')
        report_json_path = os.path.join(tmp_dir, 'report.json')
        if not os.path.exists(cov_json_path) or not os.path.exists(report_json_path):
            return {"reward": 0.3, "duration": duration} # 执行成功，但覆盖率/报告生成失败 (防崩底线)，持续时间记录实际执行时间
            
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
        final_reward = correct_score + 0.5 * (line_cov * 0.7 + branch_cov * 0.3) # 综合行覆盖率,分支覆盖率,case正确率给出奖励
        return {"reward": final_reward, "duration": duration}

    finally:
        # 无论评估成功与否，强制清理临时文件以释放磁盘空间
        shutil.rmtree(tmp_dir, ignore_errors=True)

if __name__=="__main__":
    data_list = read_jsonl('outputs/train_results_base.json')
    for item in data_list:
        base_reward = compute_time_and_reward(item['output'], {"code": item["solutions"][0]})
        print(base_reward)
        item["baseline"] = base_reward
    print("total num of files:", len(data_list))
    write_to_jsonl('data/train_results_base_with_base_reward.jsonl', data_list)
