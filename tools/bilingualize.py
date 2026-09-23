# -*- coding: utf-8 -*-
"""
文档字符串双语化（bilingualize）
===============================

把 ``malight`` 源码里**类与公开方法**的文档字符串首段变成「中文 / English」
形式，英文取自 :mod:`tools.glossary` 的术语表。

规则 / Rules:
    1. 只在首段的**第一个句号之后**插入 `` / English``，不改动原有中文，
       也不改变行结构（多行段落只在句号所在行追加）；
    2. 已经是双语的（首段同时含 `` / `` 与中文）自动跳过，可反复运行；
    3. 单行文档字符串 ``\"\"\"包围盒。\"\"\"`` 变成
       ``\"\"\"包围盒。 / Bounding box.\"\"\"``；
    4. 术语表里查不到的首段会被列出来（不报错），补进 glossary 再跑即可。

用法 / Usage::

    python tools/bilingualize.py            # 应用并报告
    python tools/bilingualize.py --dry-run  # 只看缺哪些词条，不改文件
"""

from __future__ import print_function

import ast
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from glossary import GLOSSARY, MODULE_EN                       # noqa: E402

# 「（…对应中文版…）」这类迁移提示：只是给中文读者的对照说明，英文摘要不重复它
NOTE = re.compile(r"（[^（）]*对应中文版[^（）]*）")
HAN = re.compile(r"[\u4e00-\u9fff]")
QUOTES = ('"""', "'''")


def read(path):
    return io.open(path, encoding="utf-8", newline="").read()


def save(path, text):
    io.open(path, "w", encoding="utf-8", newline="").write(text)


def docstring_span(lines, node):
    """
    返回文档字符串正文的定位信息。

    :return: ``(首行号, 首行起始列, 末行号, 末行结束列)``；没有文档字符串时 None
    """
    if not node.body:
        return None
    first = node.body[0]
    if not isinstance(first, ast.Expr) or not isinstance(first.value, ast.Constant):
        return None
    if not isinstance(first.value.value, str):
        return None
    left, right = first.lineno - 1, first.end_lineno - 1
    head = lines[left]
    quote = None
    for q in QUOTES:
        if q in head:
            quote = q
            break
    if quote is None:
        return None
    start = head.find(quote)
    if left == right:
        end = head.rfind(quote)
        if end <= start:
            return None
        return left, start + 3, left, end
    end = lines[right].rfind(quote)
    if end < 0:
        return None
    return left, start + 3, right, end


def body_segments(lines, span):
    """把文档字符串正文拆成 ``[(行号, 起始列, 结束列), ...]``。"""
    left, cs, right, ce = span
    if left == right:
        return [(left, cs, ce)]
    out = [(left, cs, len(lines[left].rstrip("\r\n")))]
    for k in range(left + 1, right):
        out.append((k, 0, len(lines[k].rstrip("\r\n"))))
    out.append((right, 0, ce))
    return out


def first_paragraph(lines, span):
    """
    返回首段的 ``(折叠文本, 段落内的行片段)``。

    段落 = 从正文开头到第一个空行为止（跳过正文起始的空行）。
    """
    segs = body_segments(lines, span)
    para, started = [], False
    for ln, cs, ce in segs:
        text = lines[ln][cs:ce]
        if not text.strip():
            if started:
                break
            continue
        started = True
        para.append((ln, cs, ce, text))
    if not para:
        return None, []
    joined = " ".join(t for _, _, _, t in para)
    return " ".join(joined.split()), para


def make_key(text):
    """
    把首段文本归一成术语表的键。

    会去掉「（…对应中文版…）」这类迁移提示，以及 ``示例::`` 之后的示例代码，
    这样术语表里写完整首段或只写核心句都能匹配上。
    """
    key = NOTE.sub("", text)
    key = key.split("示例::")[0]
    return " ".join(key.split()).strip()


def build_index():
    """把术语表归一成 ``{归一化键: 英文}``，并顺手报告冲突。"""
    index, clash = {}, []
    for raw, english in GLOSSARY.items():
        key = make_key(raw)
        if key in index and index[key] != english:
            clash.append(key)
        index[key] = english
    return index, clash


GLOSSARY_INDEX, CLASH = build_index()


def is_bilingual(text):
    """
    首段是否已经是「中文。 / English.」形式。

    判据用 ``"。 / "``（脚本自己的插入格式）而不是泛指 ``" / "``，
    否则 ``alignment-baseline / dominant-baseline`` 这类斜杠会被误判。
    """
    return "。 / " in text


