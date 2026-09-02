# -*- coding: utf-8 -*-
"""
简历岗位分类模块
================
基于 TF-IDF + 逻辑回归（scikit-learn）实现简历岗位分类。

- 训练数据：data/preprocessed/resumes_train.csv（预处理阶段生成）
- 训练目标：将简历文本映射到 25 个岗位类别之一
- 模型：TfidfVectorizer + LogisticRegression（多分类）
- 说明：本模块为可现场演示的轻量实现；答辩时可说明生产环境可替换为
  BERT 预训练模型（transformers）以获得更强语义理解，但本地演示无需外网模型。

模型缓存：首次训练后序列化到 app/models/cache/ 目录，避免重复训练。
"""

import os
import pickle
import joblib

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TRAIN_PATH = os.path.join(BASE_DIR, "data", "preprocessed", "resumes_train.csv")
TEST_PATH = os.path.join(BASE_DIR, "data", "preprocessed", "resumes_test.csv")
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
os.makedirs(CACHE_DIR, exist_ok=True)

MODEL_PATH = os.path.join(CACHE_DIR, "classifier.pkl")
VEC_PATH = os.path.join(CACHE_DIR, "tfidf.pkl")


class ResumeClassifier:
    """简历岗位分类器（TF-IDF + 逻辑回归）。"""

    def __init__(self):
        self.vectorizer = None
        self.model = None
        self.classes_ = None

    # ------------------------------------------------------------------
    def _load_data(self):
        train = pd.read_csv(TRAIN_PATH)
        test = pd.read_csv(TEST_PATH)
        return train, test

    def train(self, force: bool = False):
        """训练模型；若缓存存在且未强制则直接加载。"""
        if not force and os.path.exists(MODEL_PATH) and os.path.exists(VEC_PATH):
            self._load_model()
            return {"loaded": "cache", "classes": len(self.classes_)}

        train, test = self._load_data()
        X_train, y_train = train["Resume_clean"], train["Category"]
        X_test, y_test = test["Resume_clean"], test["Category"]

        self.vectorizer = TfidfVectorizer(
            max_features=10000, ngram_range=(1, 2), min_df=2
        )
        X_train_vec = self.vectorizer.fit_transform(X_train)
        # 新版 scikit-learn 自动采用 multinomial 多分类，无需显式指定 multi_class
        self.model = LogisticRegression(max_iter=2000, C=1.0)
        self.model.fit(X_train_vec, y_train)
        self.classes_ = self.model.classes_

        # 保存缓存
        with open(MODEL_PATH, "wb") as f:
            pickle.dump(self.model, f)
        with open(VEC_PATH, "wb") as f:
            pickle.dump(self.vectorizer, f)

        # 测试集评估
        X_test_vec = self.vectorizer.transform(X_test)
        y_pred = self.model.predict(X_test_vec)
        acc = accuracy_score(y_test, y_pred)
        return {"loaded": "trained", "classes": len(self.classes_), "test_accuracy": float(acc)}

    def _load_model(self):
        with open(MODEL_PATH, "rb") as f:
            self.model = pickle.load(f)
        with open(VEC_PATH, "rb") as f:
            self.vectorizer = pickle.load(f)
        self.classes_ = self.model.classes_

    def predict(self, text: str) -> dict:
        """预测单个简历文本的岗位类别，返回类别与置信度TopK。"""
        if self.model is None:
            self.train()
        vec = self.vectorizer.transform([text])
        probs = self.model.predict_proba(vec)[0]
        top_idx = np.argsort(probs)[::-1]
        top_k = []
        for i in top_idx[:5]:
            top_k.append({
                "category": str(self.classes_[i]),
                "score": round(float(probs[i]), 4),
            })
        return {
            "predicted_category": str(self.classes_[top_idx[0]]),
            "confidence": round(float(probs[top_idx[0]]), 4),
            "top_k": top_k,
        }

    def evaluate(self) -> dict:
        """在测试集上评估，返回准确率与分类报告。"""
        if self.model is None:
            self.train()
        train, test = self._load_data()
        X_test_vec = self.vectorizer.transform(test["Resume_clean"])
        y_pred = self.model.predict(X_test_vec)
        acc = accuracy_score(test["Category"], y_pred)
        return {
            "accuracy": float(acc),
            "test_samples": int(len(test)),
            "classification_report": classification_report(
                test["Category"], y_pred, zero_division=0
            ),
        }


def get_classifier() -> ResumeClassifier:
    """全局单例分类器。"""
    return ResumeClassifier()
