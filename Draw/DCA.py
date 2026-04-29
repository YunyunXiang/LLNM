#绘制DCA曲线
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
from sklearn.calibration import CalibratedClassifierCV
from xgboost import XGBClassifier
import matplotlib.pyplot as plt
from sklearn.impute import SimpleImputer

# =========================
# 1️⃣ 读取Excel (请确保路径正确)
# =========================
excel_path = r"F:\数据集\淋巴结转移\complete_information_last.xlsx"

if not os.path.exists(excel_path):
    df['距离/mm'] = 1; df['大小'] = 1; df['钙化'] = '有'; df['球蛋白抗体'] = 1; df['TPO'] = 1; df['BRAF V600'] = '野生型'
else:
    df = pd.read_excel(excel_path)

y_all = df['label'].values

# =========================
# 2️⃣ 处理组学特征
# =========================
def process_modality(df, mode):
    data = df.copy()
    if mode == "all":
        cols = ['距离/mm', '大小', '钙化', '球蛋白抗体', 'TPO', 'BRAF V600']
        data = data[cols + ['label']].dropna()
        data = pd.get_dummies(data, columns=['钙化'])
        data['BRAF V600'] = data['BRAF V600'].map({'突变型': 1, '野生型': 0})

    X = data.drop(columns=['label']).values
    y = data['label'].values
    return X, y, data.index

# =========================
# 3️⃣ 影像特征 (模拟加载)
# =========================
img_feat_path = r"..."#npy特征文件路径
if os.path.exists(img_feat_path):
    X_img_all = np.load(img_feat_path)
else:
    X_img_all = np.random.randn(len(df), 190)

# =========================
# 4️⃣ DCA 计算函数
# =========================
def calculate_net_benefit(y_true, y_probs, thresholds):
    net_benefits = []
    n = len(y_true)
    for pt in thresholds:
        # 计算当前阈值下的 TP 和 FP
        y_pred = (y_probs >= pt).astype(int)
        tp = np.sum((y_pred == 1) & (y_true == 1))
        fp = np.sum((y_pred == 1) & (y_true == 0))
        
        if pt == 1.0: # 防止除以0
            nb = 0
        else:
            nb = (tp / n) - (fp / n) * (pt / (1 - pt))
        net_benefits.append(nb)
    return net_benefits

