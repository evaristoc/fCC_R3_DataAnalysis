#from chatroom_analysis/cr_analysis.py
import os, sys
import copy, operator, collections, itertools, re
import urllib, urllib.request, urllib.parse
#from urllib.parse import urlparse, urljoin
from urllib import robotparser
import requests
import json, pickle, csv
#from datetime import datetime, date, timedelta
import datetime
import math
from bs4 import BeautifulSoup
import nltk



#https://stackoverflow.com/questions/423379/using-global-variables-in-a-function-other-than-the-one-that-created-them
import config.config
####PARAMETERS
datadirectory = os.getcwd()+'/data'
directory = config.config.directory
nltk.data.path.append(config.config.anacondadir)

usual_stopwords = nltk.corpus.stopwords.words('english')
other_words = ["re", "fm", "tv", "la", "al", "ben", "aq", "ca", "can", "can'", "can't", "cant", "&"]
punctuation = ["\\","/", "|","(",")",".",",",":","=","{","}","==", "===","[","]","+","++","-","--","_","<",">","'","''","``",'"',"!","!=","?",";"]
wtbr = usual_stopwords + other_words + punctuation

subjects = ['getting started', 'responsive web design', 'javascript algorithms data structures', 'front end libraries', 'data visualization', 'apis microservices', 'information security quality assurance', 'contribute open source help nonprofits', 'coding interview questions take home assignments', 'endofthewholelist']




data = pickle.load(open(directory+'db2.pkl','rb'))

dbp = data['platformstable']


#OJO INSERT SOURCE HERE!!!
def links_extraction_phase2(raw, dbp):
    '''
    db is global for this function
    '''    

    
    #net location : [params, query, user, sent]    
    for platform in raw:

        #platformstable
        plt = platform
        platform = platform.replace('.','--')
        
        if platform not in list(dbp.keys()):
            
            
            
            dbp[platform] = {}
            dbp[platform]["origurl"] = plt
            dbp[platform]["category"] = None
            # if classedplatforms[plt] in ['learn|tutorial|course|training|tips|example', 'learn|tutorial|course|training|']:
            #     dbp[platform]["category"] = 'learn|tutorial|course|training| tips|example'
            # elif classedplatforms[plt] in ['(text)?editor|interpreter|repl']:
            #     dbp[platform]["category"] = '(text )?editor|interpreter|repl'
            # else:
            #     dbp[platform]["category"] = classedplatforms[plt].strip(" ")
            dbp[platform]["frequency-recency"] = []
            dbp[platform]["subjects"] = {}
            dbp[platform]["minsecurity"] = None
            dbp[platform]["crawlstatus"] = None
            dbp[platform]["title"] = None
            dbp[platform]["description"] = None
            dbp[platform]["keywords"] = None
            dbp[platform]["htext"] = None
            dbp[platform]["params"] = set()
            dbp[platform]["textids"] = set()
            dbp[platform]["users"] = set()
            dbp[platform]["created"] = ""
            dbp[platform]["modified"] = ""
            dbp[platform]["origin"] = ["paperbot1"]
        dbp[platform]['params'].update(raw[plt]["params"])


def cv():
    '''
    this is a word count!!
    '''

    curriculum = pickle.load(open(directory+'/fcccurriculum.pkl','br'))
    
    cv = {} #cv --> k: (startposition --> int, words_count --> int)
    
    for k,v in sorted(curriculum.items(), key=operator.itemgetter(1)):
        if k not in cv:
            cv[k] = {}
        cv[k]['startposition'] = v[0]
        chswds = set()
        for chs in v[1:]:
            chs = chs.split('/')[-1].split('-')
            for ch in [w for w in chs if w not in wtbr]:
                chswds.update([ch])  
        for chsw in chswds:
            cv[k][chsw] = 0
                
    return cv

