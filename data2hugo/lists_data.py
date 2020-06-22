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

    def get_page_ref(tom, pageintom):
        return "-".join([tom, pageintom])

    page_by_ref = {}
    for page in csv_reader(PAGES_CSV):
        page_ref = get_page_ref(page['tom'], page['pageintom'])
        page_by_ref[page_ref] = page

    # sublist -> [(PAGE, [PERSON])]
    pages_and_persons_by_sublist = {}
    for sublist, persons in persons_by_sublist.items():
        persons_by_page = x2many(
            lambda r: get_page_ref(r['tom'], r['pageintom']),
            persons
        )
        pages_and_persons_by_sublist[sublist] = [(
            page_by_ref.get(page_ref),
            persons_sublist
        ) for page_ref, persons_sublist in persons_by_page.items()]

    for lst in csv_reader(LISTS_CSV):
        listtitle = lst["listtitle"]
        data = {
            "title": list2title(lst),
            "date": clean_date(lst["adate"]),
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
                        "page_image": "v%02d/%s" % (int(page["tom"]), page["picturefile"]),
                        "persons": [extend_person({
                            "num": p["nomer"],
                            "name": p["nameshow1"],
                        }, p) for p in persons]
                    } for page, persons in pages_and_persons_by_sublist.get(subl["sublistid"], [])],
                } for subl in sublists_by_list.get(lst["listid"], [])
            ]
        }
        # data file
        yaml_writer(
            os.path.join(HUGO_DATA_DIR, "lists", "%s.yaml" % list2name(lst)),
            data,
        )

if __name__ == "__main__":
    main()
