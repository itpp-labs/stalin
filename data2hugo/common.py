import os
import os.path
import csv
import json
# https://github.com/wimglenn/oyaml
import oyaml as yaml
#import yaml

# https://stackoverflow.com/questions/13518819/avoid-references-in-pyyaml
yaml.Dumper.ignore_aliases = lambda *args : True


CSV_DIR="data/db/tables/"

LISTS_CSV=os.path.join(CSV_DIR, "lists.csv")
SUBLISTS_CSV=os.path.join(CSV_DIR, "sublists.csv")
LIST_TITLE_CSV=os.path.join(CSV_DIR, "listtitl.csv")
PAGES_CSV=os.path.join(CSV_DIR, "pages.csv")
OTHERS_CSV=os.path.join(CSV_DIR, "others.csv")
POMETY_CSV=os.path.join(CSV_DIR, "pomety.csv")
TITLES_CSV=os.path.join(CSV_DIR, "titles.csv")
PERSON2PAGE_YAML="data2hugo/person2page.yaml"

PERSONS_CSV=os.path.join(CSV_DIR, "persons.csv")
SPRAVKI_CSV=os.path.join(CSV_DIR, "spravki.csv")
PRIM_CSV=os.path.join(CSV_DIR, "prim.csv")

# Can be used to debug scripts
MAX_ROWS=int(os.environ.get('MAX_ROWS', 0))

HUGO_DATA_DIR="hugo/data"
HUGO_CONTENT_DIR="hugo/content"
GB_SPRAVKI_DIR="data/disk/vkvs/z3/spravki"


# Yaml tools
class folded_unicode(str): pass
class literal_unicode(str): pass

def folded_unicode_representer(dumper, data):
    return dumper.represent_scalar(u'tag:yaml.org,2002:str', data, style='>')
def literal_unicode_representer(dumper, data):
    return dumper.represent_scalar(u'tag:yaml.org,2002:str', data, style='|')

yaml.add_representer(folded_unicode, folded_unicode_representer)
yaml.add_representer(literal_unicode, literal_unicode_representer)



def extend_person(data, p, pometa_text=None):
    for f in ["striked","underlined","pometa"]:
        if p[f] == "1":
            data[f] = True
    if pometa_text:
        data["pometa_text"] = pometa_text
    return data

def file2str(file_name, encoding="cp1251"):
    with open(file_name, "r", encoding=encoding) as f:
        return f.read()


def csv_reader(file_name):
    with open(file_name) as csvfile:
        reader = csv.DictReader(csvfile)
        count = 0
        for row in reader:
            count +=1
            if MAX_ROWS and count > MAX_ROWS:
                return
            yield row

def yaml_reader(file_name):
    with open(file_name, "r") as f:
        # TODO: /home/ubuntu/stalin/data2hugo/common.py:64: YAMLLoadWarning:
        # calling yaml.load() without Loader=... is deprecated, as the default
        # Loader is unsafe. Please read https://msg.pyyaml.org/load for full
        # details.
        return yaml.load(f)

def file_writer(file_name, file_content):
    with open(file_name, 'w') as writer:
        writer.write(file_content)

def json_writer(file_name, data, **kwargs):
    file_writer(file_name, json.dumps(data, ensure_ascii=False, **kwargs))

def yaml_writer(file_name, data):
    print ("write file: ", file_name)
    file_writer(file_name, yaml.dump(data, allow_unicode=True))

def x2many(get_id, records):
    d = dict()
    for r in records:
        i = get_id(r)
        d.setdefault(i, [])
        d[i].append(r)
    return d

def list2name(record):
    return 'list%s' % record['listid']

def person2name(record):
    return 'p%s' % record['personid']

def list2title(lst):
    delo = ""
    if lst["ed_hr"]:
        delo = ", дело %s" % lst["ed_hr"]
    return "РГАСПИ, ф.{fond}, т.{tom}, оп.{opis}{delo}, лист {page1}".format(**lst, delo=delo)

def sublist2title(lst, sublst):
    return "Список от {date} [{title}]".format(
        date=sublst["datetext"],
        title=sublst["sublisttitle"],
    )
def sublist2title_full(lst, sublst):
    return "%s - %s" % (sublist2title(lst, sublst), list2title(lst))

def person_list2url(person, lst, sublst):
    # TODO make sublink to line in page
    # "list_id": pp["listnum"],
    # "sublist_id": pp["asublistid"],
    # "pageintom": pp["pageintom"],
    # "rowinpage": pp["rowinpage"],
    # "nomer": pp["nomer"],
    return "/lists/%s#page-%s-num-%s" % (list2name(lst), person["pageintom"], person["nomer"])

def clean_date(s):
    if not s or s == "0000-00-00" or s == "NULL":
        return None
    return s

def convert_date(s):
    s = clean_date(s)
    # TODO: convert dates to DD.MM.YYYY format
    return s
