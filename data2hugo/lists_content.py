from common import *

def main():
    for lst in csv_reader(LISTS_CSV):
        content = """
---
title: Дело №{title}
---
""".format(title=lst['delonum'])
        file_writer(
            os.path.join(HUGO_CONTENT_DIR, "lists", "%s.md" % list2name(lst)),
            content
        )

if __name__ == "__main__":
    main()
