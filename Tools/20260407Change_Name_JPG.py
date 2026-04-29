#修改JPG文件名，去掉"_结果"后缀
""" 
👉 只要文件名是：xxx_结果.jpg
👉 就重命名为：xxx.jpg
"""
import os

# =========================
# 图片文件夹路径
# =========================
folder_path = r"F:\数据集\淋巴结转移\jpg\ROI无转移"

# =========================
# 遍历并重命名
# =========================
for filename in os.listdir(folder_path):
    # 只处理 jpg 文件
    if filename.lower().endswith(".jpg"):
        
        # 判断是否包含 "_结果"
        if filename.endswith("_结果.jpg"):
            
            old_path = os.path.join(folder_path, filename)
            
            # 去掉 "_结果"
            new_name = filename.replace("_结果.jpg", ".jpg")
            new_path = os.path.join(folder_path, new_name)
            
            # 如果目标文件已存在，避免覆盖
            if os.path.exists(new_path):
                print(f"跳过（已存在）: {new_name}")
                continue
            
            # 执行重命名
            os.rename(old_path, new_path)
            print(f"已重命名: {filename} -> {new_name}")

print("全部处理完成！")