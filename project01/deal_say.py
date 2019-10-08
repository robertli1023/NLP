import pandas as pd
import re,time
import jieba
from gensim.models import KeyedVectors
from gensim.models import Word2Vec
from gensim.models.word2vec import LineSentence
from collections import defaultdict
#取“说”的近似20个词，然后对于每一个近似词A再次取20个近似词，
# 如果在子轮次中出现的词C在父轮次C也出现，那么就将A,C作为“说”真正的近似词

def get_related_words(initial_words,model):
    have_seen_solution={}
    unseen = initial_words
    for i,data in enumerate(unseen):
        unseen[i]=(data,1)
    seen = defaultdict(int)
    max_size = 500  # could be greater
    while unseen and len(seen) < max_size:
        if len(seen) % 50 == 0:
            print('seen length : {}'.format(len(seen)))
        node = unseen.pop(0)
        if node[0] not in have_seen_solution:
            have_seen_solution[node[0]]={(w,s) for w, s in model.most_similar(node[0], topn=20)}
        new_expanding =[x for x in have_seen_solution[node[0]]]
        unseen += new_expanding
        seen[node[0]] +=1*node[1]
        # optimal: 1. score function could be revised
        # optimal: 2. using dymanic programming to reduce computing time
    return seen

model=Word2Vec.load("wikiand_all_news_model.model")
related_words = get_related_words(['说', '表示'], model)
res=sorted(related_words.items(), key=lambda x: x[1], reverse=True)
print(res)#[x[0] for x in res]

