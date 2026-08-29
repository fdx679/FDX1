# -*- coding: utf-8 -*-
"""
岗位描述数据预处理脚本
====================
输入 : data/raw/jobs_indeed_raw.csv（公开数据集 Indeed Job Listings 样本）
输出 : data/preprocessed/ 目录下：
    - jobs_clean.csv              筛选+清洗后的岗位数据（含抽取技能）
    - jobs_skill_relation.csv     岗位-技能关系表（供知识图谱/匹配使用）
    - job_preprocess_report.json  预处理统计报告

预处理内容
----------
1. 岗位筛选：根据简历 25 个岗位类别，用关键词映射从 Indeed 原始数据中
   筛选相关岗位（每类最多保留 N 条，保证各类别覆盖均衡）
2. 文本清洗：去 HTML、URL、多余空白
3. 技能抽取：基于常见技能词表从岗位描述文本中抽取技能关键词
4. 输出岗位-技能关系表，供后续知识图谱构建与候选人匹配使用
"""

import os
import re
import json
import html as html_lib
import pandas as pd

# ---------------------------------------------------------------------------
# 路径配置
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_PATH = os.path.join(BASE_DIR, "data", "raw", "jobs_indeed_raw.csv")
OUT_DIR = os.path.join(BASE_DIR, "data", "preprocessed")
os.makedirs(OUT_DIR, exist_ok=True)

MAX_PER_CATEGORY = 5   # 每个岗位类别最多保留的岗位数
RANDOM_SEED = 42

# ---------------------------------------------------------------------------
# 简历类别 -> 岗位标题关键词映射
# ---------------------------------------------------------------------------
CATEGORY_KEYWORDS = {
    "Data Science": ["data science", "data scientist", "machine learning", "ml engineer", "mlops", "data analyst"],
    "Java Developer": ["java developer", "java engineer", "java software"],
    "Python Developer": ["python developer", "python engineer", "python software"],
    "Database": ["database", "dba", "sql developer", "mysql", "postgresql"],
    "DevOps Engineer": ["devops", "site reliability", "cloud engineer", "sre"],
    "Network Security Engineer": ["security engineer", "cybersecurity", "cyber security", "network security", "information security"],
    "Business Analyst": ["business analyst", "business intelligence"],
    "Web Designing": ["web designer", "frontend", "front-end", "ui/ux", "ux designer", "ui designer", "web developer"],
    "HR": ["human resource", "hr manager", "hr generalist", "talent acquisition", "recruiter"],
    "Sales": ["sales manager", "sales representative", "account executive", "business development"],
    "Operations Manager": ["operations manager", "operations coordinator", "operations"],
    "Mechanical Engineer": ["mechanical engineer", "mechanical design"],
    "Electrical Engineering": ["electrical engineer", "electrical design"],
    "Civil Engineer": ["civil engineer", "structural engineer"],
    "Testing": ["qa engineer", "software tester", "quality assurance", "test engineer"],
    "Automation Testing": ["automation test", "automation engineer", "test automation"],
    "ETL Developer": ["etl", "data engineer", "data pipeline"],
    "Blockchain": ["blockchain", "solidity", "web3"],
    "SAP Developer": ["sap developer", "sap consultant", "sap abap"],
    "Hadoop": ["hadoop", "big data", "spark", "data platform"],
    "DotNet Developer": [".net developer", "dotnet", "c# developer", ".net engineer"],
    "Advocate": ["advocate", "legal counsel", "lawyer", "attorney", "paralegal"],
    "Arts": ["graphic designer", "creative designer", "visual designer", "art director", "illustrator"],
    "Health and fitness": ["fitness trainer", "health coach", "wellness", "physiotherapist", "fitness"],
    "PMO": ["project manager", "program manager", "pmo", "scrum master", "project coordinator"],
}

