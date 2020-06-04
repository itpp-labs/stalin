from common import *
import os
import os.path
import re


def main():
    html2page = dict(
        (r["textfile"].lower(), r)
        for r in csv_reader(PAGES_CSV)
    )
    person2page = {}
    for p in csv_reader(PERSONS_CSV):
        html = p["spravkafile"]
        if html == "NULL" or not html:
            continue
        html = html.lower()
        pages = []
        page = html2page.get(html)
        if page:
            pages.append(page)
        if not pages:
            name = p["nameshow1"]
            files = grep(name)
            print("Search page by name:", html, name, files)
            for filename in files:
                page = html2page.get(filename)
                if page:
                    print ("Found: ", filename)
                    pages.append(page)
        if pages:
            person2page[p["personid"]] = pages
    yaml_writer("data2hugo/person2page.yaml", person2page)



HTML_DIR = "data/disk/vkvs/z3/spravki"
def grep(s):
    res = []
    for filename in os.listdir(HTML_DIR):
        with open(os.path.join(HTML_DIR, filename), "r", encoding="cp1251") as f:
            for line in f:
                if re.search(s, line, flags=re.IGNORECASE):
                    res.append(filename)
                    break
    return res



if __name__ == "__main__":
    main()

