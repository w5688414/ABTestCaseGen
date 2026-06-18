def compute_delta_coverage_reward(generated_code, src_file, global_coverage_manager):
    """
    generated_code: 模型生成的单个测试用例代码
    src_file: 被测目标源文件
    global_coverage_manager: 全局覆盖率追踪器，维护着当前已覆盖的行/分支集合
    """
    # 1. 静态检查与编译
    if not syntax_check(generated_code):
        return -1.0  # 语法错误惩罚
        
    # 2. 动态运行测试
    success, run_log, coverage_result = execute_test(generated_code, src_file)
    if not success:
        return -0.5  # 运行时死循环或崩溃惩罚
        
    # 3. 提取当前用例覆盖集合
    current_covered = set(coverage_result.covered_lines + coverage_result.covered_branches)
    
    # 4. 获取当前轮次开始前的全局已覆盖集合
    init_covered = global_coverage_manager.get_baseline_coverage()
    
    # 5. 计算纯增量 Delta
    delta_set = current_covered - init_covered
    
    if len(delta_set) == 0:
        # 虽然运行成功，但没有贡献任何新覆盖
        reward = 0.05  # 给极小的鼓励分，鼓励其至少是个能跑通的合规代码
    else:
        # 根据行/分支赋予不同权重
        reward = 0.0
        for element in delta_set:
            if element.type == 'branch':
                reward += 3.0  # 分支权重高
            else:
                reward += 1.0  # 普通行
                
    # 6. 断言密度与长度约束
    assert_count = count_assertions_in_ast(generated_code)
    if assert_count == 0:
        reward *= 0.2  # 惩罚无断言的无效测试
        
    return reward