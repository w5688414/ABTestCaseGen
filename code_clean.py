from data_util import read_jsonl, write_to_jsonl


if __name__=="__main__":
    data_path = '/workspace/verl/Agent-RL/verl/data/python3_cases_format_python_train_3000_-1.jsonl'
    data_list = read_jsonl(data_path)
    cnt = 0
    for item in data_list:
        solutions = item['solutions']
        sol = solutions[0]
        if sol is not None and '__main__' in sol:
            print("Found __main__ in solution:")
            print(sol)
            cnt+=1
            if 'def main():' in sol:
                print("Found def main() in solution:")
                
                sol = sol.split('def main():')[0]
                print(f"post split solution: {sol}")
            else:
                sol = sol.split('if __name__ == "__main__":')[0]

            item['solutions']=[sol]

    print(f"Total cases with __main__: {cnt}")
    write_to_jsonl(f"data/python3_cases_format_python_train_3000_-1_clean_main.jsonl", data_list, 'w')
        