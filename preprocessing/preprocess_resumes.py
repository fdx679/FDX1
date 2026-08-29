# -*- coding: utf-8 -*-
"""
简历数据预处理脚本
====================
输入 : data/raw/resumes_raw.csv（公开数据集 Kaggle Resume Dataset 镜像）
输出 : data/preprocessed/ 目录下：
    - resumes_clean.csv            清洗并去隐私后的完整简历数据
    - resumes_train.csv            训练集（按类别分层 8:2）
    - resumes_test.csv             测试集（按类别分层 8:2）
    - resume_preprocess_report.json 预处理统计报告

预处理内容
----------
1. 文本清洗：去 HTML 标签、URL、多余空白、控制字符
2. 隐私保护：掩码化邮箱、电话号码、身份证等个人信息（课程设计要求去除个人信息）
3. 文本规范化：统一换行与空白
4. 分层划分：按类别(Category)分层 8:2 划分训练/测试集，保证各类别比例一致
"""

import os
import re
import json
import html as html_lib
import pandas as pd

# ---------------------------------------------------------------------------
# 路径配置
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_PATH = os.path.join(BASE_DIR, "data", "raw", "resumes_raw.csv")
OUT_DIR = os.path.join(BASE_DIR, "data", "preprocessed")
os.makedirs(OUT_DIR, exist_ok=True)

RANDOM_SEED = 42
TEST_RATIO = 0.2

# ---------------------------------------------------------------------------
# 1. 文本清洗函数
# ---------------------------------------------------------------------------

# 个人信息掩码正则（隐私保护）
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(
    r"(?<!\d)"
    r"(\+?\d{1,3}[\s\-\.]?)?(\(?\d{3,4}\)?[\s\-\.]?)?\d{3,4}[\s\-\.]?\d{4}"
    r"(?!\d)"
)
URL_RE = re.compile(r"https?://\S+|www\.\S+")
# 身份证号（15/18位）
ID_CARD_RE = re.compile(r"\b\d{17}[\dXx]\b|\b\d{15}\b")

CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def clean_text(text: str) -> str:
    """对简历文本做清洗：去HTML、URL、控制字符、规范化空白。"""
    if not isinstance(text, str):
        return ""
    # 去除 HTML 标签
    text = re.sub(r"<[^>]+>", " ", text)
    # 反转义 HTML 实体
    text = html_lib.unescape(text)
    # 去除 URL
    text = URL_RE.sub(" ", text)
    # 去除控制字符
    text = CONTROL_CHARS_RE.sub(" ", text)
    # 规范化空白（制表符/多空格/换行）
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def mask_pii(text: str) -> str:
    """掩码个人信息（隐私保护）：邮箱、电话、身份证号。"""
    if not isinstance(text, str):
        return ""
    text = EMAIL_RE.sub("[EMAIL]", text)
    text = ID_CARD_RE.sub("[ID-CARD]", text)
    text = PHONE_RE.sub("[PHONE]", text)
    return text


# ---------------------------------------------------------------------------
# 2. 主流程
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("简历数据预处理")
    print("=" * 60)

    # 读取原始数据
    df = pd.read_csv(RAW_PATH, encoding="utf-8", on_bad_lines="skip")
    print(f"读取原始简历: {len(df)} 条")
    print(f"列名: {list(df.columns)}")

    # 数据校验：至少包含类别与文本列
    assert "Category" in df.columns, "缺少 Category 列"
    text_col = "Resume" if "Resume" in df.columns else df.columns[1]
    print(f"文本列: {text_col}")

    # 去重与空值处理
    df = df.dropna(subset=[text_col])
    df = df.drop_duplicates(subset=[text_col]).reset_index(drop=True)

    # 文本清洗 + 隐私掩码
    df["Resume_clean"] = df[text_col].apply(clean_text)
    df["Resume_clean"] = df["Resume_clean"].apply(mask_pii)

    # 过滤清洗后为空的记录
    df = df[df["Resume_clean"].str.len() > 50].reset_index(drop=True)

    # 统计文本长度
    df["Resume_length"] = df["Resume_clean"].str.len()
    len_stats = df["Resume_length"].describe().to_dict()

    # 类别分布
    cat_counts = df["Category"].value_counts().to_dict()

    # -----------------------------------------------------------------------
    # 分层 8:2 划分训练/测试集
    # -----------------------------------------------------------------------
    train_list, test_list = [], []
    for cat, group in df.groupby("Category", sort=False):
        n_test = max(1, round(len(group) * TEST_RATIO))
        # 每个类别打乱后取后 n_test 条为测试集（保证测试集各类别至少1条）
        g = group.sample(frac=1.0, random_state=RANDOM_SEED)
        test_list.append(g.iloc[:n_test])
        train_list.append(g.iloc[n_test:])
    train_df = pd.concat(train_list, ignore_index=True)
    test_df = pd.concat(test_list, ignore_index=True)

    # 输出统一列
    out_cols = ["Category", "Resume_clean", "Resume_length"]
    train_df[out_cols].to_csv(
        os.path.join(OUT_DIR, "resumes_train.csv"), index=False, encoding="utf-8-sig"
    )
    test_df[out_cols].to_csv(
        os.path.join(OUT_DIR, "resumes_test.csv"), index=False, encoding="utf-8-sig"
    )
    df[out_cols].to_csv(
        os.path.join(OUT_DIR, "resumes_clean.csv"), index=False, encoding="utf-8-sig"
    )

    # 训练/测试类别分布核验
    train_cat = train_df["Category"].value_counts().to_dict()
    test_cat = test_df["Category"].value_counts().to_dict()

    # -----------------------------------------------------------------------
    # 预处理报告
    # -----------------------------------------------------------------------
    report = {
        "source": "data/raw/resumes_raw.csv",
        "source_dataset": "Kaggle Resume Dataset (snehaanbhawal/resume-dataset)",
        "source_url": "https://www.kaggle.com/datasets/snehaanbhawal/resume-dataset",
        "raw_records": int(len(df)),
        "cleaned_records": int(len(df)),
        "num_categories": int(df["Category"].nunique()),
        "train_records": int(len(train_df)),
        "test_records": int(len(test_df)),
        "split_ratio": "8:2 (stratified by category)",
        "random_seed": RANDOM_SEED,
        "text_length_stats": {k: round(float(v), 2) for k, v in len_stats.items()},
        "category_distribution": cat_counts,
        "train_category_distribution": train_cat,
        "test_category_distribution": test_cat,
        "preprocessing_steps": [
            "去HTML标签与反转义",
            "去URL",
            "去控制字符",
            "规范化空白",
            "掩码邮箱/电话/身份证（隐私保护）",
            "按类别分层8:2划分训练/测试集",
        ],
    }
    with open(
        os.path.join(OUT_DIR, "resume_preprocess_report.json"),
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # 输出摘要
    print(f"\n清洗后简历总数 : {len(df)}")
    print(f"类别数         : {df['Category'].nunique()}")
    print(f"训练集         : {len(train_df)} ({(1-TEST_RATIO)*100:.0f}%)")
    print(f"测试集         : {len(test_df)} ({TEST_RATIO*100:.0f}%)")
    print(f"平均文本长度   : {len_stats['mean']:.1f} 字符")
    print(f"\n输出文件:")
    for fn in ["resumes_clean.csv", "resumes_train.csv", "resumes_test.csv",
               "resume_preprocess_report.json"]:
        print(f"  - data/preprocessed/{fn}")
    print("\n预处理完成。")


if __name__ == "__main__":
    main()
