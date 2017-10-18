import csv
from collections import defaultdict
import pprint
import json

def extractLabelsUKWA(dir):
    with open(dir, 'r') as data:
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

        with open("data/categories_UKWA_teste.json", "w") as fp:
            json.dump(output_dict, fp)


def extractLabels(file_dir, output_dir, category_row_id, delimiter):
    with open(file_dir, 'r') as data:
        reader = csv.reader(data, delimiter=delimiter)
        categories = {}
        next(reader)
        for row in reader:
            if row[category_row_id] not in categories:
                categories[row[category_row_id]] = 1
            else:
                categories[row[category_row_id]] += 1
        pprint.pprint(categories)

        output_dict = []
        for category,size in categories.items():
            output_dict.append({"size":size,"name":category.capitalize()})

        with open(output_dir, "w") as fp:
            json.dump(output_dict, fp)


if __name__ == '__main__':
    extractLabelsUKWA('data/classification_UKWA.tsv')
    extractLabels('data/category_operationalization.csv', 'data/categories_fcc.json',0,":")
    extractLabels('./learn_anything_urls/learn-anything_urls.csv', 'data/categories_learn_anything.json',1,",")
