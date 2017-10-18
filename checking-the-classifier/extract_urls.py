import csv
from collections import defaultdict
import pprint
import json
import re

fcc_hostnames = []
ukwa_hostnames = []
with open('good_rows_fcc.csv', 'r') as data:
    reader = csv.reader(data, delimiter=',')
    url_row = 2
    next(reader)
    for row in reader:
        hostname = row[url_row].replace('www.',"")
        hostname = hostname.replace('.com',"")
        hostname = hostname.replace('.org',"")
        hostname = hostname.replace('.io',"")
        hostname = hostname.replace('.net',"")
        hostname = hostname.replace('.co',"")
        fcc_hostnames.append(hostname)

with open('classification_UKWA.tsv', 'r') as data:
    reader = csv.reader(data, delimiter='\t')
    url_row = 3
    for row in reader:
        hostname = row[url_row].replace('http://www.',"")
        hostname = hostname.replace('http://',"")
        hostname = hostname.replace('.com/',"")
        hostname = hostname.replace('.org/',"")
        hostname = hostname.replace('.org',"")
        hostname = hostname.replace('.io/',"")
        hostname = hostname.replace('.net/',"")
        hostname = hostname.replace('.co/',"")
        hostname = hostname.replace('.co',"")
        hostname = hostname.replace('.eu',"")
        hostname = hostname.replace('.uk/',"")
        ukwa_hostnames.append(hostname)

print("Same hostnames:", list(set(fcc_hostnames) & set(ukwa_hostnames)))
