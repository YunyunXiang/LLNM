#根据蔡非非.jpg去找蔡非非的分类
import pandas as pd

# ====== 路径 ======
file1_path = r"F:\数据集\淋巴结转移\新增ROI_jpg_name.xlsx"
file2_path = r"F:\数据集\淋巴结转移\tool.xlsx"
output_path = r"F:\数据集\淋巴结转移\新增ROI_jpg_name_with_label.xlsx"

# ====== 读取 Excel ======
df1 = pd.read_excel(file1_path)   # 包含 jpg_name
df2 = pd.read_excel(file2_path)   # 包含 姓名、分类

# ====== 基础检查 ======
if "jpg_name" not in df1.columns:
    raise ValueError("文件1缺少列：jpg_name")

if "姓名" not in df2.columns or "分类" not in df2.columns:
    raise ValueError("文件2缺少列：姓名 或 分类")

# ====== 去掉.jpg后缀，得到姓名 ======
df1["姓名"] = df1["jpg_name"].str.replace(".jpg", "", regex=False)

# ====== 去除可能的空格（很关键，防止匹配失败）=====
df1["姓名"] = df1["姓名"].str.strip()
df2["姓名"] = df2["姓名"].astype(str).str.strip()

# ====== 构建映射字典：姓名 -> 分类 ======
name_to_label = dict(zip(df2["姓名"], df2["分类"]))

# ====== 匹配并填充 label ======
df1["label"] = df1["姓名"].map(name_to_label)

# ====== 找出未匹配的（方便你检查）=====
unmatched = df1[df1["label"].isna()]
print(f"未匹配上的数量：{len(unmatched)}")

if len(unmatched) > 0:
    print("未匹配示例：")
    print(unmatched["jpg_name"].head())

# ====== 保存结果 ======
df1.to_excel(output_path, index=False)

print("处理完成！结果已保存到：", output_path)