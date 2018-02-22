'''
数据清洗模块
'''
import os

# 1 读取索引文件
def read_index_file(file_path):
    type_dict = {'spam':'1', 'ham':'0'} #是否为垃圾邮件类型的词典
    index_file = open(file_path)
    index_dict = {}
    try:
        for line in index_file: # 一行数据
            arr = line.split(' ') # 按空格切分
            if len(arr) == 2: ## 如果不是异常数据
                key, value = arr
            value = value.replace('../data','').replace('\n','') #去除没用字符
            index_dict[value] = type_dict[key.lower()] ## 000/000 : spam
    finally:
        index_file.close()
    return index_dict

# 2 读取邮件内容
def read_file(file_path):
    file = open(file_path,'r',encoding='gb2312',errors='ignore')
    content_dict = {}
    try:
        is_content = False # 是否为文件内容标志位
        for line in file:
            line = line.strip() # 去掉空格
            if line.startswith('From:'): 
                content_dict['from'] = line[5:] 
            elif line.startswith('To:'):
                content_dict['to'] = line[3:]
            elif line.startswith('Date:'):
                content_dict['date'] = line[5:]
            elif not line: # 遇到空行 说明到了文件内容部分
                is_content = True
        
            # 处理邮件内容 应该在行内部进行
            if is_content:
                if 'content' in content_dict:
                    content_dict['content'] += line
                else:
                    content_dict['content'] = line
    finally:
        file.close()
    
    return content_dict

#3 将content_dict 中内容拼接起来
def process_file(file_path):
    content_dict = read_file(file_path)

    result_str = content_dict.get('from','unknown').replace(',','').strip() + ','
    result_str += content_dict.get('to','unknown').replace(',','').strip() + ','
    result_str += content_dict.get('date','unknown').replace(',','').strip() + ','
    result_str += content_dict.get('content','unknown').replace(',',' ').strip()# 去除首尾空格

    return result_str

# 合并第一层文件夹下的所有文件内容,并加上标签
# data_file文件结构  data/000/000-----299
def merge1(index_file_path, data_file_path):
    index_dict = read_index_file(index_file_path) # 获取每个文件的label
    list0 = os.listdir(data_file_path) #获取第一层文件夹下的 文件目录
    for l1 in list0: # 第一层文件夹下的 每个文件夹 以此处理 l1==000
        l1_path = data_file_path + '/'+ l1 # data/000 文件夹
        print('开始处理文件夹:'+ l1_path)

        list1 = os.listdir(l1_path) # 获取data/000 下的文件目录 000----299
        write_file_path = 'process_data/p_' + l1  # 把data/000 文件夹下的所有文件合并到一起

        with open(write_file_path,'w',encoding='utf-8') as writer:
            for l2 in list1: # 000-299
                l2_path = l1_path + '/' + l2 # data/000/000
                index_key = '/' + l1 + '/' + l2 # /data/000/000
                if index_key in index_dict:
                    content_str = process_file(l2_path)
                    content_str += ',' + index_dict[index_key] + '\n'
                    writer.writelines(content_str)

# 将merge合并之后的文件再次合并到一个文件里
def merge2(process_data_path):
    list0 = os.listdir(process_data_path) # 获得当前文件夹下 所有文件名 p_210
    with open('result_process','w',encoding='utf-8') as writer:
        for l1 in list0:
            l1_path = process_data_path + '/' + l1 # 拼接成完整路径 process_data/p_210
            print('开始合并文件:' + l1_path)
            with open(l1_path, encoding='utf-8') as file:
                for line in file: # 一行一行读取数据
                    writer.writelines(line)

def main():
    index_file_path = 'full/index'
    data_file_path = 'data'
    process_data_path = 'process_data'

    merge1(index_file_path,data_file_path)
    merge2(process_data_path)
    # print(result_str)

if __name__ == '__main__':
    main()