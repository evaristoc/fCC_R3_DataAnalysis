import os, sys, pathlib
from IPython.display import display, Math, Latex #also '%%latex' magic command
import collections, itertools, operator, re, copy, datetime
import nltk, sklearn

import config.config as config

if os.path.exists(config.anacondadir):
    print('ok')
    nltk.data.path.append(config.anacondadir)

def datapreparation(data):
    
    usual_stopwords = nltk.corpus.stopwords.words('english')
    other_words = ["re", "fm", "tv", "la", "al", "ben", "aq", "ca", "can", "can'", "can't", "cant", "&"]
    punctuation = ["\\","/", "|","(",")",".",",",":","=","{","}","==", "===","[","]","+","++","-","--","_","<",">","'","''","``",'"',"!","!=","?",";"]
    wtbr = usual_stopwords + other_words + punctuation
    
    pattern01 = re.compile(r'[^a-z0-9]', flags=re.IGNORECASE)
    pattern02 = re.compile(r'\d+', flags=re.IGNORECASE)
    pattern03 = re.compile(r'\w$', flags=re.IGNORECASE)
    
    for plt in data['platform']:
        count = 0
        textlist = ['']
        if data.loc[data['platform'] == plt, 'description'].values[0] != '' and data.loc[data['platform'] == plt, 'description'].values[0] != None:
            if data.loc[data['platform'] == plt, 'description'].values[0] not in ['noinformationfound', 'errorreachingpage']:
                if type(data.loc[data['platform'] == plt, 'description'].values[0]) == 'str':
                    textlist = textlist + re.sub(pattern01, ' ',data.loc[data['platform'] == plt, 'description'].values[0].lower()).split(' ')
                    count += 1
        if data.loc[data['platform'] == plt, 'keywords'].values[0] != '' and data.loc[data['platform'] == plt, 'keywords'].values[0] != None:
            if data.loc[data['platform'] == plt, 'keywords'].values[0] not in ['noinformationfound', 'errorreachingpage']:
                if type(data.loc[data['platform'] == plt, 'keywords'].values[0]) == 'str':
                    textlist = textlist + re.sub(pattern01, ' ',data.loc[data['platform'] == plt, 'keywords'].values[0].lower()).split(' ')
                    count += 1
        if data.loc[data['platform'] == plt, 'title'].values[0] != '' and data.loc[data['platform'] == plt, 'title'].values[0] != None:
            if data.loc[data['platform'] == plt, 'title'].values[0] not in ['noinformationfound', 'errorreachingpage']:
                if type(data.loc[data['platform'] == plt, 'title'].values[0]) == 'str':
                    textlist = textlist + re.sub(pattern01, ' ',data.loc[data['platform'] == plt, 'title'].values[0].lower()).split(' ')
                    count += 1
        if data.loc[data['platform'] == plt, 'htext'].values[0] != '' and data.loc[data['platform'] == plt, 'htext'].values[0] != None:
            if data.loc[data['platform'] == plt, 'htext'].values[0] not in ['noinformationfound', 'errorreachingpage']:
                if type(data.loc[data['platform'] == plt, 'htext'].values[0]) == 'str':
                    textlist = textlist + re.sub(pattern01, ' ',data.loc[data['platform'] == plt, 'htext'].values[0].lower()).split(' ')
                    count += 1

        if type(data.loc[data['platform'] == plt, 'params'].values[0]) == 'str':
            for p in data.loc[data['platform'] == plt, 'params'].values[0].split(','):
                allpwds = re.sub(pattern01, ' ', p.lower()).split(' ')
                textlist = textlist + allpwds

        #print(set(textlist))
        
        text = ''
            
        for e in set(textlist):
            #assert type(e).__name__ == str, type(e)
            if (e != '' or e != ' ') and not re.match(pattern02, e) and e not in wtbr:
                #print(e)
                if e in ['rants', 'rant']:
                    e = 'blog'
                text = text + ' ' + e
                    
        data.loc[data['platform'] == plt, 'alltext'] = text
