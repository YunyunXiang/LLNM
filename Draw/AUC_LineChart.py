#AUC折线图
import matplotlib.pyplot as plt
import numpy as np

# ===== 横轴（已删除TGAB）=====
modalities = [
    "Image",
    "Image+M1\n(DTC_min/Size/Calcification)",
    "Image+M2\n(TPO-Ab)",
    "Image+M3\n(BRAF V600E)",
    "Image+All\n(M1+M2+M3)"
]

x = np.arange(len(modalities))

data = {
    "RF":  [0.837, 0.872, 0.851, 0.838, 0.880],
    "SVM": [0.796, 0.839, 0.801, 0.797, 0.843],
    "XGB": [0.829, 0.881, 0.845, 0.840, 0.906],
    "LR":  [0.826, 0.846, 0.835, 0.831, 0.848],
    "KNN": [0.736, 0.755, 0.741, 0.738, 0.751]
}

# ===== 画图 =====
plt.figure(figsize=(7, 5))

# ===== 五条曲线 =====
for model in data:
    if model == "XGB":
        plt.plot(x, data[model], marker='o', linewidth=2.5, label=model)
    else:
        plt.plot(x, data[model], marker='o', linewidth=1.8, alpha=0.85, label=model)

# ===== baseline（Image）=====
plt.axhline(data["XGB"][0], linestyle='--', linewidth=1)

# ===== 坐标 =====
plt.xticks(x, modalities, rotation=25, ha='right')
plt.ylabel("AUC")
plt.title("AUC Comparison Across Multimodal Combinations")

# ===== 放大差异 =====
plt.ylim(0.70, 0.95)

# ===== 网格 =====
plt.grid(axis='y', linestyle='--', alpha=0.6)

# ===== 图例 =====
plt.legend(loc='upper left', bbox_to_anchor=(1.02, 1))

plt.tight_layout()
plt.show()