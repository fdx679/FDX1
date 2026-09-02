# -*- coding: utf-8 -*-
"""
简历解析模块
============
从简历文本中抽取结构化信息：
- 姓名（通过常见英文姓名模式/中文姓名启发式，不依赖 PII 泄露）
- 邮箱（掩码展示）
- 电话（掩码展示）
- 教育背景（学历关键词）
- 工作经历（年限关键词）
- 技能（调用 skill_extractor）
- 岗位意向（常见岗位关键词）

说明：本模块在预处理阶段已对原始简历做隐私掩码，运行时解析仅做结构化提取，
邮箱/电话一律以掩码形式输出，不泄露真实个人信息。
"""

import re

from .skill_extractor import extract_skills

# 邮箱正则（识别但用于掩码显示）
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(?<!\d)(\+?\d{1,3}[\s\-\.]?)?(\(?\d{3,4}\)?[\s\-\.]?)?\d{3,4}[\s\-\.]?\d{4}(?!\d)")
URL_RE = re.compile(r"https?://\S+|www\.\S+")

# 学历关键词
EDUCATION_KEYWORDS = {
    "博士": "博士", "phd": "博士", "doctorate": "博士",
    "硕士": "硕士", "master": "硕士", "m.sc": "硕士", "m.s.": "硕士",
    "本科": "本科", "bachelor": "本科", "b.tech": "本科", "b.e": "本科", "b.s.": "本科", "b.sc": "本科",
    "大专": "大专", "associate": "大专", "diploma": "大专",
    "高中": "高中", "high school": "高中",
}

# 岗位类别关键词（用于岗位意向识别）
JOB_ROLE_KEYWORDS = [
    ("data scientist", "数据科学家"), ("data science", "数据科学"), ("data analyst", "数据分析师"),
    ("java developer", "Java开发"), ("java", "Java开发"),
    ("python developer", "Python开发"), ("python", "Python开发"),
    ("devops", "DevOps"), ("site reliability", "SRE"),
    ("security engineer", "安全工程师"), ("network security", "网络安全"), ("cyber", "网络安全"),
    ("business analyst", "业务分析师"), ("business intelligence", "商业智能"),
    ("web developer", "Web开发"), ("frontend", "前端开发"), ("front-end", "前端开发"), ("web design", "Web设计"),
    ("hr", "人力资源"), ("human resource", "人力资源"), ("recruit", "招聘"),
    ("sales", "销售"), ("operations manager", "运营经理"), ("operations", "运营"),
    ("mechanical", "机械"), ("electrical", "电气"), ("civil engineer", "土木工程"),
    ("test engineer", "测试工程师"), ("qa", "测试"), ("automation", "自动化测试"),
    ("data engineer", "数据工程师"), ("etl", "ETL"),
    ("blockchain", "区块链"), ("sap", "SAP"), ("hadoop", "Hadoop"), ("big data", "大数据"),
    (".net", ".NET"), ("dotnet", ".NET"),
    ("graphic design", "平面设计"), ("designer", "设计师"),
    ("project manager", "项目经理"), ("scrum master", "ScrumMaster"), ("pmo", "PMO"),
]


def mask_email(text: str) -> str:
    return EMAIL_RE.sub("[EMAIL]", text)


def extract_email(text: str) -> str:
    m = EMAIL_RE.search(text)
    return "[EMAIL]" if m else ""


def extract_phone(text: str) -> str:
    m = PHONE_RE.search(text)
    return "[PHONE]" if m else ""


def extract_education(text: str) -> list:
    """提取学历信息（去重）。"""
    lower = text.lower()
    found = []
    for kw, label in EDUCATION_KEYWORDS.items():
        if kw in lower and label not in found:
            found.append(label)
    return found


def extract_work_experience_years(text: str) -> int:
    """从文本中估算工作年限。"""
    patterns = [
        (r"(\d{1,2})\s*(?:\+|more)?\s*years?\s+(?:of\s+)?(?:experience|work)", "年"),
        (r"(\d{1,2})\s*年(?:以上)?(?:工作)?经验", "年"),
        (r"(?:experience|work experience)[:\s]*(\d{1,2})\s*(?:\+|more)?\s*years?", "年"),
        (r"(\d{1,2})\s*\+?\s*yrs?", "年"),
    ]
    years = []
    for pat, _ in patterns:
        years += [int(m) for m in re.findall(pat, text.lower())]
    return max(years) if years else 0


def extract_job_intent(text: str) -> list:
    """识别简历中的岗位意向。"""
    lower = text.lower()
    found = []
    for kw, label in JOB_ROLE_KEYWORDS:
        if kw in lower and label not in found:
            found.append(label)
    return found[:5]


def extract_name(text: str) -> str:
    """
    姓名提取（启发式）：
    - 英文简历：常见"NAME: xxx"或首行包含大写单词
    - 中文简历：常见"姓名：xxx"
    """
    # 中文"姓名"标签
    m = re.search(r"(?:姓名|name)\s*[：:]\s*([\u4e00-\u9fa5]{2,4})", text, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    # 英文 NAME 标签（大小写不敏感；只匹配连续字母单词，遇标点停止）
    m = re.search(r"\bname\s*[：:]\s*([A-Za-z]+(?:[ '-][A-Za-z]+)*)", text, re.IGNORECASE)
    if m:
        name = m.group(1).strip()
        return name
    return ""


def parse_resume(text: str) -> dict:
    """
    解析简历文本，返回结构化结果。
    """
    if not text:
        return {"error": "空文本"}
    text = URL_RE.sub(" ", text)
    skills = extract_skills(text)
    return {
        "name": extract_name(text) or "未识别",
        "email": extract_email(text),
        "phone": extract_phone(text),
        "education": extract_education(text),
        "experience_years": extract_work_experience_years(text),
        "job_intent": extract_job_intent(text),
        "skills": skills,
        "skill_count": len(skills),
        "text_length": len(text),
    }
