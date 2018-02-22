'''
朴素贝叶斯进行模型预测
'''

import pandas as pd 
import numpy as np 
import matplotlib as mpl
import matplotlib.pyplot as plt

from sklearn.feature_extraction.text import CountVectorizer,TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.naive_bayes import BernoulliNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score,precision_score,recall_score

#1 读取数据
df = pd.read_csv('result_process02',sep=',')
df.dropna(axis = 0, how = 'any', inplace=True)
print(df.info())

#2 分割数据
x = df[['has_date','jieba_cut_content','content_sema']]
y = df['label']
x_train,x_test,y_train,y_test = train_test_split(x, y, test_size=0.2, random_state=0)
print(x_train.shape[0])

#3 模型训练
## 3.1 文本特征转换  svd降维
transformer = TfidfVectorizer(norm='l2',use_idf=True)
svd = TruncatedSVD(n_components=20) # 降维度
jieba_cut_content = list(x_train['jieba_cut_content'].astype('str'))
df1 = transformer.fit_transform(jieba_cut_content)
df2 = svd.fit_transform(df1)
data = pd.DataFrame(df2)
print(data.head())
## 3.2 合并数据
data['has_date'] = list(x_train['has_date'])
data['content_sema'] = list(x_train['content_sema'])
print(data.info())

#4 模型训练
nb = BernoulliNB(alpha=1.0, binarize=0.0005)
model = nb.fit(data,y_train)

#4.1 对测试集进行特征转换
jieba_cut_content_test = list(x_test['jieba_cut_content'].astype('str'))
data_test = pd.DataFrame(list(svd.transform(transformer.transform(jieba_cut_content_test))))
data_test['has_date'] = list(x_test['has_date'])
data_test['content_sema'] = list(x_test['content_sema'])
print(data_test.head(5))
print(data_test.info())

#4.2 模型预测
y_predict = model.predict(data_test)

#5 模型评估
print(f'准确率:{precision_score(y_test,y_predict)}')
print(f'召回率:{recall_score(y_test,y_predict)}')
print(f'f1:{f1_score(y_test,y_predict)}')
