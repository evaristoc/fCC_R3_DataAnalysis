#!/usr/bin/env python3
# #from chatroom_analysis/cr_analysis.py
# import os, sys
# import copy, operator, collections, itertools, re
# import urllib, urllib.request, urllib.parse
# #from urllib.parse import urlparse, urljoin
# from urllib import robotparser
# import requests
# import json, pickle, csv
# #from datetime import datetime, date, timedelta
# import datetime
# import math
# from bs4 import BeautifulSoup
# import nltk
# #nltk.data.path.append(config.anacondadir+'nltk_data') #a required hack in my case
# 
# 
# usual_stopwords = nltk.corpus.stopwords.words('english')
# other_words = ["re", "fm", "tv", "la", "al", "ben", "aq", "ca", "can", "can'", "can't", "cant", "&"]
# punctuation = ["\\","/", "|","(",")",".",",",":","=","{","}","==", "===","[","]","+","++","-","--","_","<",">","'","''","``",'"',"!","!=","?",";"]
# wtbr = usual_stopwords + other_words + punctuation

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
    kk = ''
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
    
    if platformdetails['description'] != None or platformdetails['description'] != '' or platformdetails['description'] != 'noinformationfound' or platformdetails['description'] != 'errorreachingpage':
        kwslistcv.extend(re.sub(pattern01, ' ', platformdetails['description'].lower()).split(' '))
    if platformdetails['keywords'] != None or platformdetails['keywords'] != '' or platformdetails['keywords'] != 'noinformationfound' or platformdetails['keywords'] != 'errorreachingpage':
        kwslistcv.extend(re.sub(pattern01, ' ', platformdetails['keywords'].lower()).split(' '))
    if platformdetails['title'] != None or platformdetails['title'] != '' or platformdetails['title'] != 'noinformationfound' or platformdetails['title'] != 'errorreachingpage':          
        kwslistcv.extend(re.sub(pattern01, ' ', platformdetails['title'].lower()).split(' '))
    if platformdetails['htext'] != None or platformdetails['htext'] != '' or platformdetails['htext'] != 'noinformationfound' or platformdetails['htext'] != 'errorreachingpage':          
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



