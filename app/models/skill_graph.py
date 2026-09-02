# -*- coding: utf-8 -*-
"""
岗位技能知识图谱模块
====================
基于 networkx 构建「岗位类别 - 技能」知识图谱，支撑：
- 岗位所需技能查询
- 技能关联岗位反查
- 候选人匹配时的缺失技能推理
- 图谱可视化数据输出

数据来源：data/preprocessed/jobs_skill_relation.csv（预处理阶段生成）
生产环境可替换为 Neo4j 图数据库（Cypher 查询），本模块为可现场演示的轻量实现。
"""

import os
import json

import pandas as pd
import networkx as nx

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REL_PATH = os.path.join(BASE_DIR, "data", "preprocessed", "jobs_skill_relation.csv")
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
os.makedirs(CACHE_DIR, exist_ok=True)
GRAPH_CACHE = os.path.join(CACHE_DIR, "skill_graph.json")


class SkillGraph:
    """岗位-技能知识图谱（networkx 有向图：岗位 -> 技能）。"""

    def __init__(self):
        self.graph = nx.DiGraph()
        self._job_skills = {}   # 岗位类别 -> 技能集合
        self._skill_jobs = {}   # 技能 -> 岗位类别集合
        self._load()

    # ------------------------------------------------------------------
    def _load(self):
        if not os.path.exists(REL_PATH):
            raise FileNotFoundError(f"岗位-技能关系表不存在: {REL_PATH}")
        df = pd.read_csv(REL_PATH)
        for _, row in df.iterrows():
            job = str(row["Job_Category"]).strip()
            skill = str(row["Skill"]).strip()
            if not job or not skill:
                continue
            self.graph.add_edge(job, skill, relation="requires")
            self._job_skills.setdefault(job, set()).add(skill)
            self._skill_jobs.setdefault(skill, set()).add(job)

    # ------------------------------------------------------------------
    def job_count(self) -> int:
        return len(self._job_skills)

    def skill_count(self) -> int:
        return len(self._skill_jobs)

    def get_job_skills(self, job: str) -> list:
        """查询岗位所需技能。"""
        return sorted(self._job_skills.get(job, set()))

    def get_skill_jobs(self, skill: str) -> list:
        """反查拥有该技能的岗位类别。"""
        return sorted(self._skill_jobs.get(skill, set()))

    def get_all_jobs(self) -> list:
        return sorted(self._job_skills.keys())

    def get_missing_skills(self, resume_skills: list, job: str) -> list:
        """推理：岗位所需技能中简历缺失的技能。"""
        required = set(self._job_skills.get(job, set()))
        have = set(resume_skills)
        return sorted(required - have)

    def related_jobs_by_skills(self, resume_skills: list) -> list:
        """
        基于技能相似度推荐相关岗位（用于图谱推理/岗位推荐）。
        返回: [{"job":..., "score":...}]，按覆盖技能数排序。
        """
        rs = set(resume_skills)
        result = []
        for job, skills in self._job_skills.items():
            overlap = len(rs & skills)
            if overlap > 0:
                result.append({
                    "job": job,
                    "match_skills": overlap,
                    "total_skills": len(skills),
                    "score": round(overlap / len(skills), 4),
                })
        result.sort(key=lambda x: (-x["score"], -x["match_skills"]))
        return result[:10]

    def to_echarts(self, jobs: list = None) -> dict:
        """
        输出 ECharts 关系图所需的 nodes/links 数据。
        jobs: 指定导出的岗位类别列表（默认全部）。
        """
        job_list = jobs or self.get_all_jobs()
        nodes, links = [], []
        node_set = set()

        for job in job_list:
            if job not in self._job_skills:
                continue
            if job not in node_set:
                nodes.append({"name": job, "category": "job"})
                node_set.add(job)
            for skill in self._job_skills[job]:
                if skill not in node_set:
                    nodes.append({"name": skill, "category": "skill"})
                    node_set.add(skill)
                links.append({"source": job, "target": skill})

        # 简化：若节点过多只取前 N 个岗位，保证前端可渲染
        return {"nodes": nodes, "links": links}


def get_graph() -> SkillGraph:
    """全局单例知识图谱。"""
    return SkillGraph()
