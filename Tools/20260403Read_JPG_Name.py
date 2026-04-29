#遍历保存jpg与对应上一级文件夹名称
import os
from openpyxl import Workbook

# ===== 路径设置 =====
root_dir = r"G:\第三部分\有淋巴结转移\有淋巴结转移"
save_path = r"F:\数据集\淋巴结转移\Read_Name1.xlsx"

# ===== 创建Excel =====
wb = Workbook()
ws = wb.active
ws.title = "Sheet1"

# 写表头（可要可不要）
ws.append(["文件夹名", "jpg文件名"])

# ===== 遍历文件夹 =====
for folder_name in os.listdir(root_dir):
    folder_path = os.path.join(root_dir, folder_name)

    # 只处理文件夹
    if os.path.isdir(folder_path):
        try:
            for file_name in os.listdir(folder_path):
                # 只读取 jpg（不区分大小写）
                if file_name.lower().endswith(".jpg"):
                    ws.append([folder_name, file_name])

        except Exception as e:
            print(f"读取失败: {folder_path}, 错误: {e}")

# ===== 保存Excel =====
os.makedirs(os.path.dirname(save_path), exist_ok=True)
wb.save(save_path)

print("处理完成，已保存到：", save_path)