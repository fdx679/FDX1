# -*- coding: utf-8 -*-
"""
候选人匹配度计算与排序模块
==========================
融合多维度特征计算候选人-岗位匹配度：
1. 硬技能覆盖率（岗位所需技能中简历覆盖的比例）—— 知识图谱支撑
   （剔除 communication/leadership 等通用软技能，避免区分度不足）
2. 岗位类别匹配（分类模型置信度 + 预测岗位命中加分）—— 机器学习支撑
3. 工作经验年限匹配 —— 规则

评分公式（0~100）：
    match_score = 100 * ( w1*硬技能覆盖率 + w2*分类置信度 + w3*经验分 + w4*预测命中 )
"""

from .skill_extractor import extract_skills
from .skill_graph import SkillGraph
from .skill_lexicon import SOFT_SKILLS

# 权重配置
W_SKILL = 0.45     # 硬技能覆盖率权重
W_CLASS = 0.25     # 分类置信度权重
W_EXP = 0.15       # 经验权重
W_PRED = 0.15      # 预测岗位命中权重

PRED_HIT_THRESHOLD = 0.05   # 分类置信度阈值：低于此值视为不可靠，不启用命中加分


def _is_hard(skill: str) -> bool:
    """是否为硬技能（排除通用软技能）。"""
    return skill.lower() not in SOFT_SKILLS


def _hard_skills(skills: list) -> list:
    return [s for s in skills if _is_hard(s)]


def _experience_score(resume_exp: int, job_exp_req: int = 3) -> float:
    """经验得分：达到/超过要求得满分，未达到按比例。"""
    if job_exp_req <= 0:
        return 1.0
    return min(1.0, resume_exp / job_exp_req)


def compute_match(
    resume: dict,
    job_category: str,
    graph: SkillGraph,
    classifier_conf: float = 0.0,
    predicted_category: str = None,
) -> dict:
    """
    计算单个候选人对于某岗位的匹配度。
    参数:
        resume: parse_resume 输出的结构化简历
        job_category: 岗位类别
        graph: 知识图谱实例
        classifier_conf: 分类模型对该岗位的置信度（0~1）
        predicted_category: 分类模型预测的岗位类别
    返回:
        匹配详情 dict
    """
    resume_skills = resume.get("skills", [])
    resume_hard = _hard_skills(resume_skills)
    job_skills = graph.get_job_skills(job_category)
    job_hard = [s for s in job_skills if _is_hard(s)]
    missing_skills = graph.get_missing_skills(resume_hard, job_category)

    # 硬技能覆盖率
    matched_hard = set(resume_hard) & set(job_hard)
    raw_coverage = len(matched_hard) / len(job_hard) if job_hard else 0.0
    # 岗位技能规模惩罚：硬技能过少的岗位（如 HR/Sales 仅 0-1 项），
    # 单点命中易造成覆盖率虚高，按比例压缩，保证技术岗位区分度
    scale_factor = min(1.0, len(job_hard) / 4.0)
    skill_coverage = raw_coverage * scale_factor

    exp_score = _experience_score(resume.get("experience_years", 0))

    # 预测岗位命中加分
    pred_hit = 0.0
    if predicted_category and predicted_category == job_category and classifier_conf >= PRED_HIT_THRESHOLD:
        pred_hit = 1.0

    match_score = (
        W_SKILL * skill_coverage
        + W_CLASS * classifier_conf
        + W_EXP * exp_score
        + W_PRED * pred_hit
    ) * 100

    # 等级划分
    if match_score >= 80:
        level = "高匹配"
    elif match_score >= 60:
        level = "中匹配"
    else:
        level = "低匹配"

    return {
        "job_category": job_category,
        "match_score": round(match_score, 2),
        "level": level,
        "skill_coverage": round(skill_coverage * 100, 2),
        "matched_skills": sorted(matched_hard),
        "missing_skills": missing_skills,
        "job_required_skills": job_skills,
        "classifier_confidence": round(classifier_conf, 4),
        "predicted_hit": bool(pred_hit),
        "experience_years": resume.get("experience_years", 0),
    }


def rank_candidates(
    resume: dict,
    classifier_result: dict,
    graph: SkillGraph,
    job_categories: list = None,
) -> list:
    """
    对候选人（简历）与多个岗位计算匹配度并排序。
    """
    cats = job_categories or graph.get_all_jobs()
    results = []
    predicted = classifier_result.get("predicted_category")
    conf_map = {}
    for item in classifier_result.get("top_k", []):
        conf_map[item["category"]] = item["score"]

    for cat in cats:
        conf = conf_map.get(cat, 0.0)
        results.append(compute_match(
            resume, cat, graph,
            classifier_conf=conf, predicted_category=predicted,
        ))

    results.sort(key=lambda x: x["match_score"], reverse=True)
    return results
