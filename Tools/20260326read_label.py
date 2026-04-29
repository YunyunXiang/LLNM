#读取有无转移的图像名字，并标注label

import os
import pandas as pd

# =========================
# 1. 路径设置
# =========================
dir_no_metastasis = r"F:\数据集\淋巴结转移\jpg\ROI无转移"
dir_metastasis = r"F:\数据集\淋巴结转移\jpg\ROI有转移"

output_path = r"F:\数据集\淋巴结转移\LLNM_label.xlsx"

# =========================
# 2. 读取无转移图片（label=0）
# =========================
data = []

for file_name in os.listdir(dir_no_metastasis):
    if file_name.lower().endswith(".jpg"):
        data.append([file_name, 0])

# =========================
# 3. 读取有转移图片（label=1）
# =========================
for file_name in os.listdir(dir_metastasis):
    if file_name.lower().endswith(".jpg"):
        data.append([file_name, 1])

# =========================
# 4. 转为 DataFrame
# =========================
df = pd.DataFrame(data, columns=["name", "label"])

# （可选）打乱顺序
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

# =========================
# 5. 保存为 Excel
# =========================
df.to_excel(output_path, index=False)

print(f"已生成标签文件：{output_path}")
print(f"总样本数：{len(df)}")
print(df.head())