from common import *

def main():
    for p in csv_reader(PERSONS_CSV):
        content = """---
title: {nameshow1}
---
""".format(**p)
        file_writer(
            os.path.join(HUGO_CONTENT_DIR, "persons", "%s.md" % person2name(p)),
            content
        )

if __name__ == "__main__":
    main()
