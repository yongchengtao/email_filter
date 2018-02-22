import jieba

jieba.load_userdict('word.txt')
str = '我在北京交通大学上学'
cut1 = jieba.cut(str,HMM=False)
print('/'.join(cut1))