#! /usr/bin/env python
#coding=utf-8
from data import *
from document import *
import codecs
import json
from write import write2file
import nn_summary
from MMR import mmr
import re
from pr import pr_summ_exact

# import tensorflow as tf
# from keras.backend.tensorflow_backend import set_session
#
# # set GPU memory
# config = tf.ConfigProto()
# config.gpu_options.per_process_gpu_memory_fraction = 0.1
# set_session(tf.Session(config=config))

# trains = read_data(train_dir)
tests = read_data(test_dir)

# V, i2w = get_vocabrary(trains)  # 没有去停用词和取高频词
# V, i2w = get_vocabulary(trains, 30000)

# with codecs.open(r'../data/vocab3.txt', 'w', 'utf-8') as f:
#     s = json.dumps(str(V))
#     f.write(s)
with codecs.open(r'../data/vocab2.txt', 'r', 'utf-8') as f:
    vocab = dict(eval(json.load(f)))
V = vocab
print(len(V))

golds, texts = get_golds(tests)  # references
#
# results = pr_summary(tests)  # pagerank model
results = pr_summ_exact(tests, 10)

# results = nn_summary.basic(trains, tests, V)  # Single LSTM

# results = nn_summary.center_2(trains, tests, V)  # Joint Model LSTM
# # results = nn_summary.center(trains, tests, V)  # Joint Model LSTM

references = []
summarys = []
i = 0
for r, s in zip(golds, results):
    refer = r.replace(' ', '')
    summ = s.replace(' ', '')
    summ2 = mmr(summ)

    # summ = []  # 取前60个中文字符
    # for word in summ2:
    #     if u'\u4e00' <= word <= u'\u9fff':
    #         summ.append(word)
    #         if len(summ) > 60:
    #             break
    # summ3 = "".join(summ)

    references.append(refer)
    summarys.append(summ2)

    print(i)
    print("references: ", refer)
    print("summ1: ", summ)
    print("summ_mmr: ", summ2)
    # print("Chinese characters: ", "".join(summ2))
    i += 1

write2file(summarys, references)

# i = 0
# d = {}
# for r, t, s, p in zip(golds, texts,  results, position):
#
#     d["reference"] = r.replace(' ', '')
#     d["sentence"] = t.replace(' ', '')
#     d["summarization"] = s.replace(' ', '')
#     d["position"] = p
#     d["index"] = i
#     i += 1
#
#     print(i)
#
#     with codecs.open("../data/train_summ50000.txt", 'a', 'utf-8') as f:
#         s = json.dumps(d, ensure_ascii=False)
#         f.write(s)
#         f.write('\n')