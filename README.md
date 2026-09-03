# FDX1 — 课程设计项目

## 项目题目

**基于深度学习与知识图谱的智能招聘简历筛选系统设计与实现**

- 深度学习（BERT 方案 / 演示版 TF-IDF+逻辑回归）：简历文本实体识别与岗位分类
- 知识图谱（Neo4j 方案 / 演示版 networkx）：岗位技能知识图谱构建与推理
- 机器学习（逻辑回归）：候选人匹配度排序
- Web 开发（Flask + 前端页面）：演示系统

详细选题与方案见 [选题说明.md](选题说明.md)、[方案设计.md](方案设计.md)、[docs/选题提交.md](docs/选题提交.md)。

---

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 运行自动化测试（23 项）
pytest tests/

# 3. 启动系统
python run.py
# 浏览器访问 http://127.0.0.1:5000
```

### 一键启动（便捷入口）

项目提供 `start.bat` 一键启动脚本，避免每次手动输入命令：

- 双击 `start.bat`（或桌面快捷方式「启动智能招聘系统」）即可；
- 脚本自动判断：服务已在运行 → 直接打开网页；服务未运行 → 自动后台启动并等待端口就绪后打开网页；
- `start.bat` 已显式指定安装好依赖的 Python 解释器绝对路径，双击执行不依赖系统 PATH，规避 WindowsApps 占位符导致 `pip` 不可用的问题。

系统为本地可现场演示版本：SQLite 数据库、networkx 知识图谱、TF-IDF+逻辑回归分类，均无需外网/重型服务，ECharts 已本地化。

---

## 系统架构

```
前端演示界面(HTML/CSS/JS+ECharts)
      │ REST API
后端服务(Flask) ── 简历解析 ── 岗位分类 ── 知识图谱 ── 匹配排序
      │
数据层: data/raw(原始) · data/preprocessed(预处理后) · SQLite
```

业务闭环：简历上传 → 文本解析 → 岗位分类 → 技能抽取 → 知识图谱推理（缺失技能） → 多维匹配排序 → 前端可视化 → 历史入库。

---

## 数据来源说明

课程设计数据位于 [`data/`](data/) 目录，详情见 [`data/README.md`](data/README.md)。

### 1. 简历数据集（主数据集 · 公开数据集）

| 项目 | 内容 |
|------|------|
| 数据集名称 | Resume Dataset（Kaggle） |
| 来源链接 | https://www.kaggle.com/datasets/snehaanbhawal/resume-dataset |
| 说明 | 约 2400 份英文简历，25 个岗位类别。本仓库 `data/raw/resumes_raw.csv` 为公开镜像子集（169 条，覆盖全部 25 类），可直接用于课程设计；完整版请访问 Kaggle 链接。 |
| 用途 | 简历文本分类、技能匹配 |

### 2. 岗位描述数据集（辅助数据集 · 公开数据集 + 自建补充）

| 项目 | 内容 |
|------|------|
| 公开数据来源 | Indeed Job Listings 样本：https://github.com/luminati-io/Indeed-dataset-samples |
| 自建补充 | 对缺失技术类岗位人工整理 16 条自建岗位描述，标注 `Source=自建数据集` |
| 用途 | 构建岗位技能知识图谱（岗位→技能）、候选人岗位匹配 |

> **数据合规**：本仓库数据均来自公开数据集或自建演示数据，不包含私有敏感信息；简历预处理已执行隐私掩码（邮箱/电话/身份证）。

---

## 数据预处理

预处理程序位于 [`preprocessing/`](preprocessing/)，预处理后数据位于 `data/preprocessed/`：

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

## 文档

| 文档 | 说明 |
|------|------|
| [docs/需求规格说明书.md](docs/需求规格说明书.md) | 功能/数据/非功能需求、接口、验收标准 |
| [docs/选题提交.md](docs/选题提交.md) | 技术方向映射表、架构草图、数据来源 |
| [docs/vibe_coding_notes.md](docs/vibe_coding_notes.md) | vibe coding 方法学习笔记 |
| [docs/设计报告.md](docs/设计报告.md) | 设计报告（含 AI 使用披露） |
| [prompt/](prompt/) | AI 交流记录（提示词追溯） |

---

## 项目结构

```
FDX1/
├── README.md              # 本文件
├── run.py                 # 系统启动入口
├── requirements.txt       # 依赖清单
├── app/                   # 系统源码
│   ├── __init__.py        # Flask 应用工厂
│   ├── api/               # REST API（resume/match/graph/system）
│   ├── models/            # 算法模块（解析/分类/图谱/匹配/技能）
│   ├── database.py        # SQLite 数据库
│   └── static/            # 前端演示页面（HTML/CSS/JS+ECharts）
├── tests/                 # pytest 自动化测试（23 项）
├── data/                  # 数据（原始 + 预处理后）
│   ├── README.md
│   ├── raw/
│   └── preprocessed/
├── preprocessing/         # 数据预处理程序
├── docs/                  # 课程设计文档
├── prompt/                # AI 交流记录（提示词追溯）
├── 选题说明.md / 方案设计.md / 学习笔记.md
```
