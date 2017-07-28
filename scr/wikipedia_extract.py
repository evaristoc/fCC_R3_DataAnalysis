import os, sys, pathlib
from IPython.display import display, Math, Latex #also '%%latex' magic command
import collections, itertools, operator, re, copy, datetime
import urllib, urllib.request, urllib.parse, dns, ipwhois
import pickle, json, csv, zipfile
import math, random, numpy, scipy, pandas
import bs4

#actualcwd = os.getcwd()
#os.chdir(actualcwd)
#print(os.getcwd())

#REFERENCES:
#-- https://stackoverflow.com/questions/1726402/in-python-how-do-i-use-urllib-to-see-if-a-website-is-404-or-200


def wikipediasearch(platform):
    title = ''
    while True:
        url = 'https://en.wikipedia.org/w/api.php?action=query&list=search&format=json&srsearch='+platform
        req = urllib.request.Request(url)
        resp = None
        try:
            resp = urllib.request.urlopen(req)
        except urllib.error.HTTPError as e:
                print(e)
                return title
        respData = resp.read()
        r = json.loads(respData.decode("utf-8"))
        if 'error' in list(r.keys()):
            return title
        if r['query']['search'] != []:
            break
        elif r['query']['search'] == [] and len(platform.split('.')) > 2:
            platform = '.'.join(platform.split('.')[1:])
        elif r['query']['search'] == [] and len(platform.split('.')) <= 2:
            print(platform, ' not found in wikipedia')
            break
    for i,t in  enumerate(r['query']['search']):
        if set(t['title'].lower().replace('.', ' ').split(' ')).intersection(set(platform.split('.'))):
            title = t['title']
            break
        elif set([''.join(t['title'].lower().replace('.', ' ').split(' '))]).intersection(set(platform.split('.'))):
            title = t['title']
            break
    
    print(platform, title)
    return title

def wikipediaextract(title):
    title = title.replace(' ', '%20')
    url = 'https://en.wikipedia.org/w/api.php?action=query&prop=extracts&format=json&titles='+title
    try:
        req = urllib.request.Request(url)
    except:
        return ''
    resp = urllib.request.urlopen(req)
    respData = resp.read()
    r = json.loads(respData.decode("utf-8"))
    #print(r)
    return list(r['query']['pages'].values())[0]['extract']
    

def souping(extract):
    soup = bs4.BeautifulSoup(extract)
    #print(soup.find_all('p')[0].text)
    if soup.find_all('p')[0].text: print("Some Text Found")
    return soup.find_all('p')[0].text

def getting_wikipedia(data):
    for plt in data['platform']:
        title = wikipediasearch(plt)
        print(title, ' in getting wikipedia')
        if title == '':
            data.loc[data['platform'] == plt,'wiki'] = ''
            continue
        extract = wikipediaextract(title)
        wiki = souping(extract)
        #print(wiki)
        data.loc[data['platform'] == plt,'wiki'] = wiki
        #data.loc[data['platform'] == plt,'wiki'] = 1
