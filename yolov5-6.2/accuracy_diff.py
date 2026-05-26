import pandas as pd


# 测试结果文件路径
submission_path = r"E:\BDD_contest\label_contest\test_submission.csv"

# 实际结果文件路径
ground_truth_path = r"E:\BDD_contest\label_contest\testgt_submission.csv"


# 加载数据
submission_df = pd.read_csv(submission_path)
ground_truth_df = pd.read_csv(ground_truth_path)

# 确保两个数据框以图像名排序，以保证数据对齐
submission_df.sort_values('image_name', inplace=True, ignore_index=True)
ground_truth_df.sort_values('image_name', inplace=True, ignore_index=True)

# 校验image_name是否一一对应
if not submission_df['image_name'].equals(ground_truth_df['image_name']):
    print("Error: The image names in the two files do not match exactly.")
    exit()


# 计分 车
def calculate_vehicle(sub, truth):
    diff_abs = abs(sub - truth)
    if diff_abs == 0:
        score = 0.1
    elif diff_abs == 1:
        score = 0.095
    elif diff_abs == 2:
        score = 0.09
    elif diff_abs == 3:
        score = 0.085
    elif diff_abs <= 5:
        score = 0.055
    elif diff_abs <= 7:
        score = 0.03
    else:
        score = 0

    return score


# 计分 人
def calculate_people(sub, truth):
    diff_abs = abs(sub - truth)
    if diff_abs == 0:
        score = 0.1
    elif diff_abs == 1:
        score = 0.09
    elif diff_abs == 2:
        score = 0.075
    elif diff_abs == 3:
        score = 0.055
    elif diff_abs <= 5:
        score = 0.03
    else:
        score = 0

    return score
    

score_list = []
for line in range(len(submission_df)):
    score_people = calculate_people(submission_df.iloc[line,1], ground_truth_df.iloc[line,1])
    score_vehicle = calculate_vehicle(submission_df.iloc[line,2], ground_truth_df.iloc[line,2])
    score = 0.4 * score_people + 0.6 * score_vehicle
    score_list.append(score)


# print(score_list)
print("Overall accuracy: %f" % sum(score_list))
