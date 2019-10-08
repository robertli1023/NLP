#获取人名说了什么话，返回人名 论点
import jieba.posseg as psg
import jieba,re
from stanfordcorenlp import StanfordCoreNLP
import os, sys
from pyltp import SentenceSplitter, Segmentor, Postagger, Parser, NamedEntityRecognizer, SementicRoleLabeller


def get_say(filename):
    '''获取说的词典'''
    res=[]
    f_r=open(filename,"r",encoding="utf-8")
    for line in f_r:
        line=line.strip("\n")
        lines=line.split(",")
        res.extend([data for data in lines if data])
    return list(set(res))


def raplace_line_feed(sentence):
    return sentence.replace("\u3000"," ")

def more_space_to_one(sentence):
    sen=jieba.lcut(sentence)
    new_data=[]
    for data in sen:
        if new_data:
            if new_data[-1] not in [" ","   "]:
                new_data.append(data)
            elif data not in [" ","   "]:
                new_data.append(data)
        else:
            new_data.append(data)
    return "".join(new_data)


def get_name(netags,words):
    res=[]
    #print(list(netags))
    for i,data in enumerate(list(netags)):
        if data[2:]=="Nh":
            res.append(words[i])
    return list(set(res))


def get_one_name(new_sentence):
    #对于这个句子进行文本处理,获取这个句子中的姓名实体
    name_list=[]
    # new_sentence=raplace_line_feed(new_sentence)
    # new_sentence=more_space_to_one(new_sentence)
    ner_data=psg.lcut(new_sentence)
    i=0
    for w,tag in ner_data:
        if tag=="nr":
            name_list.append(w)
        i += 1
    return list(set(name_list))


def get_dependency_word(sentence):
    '''获取句法分析'''
    # global nlp
    parse_res=[]
    nlp = StanfordCoreNLP(r'D:/stanford/stanford-corenlp-full-2018-10-05', lang='zh')
    word = nlp.word_tokenize(sentence)
    res = nlp.dependency_parse(sentence)
    new_data = []
    new_data.append("ROOT")
    new_data += word
    for i, w in enumerate(res):
        parse_res.append([w[0], new_data[int(w[1])], new_data[int(w[2])]])
    nlp.close()
    return parse_res


def judge_which_say(say_words,sentence):
    '''判断句子中有哪个表示说的词'''
    res_words=[]
    # wordslist=list(set(jieba.lcut(sentence)))
    for word in say_words:
        if word in sentence:
            return True
    return False


def get_say_sentence(sentence,say):
    '''获取包含say的最简短的sentence'''
    senlist=[]
    new_sen=sentence.split(r"\n")
    for sen in new_sen:
        if say in sen:
            senlist.append(sen)
    return senlist

def get_saywords(sentence,say,per):
    #print(say,per)
    if sentence[-1] !="。":
        res1=re.findall(per+"(?:[^，.。）)]*?)"+say+"(?:[^.。]*?)"+"(?:，|:|：|,)([\s\S]*?)$",sentence)
    else:
        res1=re.findall(per+"(?:[^，.。）)]*?)"+say+"(?:[^.。]*?)"+"(?:，|:|：|,)([\s\S]*?)。",sentence)
    res2 = re.findall('(?:“|")([\s\S]*?)(?:”|")(?:,|，)?' + "(?:[^，.。,）]*?)" + per + "(?:[^，.。,）]*?)" + say,sentence)
    #print(res1)
    if res2!=[]:
        return res2[0]
    if res1!=[]:
        return res1[0]
    return ""

def judge_parse(parse_list,say,sentence):
    '''对解析的内容进行判断是不是'''
    says=""
    idex=0
    name=""
    for i,data in enumerate(parse_list):
        if data[0]=="nsubj" and data[1]==say:
            if get_one_name(data[-1])==[data[-1]]:
                # idex=i
                name=data[-1]
        if data[0]=="punct":
            idex=i
        if i>idex and data[0]!="punct" and idex!=0:
            says+=data[-1]
        else:
            says=get_saywords(sentence, say, name)
    return says,name


