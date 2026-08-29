# FDX1 — 课程设计项目

## 项目题目

**基于深度学习与知识图谱的智能招聘简历筛选系统设计与实现**

- 深度学习（BERT）：简历文本实体识别与岗位分类
- 知识图谱（Neo4j）：岗位技能知识图谱构建与推理
- 机器学习（逻辑回归）：候选人匹配度排序
- Web 开发（Flask + Vue）：演示系统

详细选题与方案见 [选题说明.md](选题说明.md) 与 [方案设计.md](方案设计.md)。

---

## 数据来源说明

课程设计数据位于 [`data/`](data/) 目录，详情见 [`data/README.md`](data/README.md)。

### 1. 简历数据集（主数据集 · 公开数据集）

| 项目 | 内容 |
|------|------|
| 数据集名称 | Resume Dataset（Kaggle） |
| 来源链接 | https://www.kaggle.com/datasets/snehaanbhawal/resume-dataset |
| 说明 | 约 2400 份英文简历，25 个岗位类别，公开可下载。本仓库 `data/raw/resumes_raw.csv` 为该数据集公开镜像子集（169 条，覆盖全部 25 类），可直接用于课程设计；完整版请访问 Kaggle 链接获取。 |
| 用途 | 简历文本分类、技能匹配 |

### 2. 岗位描述数据集（辅助数据集 · 公开数据集 + 自建补充）

| 项目 | 内容 |
|------|------|
| 公开数据来源 | Indeed Job Listings 样本：https://github.com/luminati-io/Indeed-dataset-samples |
| 自建补充 | 对 Indeed 样本中缺失的技术类岗位（Python/Web设计/自动化测试/区块链/SAP/机械/电气/土木工程），人工整理 16 条自建岗位描述，已标注 `Source=自建数据集`。 |
| 用途 | 构建岗位技能知识图谱（岗位→技能）、候选人岗位匹配 |

> **数据合规**：本仓库数据均来自公开数据集或自建演示数据，不包含私有敏感信息；简历预处理已执行隐私掩码（邮箱/电话/身份证）。

---

## 数据预处理

预处理程序位于 [`preprocessing/`](preprocessing/)：

| 脚本 | 功能 |
|------|------|
| `preprocess_resumes.py` | 简历清洗、隐私掩码、按类别分层 8:2 划分训练/测试集 |
| `preprocess_jobs.py` | 岗位筛选、文本清洗、技能抽取、生成岗位-技能关系表 |
| `verify_output.py` | 预处理结果核验脚本 |

预处理后数据（`data/preprocessed/`）：

| 数据 | 数量 |
|------|------|
| 简历（清洗后） | 166 条 / 25 类 |
| 简历训练集 / 测试集 | 135 条（80%）/ 31 条（20%） |
| 岗位 | 71 条 / 25 类（55 条公开 + 16 条自建） |
| 岗位-技能关系 | 291 条 / 85 个技能 |

复现预处理：

```bash
cd preprocessing
python preprocess_resumes.py
python preprocess_jobs.py
```

---

## AI 工具提示词追溯

与 AI 助手在课程设计全流程中的交流记录保存在 [`prompt/`](prompt/) 目录，用于开发过程追溯：

- `prompt/conversation_log.json` — AI 交流记录（JSON），每个开发阶段同步更新
- `prompt/README.md` — 记录格式与更新机制说明

后续每个阶段（模型训练、知识图谱构建、Web 系统开发、测试部署）完成后将追加更新。

---

## 项目结构

```
FDX1/
├── README.md              # 本文件
├── 选题说明.md            # 选题与目标
├── 方案设计.md            # 技术方案
├── 学习笔记.md            # AI工具学习笔记
├── data/                  # 数据（原始 + 预处理后）
│   ├── README.md          # 数据来源与预处理说明
│   ├── raw/               # 原始数据
│   └── preprocessed/      # 预处理后数据
├── preprocessing/         # 数据预处理程序
└── prompt/                # AI 交流记录（提示词追溯）
```