def bowcv_test():
    '''
    * bow : for all words, a vocabulary evaluator
    * cvlist : for vocabulary per document
    * cv : assignement of cvlist to corresponding subject title => list of tuples ofthe form (index (position), subject, words, number of words)
    '''
    
    subjects = ['getting started', 'responsive web design', 'javascript algorithms data structures', 'front end libraries', 'data visualization', 'apis microservices', 'information security quality assurance', 'contribute open source help nonprofits', 'coding interview questions take home assignments', 'endofthewholelist']
    subjectscopy = subjects[:-1]
    
    curriculum = pickle.load(open(directory+'/fcccurriculum.pkl','br'))
    bow = []
    cvlist = []
    kk = ' '
    for k,v in sorted(curriculum.items(), key=operator.itemgetter(1)):
        k = ' '.join([w for w in k.split('-') if w not in wtbr])
        if k != subjects[1]:
            kk = kk + k
            #print(kk)
            for chs in v[1:]:
                chs = chs.split('/')[-1].split('-')
                for ch in [w for w in chs if w not in wtbr]:
                    bow.extend([ch])
                    kk = kk + ' ' + ch
        else:
            cvlist.append(kk)
            kk = k
            for chs in v[1:]:
                chs = chs.split('/')[-1].split('-')
                for ch in [w for w in chs if w not in wtbr]:
                    bow.extend([ch])
                    kk = kk + ' ' + ch
            subjects = subjects[1:]
    cvlist.append(kk)
    bow = collections.Counter(bow)
    
    cv = [(i,sub,cont.split(' '),len(cont.split(' '))) for i,(sub,cont) in enumerate(zip(subjectscopy, cvlist))]
    #print(cv[0])
    #print(cv[2])
    return cv , bow


def cvcovering_test(platformdetails, cv, bow):
    '''
    1. once all words are gotten from different sources, verify which of them are in the cv per subject
    2. in the word is a word of the subject (matching query) add the log of the inverse of the length of the subvocabulary of that subject (normalization)
    3. ADDED multiply the total vocabulary normalization by a TF-IDF-ish figure: freq of that word in document against total freq of that word in all documents
    
    So,
    -- ~~all the words of a subvocabulary have the same weight~~ OJO changed to reduce the weight of common words!!
    -- the larger the subvocabulary, the smaller the weight of the word of that subvocabulary
    -- the more specific the word to that subject, the higher the TF-IDF-ish figure; the lesser, the sparsed that figure
    -- the more words related to that subject, the more added
    
    OBS:
    tf-idf rewards frequent words that are non-frequent in a document (count(wdi,alldocs)/count(wdi, docj) * count(allwdsj, docj)); for tf-idf to reward a frequent word in a document, that word should be in an large document
    my proposal (an inverse of the tf-idf) rewards frequent words in a document (count(wdi, docj)/count(wdi, alldocs)) but penalises (normalises) it if the document is large; if the word is not frequent in the document though, it is not relevant
    
    '''
    
    if platformdetails['description'] == None:
        return
    
    pattern01 = re.compile(r'[^a-z0-9]', flags=re.IGNORECASE)
    pattern02 = re.compile(r'\d+', flags=re.IGNORECASE)
    pattern03 = re.compile(r'\w$', flags=re.IGNORECASE)

    kwslistcv = []
    
   
    if platformdetails['description'] != None and platformdetails['description'] != '' and platformdetails['description'] != 'noinformationfound' and platformdetails['description'] != 'errorreachingpage':
        kwslistcv.extend(re.sub(pattern01, ' ', platformdetails['description'].lower()).split(' '))
    if platformdetails['keywords'] != None and platformdetails['keywords'] != '' and platformdetails['keywords'] != 'noinformationfound' and platformdetails['keywords'] != 'errorreachingpage':
        kwslistcv.extend(re.sub(pattern01, ' ', platformdetails['keywords'].lower()).split(' '))
    if platformdetails['title'] != None and platformdetails['title'] != '' and platformdetails['title'] != 'noinformationfound' and platformdetails['title'] != 'errorreachingpage':          
        kwslistcv.extend(re.sub(pattern01, ' ', platformdetails['title'].lower()).split(' '))
    if platformdetails['htext'] != None and platformdetails['htext'] != '' and platformdetails['htext'] != 'noinformationfound' and platformdetails['htext'] != 'errorreachingpage':          
        kwslistcv.extend(re.sub(pattern01, ' ', platformdetails['htext'].lower()).split(' '))
    
    if platformdetails['params']:
        for p in platformdetails['params']:
            allpwds = re.sub(pattern01, ' ', p.lower()).split(' ')
            kwslistcv.extend(allpwds)
    
   
    total_plt_subjects = 0
    #print(cv[0])
    import math
    #it seems that the log function is very must justified, likely relates to models of word distributions - didn't happen to me...
    for p , *sbcnt , doclength in cv:
        wdf = collections.Counter(sbcnt[1])
        for wd in kwslistcv:
            if wd in sbcnt[1]:
                #platformdetails["subjects"][sbcnt[0]]["count"] = platformdetails["subjects"][sbcnt[0]]["count"] + 1/math.log(w) * wdf[wd]/bow[wd]
                #total_plt_subjects += 1/math.log(w) * wdf[wd]/bow[wd]
                # try:
                #     platformdetails["subjects"][sbcnt[0]]["count"] = platformdetails["subjects"][sbcnt[0]]["count"] + 1/(1/math.log(doclength) * wdf[wd]/bow[wd])
                #     total_plt_subjects += 1/(1/math.log(doclength) * wdf[wd]/bow[wd])
                # except:
                #     platformdetails["subjects"][sbcnt[0]]["count"] += 0
                #     total_plt_subjects += 0                    
                platformdetails["subjects"][sbcnt[0]]["count"] = platformdetails["subjects"][sbcnt[0]]["count"] + 1/math.log(doclength)
                total_plt_subjects += 1/math.log(doclength)
    
    if total_plt_subjects == 0:
        total_plt_subjects = 1
    for psb in platformdetails["subjects"].keys():
        platformdetails["subjects"][psb]["proportion"] = platformdetails["subjects"][psb]["count"]/total_plt_subjects
        platformdetails["subjects"][psb]["count"] = platformdetails["subjects"][psb]["count"]


