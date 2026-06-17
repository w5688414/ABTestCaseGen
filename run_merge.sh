
project_name=llm
experiment_name=codeforces_testgen_grpo
python3 -m verl.model_merger merge \
    --backend fsdp \
    --local_dir checkpoints/${project_name}/${experiment_name}/global_step_300/actor \
    --target_dir checkpoints/${project_name}/${experiment_name}/global_step_300/actor/huggingface