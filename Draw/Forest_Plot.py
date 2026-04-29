#森林图
import matplotlib.pyplot as plt
import numpy as np
import matplotlib

# ================= 中文字体 =================
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False

# ================= 数据 =================
factors = ["Nodule diameter (>0.74 mm)", "DTC_min (≤1.86 mm)", "Aspect ratio (≤1)", "Microcalcification"]
OR = np.array([3.289, 2.176, 1.571, 2.946])
lower = np.array([2.155, 1.360, 1.020, 1.845])
upper = np.array([5.013, 3.480, 2.420, 4.706])

# ================= 排序（按 OR）=================
order = np.argsort(OR)
factors = np.array(factors)[order]
OR = OR[order]
lower = lower[order]
upper = upper[order]

y_pos = np.arange(len(factors))

# ================= 显著性判断 =================
significant = (lower > 1) | (upper < 1)

# ================= 画图 =================
fig, ax = plt.subplots(figsize=(7, 4.5))

# 误差条
ax.errorbar(
    OR,
    y_pos,
    xerr=[OR - lower, upper - OR],
    fmt='o',
    #markerfacecolor='lightblue',   # ⭐ 点填充色（浅蓝）
    markerfacecolor="#7DBFEB",
    markeredgecolor='#7DBFEB',   # ⭐ 点边框色（同填充色，形成圆点效果）
    #markeredgecolor='black',       # ⭐ 点边框（更清晰）
    color='black',                # ⭐ 误差线颜色（黑）
    ecolor='black',
    elinewidth=1.5,
    capsize=4,
    markersize=6,
    zorder=3
)

# 参考线（OR=1）
ax.axvline(x=1, color='gray', linestyle='--', linewidth=1.5)

# log轴
ax.set_xscale('log')
ax.set_xlim(0.8, 6)

# 刻度（论文规范）
ax.set_xticks([0.8, 1, 2, 3, 4, 5, 6])
ax.get_xaxis().set_major_formatter(plt.ScalarFormatter())

# y轴
ax.set_yticks(y_pos)
ax.set_yticklabels(factors)

# 网格（弱化）
ax.grid(axis='x', linestyle=':', alpha=0.4)

# 标签
ax.set_xlabel("Odds Ratio (95% CI)", fontsize=11)

# ================= 添加文本（核心论文元素）=================
for i in range(len(factors)):
    text = f"{OR[i]:.2f} ({lower[i]:.2f}-{upper[i]:.2f})"
    
    # 显著性标记
    if significant[i]:
        text += " ★"
    
    ax.text(
        6.2, i, text,
        va='center',
        fontsize=10,
        color='#85C1E9'   # ⭐ 整行变浅蓝（包含星星）
    )

# 留出右侧空间放文本
ax.set_xlim(0.8, 7)

# 去掉多余边框（论文风格）
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.show()