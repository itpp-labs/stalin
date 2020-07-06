from common import *
import os.path

def main():
    title2geosub = yaml_reader(TITLE2GEOSUB_YAML)
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
    def p2nomer(p):
        nomer = p['nomer'] or 0
        if nomer == "NULL":
            nomer = 0
        return int(nomer)

    for sublist, persons in persons_by_sublist.items():
        persons = sorted(persons, key=lambda p: (int(p['pageintom']), p2nomer(p)))
        persons_by_page = x2many(
            lambda r: get_page_ref(r['tom'], r['pageintom']),
            persons
        )
        pages_and_persons_by_sublist[sublist] = [(
            page_by_ref.get(page_ref),
            persons_sublist
        ) for page_ref, persons_sublist in persons_by_page.items()]

    others_by_person = x2many(
        lambda r: r["person"],
        csv_reader(OTHERS_CSV)
    )
    id2pometa_text = dict(
        (r["pometaid"], r["pometatext"])
        for r in csv_reader(POMETY_CSV)
    )

    def person2pometa_text(p):
        other = others_by_person.get(p["personid"])
        if not other:
            return None
        # there is only one record per person
        other = other[0]
        pometa_id = other["pometa"]
        return id2pometa_text.get(pometa_id)

    person2gb_spravka = {}
    for p in csv_reader(PERSONS_CSV):
        person2gb_spravka[p["personid"]] = p.get("spravkafile") and p.get("spravkafile") != "NULL"

    def subl2person_values(subl, p2value):
        sublistid = subl["sublistid"]
        persons = persons_by_sublist.get(sublistid, [])
        values = set()
        for p in persons:
            values.add(p2value(p))

        return list(values)

    for lst in csv_reader(LISTS_CSV):
        listtitle = lst["listtitle"]
        data = {
            "id": lst["listid"],
            "title": list2title(lst),
            "archive": list2archive(lst),
            "date": clean_date(lst["adate"]),
            "tom": int(lst["tom"]),
            "delo": {
                "name": lst["deloname"],
                "num": lst["delonum"],
            },
            "signs": get_signs(lst),
            "pages": [
                {
                    "image": "v%02d/%s" % (int(page["tom"]), page["picturefile"]),
                } for page in pages_by_list[lst["listid"]]
            ],
            "sublists": [
                {
                    "title": sublist2title(lst, subl),
                    "listtitle": lst["listtitle"],
                    "sublisttitle": subl["sublisttitle"],
                    "kat1": subl["kat1"] == "1",
                    "kat2": subl["kat2"] == "1",
                    "kat3": subl["kat3"] == "1",
                    "geo_ids": subl2person_values(subl, lambda p: int(p["ageographyid"])),
                    "geosub_ids": subl2person_values(subl, lambda p: int(title2geosub.get(p["atitlesid"], "0"))),
                    "group_ids": subl2person_values(subl, lambda p: int(p["agroupid"])),
                    "pages": [{
                        "page": page,
                        "page_image": "v%02d/%s" % (int(page["tom"]), page["picturefile"]),
                        "persons": [extend(
                            {
                                "id": p["headperson"],
                                "num": p["nomer"],
                                "name": p["nameshow1"],
                            },
                            striked=p["striked"] == "1",
                            underlined=p["underlined"] == "1",
                            pometa_text=person2pometa_text(p),
                            doublesexists=p["doublesexists"] == "1",
                            gb_spravka=person2gb_spravka[p["personid"]],
                            spravka=os.path.isfile("hugo/data/spravki/p%s.yaml" % p["headperson"]),
                        ) for p in persons]
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
