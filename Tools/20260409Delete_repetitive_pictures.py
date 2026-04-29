#删除重复的图片名行
import pandas as pd

# ====== 路径 ======
input_path = r"F:\数据集\淋巴结转移\complete_information.xlsx"
output_path = r"F:\数据集\淋巴结转移\complete_information_last.xlsx"

# ====== 读取 ======
df = pd.read_excel(input_path)

# ====== 检查列 ======
if "image_name" not in df.columns:
    raise ValueError("缺少列：image_name")

# ====== 清洗 ======
df["image_name"] = df["image_name"].astype(str).str.strip()

# =========================================================
# （1）找重复的“图片名”（唯一值）
# =========================================================
dup_names = df["image_name"][df["image_name"].duplicated()].unique()

print("\n========== 重复的图片名（去重后） ==========")
if len(dup_names) == 0:
    print("无")
else:
    for name in dup_names:
        print(name)
print(f"重复图片种类数：{len(dup_names)}")

# =========================================================
# （2）找出“将被删除的行”（保留第一条，其余删除）
# =========================================================
to_delete = df[df["image_name"].duplicated(keep="first")]

print("\n========== 将被删除的重复行 ==========")
if len(to_delete) == 0:
    print("无")
else:
    for name in to_delete["image_name"]:
        print(name)
print(f"删除行数：{len(to_delete)}")

# =========================================================
# （3）去重（只保留第一条）
# =========================================================
df_clean = df.drop_duplicates(subset="image_name", keep="first")

# =========================================================
# （4）保存
# =========================================================
df_clean.to_excel(output_path, index=False)

print("\n✅ 去重完成！")
print(f"原始行数：{len(df)}")
print(f"去重后行数：{len(df_clean)}")
print(f"结果已保存到：{output_path}")