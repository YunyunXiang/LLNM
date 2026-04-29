#本代码仅用于测试，进行初步实验。是无ROI的图像识别
""" 
自动 ROI（无监督方式）：自动ROI = 中心裁剪 + Otsu阈值 + 最大连通域
步骤：
1️⃣ 去黑边（裁剪中心区域）
2️⃣ Otsu 二值化
3️⃣ 找最大连通区域（认为是组织区域）
4️⃣ crop 出 ROI
“弱ROI方法”

功能
✔ 自动ROI
✔ GLCM + LBP
✔ SVM分类
✔ 5-fold CV
✔ 输出：
AUC
F1-score
Sensitivity
Specificity
"""
import os
import cv2
import numpy as np
import pandas as pd
import torch
import torchvision.models as models
import torchvision.transforms as transforms

from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score, f1_score, confusion_matrix
import torch.nn as nn
import torch.optim as optim

# =========================
# 1. 参数
# =========================
PATCH_SIZE = 64
device = "cuda" if torch.cuda.is_available() else "cpu"

# =========================
# 2. 读取图像（支持中文）
# =========================
def cv_imread(path):
    return cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)

# =========================
# 3. 切patch
# =========================
def extract_patches(img):
    patches = []
    h, w = img.shape

    for i in range(0, h-PATCH_SIZE, PATCH_SIZE):
        for j in range(0, w-PATCH_SIZE, PATCH_SIZE):
            patch = img[i:i+PATCH_SIZE, j:j+PATCH_SIZE]
            patches.append(patch)

    return patches

# =========================
# 4. ResNet特征
# =========================
backbone = models.resnet18(pretrained=True)
backbone = nn.Sequential(*list(backbone.children())[:-1])
backbone.to(device)
backbone.eval()

transform = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((224,224)),
    transforms.ToTensor(),
])

def get_patch_features(patches):
    feats = []

    for p in patches:
        p = cv2.cvtColor(p, cv2.COLOR_GRAY2RGB)
        p = transform(p).unsqueeze(0).to(device)

        with torch.no_grad():
            f = backbone(p).cpu().numpy().flatten()

        feats.append(f)

    return np.array(feats)

# =========================
# 5. Attention pooling
# =========================
class AttentionMIL(nn.Module):
    def __init__(self, in_dim):
        super().__init__()
        self.attn = nn.Sequential(
            nn.Linear(in_dim, 128),
            nn.Tanh(),
            nn.Linear(128, 1)
        )
        self.cls = nn.Linear(in_dim, 1)

    def forward(self, x):
        A = self.attn(x)  # (N,1)
        A = torch.softmax(A, dim=0)

        M = torch.sum(A * x, dim=0)  # 加权

        out = torch.sigmoid(self.cls(M))
        return out

# =========================
# 6. 数据读取
# =========================
img_root_0 = r"F:\数据集\淋巴结转移\无转移"
img_root_1 = r"F:\数据集\淋巴结转移\有转移"
df = pd.read_excel(r"F:\数据集\淋巴结转移\LLNM_label.xlsx")

bags = []
labels = []

for _, row in df.iterrows():
    name = row['name']
    label = row['label']

    path = os.path.join(img_root_0 if label==0 else img_root_1, name)

    if not os.path.exists(path):
        continue

    img = cv_imread(path)
    if img is None:
        continue

    patches = extract_patches(img)
    feats = get_patch_features(patches)

    bags.append(feats)
    labels.append(label)

# =========================
# 7. 训练 + CV
# =========================
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

aucs = []

for train_idx, test_idx in skf.split(bags, labels):

    model = AttentionMIL(512).to(device)
    optimizer = optim.Adam(model.parameters(), lr=1e-4)
    loss_fn = nn.BCELoss()

    # ===== 训练 =====
    for epoch in range(10):
        model.train()
        for i in train_idx:
            x = torch.tensor(bags[i], dtype=torch.float32).to(device)
            y = torch.tensor([labels[i]], dtype=torch.float32).to(device)

            pred = model(x)
            loss = loss_fn(pred, y)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

    # ===== 测试 =====
    model.eval()
    y_true, y_prob = [], []

    for i in test_idx:
        x = torch.tensor(bags[i], dtype=torch.float32).to(device)

        with torch.no_grad():
            p = model(x).cpu().item()

        y_true.append(labels[i])
        y_prob.append(p)

    auc = roc_auc_score(y_true, y_prob)
    aucs.append(auc)

print("AUC:", np.mean(aucs))