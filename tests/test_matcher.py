# -*- coding: utf-8 -*-
"""匹配排序模块单元测试"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.models.resume_parser import parse_resume
from app.models.skill_graph import SkillGraph
from app.models.matcher import compute_match, rank_candidates


def test_compute_match():
    graph = SkillGraph()
    resume = parse_resume("Python developer with SQL, Docker, git, machine learning skills, 3 years experience")
    jobs = graph.get_all_jobs()
    assert len(jobs) > 0
    result = compute_match(resume, jobs[0], graph, classifier_conf=0.5)
    assert 0 <= result["match_score"] <= 100
    assert "missing_skills" in result
    assert result["level"] in ("高匹配", "中匹配", "低匹配")


def test_match_score_boundaries():
    graph = SkillGraph()
    # 选硬技能充分的岗位（如 Python Developer），构造技能全覆盖简历 → 应得高分
    jobs = graph.get_all_jobs()
    job = None
    for j in jobs:
        if len(graph.get_job_skills(j)) >= 10:
            job = j
            break
    assert job is not None
    required = graph.get_job_skills(job)
    resume = parse_resume(" ".join(required) + " 5 years experience python sql")
    result = compute_match(resume, job, graph, classifier_conf=1.0, predicted_category=job)
    assert result["match_score"] >= 60


def test_rank_candidates_sorted():
    graph = SkillGraph()
    resume = parse_resume("python machine learning data analysis pandas numpy 3 years experience")
    fake_cls = {
        "predicted_category": "Data Science",
        "top_k": [{"category": "Data Science", "score": 0.8},
                  {"category": "Python Developer", "score": 0.6}],
    }
    ranking = rank_candidates(resume, fake_cls, graph)
    assert len(ranking) > 0
    scores = [r["match_score"] for r in ranking]
    assert scores == sorted(scores, reverse=True)
