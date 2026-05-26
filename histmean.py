# _*_ coding : utf-8 _*_
# @Time : 2024/8/25 20:43
# @Author : 不会写代码的小新手
# @File : delpicture
# @Project : BDD_contest





import os
import cv2
import glob

def preprocess_image(input_image_path, grayscale=False, resize=None, histogram_equalization=False, remove_gaussian_noise=False, remove_salt_pepper_noise=False):
    # 检查输入图像文件是否存在
    if not os.path.exists(input_image_path):
        print(f"错误: 文件 '{input_image_path}' 不存在。")
        return

    # 加载图像
    img = cv2.imread(input_image_path)

    # 如果图像没有成功加载，退出
    if img is None:
        print(f"警告: 无法从 '{input_image_path}' 加载图像。")
        return

    # 如需要，转换为灰度图
    if grayscale:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 如需要，调整图像大小
    if resize is not None:
        # 确保 resize 参数是一个有效的尺寸元组
        if isinstance(resize, tuple) and len(resize) == 2:
            img = cv2.resize(img, resize)
        else:
            print("错误: 无效的 resize 参数。必须是元组 (宽度, 高度)。")
            return

    # 如需要，去除高斯噪声
    if remove_gaussian_noise:
        # 使用均值滤波去除高斯噪声
        kernel_size = 5  # 滤波器大小
        img = cv2.blur(img, (kernel_size, kernel_size))

    # 如需要，去除椒盐噪声
    if remove_salt_pepper_noise:
        # 使用中值滤波去除椒盐噪声
        kernel_size = 3  # 滤波器大小，可以根据需要调整
        img = cv2.medianBlur(img, kernel_size)

    # 如需要，应用直方图均衡化
    if histogram_equalization:
        if grayscale:
            img = cv2.equalizeHist(img)
        else:
            # 转换到 YUV 颜色空间进行直方图均衡化
            img_yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
            img_yuv[:,:,0] = cv2.equalizeHist(img_yuv[:,:,0])
            img = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)

    # 保存处理后的图像，覆盖原文件
    cv2.imwrite(input_image_path, img)

# 定义输入图像文件所在的目录
input_image_dir = "./yolov5-6.2/datasets/images/val"

# 获取目录中所有 .jpg 格式的图像文件
image_files = glob.glob(os.path.join(input_image_dir, "*.jpg"))

# 循环处理每个图像文件
for image_file in image_files:
    # 调用预处理函数
    preprocess_image(image_file, grayscale=True, resize=(640, 640), histogram_equalization=True, remove_gaussian_noise=True, remove_salt_pepper_noise=True)