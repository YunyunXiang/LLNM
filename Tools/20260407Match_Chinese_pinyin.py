#按照拼音和汉字对应合并
#相似度匹配，相似度需设置为0.6

import pandas as pd
import re
from pypinyin import lazy_pinyin
from difflib import SequenceMatcher

# =========================
# 路径
# =========================
file1_path = r"F:\数据集\淋巴结转移\LLNM_label_name_last.xlsx"
file2_path = r"F:\数据集\淋巴结转移\add.xlsx"
output_path = r"F:\数据集\淋巴结转移\complete_information.xlsx"

# =========================
# 拼音函数
# =========================
def to_pinyin(x):
    if pd.isna(x):
        return ""
    return ''.join(lazy_pinyin(str(x))).lower()

# =========================
# 清洗拼音（关键）
# =========================
def clean(x):
    if pd.isna(x):
        return ""

    x = str(x).lower()
    x = re.sub(r'[^a-z]', '', x)

    # 去前缀
    for p in ['ceus', 'fm', 'f', 'm']:
        if x.startswith(p) and len(x) > len(p)+3:
            x = x[len(p):]

    # 去重复（abcabc）
    half = len(x)//2
    if x[:half] == x[half:]:
        x = x[:half]

    return x

# =========================
# 相似度函数
# =========================
def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

# =========================
# 读取
# =========================
df1 = pd.read_excel(file1_path)
df2 = pd.read_excel(file2_path)

# 列
name1 = df1.columns[0]
label = df1.columns[1]
folder = df1.columns[2]

name2 = df2.columns[1]

# =========================
# 生成key
# =========================
df1["key"] = df1[folder].apply(clean)

df2["pinyin"] = df2[name2].apply(to_pinyin)
df2["key"] = df2["pinyin"].apply(clean)

# =========================
# 匹配（核心）
# =========================
results = []
unmatched = []

for _, r1 in df1.iterrows():
    k1 = r1["key"]

    best_score = 0
    best_row = None

    for _, r2 in df2.iterrows():
        k2 = r2["key"]

        score = similarity(k1, k2)

        if score > best_score:
            best_score = score
            best_row = r2

    # 阈值（可以调）
    if best_score >= 0.5:#0.8会有很多没有匹配到，改成0.6
        results.append({
            "image_name": r1[name1],
            "label": r1[label],
            "subject_name": best_row[name2],
            "日期": best_row[df2.columns[0]],
            "备注": best_row[df2.columns[2]],
            "性别": best_row[df2.columns[3]],
            "年龄": best_row[df2.columns[4]],
            "ID号": best_row[df2.columns[5]],
            "部位-前后被膜": best_row[df2.columns[6]],
            "距离/mm": best_row[df2.columns[7]],
            "大小": best_row[df2.columns[8]],
            "TPO": best_row[df2.columns[9]],
            "BRAF V600": best_row[df2.columns[10]],
            "match_score": best_score
        })
    else:
        unmatched.append({
            "image_name": r1[name1],
            "folder_name": r1[folder],
            "clean_key": k1,
            "best_score": best_score
        })

# =========================
# 保存结果
# =========================
result_df = pd.DataFrame(results)
result_df.to_excel(output_path, index=False)

# 未匹配（完整信息）
unmatched_df = pd.DataFrame(unmatched)
unmatched_df.to_excel(r"F:\数据集\淋巴结转移\unmatched_detail.xlsx", index=False)

print("✅ 完成")
print("总数:", len(df1))
print("匹配成功:", len(result_df))
print("未匹配:", len(unmatched_df))