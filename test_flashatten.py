import torch
import torch.nn.functional as F
from torch.backends.cuda import sdp_kernel

def test_flash_attention():
    # 1. 硬件环境检查
    if not torch.cuda.is_available():
        print("❌ 错误: 未检测到 GPU。Flash Attention 需要 NVIDIA GPU (Ampere 架构或更高)。")
        return

    device = "cuda"
    gpu_name = torch.cuda.get_device_name()
    print(f"检测到 GPU: {gpu_name}")

    # 2. 定义输入数据 (Batch, Heads, Seq_len, Head_dim)
    # 注意：Flash Attention 通常要求 head_dim 是 8 的倍数（如 64, 128）
    query = torch.randn(2, 8, 1024, 64, dtype=torch.float16, device=device)
    key = torch.randn(2, 8, 1024, 64, dtype=torch.float16, device=device)
    value = torch.randn(2, 8, 1024, 64, dtype=torch.float16, device=device)

    # 3. 强制使用 Flash Attention 算子进行测试
    try:
        # 使用上下文管理器强制开启 flash_attention，关闭其他算子
        with sdp_kernel(enable_flash=True, enable_math=False, enable_mem_efficient=False):
            output = F.scaled_dot_product_attention(query, key, value)
            print("✅ 成功: Flash Attention 算子运行正常！")
            print(f"输出形状: {output.shape}")
            
    except RuntimeError as e:
        print("❌ 失败: Flash Attention 无法运行。")
        print(f"原因: {e}")
        print("\n提示: Flash Attention 通常需要 NVIDIA A100, H100 或 RTX 30/40 系列 GPU，"
              "且输入需要是 float16 或 bfloat16 类型。")

if __name__ == "__main__":
    test_flash_attention()