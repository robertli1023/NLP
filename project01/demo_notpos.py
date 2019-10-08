import os,CRFPP,jieba
#jieba.load_userdict("lcljieba.txt")
def load_model(path):
    if os.path.exists(path):
        return CRFPP.Tagger('-m{0} -v 3 -n 2'.format(path))
    return None

def locationNER(text):
    tagger=load_model('model')
    #tagger=load_model('model2')
#    if "点到" in text:
#        text=text.replace("点到","点 到")
#    if "点至" in text:
#        text=text.replace("点至","点 至")
#    if "点开" in text:
#        text=text.replace("点开","点 开")
#    if "开周会" in text:
#        text=text.replace("开周会","开 周会")
    for c in jieba.lcut(text):
        if len(c)==1:
            tagger.add(c+'\t'+'S')	
        else:
            for i in range(len(c)):
                if i==0:
                    tagger.add(c[i]+'\t'+'B')
                elif i<len(c)-1:
                    tagger.add(c[i]+'\t'+'M')
                else:
                    tagger.add(c[i]+'\t'+'E')
        #tagger.add(c+'\t'+c[0]+'\t'+c[-1])
    result=[]
    r=[]
    tagger.parse()
    word=""
    count=0
    for i in range(0,tagger.size()):
        for j in range(0,tagger.xsize()):
            count+=1
            ch=tagger.x(i,j)
            #print(ch)
            #print(ch)
            tag=tagger.y2(i)
            print("========",tag)
            print(count)
            if count%2==1:
                if "B-" in tag:
                    if word=="":
                        word=ch
                        r.append(tag[2:])
                        #print(ch)
                    else:
                        #print(word)
                        result.append(word)
                        word=""
                elif "M-" in tag:
                    word+=ch
                    #print(word)
                elif "E-" in tag:
                    word+=ch
                elif "O" in tag:
                    if word!="":
                        result.append(word)
                        word=""
                    #word+=ch
                #result.append(word)
                #r.append(tag[2:])
                if "S-" in tag:
                    if word=="":
                        word=ch
                        result.append(word)
                        r.append(tag[2:])
                    else:
                        result.append(word)
    if word!="":
        result.append(word)
    print(result,r)
    return result,r

def test_predict(text):
    result,r=locationNER(text)
    s=""
    for i in range(len(r)): 
        s+=r[i]+":"+result[i]+'\n'
    return s
if __name__=="__main__":
    text='s'
    print("关闭请按enter键"+'\n')
    while text!='':
        text=input("请输入一个句子"+'\n')
        print(text,test_predict(text),sep="==>")
        
    
