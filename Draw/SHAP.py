#SHAP可视化
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import shap
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score, f1_score, confusion_matrix
from xgboost import XGBClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier

# Global Aesthetics Settings
plt.rcParams['font.family'] = 'Arial'  # Clean academic font
plt.rcParams['axes.unicode_minus'] = False
warnings.filterwarnings("ignore")

# ==========================================
# 1. Path and Data Loading
# ==========================================
excel_path = r"F:\数据集\淋巴结转移\complete_information_last.xlsx"
img_feat_path = r"..."#此处填入超声图像特征文件，要求是.npy格式

print("Loading data...")
df = pd.read_excel(excel_path)
X_img_raw = np.load(img_feat_path).astype(np.float32)
X_img_raw = np.nan_to_num(X_img_raw) 
y = df['label'].values

# ==========================================
# 2. Refined Image Feature Naming
# ==========================================
num_total_features = X_img_raw.shape[1]
img_feat_names_list = []

for i in range(num_total_features):
    if 0 <= i <= 3:
        cat = "Stats"
    elif 4 <= i <= 51:
        cat = "GLCM"
    elif 52 <= i <= 61:
        cat = "LBP"
    elif 62 <= i <= 189:
        cat = "HOG"
    else:
        cat = "Radiomics"
    # Format requested: Image_Feat_Index (Category)
    img_feat_names_list.append(f"Image_Feat_{i} ({cat})")

# ==========================================
# 3. Clinical Modality Preprocessing
# ==========================================
def preprocess_clinical(df_in):
    df_c = df_in.copy()
    
    # --- M1: Physical (DTC_min, Size, Calcification) ---
    df_c['DTC_min'] = pd.to_numeric(df_c['距离/mm'], errors='coerce').fillna(0)
    df_c['DTC_min (Missing)'] = df_c['距离/mm'].isna().astype(float)
    
    df_c['Size'] = pd.to_numeric(df_c['大小'], errors='coerce').fillna(0)
    df_c['Size (Missing)'] = df_c['大小'].isna().astype(float)
    
    df_c['Calcification'] = df_c['钙化'].astype(str).str.strip().map({
        '无': 0, '微钙化': 1, '粗大钙化': 2
    }).fillna(-1)

    m1_data = df_c[['DTC_min', 'Size', 'DTC_min (Missing)', 'Size (Missing)', 'Calcification']].astype(np.float32)

    # --- M2: TPO ---
    df_c['TPO'] = pd.to_numeric(df_c['TPO'], errors='coerce').fillna(0)
    df_c['TPO (Missing)'] = df_c['TPO'].isna().astype(float)
    m2_data = df_c[['TPO', 'TPO (Missing)']].astype(np.float32)

    # --- M3: BRAF V600 ---
    df_c['BRAF V600'] = df_c['BRAF V600'].astype(str).str.strip().map({
        '野生型': 0, '突变型': 1
    }).fillna(-1)
    m3_data = df_c[['BRAF V600']].astype(np.float32)

    return m1_data, m2_data, m3_data

m1_df, m2_df, m3_df = preprocess_clinical(df)

# ==========================================
# 4. Feature Selection
# ==========================================
k_val = min(30, num_total_features)
selector = SelectKBest(f_classif, k=k_val)
X_img_30 = selector.fit_transform(X_img_raw, y)

selected_indices = selector.get_support(indices=True)
selected_img_names = [img_feat_names_list[i] for i in selected_indices]

# Combination Definitions
mod_combos = {
    "Radiomics Only": X_img_30,
    "Radiomics + M1": np.hstack([X_img_30, m1_df.values]),
    "Radiomics + M2": np.hstack([X_img_30, m2_df.values]),
    "Radiomics + M3": np.hstack([X_img_30, m3_df.values]),
    "Radiomics + All Clinical": np.hstack([X_img_30, m1_df.values, m2_df.values, m3_df.values])
}

# ==========================================
# 5. Multimodal Experiment
# ==========================================
models = {
    "XGB": XGBClassifier(eval_metric='logloss', random_state=42, base_score=0.5),
    "RF": RandomForestClassifier(random_state=42),
    "SVM": SVC(probability=True, random_state=42),
    "LR": LogisticRegression(max_iter=1000),
    "KNN": KNeighborsClassifier()
}

results_list = []
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

