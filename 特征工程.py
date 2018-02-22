'''
特征工程模块
'''

import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import re
import time
import jieba

#1 提取服务器地址
def extract_email_address(str1):
    it = re.findall('@([A-Za-z0-9]*\.[A-Za-z0-9\.]+)',str(str1))
    result = ''
    if len(it) > 0:
        result = it[0]
    else:
        result = 'unknown'
    return result

## 分析服务器地址
def analysis_email_address(df):
     # 获取服务器类型
    df['to_address'] = pd.Series(map(lambda str:extract_email_address(str),df['to']))
    df['from_address'] = pd.Series(map(lambda str:extract_email_address(str),df['from']))
    #print(df.head(5))
    # 查看相应数量
    print(df.to_address.value_counts())# 每种服务器 对应的邮件数量
    print(df.from_address.value_counts())# 每种发送服务器 对应的邮件数量 
    print(df.to_address.unique().shape)# 接受服务器的类型有几种
    from_address_df = df.from_address.value_counts().to_frame()
    print(from_address_df[from_address_df.from_address <= 10].shape)

# 时间提取  提取 周几 小时 时间段
def extract_email_date(str1):
    if not isinstance (str1, str): #isinstance 判断（实例对象，类型）是否类型相同
        str1 = str(str1)
    
    str_len = len(str1)
    # 0表示上午[8,12]，1表示下午[13,18],2表示晚上[19,23],3表示凌晨[0,7]
    time_quantum = ""

    if str_len <= 10:
        ## unknown
        hour = 'unknown'
        week = 'unknown'
        time_quantum = 'unknown'
        pass
    elif str_len == 16:
        #'2005-9-2 上午10:55' '2005-9-2 上午11:04'
        pattern = '(\d{2}:\d{2})'
        it = re.findall(pattern,str1)
        if len(it) == 1:
            hour = it[0]
        else:
            hour = 'unknown'
        week = 'Fri'
        time_quantum = '0'
        pass
    elif str_len == 19:
        # ['Sep 23 2005 1:04 AM']
        week = 'Sep'
        hour = '01'
        time_quantum = '3'
        pass
    elif str_len == 21:
        # ['August 24 2005 5:00pm']
        week = "Wed"
        hour = "17"
        time_quantum = "1"
        pass
    else:
        rex = r"([A-Za-z]+\d?[A-Za-z]*) .*?(\d{2}):\d{2}:\d{2}.*"
        it = re.findall(rex, str1)
        if len(it) == 1 and len(it[0]) == 2:
            week = it[0][0][-3:]
            hour = it[0][1]
            int_hour = int(hour)
            if int_hour < 8:
                time_quantum = "3"
            elif int_hour < 13:
                time_quantum = "0"
            elif int_hour < 19:
                time_quantum = "1"
            else:
                time_quantum = "2"
            pass
        else:
            week = "unknown"
            hour = "unknown"
            time_quantum = "unknown"

    week = week.lower()
    hour = hour.lower()
    time_quantum = time_quantum.lower()
    return (week, hour, time_quantum)

# 分析时间
def analysis_email_time(df):
    #1 查看时间数据有几种表示形式
    print(np.unique(list(map(lambda x:len(str(x).strip()),df['date'])))) 
    #2 查看每种长度的时间表示形式 ---> 依次分析
    print(np.unique(list(filter(lambda x:len(str(x).strip())==30,df['date']))))
    date_time_extract_result = list(map(lambda st: extract_email_date(st), df['date']))
    df['date_week'] = pd.Series(map(lambda t: t[0], date_time_extract_result))
    df['date_hour'] = pd.Series(map(lambda t: t[1], date_time_extract_result))
    df['date_time_quantum'] = pd.Series(map(lambda t: t[2], date_time_extract_result))
    df.head(4)

    print('=========星期字段属性描述===========')
    print(df.date_week.value_counts())
    print(df[['date_week','label']].groupby(['date_week','label'])['label'].count())

    print('=========hour属性描述===========')
    print(df.date_hour.value_counts())
    print(df[['date_hour','label']].groupby(['date_hour','label'])['label'].count())

    print('=========date_time_quantum属性描述===========')
    print(df.date_time_quantum.value_counts())
    print(df[['date_time_quantum','label']].groupby(['date_time_quantum','label'])['label'].count())

    ### 发现时间为unknown的均为垃圾邮件===》加入has_date属性
    df['has_date'] = df.apply(lambda c: 0 if c['date_week']=='unknown' else 1, axis=1)
    print(df['has_date'].head())