# ---------------------------------------------------------------------------
# 常见技能词表（用于从岗位描述中抽取技能）
# ---------------------------------------------------------------------------
SKILL_KEYWORDS = [
    # 编程语言
    "python", "java", "javascript", "typescript", "c++", "c#", "c sharp", "golang",
    "ruby", "php", "scala", "kotlin", "swift", "rust", "r language", "matlab", "golang",
    # 数据科学 / 机器学习
    "machine learning", "deep learning", "nlp", "natural language processing", "computer vision",
    "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "keras", "bert",
    "data analysis", "statistics", "regression", "classification", "clustering",
    "spark", "hadoop", "hive", "kafka", "airflow", "tableau", "power bi",
    # Web 开发
    "html", "css", "react", "vue", "angular", "node.js", "nodejs", "django", "flask",
    "spring", "spring boot", "rest api", "graphql", "jquery", "bootstrap",
    # 数据库
    "sql", "mysql", "postgresql", "oracle", "mongodb", "redis", "elasticsearch",
    "sql server", "nosql", "database",
    # 运维 / 云
    "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "jenkins", "ci/cd",
    "linux", "git", "terraform", "ansible", "devops", "nginx", "shell",
    # 测试
    "selenium", "junit", "pytest", "testng", "automation testing", "manual testing",
    "quality assurance", "qa", "test cases",
    # 网络与安全
    "network security", "cybersecurity", "penetration testing", "firewall", "vpn",
    "cisco", "ethical hacking", "siem",
    # 项目管理 / 业务
    "agile", "scrum", "kanban", "project management", "pmp", "business analysis",
    "stakeholder", "requirement analysis", "uml", "jira",
    # ERP / SAP / 区块链
    "sap", "sap abap", "sap fico", "sap sd", "sap mm", "blockchain", "ethereum", "solidity",
    # 设计与创意
    "photoshop", "illustrator", "figma", "sketch", "indesign", "after effects",
    "ui design", "ux design", "wireframe", "prototype",
    # 其他软技能 / 领域
    "communication", "leadership", "teamwork", "problem solving", "english", "chinese",
]

