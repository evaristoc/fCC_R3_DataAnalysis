import csv
from collections import defaultdict
import pprint
import json

with open('annotatedplatformsphase1_a6.csv', 'r') as data:
    reader = csv.reader(data, delimiter=';')
    good_rows = []
    bad_rows = []
    good_rows_count = 0
    bad_rows_count = 0
    for row in reader:
        #Rows seems to have different lengths, maybe because of newlines?

        #Generate new dataset only with rows with all columns
        if len(row) == 15:
            good_rows.append(row)
            good_rows_count +=1
        else:
            bad_rows.append(row)
            bad_rows_count +=1

    with open("good_rows_fcc.csv", "w") as fp:
        writer = csv.writer(fp)
        writer.writerows(good_rows)

    with open("bad_rows_fcc.csv", "w") as fp:
        writer = csv.writer(fp)
        writer.writerows(bad_rows)

    print("{} good rows and {} bad rows".format(good_rows_count, bad_rows_count))
