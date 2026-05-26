# _*_ coding : utf-8 _*_
# @Time : 2024/8/25 12:10 
# @Author : 不会写代码的小新手
# @File : MixProcess
# @Project : BDD_contest


import cv2
import os
import glob
import numpy as np
from random import uniform

def batch_preprocess_images(input_folder, output_folder, grayscale=False, resize=None, noise_reduction=False,
                            brightness_adjustment=1.0, contrast_enhancement=False, color_enhancement=False,
                            sharpen_image=False, histogram_equalization=False, random_brightness_contrast=False,
                            random_rotate_angle_range=(-10, 10), random_crop_ratio_range=(0.8, 1.0),
                            edge_detection=False, normalize=False):
    """
    批量预处理图像函数,处理图片
    :param input_folder: 输入图像所在的文件夹路径
    :param output_folder: 处理后图像输出的文件夹路径
    :param grayscale: 是否转换为灰度图
    :param resize: 调整图像尺寸的目标大小 (width, height)，默认为 None 不调整
    :param noise_reduction: 是否进行去噪处理
    :param brightness_adjustment: 亮度调整系数，默认为 1.0 表示不调整
    :param contrast_enhancement: 是否增强对比度
    :param color_enhancement: 是否增强色彩
    :param sharpen_image: 是否锐化图像
    :param histogram_equalization: 是否进行直方图均衡化
    :param random_brightness_contrast: 是否随机调整亮度和对比度
    :param random_rotate_angle_range: 随机旋转角度范围 (min, max)，单位为度
    :param random_crop_ratio_range: 随机剪裁比例范围 (min, max)
    :param edge_detection: 是否进行边缘检测
    :param normalize: 是否归一化像素值
    """

    # 创建输出文件夹
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 获取输入文件夹中的所有图像文件
    image_files = glob.glob(os.path.join(input_folder, '*.*'))

    for image_file in image_files:
        # 提取文件名
        filename = os.path.basename(image_file)

        # 构建输出文件路径
        output_path = os.path.join(output_folder, filename)

        # 读取图像
        img = cv2.imread(image_file)

        # 调整尺寸
        if resize is not None:
            img = cv2.resize(img, resize)

        # 转换为灰度图
        if grayscale:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 去除噪声
        if noise_reduction:
            img = cv2.GaussianBlur(img, (5, 5), 0)  # 高斯模糊
            img = cv2.medianBlur(img, 5)  # 中值滤波

        # 亮度调整
        img = cv2.convertScaleAbs(img, alpha=brightness_adjustment, beta=0)

        # 对比度增强
        if contrast_enhancement:
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            img = clahe.apply(img) if grayscale else cv2.cvtColor(clahe.apply(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)), cv2.COLOR_GRAY2BGR)

        # 色彩增强
        if color_enhancement:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            h, s, v = cv2.split(img)
            s = cv2.equalizeHist(s)
            img = cv2.merge([h, s, v])
            img = cv2.cvtColor(img, cv2.COLOR_HSV2BGR)

        # 图像锐化
        if sharpen_image:
            kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
            img = cv2.filter2D(img, -1, kernel)

        # 直方图均衡化
        if histogram_equalization:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
            y, cr, cb = cv2.split(img)
            y = cv2.equalizeHist(y)
            img = cv2.merge([y, cr, cb])
            img = cv2.cvtColor(img, cv2.COLOR_YCrCb2BGR)

        # 随机调整亮度和对比度
        if random_brightness_contrast:
            alpha = uniform(0.8, 1.2)
            beta = uniform(-20, 20)
            img = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)

        # 随机旋转图像
        if random_rotate_angle_range[0] != random_rotate_angle_range[1]:
            rotate_angle = uniform(*random_rotate_angle_range)
            (h, w) = img.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, rotate_angle, 1.0)
            img = cv2.warpAffine(img, M, (w, h))

        # 随机剪裁
        if random_crop_ratio_range[0] != random_crop_ratio_range[1]:
            ratio = uniform(*random_crop_ratio_range)
            h, w = img.shape[:2]
            new_h, new_w = int(h * ratio), int(w * ratio)
            top = (h - new_h) // 2
            left = (w - new_w) // 2
            img = img[top:top + new_h, left:left + new_w]

        # 边缘检测
        if edge_detection:
            # 在边缘检测后，需要恢复颜色通道
            img_gray = cv2.Canny(img, 100, 200)
            img = cv2.cvtColor(img_gray, cv2.COLOR_GRAY2BGR) if len(img.shape) == 2 else img

        # 归一化像素值
        if normalize:
            # 归一化后需要将像素值恢复到 [0, 255] 的范围内
            img = (img / 255.0).astype(np.float32)

        # 保存处理后的图像
        cv2.imwrite(output_path, img * 255.0 if normalize else img)

        print(f"成功将 {filename} 保存在 {output_path}里面了！！！")


if __name__ == '__main__':
    # 填入数据集文件夹路径
    input_folder = './yolov5-6.2/datasets/images/train'
    output_folder = './yolov5-6.2/datasets/images/train'

    # 预处理参数
    grayscale = False   # 转换为灰度图
    resize = (1280, 720)  # 给图片设置新的宽度和高度
    noise_reduction = True  # 去除噪声
    brightness_adjustment = 0  # 增加亮度
    contrast_enhancement = False  # 对比度增强
    color_enhancement = False  # 色彩增强
    sharpen_image = False  # 锐化图像
    histogram_equalization = False  # 直方图均衡化
    random_brightness_contrast = False  # 随机调整亮度和对比度
    random_rotate_angle_range = (-10, 10)  # 随机旋转角度范围(-10, 10)
    random_crop_ratio_range = (0,0)  # 随机剪裁比例范围(0.8, 1.0)
    edge_detection = False  # 边缘检测
    normalize = True  # 归一化像素值

    # 调用批量预处理函数
    batch_preprocess_images(input_folder, output_folder, grayscale, resize, noise_reduction,
                            brightness_adjustment, contrast_enhancement, color_enhancement,
                            sharpen_image, histogram_equalization, random_brightness_contrast,
                            random_rotate_angle_range, random_crop_ratio_range,
                            edge_detection, normalize)
