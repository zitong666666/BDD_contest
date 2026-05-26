# _*_ coding : utf-8 _*_
# @Time : 2024/8/18 16:09 
# @Author : 不会写代码的小新手
# @File : Accuracy
# @Project : BDD_contest



import pandas as pd

# 指定文件路径
submission_path = r"E:\BDD_contest\label_contest\test_submission.csv"
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

# 计算完全匹配的行数
matching_rows = (submission_df['people_num'] == ground_truth_df['people_num']) & \
                (submission_df['vehicle_num'] == ground_truth_df['vehicle_num'])
total_correct = matching_rows.sum()

# 计算正确率
accuracy = total_correct / len(submission_df)
print(f"Overall accuracy: {accuracy:.2%}")