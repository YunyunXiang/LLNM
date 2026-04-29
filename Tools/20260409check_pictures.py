#检查图片是否存在，检查图片是否重复
import os
import pandas as pd

# ====== 路径 ======
excel_path = r"F:\数据集\淋巴结转移\complete_information.xlsx"

folder_0 = r"F:\数据集\淋巴结转移\jpg\ROI无转移"
folder_1 = r"F:\数据集\淋巴结转移\jpg\ROI有转移"

# ====== 读取 Excel ======
df = pd.read_excel(excel_path)

# ====== 检查列 ======
if "image_name" not in df.columns:
    raise ValueError("Excel缺少列：image_name")

# ====== 转为字符串并去空格 ======
df["image_name"] = df["image_name"].astype(str).str.strip()

# =========================================================
# （1）检查图片是否不存在
# =========================================================
missing_images = []

for name in df["image_name"]:
    path_0 = os.path.join(folder_0, name)
    path_1 = os.path.join(folder_1, name)

    if not os.path.exists(path_0) and not os.path.exists(path_1):
        missing_images.append(name)

print("\n========== 不存在的图片（两个文件夹都没有） ==========")
if len(missing_images) == 0:
    print("无")
else:
    for img in missing_images:
        print(img)
print(f"总数：{len(missing_images)}")

# =========================================================
# （2）检查重复 image_name（全部列出，不去重）
# =========================================================
duplicates = df[df["image_name"].duplicated(keep=False)]["image_name"].tolist()

print("\n========== Excel中重复的图片名（全部列出） ==========")
if len(duplicates) == 0:
    print("无")
else:
    for img in duplicates:
        print(img)
print(f"总数：{len(duplicates)}")