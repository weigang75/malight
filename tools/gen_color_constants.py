# -*- coding: utf-8 -*-
"""
颜色常量显式化（gen_color_constants）
=====================================

`Color` 类原来用一行 ``locals().update({en.upper(): v for en, v in
_ENGLISH_NAMES.items()})`` 动态生成 138 个颜色常量。运行时没问题，但
**PyCharm 的静态分析看不见动态写入的属性** —— ``Color.`` 后面敲不出补全，
``Color.BLACK`` 会被标成 "Unresolved attribute reference"，颜色名写错也
没有红线。用户在 PyCharm 里的体验直接掉一档。

本工具把这段动态生成改成**显式类属性块**（``BLACK = "#000000"`` 一行一个），
写成静态可分析的形式，补全和检查立刻恢复。

单一口径：颜色数据仍然只写在 ``malight/definitions.py`` 的 ``_COLOR_TABLE``
里（中文名 -> 英文明 + 十六进制），本工具只是把它展开。手改生成块会被
``--check`` 判为不同步，所以不会出现「表改了常量没改」的静默漂移。

用法 / Usage::

    python tools/gen_color_constants.py           # 就地重写生成块
    python tools/gen_color_constants.py --check   # 只检查是否同步（回归用，退出码 0/1）
"""

from __future__ import print_function

import ast
import io
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

TARGET = os.path.join(ROOT, "malight", "definitions.py")

BEGIN = "    # >>> gen_color_constants: begin (generated, do not edit by hand)"
END = "    # <<< gen_color_constants: end"


def read_table(path=TARGET):
    """
    用 AST 读 `_COLOR_TABLE`，**不导入 malight**。

    不能 `import malight.definitions`：那会先执行包 `__init__`，而板级代码
    的默认参数（`fill_color=Color.BLACK`）在类体求值时就要求常量已存在 ——
    生成块还没写进去时正好是个死循环。AST 字面量求值绕开整个导入链。
    """
    tree = ast.parse(io.open(path, encoding="utf-8").read(), path)
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for tgt in node.targets:
            if isinstance(tgt, ast.Name) and tgt.id == "_COLOR_TABLE":
                return ast.literal_eval(node.value)
    raise SystemExit("definitions.py 里找不到 _COLOR_TABLE")


def build_block(table):
    """按 _COLOR_TABLE 的顺序展开成显式赋值块（含首尾标记）。"""
    rows = [(en.upper(), hexv) for _cn, (en, hexv) in table.items()]
    width = max(len(name) for name, _ in rows) + 1
    lines = [BEGIN]
    for name, hexv in rows:
        lines.append('    {0}= "{1}"'.format((name + " ").ljust(width), hexv))
    lines.append(END)
    return "\n".join(lines) + "\n"


def splice(text, block):
    """把 text 里两个标记之间的内容替换成 block；找不到标记就报错。"""
    head, sep, rest = text.partition(BEGIN)
    if not sep:
        return None, "未找到起始标记，请手工加入：\n%s" % BEGIN
    _old, sep2, tail = rest.partition(END)
    if not sep2:
        return None, "未找到结束标记，请手工加入：\n%s" % END
    # tail 从 END 之后开始，先吃掉 END 那行的换行（block 自带结尾换行）
    for term in ("\r\n", "\n"):
        if tail.startswith(term):
            tail = tail[len(term):]
            break
    return head + block + tail, None


# ---------------------------------------------------------------------------
# 可选：类型检查器实测（证明常量真的静态可见）
# ---------------------------------------------------------------------------
#: 探针表达式 -> 期望类型。正面 4 条必须解析成 str；反面 1 条必须报错，
#: 否则说明检查器根本没在看这个类（那「能补全」就成了自说自话）。
PROBE_OK = ["Color.BLACK", "Color.WHITE", "Color.RED", "Color.TRANSPARENT",
            "Color.AQUA"]
PROBE_BAD = "Color.NOT_A_REAL_COLOR"

