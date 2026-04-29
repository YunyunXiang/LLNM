#LBP特征可视化
import cv2
import numpy as np
import matplotlib.pyplot as plt
from skimage.feature import local_binary_pattern
import os

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

def visualize_lbp(image_path):
    # 1. 读取图片 (处理中文路径)
    img_array = np.fromfile(image_path, dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_GRAYSCALE)
    if img is None: return
    
    # 2. 预处理 (保持和你代码逻辑一致)
    img = cv2.resize(img, (128, 128))
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    img_enhanced = clahe.apply(img)

    # 3. 计算 LBP
    # P=8 (8个邻域点), R=1 (半径为1)
    # method="uniform" ，它能产生 10 种模式
    radius = 1
    n_points = 8 * radius
    lbp = local_binary_pattern(img_enhanced, n_points, radius, method="uniform")

    # 4. 计算 LBP 直方图 (这就是你代码中提取的 10 维特征)
    # n_bins = P + 2 = 10
    n_bins = int(lbp.max() + 1)
    hist, _ = np.histogram(lbp.ravel(), bins=n_bins, range=(0, n_bins), density=True)

    # 5. 绘图
    plt.figure(figsize=(18, 5))

    # 子图 1: 增强后的原图
    plt.subplot(1, 3, 1)
    plt.imshow(img_enhanced, cmap='gray')
    plt.title("Input image (CLAHE)")
    plt.axis('off')

    # 子图 2: LBP 特征图
    # 这里的颜色代表不同的局部纹理类型
    plt.subplot(1, 3, 2)
    plt.imshow(lbp, cmap='gray')
    plt.title("LBP texture map")
    plt.axis('off')

    # 子图 3: LBP 直方图
    plt.subplot(1, 3, 3)
    plt.bar(range(n_bins), hist, color='skyblue', edgecolor='black')
    plt.title("LBP 10-dimensional feature vector (input data for the model)")
    plt.xlabel("Pattern Number (0-9)")
    plt.ylabel("frequency of occurrence")

    plt.tight_layout()
    plt.show()

# --- 文件路径 ---
file_path = r"F:\数据集\淋巴结转移\jpg\ROI有转移\1.740423.1443600870.36828.19920.3123408563.666607674.jpg"

if os.path.exists(file_path):
    visualize_lbp(file_path)