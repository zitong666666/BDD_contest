# 数据集说明

本文件夹包含用于 YOLOv5 行人车辆检测与计数任务的 BDD100K 数据集。

## 目录结构

```
datasets/
├── images/                 # 图片文件夹
│   ├── train/             # 训练集图片 (80%)
│   ├── val/               # 验证集图片 (10%)
│   ├── test/              # 测试集图片 (10%)
│   ├── test01/            # 测试集1 (TrainB)
│   └── test02/            # 测试集2 (TrainA)
└── labels/                 # 标签文件夹 (YOLO格式)
    ├── train/             # 训练集标签
    ├── val/               # 验证集标签
    └── test/              # 测试集标签
```

## 数据集简介

### BDD100K 数据集

BDD100K 是由加州大学伯克利分校发布的大规模驾驶场景数据集，包含：

- **数据量**: 100,000 张高清图片
- **分辨率**: 1280 x 720 像素
- **来源**: 1100 小时行车记录视频
- **场景**: 不同天气、时间、地理位置的驾驶场景

### 检测类别 (9类)

| 类别ID | 类别名称 | 中文描述 | 类别类型 |
|--------|----------|----------|----------|
| 0 | bus | 公交车 | 车辆 |
| 1 | traffic light | 交通灯 | 交通设施 |
| 2 | traffic sign | 交通标志 | 交通设施 |
| 3 | person | 行人 | 行人 |
| 4 | bike | 自行车 | 车辆 |
| 5 | truck | 卡车 | 车辆 |
| 6 | motor | 摩托车 | 车辆 |
| 7 | car | 汽车 | 车辆 |
| 8 | rider | 乘车人 | 行人 |

## 数据集获取方式

### 方式一：百度网盘下载

