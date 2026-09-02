# -*- coding: utf-8 -*-
"""
技能抽取模块
============
从简历/岗位文本中抽取技能关键词，支持中英文混合文本。

策略：
1. 英文技能：基于技能词表做词边界匹配
2. 中文技能：jieba 分词 + 技能词表匹配
3. 技能规范化：统一小写返回
"""

import re
from .skill_lexicon import ALL_SKILLS, SKILL_KEYWORDS_EN, SKILL_KEYWORDS_ZH

try:
    import jieba
    _JIEBA_AVAILABLE = True
except ImportError:
    _JIEBA_AVAILABLE = False

# 预编译英文技能正则
_EN_PATTERNS = []
for skill in SKILL_KEYWORDS_EN:
    # 只对纯字母/数字/符号类技能做词边界匹配
    _EN_PATTERNS.append((skill, re.compile(r"(?<![a-z0-9])" + re.escape(skill) + r"(?![a-z0-9])")))


def extract_skills(text: str) -> list:
    """
    从文本中抽取技能列表（去重、有序）。
    参数:
        text: 简历/岗位文本
    返回:
        list[str]: 技能列表
    """
    if not text or not isinstance(text, str):
        return []
    lower = text.lower()
    found = []
    # 英文匹配（词边界）
    for skill, pat in _EN_PATTERNS:
        if pat.search(lower):
            found.append(skill)
    # 中文匹配：jieba 分词 + 词表
    if _JIEBA_AVAILABLE:
        tokens = set(jieba.cut(text))
        for skill in SKILL_KEYWORDS_ZH:
            # 中文技能可能被切分成多个 token，直接在原文中检索更可靠
            if skill in lower:
                found.append(skill)
    else:
        # 无 jieba 时的降级：直接子串匹配中文技能
        for skill in SKILL_KEYWORDS_ZH:
            if skill in lower:
                found.append(skill)

    # 去重并保持顺序
    seen = set()
    result = []
    for s in found:
        if s not in seen:
            seen.add(s)
            result.append(s)
    return result


def count_skill_overlap(resume_skills: list, job_skills: list) -> tuple:
    """
    计算简历技能与岗位技能的覆盖率。
    返回: (交集技能列表, 简历技能数, 岗位技能数, 覆盖率)
    """
    rs = set(resume_skills)
    js = set(job_skills)
    overlap = sorted(rs & js)
    coverage = len(overlap) / len(js) if js else 0.0
    return overlap, len(rs), len(js), coverage
