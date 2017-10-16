
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



def getcategories(dir):
    cats = {}
    
    with open(docsdirectory+'/category_operationalization.csv', 'r') as infile:
        reader = csv.DictReader(infile, delimiter=':')
        print(reader)
        for row in reader:
            cats[row['category']] = row['category_regex']
    return cats

def datatypecorrection(v): #check WHY this is happening here!!!
    if isinstance(v,list):
        return v[0]
    else:
        return v

def etl_formattingsetstolists(db):
    '''
    db is global for this function
    for some reason in previous codes I saved some data points as sets; this will transform sets into lists so they can be accepted by firebase
    ''' 
    for plt in db['platformstable']:
        for k in db['platformstable'][plt]:
            if type(db['platformstable'][plt][k]) == set:
                db['platformstable'][plt][k] = list(db['platformstable'][plt][k])

    # for txt in db['textstable']:
    #     for k in db['textstable'][txt]:
    #         if type(db['textstable'][txt][k]) == set:
    #             db['textstable'][txt][k] = list(db['textstable'][txt][k])
    #     
    # for usr in db['userstable']:
    #     if type(db['userstable'][usr]) == set:
    #         db['userstable'][usr] = list(db['userstable'][usr])

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

    dbconfig = config.config.dbconfig

    

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

    dbconfig = config.config.dbconfig

    

    firebase = pyrebase.initialize_app(dbconfig)
    
    def authenitcation():
        #authenticate a user
        email = config.config.email
        password = config.config.password
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
        
        
        ## OJO differences between *.push(...) and *.set(...) !!!
        
        #db.child("fcc_subjects").push(data["fcc_subjects"], user['idToken'])
        
        #db.child("plt_categories").push(data["plt_categories"], user['idToken'])
        
        #db.child("users").push(data["userstable"], user['idToken'])
        
        for i, record in enumerate(data["platformstable"]):
            print(record)
            if record not in pt:
                db.child("platformstable").child(record).push(dict([(x,y) for x,y in data["platformstable"][record].items() if x != "subjects"]), user['idToken'])
                for s in data["platformstable"][record]['subjects']:
                    if s == None:
                        print('Subjects failed for ', pt)
                    db.child("platformstable").child(record).child('subjects').child(s).push(data["platformstable"][record]['subjects'][s], user['idToken'])
                
        # for i, record in enumerate(data["textstable"]):
        #     print(record)
        #     if record not in tt:
        #         db.child("textstable").child(record).push(dict([(x,y) for x,y in data["textstable"][record].items()]), user['idToken'])
        # 

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
        
  
    datacreation(db, user, data)


def pyrebase_manip(data):
    #import firebase_admin
    import pyrebase

    dbconfig = config.config.dbconfig

    

    firebase = pyrebase.initialize_app(dbconfig)
    
    def authenitcation():
        #authenticate a user
        email = config.config.email
        password = config.config.passport
        #auth.create_user_with_email_and_password(email, password)
        #Get a reference to the auth service
        # Log the user in
        auth = firebase.auth()
        user = auth.sign_in_with_email_and_password(email, password)

        return user
    
    
    user = authenitcation()

    # Get a reference to the database service
    db = firebase.database()

    def datacheck(db,*args):
        child1 = args[0]
        print(child1, args)
        cont = []
        if db.child(child1).get().val():
            #print(db.child(child1).get().val())
            #print(db.child(child1).get().val().keys())
            for k in db.child(child1).get().val().keys():
                #print(k)
                cont.append(k)
        return cont
    
    for rec in data['platformstable']:
        if rec:
            rec = 'ajax--googleapis--com'
            if db.child('platformstable').child(rec):
                #print(rec, db.child('platformstable').get().val().keys())
                break
    if db.child('platformstable').get().val():
        print(db.child('platformstable').get().val().keys())
    else:
        print('None')
        
    #print(list(db.child(list(db.get().val().keys())[0]).child('ajax--googleapis--com').get().val().keys()))
    print(list(db.child('platformstable').child('ajax--googleapis--com').get().val().keys()))
    print(db.child('platformstable').child('ajax--googleapis--com').shallow().get().val())
    #pt = datacheck(db,"platformstable")
    #print('this is pt', pt)
    
    counter = 0
    for rec in data['platformstable']:
        if db.child('platformstable').child(rec).get().val().keys():
            if 'subjects' not in list(db.child('platformstable').child(rec).get().val().keys()):
                print(rec)
    print(counter)




