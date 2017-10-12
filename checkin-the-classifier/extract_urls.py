<<<<<<< HEAD
import os,sys
=======
>>>>>>> 3852fdcde8831e44299f76aa3e21c894fa37abaa
import csv
from collections import defaultdict
import pprint
import json
import re

fcc_hostnames = []
ukwa_hostnames = []
<<<<<<< HEAD
with open(os.getcwd()+'/checkin-the-classifier/good_rows_fcc.csv', 'r') as data:
=======
with open('good_rows_fcc.csv', 'r') as data:
>>>>>>> 3852fdcde8831e44299f76aa3e21c894fa37abaa
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
<<<<<<< HEAD
        #fcc_hostnames.append(hostname)
        fcc_hostnames.append(hostname.split("."))

with open(os.getcwd()+'/checkin-the-classifier/classification_UKWA.tsv', 'r') as data:
=======
        fcc_hostnames.append(hostname)

with open('classification_UKWA.tsv', 'r') as data:
>>>>>>> 3852fdcde8831e44299f76aa3e21c894fa37abaa
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

<<<<<<< HEAD
#print("Same hostnames:", list(set(fcc_hostnames) & set(ukwa_hostnames)))

for fcch in fcc_hostnames:
    for sec in fcch:
        for ukwah in ukwa_hostnames:
            if ukwah.find(sec) != -1:
                if len(ukwah) == len(sec):
                    print(sec, ukwah)
=======
print("Same hostnames:", list(set(fcc_hostnames) & set(ukwa_hostnames)))
>>>>>>> 3852fdcde8831e44299f76aa3e21c894fa37abaa
