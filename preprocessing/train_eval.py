# -*- coding: utf-8 -*-
"""训练并评估分类器"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from app.models.classifier import ResumeClassifier

clf = ResumeClassifier()
r = clf.train(force=True)
print("训练结果:", r)
ev = clf.evaluate()
print(f"测试集准确率: {ev['accuracy']*100:.1f}% ({ev['test_samples']} 样本)")
