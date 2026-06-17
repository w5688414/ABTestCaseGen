import json
import requests

# SandboxFusion 服务的地址（根据你的实际部署情况修改端口或域名）
url = "http://localhost:8080/run_code"

# 编写你的测试代码（包含业务逻辑和测试用例）
test_code = """
def add(a, b):
    if a > 0:
        return a + b
    return b

def test_add():
    assert add(1, 2) == 3
    assert add(-1, 2) == 2
"""

# 构造请求体
payload = {
    "language": "pytest",
    "code": test_code,
    # 核心：传入自定义的 pytest 参数
    "args": [
        "--cov-branch", 
        "--json-report", 
        "--json-report-file=report.json"
    ],
    # 核心：执行完毕后把生成的 JSON 报告文件捞出来
    "fetch_files": ["report.json"]
}

# 发送 POST 请求
response = requests.post(url, json=payload)
result = response.json()

# 打印运行状态和标准输出
print("Status:", result.get("status"))
print("Stdout:\n", result.get("run_result", {}).get("stdout"))
print("Stderr:\n", result.get("run_result", {}).get("stderr"))

# 提取并打印返回的 json-report 内容
files = result.get("files", {})
breakpoint()
if "report.json" in files:
    print("\n--- JSON Report Content ---")
    report_content = files["report.json"]
    # 如果返回的是字节流或 base64，可能需要解码，通常高级沙箱会直接返回字符串或编码后的内容
    print(report_content)
else:
    print("\n[Warning] report.json not found in the response files.")