for combo_name, X_full in mod_combos.items():
    X_full = np.nan_to_num(X_full).astype(np.float32)
    for model_name, model in models.items():
        metrics_cv = []
        for train_idx, val_idx in skf.split(X_full, y):
            X_tr, X_va = X_full[train_idx], X_full[val_idx]
            y_tr, y_va = y[train_idx], y[val_idx]
            sc = StandardScaler()
            X_tr_s = sc.fit_transform(X_tr)
            X_va_s = sc.transform(X_va)
            model.fit(X_tr_s, y_tr)
            y_prob = model.predict_proba(X_va_s)[:, 1]
            y_pred = (y_prob > 0.5).astype(int)
            auc = roc_auc_score(y_va, y_prob)
            f1 = f1_score(y_va, y_pred)
            tn, fp, fn, tp = confusion_matrix(y_va, y_pred).ravel()
            sens = tp/(tp+fn) if (tp+fn)>0 else 0
            spec = tn/(tn+fp) if (tn+fp)>0 else 0
            metrics_cv.append([auc, f1, sens, spec])
        avg, std = np.mean(metrics_cv, axis=0), np.std(metrics_cv, axis=0)
        results_list.append({"Combination": combo_name, "Model": model_name, "AUC": f"{avg[0]:.3f}±{std[0]:.3f}", 
                             "F1-Score": f"{avg[1]:.3f}±{std[1]:.3f}", "Sensitivity": f"{avg[2]:.3f}±{std[2]:.3f}", "Specificity": f"{avg[3]:.3f}±{std[3]:.3f}"})

print("\nMULTIMODAL PERFORMANCE SUMMARY")
print(pd.DataFrame(results_list))

# ==========================================
# 6. SHAP Visualization (XGBoost + All Clinical)
# ==========================================
print("\nRunning SHAP Analysis...")
X_final = mod_combos["Radiomics + All Clinical"]

# ===== 名称映射（只影响显示）=====
rename_dict = {
    "TPO": "TPO-Ab",
    "TPO (Missing)": "TPO-Ab (Missing)",
    "BRAF V600": "BRAF V600E"
}

all_feat_names = (
    selected_img_names
    + list(m1_df.columns)
    + [rename_dict.get(c, c) for c in m2_df.columns]
    + [rename_dict.get(c, c) for c in m3_df.columns]
)

final_model = XGBClassifier(eval_metric='logloss', random_state=42, base_score=0.5)
final_model.fit(X_final, y)

explainer = shap.Explainer(final_model.predict_proba, X_final, feature_names=all_feat_names)
shap_values = explainer(X_final)
shap_data = shap_values.values[:, :, 1] if len(shap_values.shape) == 3 else shap_values.values

# 6.1 SHAP Summary Dot Plot (展示影响方向)
plt.figure(figsize=(10, 8))
shap.summary_plot(shap_data, X_final, feature_names=all_feat_names, show=False)
plt.title("XGBoost Summary Dot Plot", fontsize=15, pad=20)
plt.tight_layout()
plt.show()

# 6.2 SHAP Global Importance Bar Plot (展示影响力排序 - 你要的排序柱状图)
plt.figure(figsize=(10, 8))
# plot_type="bar" 就会生成均值绝对值排序柱状图
shap.summary_plot(shap_data, X_final, feature_names=all_feat_names, plot_type="bar", show=False)
plt.title("XGBoost Feature Importance Ranking (Mean SHAP)", fontsize=15, pad=20)
plt.xlabel("mean(|SHAP value|) (Average impact on model output)", fontsize=12)
plt.tight_layout()
plt.show()

# 6.3 Modality Contribution Pie Chart (Donut Style)
mod_mapping = {
    "Radiomics": selected_img_names,
    "DTC_min/Size/Calcification (M1)": list(m1_df.columns),
    "TPO-Ab (M2)": ["TPO-Ab", "TPO-Ab (Missing)"],
    "BRAF V600E (M3)": ["BRAF V600E"]
}

mod_weights = {}
abs_shap = np.abs(shap_data)
for m_name, m_cols in mod_mapping.items():
    idxs = [all_feat_names.index(c) for c in m_cols]
    mod_weights[m_name] = np.mean(np.sum(abs_shap[:, idxs], axis=1))

colors = ["#7fb1e3", "#f9b282", "#91cf95", "#e98982"] 
total_val = sum(mod_weights.values())
labels = [f"{k}\n({v/total_val:.1%})" for k, v in mod_weights.items()]

fig, ax = plt.subplots(figsize=(8, 8), dpi=100)
wedges, texts = ax.pie(mod_weights.values(), labels=labels, startangle=140, colors=colors,
                                  wedgeprops={'width': 0.4, 'edgecolor': 'white', 'linewidth': 1.5},
                                  textprops={'fontsize': 11, 'fontweight': 'bold'})

plt.title("Contribution of Different Modalities\nto Metastasis Prediction", fontsize=16, fontweight='bold', pad=20)
centre_circle = plt.Circle((0,0), 0.70, fc='white')
fig.gca().add_artist(centre_circle)

for text in texts:
    text.set_color('#333333')

plt.tight_layout()
plt.show()

print("\nAnalysis finished successfully.")