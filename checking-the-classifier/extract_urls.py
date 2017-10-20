import csv
from collections import defaultdict
from pprint import pprint
import json
import re

def extractUrls(file_dir, url_row_index, delimiter):
    categories = []
    with open(file_dir, 'r') as data:
        reader = csv.reader(data, delimiter=delimiter)
        url_row = url_row_index
        next(reader)
        for row in reader:
            if(len(row)-1 >= url_row):
                hostname = row[url_row]
                hostname = hostname.replace('.uk/',"")
                categories.append(hostname)

    return categories

def getHostname(url):
    hostname = url.replace('www.',"")
    hostname = hostname.replace('.com',"")
    hostname = hostname.replace('.org',"")
    hostname = hostname.replace('.org/',"")
    hostname = hostname.replace('.io',"")
    hostname = hostname.replace('.io/',"")
    hostname = hostname.replace('.net',"")
    hostname = hostname.replace('.net/',"")
    hostname = hostname.replace('.co',"")
    hostname = hostname.replace('.co/',"")
    hostname = hostname.replace('http://',"")
    hostname = hostname.replace('https://',"")
    hostname = hostname.replace('http://',"")
    hostname = hostname.replace('.eu',"")
    return url

if __name__ == '__main__':
    fcc_hostnames = extractUrls('data/good_rows_fcc.csv', 2, ',')
    ukwa_hostnames = extractUrls('data/classification_UKWA.tsv', 3,'\t')
    learn_anything_hostnames = extractUrls('./learn_anything_urls/learn-anything_urls.csv', 8, ',')
    print("Same hostnames fCC UKWA", list(set(fcc_hostnames) & set(ukwa_hostnames)))
    print("Same hostnames fCC learn-anything", list(set(fcc_hostnames) & set(learn_anything_hostnames)))
