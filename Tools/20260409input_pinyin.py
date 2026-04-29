#输出重复的姓名拼音
import pandas as pd

# ====== 路径 ======
file_path = r"F:\数据集\淋巴结转移\add_pinyin.xlsx"

# ====== 读取 ======
df = pd.read_excel(file_path)

# ====== 检查列 ======
if "姓名拼音" not in df.columns:
    raise ValueError("缺少列：姓名拼音")

# ====== 清洗（非常关键）=====
df["姓名拼音"] = df["姓名拼音"].astype(str).str.strip().str.lower()

# =========================================================
# （1）输出重复的拼音（去重后）
# =========================================================
dup_unique = df["姓名拼音"][df["姓名拼音"].duplicated()].unique()

print("\n========== 重复的姓名拼音（去重后） ==========")
if len(dup_unique) == 0:
    print("无")
else:
    for name in dup_unique:
        print(name)

print(f"重复拼音种类数：{len(dup_unique)}")

# =========================================================
# （2）输出所有重复行（不去重）
# =========================================================
dup_all = df[df["姓名拼音"].duplicated(keep=False)]

print("\n========== 所有重复的姓名拼音（完整列出） ==========")
if len(dup_all) == 0:
    print("无")
else:
    for name in dup_all["姓名拼音"]:
        print(name)

print(f"重复总行数：{len(dup_all)}")