#!/usr/bin/env python3
"""Print the text of HTML elements by id, so agents can read only the sections they need."""
import sys
from html.parser import HTMLParser

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
BLOCK = {"p", "div", "section", "article", "h1", "h2", "h3", "h4", "h5", "h6", "li", "tr", "pre", "table", "ul", "ol", "blockquote"}
CELL = {"td", "th"}


class SectionParser(HTMLParser):
    def __init__(self, wanted):
        super().__init__(convert_charrefs=True)
        self.wanted = set(wanted)
        self.found = {}
        self.depth = {}

    def handle_starttag(self, tag, attrs):
        if tag in VOID:
            if tag == "br":
                self._emit("\n")
            return
        for key in self.depth:
            self.depth[key] += 1
        element_id = dict(attrs).get("id")
        if element_id in self.wanted and element_id not in self.found:
            self.found[element_id] = []
            self.depth[element_id] = 1
        if tag in BLOCK:
            self._emit("\n")
        if tag == "li":
            self._emit("- ")
        elif tag in CELL:
            self._emit(" | ")

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if tag in BLOCK:
            self._emit("\n")
        for key in list(self.depth):
            self.depth[key] -= 1
            if self.depth[key] == 0:
                del self.depth[key]

    def handle_data(self, data):
        self._emit(data)

    def _emit(self, text):
        for key in self.depth:
            self.found[key].append(text)


def normalize(text):
    lines = (" ".join(line.split()) for line in text.split("\n"))
    return "\n".join(line for line in lines if line)


def extract(html, ids):
    parser = SectionParser(ids)
    parser.feed(html)
    parser.close()
    return {key: normalize("".join(parts)) for key, parts in parser.found.items()}


def main(argv):
    if len(argv) < 3:
        print("usage: section.py <file.html> <id> [<id>...]", file=sys.stderr)
        return 1
    path, ids = argv[1], argv[2:]
    try:
        with open(path, encoding="utf-8") as handle:
            html = handle.read()
    except OSError as error:
        print(f"ERROR: cannot read {path}: {error.strerror}", file=sys.stderr)
        return 2
    sections = extract(html, ids)
    for key in ids:
        if key in sections:
            print(f"## {key}\n{sections[key]}\n")
    missing = [key for key in ids if key not in sections]
    for key in missing:
        print(f"MISSING: {key}", file=sys.stderr)
    return 3 if missing else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
