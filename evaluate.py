import os
import subprocess
import json
import tempfile
import uuid
import shutil
import re
from tqdm import tqdm 
from data_util import read_jsonl, check_assert
from concurrent.futures import ProcessPoolExecutor, as_completed
import argparse

def extract_code_block(solution_str: str) -> str:
    """从 LLM 生成的回复中提取 Python 代码块"""
    if "```python" in solution_str:
        return solution_str.split("```python")[1].split("```")[0].strip()
    elif "```" in solution_str:
        return solution_str.split("```")[1].split("```")[0].strip()
    return solution_str.strip()


def compute_coverage(data_list) -> float:
    total_syn_correct = 0
    total_exec_correct = 0
    failed_count = 0
    total_line_cov=0
    total_branch_cov=0
    total_passed = 0
    total_cases = 0
    for item in tqdm(data_list):
        solution_str = item["output"]
        source_code = item["solutions"][0]
        func_name = item.get('func_name', 'solve')
    
        testcase_code = extract_code_block(solution_str)
        # print(f"Raw solution: {solution_str} Extracted Test Code:\n{testcase_code}\n")
        if not testcase_code:
            failed_count+=1
            continue


        # 1. 语法检查 (Syntax Check)
        try:
            compile(testcase_code, '<string>', 'exec')
            total_syn_correct+=1
        except SyntaxError:
            failed_count+=1
            continue
            

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
                '--json-report',
                '--json-report-file=report.json',
                f'--cov-report=json:{os.path.join(tmp_dir, "coverage.json")}',
                'test_target.py'
            ]
            result = subprocess.run(
                cov_command, 
                cwd=tmp_dir, 
                capture_output=True, 
                env=env, # 传入环境变量
                timeout=10  # 代替原来的 TimeoutHandler
            )
            report_json_path = os.path.join(tmp_dir, 'report.json')
            with open(report_json_path, 'r') as f:
                test_report = json.load(f)
            if 'failed' in test_report['summary']:
                failed_count += 1
            if 'passed' in test_report['summary']:
                passed = test_report['summary']["passed"]
                total_passed += passed
            total = test_report['summary']["total"]
            collected = test_report['summary']["collected"]
            total_cases += total
            print(f"Test results: Passed {total_passed}/{total_cases}")
            

            cov_json_path = os.path.join(tmp_dir, 'coverage.json')
            if os.path.exists(cov_json_path):
                with open(cov_json_path, 'r') as f:
                    cov_report = json.load(f)
                total_stmt=cov_report['totals']['num_statements']
                covered_stmt=cov_report['totals']['covered_lines']
                line_cov=covered_stmt/total_stmt
                total_branch=cov_report['totals']['num_branches']
                covered_branch=cov_report['totals']['covered_branches']
                branch_cov = covered_branch / total_branch if total_branch > 0 else 1.0
                total_line_cov+=line_cov
                total_branch_cov+=branch_cov

                total_exec_correct += 1
            else:
                print(result.stderr.decode())
                continue
        except Exception as e:
            print(f"Error processing item: {e}")
            continue
        finally:
            # 无论评估成功与否，强制清理临时文件以释放磁盘空间
            shutil.rmtree(tmp_dir, ignore_errors=True)

    syn_correct=total_syn_correct/len(data_list)
    exec_correct=total_exec_correct/len(data_list)
    print(f'Syntax Correctness: {syn_correct:.2%}')
    print(f'Executable Correctness: {exec_correct:.2%}')
    
    avg_line_cov=total_line_cov/len(data_list)
    avg_branch_cov=total_branch_cov/len(data_list)
    print(f'Average Line Coverage: {avg_line_cov:.2%}, Average Branch Coverage: {avg_branch_cov:.2%}')
    print(f'Test Case Pass Rate: {total_passed/total_cases:.2%}')
    return [avg_line_cov, avg_branch_cov]

