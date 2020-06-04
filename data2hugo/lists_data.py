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
    pages_by_id = csv_reader(PAGES_CSV)
    person2page = yaml_reader(PERSON2PAGE_YAML)
    # sublist -> [(PAGE, [PERSON])]
    pages_and_persons_by_sublist = {}
    for sublist, persons in persons_by_sublist.items():
        persons_by_page = x2many(
            lambda p: person2page[p['personid']]['pageid']
            persons
        )
        pages_and_persons_by_sublist[sublist] = [(
            pages_by_id[pageid],
            persons_sublist
        ) for pageid, persons_sublist in persons_by_page.items()]

    pages_by_sublist = x2many(
        lambda r: r["asublistid"],
        csv_reader(PERSONS_CSV),
        lambda r: person2page.get(r["personid"]),

    )

    for lst in csv_reader(LISTS_CSV):
        listtitle = lst["listtitle"]
        data = {
            "title": list2title(lst)
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
                # TODO: debug and make Text\Photo switcher
                {
                    "title": sublist2title(lst, subl),
                    "sublisttitle": subl["sublisttitle"],
                    "pages": [{
                        "page": page,
                        "persons": [{
                            "num": p["nomer"],
                            "name": p["nameshow1"],
                        } for p in persons]
                    } for page, persons in pages_and_persons_by_sublist.get(subl["sublistid"])],
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
