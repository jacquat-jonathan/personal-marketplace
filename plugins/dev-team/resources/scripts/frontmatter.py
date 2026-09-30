#!/usr/bin/env python3
"""Read or update one top-level key in a Markdown file's YAML frontmatter, leaving everything else untouched."""
import re
import sys


class NoFrontmatter(Exception):
    pass


def split(text):
    if not text.startswith("---\n"):
        raise NoFrontmatter
    end = text.find("\n---", 3)
    if end == -1:
        raise NoFrontmatter
    body = text[4:end] if end > 3 else ""
    return (body.split("\n") if body else []), text[end:]


def key_pattern(key):
    return re.compile(rf"^{re.escape(key)}:(.*)$")


def get(text, key):
    lines, _ = split(text)
    pattern = key_pattern(key)
    for line in lines:
        match = pattern.match(line)
        if match:
            return re.split(r"\s+#", match.group(1), maxsplit=1)[0].strip()
    return None


def set_value(text, key, value):
    lines, rest = split(text)
    pattern = key_pattern(key)
    new_line = f"{key}: {value}"
    for index, line in enumerate(lines):
        if pattern.match(line):
            lines[index] = new_line
            break
    else:
        lines.append(new_line)
    return "---\n" + "\n".join(lines) + rest


def main(argv):
    usage_ok = len(argv) >= 2 and (
        (argv[1] == "get" and len(argv) == 4) or (argv[1] == "set" and len(argv) == 5)
    )
    if not usage_ok:
        print("usage: frontmatter.py get <file> <key> | set <file> <key> <value>", file=sys.stderr)
        return 1
    command, path, key = argv[1], argv[2], argv[3]
    try:
        with open(path, encoding="utf-8") as handle:
            text = handle.read()
    except OSError as error:
        print(f"ERROR: cannot read {path}: {error.strerror}", file=sys.stderr)
        return 2
    try:
        if command == "get":
            value = get(text, key)
            if value is None:
                print(f"MISSING KEY: {key}", file=sys.stderr)
                return 4
            print(value)
            return 0
        updated = set_value(text, key, argv[4])
    except NoFrontmatter:
        print(f"ERROR: {path} has no frontmatter", file=sys.stderr)
        return 5
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(updated)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
