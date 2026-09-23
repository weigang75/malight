# -*- coding: utf-8 -*-
"""把待双语的首段摘要压缩成「核心语义」清单，便于作者化英文（一次性脚本）。"""
import ast
import io
import os
import re
import sys

NOTE = re.compile(r"（对应中文版 `[^`]+`）")
NOTE2 = re.compile(r"（[^（）]*对应中文版[^（）]*）")


def first_summary(node):
    doc = ast.get_docstring(node)
    if not doc:
        return None
    cur = []
    for raw in doc.strip().splitlines():
        line = raw.strip()
        if not line:
            break
        cur.append(line)
    if not cur or cur[0].endswith("::"):
        return None
    text = " ".join(" ".join(cur).split())
    return text


seen, out = set(), []
for root, dirs, files in os.walk("malight"):
    dirs[:] = [d for d in dirs if d != "__pycache__"]
    for n in sorted(files):
        if not n.endswith(".py"):
            continue
        path = os.path.join(root, n).replace(os.sep, "/")
        tree = ast.parse(io.open(path, encoding="utf-8").read())
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            items = [("C", node)]
            items += [("m", s) for s in node.body
                      if isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef))
                      and not s.name.startswith("_")]
            for kind, sub in items:
                text = first_summary(sub)
                if not text or " / " in text:
                    continue
                if text in seen:
                    continue
                seen.add(text)
                core = NOTE2.sub("", NOTE.sub("", text)).strip()
                out.append((path, kind, text, core))

sys.stdout.write("### TOTAL %d\n" % len(out))
for path, kind, text, core in out:
    sys.stdout.write("%s\t%s\t%s\n" % (path.replace("malight/", ""), kind, core))
