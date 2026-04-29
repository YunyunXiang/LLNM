#删除名字中有_结果的图片
import os

# ====== 目标文件夹 ======
folder_path = r"F:\数据集\淋巴结转移\jpg\ROI有转移"

# ====== 统计 ======
to_delete = []

for file in os.listdir(folder_path):
    if file.lower().endswith(".jpg") and "_结果" in file:
        to_delete.append(file)

print(f"找到 {len(to_delete)} 个包含'_结果'的图片")

# ====== 先预览（防止误删）=====
for f in to_delete[:10]:
    print(f)

# ====== 确认删除 ======
confirm = input("是否删除这些文件？输入 y 确认：")

if confirm.lower() == 'y':
    for file in to_delete:
        file_path = os.path.join(folder_path, file)
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"删除失败：{file}，原因：{e}")

    print("✅ 删除完成！")
else:
    print("❌ 已取消删除")