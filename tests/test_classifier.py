# -*- coding: utf-8 -*-
"""分类器单元测试（TF-IDF + 逻辑回归）"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.models.classifier import ResumeClassifier


def test_classifier_train_and_predict():
    clf = ResumeClassifier()
    result = clf.train(force=False)
    # 训练完成或从缓存加载
    assert clf.classes_ is not None
    assert len(clf.classes_) > 0

    # 用一条测试样本预测
    pred = clf.predict("Python developer with machine learning and data analysis skills, "
                       "experienced with pandas, numpy, scikit-learn and TensorFlow")
    assert "predicted_category" in pred
    assert pred["confidence"] > 0
    assert len(pred["top_k"]) > 0


def test_classifier_evaluate():
    clf = ResumeClassifier()
    result = clf.evaluate()
    assert result["accuracy"] >= 0.0
    assert result["test_samples"] > 0
    assert 0.0 <= result["accuracy"] <= 1.0
