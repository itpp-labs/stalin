import os
import os.path
import csv
import json
from datetime import datetime
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
TITLE2GEOSUB_YAML="data2hugo/title2geosub.yaml"

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



def extend(data, **kwargs):
    for k, v in kwargs.items():
        if v:
            data[k] = v
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
    print ("write file: ", file_name)
    with open(file_name, 'w') as writer:
        writer.write(file_content)

def json_writer(file_name, data, **kwargs):
    file_writer(file_name, json.dumps(data, ensure_ascii=False, **kwargs))

def yaml_writer(file_name, data):
    file_writer(file_name, yaml.dump(data, allow_unicode=True))

def x2many(get_id, records):
    d = dict()
    for r in records:
        i = get_id(r)
        d.setdefault(i, [])
        d[i].append(r)
    return d


def get_signs(lst):
    res = {}
    for key in ["signstalin", "signmolotov", "signjdanov", "signkaganovic", "signvoroshilov", "signmikoyan", "signejov", "signkosior"]:
        if lst[key] == "1":
            res[key[4:]] = True
    return res

def list2name(record):
    return 'list%s' % record['listid']

def person2name(record):
    return 'p%s' % record['personid']

def list2title(lst):
    res = lst["listtitle"]
    if lst["datetext"] and lst["datetext"] != "NULL":
        res += " // %s" % lst["datetext"]
    return res

def list2archive(lst):
    delo = ""
    if lst["ed_hr"]:
        delo = ", дело %s" % lst["ed_hr"]
    archive_title = "РГАСПИ"
    if lst["listid"] in ["411", "412"]:
        archive_title = "АП РФ"
    return {
        "ref": "{archive_title}, ф.{fond}, оп.{opis}{delo}".format(**lst, delo=delo, archive_title=archive_title),
        "page1": lst["page1"]
    }

def sublist2title(lst, sublst, kat=None):
    if not sublst["datetext"]:
        return sublst["sublisttitle"]
    res = "Список от {date}".format(
        date=sublst["datetext"],
    )
    if sublst["sublisttitle"]:
        res += " [{title}]".format(
            title=sublst["sublisttitle"],
        )
    if kat:
        res += " - %s-я категория" % kat

    return res

def sublist2title_full(lst, sublst, person=None):
    archive = list2archive(lst)
    page = archive["page1"]
    kat = None
    if person:
        page = person["pageintom"]
        kat = person["kat"]
    res = "%s, лист %s" % (archive["ref"], page)
    st = sublist2title(lst, sublst, kat)
    if st:
        res = "%s - %s" % (st, res)
    return res

def person_list2url(person, lst, sublst):
    return "/lists/%s#person-%s-%s-%s" % (
        list2name(lst),
        person["pageintom"],
        person["nomer"],
        person['rowinpage']
    )

def clean_date(s):
    if not s or s == "0000-00-00" or s == "NULL":
        return None
    return s

def convert_date(s):
    s = clean_date(s)
    if s:
        d = datetime.strptime(s, "%Y-%m-%d")
        s = d.strftime("%d.%m.%Y")
    return s

def get_sorted_lists():
    return sorted(csv_reader(LISTS_CSV), key=lambda lst: (lst['ed_hr'], int(lst['page1'])))
