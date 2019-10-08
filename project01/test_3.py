#获取人名说了什么话，返回人名 论点
import jieba.posseg as psg
import jieba,re
from stanfordcorenlp import StanfordCoreNLP
import os, sys
from pyltp import SentenceSplitter, Segmentor, Postagger, Parser, NamedEntityRecognizer, SementicRoleLabeller

# global nlp
# nlp= StanfordCoreNLP(r'D:/stanford/stanford-corenlp-full-2018-10-05', lang='zh')

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
    for word in say_words:
        if word in jieba.lcut(sentence):
            res_words.append(word)
    return list(set(res_words))


def get_say_sentence(sentence,say):
    '''获取包含say的最简短的sentence'''
    senlist=[]
    new_sen=sentence.split(r"\n")
    for sen in new_sen:
        if say in sen:
            senlist.append(sen)
    return senlist

def second_say_words(sentence,say,per):
   # per=per.replace("\\","")
   # print("==========="+per)
    res2 = re.findall('(?:“|")([\s\S]*?)(?:”|")(?:,|，)?' + "(?:[^，.。,）]*?)" + per + "(?:[^，.。,）]*?)" + say, sentence)
    res1=re.findall(per+"(?:[^，.。）)]*?)"+say+"(?:[^，.。]*?)"+"(?:，|:|：|,)([\s\S]*?)。",sentence)
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
            says=second_say_words(sentence, say, name)
    return says,name


#一个人说的话一共三种情况，1.最简单的一种就是人名后面紧跟说，说后面紧跟说的话 2.人名后面紧跟说，人名前面用引号引住说的话。3.其他格式
def get_some_idea(sentence,netags,words):
    #根据与表述相关的词的词库，获取每个人说的话
    global say_words
    new_sentence = raplace_line_feed(sentence)
    new_sentence = more_space_to_one(new_sentence)
   # print(new_sentence)
    name_list=get_name(netags,words)
    #print(name_list)
    have_say=judge_which_say(say_words,new_sentence)
    say_words_list={}
    if have_say!=[] and name_list!=[]:
        for say in have_say:
            sen_part=get_say_sentence(new_sentence,say)
            for onesen in sen_part:
                for name in name_list:
                    ls=second_say_words(onesen,say,name)
                    if ls:
                        if name not in say_words_list:
                            say_words_list[name] = []
                        say_words_list[name].append((say, ls))
    else:
        return []
    return say_words_list


def get_all_name(r_filename,w_file):
    # global nlp
    LTP_DATA_DIR = r'ltp_data_v3.4.0'  # LTP模型目录路径
    # 分词
    segmentor = Segmentor()  # 初始化
    segmentor.load(os.path.join(LTP_DATA_DIR, 'cws.model'))  # 加载模型
    # 词性标注
    postagger = Postagger()  # 初始化
    postagger.load(os.path.join(LTP_DATA_DIR, 'pos.model'))  # 加载模型
    # 命名实体识别
    recognizer = NamedEntityRecognizer()  # 实例化
    recognizer.load(os.path.join(LTP_DATA_DIR, 'ner.model'))
    f_r=open(r_filename,"r",encoding="utf-8")
    f_w=open(w_file,"w",encoding="utf-8")
    count=0
    for line in f_r:
        count+=1
        lines=line.strip("\n").replace(r"\n","")
    #    print("----------"+lines)
        words = segmentor.segment(lines)
        postags = postagger.postag(words)
        netags = recognizer.recognize(words, postags)
        sen=get_some_idea(line,netags,words)
        print(sen)
        if sen:
            for key in sen:
                sens="\t".join(list(set([data[1] for data in sen[key]])))
                f_w.write(key +"\t"+sens +"\n")
    # nlp.close()
    f_r.close()
    f_w.close()


if __name__=="__main__":
    # get_all_name("lclnew.txt","name.txt")
    global say_words
    say_words = get_say("say.txt")
    #print(get_dependency_word("刘春玲慷慨激昂的说道,这里没有东西"))
    # res=get_one_name("刘春玲说了什么话")
    get_all_name("lclnew.txt","sentences.txt")
    # print(s)
