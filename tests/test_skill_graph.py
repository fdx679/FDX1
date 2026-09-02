# -*- coding: utf-8 -*-
"""知识图谱模块单元测试（networkx）"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.models.skill_graph import SkillGraph


def test_graph_load():
    graph = SkillGraph()
    assert graph.job_count() > 0
    assert graph.skill_count() > 0


def test_job_skills():
    graph = SkillGraph()
    jobs = graph.get_all_jobs()
    assert len(jobs) > 0
    # 至少存在一个岗位有技能
    any_skills = any(len(graph.get_job_skills(j)) > 0 for j in jobs)
    assert any_skills


def test_missing_skills():
    graph = SkillGraph()
    jobs = graph.get_all_jobs()
    job = jobs[0]
    required = set(graph.get_job_skills(job))
    missing = graph.get_missing_skills([], job)
    assert set(missing) == required  # 无技能时全部缺失


def test_related_jobs():
    graph = SkillGraph()
    result = graph.related_jobs_by_skills(["python", "sql", "docker"])
    # 返回列表按分数降序
    scores = [r["score"] for r in result]
    assert scores == sorted(scores, reverse=True)


def test_echarts_data():
    graph = SkillGraph()
    data = graph.to_echarts(jobs=graph.get_all_jobs()[:3])
    assert "nodes" in data and "links" in data
    assert len(data["nodes"]) > 0
