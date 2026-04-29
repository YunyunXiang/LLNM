#绘制校准曲线，本代码没有删除Tgab，需要删除
import os
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

import matplotlib
matplotlib.use('Agg')  # 🔥 强制无界面保存图像（关键）
import matplotlib.pyplot as plt

from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.metrics import roc_curve, auc, f1_score, recall_score, confusion_matrix
from sklearn.calibration import calibration_curve
from sklearn.metrics import brier_score_loss

from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from xgboost import XGBClassifier


# =========================
# 1️⃣ 读取Excel
# =========================
excel_path = r"F:\数据集\淋巴结转移\complete_information_last.xlsx"
df = pd.read_excel(excel_path)

y_all = df['label'].values


# =========================
# 2️⃣ 处理组学特征
# =========================
def process_modality(df, mode):

    data = df.copy()

    if mode == "mod1":
        cols = ['距离/mm', '大小', '钙化']
        data = data[cols + ['label']].dropna()
        data = pd.get_dummies(data, columns=['钙化'])

    elif mode == "mod2":
        cols = ['球蛋白抗体']
        data = data[cols + ['label']].dropna()

    elif mode == "mod3":
        cols = ['TPO']
        data = data[cols + ['label']].dropna()

    elif mode == "mod4":
        cols = ['BRAF V600']
        data = data[cols + ['label']].dropna()
        data['BRAF V600'] = data['BRAF V600'].map({'突变型':1, '野生型':0})
        data = data.dropna()

    elif mode == "all":
        cols = ['距离/mm','大小','钙化','球蛋白抗体','TPO','BRAF V600']
        data = data[cols + ['label']].dropna()
        data = pd.get_dummies(data, columns=['钙化'])
        data['BRAF V600'] = data['BRAF V600'].map({'突变型':1, '野生型':0})
        data = data.dropna()

    X = data.drop(columns=['label']).values
    y = data['label'].values

    return X, y, data.index


# =========================
# 3️⃣ 影像特征
# =========================
img_feat_path = r"..."#特征文件路径
X_img_all = np.load(img_feat_path)


# =========================
# 4️⃣ 模型
# =========================
models = {
    "RF": RandomForestClassifier(n_estimators=100),
    "SVM": SVC(probability=True),
    "XGB": XGBClassifier(eval_metric='logloss'),
    "LR": LogisticRegression(max_iter=1000),
    "KNN": KNeighborsClassifier()
}


# =========================
# 5️⃣ 实验函数（含ROC + Calibration）
# =========================
def run_experiment(X_img, X_omics, y, name):

    print(f"\n========== {name} ==========")

    scaler_img = StandardScaler()
    X_img = scaler_img.fit_transform(X_img)

    if X_omics is not None:
        scaler_omics = StandardScaler()
        X_omics = scaler_omics.fit_transform(X_omics)
        X = np.concatenate([0.7*X_img, 0.3*X_omics], axis=1)
    else:
        X = X_img

    mask = ~np.isnan(X).any(axis=1)
    X = X[mask]
    y = y[mask]

    selector = SelectKBest(f_classif, k=30)
    X[:, :30] = selector.fit_transform(X[:, :190], y)

    kf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    # ================= ROC =================
    plt.figure(figsize=(6,6))

    # ================= Calibration =================
    plt.figure(figsize=(6,6))
    plt.plot([0,1],[0,1],'--', color='gray')

    for model_name, model in models.items():

        auc_list = []
        tprs = []
        mean_fpr = np.linspace(0,1,100)

        all_probs = []
        all_true = []

        for train_idx, test_idx in kf.split(X,y):

            X_train, X_test = X[train_idx], X[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]

            model.fit(X_train, y_train)

            y_prob = model.predict_proba(X_test)[:,1]

            # ===== ROC =====
            fpr, tpr, _ = roc_curve(y_test, y_prob)
            auc_list.append(auc(fpr,tpr))

            tpr_interp = np.interp(mean_fpr, fpr, tpr)
            tprs.append(tpr_interp)

            # ===== Calibration数据 =====
            all_probs.extend(y_prob)
            all_true.extend(y_test)

        # ===== ROC plot =====
        mean_tpr = np.mean(tprs, axis=0)
        mean_auc = np.mean(auc_list)

        plt.figure(1)
        plt.plot(mean_fpr, mean_tpr, label=f"{model_name} (AUC={mean_auc:.3f})")

        # ===== Calibration plot =====
        all_probs = np.array(all_probs)
        all_true = np.array(all_true)

        prob_true, prob_pred = calibration_curve(all_true, all_probs, n_bins=5)
        brier = brier_score_loss(all_true, all_probs)

        plt.figure(2)
        plt.plot(prob_pred, prob_true, marker='o',
                 label=f"{model_name} (Brier={brier:.3f})")

    # ===== 保存 ROC =====
    plt.figure(1)
    plt.plot([0,1],[0,1],'--')
    plt.xlabel("FPR")
    plt.ylabel("TPR")
    plt.title(name + " - ROC")
    plt.legend()
    plt.savefig(f"ROC_{name}.png", dpi=300)
    plt.close()

    # ===== 保存 Calibration =====
    plt.figure(2)
    plt.xlabel("Predicted Probability")
    plt.ylabel("Observed Probability")
    plt.title(name + " - Calibration")
    plt.legend()
    plt.savefig(f"Calibration_{name}.png", dpi=300)
    plt.close()


# =========================
# 6️⃣ 运行
# =========================

run_experiment(X_img_all, None, y_all, "Image_Only")

for mode in ["mod1","mod2","mod3","mod4","all"]:
    X_omics, y, idx = process_modality(df, mode)
    X_img = X_img_all[idx]
    run_experiment(X_img, X_omics, y, f"Image+{mode}")