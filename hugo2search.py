import re
import os
import os.path
import csv
import json
# https://github.com/wimglenn/oyaml
import oyaml as yaml
#import yaml

HUGO_DATA_DIR="hugo/data/"
PERSONS_INDEX="search/elasticsearch-persons.json"
LISTS_INDEX="search/elasticsearch-lists.json"

# Can be used to debug scripts
MAX_ROWS=int(os.environ.get('MAX_ROWS', 0))


def main():
    # Persons index
    rm_file(PERSONS_INDEX)
    with open(PERSONS_INDEX, "a") as index_file:
        i = 0
        for doc_id, p in yaml_reader_folder(os.path.join(HUGO_DATA_DIR, "persons")):
            i += 1
            if not i % 1000:
                print (doc_id)
            data = {
                "firstname": p["name"]["firstname"],
                "midname": p["name"]["midname"],
                "lastname": p["name"]["lastname"],
                "nameshow": p["name"]["nameshow"],
            }
            content = data2index("persons", doc_id, data)
            index_file.write(content)


def data2index(index_name, doc_id, data):
    # see https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-bulk.html#docs-bulk-api-desc
    return "\n".join([
        json_dumps({"index": {"_index": index_name, "_id": doc_id}}),
        json_dumps(data),
        ""
    ])

def json_dumps(data):
    return json.dumps(data, ensure_ascii=False)

def yaml_reader_folder(folder):
    for fname in sorted(os.listdir(folder), key=alphanum_key):
        if not fname.endswith(".yaml"):
            print ("ignored file:", fname)
            continue
        name = fname.split(".")[0]
        yield name, yaml_reader(os.path.join(folder, fname))


def yaml_reader(file_name):
    with open(file_name, "r") as f:
        return yaml.load(f)

def rm_file(file_name):
    try:
        os.remove(file_name)
    except OSError:
        pass

# From https://stackoverflow.com/a/4623518/222675
def tryint(s):
    try:
        return int(s)
    except:
        return s

def alphanum_key(s):
    """ Turn a string into a list of string and number chunks.
        "z23a" -> ["z", 23, "a"]
    """
    return [ tryint(c) for c in re.split('([0-9]+)', s) ]

if __name__ == "__main__":
    main()
