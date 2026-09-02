# -*- coding: utf-8 -*-
"""
匹配 API：候选人岗位匹配度计算与排序
"""

from flask import Blueprint, request, jsonify

from ..models import parse_resume, get_classifier, get_graph, rank_candidates
from ..database import save_resume, save_analysis

match_bp = Blueprint("match", __name__)


@match_bp.route("/rank", methods=["POST"])
def rank():
    """对简历文本与岗位库匹配排序。
    body: {"text": "简历文本", "jobs": ["可选，指定岗位类别"]}
    """
    data = request.get_json(force=True, silent=True) or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "简历文本为空"}), 400

    jobs = data.get("jobs") or None

    parsed = parse_resume(text)
    classifier = get_classifier()
    classification = classifier.predict(text)
    graph = get_graph()
    ranking = rank_candidates(parsed, classification, graph, job_categories=jobs)

    # 入库
    resume_id = save_resume(parsed, classification["predicted_category"], text)
    save_analysis(resume_id, parsed["name"], classification["predicted_category"], ranking)

    return jsonify({
        "resume_id": resume_id,
        "parsed": parsed,
        "classification": classification,
        "ranking": ranking,
    })


@match_bp.route("/history", methods=["GET"])
def history():
    """查询匹配历史。"""
    from ..database import list_analyses
    return jsonify({"analyses": list_analyses()})