# 文本长度分类
def precess_content_length(lg):
    if lg <= 10:
        return 0
    elif lg <= 100:
        return 1
    elif lg <= 500:
        return 2
    elif lg <= 1000:
        return 3
    elif lg <= 1500:
        return 4
    elif lg <= 2000:
        return 5
    elif lg <= 2500:
        return 6
    elif lg <=  3000:
        return 7
    elif lg <= 4000:
        return 8
    elif lg <= 5000:
        return 9
    elif lg <= 10000:
        return 10
    elif lg <= 20000:
        return 11
    elif lg <= 30000:
        return 12
    elif lg <= 50000:
        return 13
    else:
        return 14
    
# 文本内容进行分析
def analysis_email_content(df):
    ## 分词操作
    df['content'] = df['content'].astype('str')
    df['jieba_cut_content'] = list(map(lambda s:' '.join(jieba.cut(s)),df['content']))
    print(df['jieba_cut_content'].head())
    ## 计算文本长度
    df['content_length'] = pd.Series(map(lambda x:len(x),df['content']))
    df['content_length_type'] = pd.Series(map(lambda x:precess_content_length(x),df['content_length']))
    df2 = df.groupby(['content_length_type','label'])['label'].agg(['count']).reset_index()
    df3 = df2[df2.label==1][['content_length_type','count']].rename(columns = {'count':'c1'})
    df4 = df2[df2.label==0][['content_length_type','count']].rename(columns = {'count':'c2'})
    df5 = pd.merge(df3,df4)
    df5['c1_rate'] = df5.apply(lambda x:x['c1'] / (x['c1']+x['c2']),axis =1)
    df5['c2_rate'] = df5.apply(lambda x:x['c2'] / (x['c1']+x['c2']),axis =1)

    print(df5.head(5))
    # 画图
    plt.plot(df5['content_length_type'], df5['c1_rate'], label=u'垃圾邮件比例')
    plt.plot(df5['content_length_type'], df5['c2_rate'], label=u'正常邮件比例')
    plt.grid(True)
    plt.legend(loc = 0)
    plt.show()

## 特征工程四 ==> 添加信号量
def process_content_sema(x):
    if x > 10000:
        return 0.5 / np.exp(np.log10(x) - np.log10(500)) + np.log(abs(x - 500) + 1) - np.log(abs(x - 10000)) + 1
    else:
        return 0.5 / np.exp(np.log10(x) - np.log10(500)) + np.log(abs(x - 500) + 1) + 1


def main():
    df = pd.read_csv('result_process', sep=',', header= None, names = ['from', 'to', 'date', 'content', 'label'])

    analysis_email_address(df) # datafream可变参数，传递引用, 函数内操作影响原始内容   
    analysis_email_time(df)
 
    analysis_email_content(df)
    df['content_sema'] = list(map(lambda st: process_content_sema(st), df['content_length']))

    # 获取需要的列
    df.drop(['from', 'to', 'date', 'content', 'to_address', 
            'from_address', 'date_week', 'date_hour', 'date_time_quantum', 
            'content_length', 'content_length_type'], 1, inplace=True)
    df.info()

    df.to_csv("result_process02", encoding='utf-8', index=False)
if __name__ == '__main__':
    main()