def links_extraction_phase1(raw, source):
    '''
    db is global for this function
    '''    
    classedplatforms = dict([(obj['platform'], obj['newclass']) for obj in csv.DictReader(open(directory+'labeledplatformsphase1.csv'))])
    
    print(len(classedplatforms))
    #print(list(classedplatforms.keys()))
    
    # if 'azmind.com' in list(classedplatforms.keys()):
    #     print('azmind.com is in classedplatforms')
    
    classedplatforms['medium.freecodecamp.com'] = 'blog|media|news|articl|content|post|journal'
    classedplatforms['forum.freecodecamp.com'] = 'community|support|people|forum'    
    
    #net location : [params, query, user, sent]    
    for elem in raw:
        if elem["fromUser"]["username"] == "camperbot":
            continue

        for u in elem["urls"]:
            url = u['url']
            try:
                platform,params,urlq = urllib.parse.urlsplit(url)[1:4]
            except:
                print(url)
                continue

            #assert platform != 'azmind.com', (platform, source)
            
            if platform in list(classedplatforms.keys()):
                if platform == 'forum.freecodecamp.com' and params in ["/fcc-relaxing-cat", "/t/free-code-camp-official-chat-rooms/19390", "/t/free-code-camp-official-chat-rooms", "/t/free-code-camp-brownie-points/18380", "/t/markdown-code-formatting/18391"]:
                    continue

                #platformstable
                plt = platform
                platform = platform.replace('.','--')
                
                if platform not in list(db['platformstable'].keys()):
                    db["platformstable"][platform] = {}
                    db["platformstable"][platform]["origurl"] = plt
                    if classedplatforms[plt] in ['learn|tutorial|course|training|tips|example', 'learn|tutorial|course|training|']:
                        db["platformstable"][platform]["category"] = 'learn|tutorial|course|training| tips|example'
                    elif classedplatforms[plt] in ['(text)?editor|interpreter|repl']:
                        db["platformstable"][platform]["category"] = '(text )?editor|interpreter|repl'
                    else:
                        db["platformstable"][platform]["category"] = classedplatforms[plt].strip(" ")
                    db["platformstable"][platform]["frequency-recency"] = []
                    db["platformstable"][platform]["subjects"] = {}
                    db["platformstable"][platform]["minsecurity"] = None
                    db["platformstable"][platform]["crawlstatus"] = None
                    db["platformstable"][platform]["title"] = None
                    db["platformstable"][platform]["description"] = None
                    db["platformstable"][platform]["keywords"] = None
                    db["platformstable"][platform]["htext"] = None
                    db["platformstable"][platform]["params"] = set()
                    db["platformstable"][platform]["textids"] = set()
                    db["platformstable"][platform]["users"] = set()
                    db["platformstable"][platform]["created"] = ""
                    db["platformstable"][platform]["modified"] = ""
                db['platformstable'][platform]['params'].update([params])
                db["platformstable"][platform]["textids"].update([elem["id"]])
                #calculation of frequency-recency (formerly wrongly named "prevalence")
                date = elem['sent'].split('-')
                year = int(date[0])
                month = int(date[1])
                day = int(date[2].split('T')[0])
                current = datetime.datetime(year, month, day)
                if year == 2016:
                    db["platformstable"][platform]['frequency-recency'].append(month - 6)
                elif year == 2017:
                    db["platformstable"][platform]['frequency-recency'].append(month + 7)

                #textstable
                if elem["id"] not in db["textstable"].keys():
                    db["textstable"][elem["id"]] = {}
                    db["textstable"][elem["id"]]["text"] = elem["text"]
                    db["textstable"][elem["id"]]["source"] = source
                    db["textstable"][elem["id"]]["user"] = elem["fromUser"]["username"]
                    db["textstable"][elem["id"]]["sent"] = elem["sent"]
                    db["textstable"][elem["id"]]["prestige"] = 1
                    db["textstable"][elem["id"]]["urls"] = elem["urls"]
                    db["textstable"][elem["id"]]["platforms"] = set()
                    db["textstable"][elem["id"]]["created"] = ""
                    db["textstable"][elem["id"]]["modified"] = ""
                db["textstable"][elem["id"]]["platforms"].update((platform, "sentiment"))

                #userstable
                if elem['fromUser']['username'] not in list(db['userstable'].keys()):
                    db['userstable'][elem['fromUser']['username']] = set()
                db['userstable'][elem['fromUser']['username']].update([platform])  
    #return db

def custom_robotparser(botx):
    r = requests.get(botx)
    if r.status_code == 404:
        True
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
    try:
        print(urllib.parse.urljoin(URL_BASE_2,'/robots.txt'))
        #rp.set_url(urljoin(URL_BASE_2,'/robots.txt'))
        #rp.read()
        #if rp.can_fetch("*", "/") == True:
        if custom_robotparser(urllib.parse.urljoin(URL_BASE_2,'/robots.txt')) == True:
            print('robot parser successful for ', URL_BASE_2, '\n')
            db['platformstable'][platform]['minsecurity'] = 'https://'
            db['platformstable'][platform]['title'], db['platformstable'][platform]['description'], db['platformstable'][platform]['keywords'], db['platformstable'][platform]['htext'] = finding_tags(URL_BASE_2)
            db['platformstable'][platform]['crawlstatus'] = 'ok_crawl'
        else:
            print('bot data collection not allowed for ', URL_BASE_2, '\n')
            db['platformstable'][platform]['crawlstatus'] = 'no_crawl'            
    except:
        print('robot parser failed for ', URL_BASE_2, '\n')
        db['platformstable'][platform]['crawlstatus'] = 'err_crawl'

    if db['platformstable'][platform]['crawlstatus'] == 'err_crawl': ##TEMPORARY LINE!!!
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
                db['platformstable'][platform]['minsecurity'] = 'http://'
                db['platformstable'][platform]['title'], db['platformstable'][platform]['description'], db['platformstable'][platform]['keywords'], db['platformstable'][platform]['htext'] = finding_tags(URL_BASE_2)
                db['platformstable'][platform]['crawlstatus'] = 'ok_crawl'
            else:
                print('crawling not allowed for ', URL_BASE_2, '\n')
                db['platformstable'][platform]['crawlstatus'] = 'no_crawl'            
        except:
            raise
            print('robot parser failed for ', URL_BASE_2, '\n')
            db['platformstable'][platform]['crawlstatus'] = 'err_crawl'



