from common import *

def main():
    for p in csv_reader(PERSONS_CSV):
        if p["personid"] != p["headperson"]:
            # it's a technical record for a person from another record
            continue

        data_file = os.path.join(HUGO_DATA_DIR, "persons", "p%s.yaml" % p["personid"])
        data = yaml_reader(data_file)
        spravki_file = os.path.join(HUGO_DATA_DIR, "spravki", "p%s.yaml" % p["personid"])
        spravki = []
        try:
            spravki = yaml_reader(spravki_file)
        except:
            pass
        name = data["name"]["nameshow"]
        name = name.replace("<br />", " ").replace("<br/>", " ")
        meta = {
            "title": name
        }
        if spravki:
            meta["description"] = spravki[0]["spravka"].replace("\t", " ").replace("\\n", " ")
        content = "---\n%s---" % yaml.dump(meta, allow_unicode=True)
        file_writer(
            os.path.join(HUGO_CONTENT_DIR, "persons", "%s.md" % person2name(p)),
            content
        )

if __name__ == "__main__":
    main()
