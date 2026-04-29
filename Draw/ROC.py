#绘制ROC曲线，本代码没有删除Tgab，需要删除
import os
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.metrics import roc_curve, auc, f1_score, recall_score, confusion_matrix

from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier

from xgboost import XGBClassifier

import matplotlib.pyplot as plt

# =========================
# 1️⃣ 读取Excel
# =========================
excel_path = r"F:\数据集\淋巴结转移\complete_information_last.xlsx"
df = pd.read_excel(excel_path)

# label
y_all = df['label'].values

# =========================
# 2️⃣ 处理组学特征（仅修NaN）
# =========================

def process_modality(df, mode):
    data = df.copy()

    # ===== 模态1 =====
    if mode == "mod1":
        cols = ['距离/mm', '大小', '钙化']
        data = data[cols + ['label']].dropna()
        data = pd.get_dummies(data, columns=['钙化'])

    # ===== 模态2 =====
    elif mode == "mod2":
        cols = ['球蛋白抗体']
        data = data[cols + ['label']].dropna()

    # ===== 模态3 =====
    elif mode == "mod3":
        cols = ['TPO']
        data = data[cols + ['label']].dropna()

    # ===== 模态4 =====
    elif mode == "mod4":
        cols = ['BRAF V600']
        data = data[cols + ['label']].dropna()

        data['BRAF V600'] = data['BRAF V600'].map({
            '突变型': 1,
            '野生型': 0
        })

        data = data.dropna()   # 🔥 修复点1：map后再次清洗

    # ===== 全模态 =====
    elif mode == "all":
        cols = ['距离/mm', '大小', '钙化', '球蛋白抗体', 'TPO', 'BRAF V600']
        data = data[cols + ['label']].dropna()

        data = pd.get_dummies(data, columns=['钙化'])
        data['BRAF V600'] = data['BRAF V600'].map({'突变型': 1, '野生型': 0})

        data = data.dropna()   # 🔥 修复点1

    X = data.drop(columns=['label']).values
    y = data['label'].values

    return X, y, data.index


# =========================
# 3️⃣ 读取影像特征
# =========================
img_feat_path = r"..."#特征文件路径
X_img_all = np.load(img_feat_path)

# =========================
# 4️⃣ 模型定义（完全没动）
# =========================

models = {
    "RF": RandomForestClassifier(n_estimators=100),
    "SVM": SVC(probability=True),
    "XGB": XGBClassifier(eval_metric='logloss'),
    "LR": LogisticRegression(max_iter=1000),
    "KNN": KNeighborsClassifier()
}

# =========================
# 5️⃣ 核心实验函数（仅修NaN）
# =========================

def run_experiment(X_img, X_omics, y, name):

    print(f"\n========== {name} ==========")

    # ===== 标准化 =====
    scaler_img = StandardScaler()
    X_img = scaler_img.fit_transform(X_img)

    if X_omics is not None:
        scaler_omics = StandardScaler()
        X_omics = scaler_omics.fit_transform(X_omics)

        alpha = 0.7
        beta = 0.3

        X = np.concatenate([alpha * X_img, beta * X_omics], axis=1)
    else:
        X = X_img

    # 🔥🔥🔥 修复点2：终极删除NaN样本（关键！！）
    mask = ~np.isnan(X).any(axis=1)
    X = X[mask]
    y = y[mask]

    # ===== 特征选择（完全没动）=====
    selector = SelectKBest(f_classif, k=30)
    X[:, :30] = selector.fit_transform(X[:, :190], y)

    kf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    for model_name, model in models.items():

        auc_list, f1_list, sen_list, spe_list = [], [], [], []
        tprs = []
        mean_fpr = np.linspace(0, 1, 100)

        for train_idx, test_idx in kf.split(X, y):

            X_train, X_test = X[train_idx], X[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]

            model.fit(X_train, y_train)

            y_prob = model.predict_proba(X_test)[:, 1]
            y_pred = (y_prob > 0.5).astype(int)

            fpr, tpr, _ = roc_curve(y_test, y_prob)
            roc_auc = auc(fpr, tpr)
            auc_list.append(roc_auc)

            tpr_interp = np.interp(mean_fpr, fpr, tpr)
            tpr_interp[0] = 0.0
            tprs.append(tpr_interp)

            f1_list.append(f1_score(y_test, y_pred))
            sen_list.append(recall_score(y_test, y_pred))

            tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
            spe_list.append(tn / (tn + fp))

        print(f"{model_name:5s} | "
              f"AUC {np.mean(auc_list):.3f}±{np.std(auc_list):.3f} | "
              f"F1 {np.mean(f1_list):.3f}±{np.std(f1_list):.3f} | "
              f"Sen {np.mean(sen_list):.3f}±{np.std(sen_list):.3f} | "
              f"Spe {np.mean(spe_list):.3f}±{np.std(spe_list):.3f}")

        # ===== ROC =====
        mean_tpr = np.mean(tprs, axis=0)
        mean_auc = np.mean(auc_list)

        plt.plot(mean_fpr, mean_tpr, label=f"{model_name} (AUC={mean_auc:.3f})")

    plt.plot([0,1],[0,1],'--')
    plt.title(name)
    plt.xlabel("FPR")
    plt.ylabel("TPR")
    plt.legend()
    plt.show()


# =========================
# 6️⃣ 开始实验
# =========================

# ① Image Only
run_experiment(X_img_all, None, y_all, "Image Only")

# ② 各模态
for mode in ["mod1", "mod2", "mod3", "mod4", "all"]:

    X_omics, y, idx = process_modality(df, mode)

    X_img = X_img_all[idx]

    run_experiment(X_img, X_omics, y, f"Image + {mode}")