def get_per_and_say(say_list,postags,words,sentence,parser):
    # words = segmentor.segment(sentence)
    atts={}
    per_say=[]
    s=list(words)
    res=[]
    res.append("ROOT")
    res.extend(list(words))
    arcs = parser.parse(words, postags)
    dd=[(s[i],res[int(arc.head)],arc.relation) for i,arc in enumerate(arcs)]
   # print(dd)
    for da in dd:
        if da[-1]=="SBV":
            if da[1] in say_list:
                if da[0] in atts:
                    poss_per="".join(atts[da[0]])
                    if poss_per+da[0] in sentence:
                        per_say.append((poss_per+da[0],da[1]))
                    else:
                        per_say.append((da[0],da[1]))
                else:
                    per_say.append((da[0],da[1]))
        if da[-1]=="ATT":
            if da[1] not in atts:
                atts[da[1]]=[]
            atts[da[1]].append(da[0])
    #print(per_say)
    return per_say


#一个人说的话一共三种情况，1.最简单的一种就是人名后面紧跟说，说后面紧跟说的话 2.人名后面紧跟说，人名前面用引号引住说的话。3.其他格式
def get_some_idea(say_words,postags,words,senten,parser):
    #根据与表述相关的词的词库，获取每个人说的话
    say_words_list={}
    per_say=get_per_and_say(say_words,postags,words,senten,parser)#say_list,postags,words,sentence,parser
    if per_say!=[]:
        for data in per_say:
            if len(data)==2:
                ls=get_saywords(senten,data[-1],data[0])
                if ls:
                    if data[0] not in say_words_list:
                        say_words_list[data[0]] = []
                    say_words_list[data[0]].append((data[-1], ls))
    return say_words_list


def get_models():
    LTP_DATA_DIR = r'ltp_data_v3.4.0'  # LTP模型目录路径
    # 分词
    segmentor = Segmentor()  # 初始化
    segmentor.load(os.path.join(LTP_DATA_DIR, 'cws.model'))  # 加载模型
    # 词性标注
    postagger = Postagger()  # 初始化
    postagger.load(os.path.join(LTP_DATA_DIR, 'pos.model'))  # 加载模型
    parser = Parser()
    parser.load(os.path.join(LTP_DATA_DIR, 'parser.model'))
    return segmentor,postagger,parser


def get_all_say_sentence(r_filename,w_file):
    segmentor, postagger, parser=get_models()
    say_words = get_say("say.txt")
    f_r=open(r_filename,"r",encoding="utf-8")
    f_w=open(w_file,"w",encoding="utf-8")
    for line in f_r:
        lines=line.strip("\n").split(r"\n")
        for senten in lines:
            have_or_not=judge_which_say(say_words,senten)
            if have_or_not:
                new_sentence = raplace_line_feed(senten)
                new_sentence = more_space_to_one(new_sentence)
                words = segmentor.segment(new_sentence)
                postags = postagger.postag(words)
                sen=get_some_idea(say_words,postags,words,new_sentence,parser)
                if sen:
                    for key in sen:
                        sens="\t".join(list(set([data[1] for data in sen[key]])))
                        f_w.write(key +"\t"+sens +"\n")
    f_r.close()
    f_w.close()


def get_one_say_sentence(line):
    res={}
    segmentor, postagger, parser=get_models()
    say_words = get_say("say.txt")
    lines=line.strip("\n").split(r"\n")
    for senten in lines:
        have_or_not=judge_which_say(say_words,senten)
       # print(have_or_not)
        if have_or_not:
            new_sentence = raplace_line_feed(senten)
            new_sentence = more_space_to_one(new_sentence)
            words = segmentor.segment(new_sentence)
            postags = postagger.postag(words)
            sen=get_some_idea(say_words,postags,words,new_sentence,parser)
            if sen:
                for key in sen:
                    sens="\t".join(list(set([data[1] for data in sen[key]])))
                    if key not in res:
                        res[key]=[]
                    res[key].append(sens)
    return res

if __name__=="__main__":
    t=get_one_say_sentence("刘春玲说,你什么时候要去开会")
    print(t)
