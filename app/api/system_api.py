# -*- coding: utf-8 -*-
"""
系统 API：系统信息、分类器状态、统计
"""

from flask import Blueprint, jsonify

from ..models import get_classifier, get_graph

system_bp = Blueprint("system", __name__)


@system_bp.route("/info", methods=["GET"])
def info():
    """系统概览信息。"""
    graph = get_graph()
    classifier = get_classifier()
    classifier.train()  # 确保模型就绪（有缓存则加载）
    return jsonify({
        "project": "基于深度学习与知识图谱的智能招聘简历筛选系统",
        "job_count": graph.job_count(),
        "skill_count": graph.skill_count(),
        "classifier_classes": len(classifier.classes_) if classifier.classes_ is not None else 0,
        "tech_stack": {
            "backend": "Flask",
            "database": "SQLite",
            "classifier": "TF-IDF + LogisticRegression",
            "knowledge_graph": "networkx",
            "frontend": "HTML/CSS/JS + ECharts",
        },
    })


@system_bp.route("/classifier/evaluate", methods=["GET"])
def evaluate():
    """分类器测试集评估。"""
    classifier = get_classifier()
    result = classifier.evaluate()
    return jsonify({"accuracy": result["accuracy"], "test_samples": result["test_samples"]})