#########################################
##MAIN
#########################################

if __name__ == "__main__":
    '''
    db (data) keys = ['userstable', 'platformstable', 'textstable', 'plt_categories', 'fcc_subjects']
    record keys = ['htext', 'users', 'subjects', 'modified', 'keywords', 'origurl', 'category', 'alltext', 'title', 'textids', 'minsecurity', 'created', 'params', 'frequency-recency', 'description', 'crawlstatus']
    
    
    '''

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
    
    docsdirectory = os.getcwd()+'/docs'
    
    cats = getcategories(docsdirectory)
    
    cv_subjects = ['getting started', 'responsive web design', 'javascript algorithms data structures', 'front end libraries', 'data visualization', 'apis microservices', 'information security quality assurance', 'contribute open source help nonprofits', 'coding interview questions take home assignments']
    
    cv, bow = bowcv_test()
    
    with open(datadirectory+'/annotatedplatformsphase1_a8.csv', 'r') as infile:
        reader = csv.DictReader(infile, delimiter=";", quotechar="'")
        for row in reader:
            if row["platform"].replace('.','--') in list(dbp.keys()):
                cat = ''
                if row["category"] in  'COMMUITY,COMMUNITY'.split(','):
                    cat = 'SOCIAL'
                elif row["category"] in ['REPL']:
                    cat = 'TOOLS'
                elif row["category"] in ['PAAS']:
                    cat = 'CLOUD'
                elif row["category"] in  'NEWS, WRCOTENT'.split(','):
                    cat = 'WRCONTENT'
                else:
                    cat = row["category"]
                dbp[row["platform"].replace('.','--')]["category"] =  cat
                dbp[row["platform"].replace('.','--')]['category_regex'] = cats[cat]
                dbp[row["platform"].replace('.','--')]["alltext"] =  row["alltext"]
                dbp[row["platform"].replace('.','--')]["params"] =  row["params"].split(',')
            
            ## HACK!!!!
            else:
                plt = row["platform"]
                platform = row["platform"].replace('.','--')
                cat = ''
                if row["category"] in  'COMMUITY,COMMUNITY'.split(','):
                    cat = 'SOCIAL'
                elif row["category"] in ['REPL']:
                    cat = 'TOOLS'
                elif row["category"] in ['PAAS']:
                    cat = 'CLOUD'
                elif row["category"] in  'NEWS, WRCOTENT'.split(','):
                    cat = 'WRCONTENT'
                else:
                    cat = row["category"]
                dbp[platform] = {}
                dbp[platform]["origurl"] = plt
                dbp[platform]["category"] = cat
                dbp[platform]["category_regex"] = cats[cat]
                dbp[platform]["frequency-recency"] = []
                dbp[platform]["subjects"] = {}
                dbp[platform]["minsecurity"] = None
                dbp[platform]["crawlstatus"] = None
                dbp[platform]["title"] = row["title"]
                dbp[platform]["description"] = row["description"]
                dbp[platform]["keywords"] = row["keywords"]
                dbp[platform]["htext"] = row["htext"]
                dbp[platform]["alltext"] = row["alltext"]
                dbp[platform]["params"] = row["params"].split(',')
                dbp[platform]["textids"] = set()
                dbp[platform]["users"] = set()
                dbp[platform]["created"] = ""
                dbp[platform]["modified"] = ""
                for s in cv_subjects:
                    dbp[platform]["subjects"][s] = {}
                    dbp[platform]["subjects"][s]["proportion"] = 0
                    dbp[platform]["subjects"][s]["count"] = 0
                cvcovering_test(dbp[platform], cv, bow)

    
    # for reck in dbp:
    #     cat = ''
    #     if datatypecorrection(dbp[reck]['category']) in 'COMMUITY,COMMUNITY'.split(','):
    #         cat = 'SOCIAL'
    #     elif datatypecorrection(dbp[reck]['category']) in ['REPL']:
    #         cat = 'TOOLS'
    #     elif row["category"] in ['PAAS']:
    #         cat = 'CLOUD'
    #     elif datatypecorrection(dbp[reck]['category']) in 'NEWS, WRCOTENT'.split(','):
    #         cat = 'WRCONTENT'
    #     else:
    #         cat = datatypecorrection(dbp[reck]['category'])
    #     dbp[reck]['category'] = cat
    #     dbp[reck]['category_regex'] = cats[cat]
    
    #similar platforms: implement kNN/cosine similarity for comparisons between platforms based on ranking per subject; 10 per subject
    
    count = 0
    for rec in dbp: #check post
        #print(dbp[rec]['alltext'])
        count += 1
        if count > 5:
            break    
    
    
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy
    from scipy import sparse
    
    tfidf = TfidfVectorizer(norm='l2', min_df=0, use_idf=True, smooth_idf=False, sublinear_tf=True)
    
    a = list()    
    count = 0
    
    
    for rec in dbp: #check post
        #print(dbp[rec]['alltext'])
        a.append([rec,datatypecorrection(dbp[rec]['category']),dbp[rec]['alltext']])
    #    count += 1
    #    if count > 5:
    #        break
    #print(numpy.array(a))
    #print(numpy.array(a)[1])
    
    A =  numpy.array(a).T
    A_sparse = sparse.csr_matrix(tfidf.fit_transform(A[2]))
    
    similarities = cosine_similarity(A_sparse)
    
    
    
    # for i in range(11):
    #     selection = numpy.argsort(similarities[i])[::-1][:11]
    #     print(list(zip(A[0][selection],A[1][selection],similarities[i][selection])))
    
    
    
    for ii in range(len(A[0])):
        if 'similars' not in list(dbp[A[0][ii]].keys()):
            dbp[A[0][ii]]['similars'] = []
            categorysearch = A[1][ii]
            selection = numpy.argsort(similarities[ii])[::-1]
            count = 0
            for kk in selection:
                if A[1][kk] == categorysearch:
                    #print(A[0][kk],A[1][kk],similarities[ii][kk])
                    dbp[A[0][ii]]['similars'].append(A[0][kk])
                    count += 1
                if count == 11:
                     break
    
    
    #other people's selection: identify other mentions of platforms and find similarities as above (?); 10 per subject
    
    ##building the lists of people's selections...
    data = pickle.load(open(directory+'db.pkl','rb'))
    user = data['userstable']
    
    # count = 0    
    # for reck in dbp:
    #     for us in dbp[reck]['users']:
    #         print(us, len(users[us]))
    #     count += 1
    #     if count > 5:
    #         break
    # 
    # count = 0    
    # for reck in dbp:
    #     for us in dbp[reck]['users']:
    #         print(us)
    #     count += 1
    #     if count > 5:
    #         break

    #count = 0            
    for reck in dbp:
        dictofothers = dict()
        dbp[reck]['listofothers'] = []
        for us in user:
            if reck in user[us]:
                #print(reck, us, len(user[us]))
                for other in user[us]:
                    if other not in list(dictofothers.keys()):
                        dictofothers[other] = 0
                    if other != reck:
                        dictofothers[other] += 1
        dictofothers = sorted(dictofothers.items(), key = lambda x: x[1], reverse=True)[:10]
        #print(reck, ' : ', dictofothers)
        for o in dictofothers:
            if o[1] != 0:
                dbp[reck]['listofothers'].append(o[0])
        # count += 1
        # if count > 10:
        #     break
        

    #update last date
    
    # #data pushed into db
    datadb = {}
    datadb["platformstable"] = dbp
    # datadb["fcc_subjects"] = cv
     
     
    etl_formattingsetstolists(datadb)
     
    pyrebase_conn(datadb) #-Ktku4KfM-kJaELMHipC to delete!
     



  