def custom_robotparser(botx):
    '''
    False for not allowed
    '''
    try:
        r = requests.get(botx)
    except:
        return False
    ck = [(a.split(':')[0], a.split(':')[1][1:]) for a in r.content.decode('utf8').split('\n')[:-1] if a.find(':')>-1]
    for pair in ck:
        if pair[0] == 'Disallow':
            if pair[1] == '\\':
                return False
    return True
                
def finding_tags(x):
    try:
        r = requests.get(x)
        print("successful status code? ", r.status_code)
    except:
        print('error reaching the page ', x, '; code status ', r.status_code)
        return ['errorreachingpage']*4
    soup = BeautifulSoup(r.content)
    ks = {'description':'noinformationfound', 'keywords': 'noinformationfound', 'title':'noinformationfound', 'htext':'noinformationfound'}
    t = 0
    try:
        ks['title'] = t = soup.title.get_text()
        allmeta = soup.find_all("meta")
        print("found meta data ", len(allmeta))
        for m1a in allmeta:
        #    print(type(m))
            if m1a.attrs.get('name'):
                if m1a.attrs.get('name') == 'description':
                    ks['description'] = m1a.attrs.get('content')
                    #print(ks['description'])
                    break
        for m1b in allmeta:
        #    print(type(m))
            if m1b.attrs.get('property'):
                if m1b.attrs.get('property') == 'og:description':
                    ks['description'] = m1b.attrs.get('content')
                    #print(ks['description'])
                    break
        for m2 in allmeta:
        #    print(type(m))
            if m2.attrs.get('name'):                
                if m2.attrs.get('name') == 'keywords':
                    ks['keywords'] = m2.attrs.get('content')
                    #print(ks['keywords'])
                    break
        #print('the description for ', x, ' is ', m[0])

        fp = soup.find_all("p")
        if fp:
            if ks['htext'] == 'noinformationfound':
                ks['htext'] = fp[0].text + ' '      
        
        fh1 = soup.find_all("h1")
        if fh1:
            if ks['htext'] == 'noinformationfound':
                ks['htext'] = fh1[0].text + ' '
            else:
                ks['htext'] = ks['htext'] + fh1[0].text + ' '        
        
        fh2 = soup.find_all("h2")
        if fh2:
            if ks['htext'] == 'noinformationfound':
                ks['htext'] = fh2[0].text + ' '
            else:
                ks['htext'] = ks['htext'] + fh2[0].text + ' '  

    except:
        #raise
        print('error when finding some information for ', x)
    finally:
        print(ks['title'],ks['description'],ks['keywords'],ks['htext'])
        return ks['title'],ks['description'],ks['keywords'],ks['htext']
        #return desc_and_kw


    #return desc_and_kw