def process_single_item(item):
    """处理单个数据项的核心函数，返回结果字典"""
    res = {
        "syn_correct": 0,
        "exec_correct": 0,
        "line_cov": 0.0,
        "branch_cov": 0.0,
        "passed": 0,
        "total": 0
    }
    failed_count = 0
    
    solution_str = item["output"]
    source_code = item["solutions"][0]
    testcase_code = extract_code_block(solution_str)

    if not testcase_code:
        return res

    # 1. 语法检查
    try:
        compile(testcase_code, '<string>', 'exec')
        res["syn_correct"] = 1
    except SyntaxError:
        return res

    # 2. 创建独立临时目录
    tmp_dir = os.path.join(tempfile.gettempdir(), f"verl_eval_{uuid.uuid4().hex}")
    os.makedirs(tmp_dir, exist_ok=True)

    try:
        under_test_path = os.path.join(tmp_dir, 'under_test.py')
        with open(under_test_path, 'w') as f:
            f.write(source_code)
            
        test_file_path = os.path.join(tmp_dir, 'test_target.py')
        with open(test_file_path, 'w') as f:
            # 这里的 import 逻辑取决于你的数据结构，假设 under_test.py 里有 Solution 类
            f.write(f"from under_test import Solution\n{testcase_code}")
            
        coveragerc_path = os.path.join(tmp_dir, '.coveragerc')
        with open(coveragerc_path, 'w') as f:
            f.write("[run]\nbranch = True\n")
        
        env = os.environ.copy()
        env['PYTHONPATH'] = tmp_dir
        
        cov_json_path = os.path.join(tmp_dir, 'coverage.json')
        cov_command = [
            'pytest', 
            '--cov=under_test', 
            '--cov-branch', 
            '--json-report',
            '--json-report-file=report.json',
            f'--cov-report=json:{cov_json_path}',
            'test_target.py'
        ]
        
        # 运行 pytest
        subprocess.run(
            cov_command, 
            cwd=tmp_dir, 
            capture_output=True, 
            env=env,
            timeout=10 
        )
        report_json_path = os.path.join(tmp_dir, 'report.json')
        with open(report_json_path, 'r') as f:
            test_report = json.load(f)

        passed = 0
        if 'failed' in test_report['summary']:
                failed_count += 1
        if 'passed' in test_report['summary']:
            passed = test_report['summary']["passed"]
        total = test_report['summary']["total"]
        collected = test_report['summary']["collected"]
        res["passed"]=passed
        res["total"]=total
        print(f"Test results: Passed {passed}/{total} (Collected: {collected})")
        
        if os.path.exists(cov_json_path):
            with open(cov_json_path, 'r') as f:
                cov_report = json.load(f)
            
            total_stmt = cov_report['totals']['num_statements']
            covered_stmt = cov_report['totals']['covered_lines']
            res["line_cov"] = covered_stmt / total_stmt if total_stmt > 0 else 0.0
            
            total_branch = cov_report['totals']['num_branches']
            covered_branch = cov_report['totals']['covered_branches']
            res["branch_cov"] = covered_branch / total_branch if total_branch > 0 else 1.0
            res["exec_correct"] = 1
            
    except Exception:
        pass
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
    return res

def compute_coverage_parallel(data_list, max_workers=None):
    """使用进程池并行计算"""
    total_syn_correct = 0
    total_exec_correct = 0
    total_line_cov = 0.0
    total_branch_cov = 0.0
    total_passed = 0.0
    total_cases = 0.0
    num_items = len(data_list)

    # 并行执行
    print(f"Starting parallel evaluation with {max_workers or 'default'} workers...")
    results = []
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        futures = {executor.submit(process_single_item, item): item for item in data_list}
        
        # 使用 tqdm 追踪进度
        for future in tqdm(as_completed(futures), total=num_items, desc="Evaluating"):
            try:
                res = future.result()
                total_syn_correct += res["syn_correct"]
                total_exec_correct += res["exec_correct"]
                total_line_cov += res["line_cov"]
                total_branch_cov += res["branch_cov"]
                total_passed += res["passed"]
                total_cases += res["total"]
            except Exception as e:
                print(f"Worker failed: {e}")

    # 计算最终指标
    syn_correct_rate = total_syn_correct / num_items
    exec_correct_rate = total_exec_correct / num_items
    avg_line_cov = total_line_cov / num_items
    avg_branch_cov = total_branch_cov / num_items

    print(f'\n--- Results ---')
    print(f'Syntax Correctness: {syn_correct_rate:.2%}')
    print(f'Executable Correctness: {exec_correct_rate:.2%}')
    print(f'Average Line Coverage: {avg_line_cov:.2%}')
    print(f'Average Branch Coverage: {avg_branch_cov:.2%}')
    print(f'Test Case Pass Rate: {total_passed/total_cases:.2%}')
    return [avg_line_cov, avg_branch_cov]


parser = argparse.ArgumentParser(description="A simple evaluation script")
parser.add_argument("--data_path", help="The data path",default="./outputs/python3_apps_test_checkpoint_500.jsonl")
parser.add_argument("--num_workers", type=int, default=-1, help="Number of parallel processes")


if __name__=="__main__":
    args = parser.parse_args()
    data_path = args.data_path
    print(data_path)
    data_list = read_jsonl(data_path)
    if args.num_workers>0:
        compute_coverage_parallel(data_list, max_workers=args.num_workers)
    else:
        compute_coverage(data_list)
    print("End of evaluation")