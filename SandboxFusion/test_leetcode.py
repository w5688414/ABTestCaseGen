from datasets import load_dataset
import requests

config = {
  'compile_timeout': 40,
  'run_timeout': 20,
  'dataset_type': "AutoEvalDataset"
}

# Get dataset data in sandbox format
data = list(load_dataset("sine/LeetCodeSample", "python", split="test"))

config['provided_data'] = data
prompts = requests.post('http://localhost:8080/get_prompts', json={
  'dataset': 'leetcode_sample_python',
  'config': config
}).json()

print('please perform model inference on these prompts:')
print('\n'.join([p['prompt'] for p in prompts[:3]]))
print('...')

# your model inference code here
completions = ['' for _ in prompts]
idx = 0
for completion, sample in zip(completions, data):
    config['provided_data'] = sample
    res = requests.post('http://localhost:8080/submit', json={
        'dataset': 'leetcode_sample_python',
        'id': '',
        'completion': completion,
        'config': config
    })

    print(f'result: {res.json()}')
    idx+=1
    if idx>5:
        break