# -*- coding: utf-8 -*-
"""
知识图谱 API：岗位技能查询、技能反查、图谱可视化、缺失技能推理
"""

from flask import Blueprint, request, jsonify

from ..models import get_graph

graph_bp = Blueprint("graph", __name__)


@graph_bp.route("/jobs", methods=["GET"])
def jobs():
    """获取全部岗位类别。"""
    graph = get_graph()
    return jsonify({"jobs": graph.get_all_jobs(), "job_count": graph.job_count()})


@graph_bp.route("/job_skills", methods=["GET"])
def job_skills():
    """查询岗位所需技能。参数: job=岗位类别"""
    job = request.args.get("job", "")
    graph = get_graph()
    if job not in graph.get_all_jobs():
        return jsonify({"error": f"岗位类别不存在: {job}"}), 404
    return jsonify({"job": job, "skills": graph.get_job_skills(job)})


@graph_bp.route("/skill_jobs", methods=["GET"])
def skill_jobs():
    """技能反查岗位。参数: skill=技能"""
    skill = request.args.get("skill", "")
    graph = get_graph()
    return jsonify({"skill": skill, "jobs": graph.get_skill_jobs(skill)})


@graph_bp.route("/missing", methods=["POST"])
def missing():
    """推理缺失技能。body: {"job":..., "resume_skills":[...]}"""
    data = request.get_json(force=True, silent=True) or {}
    job = data.get("job", "")
    skills = data.get("resume_skills", [])
    graph = get_graph()
    missing = graph.get_missing_skills(skills, job)
    return jsonify({"job": job, "missing_skills": missing})


@graph_bp.route("/echarts", methods=["GET"])
def echarts():
    """输出 ECharts 关系图数据。参数: jobs=类别1,类别2（可选）"""
    jobs_str = request.args.get("jobs", "")
    jobs = [j.strip() for j in jobs_str.split(",") if j.strip()] or None
    graph = get_graph()
    data = graph.to_echarts(jobs=jobs)
    return jsonify(data)
