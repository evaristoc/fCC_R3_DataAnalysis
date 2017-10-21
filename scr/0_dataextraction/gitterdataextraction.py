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

def date_msg(elem):
    ##START
    elem = elem[:10]
    datetext = datetime.date(int(elem[:4]),int(elem[5:7]),int(elem[8:10]))
    return datetext
    ##END date_msg

def gitter_data_collection(channel, directory):
    ##START
    # large limits not valid any more
    #url = "https://api.gitter.im/v1/rooms/"+channel+"/chatMessages?limit=80000"
    limit = 80000
    url = "https://api.gitter.im/v1/rooms/"+channel+"/chatMessages?limit=100"
    apikey = config.config.gitterapikey
    gitterheader = {
        "User-Agent": "freecodecamp project (@evaristoc github) Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:38.0) Gecko/20100101 Firefox/38.0",
        "Content-Type": "Application/json",
        "Accept": "application/json",
        "Authorization":"Bearer "+apikey
        }
    req = urllib.request.Request(url, headers=gitterheader)
    resp = urllib.request.urlopen(req)
    respData = resp.read()
    r = json.loads(respData.decode("utf-8"))
    rep = 1
    print(len(r))
    print(r[0]['sent'])
    print(r[0]['id'])
    print(sys.getsizeof(r))
    rdumped = r
    print(rep)
    print()
    print()
    try:
        while rep < limit:
            url_seek = url+"&beforeId="+r[0]['id']
            req = urllib.request.Request(url_seek, headers=gitterheader)
            resp = urllib.request.urlopen(req)
            respData = resp.read()
            r = json.loads(respData.decode("utf-8"))
            rep += 1
            print(len(r))
            if len(r) == 0:
                break
            print(r[0]['sent'])
            print(r[0]['id'])
            print(sys.getsizeof(r))
            rdumped = r + rdumped
            print(rep)
            if date_msg(r[0]["sent"]) - LOWERLIMITmsg < datetime.timedelta(0):
                break
            print()
            print()
    except:
        raise
    finally:
        with open(directory+"/"+title[ic]+"_test.pkl", "bw") as f_out:
            pickle.dump(rdumped, f_out)
    ##END data_collection           


