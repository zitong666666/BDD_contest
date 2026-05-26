# _*_ coding : utf-8 _*_
# @Time : 2024/8/25 20:43 
# @Author : 不会写代码的小新手
# @File : delpicture
# @Project : BDD_contest


import cv2
import numpy as np
import os
import subprocess


def laplacian_variance(image):
    # 应用拉普拉斯算子
    laplacian = cv2.Laplacian(image, cv2.CV_64F)

    # 计算变差
    variance = np.var(laplacian)

    return variance


def tenengrad(image):
    # 计算水平和垂直方向上的梯度
    grad_x = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=3)

    # 计算梯度的模
    magnitude = np.sqrt(grad_x ** 2 + grad_y ** 2)

    # 计算Tenengrad值
    tenengrad_value = np.mean(magnitude)

    return tenengrad_value


def entropy(image):
    # 计算像素出现的概率
    hist = cv2.calcHist([image], [0], None, [256], [0, 256])
    hist /= hist.sum()  # 归一化概率

    # 计算熵
    entropy = -np.sum(hist * np.log2(hist + np.finfo(float).eps))

    return entropy


def get_entropy_image_magick(image_path):
    try:
        output = subprocess.check_output(['convert', image_path, '-format', '%[entropy]', 'info:'])
        entropy = float(output.decode('utf-8').strip())
        return entropy
    except Exception as e:
        print(f"Error: {e}")
        return None


def check_images(directory, labels_directory, laplacian_threshold=100, tenengrad_threshold=100, delete_blurry=False):
    # 遍历目录中的所有图像文件
    for filename in os.listdir(directory):
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            filepath = os.path.join(directory, filename)

            # 构建对应的标签文件路径
            label_filename = os.path.splitext(filename)[0] + ".txt"
            label_filepath = os.path.join(labels_directory, label_filename)

            # 读取图像为灰度模式
            image = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)

            # 计算拉普拉斯变差
            laplacian_var = laplacian_variance(image)

            # 计算Tenengrad值
            tenengrad_val = tenengrad(image)

            # 计算熵
            ent = entropy(image)

            # 输出结果
            print(f"图片: {filename}")
            print(f"  拉普拉斯变差 : {laplacian_var:.2f}")
            print(f"  Tenengrad算子: {tenengrad_val:.2f}")
            print(f"  熵: {ent:.2f}")

            # 判断是否为模糊图像
            if laplacian_var < laplacian_threshold and tenengrad_val < tenengrad_threshold:
                print(" 图片是模糊的！！！")

                # 根据选项删除模糊图像及其对应的标签文件
                if delete_blurry:
                    print(f"  删除图片: {filepath}")
                    os.remove(filepath)  # 删除图片文件

                    # 删除对应的标签文件
                    if os.path.exists(label_filepath):
                        print(f"  删除标签文件: {label_filepath}")
                        os.remove(label_filepath)  # 删除标签文件

            print()


# 设置图片和标签文件删除路径
directory = './yolov5-6.2/datasets/images/val'
labels_directory = './yolov5-6.2/datasets/label/val'

# 执行批量检查(阈值需要手动设置)
check_images(directory, labels_directory, laplacian_threshold=110, tenengrad_threshold=40, delete_blurry=True)