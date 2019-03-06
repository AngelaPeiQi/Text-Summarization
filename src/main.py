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


tests = read_data(test_dir)

with codecs.open(r'../data/vocab2.txt', 'r', 'utf-8') as f:
    vocab = dict(eval(json.load(f)))
V = vocab
print(len(V))

golds, texts = get_golds(tests)  

results = pr_summ_exact(tests, 10)

references = []
summarys = []
i = 0
for r, s in zip(golds, results):
    refer = r.replace(' ', '')
    summ = s.replace(' ', '')
    summ2 = mmr(summ)

    references.append(refer)
    summarys.append(summ2)

    print(i)
    print("references: ", refer)
    print("summ1: ", summ)
    print("summ_mmr: ", summ2)
    i += 1

write2file(summarys, references)