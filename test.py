import pandas as pd
import numpy as np


dict_data = {'content_length_type': np.random.randint(0,6,10), 
             'label': np.random.randint(0,2,10),
             'content':'ss',
              }
#print dict_data
df = pd.DataFrame(dict_data)


df2 = df.groupby(['content_length_type', 'label'])['label'].agg(['count']).reset_index()
# print(df[['content_length_type', 'label']].groupby(['content_length_type', 'label'])['label'].count())

print(df2)
print('*'*30)
df3 = df2[df2.label == 1][['content_length_type', 'count']].rename(columns={'count':'c1'})
df4 = df2[df2.label == 0][['content_length_type', 'count']].rename(columns={'count':'c2'})
df5 = pd.merge(df3, df4) # 默认取 列名相同的列的值并集进行作为新的索引 进行连接
print(df5)
print('='*30)
print(df3)
print(df4)
df5['c1_rage'] = df5.apply(lambda r: r['c1'] / (r['c1'] + r['c2']), axis=1)
df5['c2_rage'] = df5.apply(lambda r: r['c2'] / (r['c1'] + r['c2']), axis=1)
print(df5)