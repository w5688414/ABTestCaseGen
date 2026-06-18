


# for _ in range(int(input())):
#     ins = input().strip()
#     stck = []
#     res = "YES"
    
#     for x in ins:
#         if x == "(":
#             stck.append(x)
#         else:
#             if len(stck) > 0:
#                 stck.pop()
#             else:
#                 res = "NO"
#                 break
                
#     if len(stck) > 0: 
#         res = "NO"
        
#     print(res)


def calculate_score(max_score, minutes_passed, wrong_submissions):
    """
    计算单道题目的最终得分
    """
    t = (1 - (minutes_passed / 250)) * max_score - (50 * wrong_submissions)
    return max(0.3 * max_score, t)

# 每道题目的满分值
scores_limit = [500, 1000, 1500, 2000, 2500]

# 输入处理
m = list(map(int, input().split()))  # 每题通过的时间（分钟）
w = list(map(int, input().split()))  # 每题错误的尝试次数
s, u = map(int, input().split())     # s: 成功黑入次数, u: 失败黑入次数

total_res = 0

# 累加五道题的分数
for i in range(5):
    total_res += calculate_score(scores_limit[i], m[i], w[i])

# 加上 Hack 成功的奖励并减去失败的惩罚
total_res += (100 * s)
total_res -= (50 * u)

# 输出最终整数得分
print(int(total_res))

    