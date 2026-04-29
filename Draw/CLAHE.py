#CLAHE图像增强示意
import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

# 解决 matplotlib 显示中文问题
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

def process_and_show_separate(image_path):
    # 1. 解决中文路径读取问题
    try:
        img_array = np.fromfile(image_path, dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        
        if img is None:
            print("错误：无法读取图片，请检查路径。")
            return
    except Exception as e:
        print(f"读取出错: {e}")
        return

    # 2. 转换为灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 3. 普通直方图均衡化 (HE)
    res_he = cv2.equalizeHist(gray)

    # 4. CLAHE 增强
    # clipLimit: 限制对比度，tileGridSize: 分块大小
    clahe_obj = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    res_clahe = clahe_obj.apply(gray)

    # --- 分开输出图片 ---

    # 窗口 1: 原始灰度图
    plt.figure(num="1. 原始灰度图", figsize=(8, 6))
    plt.imshow(gray, cmap='gray')
    plt.title("Original grayscale image")
    plt.axis('off')

    # 窗口 2: 普通均衡化 (HE)
    plt.figure(num="2. 普通均衡化 (HE)", figsize=(8, 6))
    plt.imshow(res_he, cmap='gray')
    plt.title("Homogeneous equalization (HE) - prone to overexposure")
    plt.axis('off')

    # 窗口 3: CLAHE 增强
    plt.figure(num="3. CLAHE 增强", figsize=(8, 6))
    plt.imshow(res_clahe, cmap='gray')
    plt.title("CLAHE enhancement - details are clear and natural")
    plt.axis('off')

    # 展示所有窗口
    print("正在弹出图片窗口，请查看...")
    plt.show()

# --- 文件路径 ---
file_path = r"F:\数据集\淋巴结转移\jpg\ROI有转移\1.740423.1443600870.36828.19920.3123408563.666607674.jpg"

if __name__ == "__main__":
    if os.path.exists(file_path):
        process_and_show_separate(file_path)
    else:
        print(f"文件未找到，请检查路径是否正确:\n{file_path}")