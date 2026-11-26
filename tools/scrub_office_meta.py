"""Reset author fields in .docx/.xlsx files so no personal name ships with them.

Word and Excel stamp the saving user's name into docProps/core.xml (dc:creator, cp:lastModifiedBy).
Run after any Office save:  python -I tools/scrub_office_meta.py file1.docx file2.xlsx ...
"""
import os, re, shutil, sys, tempfile, zipfile

NAME = "SenseBook founding team"


def scrub(path):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(path)[1])
    tmp.close()
    with zipfile.ZipFile(path) as src, zipfile.ZipFile(tmp.name, "w") as dst:
        for item in src.infolist():
            data = src.read(item.filename)
            if item.filename == "docProps/core.xml":
                x = data.decode("utf-8")
                for tag in ("dc:creator", "cp:lastModifiedBy"):
                    x = re.sub(rf"<{tag}>[^<]*</{tag}>", f"<{tag}>{NAME}</{tag}>", x)
                x = re.sub(r"<cp:lastPrinted>[^<]*</cp:lastPrinted>", "", x)
                data = x.encode("utf-8")
            if item.filename == "docProps/app.xml":
                x = data.decode("utf-8")
                x = re.sub(r"<Company>[^<]*</Company>", "<Company></Company>", x)
                x = re.sub(r"<Manager>[^<]*</Manager>", "", x)
                data = x.encode("utf-8")
            dst.writestr(item, data)
    shutil.move(tmp.name, path)
    with zipfile.ZipFile(path) as z:
        core = z.read("docProps/core.xml").decode("utf-8") if "docProps/core.xml" in z.namelist() else ""
    print(path, "->", re.findall(r"<(dc:creator|cp:lastModifiedBy)>([^<]*)<", core))


if __name__ == "__main__":
    for p in sys.argv[1:]:
        scrub(p)
