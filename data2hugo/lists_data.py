from common import *

def main():
    persons_by_sublist = x2many(
        lambda r: r["asublistid"],
        csv_reader(PERSONS_CSV)
    )
    sublists_by_list = x2many(
        lambda r: r["alistid"],
        csv_reader(SUBLISTS_CSV)
    )
    pages_by_list = x2many(
        lambda r: r["alistid"],
        csv_reader(PAGES_CSV)
    )
    for lst in csv_reader(LISTS_CSV):
        listtitle = lst["listtitle"]
        data = {
            "delo": {
                "name": lst["deloname"],
                "num": lst["delonum"],
            },
            "pages": [
                {
                    "image": "v%02d/%s" % (int(page["tom"]), page["picturefile"]),
                } for page in pages_by_list[lst["listid"]]
            ],
            "sublists": [
                {
                    "title": subl["sublisttitle"],
                    "persons": [
                        {
                            "num": p["rowinpage"],
                            "name": p["nameshow1"],
                        }
                        for p in persons_by_sublist.get(subl["sublistid"], [])
                    ]
                } for subl in sublists_by_list.get(lst["listid"], [])
            ]
        }
        # data file
        json_writer(
            os.path.join(HUGO_DATA_DIR, "lists", "%s.json" % list2name(lst)),
            data,
        )

if __name__ == "__main__":
    main()