def botcrawler(platform, URL_BASE_1):
    if urllib.parse.urlparse(URL_BASE_1)[0] == '':
        URL_BASE_2 = 'https://'+URL_BASE_1
    #rp = robotparser.RobotFileParser()
    #print(type(rp))
    else:
        print('robot parser failed for ', URL_BASE_1, '\n')
        dbp[platform]['crawlstatus'] = 'err_crawl'
        return
    try:
        print(urllib.parse.urljoin(URL_BASE_2,'/robots.txt'))
        #rp.set_url(urljoin(URL_BASE_2,'/robots.txt'))
        #rp.read()
        #if rp.can_fetch("*", "/") == True:
        if custom_robotparser(urllib.parse.urljoin(URL_BASE_2,'/robots.txt')) == True:
            print('robot parser successful for ', URL_BASE_2, '\n')
            dbp[platform]['minsecurity'] = 'https://'
            dbp[platform]['title'], dbp[platform]['description'], dbp[platform]['keywords'], dbp[platform]['htext'] = finding_tags(URL_BASE_2)
            dbp[platform]['crawlstatus'] = 'ok_crawl'
        else:
            print('bot data collection not allowed for ', URL_BASE_2, '\n')
            dbp[platform]['crawlstatus'] = 'no_crawl'            
    except:
        #raise
        print('robot parser failed for ', URL_BASE_2, '\n')
        dbp[platform]['crawlstatus'] = 'err_crawl'

    if dbp[platform]['crawlstatus'] == 'err_crawl': ##TEMPORARY LINE!!!
        if urllib.parse.urlparse(URL_BASE_1)[0] == '':
            URL_BASE_2 = 'http://'+URL_BASE_1
        #rp = robotparser.RobotFileParser()
        #print(type(rp))
        try:
            print(urllib.parse.urljoin(URL_BASE_2,'/robots.txt'))
            #rp.set_url(urljoin(URL_BASE_2,'/robots.txt'))
            #rp.read()
            #if rp.can_fetch("*", "/") == True or requests.get(urljoin(URL_BASE_2,'/robots.txt')).status_code == 404:
            if custom_robotparser(urllib.parse.urljoin(URL_BASE_2,'/robots.txt')) == True:
                print('robot parser successful for ', URL_BASE_2, '\n')
                dbp[platform]['minsecurity'] = 'http://'
                dbp[platform]['title'], dbp[platform]['description'], dbp[platform]['keywords'], dbp[platform]['htext'] = finding_tags(URL_BASE_2)
                dbp[platform]['crawlstatus'] = 'ok_crawl'
            else:
                print('crawling not allowed for ', URL_BASE_2, '\n')
                dbp[platform]['crawlstatus'] = 'no_crawl'            
        except:
            #raise
            print('robot parser failed for ', URL_BASE_2, '\n')
            dbp[platform]['crawlstatus'] = 'err_crawl'

def completing_db_with_data_from_botandcv(botdata, dbp):
    '''
    db is global for this function
    ''' 
    #cv_subjects = ["1_respwebdesign", "2_javascriptalgos", "3_frontendlibs", "4_dataviz", "5_apismicro", "6_infosec", "7_opensource", "8_extras"]
    cv_subjects = ['getting started', 'responsive web design', 'javascript algorithms data structures', 'front end libraries', 'data visualization', 'apis microservices', 'information security quality assurance', 'contribute open source help nonprofits', 'coding interview questions take home assignments']
    cv, bow = bowcv_test()

    for platform in list(dbp.keys()):
        plt = dbp[platform]['origurl']
        for s in cv_subjects:
            dbp[platform]["subjects"][s] = {}
            dbp[platform]["subjects"][s]["proportion"] = 0
            dbp[platform]["subjects"][s]["count"] = 0

        if  dbp[platform]["crawlstatus"] == None:
            print("This platform doesn't have any crawl ", platform, plt)
            botcrawler(platform, plt)
            cvcovering_test(dbp[platform], cv, bow)            
        
        elif botdata != None and plt in list(botdata.keys()):
            dbp[platform]["minsecurity"] = botdata[plt]["minsecurity"]
            dbp[platform]["crawlstatus"] = botdata[plt]["crawlstatus"]
            dbp[platform]["title"] = botdata[plt]["title"]
            dbp[platform]["description"] = botdata[plt]["description"]
            dbp[platform]["keywords"] = botdata[plt]["keywords"]
            dbp[platform]["htext"] = botdata[plt]["htext"]
            
          
            cvcovering_test(dbp[platform], cv, bow)

        else:
            print("This platform not in botdata ", platform, plt)
            botcrawler(platform, plt)
            cvcovering_test(dbp[platform], cv, bow)
            
    
   
    #db = {"textstable":db["textstable"], "cv": db["cv"], "categories": db["categories"]}
                        
    #return db



