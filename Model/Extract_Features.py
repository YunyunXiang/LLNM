#从图片中提取190维特征
import os
import cv2
import numpy as np
import pandas as pd
from tqdm import tqdm

from skimage.feature import graycomatrix, graycoprops, local_binary_pattern, hog

# =========================
# 1️⃣ 路径
# =========================

excel_path = r"F:\数据集\淋巴结转移\complete_information_last.xlsx"

img_dir_0 = r"F:\数据集\淋巴结转移\jpg\ROI无转移"
img_dir_1 = r"F:\数据集\淋巴结转移\jpg\ROI有转移"

save_path = r"..."#保存特征文件的路径

# =========================
# 2️⃣ 读取Excel
# =========================

df = pd.read_excel(excel_path)

# =========================
# 3️⃣ 构建文件名 → 路径映射（支持中文）
# =========================

def build_img_dict(folder):
    d = {}
    for f in os.listdir(folder):
        d[f] = os.path.join(folder, f)
    return d

dict0 = build_img_dict(img_dir_0)
dict1 = build_img_dict(img_dir_1)

img_dict = {**dict0, **dict1}

# =========================
# 4️⃣ CLAHE增强
# =========================

def clahe(img):
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    return clahe.apply(img)

# =========================
# 5️⃣ 特征提取（≈190维）
# =========================

def extract_features(img):

    feats = []

    # ===== resize =====
    img = cv2.resize(img, (128, 128))

    # ===== CLAHE =====
    img = clahe(img)

    # ===== 一阶统计 =====
    feats.extend([
        np.mean(img),
        np.std(img),
        np.min(img),
        np.max(img),
        np.percentile(img, 25),
        np.percentile(img, 50),
        np.percentile(img, 75)
    ])

    # ===== GLCM =====
    glcm = graycomatrix(img, distances=[1,2], angles=[0, np.pi/4, np.pi/2], levels=256, symmetric=True, normed=True)

    props = ['contrast', 'dissimilarity', 'homogeneity', 'energy', 'correlation']

    for p in props:
        feats.extend(graycoprops(glcm, p).flatten())

    # ===== LBP =====
    lbp = local_binary_pattern(img, P=8, R=1, method='uniform')
    hist, _ = np.histogram(lbp, bins=59, range=(0,59))
    feats.extend(hist)

    # ===== HOG =====
    hog_feat = hog(img, pixels_per_cell=(16,16), cells_per_block=(2,2), feature_vector=True)
    feats.extend(hog_feat[:100])  # 控制维度

    return np.array(feats)


# =========================
# 6️⃣ 主循环（按Excel顺序）
# =========================

features = []
valid_index = []

for i, row in tqdm(df.iterrows(), total=len(df)):

    name = row['image_name']

    if name not in img_dict:
        print(f"⚠️ 找不到图像: {name}")
        continue

    path = img_dict[name]

    # 中文路径读取
    img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)

    if img is None:
        print(f"⚠️ 读取失败: {name}")
        continue

    feat = extract_features(img)

    features.append(feat)
    valid_index.append(i)

# =========================
# 7️⃣ 转numpy并保存
# =========================

X = np.array(features)

print("特征维度:", X.shape)

np.save(save_path, X)

# 同时保存index（用于对齐）
np.save(save_path.replace(".npy", "_index.npy"), np.array(valid_index))

print("✅ 特征提取完成！")