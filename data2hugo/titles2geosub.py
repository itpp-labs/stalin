# Computes following structure out of titles.csv
#
# [[geo_id, title, geosub_id, title_id]]
#
# * geo_id is ageographyid (the same as "regionid" in geogr.csv)
# * title is "sublisttitle//subgeogroup""
# * geosub_id is a new id assigned by this script. Unique for geo_id+title
# * title_id - original id
#
# Output files:
#
# * geosub.json: geo_id -> {geosub_id -> title}
# * title2geosub.yaml: title_id -> geosub_id

from common import *
import os
import os.path
import re


def main():
    records = []
    geosub_index = {}
    next_id = 1
    for t in csv_reader(TITLES_CSV):
        geo_id = t["ageographyid"]
        title = t["sublisttitle"]
        if t["subgeogroup"]:
            title += " // " + t["subgeogroup"]

        code = "%s:%s" % (geo_id, fix_title(title))
        geosub_id = geosub_index.get(code)
        if not geosub_id:
            geosub_id = next_id
            next_id = next_id + 1
            geosub_index[code] = geosub_id

        title_id = t['titleid']
        records.append([geo_id, title, geosub_id, title_id])

    print ("geosub num:", next_id-1)
    # geosub.json
    geosub_data = {}
    title2geosub_data = {}
    for geo_id, title, geosub_id, title_id in records:
        title2geosub_data[title_id] = geosub_id
        geosub_data.setdefault(geo_id, {})
        geosub_data[geo_id][geosub_id] = fix_title(title)

    yaml_writer("data2hugo/title2geosub.yaml", title2geosub_data)
    json_writer("data2hugo/geosub.json", geosub_data, sort_keys=True, indent=4)

# TODO
SYNONYMS = [
    [
        "Украинская ССР // Харьков - Южная жел.дор.",
        "г.Харьков // ДТО Южных жел.дор.",
        "г.Харьков - Южная жел.дорога",
        "Гор.Харьков.-Южная жел.дор.",
        "Гор.Харьков. Южная жел.дор.",
        "г.Харьков. Южная жел.дор."
    ]
]


def fix_title(code):
    for g in SYNONYMS:
        if code in g:
            return g[0]
    return code

if __name__ == "__main__":
    main()

