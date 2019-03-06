#! /usr/bin/env python
#coding=utf-8
import os

LEN_SUMMARY = 30
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_stop_words():
    """加载停用词"""
    stop_words = []
    for line in open(BASE_DIR + '/data/stopword', 'rt', encoding='utf-8'):
        stop_words.append(line.strip())
    return stop_words


def get_vocabrary(documents):
    # DF
    df = {}
    for d in documents:
        for sentence in d.sentences:
            for w in sentence.split():
                if w not in df:
                    df[w] = 0
                df[w] += 1

    V = {}
    for i, w in enumerate(df):
        V[w] = len(V)

    # print("df: ", df)
    # print("V: ", V)
    # print('length of V:', len(V))

    word_index = {V[w]: w for w in V}  # i2w

    return V, word_index


def get_vocabulary(documents, count):
    """
    生成词典，去除停用词，取词频最高的前count个作为词表
    :param documents:
    :param count:
    :return:
    """
    stopwords = load_stop_words()
    df = {}
    for d in documents:
        for sentence in d.sentences:
            for w in sentence.split():
                if w not in stopwords:
                    if w not in df:
                        df[w] = 0
                    df[w] += 1

    words = dict(sorted(df.items(), key=lambda d: d[1], reverse=True)[:count])  # 将词频降序排序，并取前count个作为词表

    V = {}
    for i, w in enumerate(words):
        V[w] = len(V)

    # print("df: ", df)
    # print("V: ", V)
    # print('length of V:', len(V))

    word_index = {V[w]: w for w in V}  # i2w

    return V, word_index


def get_golds(tests):
    references = [d.reference.decode('utf-8', 'ignore') for d in tests]
    texts = []
    for d in tests:
        sentences = d.sentences
        text = []
        for s in sentences:
            text.append(s.decode('utf-8', 'ignore'))
        texts.append("".join(text))
    return references, texts


def formatK(documents, V):
    X = []
    Y = []
    for d in documents:
        x = []
        for w in d.words:
            if w in V:
                x.append(V[w])
        X.append(x)
        Y.append(d.label)
    return X, Y


