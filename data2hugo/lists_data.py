import json
from .common import *

def main():
    persons_by_ = dict(
        (, r)
        for r in csv_reader(PERSONS_CSV)
    )
    sublists_by_list = x2many(
        lambda r: r['alistid'],
        csv_reader(SUBLISTS_CSV)
    )
    for lst in csv_reader(LISTS_CSV):
        listtitle = lst['listtitle']
        data = {
            "delo": {
                "name": lst['deloname'],
                "num": lst['delonum'],
            },
            "pages": [
                {
                    "filename": TODO,
                } for page in TODO
            ]
            "sublists": [
                {
                    "title": subl["sublisttitle"],
                    "persons": [
                        {
                            "name": p['nameshow1']
                        }
                    ] for p in TODO
                } for subl in sublists_by_list(lst['listid'])
            ]
        }
        # data file
        file_writer(
            json.dumps(data),
            os.path.join(HUGO_DATA_DIR, '%s.json' % list2name(record))
        )

def list2page(record):
    return """
# Дело: {deloname}
## {listtitle}
""".format(**record)

if __name__ == '__main__':
    main()
