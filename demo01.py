# _*_ coding : utf-8 _*_
# @Time : 2024/8/22 15:31 
# @Author : 不会写代码的小新手
# @File : demo01
# @Project : BDD_contest


import pandas as pd


def synchronize_dataframes(df1, df2, column_name='image_name'):
    """
    同步两个 DataFrame 的数据：
    1. 将 df2 中不在 df1 中的行追加到 df1 中。
    2. 删除 df1 中不在 df2 中的行。
    """
    # 确保 image_name 列的数据类型一致
    if df1[column_name].dtype != df2[column_name].dtype:
        df1[column_name] = df1[column_name].astype(df2[column_name].dtype)

    # 查找 df2 中不在 df1 中的行，并追加到 df1
    missing_in_df1 = df2[~df2[column_name].isin(df1[column_name])]
    if not missing_in_df1.empty:
        print("Missing rows in df1 from df2:")
        print(missing_in_df1)
        df1 = pd.concat([df1, missing_in_df1]).reset_index(drop=True)

    # 查找 df1 中不在 df2 中的行，并从 df1 中删除
    extra_in_df1 = df1[~df1[column_name].isin(df2[column_name])]
    if not extra_in_df1.empty:
        print("Extra rows in df1 not in df2:")
        print(extra_in_df1)
        df1.drop(extra_in_df1.index, inplace=True)

    # 对 DataFrame 进行排序，以确保数据的一致性
    df1.sort_values(by=column_name, inplace=True, ignore_index=True)

    return df1


def check_consistency(df1, df2, column_name='image_name'):
    """
    检查两个 DataFrame 在指定列上是否一致，并输出结果。
    """
    consistent = df1[column_name].equals(df2[column_name])
    print(f"Consistency of '{column_name}' column between df1 and df2: {consistent}")


def main():
    # 读取 CSV 文件
    df1 = pd.read_csv('./label_contest/test_submission.csv')
    df2 = pd.read_csv('./label_contest/testgt_submission.csv')

    # 在任何处理之前先对两个 DataFrame 进行排序
    df1.sort_values(by='image_name', inplace=True, ignore_index=True)
    df2.sort_values(by='image_name', inplace=True, ignore_index=True)

    # 同步两个 DataFrame 的数据
    df1 = synchronize_dataframes(df1, df2)

    # 保存更新后的 df1
    df1.to_csv('./label_contest/test_submission.csv', index=False)

    # 输出调试信息
    print("Updated df1:\n", df1)

    # 检查并输出两个 DataFrame 在 image_name 列上是否一致
    check_consistency(df1, df2)


if __name__ == '__main__':
    main()

