#阅读并保存指定文件夹的JPG名字
import os
import pandas as pd

# ====== 路径 ======
folder_path = r"F:\数据集\淋巴结转移\新增ROI_jpg"
output_excel = r"F:\数据集\淋巴结转移\新增ROI_jpg_name.xlsx"

# ====== 读取jpg文件名 ======
jpg_names = []

for file in os.listdir(folder_path):
    if file.lower().endswith('.jpg'):
        jpg_names.append(file)

# ====== 转为DataFrame ======
df = pd.DataFrame(jpg_names, columns=["jpg_name"])

# ====== 保存为Excel ======
df.to_excel(output_excel, index=False)

print(f"完成，共读取 {len(jpg_names)} 个jpg文件！")