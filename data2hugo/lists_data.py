from common import *
import os.path
import re
import itertools


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


    # pageid -> sublistid -> [PERSON]
    sublists_and_persons_by_page = {}
    for p in csv_reader(PERSONS_CSV):
        page_ref = get_page_ref(p['tom'], p['pageintom'])
        page = page_by_ref.get(page_ref)
        pageid = page["pageid"]
        sublistid = p["asublistid"]
        sublists_and_persons_by_page.setdefault(pageid, {})
        sublists_and_persons_by_page[pageid].setdefault(sublistid, [])
        sublists_and_persons_by_page[pageid][sublistid].append(p)

    others_by_person = x2many(
        lambda r: r["person"],
        csv_reader(OTHERS_CSV)
    )
    id2pometa_text = dict(
        (r["pometaid"], r["pometatext"])
        for r in csv_reader(POMETY_CSV)
    )
    id2listtitl = dict(
        (r["textid"], r["textcaption"])
        for r in csv_reader(LIST_TITLE_CSV)
    )

    id2sublist = dict(
        (r["sublistid"], r)
        for r in csv_reader(SUBLISTS_CSV)
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

    def p2name(p, lst):
        name = p["nameshow1"]
        if lst["listid"] not in ["410", "413"]:
            return name
        name = name.split(" ")
        name.insert(1, "<br/>")
        return " ".join(name)

    def html_classes(red=False, underlined=False):
        res = []
        if red:
            res.append("red-text")
        if underlined:
            res.append("underlined-text")
        if not res:
            return ""
        res.insert(0, "")  # add a space in beginning
        return " ".join(res)

    def html_left(html):
        if not html:
            return ""
        return '<p>%s</p>' % html

    # helpers use bulma classes. See https://bulma.io/documentation/helpers/typography-helpers/
    def html_center(html, **kwargs):
        if not html:
            return ""
        return '<p class="has-text-centered%s">%s</p>' % (html_classes(**kwargs), html)

    def html_right(html, **kwargs):
        if not html:
            return ""
        return '<p class="has-text-right%s">%s</p>' % (html_classes(**kwargs), html)

    def generate_page_html(lst, page):
        # see https://github.com/itpp-labs/stalin/issues/76
        html = ""
        if page["pagekind"] == "2":
            # it's a title page
            html += html_center(id2listtitl.get(lst["toptext"]))
            html += html_center(id2listtitl.get(lst["centertext"]))
            html += html_right(lst["datetext"])
            html += html_center(id2pometa_text.get(page["pometa"]), red=True)
            html += html_center(lst["politsigns"], red=True)
        if page["pagekind"] == "3":
            # it's a list spravka
            html += html_center("СПРАВКА", underlined=True)

            lines = ""
            LINE_HTML="""
<div class="columns is-mobile">
  <div class="column is-half has-text-right">{sublisttitle}</div>
  {categories}
</div>
                """
            kats = {}
            for sublist in sublists_by_list.get(lst["listid"], []):
                for kat in ["1", "2", "3"]:
                    if sublist["kat" + kat] == "1":
                        kats[kat] = True

            for sublist in sublists_by_list.get(lst["listid"], []):

                categories = ""
                total = 0
                for kat in ["1", "2", "3"]:
                    kat_count = None
                    if sublist["kat" + kat] == "1":
                        kat_count = sublist["kat" + kat + "count"]
                        total += int(kat_count)
                    elif kats.get(kat):
                        kat_count = "-"

                    if kat_count:
                        categories += """<div class="column">%s</div>""" % kat_count

                categories += """<div class="column">%s</div>""" % total

                lines += LINE_HTML.format(sublisttitle=sublist["sublisttitle"], categories=categories)

            categories = ""
            for kat in ["1", "2", "3"]:
                if not kats.get(kat):
                    # we guess that there is no such column
                    continue
                categories += """<div class="column underlined-text">%s-я кат.<br/><br/></div>""" % kat
            categories += """<div class="column underlined-text">ВСЕГО<br/><br/></div>"""
            html += LINE_HTML.format(sublisttitle="&nbsp;<br/><br/>", categories=categories)
            html += lines

        # Other pagekinds are:
        # 1 - spisok
        # 4 - person spravka
        # 5 - spisok with signature
        # 6 - zapiska
        # 7 - opis'
        #
        # To get page examples use command
        #
        # mlr --csv cut -f "tom,pagekind,picturefile" data/db/tables/pages.csv|less


        return html

    def get_page_html(lst, page):
        textfile = page["textfile"]
        if not textfile or textfile == "NULL":
            return generate_page_html(lst, page)

        try:
            html = file2str(os.path.join(GB_SPRAVKI_DIR, textfile.lower()))
        except:
            # see https://github.com/itpp-labs/stalin/issues/66
            print ("file not found", textfile)
            return

        html = re.sub("<HEAD>.*?</HEAD>", "", html, flags=re.DOTALL)
        html = re.sub("<HEAD>", "", html, flags=re.IGNORECASE)
        html = re.sub("<HTML>", "", html, flags=re.IGNORECASE)
        html = re.sub("</HTML>", "", html, flags=re.IGNORECASE)
        html = re.sub("<BODY>", "", html, flags=re.IGNORECASE)
        html = re.sub("</BODY>", "", html, flags=re.IGNORECASE)

        for persons in sublists_and_persons_by_page.get(page["pageid"], {}).values():
            for p in persons:
                query = r"([0-9]*\.\s*(<b><u>)?%s)" % p["lastname1"]
                html = re.sub(query, r"PERSON%s<br/>\1" % p["headperson"], html, flags=re.IGNORECASE)
        return html


    sublist_title = {
        r["sublistid"]: r["sublisttitle"]
        for r in csv_reader(SUBLISTS_CSV)
    }

    class Page2Title():
        def __init__(self):
            self.prev = None
        def __call__(self, page):
            first = None
            first_person = None
            last = None
            for sublistid, persons in sublists_and_persons_by_page.get(page["pageid"], {}).items():
                if not first:
                    first = sublistid
                    first_person = persons[0]
                last = sublistid

            prev = self.prev
            self.prev = last

            if not first:
                return None

            # e.g. <p align="right"><u>3-я категория.</u></p><p align="center"><u>КРАСНОЯРСКИЙ КРАЙ.</u>
            page_starts_with_title =  first_person and "center" in first_person["subtitle1"]
            if prev != first or page_starts_with_title:
                return None
            return sublist_title.get(first)

    page2title = Page2Title()

    all_lists = get_sorted_lists()
    all_lists = itertools.chain(all_lists, iter([None]))

    prev_lst = None
    lst = None
    next_lst = next(all_lists)
    for lst_ in all_lists:
        prev_lst = lst
        lst = next_lst
        next_lst = lst_

        listtitle = lst["listtitle"]

        has_primzv = False
        for subl in sublists_by_list.get(lst["listid"], []):
            if has_primzv:
                break
            for p in persons_by_sublist.get(subl["sublistid"], []):
                if p["primzv"]:
                    has_primzv = True
                    break
        prev_id = None
        if prev_lst and prev_lst["ed_hr"] == lst["ed_hr"]:
            prev_id = prev_lst["listid"]
        next_id = None
        if next_lst and next_lst["ed_hr"] == lst["ed_hr"]:
            next_id = next_lst["listid"]

        data = {
            "id": lst["listid"],
            "prev_id": prev_id,
            "next_id": next_id,
            "title": list2title(lst),
            "archive": list2archive(lst),
            "date": clean_date(lst["adate"]),
            "date_ru": convert_date(lst["adate"]),
            "tom": int(lst["tom"]),
            "delo": {
                "name": lst["deloname"],
                "num": lst["delonum"],
            },
            "signs": get_signs(lst),
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
                } for subl in sublists_by_list.get(lst["listid"], [])
            ],
            "pages": [
                extend({
                    "pageintom": page["pageintom"],
                    "image": "v%02d/%s" % (int(page["tom"]), page["picturefile"]),
                    "title": page2title(page),
                    "sublists": [
                        {
                            "sublid": sublistid,
                            "persons": [extend(
                                {
                                    "id": p["headperson"],
                                    "num": p["nomer"],
                                    "name": p2name(p, lst),
                                },
                                rowinpage=p['rowinpage'],
                                striked=p["striked"] == "1",
                                underlined=p["underlined"] == "1",
                                pometa_text=person2pometa_text(p),
                                primzv=p["primzv"],
                                primcoc=p["primcoc"],
                                doublesexists=p["doublesexists"] == "1",
                                gb_spravka=person2gb_spravka[p["personid"]],
                                spravka=os.path.isfile("hugo/data/spravki/p%s.yaml" % p["headperson"]),
                                subtitle1=p["subtitle1"],
                            ) for p in persons]
                        } for sublistid, persons in sublists_and_persons_by_page.get(page["pageid"], {}).items()
                    ],
                }, html=get_page_html(lst, page))
                for page in pages_by_list[lst["listid"]]
            ],
        }
        has_textfile = False
        for page in pages_by_list[lst["listid"]]:
            if page["textfile"]:
                has_textfile = True
                break

        extend(
            data,
            two_columns=has_primzv,
            name_align_center=lst["listid"] in ["410", "413"],
            html=has_textfile,
        )

        # data file
        yaml_writer(
            os.path.join(HUGO_DATA_DIR, "lists", "%s.yaml" % list2name(lst)),
            data,
        )

if __name__ == "__main__":
    main()
