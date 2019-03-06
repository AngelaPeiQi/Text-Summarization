#! /usr/bin/env python
#coding=utf-8
from __future__ import division
import math
import os

SIM_RATE = 0.15

train_dir = '../data/train3'
test_dir = '../data/test3'
# test_dir = '../data/train50000'


def cosine(source, target):
    """
    利用余弦相似度公式,cosine(s,t)=(s*t)/(|s|*|t|), 计算两个句子之间的余弦相似度
    :param source: refer words
    :param target: sentence words
    :return:
    """
    numerator = sum([source[word]*target[word] for word in source if word in target])
    sourceLen = math.sqrt(sum([value*value for value in source.values()]))
    targetLen = math.sqrt(sum([value*value for value in target.values()]))
    denominator = sourceLen*targetLen
    if denominator == 0:
        return 0
    else:
        return numerator/denominator


class Document:
    def __init__(self, sentence, label):
        self.text = sentence
        self.words = sentence.split()
        self.label = label


class Article:
    def __init__(self, sentence, position):
        self.text = sentence
        self.position = position


class News:
    def __init__(self, reference, sentences, cens):
        self.reference = reference
        self.sentences = sentences
        self.cens = cens
        self.documents = self.split_pos_neg(reference, sentences)
        
    def split_pos_neg(self, reference, sentences):
        ref_words = dict([(w, 1)for w in self.reference.split()])
        
        results = []
        for i, sentence in enumerate(self.sentences):
            sen_words = dict([(w, 1)for w in sentence.split()])
            results.append((cosine(ref_words, sen_words), i))
        results.sort()
        results.reverse()  # 相似度降序排序
        
        documents = []
        pos_i_set = set([i for score, i in results[:int(len(results)*SIM_RATE)]])  # 创建一个无序不重复元素集，相似度
        
        for i, sentence in enumerate(sentences):
            if i in pos_i_set:
                # pos
                documents.append(Document(sentence, 1))  # 相似度最高的前15%，标记为1
            else:
                # neg
                documents.append(Document(sentence, 0))   # 剩余的部分，标记为0
        
        return documents


def read_data(dir0):
    samples = []
    path_list = os.listdir(dir0)
    path_list.sort()  # 按序读取文件夹下的所有文件
    for fpath in path_list:
        lines = []
        for line in open('%s/%s' % (dir0, fpath), 'rb'):
            line = line.strip()
            lines.append(line)
        reference = lines[0]
        sentences = lines[1:-1]
        cens = [int(i) for i in lines[-1].split()]
        
        # print(len(sentences), len(cens))
        
        if len(sentences) > 1:  # 去除训练集中的未解析文章
            samples.append(News(reference, sentences, cens))
    return samples
