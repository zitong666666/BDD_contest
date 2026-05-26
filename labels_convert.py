# _*_ coding : utf-8 _*_
# @Time : 2024/8/17 17:44 
# @Author : 不会写代码的小新手
# @File : labels_convert.py
# @Project : BDD_contest


import os

# 所有图片的大小固定
img_width = 1280
img_height = 720


def convert_bbox_to_yolo_format(x_min, y_min, x_max, y_max, img_w, img_h):
    '''
    将边界框<x_min,y_min,x_max,y_max>转换为YOLO格式　
    <x_center,y_center,width,height>格式   并归一化坐标
    '''
    x_center = ((x_min + x_max) / 2) / img_w
    y_center = ((y_min + y_max) / 2) / img_h
    width = (x_max - x_min) / img_w
    height = (y_max - y_min) / img_h
    return x_center, y_center, width, height


def process_label_files(label_dir):
    '''
    处理label文件
    '''
    for label_file in os.listdir(label_dir):
        file_path = os.path.join(label_dir, label_file)
        try:
            with open(file_path, 'r') as file:
                lines = file.readlines()

            # 准备新的标签内容
            new_lines = []
            for line in lines:
                parts = line.strip().split()
                if len(parts) == 5:
                    cls, x_min, y_min, x_max, y_max = map(float, parts)
                    x_center, y_center, width, height = convert_bbox_to_yolo_format(x_min, y_min, x_max, y_max, img_width, img_height)
                    new_line = f"{int(cls)}\t{x_center:.6f}\t{y_center:.6f}\t{width:.6f}\t{height:.6f}\n"
                    new_lines.append(new_line)
            # 将转换后的标签写回标签文件
            with open(file_path, 'w') as file:
                file.writelines(new_lines)
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")


if __name__ == '__main__':
    label_directory = 'trainB/labels/label-trainB'
    process_label_files(label_directory)

print("标签转换完成")