with open(os.getcwd()+'/data/linkspaperbot_listcopiedshortlisted.csv','r') as infile:
    newdata = []
    reader = csv.reader(infile)
    for row in reader:
        newdata.append(row)

newdatadict = {}

for record in newdata:
    try:
        url,params,urlq = urllib.parse.urlsplit(record[2])[1:4]
    except:
        print(url)
        continue
    if not url or url == '':
        continue
    # if url_elimination(url, record[2], params) == True: #true means it is excluded
    #     print(url)
    #     continue
    scheme = urllib.parse.urlparse(record[2]).scheme
    user = record[1]
    text = record[0]
    if url not in list(newdatadict.keys()):
        newdatadict[url] = {}
        newdatadict[url]['params'] = []
        newdatadict[url]['users'] = []
        newdatadict[url]['scheme'] = ''
        newdatadict[url]['text_paperbot'] = []
    newdatadict[url]['params'].append(params)
    newdatadict[url]['users'].append(user)
    newdatadict[url]['text_paperbot'].append(text)
    

# with open(os.getcwd()+'/data/linkspaperbot_listcopiedshortlisted.pkl','bw') as outfile:
#     pickle.dump(datadict, outfile)

todel = []    
for url in newdatadict:
    if url.replace('.', '--') in list(dbp.keys()):
        k = url.replace('.', '--')
        dbp[k]['params'].extend(list(set(newdatadict[url]['params'])))
        dbp[k]['users'].extend(list(set(newdatadict[url]['users'])))
        for t in newdatadict[url]['text_paperbot']:
            if dbp[k]['htext'] != None:
                dbp[k]['htext'] = dbp[k]['htext'] + t + ' '
            else:
                dbp[k]['htext'] = t + ' '
        todel.append(url)

for url in todel:
    del newdatadict[url]
        
links_extraction_phase2(newdatadict, dbp)

completing_db_with_data_from_botandcv({}, dbp)

for k in dbp:
    if dbp[k]["category"] == None:
        if isinstance(dbp[k]['params'], set):
            list(dbp[k]['params']).extend(list(set(newdatadict[dbp[k]['origurl']]['params'])))
        if isinstance(dbp[k]['users'], set):
            list(dbp[k]['users']).extend(list(set(newdatadict[dbp[k]['origurl']]['users'])))
        for t in newdatadict[dbp[k]['origurl']]['text_paperbot']:
            if dbp[k]['htext'] != None:
                dbp[k]['htext'] = dbp[k]['htext'] + t + ' '
            else:
                dbp[k]['htext'] = t + ' '

#  ## a temporary hack!!!
# for k in dbp:
#     list(set(dbp[k]['params']))
#     list(set(dbp[k]['users']))
#     if dbp[k]['htext'] != None:
#         if dbp[k]['origurl'] in list(newdatadict.keys()):
#             for t in newdatadict[dbp[k]['origurl']]['text_paperbot']:
#                 dbp[k]['htext'] = t + ' '

###
#pickle.dump(dbp, open(directory+'dbp2.pkl','wb'))


with open(datadirectory+'/notatedplatformsphase1_a7.csv', 'w') as outfile:
    writer = csv.writer(outfile, delimiter=";", quotechar="'")
    writer.writerow(["platform","title","description","keywords","htext","params","category","wiki"])
    for k in dbp:
        if dbp[k]["category"] == None:
            if isinstance(dbp[k]['params'], set):
                p = ''
                for e in dbp[k]['params']:
                    p = e + ' ' 
            writer.writerow([dbp[k]["origurl"],dbp[k]["title"],dbp[k]["description"],dbp[k]["keywords"],dbp[k]["htext"],p,'',''])
            