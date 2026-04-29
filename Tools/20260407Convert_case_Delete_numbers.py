#转换大小写，删除数字，转换中文
import pandas as pd
import re
from pypinyin import lazy_pinyin

# =========================
# 输入输出路径
# =========================
input_path = r"F:\数据集\淋巴结转移\LLNM_label_name_delete.xlsx"
output_path = r"F:\数据集\淋巴结转移\LLNM_label_name_last.xlsx"

# =========================
# 判断是否包含中文
# =========================
def contains_chinese(text):
    return bool(re.search(r'[\u4e00-\u9fff]', text))

# =========================
# 处理 folder_name
# =========================
def process_folder_name(name):
    if pd.isna(name):
        return name

    name = str(name)

    # 1️⃣ 如果包含中文 → 转拼音
    if contains_chinese(name):
        name = ''.join(lazy_pinyin(name))

    # 2️⃣ 转小写
    name = name.lower()

    # 3️⃣ 删除所有非字母（包括数字、符号等）
    name = re.sub(r'[^a-z]', '', name)

    return name

# =========================
# 读取 Excel
# =========================
df = pd.read_excel(input_path)

# 检查列名（防止列顺序问题）
print("列名：", df.columns.tolist())

# =========================
# 处理第三列 folder_name
# =========================
folder_col = df.columns[2]  # 第三列

df[folder_col] = df[folder_col].apply(process_folder_name)

# =========================
# 保存结果
# =========================
df.to_excel(output_path, index=False)

print("处理完成，已保存到：", output_path)