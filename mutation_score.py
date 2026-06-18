import ast
import importlib.util
import sys
import types
import textwrap

# =====================================================================
# 1. THE AST MUTATOR
# =====================================================================
class OperatorMutator(ast.NodeTransformer):
    """
    Traverses the AST and replaces specific binary operators 
    with alternative ones to create simulated bugs (mutants).
    """
    def __init__(self, target_lineno):
        self.target_lineno = target_lineno
        self.mutated = False

    def visit_BinOp(self, node):
        # Line-specific mutation so we can generate distinct mutants
        if node.lineno == self.target_lineno and not self.mutated:
            # Swap Add (+) with Sub (-), or Sub (-) with Add (+)
            if isinstance(node.op, ast.Add):
                node.op = ast.Sub()
                self.mutated = True
            elif isinstance(node.op, ast.Sub):
                node.op = ast.Add()
                self.mutated = True
        return self.generic_visit(node)

# =====================================================================
# 2. RUNTIME MUTANT EXECUTION ENVIRONMENT
# =====================================================================
def execute_test_on_mutant(original_code, test_code, lineno_to_mutate):
    """
    Parses the source code, mutates the AST at a specific line, 
    compiles it, executes the generated tests against it, 
    and checks if the mutant was 'killed' (detected by the test).
    """
    try:
        # Parse original code into an Abstract Syntax Tree
        tree = ast.parse(original_code)
        
        # Mutate the AST
        mutator = OperatorMutator(lineno_to_mutate)
        mutated_tree = mutator.visit(tree)
        ast.fix_missing_locations(mutated_tree)
        
        if not mutator.mutated:
            return "survived" # No mutation was applicable on this line

        # Compile mutated AST into an executable module object
        compiled_code = compile(mutated_tree, filename="<mutant>", mode="exec")
        mutant_module = types.ModuleType("mutant_module")
        exec(compiled_code, mutant_module.__dict__)
        
        # Inject the mutated module into the environment context of the test execution
        test_env = {"target": mutant_module, "assert_failed": False}
        
        # 【修复1】对 LLM 生成的 test_code 进行严格的缩进对齐，防止 IndentationError
        indented_test_code = textwrap.indent(textwrap.dedent(test_code), "    ")
        
        wrapped_test = f"try:\n{indented_test_code}\nexcept AssertionError:\n    assert_failed = True"
        
        # 执行测试
        exec(wrapped_test, test_env)
        
        # If the assertion tripped, the test caught the bug! Mutant Killed.
        return "killed" if test_env.get("assert_failed") else "survived"
        
    except AssertionError:
        # 显式捕获可能直接逃逸的断言
        return "killed"
    except Exception as e:
        # 【修复2】如果是由于算术错误（如变异导致除以0）或崩溃，算 killed。
        # 如果是 LLM 代码语法错/命名错，在 GRPO 中建议视作 survived 或在最外层给负分，防止 Reward Hack。
        if isinstance(e, (ZeroDivisionError, TypeError, ValueError)):
            return "killed"
        return "survived"

# =====================================================================
# 3. GRPO REWARD CALCULATOR
# =====================================================================
def compute_mutation_reward(original_code, candidate_test_suite, mutation_lines):
    """
    Computes the raw mutation coverage reward for GRPO.
    """
    # Quick syntax pass on the LLM's generated test suite
    try:
        ast.parse(candidate_test_suite)
    except SyntaxError:
        return -1.0 # Strict penalty for unparsable code

    total_mutants = 0
    killed_mutants = 0

    for line in mutation_lines:
        status = execute_test_on_mutant(original_code, candidate_test_suite, line)
        if status == "killed":
            killed_mutants += 1
            total_mutants += 1
        elif status == "survived":
            total_mutants += 1

    if total_mutants == 0:
        return 0.0
        
    return killed_mutants / total_mutants

# =====================================================================
# EXAMPLE WALKTHROUGH
# =====================================================================
if __name__ == "__main__":
    source_function = """
def calculate_net_income(revenue, expenses):
    return revenue - expenses
"""
    lines_to_mutate = [3]

    weak_test = """
result = target.calculate_net_income(100, 50)
assert result is not None
"""

    strong_test = """
result = target.calculate_net_income(100, 50)
assert result == 50
"""

    reward_A = compute_mutation_reward(source_function, weak_test, lines_to_mutate)
    reward_B = compute_mutation_reward(source_function, strong_test, lines_to_mutate)

    print(f"Candidate A (Weak Test) Reward: {reward_A}")   # Outputs 0.0
    print(f"Candidate B (Strong Test) Reward: {reward_B}") # Outputs 1.0