def completing_db_with_data_from_botandcv(botdata):
    '''
    db is global for this function
    ''' 
    #cv_subjects = ["1_respwebdesign", "2_javascriptalgos", "3_frontendlibs", "4_dataviz", "5_apismicro", "6_infosec", "7_opensource", "8_extras"]
    cv_subjects = ['getting started', 'responsive web design', 'javascript algorithms data structures', 'front end libraries', 'data visualization', 'apis microservices', 'information security quality assurance', 'contribute open source help nonprofits', 'coding interview questions take home assignments']
    cv, bow = bowcv_test()

    for platform in list(db['platformstable'].keys()):
        plt = db['platformstable'][platform]['origurl']
        for s in cv_subjects:
            db["platformstable"][platform]["subjects"][s] = {}
            db["platformstable"][platform]["subjects"][s]["proportion"] = 0
            db["platformstable"][platform]["subjects"][s]["count"] = 0

        if plt in list(botdata.keys()):
            db["platformstable"][platform]["minsecurity"] = botdata[plt]["minsecurity"]
            db["platformstable"][platform]["crawlstatus"] = botdata[plt]["crawlstatus"]
            db["platformstable"][platform]["title"] = botdata[plt]["title"]
            db["platformstable"][platform]["description"] = botdata[plt]["description"]
            db["platformstable"][platform]["keywords"] = botdata[plt]["keywords"]
            db["platformstable"][platform]["htext"] = botdata[plt]["htext"]
            
          
            cvcovering_test(db["platformstable"][platform], cv, bow)

        else:
            print("This platform not in botdata ", platform, plt)
            #botcrawler(platform, plt)
            #cvcovering_test(db["platformstable"][platform], cv, bow)
            
    
   
    #db = {"textstable":db["textstable"], "cv": db["cv"], "categories": db["categories"]}
                        
    #return db


def calculating_total_subjectandcategories():
    '''
    db is global for this function
    ''' 

    cv, _ = bowcv_test()
    
    db["fcc_subjects"] = cv

    categoryset = set()
    print(db["platformstable"].keys())
    for plf in db["platformstable"].keys():
        categoryset.update([db["platformstable"][plf]["category"]])
    
    db["plt_categories"] = list(categoryset)


def etl_formattingsetstolists():
    '''
    db is global for this function
    ''' 
    for plt in db['platformstable']:
        for k in db['platformstable'][plt]:
            if type(db['platformstable'][plt][k]) == set:
                db['platformstable'][plt][k] = list(db['platformstable'][plt][k])

    for txt in db['textstable']:
        for k in db['textstable'][txt]:
            if type(db['textstable'][txt][k]) == set:
                db['textstable'][txt][k] = list(db['textstable'][txt][k])
        
    for usr in db['userstable']:
        if type(db['userstable'][usr]) == set:
            db['userstable'][usr] = list(db['userstable'][usr])


def pyrebase_conn_test():
    '''
        --- https://firebase.google.com/docs/database/admin/retrieve-data
        --- https://firebase.google.com/docs/auth/web/github-auth
        
        Also:
        --- https://stackoverflow.com/questions/39061866/python-firebase-401-unauthorised-error
        --- https://stackoverflow.com/questions/37922251/firebase-keeps-throwing-oauth2-client-id-in-server-configuration-is-not-found
        --- https://github.com/firebase/functions-samples/tree/master/github-to-slack
        --- https://github.com/firebase/firebase-simple-login
        --- https://ozgur.github.io/python-firebase/
        --- https://www.youtube.com/watch?v=io_r-0e3Qcw
        --- https://blog.devcolor.org/heating-up-with-firebase-tutorial-on-how-to-integrate-firebase-into-your-app-6ce97440175d
    '''
    #import firebase_admin
    import pyrebase

    dbconfig = config.dbconfig

    

    firebase = pyrebase.initialize_app(dbconfig)


    # Get a reference to the database service
    db = firebase.database()

    
    def datacheck(db,*args):
        child1 = args[0]
        cont = []
        if db.child(child1).get().val():
            #print(db.child(child1).get().val())
            print(db.child(child1).get().val().keys())
            for k in db.child(child1).get().val().keys():
                print(k)
                cont.append(k)
        return cont

    return datacheck(db,"platformstable"), datacheck(db, "textstable")



