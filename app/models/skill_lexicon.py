# -*- coding: utf-8 -*-
"""
共享技能词表模块
================
供技能抽取（预处理与运行时）、岗位匹配、知识图谱构建共用。
包含中英文常见技能关键词，覆盖课程设计涉及的 25 个岗位类别。
"""

# 英文技能词表
SKILL_KEYWORDS_EN = [
    # 编程语言
    "python", "java", "javascript", "typescript", "c++", "c#", "golang", "ruby",
    "php", "scala", "kotlin", "swift", "rust", "matlab", "r language",
    # 数据科学 / 机器学习
    "machine learning", "deep learning", "nlp", "natural language processing",
    "computer vision", "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch",
    "keras", "bert", "data analysis", "statistics", "regression", "classification",
    "clustering", "spark", "hadoop", "hive", "kafka", "airflow", "tableau", "power bi",
    # Web 开发
    "html", "css", "react", "vue", "angular", "node.js", "nodejs", "django",
    "flask", "spring", "spring boot", "rest api", "graphql", "jquery", "bootstrap",
    # 数据库
    "sql", "mysql", "postgresql", "oracle", "mongodb", "redis", "elasticsearch",
    "sql server", "nosql", "database",
    # 运维 / 云
    "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "jenkins",
    "ci/cd", "linux", "git", "terraform", "ansible", "devops", "nginx", "shell",
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
    # 其他
    "communication", "leadership", "teamwork", "problem solving", "english", "chinese",
    # 工程与制造
    "cad", "solidworks", "autocad", "structural analysis", "plc", "circuit design",
    "mechanical engineering", "electrical engineering", "civil engineering",
]

# 中文技能词表
SKILL_KEYWORDS_ZH = [
    # 编程语言
    "python", "java", "javascript", "c++", "c语言", "php", "go语言", "golang",
    "c#", "前端", "后端", "全栈",
    # 数据科学 / 机器学习
    "机器学习", "深度学习", "自然语言处理", "nlp", "计算机视觉", "数据分析",
    "数据挖掘", "神经网络", "tensorflow", "pytorch", "大模型", "算法",
    "大数据", "hadoop", "spark", "flink", "kafka",
    # Web 开发
    "html", "css", "vue", "react", "nodejs", "django", "flask", "spring",
    "小程序", "接口开发", "restful",
    # 数据库
    "数据库", "mysql", "oracle", "sqlserver", "sql", "redis", "mongodb",
    "数据仓库", "etl",
    # 运维 / 云
    "linux", "docker", "kubernetes", "k8s", "云原生", "阿里云", "aws", "运维",
    "jenkins", "git", "自动化部署", "ci/cd",
    # 测试
    "软件测试", "自动化测试", "selenium", "测试用例", "性能测试", "功能测试",
    # 网络与安全
    "网络安全", "渗透测试", "信息安全", "防火墙",
    # 项目管理 / 业务
    "项目管理", "需求分析", "产品经理", "敏捷开发", "scrum",
    # ERP / SAP / 区块链
    "sap", "erp", "区块链", "智能合约", "solidity",
    # 设计与创意
    "photoshop", "ps", "illustrator", "ui设计", "ux设计", "原型设计", "figma",
    # 工程与制造
    "机械设计", "solidworks", "autocad", "cad", "电气设计", "plc", "电路设计",
    "土木工程", "结构设计", "工程造价",
    # 通用
    "沟通能力", "团队协作", "英语", "管理能力", "责任心", "抗压能力",
]

# 全部技能词表（去重、统一小写）
ALL_SKILLS = sorted(set([s.lower() for s in SKILL_KEYWORDS_EN + SKILL_KEYWORDS_ZH]))

# 软技能（通用能力，不具备岗位区分度，匹配计算中不计入硬技能覆盖率）
SOFT_SKILLS = {
    "communication", "leadership", "teamwork", "problem solving", "english",
    "chinese", "responsibility", "抗压能力", "沟通能力", "团队协作",
    "管理能力", "责任心", "agile", "scrum", "project management", "business analysis",
    "requirement analysis", "stakeholder", "pmp", "kanban", "jira",
    "uml", "需求分析", "项目管理", "敏捷开发", "产品经理",
}

# 岗位技能评分权重（用于匹配度计算）
SKILL_WEIGHT_DEFAULT = 1.0
