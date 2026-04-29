#统计特征可视化
import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import skew, kurtosis

# ==========================================
# 1. 路径设置 
# ==========================================
img_path = r'F:\数据集\淋巴结转移\jpg\ROI有转移\1.740423.1443600870.36828.19920.3123408563.666607674.jpg'

# ==========================================
# 2. 图像预处理 
# ==========================================
# 使用 np.fromfile 防止中文路径报错
img = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
img_resized = cv2.resize(img, (128, 128))

# 应用 CLAHE 增强
clahe = cv2.create_CLE = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
img_enhanced = clahe.apply(img_resized)

# 展平像素用于计算统计量
pixels = img_enhanced.flatten()

# ==========================================
# 3. 计算四维一阶统计特征
# ==========================================
feat_mean = np.mean(pixels)
feat_std = np.std(pixels)
feat_skew = skew(pixels)
feat_kurt = kurtosis(pixels)

# ==========================================
# 4. 绘图可视化
# ==========================================
plt.figure(figsize=(14, 5), dpi=120)
plt.rcParams['font.family'] = 'Arial'

# --- 子图 1: 处理后的 ROI 图像 ---
plt.subplot(1, 3, 1)
plt.imshow(img_enhanced, cmap='gray')
plt.title('Processed Ultrasound ROI', fontsize=14, pad=10)
plt.axis('off')

# --- 子图 2: 像素强度直方图 ---
plt.subplot(1, 3, 2)
sns.histplot(pixels, bins=50, kde=True, color='skyblue', edgecolor='white')
plt.axvline(feat_mean, color='red', linestyle='--', label=f'Mean: {feat_mean:.2f}')
plt.title('Pixel Intensity Distribution', fontsize=14, pad=10)
plt.xlabel('Intensity Value (0-255)')
plt.ylabel('Frequency')
plt.legend()

# --- 子图 3: 特征数值面板 ---
plt.subplot(1, 3, 3)
plt.axis('off')
text_str = (
    f"First-order Statistical Features\n\n"
    f"● Mean (mean brightness): {feat_mean:.4f}\n"
    f"  [Reflect the overall echo level of ROI]\n\n"
    f"● Std Deviation: {feat_std:.4f}\n"
    f"  [Reflect internal heterogeneity/coarseness]\n\n"
    f"● Skewness: {feat_skew:.4f}\n"
    f"  [Reflect the symmetry of brightness distribution]\n\n"
    f"● Kurtosis: {feat_kurt:.4f}\n"
    f"  [Reflect the sharpness or flatness of the distribution]"
)
plt.text(0.05, 0.5, text_str, fontsize=12, family='Microsoft YaHei', 
         verticalalignment='center', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

plt.tight_layout()
plt.show()

print(f"统计特征计算完毕: Mean={feat_mean:.2f}, Std={feat_std:.2f}, Skew={feat_skew:.2f}, Kurt={feat_kurt:.2f}")