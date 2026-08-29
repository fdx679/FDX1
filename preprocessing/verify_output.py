# -*- coding: utf-8 -*-
"""验证预处理输出"""
import pandas as pd

print('=== 简历清洗后 ===')
df = pd.read_csv('data/preprocessed/resumes_clean.csv')
print('列:', list(df.columns))
print('行数:', len(df))
for _, r in df.head(3).iterrows():
    print(f"[{r['Category']}] 长度={r['Resume_length']}: {r['Resume_clean'][:120]}...")

print()
print('=== 隐私掩码检查 ===')
email_cnt = df['Resume_clean'].str.contains(r'\[EMAIL\]').sum()
phone_cnt = df['Resume_clean'].str.contains(r'\[PHONE\]').sum()
print(f'含[EMAIL]掩码: {email_cnt} 条, 含[PHONE]掩码: {phone_cnt} 条')

# 检查是否有残留邮箱
import re
remain = df['Resume_clean'].str.contains(r'[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}', regex=True).sum()
print(f'残留邮箱: {remain} 条')

print()
print('=== 训练/测试集 ===')
train = pd.read_csv('data/preprocessed/resumes_train.csv')
test = pd.read_csv('data/preprocessed/resumes_test.csv')
print(f'训练集: {len(train)}, 测试集: {len(test)}')
print('训练集类别数:', train['Category'].nunique(), '| 测试集类别数:', test['Category'].nunique())

print()
print('=== 岗位清洗后 ===')
jobs = pd.read_csv('data/preprocessed/jobs_clean.csv')
print('列:', list(jobs.columns))
print('行数:', len(jobs))
print('来源分布:', jobs['Source'].value_counts().to_dict())
print('类别数:', jobs['Category'].nunique())

print()
print('=== 岗位-技能关系 ===')
rel = pd.read_csv('data/preprocessed/jobs_skill_relation.csv')
print('行数:', len(rel), '| 唯一技能:', rel['Skill'].nunique())
print(rel.head(8).to_string(index=False))
