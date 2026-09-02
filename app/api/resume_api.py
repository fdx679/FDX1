# -*- coding: utf-8 -*-
"""
简历 API：上传/解析/分类
"""

from flask import Blueprint, request, jsonify

from ..models import parse_resume, get_classifier
from ..database import save_resume

resume_bp = Blueprint("resume", __name__)


@resume_bp.route("/parse", methods=["POST"])
def parse():
    """解析并分类简历。body: {"text": "简历文本"}"""
    data = request.get_json(force=True, silent=True) or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "简历文本为空"}), 400

    # 1. 结构化解析
    parsed = parse_resume(text)
    # 2. 岗位分类
    classifier = get_classifier()
    classification = classifier.predict(text)
    # 3. 入库
    resume_id = save_resume(parsed, classification["predicted_category"], text)

    return jsonify({
        "resume_id": resume_id,
        "parsed": parsed,
        "classification": classification,
    })


@resume_bp.route("/history", methods=["GET"])
def history():
    """查询简历历史记录。"""
    from ..database import list_resumes
    return jsonify({"resumes": list_resumes()})