# ---------------------------------------------------------------------------
# 自建补充岗位数据（自建数据集）
# ---------------------------------------------------------------------------
# 说明：Indeed 公开样本中部分技术类岗位样本缺失，为保证知识图谱覆盖简历
#       全部 25 个岗位类别，此处为缺失类别补充自建岗位描述。
#       该部分数据为**自建数据集**（人工整理，非第三方公开数据）。
SELF_BUILT_JOBS = [
    # ---- Python Developer ----
    {
        "Category": "Python Developer",
        "Job_Title": "Python Developer",
        "Company": "TechLabs",
        "Location": "Remote",
        "Job_Type": "Full-time",
        "Description": "We are looking for a Python Developer to build and maintain backend services and APIs. "
                       "Responsibilities include writing reusable Python code, developing REST APIs with Flask or Django, "
                       "working with MySQL and Redis databases, writing unit tests with pytest, and collaborating "
                       "with frontend developers. Required skills: Python, Django, Flask, REST API, MySQL, Redis, "
                       "Git, Linux, pytest. Good communication and problem solving skills required.",
    },
    {
        "Category": "Python Developer",
        "Job_Title": "Senior Python Engineer - Data Platform",
        "Company": "DataWave",
        "Location": "Beijing",
        "Job_Type": "Full-time",
        "Description": "Join our data platform team as a Senior Python Engineer. You will design ETL pipelines, "
                       "build data processing services using Python and pandas, work with Spark and Airflow for "
                       "batch and stream processing, and deploy services with Docker and Kubernetes. Required: "
                       "Python, pandas, numpy, Spark, Airflow, Docker, Kubernetes, SQL, Linux, Git.",
    },
    # ---- Web Designing ----
    {
        "Category": "Web Designing",
        "Job_Title": "Web Designer / UI Designer",
        "Company": "PixelWorks",
        "Location": "Shanghai",
        "Job_Type": "Full-time",
        "Description": "We seek a creative Web Designer to design responsive websites and web applications. "
                       "You will create wireframes and prototypes using Figma, design UI components with Sketch, "
                       "and build front-end pages using HTML, CSS, JavaScript and Vue. Required skills: HTML, CSS, "
                       "JavaScript, Vue, Figma, UI design, UX design, wireframe, prototype, Photoshop.",
    },
    {
        "Category": "Web Designing",
        "Job_Title": "Frontend Web Designer",
        "Company": "CreativeHub",
        "Location": "Shenzhen",
        "Job_Type": "Full-time",
        "Description": "Looking for a frontend-focused web designer to craft landing pages and marketing websites. "
                       "Duties include responsive web design, implementing pages with HTML, CSS, JavaScript and "
                       "React, and optimizing user experience. Required: HTML, CSS, JavaScript, React, Bootstrap, "
                       "UI design, communication skills.",
    },
    # ---- Automation Testing ----
    {
        "Category": "Automation Testing",
        "Job_Title": "Automation Test Engineer",
        "Company": "QualityFirst",
        "Location": "Hangzhou",
        "Job_Type": "Full-time",
        "Description": "We are hiring an Automation Test Engineer to design and maintain automated test frameworks. "
                       "You will write test automation scripts using Selenium and Python pytest, execute regression "
                       "test cases, and integrate CI/CD with Jenkins. Required skills: Selenium, Python, pytest, "
                       "automation testing, quality assurance, Jenkins, Git, Linux.",
    },
    {
        "Category": "Automation Testing",
        "Job_Title": "QA Automation Engineer",
        "Company": "TestPro",
        "Location": "Wuhan",
        "Job_Type": "Full-time",
        "Description": "Responsible for building UI and API automated test suites, managing manual testing and test "
                       "cases, and reporting quality metrics. Required skills: Selenium, Python, Java, TestNG, "
                       "manual testing, test cases, Jira, Agile.",
    },
    # ---- Blockchain ----
    {
        "Category": "Blockchain",
        "Job_Title": "Blockchain Developer",
        "Company": "ChainCore",
        "Location": "Remote",
        "Job_Type": "Full-time",
        "Description": "We need a Blockchain Developer to design and implement smart contracts on Ethereum. "
                       "Responsibilities include writing Solidity smart contracts, integrating Web3 libraries, "
                       "building decentralized applications, and ensuring blockchain security. Required skills: "
                       "Blockchain, Ethereum, Solidity, Web3, JavaScript, Node.js, cryptography, Git.",
    },
    {
        "Category": "Blockchain",
        "Job_Title": "Smart Contract Engineer",
        "Company": "DeFiLabs",
        "Location": "Singapore",
        "Job_Type": "Full-time",
        "Description": "Design, develop and audit smart contracts and DeFi protocols. Strong knowledge of Solidity, "
                       "Ethereum, Web3 and blockchain fundamentals is required. Experience with Go or Rust is a plus. "
                       "Required: Solidity, Ethereum, Blockchain, Web3, Go, Git, security awareness.",
    },
    # ---- SAP Developer ----
    {
        "Category": "SAP Developer",
        "Job_Title": "SAP ABAP Developer",
        "Company": "ERP Solutions",
        "Location": "Chengdu",
        "Job_Type": "Full-time",
        "Description": "Develop and maintain SAP applications using ABAP programming. You will customize SAP modules "
                       "such as SAP SD, SAP MM and SAP FICO, write reports and interfaces, and support system "
                       "upgrades. Required skills: SAP, SAP ABAP, SAP SD, SAP MM, SAP FICO, SQL, database, "
                       "communication skills.",
    },
    {
        "Category": "SAP Developer",
        "Job_Title": "SAP Consultant",
        "Company": "Global ERP",
        "Location": "Guangzhou",
        "Job_Type": "Full-time",
        "Description": "Provide SAP implementation and configuration consulting for enterprise clients. "
                       "Responsibilities include requirement analysis, SAP module configuration (SD/MM/FICO), "
                       "and end-user training. Required: SAP, SAP SD, SAP MM, SAP FICO, business analysis, "
                       "requirement analysis, communication.",
    },
    # ---- Mechanical Engineer ----
    {
        "Category": "Mechanical Engineer",
        "Job_Title": "Mechanical Design Engineer",
        "Company": "AutoTech",
        "Location": "Changchun",
        "Job_Type": "Full-time",
        "Description": "Design mechanical components and assemblies for automotive products using CAD software. "
                       "Perform structural analysis, create engineering drawings, and collaborate with manufacturing. "
                       "Required skills: mechanical engineering, CAD, SolidWorks, AutoCAD, structural analysis, "
                       "MATLAB, teamwork, problem solving.",
    },
    {
        "Category": "Mechanical Engineer",
        "Job_Title": "Mechanical Engineer",
        "Company": "MachineryWorks",
        "Location": "Shenyang",
        "Job_Type": "Full-time",
        "Description": "We seek a Mechanical Engineer for equipment design and process optimization. Duties include "
                       "mechanical design, thermal and stress analysis, and supporting production. Required: "
                       "mechanical engineering, CAD, SolidWorks, MATLAB, problem solving.",
    },
    # ---- Electrical Engineering ----
    {
        "Category": "Electrical Engineering",
        "Job_Title": "Electrical Engineer",
        "Company": "PowerGrid",
        "Location": "Nanjing",
        "Job_Type": "Full-time",
        "Description": "Design and test electrical systems and circuits for industrial applications. Responsibilities "
                       "include electrical design, circuit simulation, PLC programming, and on-site commissioning. "
                       "Required skills: electrical engineering, circuit design, PLC, MATLAB, AutoCAD, problem solving.",
    },
    {
        "Category": "Electrical Engineering",
        "Job_Title": "Electrical Design Engineer",
        "Company": "VoltTech",
        "Location": "Xi'an",
        "Job_Type": "Full-time",
        "Description": "Develop electrical schematics and power distribution systems, run simulation with MATLAB and "
                       "EPLAN, and coordinate with hardware teams. Required: electrical engineering, circuit design, "
                       "MATLAB, AutoCAD, communication.",
    },
    # ---- Civil Engineer ----
    {
        "Category": "Civil Engineer",
        "Job_Title": "Civil Engineer",
        "Company": "BuildCore",
        "Location": "Qingdao",
        "Job_Type": "Full-time",
        "Description": "Plan and oversee construction projects, perform structural and site analysis, and ensure "
                       "compliance with engineering standards. Required skills: civil engineering, structural "
                       "engineering, AutoCAD, project management, problem solving.",
    },
    {
        "Category": "Civil Engineer",
        "Job_Title": "Structural Engineer",
        "Company": "FoundationCo",
        "Location": "Tianjin",
        "Job_Type": "Full-time",
        "Description": "Design structural frameworks for buildings and bridges, run load analysis, and prepare "
                       "engineering reports. Required: civil engineering, structural engineering, AutoCAD, "
                       "MATLAB, teamwork.",
    },
]

