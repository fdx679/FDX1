# -*- coding: utf-8 -*-
"""
生成课程设计所需的原始模拟数据。

输出：
  data/raw/process_quality_raw.csv     工艺参数 + 质检结果（质量预测模块用）
  data/raw/sensor_timeseries_raw.csv   设备传感器时序数据（预测性维护模块用）

说明：本数据依据精密切削加工领域常识模拟，非真实企业数据。
缺陷/退化机理设计参考：切深过大、冷却不足、负载过高会显著增加尺寸超差概率；
设备随运行时长振动 RMS、温度、电流呈单调退化趋势（参考 NASA C-MAPSS 退化范式）。
"""
import os
import numpy as np
import pandas as pd

np.random.seed(42)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
os.makedirs(RAW_DIR, exist_ok=True)


def generate_process_quality(n: int = 200) -> pd.DataFrame:
    """生成工艺参数与质检结果数据。"""
    materials = ["45#钢", "铝合金", "不锈钢"]
    rows = []
    for i in range(n):
        material = np.random.choice(materials, p=[0.5, 0.3, 0.2])
        speed = np.random.uniform(900, 2200)          # 主轴转速 rpm
        feed = np.random.uniform(0.10, 0.45)          # 进给量 mm/r
        depth = np.random.uniform(0.5, 3.8)           # 切削深度 mm
        coolant_temp = np.random.uniform(22, 52)      # 切削液温度 ℃
        spindle_load = np.random.uniform(35, 95)      # 主轴负载 %

        # 缺陷概率：由危险工艺参数共同决定
        p_defect = 0.10
        if depth > 2.5:
            p_defect += 0.25
        if coolant_temp > 40:
            p_defect += 0.20
        if spindle_load > 80:
            p_defect += 0.20
        if speed > 2000 or speed < 1000:
            p_defect += 0.10
        if material == "不锈钢":
            p_defect += 0.05
        p_defect = float(np.clip(p_defect, 0.05, 0.9))

        is_defect = int(np.random.rand() < p_defect)

        # 尺寸误差：缺陷件误差更大
        base_err = np.random.normal(0.02, 0.015)
        if is_defect:
            base_err += np.random.uniform(0.04, 0.12)
        dimension_error = round(abs(base_err), 4)

        rows.append({
            "sample_id": f"S{i+1:04d}",
            "material": material,
            "speed_rpm": round(speed, 1),
            "feed_rate": round(feed, 3),
            "depth_of_cut": round(depth, 2),
            "coolant_temp": round(coolant_temp, 1),
            "spindle_load": round(spindle_load, 1),
            "dimension_error": dimension_error,
            "is_defect": is_defect,
        })
    return pd.DataFrame(rows)


def generate_sensor_timeseries(n_equip: int = 6, cycles: int = 120) -> pd.DataFrame:
    """生成设备传感器时序退化数据。"""
    equip_ids = [f"EQ00{i}" for i in range(1, n_equip + 1)]
    # 每台设备的初始状态与退化斜率
    init_vib = np.random.uniform(0.25, 0.35, n_equip)
    init_temp = np.random.uniform(33, 38, n_equip)
    init_curr = np.random.uniform(7.5, 9.0, n_equip)
    slope_vib = np.random.uniform(0.006, 0.010, n_equip)
    slope_temp = np.random.uniform(0.30, 0.45, n_equip)
    slope_curr = np.random.uniform(0.035, 0.060, n_equip)

    rows = []
    for k, eid in enumerate(equip_ids):
        for c in range(1, cycles + 1):
            vib = init_vib[k] + slope_vib[k] * c + np.random.normal(0, 0.01)
            temp = init_temp[k] + slope_temp[k] * c + np.random.normal(0, 0.4)
            curr = init_curr[k] + slope_curr[k] * c + np.random.normal(0, 0.08)
            rows.append({
                "equipment_id": eid,
                "cycle": c,
                "vibration_rms": round(max(vib, 0.1), 4),
                "temperature": round(temp, 2),
                "current": round(max(curr, 1.0), 3),
                "runtime_hours": round(c * 2.5, 1),  # 每 cycle 约 2.5 小时
            })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    df_q = generate_process_quality()
    q_path = os.path.join(RAW_DIR, "process_quality_raw.csv")
    df_q.to_csv(q_path, index=False, encoding="utf-8-sig")
    print(f"[OK] 写出工艺质检数据: {q_path}  shape={df_q.shape}  缺陷率={df_q['is_defect'].mean():.2%}")

    df_s = generate_sensor_timeseries()
    s_path = os.path.join(RAW_DIR, "sensor_timeseries_raw.csv")
    df_s.to_csv(s_path, index=False, encoding="utf-8-sig")
    print(f"[OK] 写出传感器时序数据: {s_path}  shape={df_s.shape}  设备数={df_s['equipment_id'].nunique()}")
