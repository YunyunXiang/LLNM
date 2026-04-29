#HOG特征可视化
import cv2
import numpy as np
import matplotlib.pyplot as plt
from skimage.feature import hog
from skimage import exposure
import os

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

def visualize_hog(image_path):
    # 1. 读取并预处理 (处理中文路径)
    img_array = np.fromfile(image_path, dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_GRAYSCALE)
    if img is None: return
    
    # 2. 预处理 (128x128)
    img = cv2.resize(img, (128, 128))
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    img_enhanced = clahe.apply(img)

    # 3. 计算 HOG
    # 参数必须和你原始代码一致：8方向, 32x32像素每个cell
    fd, hog_image = hog(img_enhanced, 
                        orientations=8, 
                        pixels_per_cell=(32, 32),
                        cells_per_block=(1, 1), 
                        visualize=True)

    # 4. 增强 HOG 图像的可视化效果（拉高亮度）
    hog_image_rescaled = exposure.rescale_intensity(hog_image, in_range=(0, 10))

    # 5. 绘图
    plt.figure(figsize=(12, 6))

    # 子图 1: 原图
    plt.subplot(1, 2, 1)
    plt.imshow(img_enhanced, cmap='gray')
    plt.title("input image (CLAHE)")
    plt.axis('off')

    # 子图 2: HOG 特征图
    plt.subplot(1, 2, 2)
    plt.imshow(hog_image_rescaled, cmap='jet') # 使用 jet 颜色表让梯度方向更明显
    plt.title("HOG edge direction feature map\n")
    plt.axis('off')

    plt.show()
    
    print(f"HOG feature vector dimension: {len(fd)}")

# --- 文件路径 ---
file_path = r"F:\数据集\淋巴结转移\jpg\ROI有转移\1.740423.1443600870.36828.19920.3123408563.666607674.jpg"

if os.path.exists(file_path):
    visualize_hog(file_path)