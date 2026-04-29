#输出遗漏的被试（没有图片的被试），最终版
import pandas as pd

# =========================
# 1. 文件路径
# =========================
file1_path = r"F:\数据集\淋巴结转移\LLNM_label_name_last.xlsx"
file2_path = r"F:\数据集\淋巴结转移\add_pinyin.xlsx"

output_path = r"F:\数据集\淋巴结转移\complete_information.xlsx"
unmatched1_path = r"F:\数据集\淋巴结转移\unmatched_file1.xlsx"
unmatched2_path = r"F:\数据集\淋巴结转移\unmatched_file2.xlsx"

# =========================
# 2. 读取数据
# =========================
df1 = pd.read_excel(file1_path)
df2 = pd.read_excel(file2_path)

# =========================
# 3. 统一拼音格式（非常关键）
# =========================
def normalize(s):
    return str(s).strip().lower().replace(" ", "")

df1['folder_name'] = df1['folder_name'].apply(normalize)
df2['姓名拼音'] = df2['姓名拼音'].apply(normalize)

# =========================
# 4. 合并（文件1为主）
# =========================
merged = pd.merge(
    df1,
    df2,
    left_on='folder_name',
    right_on='姓名拼音',
    how='left',
    indicator=True
)

# =========================
# 5. 构造输出表
# =========================
result = pd.DataFrame()

result['image_name'] = merged['name']
result['label'] = merged['label']
result['subject_name'] = merged['姓名']
result['pinyin'] = merged['folder_name']

# 文件2字段
result['日期'] = merged['日期']
result['备注'] = merged['备注']
result['性别'] = merged['性别']
result['年龄'] = merged['年龄']
result['ID号'] = merged['ID号']
result['距离/mm'] = merged['距离/mm']
result['大小'] = merged['大小']
result['钙化'] = merged['钙化']
result['球蛋白抗体'] = merged['球蛋白抗体']
result['二分类'] = merged['二分类']
result['TPO'] = merged['TPO']
result['分组'] = merged['分组']
result['BRAF V600'] = merged['BRAF V600']
result['姓名拼音'] = merged['姓名拼音']

# =========================
# 6. 保存合并结果
# =========================
result.to_excel(output_path, index=False)

# =========================
# 7. 文件1未匹配
# =========================
unmatched1 = merged[merged['_merge'] == 'left_only']

unmatched1_out = unmatched1[['name', 'label', 'folder_name']]
unmatched1_out.columns = ['image_name', 'label', 'pinyin']

unmatched1_out.to_excel(unmatched1_path, index=False)

# =========================
# 8. 文件2未匹配（重点🔥）
# =========================

# 找出被匹配到的拼音
matched_pinyin = set(merged[merged['_merge'] == 'both']['姓名拼音'])

# 文件2中没被匹配的
unmatched2 = df2[~df2['姓名拼音'].isin(matched_pinyin)]

unmatched2.to_excel(unmatched2_path, index=False)

# =========================
# 9. 打印统计信息
# =========================
print("===== 完成 =====")
print(f"文件1总行数: {len(df1)}")
print(f"文件2总行数: {len(df2)}")

print(f"\n匹配成功: {(merged['_merge'] == 'both').sum()}")
print(f"文件1未匹配: {(merged['_merge'] == 'left_only').sum()}")
print(f"文件2未匹配: {len(unmatched2)}")

print(f"\n输出文件：")
print(f"✔ 合并结果: {output_path}")
print(f"✔ 文件1未匹配: {unmatched1_path}")
print(f"✔ 文件2未匹配: {unmatched2_path}")