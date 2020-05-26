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

with open("db/tables/spravki.csv", newline="", encoding="utf-8") as csvfile:
    dr = csv.DictReader(csvfile)
    for row in dr:
        filename = "db/tables/spravki/p%s.yaml" % row["personid"]
        repryear = row["repryear"]
        if repryear == "NULL":
            repryear = None
        else:
            repryear = int(repryear)
        data = {
            "spravka_old_id": int(row["idspravki"]),
            "repryear": repryear,
            "fio": row["fio"],
            "source": row["source"],
            "spravka": literal_unicode(row["spravka"]),
        }
        s = yaml.dump([data], allow_unicode=True)
        s = s.replace(" \\n", "\\n").replace("\\n ", "\n    ").replace("\\n", "\n    ")
        #print (s)
        with open(filename, "a") as yamlfile:
            yamlfile.write(s)