| 数据集 | 大小 | 下载链接 | 提取码 |
|--------|------|----------|--------|
| TrainA | 2.37 GB | [点击下载](https://pan.baidu.com/s/1zj3MqZEHKHpFACs95Ov4gQ) | ma1p |
| TrainB | 880 MB | [点击下载](https://pan.baidu.com/s/1whg_-jLfbUnfpZkKjvdziQ) | yg54 |

### 方式二：BDD100K 官网下载

访问 [BDD100K 官网](https://bdd-data.berkeley.edu/) 注册账号后下载。

## 数据集创建方式

### 第一步：下载并解压数据

1. 从上述链接下载 TrainA 和 TrainB 数据集
2. 解压到项目根目录，形成以下结构：

```
BDD_contest/
├── trainA/
│   ├── images/           # 原始图片
│   └── labels/
│       └── label-trainA/ # 原始标签 (xmin,ymin,xmax,ymax格式)
└── trainB/
    ├── images/           # 原始图片
    └── labels/
        └── label-trainB/ # 原始标签 (xmin,ymin,xmax,ymax格式)
```

### 第二步：标签格式转换

YOLOv5 要求标签格式为归一化的中心点坐标，需要转换原始标签格式。

**原始格式**:
```
类别ID  x_min  y_min  x_max  y_max
```

**YOLO格式**:
```
类别ID  x_center  y_center  width  height
```

运行转换脚本：

```bash
# 转换 TrainA 标签
python labels_convert.py

# 修改 labels_convert.py 中的 label_directory 变量可转换 TrainB 标签
```

脚本位置：`BDD_contest/labels_convert.py`

**转换说明**:
- 图片固定尺寸: 1280 x 720
- 坐标归一化到 [0, 1] 范围
- 计算公式:
  - x_center = ((x_min + x_max) / 2) / img_width
  - y_center = ((y_min + y_max) / 2) / img_height
  - width = (x_max - x_min) / img_width
  - height = (y_max - y_min) / img_height

### 第三步：划分数据集

按 **训练集:验证集:测试集 = 8:1:1** 的比例划分数据集。

运行划分脚本：

```bash
python split_data.py
```

脚本位置：`BDD_contest/split_data.py`

**划分说明**:
- 随机打乱图片顺序
- 按比例分配到 train/val/test 文件夹
- 图片和标签同步复制

### 第四步：验证数据集

划分完成后，`datasets` 文件夹应包含：

```
datasets/
├── images/
│   ├── train/    # 约 2850 张图片
│   ├── val/      # 约 356 张图片
│   └── test/     # 约 356 张图片
└── labels/
    ├── train/    # 对应训练集标签
    ├── val/      # 对应验证集标签
    └── test/     # 对应测试集标签
```

## YOLO 标签格式说明

每个图片对应一个同名的 `.txt` 标签文件。

**示例** (train_A_1501.txt):
```
2	0.404687	0.295833	0.012500	0.041667
2	0.386719	0.263889	0.045312	0.063889
7	0.442578	0.482639	0.010156	0.018056
```

**格式说明**:
- 每行代表一个目标
- 第一列: 类别ID (0-8)
- 第二列: 边界框中心点 x 坐标 (归一化)
- 第三列: 边界框中心点 y 坐标 (归一化)
- 第四列: 边界框宽度 (归一化)
- 第五列: 边界框高度 (归一化)

## 数据集配置文件

在 `yolov5-6.2/data/` 目录下创建 `bdd_traina.yaml` 文件：

```yaml
# 数据集根目录 (修改为你的实际路径)
path: /path/to/BDD_contest/yolov5-6.2/datasets

# 训练集和验证集路径 (相对于 path)
train: images/train
val: images/val
test: images/test  # 可选

# 类别数量
nc: 9

# 类别名称 (顺序对应类别ID)
names: ['bus', 'traffic light', 'traffic sign', 'person', 'bike', 
        'truck', 'motor', 'car', 'rider']
```

## 数据集统计

### 示例统计 (TrainA - 3564张图片)

| 类别 | 图片数量 | 标签数量 | 精确率 (P) | 召回率 (R) | mAP@0.5 | mAP@0.5:0.95 |
|------|----------|----------|------------|------------|---------|--------------|
| bus | 3564 | 853 | 0.737 | 0.479 | 0.570 | 0.414 |
| traffic light | 3564 | 8763 | 0.661 | 0.548 | 0.577 | 0.222 |
| traffic sign | 3564 | 12993 | 0.735 | 0.523 | 0.588 | 0.293 |
| person | 3564 | 6414 | 0.716 | 0.487 | 0.558 | 0.263 |
| bike | 3564 | 534 | 0.624 | 0.436 | 0.460 | 0.199 |
| truck | 3564 | 2046 | 0.656 | 0.554 | 0.588 | 0.416 |
| motor | 3564 | 195 | 0.636 | 0.385 | 0.416 | 0.196 |
| car | 3564 | 39024 | 0.793 | 0.685 | 0.748 | 0.475 |
| rider | 3564 | 324 | 0.719 | 0.332 | 0.396 | 0.174 |
| **总计** | **3564** | **71146** | **0.697** | **0.492** | **0.544** | **0.295** |

## 注意事项

1. **图片格式**: 支持 `.jpg`, `.jpeg`, `.png`
2. **标签同步**: 每个图片必须有对应的 `.txt` 标签文件（无目标可不创建）
3. **路径配置**: 使用数据集前确保 `bdd_traina.yaml` 中的路径正确
4. **内存要求**: 训练时建议 16GB+ 内存，可设置 `--cache ram` 加速
5. **显存要求**: GPU 训练时，batch-size 根据显存调整

## 常见问题

### Q: 标签文件格式不对怎么办？

A: 确保原始标签格式为：`类别ID x_min y_min x_max y_max`，每行一个目标，使用空格或制表符分隔。

### Q: 如何检查标签是否正确？

A: 可以使用以下脚本可视化标签：
```python
import cv2
import os

img_path = 'datasets/images/train/train_A_1.jpg'
label_path = 'datasets/labels/train/train_A_1.txt'

img = cv2.imread(img_path)
h, w = img.shape[:2]

with open(label_path, 'r') as f:
    for line in f:
        cls, cx, cy, bw, bh = map(float, line.split())
        x1 = int((cx - bw/2) * w)
        y1 = int((cy - bh/2) * h)
        x2 = int((cx + bw/2) * w)
        y2 = int((cy + bh/2) * h)
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(img, str(int(cls)), (x1, y1-5), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

cv2.imshow('Label Check', img)
cv2.waitKey(0)
cv2.destroyAllWindows()
```

### Q: 数据集太大，磁盘空间不足怎么办？

A: 
1. 只使用 TrainA 或 TrainB 其中一个数据集
2. 减少训练集比例，如 7:1.5:1.5
3. 使用更小的图片尺寸训练，修改 `--imgsz` 参数

## 联系方式

如有问题，欢迎联系：
- **邮箱**: 2102353304@qq.com
- **微信公众号**: 不会写代码的小新手
- **GitHub**: [提交 Issue](https://github.com/your-username/BDD_contest/issues)
