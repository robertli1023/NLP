import os, sys
from pyltp import SentenceSplitter, Segmentor, Postagger, Parser, NamedEntityRecognizer, SementicRoleLabeller

def get_name(line):
    LTP_DATA_DIR = r'ltp_data_v3.4.0'  # LTP模型目录路径

    # 分词
    segmentor = Segmentor()  # 初始化
    segmentor.load(os.path.join(LTP_DATA_DIR, 'cws.model'))  # 加载模型
    words = segmentor.segment(line)  # 分词


    # 词性标注
    postagger = Postagger()  # 初始化
    postagger.load(os.path.join(LTP_DATA_DIR, 'pos.model'))  # 加载模型
    postags = postagger.postag(words)
    # postags = postagger.postag(['中国', '进出口', '银行', '与', '中国银行', '加强', '合作', '。'])
    res=[]
    # 命名实体识别
    recognizer = NamedEntityRecognizer()  # 实例化
    recognizer.load(os.path.join(LTP_DATA_DIR, 'ner.model'))
    netags = recognizer.recognize(words, postags)
    for i,data in enumerate(list(netags)):
        if data[2:]=="Nh":
            res.append(words[i])
    return list(set(res))

t=get_name("“我们都用艺名”，来自浙江的茶茶说。")
print(t)
