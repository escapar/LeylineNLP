import simplejson as json
from gensim.models import Word2Vec
import jieba
import jieba.posseg
import re
import random
model = Word2Vec.load('./shnu/shnu_w2v_alt.bin')

words = []
txt = ''
original = ''
jieba.enable_parallel(4)
ignored = ['ns','nrfg','nrt','b','nr','nt','vn','nz','vd','n','uj','r','x','c','t','m','l','eng']
#ignored = []


def initindexs(char, string):
    index = []
    length = len(string)
    for i in range(length):
        if char == string[i]:
            index.append(i + 1)  # 保存相同字符坐标+1的位置
    return index


def common_sub_exists(str1, str2):
    str1_len = len(str1)
    str2_len = len(str2)
    length = 0
    longest = 0
    startposition = 0
    start = 0
    for i in range(str1_len):
        start = i
        index = initindexs(str1[i], str2)
        index_len = len(index)
        for j in range(index_len):
            end = i + 1
            while end < str1_len and index[j] < str2_len and str1[end] == str2[index[j]]:  # 保证下标不会超出列表范围
                end += 1
                index[j] += 1
            length = end - start
            if length > longest:
                longest = length
                startposition = start

    return longest>0

def inChinese(c):
    zhPattern = re.compile(u"[\u4e00-\u9fa5]+")
    try:
        return zhPattern.search(c) is not None
    except Exception as e:
        return None

with open('./shnu/topic_gen_model.txt',encoding='utf-8',errors='ignore') as f:
    for line in f:
        l = jieba.posseg.cut(line, HMM=False)
        original+=line
        for i in l:
            word = i.word
            if (i.flag in ignored) or len(word)<2 or word is '\n' or word is '\t' :
                txt+=word
                continue
            try:
                suggested = model.most_similar(word)
            except Exception as e:
                print(word + 'is not found')
                suggested = []
                txt+=word


            if(suggested is not None and len(suggested)>0):
                replaced = False
                candidates_best = []
                candidates_secondary = []
                candidate = None
                for (k,v) in suggested:
                    if word not in k \
                            and k not in word \
                            and k not in txt \
                            and len(k)>1 \
                            and inChinese(k): #TBD
                        #if len(word) == 2 and len(k)==2 or len(k)==4 and common_sub_exists(k,word):
                        if len(word) == 2 and len(k)==2 and common_sub_exists(k,word):
                            candidates_best.append(k)
                        elif len(word) == 2:
                            candidates_secondary.append(k)
                        elif len(word) != 2 and common_sub_exists(k,word):
                            candidates_secondary.append(k)
                        elif len(word) != 2 and not common_sub_exists(k,word):
                            candidates_secondary.append(k)
                        else:
                            candidates_best.append(k)



                if len(candidates_best)>0:
                    candidate = candidates_best[0]
                    print(word + i.flag+ ' --> best: ' + candidate)
                elif len(candidates_secondary)>0:
                    candidate = candidates_secondary[0]
                    print(word + i.flag+ ' --> secondary: ' + candidate)

                if candidate is not None:
                    txt+=candidate
                else:
                    count = 0
                    res = ''
                    while True:
                        indice = random.randint(0, len(suggested)-1)
                        tuple = suggested[indice]
                        if (count > 4):
                            res+=word
                            break
                        count += 1
                        if inChinese(tuple[0]):
                            res+=tuple[0]
                            break
                    txt+=res
                    if res != word:
                        print(word + i.flag+ ' --> shuffle: '+res)
            else:
                # not reachable
                txt+=word
                print(word + i.flag + ' --> not found')

print('结果：')
print(txt)
print('原文：')
print(original)
