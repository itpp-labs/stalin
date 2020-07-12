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
    persons_index()
    lists_index()

def persons_index():
    rm_file(PERSONS_INDEX)
    with open(PERSONS_INDEX, "w") as index_file:
        i = 0
        for doc_id, p in yaml_reader_folder(os.path.join(HUGO_DATA_DIR, "persons")):
            i += 1
            if not i % 1000:
                print (doc_id)
            spravki = []
            try:
                spravki = yaml_reader(os.path.join(HUGO_DATA_DIR, "spravki", "%s.yaml" % doc_id))
            except:
                pass

            if spravki:
                spravka_preview = spravki[0]["spravka"][:500].replace("\\t", " ").replace("\n", " ")
            else:
                spravka_preview = ""
            data = {
                "firstname": p["name"]["firstname"],
                "midname": p["name"]["midname"],
                "lastname": p["name"]["lastname"],
                "nameshow": p["name"]["nameshow"],
                "sort": p["name"]["nameshow"],
                "striked": p.get("striked", False),
                "underlined": p.get("underlined", False),
                "pometa": p.get("pometa", False),
                "kat": p.get("kat"),
                "tom": p.get("tom"),
                "geo": p.get("geo_id"),
                "geosub": p.get("geosub_id"),
                "group": p.get("group_id"),
                "lists_date": aggregate_values(p["lists"], lambda r: r["date"]),
                "signstalin": p2sign(p, "stalin"),
                "signmolotov": p2sign(p, "molotov"),
                "signjdanov": p2sign(p, "jdanov"),
                "signkaganovic": p2sign(p, "kaganovic"),
                "signvoroshilov": p2sign(p, "voroshilov"),
                "signmikoyan": p2sign(p, "mikoyan"),
                "signejov": p2sign(p, "ejov"),
                "signkosior": p2sign(p, "kosior"),
                "fond7": ". ".join(p["fond7"]["text_lines"]),
                "gb_spravka_preview": bool(p["gb_spravka"]),
                "spravka_preview": spravka_preview,
                "lists": json_dumps(p["lists"]),
                "spravka": json_dumps([s["spravka"].replace("\t", " ").replace("\n", " ") for s in spravki]),
                "gb_spravka": clean_html(" ".join(data['html'] for data in p["gb_spravka"])),
            }
            content = data2index("persons", doc_id, data)
            index_file.write(content)

def lists_index():
    rm_file(LISTS_INDEX)
    with open(LISTS_INDEX, "w") as index_file:
        for doc_id, r in yaml_reader_folder(os.path.join(HUGO_DATA_DIR, "lists")):
            data = {
                "date": r["date"],
                "title": r["title"],  #globalsearch
                "deloname": r["delo"]["name"],  # globalsearch
                "delonum": r["delo"]["num"],  # globalsearch
                "tom": r["tom"],
                "has_striked": any_person(r, lambda p: p.get("striked")),
                "has_underlined": any_person(r, lambda p: p.get("underlined")),
                "has_pometa": any_person(r, lambda p: p.get("pometa_text")),
                "has_kat1": any_sublist(r, lambda subl: subl["kat1"]),
                "has_kat2": any_sublist(r, lambda subl: subl["kat2"]),
                "has_kat3": any_sublist(r, lambda subl: subl["kat3"]),
                "geo_ids": aggregate_sublists(r, lambda subl: subl["geo_ids"]),
                "geosub_ids": aggregate_sublists(r, lambda subl: subl["geosub_ids"]),
                "group_ids": aggregate_sublists(r, lambda subl: subl["group_ids"]),
                "signstalin": r["signs"].get("stalin", False),
                "signmolotov": r["signs"].get("molotov", False),
                "signjdanov": r["signs"].get("jdanov", False),
                "signkaganovic": r["signs"].get("kaganovic", False),
                "signvoroshilov": r["signs"].get("voroshilov", False),
                "signmikoyan": r["signs"].get("mikoyan", False),
                "signejov": r["signs"].get("ejov", False),
                "signkosior": r["signs"].get("kosior", False),
            }
            content = data2index("lists", doc_id, data)
            index_file.write(content)

def aggregate_sublists(list_data, subl2value):
    res = []
    for subl in list_data["sublists"]:
        res += subl2value(subl)
    return res

def aggregate_values(array, r2value):
    res = []
    for r in array:
        res.append(r2value(r))
    return res

def any_person(list_data, check_person):
    return any(
        any(
            any(
                check_person(p)
                for p in s["persons"]
            )
            for s in page["sublists"]
        )
        for page in list_data["pages"]
    )

def any_sublist(list_data, check):
    return any(
        check(subl)
        for subl in list_data["sublists"]
    )

def any_value(array, check):
    return any(check(r) for r in array)

def p2sign(p, sign_name):
    return any_value(p["lists"], lambda r: r["signs"].get(sign_name))

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

# Credits: https://stackoverflow.com/questions/9662346/python-code-to-remove-html-tags-from-a-string
def clean_html(raw_html):
    if not raw_html:
        return raw_html
    cleanr = re.compile('\t|\n|<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
    cleantext = re.sub(cleanr, ' ', raw_html)
    return cleantext


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