# =========================
# 5️⃣ 实验函数 (包含DCA绘图)
# =========================
def run_experiment(X_img, X_omics, y, name):
    print(f"\n========== {name} (DCA Analysis) ==========")

    scaler_img = StandardScaler()
    X_img = scaler_img.fit_transform(X_img)

    if X_omics is not None:
        scaler_omics = StandardScaler()
        X_omics = scaler_omics.fit_transform(X_omics)
        alpha, beta = 0.7, 0.3
        X = np.concatenate([alpha * X_img, beta * X_omics], axis=1)
    else:
        X = X_img

    # 原始全局特征选择
    selector = SelectKBest(f_classif, k=30)
    if X.shape[1] >= 190:
        X[:, :30] = selector.fit_transform(X[:, :190], y)

    kf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    # 准备绘图
    plt.figure(figsize=(10, 8))
    thresholds = np.linspace(0, 0.99, 100) # 阈值范围从 0 到 1

    # 为了画 DCA 基准线 (Treat All / Treat None)
    # 我们只需要在第一轮循环外计算一次基准线
    prevalence = np.mean(y)
    net_benefit_all = [prevalence - (1 - prevalence) * (pt / (1 - pt)) if pt < 1 else 0 for pt in thresholds]
    
    # 存储每个模型的预测结果以便计算汇总DCA
    models_to_run = {
        "RF": RandomForestClassifier(n_estimators=100),
        "SVM": "custom_svm",
        "XGB": XGBClassifier(eval_metric='logloss'),
        "LR": "custom_lr",
        "KNN": "custom_knn"
    }

    for model_name, base_model in models_to_run.items():
        all_y_true = []
        all_y_probs = []

        for train_idx, test_idx in kf.split(X, y):
            X_train, X_test = X[train_idx], X[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]

            imputer = SimpleImputer(strategy='mean')
            X_train = imputer.fit_transform(X_train)
            X_test = imputer.transform(X_test)

            # --- 保留你的原模型逻辑 ---
            if model_name == "KNN":
                selector_knn = SelectKBest(f_classif, k=30)
                X_img_train, X_img_test = X_train[:, :190], X_test[:, :190]
                X_img_train_new = selector_knn.fit_transform(X_img_train, y_train)
                X_img_test_new = selector_knn.transform(X_img_test)
                X_train = np.concatenate([X_img_train_new, X_train[:, 190:]], axis=1)
                X_test = np.concatenate([X_img_test_new, X_test[:, 190:]], axis=1)
                
                scaler = StandardScaler()
                X_train = scaler.fit_transform(X_train)
                X_test = scaler.transform(X_test)
                
                cov = np.cov(X_train, rowvar=False) + np.eye(X_train.shape[1]) * 1e-6
                VI = np.linalg.pinv(cov)
                model = KNeighborsClassifier(n_neighbors=5, weights='distance', metric='mahalanobis', metric_params={'VI': VI})

            elif model_name == "SVM":
                selector_svm = SelectKBest(f_classif, k=40)
                X_img_train, X_img_test = X_train[:, :190], X_test[:, :190]
                X_img_train_new = selector_svm.fit_transform(X_img_train, y_train)
                X_img_test_new = selector_svm.transform(X_img_test)
                X_train = np.concatenate([X_img_train_new, X_train[:, 190:]], axis=1)
                X_test = np.concatenate([X_img_test_new, X_test[:, 190:]], axis=1)
                
                scaler = StandardScaler()
                X_train = scaler.fit_transform(X_train)
                X_test = scaler.transform(X_test)
                base_svm = SVC(kernel='rbf', C=5, gamma='scale', probability=True)
                model = CalibratedClassifierCV(base_svm, method='sigmoid', cv=3)

            elif model_name == "LR":
                selector_lr = SelectKBest(f_classif, k=50)
                X_img_train, X_img_test = X_train[:, :190], X_test[:, :190]
                X_img_train_new = selector_lr.fit_transform(X_img_train, y_train)
                X_img_test_new = selector_lr.transform(X_img_test)
                X_train = np.concatenate([X_img_train_new, X_train[:, 190:]], axis=1)
                X_test = np.concatenate([X_img_test_new, X_test[:, 190:]], axis=1)
                
                scaler = StandardScaler()
                X_train = scaler.fit_transform(X_train)
                X_test = scaler.transform(X_test)
                base_lr = LogisticRegression(penalty='l1', solver='liblinear', C=1.5, max_iter=2000)
                model = CalibratedClassifierCV(base_lr, method='sigmoid', cv=3)
            else:
                model = base_model

            model.fit(X_train, y_train)
            y_prob = model.predict_proba(X_test)[:, 1]
            
            all_y_true.extend(y_test)
            all_y_probs.extend(y_prob)

        # 计算该模型的 DCA 曲线
        all_y_true = np.array(all_y_true)
        all_y_probs = np.array(all_y_probs)
        
        # 简单打印一下AUC看看性能是否正常
        fpr, tpr, _ = roc_curve(all_y_true, all_y_probs)
        current_auc = auc(fpr, tpr)
        print(f"{model_name:5s} | Aggregated AUC: {current_auc:.3f}")

        net_benefits = calculate_net_benefit(all_y_true, all_y_probs, thresholds)
        plt.plot(thresholds, net_benefits, label=f"{model_name} (AUC={current_auc:.3f})", lw=2)

    # 绘制基准线
    plt.plot(thresholds, net_benefit_all, color='black', linestyle='--', label='Treat All', alpha=0.5)
    plt.axhline(y=0, color='gray', linestyle='-', label='Treat None', alpha=0.5)

    # 美化图表
    plt.ylim(-0.1, max(prevalence + 0.1, 0.5)) # 动态设置y轴
    plt.xlim(0, 0.8)#全图是1，医学常用0.1-0.6，预估患者患病的概率
    plt.xlabel('Threshold Probability', fontsize=12)
    plt.ylabel('Net Benefit', fontsize=12)
    plt.title(f'Decision Curve Analysis: {name}', fontsize=14)
    plt.legend(loc='upper right')
    plt.grid(alpha=0.3)
    plt.show()

# =========================
# 6️⃣ 运行实验
# =========================
# 任务 1: 仅影像
run_experiment(X_img_all, None, y_all, "Image Only")

# 任务 2: 影像 + 组学
X_omics, y_omics, idx = process_modality(df, "{mode}")
X_img_sub = X_img_all[idx]
run_experiment(X_img_sub, X_omics, y_omics, "Image + Omics Combined")