def pyrebase_conn(data):
    '''

        Also:
        --- https://stackoverflow.com/questions/39061866/python-firebase-401-unauthorised-error
        --- https://stackoverflow.com/questions/37922251/firebase-keeps-throwing-oauth2-client-id-in-server-configuration-is-not-found
        --- https://github.com/firebase/functions-samples/tree/master/github-to-slack
        --- https://github.com/firebase/firebase-simple-login
        --- https://ozgur.github.io/python-firebase/
        --- https://firebase.google.com/docs/auth/web/github-auth
        --- https://www.youtube.com/watch?v=io_r-0e3Qcw
        --- https://blog.devcolor.org/heating-up-with-firebase-tutorial-on-how-to-integrate-firebase-into-your-app-6ce97440175d
        --- https://stackoverflow.com/questions/40613907/how-can-i-pull-nested-json-values-from-python-using-dictionaries
    '''
    #import firebase_admin
    import pyrebase

    dbconfig = config.dbconfig

    

    firebase = pyrebase.initialize_app(dbconfig)
    
    def authenitcation():
        #authenticate a user
        email = config.email
        password = config.passport
        #auth.create_user_with_email_and_password(email, password)
        #Get a reference to the auth service
        # Log the user in
        auth = firebase.auth()
        user = auth.sign_in_with_email_and_password(email, password)

        return user
    
    
    user = authenitcation()

    # Get a reference to the database service
    db = firebase.database()

    pt, tt = pyrebase_conn_test()
    
    def datacreation(db, user, data):
        #data to save
        # exampledata = {
        #     "name": "Mortimer 'Morty' Smith"
        # }
        
        
        db.child("fcc_subjects").push(data["fcc_subjects"], user['idToken'])
        
        db.child("plt_categories").push(data["plt_categories"], user['idToken'])
        
        db.child("users").push(data["userstable"], user['idToken'])
        
        for i, record in enumerate(data["platformstable"]):
            print(record)
            if record not in pt:
                db.child("platformstable").child(record).push(dict([(x,y) for x,y in data["platformstable"][record].items() if x != "subjects"]), user['idToken'])
                for s in data["platformstable"][record]['subjects']:
                    db.child("platformstable").child(record).child('subjects').child(s).push(data["platformstable"][record]['subjects'][s], user['idToken'])
                
        for i, record in enumerate(data["textstable"]):
            print(record)
            if record not in tt:
                db.child("textstable").child(record).push(dict([(x,y) for x,y in data["textstable"][record].items()]), user['idToken'])
        

    # def datacreation(db, user, data):
    #     '''
    #     TEMPORARY!!
    #     '''
    #     
    #     #data to save
    #     # exampledata = {
    #     #     "name": "Mortimer 'Morty' Smith"
    #     # }
    #     
    #     db.child("plt_categories").push(data["plt_categories"], user['idToken'])
    #     
    #     for i, record in enumerate(data["platformstable"]):
    #         print(record)
    #         if record not in pt:
    #             db.child("platformstable").child(record).push(dict([(x,y) for x,y in data["platformstable"][record].items() if x != "subjects"]), user['idToken'])
    #             for s in data["platformstable"][record]['subjects']:
    #                 db.child("platformstable").child(record).child('subjects').child(s).push(data["platformstable"][record]['subjects'][s], user['idToken'])
    #             
    #     for i, record in enumerate(data["textstable"]):
    #         print(record)
    #         if record not in tt:
    #             db.child("textstable").child(record).push(dict([(x,y) for x,y in data["textstable"][record].items()]), user['idToken'])
    #     
        
    etl_formattingsetstolists()
    
    datacreation(db, user, data)



