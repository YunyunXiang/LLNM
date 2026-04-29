#根据表格标签移动图片
import os
import shutil
import pandas as pd

# ====== 路径配置 ======
excel_path = r"F:\数据集\淋巴结转移\新增ROI_jpg_name_with_label.xlsx"

jpg_src = r"F:\数据集\淋巴结转移\新增ROI_jpg"
png_src = r"F:\数据集\淋巴结转移\新增ROI_png"

jpg_dst_0 = r"F:\数据集\淋巴结转移\jpg\ROI无转移"
jpg_dst_1 = r"F:\数据集\淋巴结转移\jpg\ROI有转移"

png_dst_0 = r"F:\数据集\淋巴结转移\png\ROI无转移"
png_dst_1 = r"F:\数据集\淋巴结转移\png\ROI有转移"

# ====== 创建目标文件夹 ======
for path in [jpg_dst_0, jpg_dst_1, png_dst_0, png_dst_1]:
    os.makedirs(path, exist_ok=True)

# ====== 读取Excel ======
df = pd.read_excel(excel_path)

# ====== 检查列 ======
if not {"jpg_name", "label"}.issubset(df.columns):
    raise ValueError("Excel必须包含列：jpg_name 和 label")

# ====== 记录异常 ======
missing_jpg = []
missing_png = []

# ====== 主逻辑 ======
for idx, row in df.iterrows():
    jpg_name = str(row["jpg_name"]).strip()
    label = row["label"]

    # 跳过空label
    if pd.isna(label):
        continue

    label = int(label)

    # ====== 构造文件路径 ======
    jpg_path = os.path.join(jpg_src, jpg_name)

    png_name = jpg_name.replace(".jpg", ".png")
    png_path = os.path.join(png_src, png_name)

    # ====== 选择目标路径 ======
    if label == 0:
        jpg_dst = jpg_dst_0
        png_dst = png_dst_0
    elif label == 1:
        jpg_dst = jpg_dst_1
        png_dst = png_dst_1
    else:
        print(f"⚠️ 非法label（跳过）：{jpg_name} -> {label}")
        continue

    # ====== 复制 jpg ======
    if os.path.exists(jpg_path):
        shutil.copy(jpg_path, os.path.join(jpg_dst, jpg_name))
    else:
        missing_jpg.append(jpg_name)

    # ====== 复制 png ======
    if os.path.exists(png_path):
        shutil.copy(png_path, os.path.join(png_dst, png_name))
    else:
        missing_png.append(png_name)

# ====== 输出结果 ======
print("✅ 处理完成！")

print(f"缺失 jpg 数量：{len(missing_jpg)}")
if len(missing_jpg) > 0:
    print("示例：", missing_jpg[:5])

print(f"缺失 png 数量：{len(missing_png)}")
if len(missing_png) > 0:
    print("示例：", missing_png[:5])