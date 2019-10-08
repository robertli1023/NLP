import os, sys
from pyltp import SentenceSplitter, Segmentor, Postagger, Parser, NamedEntityRecognizer, SementicRoleLabeller

LTP_DATA_DIR = r'ltp_data_v3.4.0'  # LTP模型目录路径

cws_model_path = os.path.join(LTP_DATA_DIR, 'cws.model')  # 分词模型路径， 模型名称为'cws.model'

# paragraph = '中国进出口银行与中国银行加强合作。中国进出口银行与中国银行加强合作！'
# 
# sentence = SentenceSplitter.split(paragraph)[0]  # 分句并取第一句

# 分词
segmentor = Segmentor()  # 初始化
segmentor.load(os.path.join(LTP_DATA_DIR, 'cws.model'))  # 加载模型
words = segmentor.segment("熊老师直喊过分")  # 分词
print(list(words))
print('|'.join(words))

# 词性标注
postagger = Postagger()  # 初始化
postagger.load(os.path.join(LTP_DATA_DIR, 'pos.model'))  # 加载模型
postags = postagger.postag(words)
# postags = postagger.postag(['中国', '进出口', '银行', '与', '中国银行', '加强', '合作', '。'])
print(list(postags))

# 依存句法分析
def get_yufa(say_list,postags):
	atts={}
	per_say=[]
	s=list(words)
	res=[]
	res.append("ROOT")
	res.extend(list(words))
	parser = Parser()
	parser.load(os.path.join(LTP_DATA_DIR, 'parser.model'))
	arcs = parser.parse(words, postags)
	dd=[(s[i],res[int(arc.head)],arc.relation) for i,arc in enumerate(arcs)]
	for da in dd:
		if da[-1]=="SBV":
			if da[1] in say_list:
				if da[0] in atts:
					per_say.append(("".join(atts[da[0]])+da[0],da[1]))
		if da[-1]=="ATT":
			if da[1] not in atts:
				atts[da[1]]=[]
			atts[da[1]].append(da[0])		
	return per_say
ss=get_yufa(['说','表示'],postags)
print(ss)
#for s in arcs:
#	print(s)

# 命名实体识别
recognizer = NamedEntityRecognizer()  # 实例化
recognizer.load(os.path.join(LTP_DATA_DIR, 'ner.model'))
netags = recognizer.recognize(words, postags)
print(list(netags))
