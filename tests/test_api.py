# -*- coding: utf-8 -*-
"""API 集成测试（Flask test client）"""

import sys, os, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pytest
from app import create_app


@pytest.fixture()
def client(tmp_path):
    # 使用临时数据库，避免污染正式数据
    os.environ["FDX1_TEST_DB"] = str(tmp_path / "test.db")
    app = create_app({"TESTING": True})
    with app.test_client() as c:
        yield c


SAMPLE = "Name: Li Ming. Python developer with machine learning, SQL, Docker, Git skills, 3 years experience."


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"


def test_index_page(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "智能招聘简历筛选系统" in r.get_data(as_text=True)


def test_parse_resume_api(client):
    r = client.post("/api/resume/parse", json={"text": SAMPLE})
    assert r.status_code == 200
    data = r.get_json()
    assert "parsed" in data
    assert "classification" in data
    assert data["parsed"]["skill_count"] > 0


def test_match_rank_api(client):
    r = client.post("/api/match/rank", json={"text": SAMPLE})
    assert r.status_code == 200
    data = r.get_json()
    assert "ranking" in data
    assert len(data["ranking"]) > 0
    # 排序降序
    scores = [x["match_score"] for x in data["ranking"]]
    assert scores == sorted(scores, reverse=True)


def test_parse_empty_error(client):
    r = client.post("/api/resume/parse", json={"text": "   "})
    assert r.status_code == 400


def test_graph_jobs_api(client):
    r = client.get("/api/graph/jobs")
    assert r.status_code == 200
    assert r.get_json()["job_count"] > 0


def test_graph_echarts_api(client):
    r = client.get("/api/graph/echarts")
    assert r.status_code == 200
    data = r.get_json()
    assert "nodes" in data and "links" in data


def test_history_api(client):
    r = client.get("/api/match/history")
    assert r.status_code == 200
    assert "analyses" in r.get_json()
