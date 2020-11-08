import os
import jieba
import csv
import codecs
import collections


if __name__ == '__main__':

    txt = ''
    with codecs.open('./data/fmprc_zyjh.csv', encoding='utf-8') as f:
        for line in f: txt += repr(line)
            
    words  = jieba.lcut(txt)
    word_count= collections.defaultdict(int)
    for w in words:
        word_count[w] += 1
    
    items = list(word_count.items())
    items.sort(key=lambda x: x[1], reverse=True)