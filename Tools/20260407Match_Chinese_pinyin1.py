#解决多音字不匹配问题
import pandas as pd
from pypinyin import pinyin, Style
from itertools import product
from rapidfuzz import fuzz

# =========================
# 1. 文件路径
# =========================
file1_path = r"F:\数据集\淋巴结转移\LLNM_label_name_last.xlsx"
file2_path = r"F:\数据集\淋巴结转移\add_pinyin.xlsx"
output_path = r"F:\数据集\淋巴结转移\complete_information.xlsx"
unmatched_path = r"F:\数据集\淋巴结转移\unmatched_file.xlsx"

# =========================
# 2. 读取数据
# =========================
df1 = pd.read_excel(file1_path)
df2 = pd.read_excel(file2_path)

# =========================
# 3. 标准化字符串
# =========================
def normalize(s):
    return str(s).strip().lower().replace(" ", "")

df1['folder_name'] = df1['folder_name'].apply(normalize)
df2['姓名拼音'] = df2['姓名拼音'].apply(normalize)

# =========================
# 4. 生成“多音字拼音组合”
# =========================
def get_all_pinyin_combinations(name):
    pys = pinyin(name, style=Style.NORMAL, heteronym=True)
    combinations = product(*pys)
    result = [''.join(p) for p in combinations]
    return result

# =========================
# 5. 给文件2生成多音字候选拼音
# =========================
df2['all_pinyin'] = df2['姓名'].apply(get_all_pinyin_combinations)

# =========================
# 6. 匹配函数（核心）
# =========================
def match_pinyin(pinyin1, candidate_list, threshold=90):
    best_score = 0
    best_match = None

    for cand in candidate_list:
        score = fuzz.ratio(pinyin1, cand)
        if score > best_score:
            best_score = score
            best_match = cand

    return best_score, best_match

# =========================
# 7. 逐行匹配（文件1 → 文件2）
# =========================
merged_rows = []
unmatched_rows = []

for idx1, row1 in df1.iterrows():
    p1 = row1['folder_name']

    best_score = 0
    best_row2 = None

    for idx2, row2 in df2.iterrows():
        score, _ = match_pinyin(p1, row2['all_pinyin'])

        if score > best_score:
            best_score = score
            best_row2 = row2

    # 阈值（建议90以上）
    if best_score >= 90:
        merged_rows.append({
            'image_name': row1['name'],
            'label': row1['label'],
            'subject_name': best_row2['姓名'],
            'pinyin': row1['folder_name'],
            '日期': best_row2['日期'],
            '备注': best_row2['备注'],
            '性别': best_row2['性别'],
            '年龄': best_row2['年龄'],
            'ID号': best_row2['ID号'],
            '部位-前后被膜': best_row2['部位-前后被膜'],
            '距离/mm': best_row2['距离/mm'],
            '大小': best_row2['大小'],
            'TPO': best_row2['TPO'],
            'BRAF V600': best_row2['BRAF V600'],
            '姓名拼音': best_row2['姓名拼音'],
            'match_score': best_score
        })
    else:
        unmatched_rows.append({
            'image_name': row1['name'],
            'label': row1['label'],
            'pinyin': row1['folder_name'],
            'best_score': best_score
        })

# =========================
# 8. 保存结果
# =========================
df_merged = pd.DataFrame(merged_rows)
df_unmatched = pd.DataFrame(unmatched_rows)

df_merged.to_excel(output_path, index=False)
df_unmatched.to_excel(unmatched_path, index=False)

# =========================
# 9. 输出统计
# =========================
print("===== 完成 =====")
print(f"总数: {len(df1)}")
print(f"匹配成功: {len(df_merged)}")
print(f"未匹配: {len(df_unmatched)}")