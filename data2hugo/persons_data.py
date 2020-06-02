from common import *

def main():
    person2pages = yaml_reader(PERSON2PAGE_YAML)
    for p in csv_reader(PERSONS_CSV):

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
            # I assume, that this was original columns which were fixed later
            # into firstname1, midname1, etc. But let's keep them just in case
            # -- @yelizariev
            "name_mixed": {
                "firstname": p["firstname"],
                "midlastname": p["midlastname"],
                "nameshow": p["nameshow"],
            },
            "lists": ["TODO"],
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
