import re
import time
from typing import Dict, Any

def leetcode_reward_function(solution_code: str, test_cases: list, metadata: Dict[str, Any]) -> float:
    """
    针对 LeetCode 任务的评估奖励计算
    """
    # 1. 基础检查：语法与静态分析
    if not solution_code.strip():
        return -1.0
    
    try:
        compile(solution_code, '<string>', 'exec')
    except SyntaxError:
        return -0.8  # 语法错误惩罚

    # 2. 动态执行：通过率计算
    passed_count = 0
    total_time = 0
    max_time_limit = metadata.get('timeout', 1.0)
    
    for case in test_cases:
        start_time = time.perf_counter()
        result = execute_with_sandbox(solution_code, case['input'], case['expected'])
        elapsed = time.perf_counter() - start_time
        
        if result['status'] == 'success':
            passed_count += 1
            total_time += elapsed
        elif result['status'] == 'timeout':
            return -0.5 # TLE 严重惩罚
            
    pass_rate = passed_count / len(test_cases)
    
    # 3. 效率与性能 Reward (仅在通过全部测试时激活)
    efficiency_bonus = 0
    if pass_rate == 1.0:
        # 假设题目预设的基准耗时为 baseline_t
        baseline_t = metadata.get('baseline_time', 0.1)
        efficiency_bonus = max(0, 0.2 * (1 - total_time / (baseline_t * len(test_cases))))

    # 4. 综合评分
    # 基础通过奖励 + 性能奖金 - 长度惩罚
    code_length_penalty = len(solution_code) * 0.0001
    total_reward = (pass_rate * 1.0) + efficiency_bonus - code_length_penalty
    
    return max(-1.0, total_reward)