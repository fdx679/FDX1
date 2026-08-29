# 数据目录说明（/data）

本目录存放《基于深度学习与知识图谱的智能招聘简历筛选系统设计与实现》课程设计所需的全部数据，包括**原始数据**与**预处理后数据**。

---

## 一、目录结构

```
data/
├── README.md                    # 本说明文件
├── raw/                         # 原始数据
│   ├── resumes_raw.csv          # 简历原始数据（169 条，25 个岗位类别）
│   └── jobs_indeed_raw.csv      # 岗位原始数据（Indeed 岗位样本 1000 条）
└── preprocessed/                # 预处理后数据（由 preprocessing/ 脚本生成）
    ├── resumes_clean.csv        # 清洗+去隐私后的完整简历（166 条）
    ├── resumes_train.csv        # 简历训练集（135 条，80%）
    ├── resumes_test.csv         # 简历测试集（31 条，20%）
    ├── resume_preprocess_report.json  # 简历预处理统计报告
    ├── jobs_clean.csv           # 筛选+清洗+技能抽取后的岗位数据（71 条，25 类）
    ├── jobs_skill_relation.csv  # 岗位-技能关系表（291 条，85 个技能）
    └── job_preprocess_report.json    # 岗位预处理统计报告
```

---

## 二、数据来源说明

### 1. 简历数据集（主数据集 · 公开数据集）

| 项目 | 内容 |
|------|------|
| 数据集名称 | Resume Dataset（Kaggle） |
| 来源链接 | https://www.kaggle.com/datasets/snehaanbhawal/resume-dataset |
| 说明 | 约 2400 份英文简历，涵盖 25 个岗位类别（Data Science、Java Developer、HR、DevOps 等），为公开可下载的数据集。 |
| 本仓库数据 | 本仓库 `raw/resumes_raw.csv` 为该数据集的公开镜像子集（169 条），覆盖全部 25 个类别，可直接用于课程设计演示与模型训练；如需完整版，请访问上方 Kaggle 链接获取。 |
| 镜像来源 | https://github.com/owais4321/Helping-HR-Automated-Resume-Classification（GitHub 公开镜像，便于国内直接下载） |
| 用途 | 简历文本分类（BERT 实体识别与类别预测）、候选人技能匹配 |

### 2. 岗位描述数据集（辅助数据集 · 公开数据集 + 自建补充）

| 项目 | 内容 |
|------|------|
| 公开数据来源 | Indeed Job Listings 样本：https://github.com/luminati-io/Indeed-dataset-samples |
| 公开数据说明 | 1000 条真实岗位发布信息（含岗位名称、公司、描述、地点等），从中筛选出与简历 25 个类别相关的岗位 55 条。 |
| 自建补充数据 | 由于 Indeed 样本中部分技术类岗位（Python Developer、Web Designing、Automation Testing、Blockchain、SAP Developer、Mechanical Engineer、Electrical Engineering、Civil Engineer）缺失，人工整理了 16 条**自建岗位描述**，标注 `Source=自建数据集`。 |
| 用途 | 构建岗位技能知识图谱（岗位→技能关系）、候选人岗位匹配打分 |

> **自建数据集说明**：`jobs_clean.csv` 中 `Source` 字段区分数据来源——`Indeed公开数据`（第三方公开数据）与 `自建数据集`（人工整理，仅用于课程设计，无第三方版权）。岗位-技能关系表 `jobs_skill_relation.csv` 同样标注来源。

---

## 三、数据预处理说明

预处理程序位于 `preprocessing/` 目录：

| 脚本 | 功能 |
|------|------|
| `preprocess_resumes.py` | 简历预处理：文本清洗、隐私掩码、按类别分层 8:2 划分训练/测试集 |
| `preprocess_jobs.py` | 岗位预处理：岗位筛选、文本清洗、技能抽取、生成岗位-技能关系表 |

### 简历预处理流程
1. 去 HTML 标签、URL、控制字符，规范化空白
2. **隐私保护**：掩码化简历中的邮箱（`[EMAIL]`）、电话（`[PHONE]`）、身份证号（`[ID-CARD]`）
3. 文本去重、过滤过短文本（>50 字符）
4. 按岗位类别分层 8:2 划分训练集/测试集（保证各类别比例一致）

### 岗位预处理流程
1. 根据简历 25 个类别，用关键词映射筛选 Indeed 原始数据中的相关岗位（每类最多 5 条）
2. 补充自建岗位描述，覆盖缺失的技术类岗位
3. 文本清洗（去 HTML/URL、规范化空白）
4. 基于技能词表从岗位描述中抽取技能关键词
5. 生成 `jobs_skill_relation.csv` 岗位-技能关系表，供知识图谱构建与匹配使用

### 预处理结果摘要

| 数据 | 数量 | 说明 |
|------|------|------|
| 简历（清洗后） | 166 条 | 25 类，平均文本长度约 2917 字符 |
| 简历训练集 | 135 条（80%） | 分层划分，覆盖 25 类 |
| 简历测试集 | 31 条（20%） | 分层划分，覆盖 25 类 |
| 岗位 | 71 条 | 覆盖 25 类（55 条公开 + 16 条自建） |
| 岗位-技能关系 | 291 条 | 85 个唯一技能 |

### 复现预处理
```bash
cd preprocessing
python preprocess_resumes.py
python preprocess_jobs.py
```
运行后自动覆盖更新 `data/preprocessed/` 下的输出文件与统计报告。

---

## 四、数据合规说明

1. 本目录数据均来自**公开数据集**（Kaggle / Indeed / GitHub 开源镜像）或**自建演示数据**，不包含任何私有、敏感或个人信息。
2. 简历预处理已执行隐私掩码，去除邮箱、电话、身份证等可识别信息。
3. 完整版简历数据集（约 2400 份）请在 Kaggle 官方页面下载（需 Kaggle 账号），链接见上表。
