import csv
# https://github.com/wimglenn/oyaml
# sudo pip3 install oyaml

import oyaml as yaml
#import yaml


class folded_unicode(str): pass
class literal_unicode(str): pass

def folded_unicode_representer(dumper, data):
    return dumper.represent_scalar(u'tag:yaml.org,2002:str', data, style='>')
def literal_unicode_representer(dumper, data):
    return dumper.represent_scalar(u'tag:yaml.org,2002:str', data, style='|')

yaml.add_representer(folded_unicode, folded_unicode_representer)
yaml.add_representer(literal_unicode, literal_unicode_representer)

with open("data/spravki/all.csv", newline="", encoding="utf-8") as csvfile:
    dr = csv.DictReader(csvfile, delimiter=";", fieldnames=("personid", "repryear", "fio", "spravka", "source"))
    line = 0
    for row in dr:
        line += 1
        filename = "hugo/data/spravki/p%s.yaml" % int(row["personid"])
        repryear = row["repryear"]
        if not repryear or repryear == "NULL":
            repryear = None
        data = {
            "id": "all.csv-line-%s" % line,
            "repryear": repryear,
            "fio": row["fio"],
            "source": row["source"],
            "spravka": literal_unicode(row["spravka"].replace("#", "\\n")),
        }
        s = yaml.dump([data], allow_unicode=True)
        s = s.replace(" \\n", "\\n").replace("\\n ", "\n    ").replace("\\n", "\n    ")
        #print (s)
        with open(filename, "a") as yamlfile:
            print ("write", filename)
            yamlfile.write(s)