URL_RE = re.compile(r"https?://\S+|www\.\S+")
CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def clean_text(text) -> str:
    """清洗岗位描述文本。"""
    if not isinstance(text, str):
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = html_lib.unescape(text)
    text = URL_RE.sub(" ", text)
    text = CONTROL_CHARS_RE.sub(" ", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_skills(text: str) -> list:
    """从文本中抽取技能关键词（基于技能词表匹配）。"""
    lower = text.lower()
    found = []
    for skill in SKILL_KEYWORDS:
        # 用词边界匹配，避免 "r" 这类短词误匹配
        pattern = r"(?<![a-z0-9])" + re.escape(skill) + r"(?![a-z0-9])"
        if re.search(pattern, lower):
            found.append(skill)
    return found


def match_category(title: str):
    """根据岗位标题匹配简历类别，返回 (类别, 匹配关键词) 或 (None, None)。"""
    if not isinstance(title, str):
        return None, None
    t = title.strip().lower()
    for cat, kws in CATEGORY_KEYWORDS.items():
        for kw in kws:
            if kw in t:
                return cat, kw
    return None, None


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("岗位描述数据预处理")
    print("=" * 60)

    df = pd.read_csv(RAW_PATH, encoding="utf-8", on_bad_lines="skip")
    print(f"读取原始岗位: {len(df)} 条")

    # 逐条匹配岗位类别
    matched = []
    for _, row in df.iterrows():
        title = row.get("job_title", "")
        cat, kw = match_category(title)
        if cat is not None:
            matched.append((cat, kw, row))
    print(f"初筛匹配岗位: {len(matched)} 条")

    # 每个类别最多保留 MAX_PER_CATEGORY 条，保证均衡
    import random
    random.seed(RANDOM_SEED)
    per_cat = {}
    random.shuffle(matched)
    for cat, kw, row in matched:
        per_cat.setdefault(cat, []).append((kw, row))
    selected = []
    for cat, items in per_cat.items():
        for kw, row in items[:MAX_PER_CATEGORY]:
            selected.append((cat, kw, row))

    # 构造输出 DataFrame
    records = []
    for cat, kw, row in selected:
        desc = clean_text(row.get("description_text") or row.get("description") or "")
        skills = extract_skills(desc)
        records.append({
            "Category": cat,
            "Job_Title": (row.get("job_title") or "").strip(),
            "Company": (row.get("company_name") or "").strip(),
            "Location": (row.get("location") or "").strip(),
            "Job_Type": (row.get("job_type") or "").strip(),
            "Job_Description_clean": desc,
            "Extracted_Skills": "; ".join(skills),
            "Source": "Indeed公开数据",
            "Source_Url": (row.get("url") or "").strip(),
        })

    # 合并自建岗位数据（覆盖 Indeed 样本中缺失的技术类岗位）
    for j in SELF_BUILT_JOBS:
        desc = clean_text(j["Description"])
        skills = extract_skills(desc)
        records.append({
            "Category": j["Category"],
            "Job_Title": j["Job_Title"],
            "Company": j["Company"],
            "Location": j["Location"],
            "Job_Type": j["Job_Type"],
            "Job_Description_clean": desc,
            "Extracted_Skills": "; ".join(skills),
            "Source": "自建数据集",
            "Source_Url": "",
        })

    out_df = pd.DataFrame(records)
    out_df = out_df.reset_index(drop=True)
    out_df["Job_Description_length"] = out_df["Job_Description_clean"].str.len()

    # 输出岗位-技能关系表（供知识图谱）
    rel_rows = []
    for _, r in out_df.iterrows():
        for skill in (r["Extracted_Skills"].split("; ") if r["Extracted_Skills"] else []):
            rel_rows.append({
                "Job_Category": r["Category"],
                "Job_Title": r["Job_Title"],
                "Skill": skill,
                "Source": r["Source"],
            })
    rel_df = pd.DataFrame(rel_rows)

    # 保存
    out_df.to_csv(os.path.join(OUT_DIR, "jobs_clean.csv"), index=False, encoding="utf-8-sig")
    rel_df.to_csv(os.path.join(OUT_DIR, "jobs_skill_relation.csv"), index=False, encoding="utf-8-sig")

    # 报告
    public_n = int((out_df["Source"] == "Indeed公开数据").sum())
    selfbuilt_n = int((out_df["Source"] == "自建数据集").sum())
    report = {
        "source": "data/raw/jobs_indeed_raw.csv",
        "source_dataset": "Indeed Job Listings (sample) - luminati-io/Indeed-dataset-samples",
        "source_url": "https://github.com/luminati-io/Indeed-dataset-samples",
        "raw_records": int(len(df)),
        "matched_records": len(matched),
        "selected_records": int(len(out_df)),
        "public_records": public_n,
        "self_built_records": selfbuilt_n,
        "self_built_note": "自建数据集：为补齐 Indeed 样本缺失的技术类岗位（Python/Web设计/自动化测试/区块链/SAP/机械/电气/土木工程），人工整理了自建岗位描述。",
        "max_per_category": MAX_PER_CATEGORY,
        "category_distribution": out_df["Category"].value_counts().to_dict(),
        "num_skill_relations": int(len(rel_df)),
        "num_unique_skills": int(rel_df["Skill"].nunique()) if len(rel_df) else 0,
        "preprocessing_steps": [
            "按简历类别关键词筛选岗位(Indeed公开数据)",
            "补充自建岗位数据覆盖缺失技术类岗位(自建数据集)",
            "去HTML/URL/控制字符，规范化空白",
            "基于技能词表抽取岗位技能",
            "生成岗位-技能关系表（供知识图谱）",
        ],
    }
    with open(os.path.join(OUT_DIR, "job_preprocess_report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # 摘要
    print(f"选定岗位     : {len(out_df)} 条（每类最多 {MAX_PER_CATEGORY} 条）")
    print(f"覆盖类别     : {out_df['Category'].nunique()} 类")
    print(f"技能关系     : {len(rel_df)} 条, 唯一技能 {report['num_unique_skills']} 个")
    print("\n类别分布:")
    for c, n in out_df["Category"].value_counts().items():
        print(f"  {c}: {n}")
    print("\n输出文件:")
    for fn in ["jobs_clean.csv", "jobs_skill_relation.csv", "job_preprocess_report.json"]:
        print(f"  - data/preprocessed/{fn}")
    print("\n预处理完成。")


if __name__ == "__main__":
    main()
