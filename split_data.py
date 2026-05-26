# _*_ coding : utf-8 _*_
# @Time : 2024/8/17 18:30 
# @Author : 不会写代码的小新手
# @File : split_data.py
# @Project : BDD_contest


import os
import random
from shutil import copyfile


def split_dataset(image_folder, txt_folder, output_folder, split_ratio=(0.8, 0.1, 0.1)):
    # Ensure output folders exist
    for phase in ['train', 'val', 'test']:
        os.makedirs(os.path.join(output_folder, 'images', phase), exist_ok=True)
        os.makedirs(os.path.join(output_folder, 'labels', phase), exist_ok=True)

    # Get list of image files
    image_files = [f for f in os.listdir(image_folder) if f.endswith(('.jpg', '.jpeg', '.png'))]
    random.shuffle(image_files)

    num_images = len(image_files)
    num_train = int(split_ratio[0] * num_images)
    num_val = int(split_ratio[1] * num_images)

    train_images = image_files[:num_train]
    val_images = image_files[num_train:num_train + num_val]
    test_images = image_files[num_train + num_val:]

    # Copy images and labels to respective folders
    for phase, images_list in zip(['train', 'val', 'test'], [train_images, val_images, test_images]):
        for image_file in images_list:
            # Copy image
            image_path = os.path.join(image_folder, image_file)
            target_image_path = os.path.join(output_folder, 'images', phase, image_file)
            copyfile(image_path, target_image_path)

            # Copy corresponding txt file if exists
            txt_file = os.path.splitext(image_file)[0] + '.txt'
            txt_path = os.path.join(txt_folder, txt_file)
            target_txt_path = os.path.join(output_folder, 'labels', phase, txt_file)
            if os.path.exists(txt_path):
                copyfile(txt_path, target_txt_path)


if __name__ == "__main__":
    image_folder_path = "trainA/images"
    txt_folder_path = "trainA/labels/label-trainA"
    output_dataset_path = "yolov5-6.2/datasets"

    split_dataset(image_folder_path, txt_folder_path, output_dataset_path)

print("Split complete.")
