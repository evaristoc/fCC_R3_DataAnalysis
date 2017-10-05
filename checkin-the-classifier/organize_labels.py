import csv
from collections import defaultdict
import pprint
import json

with open('classification_UKWA.tsv', 'r') as data:
    reader = csv.reader(data, delimiter='\t')
    categories = {}
    next(reader)
    for row in reader:
        if row[0] not in categories:
            categories[row[0]] = 1
        else:
            categories[row[0]] += 1

    pprint.pprint(categories)
    output_dict = []
    for category,size in categories.items():
        output_dict.append({"size":size,"name":category})

    with open("categories_UKWA_teste.json", "w") as fp:
        json.dump(output_dict, fp)

with open('category_operationalization.csv', 'r') as data:
    reader = csv.reader(data, delimiter=':')
    categories = {}
    next(reader)
    for row in reader:
        if row[0] not in categories:
            categories[row[0]] = 1
        else:
            categories[row[0]] += 1
    pprint.pprint(categories)

    output_dict = []
    for category,size in categories.items():
        output_dict.append({"size":size,"name":category.capitalize()})

    with open("categories_fcc.json", "w") as fp:
        json.dump(output_dict, fp)