def plan_insert(para):
    """
    定位插入点：段落里**最后一个句号**之后。

    段落含 ``示例::`` 时只在其之前找句号，避免英文被插到示例代码后面。
    之所以用「最后一个句号」而不是第一个：术语表是按整个首段归一的，
    英文摘要覆盖的也是整段，插在第一个句号后会与后半句中文重复。

    :return: ``(行号, 插入列)``；找不到句号时返回 None
    """
    flat = []
    for ln, cs, _ce, text in para:
        for i, ch in enumerate(text):
            flat.append((ln, cs + i, ch))
    if not flat:
        return None
    joined = "".join(c for _, _, c in flat)
    limit = joined.find("示例::")
    if limit < 0:
        limit = len(flat)
    for k in range(limit - 1, -1, -1):
        if flat[k][2] == "。":
            return flat[k][0], flat[k][1] + 1
    return None


def apply_module(lines, tree, rel):
    """
    把 :data:`tools.glossary.MODULE_EN` 里的英文插进模块文档字符串。

    · 标题带 ``====`` 下划线的模块 -> 英文单独成段，插在下划线之后；
    · 普通模块 -> 追加到标题行末尾，形成「中文标题 / English title」。

    :return: ``(改动处数, 跳过原因)``；成功时原因字段为 None
    """
    english = MODULE_EN.get(rel)
    if not english:
        return 0, "未登记"
    if not tree.body:
        return 0, "空模块"
    first = tree.body[0]
    if not (isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant)
            and isinstance(first.value.value, str)):
        return 0, "无模块文档字符串"
    left, right = first.lineno - 1, first.end_lineno - 1
    if english in "".join(lines[left:right + 1]):
        return 0, "已是双语"
    if left == right:
        return 0, "单行模块文档字符串"
    title = left + 1
    underline = title + 1
    mark = lines[underline].strip() if underline <= right else ""
    if len(mark) >= 4 and set(mark) == {"="}:
        # 下划线后留空行再写英文，保持「标题 / 下划线 / 英文摘要 / 正文」的层次
        lines.insert(underline + 1, "\n" + english + "\n")
    else:
        lines[title] = lines[title].rstrip("\r\n") + " / " + english + "\n"
    return 1, None


def apply_to_file(path, rel, dry_run=False):
    """
    处理一个文件的模块级与类/方法级文档字符串。

    :return: ``(改动处数, 缺失词条的键列表)``
    """
    lines = read(path).splitlines(True)
    tree = ast.parse("".join(lines))
    mod_changed, _skipped = apply_module(lines, tree, rel)
    if mod_changed:
        tree = ast.parse("".join(lines))

    targets = []
    # 模块级函数（工具函数、几何算法等）也要覆盖 —— 曾经只走 ast.walk
    # 遍历类与类方法，于是 tools.py 这类「函数为主」的模块整片漏掉，
    # 英文页的 API 表只能回退显示中文。
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not node.name.startswith("_"):
                targets.append(node)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            targets.append(node)
            for sub in node.body:
                if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if not sub.name.startswith("_"):
                        targets.append(sub)
    targets.sort(key=lambda n: (n.lineno, n.col_offset), reverse=True)

    missing, changed = [], mod_changed
    for node in targets:
        span = docstring_span(lines, node)
        if span is None:
            continue
        text, para = first_paragraph(lines, span)
        if not text or is_bilingual(text):
            continue
        key = make_key(text)
        english = GLOSSARY_INDEX.get(key)
        if english is None:
            missing.append(key)
            continue
        spot = plan_insert(para)
        if spot is None:
            missing.append("（首段无句号）" + key)
            continue
        ln, col = spot
        line = lines[ln]
        # 句号后紧跟中文时补一个空格，避免中英粘连
        tail = line[col:]
        gap = "" if (not tail or tail[0] in " \t\r\n") else " "
        lines[ln] = line[:col] + " / " + english + gap + line[col:]
        changed += 1

    if changed and not dry_run:
        save(path, "".join(lines))
    return changed, missing


def main(argv):
    dry = "--dry-run" in argv
    files, total, all_missing = [], 0, []
    for root, dirs, names in os.walk(os.path.join(ROOT, "malight")):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for n in sorted(names):
            if n.endswith(".py"):
                files.append(os.path.join(root, n))
    for path in files:
        rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
        changed, missing = apply_to_file(path, rel, dry)
        if changed:
            print("%-42s %s %d 处" % (rel, "将修改" if dry else "已改", changed))
        total += changed
        all_missing += [(rel, m) for m in missing]

    print("\n合计%s %d 处" % ("将修改" if dry else "已修改", total))
    uniq = {}
    for rel, m in all_missing:
        uniq.setdefault(m, []).append(rel)
    print("术语表缺失 %d 条" % len(uniq))
    for m, where in sorted(uniq.items()):
        print("  - %s   <%s>" % (m[:80], where[0]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
