import logging
from gensim.models import word2vec

def main():
    logging.basicConfig(format="%(asctime)s:%(levelname)s:%(message)s",level=logging.INFO)    
    sentences = word2vec.LineSentence("D:/NLP/assignment-04/AA/wiki_corpus")    
    model = word2vec.Word2Vec(sentences,size=100,min_count=500, workers=4)    #保存模型   
    model.save("wiki_corpus.model")

if __name__ == '__main__':
    main()