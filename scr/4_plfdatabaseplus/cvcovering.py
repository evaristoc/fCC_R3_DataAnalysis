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