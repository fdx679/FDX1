# -*- coding: utf-8 -*-
"""分类器参数搜索实验"""
import warnings; warnings.filterwarnings('ignore')
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score

train = pd.read_csv('data/preprocessed/resumes_train.csv')
test = pd.read_csv('data/preprocessed/resumes_test.csv')
print(f"训练: {len(train)}, 测试: {len(test)}, 类别: {train['Category'].nunique()}")

configs = [
    ('LR ngram1-2 min2', LogisticRegression(max_iter=2000, C=1.0),
     {'max_features': 10000, 'ngram_range': (1, 2), 'min_df': 2, 'sublinear_tf': False}),
    ('LR ngram1-2 min2 sublinear', LogisticRegression(max_iter=2000, C=1.0),
     {'max_features': 10000, 'ngram_range': (1, 2), 'min_df': 2, 'sublinear_tf': True}),
    ('LR ngram1-3 min2', LogisticRegression(max_iter=2000, C=1.0),
     {'max_features': 10000, 'ngram_range': (1, 3), 'min_df': 2, 'sublinear_tf': False}),
    ('LR ngram1-2 min1', LogisticRegression(max_iter=2000, C=1.0),
     {'max_features': 10000, 'ngram_range': (1, 2), 'min_df': 1, 'sublinear_tf': False}),
    ('NB ngram1-2 min2', MultinomialNB(),
     {'max_features': 10000, 'ngram_range': (1, 2), 'min_df': 2, 'sublinear_tf': False}),
]
best = None
for name, clf, vec_params in configs:
    vec = TfidfVectorizer(**vec_params)
    Xtr = vec.fit_transform(train['Resume_clean'])
    clf.fit(Xtr, train['Category'])
    Xte = vec.transform(test['Resume_clean'])
    acc = accuracy_score(test['Category'], clf.predict(Xte))
    print(f"  {name}: {acc*100:.1f}%")
    if best is None or acc > best[1]:
        best = (name, acc)
print(f"\n最佳: {best[0]} -> {best[1]*100:.1f}%")
