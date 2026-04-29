#把中文转换成拼音
import pandas as pd
from pypinyin import lazy_pinyin

# =========================
# 文件路径
# =========================
input_path = r"F:\数据集\淋巴结转移\add_pinyin.xlsx"
output_path = r"F:\数据集\淋巴结转移\add_pinyin1.xlsx"

# =========================
# 读取Excel
# =========================
df = pd.read_excel(input_path)

# =========================
# 定义中文转拼音函数（小写 + 无空格）
# =========================
def chinese_to_pinyin(name):
    if pd.isna(name):
        return name
    return ''.join(lazy_pinyin(str(name))).lower()

# =========================
# 新增拼音列（列名为：姓名拼音）
# =========================
df['姓名拼音'] = df.iloc[:, 1].apply(chinese_to_pinyin)

# =========================
# 保存新文件
# =========================
df.to_excel(output_path, index=False)

print("处理完成！已保存到：", output_path)