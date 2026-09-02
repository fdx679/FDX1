# -*- coding: utf-8 -*-
"""
智能招聘简历筛选系统 - Flask 应用
================================
基于深度学习与知识图谱的智能招聘简历筛选系统（课程设计演示系统）

技术栈：
- 后端：Flask + Flask-CORS
- 算法：TF-IDF+逻辑回归（分类）、规则技能抽取、networkx 知识图谱
- 数据库：SQLite
- 前端：HTML/CSS/JS + ECharts（app/static）
"""

import os

from flask import Flask, send_from_directory
from flask_cors import CORS

from .database import init_db


def create_app(test_config=None):
    app = Flask(__name__, static_folder="static", static_url_path="/static")
    app.config["JSON_AS_ASCII"] = False
    CORS(app)

    if test_config:
        app.config.update(test_config)

    # 初始化数据库
    init_db()

    # 注册蓝图
    from .api.resume_api import resume_bp
    from .api.match_api import match_bp
    from .api.graph_api import graph_bp
    from .api.system_api import system_bp

    app.register_blueprint(resume_bp, url_prefix="/api/resume")
    app.register_blueprint(match_bp, url_prefix="/api/match")
    app.register_blueprint(graph_bp, url_prefix="/api/graph")
    app.register_blueprint(system_bp, url_prefix="/api/system")

    # 首页（前端演示页）
    @app.route("/")
    def index():
        return send_from_directory(app.static_folder, "index.html")

    @app.route("/health")
    def health():
        return {"status": "ok", "service": "resume-screening-system"}

    return app
