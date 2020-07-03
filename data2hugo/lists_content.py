from common import *

def main():
    for lst in csv_reader(LISTS_CSV):
        data_file = os.path.join(HUGO_DATA_DIR, "lists", "list%s.yaml" % lst["listid"])
        data = yaml_reader(data_file)
        meta = {
            "title": data["title"],
            "description": "%s, лист %s" % (data["archive"]["ref"], data["archive"]["page1"]),
            "images": [
                "/disk/pictures/%s" % p["image"]
                for p in data["pages"][:6]
            ]
        }
        content = "---\n%s---" % yaml.dump(meta, allow_unicode=True)
        file_writer(
            os.path.join(HUGO_CONTENT_DIR, "lists", "%s.md" % list2name(lst)),
            content
        )

if __name__ == "__main__":
    main()