PROBE = '''# -*- coding: utf-8 -*-
from malight import Color
%s
%s
''' % ("\n".join("reveal_type(%s)" % e for e in PROBE_OK), PROBE_BAD)


def mypy_check():
    """返回 (状态, 说明)。状态：ok / fail / skip。"""
    try:
        import mypy  # noqa: F401
    except ImportError:
        return "skip", "未安装 mypy，跳过（静态检查仍已生效）"
    # mypy 默认会在仓库根写 .mypy_cache/，会污染工作区（回归的行尾检查会报它），
    # 所以缓存目录指到临时目录里。
    fd, path = tempfile.mkstemp(suffix=".py", prefix="_color_probe_", dir=ROOT)
    cache = tempfile.mkdtemp(prefix="malight_mypy_")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(PROBE)
        proc = subprocess.run(
            [sys.executable, "-m", "mypy", "--no-error-summary",
             "--no-incremental", "--follow-imports=silent",
             "--cache-dir", cache, path],
            cwd=ROOT, capture_output=True, encoding="utf-8", errors="replace")
        out = (proc.stdout or "") + (proc.stderr or "")
        problems = []
        revealed = {}
        for line in out.splitlines():
            if "Revealed type is" in line:
                revealed[int(line.split(":")[1].strip())] = line.split('"')[1]
        first = PROBE.split("\n").index("reveal_type(%s)" % PROBE_OK[0]) + 1
        for i, expr in enumerate(PROBE_OK):
            have = revealed.get(first + i, "未解析")
            # mypy 有时报全限定名（builtins.str），有时报短名（str），都算对
            if have.rsplit(".", 1)[-1] != "str":
                problems.append("%s -> %s（期望 str）" % (expr, have))
        # 反面探针：拼错的名字必须被标红，否则「能补全」只是自说自话。
        # 报错原文形如 ``"type[Color]" has no attribute "NOT_A_REAL_COLOR"``，
        # 不是 ``Color.X``，所以只比对属性名。
        if PROBE_BAD.rsplit(".", 1)[-1] not in out:
            problems.append("%s 没有被检查器报错 —— 说明它仍未静态可见" % PROBE_BAD)
        if problems:
            return "fail", "\n".join(problems)
        return "ok", ("mypy 实测 %d 个常量全部解析成 str，"
                      "且拼错的名字会被报错" % len(PROBE_OK))
    finally:
        try:
            os.remove(path)
        except OSError:
            pass
        shutil.rmtree(cache, ignore_errors=True)


def main(argv):
    check = "--check" in argv
    table = read_table()
    text = io.open(TARGET, encoding="utf-8", newline="").read()
    block = build_block(table)
    new_text, err = splice(text, block)
    if err:
        print("gen_color_constants: " + err)
        return 1
    if new_text != text:
        if check:
            old = text.partition(BEGIN)[2].partition(END)[0]
            new = block.partition(BEGIN)[2].partition(END)[0]
            print("颜色常量与 _COLOR_TABLE 不同步，请运行：python tools/gen_color_constants.py")
            for a, b in zip(old.splitlines(), new.splitlines()):
                if a != b:
                    print("  表内: %s" % a.strip())
                    print("  期望: %s" % b.strip())
                    break
            print("  (旧 %d 行 / 新 %d 行)" % (len(old.splitlines()), len(new.splitlines())))
            return 1
        io.open(TARGET, "w", encoding="utf-8", newline="").write(new_text)
        print("已写入 %d 个颜色常量 -> %s" % (len(table), os.path.relpath(TARGET, ROOT)))
        return 0
    print("颜色常量与 _COLOR_TABLE 同步（%d 个）" % len(table))
    if "--mypy" in argv:
        state, detail = mypy_check()
        print("类型检查器实测：%s（%s）"
              % ("通过" if state == "ok" else "跳过" if state == "skip" else "失败", detail))
        return 1 if state == "fail" else 0
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
