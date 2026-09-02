# -*- coding: utf-8 -*-
"""
系统启动入口
============
运行：python run.py
访问：http://127.0.0.1:5000
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    print("=" * 50)
    print("智能招聘简历筛选系统")
    print("访问地址: http://127.0.0.1:5000")
    print("=" * 50)
    app.run(host="127.0.0.1", port=5000, debug=True)
