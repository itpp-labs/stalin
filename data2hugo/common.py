import os
import os.path
import csv
import json

CSV_DIR="data/db/tables/"

LISTS_CSV=os.path.join(CSV_DIR, "lists.csv")
SUBLISTS_CSV=os.path.join(CSV_DIR, "sublists.csv")
LIST_TITLE_CSV=os.path.join(CSV_DIR, "listtitl.csv")
PAGES_CSV=os.path.join(CSV_DIR, "pages.csv")

PERSONS_CSV=os.path.join(CSV_DIR, "persons.csv")
SPRAVKI_CSV=os.path.join(CSV_DIR, "spravki.csv")

# Can be used to debug scripts
MAX_ROWS=int(os.environ.get('MAX_ROWS', 0))

HUGO_DATA_DIR="hugo/data"
HUGO_CONTENT_DIR="hugo/content"

def csv_reader(file_name):
    with open(file_name) as csvfile:
        reader = csv.DictReader(csvfile)
        count = 0
        for row in reader:
            count +=1
            if MAX_ROWS and count > MAX_ROWS:
                return
            yield row

def file_writer(file_name, file_content):
    with open(file_name, 'w') as writer:
        writer.write(file_content)

def json_writer(file_name, data):
    file_writer(file_name, json.dumps(data, ensure_ascii=False))

def x2many(get_id, records):
    d = dict()
    for r in records:
        i = get_id(r)
        d.setdefault(i, [])
        d[i].append(r)
    return d

def list2name(record):
    return 'list-%s' % record['listid']