def html_tests(subject):
    
    html = '''
            <div class="row">
                <div class="col-md-offset-8 col-md-4">
                    <input type="text" id="myInput" onkeyup="myFunction()" placeholder="Search by class (regex)...">
                </div>
            </div>
            <div>
               <table id="myTable">
                <tr class="header">
                    <th>DOMAIN</th>
                    <th>DESCRIPTION or KEYWORDS</th>
                    <th>TENTATIVE CLASSIFICATION</th>
                </tr>
    '''
    
    newcont = []
    for k in sorted(db['platformstable']):
        for s in db['platformstable'][k]['subjects']:
            if s == subject:
                print(k, s,  db['platformstable'][k]['subjects'][s]['count'], db['platformstable'][k]['subjects'][s]['proportion'])
                newcont.append((db['platformstable'][k]['subjects'][s]['proportion'],k,s,db['platformstable'][k]['category']))            
    
    for el in sorted(newcont, reverse=True):
        #print(el[1],el[2],el[3],el[0])
        html = html + "<tr><td><a href='"+el[1].replace('--','.')+"'>"+el[1].replace('--','.')+"</a></td><td style='font-size:110%;color:#3A4462;'>"+"{0}, ranking : {1:.2f}".format(el[2],el[0])+"</td><td>"+el[3]+"</td></tr>"

    endhtml = '''
    </table>
    </div>
        <script>
        function myFunction() {
            // Declare variables 
            var input, filter, table, tr, td, i;
            input = document.getElementById("myInput");
            //filter = input.value.toUpperCase();
            filter = new RegExp(input.value.toUpperCase());
            table = document.getElementById("myTable");
            tr = table.getElementsByTagName("tr");

            // Loop through all table rows, and hide those who don't match the search query
            for (i = 0; i < tr.length; i++) {
                //td = tr[i].getElementsByTagName("td")[0];
                td = tr[i].getElementsByTagName("td")[2];
                if (td) {
                    //if (td.innerHTML.toUpperCase().indexOf(filter) > -1) {
                    //console.log(td.innerHTML.toUpperCase())
                    if (td.innerHTML.toUpperCase().search(filter) > -1) {
                        tr[i].style.display = "";
                    } else {
                        tr[i].style.display = "none";
                    }
                }
            }
        }

        function myButton() {
            document.getElementById("myButton").onclick = function() {
                location.href = "./reference.html";
            };
        }
    </script>
    '''
    html = html + endhtml
    
    
    return html




# #########################################
# ##MAIN
# #########################################
# 
# if __name__ == "__main__":
#     #https://stackoverflow.com/questions/423379/using-global-variables-in-a-function-other-than-the-one-that-created-them
#     
#     ####PARAMETERS
#     directory = config.directory
#     subjects = ['getting started', 'responsive web design', 'javascript algorithms data structures', 'front end libraries', 'data visualization', 'apis microservices', 'information security quality assurance', 'contribute open source help nonprofits', 'coding interview questions take home assignments', 'endofthewholelist']
# 
#     
#     channels = [
#         #{"id":"546fd572db8155e6700d6eaf","name":"FreeCodeCamp/Freecodecamp"},
#         {"id":"5695eb3e16b6c7089cc24e10","name":"FreeCodeCamp/HelpBackEnd"},
#         #{"id":"5695e9a116b6c7089cc24db5","name":"FreeCodeCamp/HelpJavaScript"},
#         {"id":"5695eab116b6c7089cc24de2","name":"FreeCodeCamp/HelpFrontEnd"},
#         #{"id":"54a2fa80db8155e6700e42c3","name":"FreeCodeCamp/Help"},
#         ]
#     
#     title = [
#             #freecodecamp2,
#             "helpbackend1",
#             #"helpjavascript1",
#             "helpfrontend1",
#             #"help1",
#              ]
#     
#     def create_global_db():
#         global db
#         db = {"platformstable":{}, "userstable":{}, "textstable":{}, "fcc_subjects": {}, "plt_categories" : []}
#     
#     def use_global_db():
#         return db
#         
#     create_global_db()    
#     
#     for ic, channel in enumerate(channels):
#         print(channel["name"])
#         #data_collection(channel["id"], directory)
#         with open(directory+title[ic]+"_test.pkl", "rb") as infile:
#             raw = pickle.load(infile)
#             links_extraction_phase1(raw, title[ic])
#         try:
#             with open(directory+title[ic]+"_treateddata_links.pkl", "rb") as infile:
#                 botdata = pickle.load(infile)
#                 completing_db_with_data_from_botandcv(botdata)
#         except (FileNotFoundError):
#             print("A FILE ERROR has been found for ", title[ic])
#         except:
#             raise
#     for sb in subjects:
#         html_ranking = html_tests(sb)
#         with open(directory+'A_html_'+sb+'_links.html','w') as f:
#             f.write(html_ranking)
#     #calculating_total_subjectandcategories()
#     #pyrebase_conn(db)

    







            
