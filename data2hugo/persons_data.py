from common import *

def main():
    list_by_id = dict(
        (r["listid"], r)
        for r in csv_reader(LISTS_CSV)
    )
    prim_by_person_id = dict(
        (r["personprim"], r["primtext"])
        for r in csv_reader(PRIM_CSV)
    )
    sublist_by_id = dict(
        (r["sublistid"], r)
        for r in csv_reader(SUBLISTS_CSV)
    )

    persons_by_headperson = x2many(
        lambda r: r["headperson"],
        csv_reader(PERSONS_CSV)
    )

    person2pages = yaml_reader(PERSON2PAGE_YAML)
    title2geosub = yaml_reader(TITLE2GEOSUB_YAML)

    def fond7(p):
        res = {
            "deathdate": clean_date(p["deathdate"]),
            "sessiondate": clean_date(p["sessiondate"]),
            "primsud": p["primsud"],
            "primtext": prim_by_person_id.get(p["personid"], ""),
        }
        text_lines = []
        if any(res.values()):
            if res["primtext"]:
                text_lines += res["primtext"].split("\\n")
            elif res["primsud"]:
                text_lines.append("%s" % res["primsud"])
            elif res["sessiondate"]:
                text_lines.append("Дата сессии ВК ВС: %s" % convert_date(res["sessiondate"]))

            if res["deathdate"]:
                text_lines.append("Дата расстрела: %s" % convert_date(res["deathdate"]))
        res["text_lines"] = text_lines
        return res

    for p in csv_reader(PERSONS_CSV):

        if p["personid"] != p["headperson"]:
            # it's a technical record for a person from another record
            continue

        gb_spravka_html = None
        if p.get("spravkafile") and p.get("spravkafile") != "NULL":
            gb_spravka_html = file2str(os.path.join(GB_SPRAVKI_DIR, p.get("spravkafile").lower()))
        data = {
            "name": {
                "firstname": p["firstname1"],
                "midname": p["midname1"],
                "lastname": p["lastname1"],
                "nameshow": p["nameshow1"],
                "primname": p["primname"],
            },
            "kat": int(p["kat"]),
            "tom": int(p["tom"]),
            "geo_id": int(p["ageographyid"]),
            "geosub_id": int(title2geosub.get(p["atitlesid"], "0")),
            "group_id": int(p["agroupid"]),
            # I assume, that this was original columns which were fixed later
            # into firstname1, midname1, etc. But let's keep them just in case
            # -- @yelizariev
            "name_mixed": {
                "firstname": p["firstname"],
                "midlastname": p["midlastname"],
                "nameshow": p["nameshow"],
            },
            "fond7": fond7(p),
            "lists": [
                {
                    "title": sublist2title_full(list_by_id[pp["listnum"]], sublist_by_id[pp["asublistid"]]),
                    "url": person_list2url(pp, list_by_id[pp["listnum"]], sublist_by_id[pp["asublistid"]]),
                    "date": clean_date(list_by_id[pp["listnum"]]["adate"]),
                    "signs": get_signs(list_by_id[pp["listnum"]]),
                } for pp in persons_by_headperson[p["personid"]] if pp["listnum"] != "0"
            ],
            "gb_spravka": {
                "pages": [
                    {
                        "picture": "disk/pictures/v{tom:02d}/{picturefile}".format(
                            tom=int(page['tom']),
                            picturefile=page['picturefile']
                        )
                    } for page in person2pages.get(p['personid'], [])
                ],
                "html": gb_spravka_html,
            },
        }
        data = extend(data,
            striked=any(pp["striked"] == "1" for pp in persons_by_headperson[p["personid"]]),
            underlined=any(pp["underlined"] == "1" for pp in persons_by_headperson[p["personid"]]),
            pometa=any(pp["pometa"] == "1" for pp in persons_by_headperson[p["personid"]])
        )

        # data file
        yaml_writer(
            os.path.join(HUGO_DATA_DIR, "persons", "%s.yaml" % person2name(p)),
            data,
        )

if __name__ == "__main__":
    main()


# fields in persons.csv:
#
#"personid"
#"tom"
#"pageintom"
#"rowinpage"
#"listnum"
#"asublistid"
#"kat"
#"ageographyid"
#"agroupid"
#"atitlesid"
#"nomer"
#"firstname"
#"midlastname"
#"nameshow"
#"doublesexists"
#"headperson"
#"reabspravka"
#"others"
#"add_id"
#"firstlet"
#"metka"
#"deathdate"
#"sessiondate"
#"firstname1"
#"midname1"
#"lastname1"
#"nameshow1"
#"primname"
#"primsud"
#"primwrk"
#"subtitle1"
#"primzv"
#"primcoc"
#"primpb"
#"striked"
#"underlined"
#"pometa"
#"spravkafile"
#"prim"
#"katprim"
#"groupprim"
