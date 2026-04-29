#绘制五个模型的AUC图
import matplotlib.pyplot as plt
import numpy as np

modalities = [
    "Image",
    "Image+M1\n(DTC_min/Size/Calcification)",
    "Image+M2\n(TPO-Ab)",
    "Image+M3\n(BRAF V600E)",
    "Image+All"
]

# ===== 所有模型 =====
data = {
    "RF": {
        "auc": [0.837, 0.853, 0.845, 0.838, 0.862],
        "std": [0.022, 0.013, 0.015, 0.013, 0.017]
    },
    "SVM": {
        "auc": [0.796, 0.811, 0.797, 0.797, 0.819],
        "std": [0.008, 0.013, 0.012, 0.015, 0.018]
    },
    "XGB": {
        "auc": [0.829, 0.881, 0.845, 0.840, 0.906],
        "std": [0.016, 0.017, 0.022, 0.027, 0.028]
    },
    "LR": {
        "auc": [0.837, 0.862, 0.839, 0.840, 0.865],
        "std": [0.031, 0.032, 0.032, 0.027, 0.035]
    },
    "KNN": {
        "auc": [0.736, 0.748, 0.752, 0.738, 0.755],
        "std": [0.051, 0.060, 0.085, 0.075, 0.084]
    }
}

for model in data:
    auc = np.array(data[model]["auc"])
    std = np.array(data[model]["std"])
    x = np.arange(len(modalities))

    plt.figure(figsize=(8, 5))
    plt.bar(x, auc, yerr=std, capsize=5, color='lightblue')

    plt.xticks(x, modalities, rotation=30, ha='right')
    plt.ylabel("AUC")
    plt.title(f"AUC (Adaptive Zoom) - {model}")

    # ===== ⭐ 自适应y轴 =====
    # ===== ⭐ 自动范围（完整包含误差棒）=====
    y_max = np.max(auc + std)
    y_min = np.min(auc - std)

    # ===== ⭐ 加留白（关键）=====
    margin = (y_max - y_min) * 0.3

    plt.ylim(y_min - margin, y_max + margin)

    # ===== ⭐ 标注偏移=====
    offset = (y_max - y_min) * 0.05

    for i, (a, s) in enumerate(zip(auc, std)):
        plt.text(
            i,
            a + s + offset,
            f"{a:.3f}±{s:.3f}",
            ha='center',
            va='bottom',
            fontsize=9
        )

    plt.tight_layout()
    plt.show()