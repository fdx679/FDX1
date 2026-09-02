# -*- coding: utf-8 -*-
"""
SQLite 数据库模块
=================
存储简历记录、候选人分析结果、岗位数据，提供历史查询。
生产环境可替换为 MySQL（见方案设计.md），本地演示使用 SQLite 零配置即可运行。
"""

import os
import sqlite3
import json
import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.environ.get("FDX1_TEST_DB", os.path.join(BASE_DIR, "app", "data.db"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS resumes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    phone TEXT,
    education TEXT,
    experience_years INTEGER DEFAULT 0,
    predicted_category TEXT,
    skills TEXT,
    raw_text TEXT,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS candidate_analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    resume_id INTEGER,
    resume_name TEXT,
    predicted_category TEXT,
    match_result TEXT,          -- JSON: 各岗位匹配排序
    created_at TEXT
);
"""


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()


def save_resume(parsed: dict, predicted_category: str, raw_text: str) -> int:
    """保存简历记录，返回 resume_id。"""
    conn = get_connection()
    cur = conn.execute(
        """INSERT INTO resumes
           (name, email, phone, education, experience_years, predicted_category, skills, raw_text, created_at)
           VALUES (?,?,?,?,?,?,?,?,?)""",
        (
            parsed.get("name", ""),
            parsed.get("email", ""),
            parsed.get("phone", ""),
            "、".join(parsed.get("education", [])),
            parsed.get("experience_years", 0),
            predicted_category,
            "、".join(parsed.get("skills", [])),
            raw_text,
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )
    conn.commit()
    rid = cur.lastrowid
    conn.close()
    return rid


def save_analysis(resume_id: int, resume_name: str, predicted_category: str, match_result: list):
    conn = get_connection()
    conn.execute(
        """INSERT INTO candidate_analyses
           (resume_id, resume_name, predicted_category, match_result, created_at)
           VALUES (?,?,?,?,?)""",
        (
            resume_id,
            resume_name,
            predicted_category,
            json.dumps(match_result, ensure_ascii=False),
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )
    conn.commit()
    conn.close()


def list_resumes(limit: int = 20) -> list:
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, name, predicted_category, skills, experience_years, created_at "
        "FROM resumes ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def list_analyses(limit: int = 20) -> list:
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, resume_name, predicted_category, match_result, created_at "
        "FROM candidate_analyses ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        try:
            d["match_result"] = json.loads(d["match_result"])
        except Exception:
            d["match_result"] = []
        result.append(d)
    return result
