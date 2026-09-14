# 数据集来源说明（/data）

本项目数据分为两类：**自建模拟小数据**（直接入库）与**公开数据集参考**（提供来源链接，不下载大文件入库）。

---

## 一、自建模拟数据（直接入库，数据量小）

> 依据精密切削加工领域常识生成，非真实企业数据，无隐私风险。

| 文件 | 说明 | 行数 | 生成脚本 |
|---|---|---|---|
| `raw/process_quality_raw.csv` | 工艺参数 + 质检结果：转速、进给、切深、冷却液温度、主轴负载、尺寸误差、是否缺陷 | 200 | `scripts/generate_raw_data.py` |
| `raw/sensor_timeseries_raw.csv` | 6 台设备 × 120 cycle 的传感器时序：振动 RMS、温度、电流、累计运行时长 | 720 | `scripts/generate_raw_data.py` |

预处理后产物（见 `processed/`）：

| 文件 | 说明 |
|---|---|
| `processed/quality_features.csv` | 工艺质量数据经清洗、派生特征、one-hot、标准化后的建模特征（200×18） |
| `processed/equipment_health.csv` | 传感器时序经 10 步滑动窗口统计、健康分与预警等级（666 行窗口特征） |
| `processed/preprocessing_summary.json` | 预处理步骤与标准化参数摘要 |

---

## 二、公开数据集（提供来源链接，不入库）

### NASA C-MAPSS 涡扇发动机退化仿真数据集

用于**预测性维护（LSTM/RUL）模块的建模范式参考与算法验证**。

- **数据集说明**：NASA 预测数据中心（PCoE）发布，记录多台涡扇发动机在 21 个传感器通道下从全新状态到失效的时序退化数据，并提供剩余使用寿命（RUL）标签，是国际上预测性维护领域最经典的公开基准数据集。
- **官方来源链接（已验证可访问）**：
  - NASA PCoE 预测数据仓库：<https://ti.arc.nasa.gov/tech/dash/groups/pcoe/prognostic-data-repository/>
  - NASA Open Data 镜像：<https://data.nasa.gov/dataset/C-MAPSS-Turbofan-Engine-Degradation-Simulatio/>
- **本项目使用方式**：借鉴其"多维传感器时序 → 剩余寿命/健康退化"的建模思路，迁移到制造车间设备（振动 RMS、温度、电流）场景；本地 `raw/sensor_timeseries_raw.csv` 即按该退化范式模拟生成。

> 本项目未将该公开数据集原始文件（约数 MB）克隆进仓库，仅引用链接；如后端算法需要，可按上述链接下载 `train_FD001.txt` 等文件放入本目录。

---

## 三、数据合规说明

- 不使用任何真实企业内部数据或私有敏感数据；
- 自建模拟数据仅用于课程教学演示；
- 公开数据集遵循 NASA 公开数据集引用规范（见参考文献 [1][7]）。
