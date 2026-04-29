#匹配jpg和对应的name
import os
import pandas as pd

# ===== 路径 =====
file1_path = r"F:\数据集\淋巴结转移\Read_Name_all.xlsx"
file2_path = r"F:\数据集\淋巴结转移\LLNM_label1.xlsx"
save_path = r"F:\数据集\淋巴结转移\LLNM_label_name.xlsx"

# ===== 读取 Excel =====
df1 = pd.read_excel(file1_path)  # 文件1：文件夹名 + jpg名
df2 = pd.read_excel(file2_path)  # 文件2：name + label

# ===== 确保列名正确（防止中文/空格问题）=====
df1.columns = ["folder", "jpg_name"]
df2.columns = ["name", "label"]

# ===== 构建映射：jpg名 -> 文件夹名 =====
# 注意：如果有重复jpg名，保留第一个（一般不会重复）
mapping = dict(zip(df1["jpg_name"], df1["folder"]))

# ===== 匹配并生成新列 =====
df2["folder_name"] = df2["name"].map(mapping)

# ===== 保存结果 =====
os.makedirs(os.path.dirname(save_path), exist_ok=True)
df2.to_excel(save_path, index=False)

print("处理完成！结果已保存到：", save_path)

# ===== 可选：输出匹配情况 =====
matched = df2["folder_name"].notna().sum()
total = len(df2)
print(f"匹配成功: {matched} / {total}")