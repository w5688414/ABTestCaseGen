
project_name=llm
experiment_name=leetcode_testgen_grpo
# checkpoint_num=500
# python3 -m verl.model_merger merge \
#     --backend fsdp \
#     --local_dir checkpoints/${project_name}/${experiment_name}/global_step_${checkpoint_num}/actor \
#     --target_dir checkpoints/${project_name}/${experiment_name}/global_step_${checkpoint_num}/actor/huggingface

# python -m test_vllm \
#     --model_name checkpoints/${project_name}/${experiment_name}/global_step_${checkpoint_num}/actor/huggingface \
#     --output_file ./outputs/test_results_${checkpoint_num}.json

# python evaluate.py --data_path ./outputs/test_results_${checkpoint_num}.json


# checkpoint_num=100
# python3 -m verl.model_merger merge \
#     --backend fsdp \
#     --local_dir checkpoints/${project_name}/${experiment_name}/global_step_${checkpoint_num}/actor \
#     --target_dir checkpoints/${project_name}/${experiment_name}/global_step_${checkpoint_num}/actor/huggingface

# python -m test_vllm \
#     --model_name checkpoints/${project_name}/${experiment_name}/global_step_${checkpoint_num}/actor/huggingface \
#     --output_file ./outputs/test_results_${checkpoint_num}.json

# python evaluate.py --data_path ./outputs/test_results_${checkpoint_num}.json --num_workers 5 2>&1 | tee logs/evaluate_qwen25_15_${checkpoint_num}.log


# python -m test_vllm \
#     --model_name /workspace/verl/models/Qwen2.5-1.5B-Instruct \
#     --output_file ./outputs/test_results_qwen25_15b.json
# python evaluate.py --data_path ./outputs/test_results_qwen25_15b.json --num_workers 10 2>&1 | tee logs/evaluate_qwen25_15b.log


# python -m test_vllm \
#     --model_name /workspace/verl/models/Qwen3.5-9B \
#     --output_file ./outputs/test_results_qwen3_9b.json
# python evaluate.py --data_path ./outputs/test_results_qwen3_9b.json 2>&1 | tee logs/evaluate_qwen3_9b.log


now=$(date "+%Y-%m-%d-%H-%M-%S")
echo "当前时间: $now"

for item in 200 300 400 500 600 700 800 900 1000 1080; do
    echo "Processing $item"
    checkpoint_num=$item
    python3 -m verl.model_merger merge \
        --backend fsdp \
        --local_dir checkpoints/${project_name}/${experiment_name}/global_step_${checkpoint_num}/actor \
        --target_dir checkpoints/${project_name}/${experiment_name}/global_step_${checkpoint_num}/actor/huggingface

    python3 -m test_vllm \
        --model_name checkpoints/${project_name}/${experiment_name}/global_step_${checkpoint_num}/actor/huggingface \
        --output_file ./outputs/test_results_${checkpoint_num}_$now.json

    python3 evaluate.py --data_path ./outputs/test_results_${checkpoint_num}_$now.json --num_workers 10 2>&1 | tee logs/evaluate_qwen25_15_${checkpoint_num}_$now.log
done









