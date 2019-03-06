#coding:utf-8
import jieba
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from document import load_stop_words


def cosine(x, y):
    """
    余弦定理计算句子相似度
    :param x:
    :param y:
    :return:
    """
    d = (np.linalg.norm(x) * np.linalg.norm(y))
    return np.dot(x, y) / d if d else 0


def cut_sentence(sentence):
    """
    分词、去停用词并将词组转换成空格间开的形式
    :param sentence: 一个句子
    :return: 一个句子分词、去停用词后的词表
    """
    wordList = []
    stop_words = load_stop_words()
    for word in jieba.cut(sentence):
        if word not in stop_words:  # 去除停用词
            wordList.append(word)
    return ' '.join(wordList)


def sentence2vec(sentences):
    """
    通过idftf转换为词频矩阵
    :param sentences: 若干句子集
    :return: 转化后的句子向量
    """
    sentence = [cut_sentence(s) for s in sentences]
    vectorizer = CountVectorizer()  # 该类会将文本中的词语转换为词频矩阵，矩阵元素a[i][j] 表示j词在i类文本下的词频
    transformer = TfidfTransformer()  # 该类会统计每个词语的tf-idf权值
    tfidf = transformer.fit_transform(vectorizer.fit_transform(sentence))
    # 第一个fit_transform是计算tf-idf，第二个fit_transform是将文本转为词频矩阵
    weight = tfidf.toarray()  # 将tf-idf矩阵抽取出来，元素a[i][j]表示j词在i类文本中的tf-idf权重
    return weight


def transition_probality(sentences):
    """
    计算转移概率
    :param article: article类
    :return: 归一化后的转移概率矩阵
    """
    doc_len = len(sentences)
    sentence_array = sentence2vec(sentences)  # tfidf生成句子向量
    # sentence_array = sentence2vec_by_fasttext(sentences)  # fasttext生成句子向量

    matrix = np.zeros((doc_len, doc_len))
    for i in range(doc_len):
        for j in range(i + 1, doc_len):
            score = cosine(sentence_array[i], sentence_array[j])
            if score < 0:   # fasttext训练向量时，存在负数，把负数的部分用其绝对值表示
                matrix[i, j] = abs(score)
            else:
                matrix[i, j] = score
            matrix[j, i] = matrix[i, j]
    # 归一化
    m = matrix.copy()
    for i in range(doc_len):
        for j in range(doc_len):
            sigma = sum([matrix[i, k] for k in range(doc_len)])
            if sigma:
                m[i, j] /= sigma
    return m


def sentence_score(m):
    """
    计算句子间得分
    :param m: 归一化后的句子转移概率矩阵
    :return: 句子得分列表
    """
    scores = np.full((m.shape[0], 1), 1)
    mu = 0.85
    epsilon = 0.0001
    while True:
        temp = scores.copy()
        scores = mu * np.mat(m).T * scores + (1 - mu) / m.shape[0]
        if max([abs(i) for i in (temp - scores)]) < epsilon:
            break
    return scores


def pr_summ_exact(tests, n):
    """
    pagerank摘要提取
    :param article: article 类
    :param n: 抽取的规模大小，句子个数
    :return: 抽取出来的文本摘要
    """
    summarys = []
    for test in tests:
        sentences = [d.text.decode('utf-8', 'ignore') for d in test.documents if len(d.text) > 10]
        doc_len = len(sentences)
        summary = []
        count = n if n < doc_len else doc_len
        m = transition_probality(sentences)
        scores = [it[0] for it in sentence_score(m).tolist()]
        d = {i: s for i, s in enumerate(scores)}  # 给scores标出序号

        sel_sens = sorted(d.items(), key=lambda x: x[1], reverse=True)[:count]  # 选取排名最大的前几个句子
        sel_sens = sorted(sel_sens.__iter__(), key=lambda x: x[0], reverse=False)  # 按原文中顺序排序

        for item in sel_sens:
            summary.append(sentences[item[0]])

        summarys.append("".join(summary))
    return summarys

