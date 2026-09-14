# -*- coding: utf-8 -*-
"""
数据预处理程序。

读取 data/raw/ 下的原始数据，完成：
  1) 缺失值/异常值清洗
  2) 工艺质检数据：数值标准化、类别编码、派生特征
  3) 传感器时序数据：按设备滑动窗口提取统计特征、计算健康分

输出：
  data/processed/quality_features.csv       供质量缺陷预测模型使用
  data/processed/equipment_health.csv      供预测性维护模型使用
  data/processed/preprocessing_summary.json 预处理统计信息（供 README/调试）

运行：python scripts/preprocess.py
依赖：pandas, numpy
"""
import os
import json
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
PROC_DIR = os.path.join(BASE_DIR, "data", "processed")
os.makedirs(PROC_DIR, exist_ok=True)

NUMERIC_COLS = ["speed_rpm", "feed_rate", "depth_of_cut", "coolant_temp", "spindle_load"]
SENSOR_COLS = ["vibration_rms", "temperature", "current"]


def preprocess_quality() -> pd.DataFrame:
    df = pd.read_csv(os.path.join(RAW_DIR, "process_quality_raw.csv"))
    n_raw = len(df)

    # 1. 缺失值：数值列用中位数填充
    for c in NUMERIC_COLS:
        df[c] = df[c].fillna(df[c].median())

    # 2. 异常值：尺寸误差 > 0.20mm 视为记录错误，截断为 NaN 后按中位数补
    df.loc[df["dimension_error"] > 0.20, "dimension_error"] = np.nan
    df["dimension_error"] = df["dimension_error"].fillna(df["dimension_error"].median())

    # 3. 派生特征：工艺负荷指数（切深×进给）
    df["material_removal_rate"] = (df["depth_of_cut"] * df["feed_rate"]).round(4)

    # 4. 材料 one-hot 编码
    df = pd.get_dummies(df, columns=["material"], prefix="mat", dtype=int)

    # 5. 数值特征标准化（保存均值/标准差供后端推理复用）
    scaler_stats = {}
    for c in NUMERIC_COLS + ["material_removal_rate"]:
        mu, sd = df[c].mean(), df[c].std(ddof=0)
        df[c + "_z"] = ((df[c] - mu) / sd).round(5)
        scaler_stats[c] = {"mean": round(float(mu), 4), "std": round(float(sd), 4)}

    out_path = os.path.join(PROC_DIR, "quality_features.csv")
    df.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"[OK] 工艺质量预处理: {out_path}  shape={df.shape} (原始 {n_raw} 行)")
    return df, scaler_stats


def preprocess_equipment() -> pd.DataFrame:
    df = pd.read_csv(os.path.join(RAW_DIR, "sensor_timeseries_raw.csv"))
    n_raw = len(df)
    window = 10  # 滑动窗口大小

    feat_rows = []
    # 阈值依据：振动 RMS 0.3~1.2、温度 35~75、电流 8~14
    thr_vib = (0.3, 1.2)
    thr_temp = (35.0, 75.0)
    thr_curr = (8.0, 14.0)

    for eid, g in df.groupby("equipment_id"):
        g = g.sort_values("cycle").reset_index(drop=True)
        for end in range(window, len(g) + 1):
            w = g.iloc[end - window:end]
            row = {
                "equipment_id": eid,
                "cycle": int(w["cycle"].iloc[-1]),
                "runtime_hours": round(float(w["runtime_hours"].iloc[-1]), 1),
                # 窗口统计特征（均值/标准差/最大值/趋势斜率）
                "vib_mean": round(float(w["vibration_rms"].mean()), 4),
                "vib_std": round(float(w["vibration_rms"].std(ddof=0)), 4),
                "vib_max": round(float(w["vibration_rms"].max()), 4),
                "temp_mean": round(float(w["temperature"].mean()), 2),
                "temp_std": round(float(w["temperature"].std(ddof=0)), 2),
                "curr_mean": round(float(w["current"].mean()), 3),
            }
            # 健康分 0~100：越接近阈值上限越低
            def health_score(val, lo, hi):
                s = 1.0 - (val - lo) / (hi - lo)
                return round(float(np.clip(s, 0, 1) * 100), 1)

            h_vib = health_score(row["vib_max"], *thr_vib)
            h_temp = health_score(row["temp_mean"], *thr_temp)
            h_curr = health_score(row["curr_mean"], *thr_curr)
            row["health_score"] = round((h_vib + h_temp + h_curr) / 3, 1)
            # 预警等级
            if row["health_score"] >= 70:
                row["alert_level"] = "正常"
            elif row["health_score"] >= 50:
                row["alert_level"] = "关注"
            elif row["health_score"] >= 30:
                row["alert_level"] = "预警"
            else:
                row["alert_level"] = "危险"
            feat_rows.append(row)

    out = pd.DataFrame(feat_rows)
    out_path = os.path.join(PROC_DIR, "equipment_health.csv")
    out.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"[OK] 设备健康预处理: {out_path}  shape={out.shape} (原始 {n_raw} 行时序 -> 窗口特征)")
    return out


if __name__ == "__main__":
    _, scaler_stats = preprocess_quality()
    preprocess_equipment()
    summary = {
        "source": "scripts/generate_raw_data.py 生成的模拟数据",
        "quality_features": {
            "rows": 200,
            "features": NUMERIC_COLS + ["material_removal_rate"],
            "scaler_stats": scaler_stats,
        },
        "equipment_health": {
            "equipment_count": 6,
            "window_size": 10,
            "features": ["vib_mean", "vib_std", "vib_max", "temp_mean", "temp_std", "curr_mean"],
        },
        "steps": [
            "缺失值中位数填充",
            "尺寸误差异常值截断",
            "派生特征 material_removal_rate",
            "材料 one-hot 编码",
            "数值特征 z-score 标准化",
            "传感器时序滑动窗口统计特征",
            "基于阈值的健康分与预警等级",
        ],
    }
    with open(os.path.join(PROC_DIR, "preprocessing_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print("[OK] 预处理摘要已写出")
