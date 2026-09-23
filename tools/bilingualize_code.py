# -*- coding: utf-8 -*-
"""
示例代码双语化（bilingualize_code）
===================================

把各模块 ``__main__`` 示例里的**中文注释**与**中文文案**补成
``中文 / English`` 双语对，译文取自 ``tools/code_en.py``。

注入之后：源码里中英并存（谁读都看得懂），而 ``tools/gen_docs.py`` 生成文档
时用 ``tools/bipair.py`` 的同一套规则按语言各取一半，于是中文页与英文页
各自只有一种语言。

Injects the English halves from ``tools/code_en.py`` into the example code, so the
source carries both languages and the docs generator can split them per page.

用法 / Usage::

    python tools/bilingualize_code.py            # 注入（幂等，可反复跑）
    python tools/bilingualize_code.py --check    # 只检查：有未翻译/未配对的片段就退出码 1
    python tools/bilingualize_code.py --list     # 列出示例区里所有含中文的片段
    python tools/bilingualize_code.py path.py    # 只处理名字匹配的模块
"""

from __future__ import print_function

import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import bipair                                              # noqa: E402
from code_en import COMMENT_EN, STRING_EN                  # noqa: E402

MARKS = ('if __name__ == "__main__":', 'if __name__ == "__main__" and not __package__:')


def read(path):
    return io.open(path, encoding="utf-8", newline="").read()


def save(path, text):
    io.open(path, "w", encoding="utf-8", newline="").write(text)


def demo_start(src):
    """
    返回示例区（最后一个 ``__main__`` 块）在源码里的下标；没有则返回 -1。

    取**最后**一个：包内文件开头常有「直接运行引导」块，它同样是
    ``if __name__ == "__main__" ...``，但不是示例。
    """
    idx = -1
    for mark in MARKS:
        pos = src.rfind(mark)
        idx = max(idx, pos)
    return idx


def inject_line(line, missing):
    """处理一行：给中文注释与中文字符串补上英文半边。"""
    comment_at, strings = bipair.scan_line(line)
    code = line if comment_at < 0 else line[:comment_at]
    tail = "" if comment_at < 0 else line[comment_at:]
    changed = 0

    # 1) 字符串字面量（从右往左，避免下标错位）
    for start, end, quote in reversed(strings):
        inner = code[start:end]
        if not bipair.has_cjk(inner) or bipair.is_paired(inner):
            continue
        english = STRING_EN.get(inner)
        if english is None:
            missing.append(("S", inner))
            continue
        if quote in english or english.endswith("\\"):
            missing.append(("S!", inner))                  # 英文里含同款引号，需手工
            continue
        code = code[:start] + inner + bipair.SEP + english + code[end:]
        changed += 1

    # 2) 注释
    if tail:
        body = tail[1:]
        newline = "\n" if body.endswith("\n") else ""
        text = body[:-1] if newline else body
        stripped = text.strip()
        if bipair.has_cjk(stripped) and not bipair.is_paired(stripped):
            english = COMMENT_EN.get(stripped)
            if english is None:
                missing.append(("C", stripped))
            else:
                lead = text[:len(text) - len(text.lstrip())]
                body = lead + stripped + bipair.SEP + english + newline
                changed += 1
        tail = "#" + body

    return code + tail, changed


def process(path, rel, check=False, list_only=False):
    """处理一个文件，返回 ``(改动数, 缺失列表)``。"""
    src = read(path)
    idx = demo_start(src)
    if idx < 0:
        return 0, []
    head, tail = src[:idx], src[idx:]
    out, changed, missing = [], 0, []
    for line in tail.splitlines(True):
        if list_only:
            at, frags = bipair.scan_line(line)
            for start, end, _q in frags:
                inner = line[start:end]
                if bipair.has_cjk(inner):
                    print("  %s:%s S %s" % (rel, "已" if bipair.is_paired(inner) else "缺", inner[:80]))
            if at >= 0:
                text = line[at + 1:].strip()
                if bipair.has_cjk(text):
                    print("  %s:%s C %s" % (rel, "已" if bipair.is_paired(text) else "缺", text[:80]))
            out.append(line)
            continue
        new_line, count = inject_line(line, missing)
        out.append(new_line)
        changed += count

    if list_only:
        return 0, []

    body = head + "".join(out)
    if changed and not check:
        try:
            compile(body, path, "exec")                    # 改坏了就别写盘
        except SyntaxError as exc:
            print("!! 注入后语法错误，未写入：%s -> %s" % (rel, exc))
            return 0, missing
        save(path, body)
    return changed, missing


def main(argv):
    check = "--check" in argv
    list_only = "--list" in argv
    filters = [a for a in argv if not a.startswith("--")]

    files = []
    for root, dirs, names in os.walk(os.path.join(ROOT, "malight")):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for name in sorted(names):
            if name.endswith(".py"):
                files.append(os.path.join(root, name))

    total, all_missing = 0, []
    for path in files:
        rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
        if filters and not any(f in rel for f in filters):
            continue
        changed, missing = process(path, rel, check, list_only)
        if changed:
            print("%-44s %s %d 处" % (rel, "待改" if check else "已改", changed))
        total += changed
        all_missing += [(rel, kind, text) for kind, text in missing]

    if check:
        print("\n共 %d 处待双语化，%d 条译文缺失" % (total, len(all_missing)))
        for rel, kind, text in all_missing:
            print("   缺[%s] %s  <%s>" % (kind, text[:70], rel))
        return 1 if (total or all_missing) else 0
    if list_only:
        return 0
    print("\n共双语化 %d 处" % total)
    if all_missing:
        print("译文缺失 %d 条（补进 tools/code_en.py 后重跑）：" % len(all_missing))
        for rel, kind, text in all_missing:
            print("   [%s] %s   <%s>" % (kind, text, rel))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
