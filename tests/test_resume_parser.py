# -*- coding: utf-8 -*-
"""简历解析模块单元测试"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.models.resume_parser import parse_resume, extract_skills


SAMPLE_EN = """
Name: Li Ming
Email: liming@example.com
Phone: +86 138 0000 0000
Education: Bachelor of Computer Science

Skills: Python, Django, Flask, SQL, MySQL, Git, Docker, machine learning
"""

SAMPLE_ZH = """
姓名：王强
电话：13812345678
学历：硕士
技能：Python、机器学习、数据分析、MySQL、TensorFlow
经验：5年工作经验
"""


def test_parse_english_resume():
    r = parse_resume(SAMPLE_EN)
    assert r["name"] != ""
    assert r["email"] == "[EMAIL]"
    assert r["phone"] == "[PHONE]"
    assert "本科" in r["education"]
    assert "python" in [s.lower() for s in r["skills"]]
    assert r["skill_count"] > 0


def test_parse_chinese_resume():
    r = parse_resume(SAMPLE_ZH)
    assert r["name"] == "王强"
    assert r["phone"] == "[PHONE]"
    assert "硕士" in r["education"]
    assert r["experience_years"] >= 5


def test_parse_empty():
    r = parse_resume("")
    assert "error" in r


def test_extract_skills():
    skills = extract_skills("python java sql docker 机器学习 数据分析")
    assert "python" in skills
    assert "java" in skills
    assert "机器学习" in skills


def test_privacy_masked():
    """隐私掩码：解析结果不应泄露真实邮箱/电话。"""
    r = parse_resume(SAMPLE_EN)
    assert r["email"] == "[EMAIL]"
    assert r["phone"] == "[PHONE]"
