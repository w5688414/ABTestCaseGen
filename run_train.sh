


# python3 -c "import transformers; transformers.pipeline('text-generation', model='/workspace/verl/models/Qwen2.5-1.5B-Instruct')"


# PYTHONUNBUFFERED=1 python3 -m verl.trainer.main_ppo \
#  data.train_files=$HOME/data/gsm8k/train.parquet \
#  data.val_files=$HOME/data/gsm8k/test.parquet \
#  data.train_batch_size=256 \
#  data.max_prompt_length=512 \
#  data.max_response_length=512 \
#  actor_rollout_ref.model.path=/workspace/verl/models/Qwen2.5-1.5B-Instruct \
#  actor_rollout_ref.actor.optim.lr=1e-6 \
#  actor_rollout_ref.actor.ppo_mini_batch_size=64 \
#  actor_rollout_ref.actor.ppo_micro_batch_size_per_gpu=4 \
#  actor_rollout_ref.rollout.name=vllm \
#  actor_rollout_ref.rollout.log_prob_micro_batch_size_per_gpu=8 \
#  actor_rollout_ref.rollout.tensor_model_parallel_size=1 \
#  actor_rollout_ref.rollout.gpu_memory_utilization=0.4 \
#  actor_rollout_ref.ref.log_prob_micro_batch_size_per_gpu=4 \
#  critic.optim.lr=1e-5 \
#  critic.model.path=/workspace/verl/models/Qwen2.5-1.5B-Instruct \
#  critic.ppo_micro_batch_size_per_gpu=4 \
#  algorithm.kl_ctrl.kl_coef=0.001 \
#  trainer.logger=console \
#  trainer.val_before_train=False \
#  trainer.n_gpus_per_node=1 \
#  trainer.nnodes=1 \
#  trainer.save_freq=100 \
#  trainer.test_freq=10 \
#  trainer.total_epochs=15 2>&1 | tee verl_demo.log


# run_grpo_testgen.sh

# 环境变量设置，针对大规模 GPU 集群优化
# export NCCL_DEBUG=INFO
# export VLLM_ATTENTION_BACKEND=FLASH_ATTN

#  actor_rollout_ref.rollout.max_model_len=8192 \
#  actor_rollout_ref.rollout.max_num_batched_tokens=8192 \
#  actor_rollout_ref.rollout.response_length=2048 \

export WANDB_API_KEY=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
# YOUR_PROJECT_NAME='llm'
# YOUR_RUN_NAME='codeforces_testgen_grpo'
# PYTHONUNBUFFERED=1 python3 -m verl.trainer.main_ppo \
#  algorithm.adv_estimator=grpo \
#  data.train_files=./data/codeforces_testgen/train.parquet \
#  data.val_files=./data/codeforces_testgen/test.parquet \
#  data.train_batch_size=64 \
#  data.max_prompt_length=4096 \
#  data.max_response_length=512 \
#  data.filter_overlong_prompts=True \
#  actor_rollout_ref.model.path=/workspace/verl/models/Qwen3-1.7B \
#  actor_rollout_ref.actor.optim.lr=1e-6 \
#  actor_rollout_ref.actor.ppo_mini_batch_size=64 \
#  actor_rollout_ref.actor.ppo_micro_batch_size_per_gpu=4 \
#  actor_rollout_ref.rollout.name=vllm \
#  actor_rollout_ref.rollout.log_prob_micro_batch_size_per_gpu=8 \
#  actor_rollout_ref.rollout.tensor_model_parallel_size=1 \
#  actor_rollout_ref.rollout.gpu_memory_utilization=0.5 \
#  actor_rollout_ref.ref.log_prob_micro_batch_size_per_gpu=4 \
#  reward.custom_reward_function.path="reward_function.py" \
#  reward.custom_reward_function.name=codeforces_testcase_reward \
#  algorithm.use_kl_in_reward=False \
#  trainer.logger=["console","wandb"] \
#  trainer.project_name=$YOUR_PROJECT_NAME \
#  trainer.experiment_name=$YOUR_RUN_NAME \
#  trainer.val_before_train=True \
#  trainer.n_gpus_per_node=1 \
#  trainer.nnodes=1 \
#  trainer.save_freq=100 \
#  trainer.test_freq=10 \
#  trainer.total_epochs=15 2>&1 | tee verl_demo.log



YOUR_PROJECT_NAME='llm'
YOUR_RUN_NAME='leetcode_testgen_grpo'
train_batch_size=64
PYTHONUNBUFFERED=1 python3 -m verl.trainer.main_ppo \
 algorithm.adv_estimator=grpo \
 data.train_files=./data/mix_data/train.parquet \
 data.val_files=./data/mix_data/test.parquet \
 data.train_batch_size=$train_batch_size \
 data.max_prompt_length=4096 \
 data.max_response_length=1024 \
 data.filter_overlong_prompts=True \
 actor_rollout_ref.model.path=/workspace/verl/models/Qwen2.5-1.5B-Instruct \
 actor_rollout_ref.actor.optim.lr=1e-6 \
 actor_rollout_ref.actor.ppo_mini_batch_size=$train_batch_size \
 actor_rollout_ref.actor.ppo_micro_batch_size_per_gpu=4 \
 actor_rollout_ref.rollout.name=vllm \
 actor_rollout_ref.rollout.log_prob_micro_batch_size_per_gpu=8 \
 actor_rollout_ref.rollout.tensor_model_parallel_size=1 \
 actor_rollout_ref.rollout.gpu_memory_utilization=0.5 \
 actor_rollout_ref.ref.log_prob_micro_batch_size_per_gpu=4 \
 reward.custom_reward_function.path="test_case_cov_reward.py" \
 reward.custom_reward_function.name=compute_reward \
 algorithm.use_kl_in_reward=False \
 trainer.logger=["console","wandb"] \
 trainer.project_name=$YOUR_PROJECT_NAME \
 trainer.experiment_name=$YOUR_RUN_NAME \
 trainer.val_before_train=True \
 trainer.n_gpus_per_node=1 \
 trainer.nnodes=1 \
 trainer.save_freq=100 \
 trainer.test_freq=10 \
 trainer.total_epochs=15 2>&1 | tee verl_demo.log