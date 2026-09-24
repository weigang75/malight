# -*- coding: utf-8 -*-
"""
元素参数访问器显式化（gen_attr_accessors）
==========================================

`Element.__getattr__` 会按 `_attr_params` 动态合成 `set_<参数>` / `get_<参数>`：
运行时好用，但**PyCharm 看不见动态合成的成员** —— `circle.set_radius(` 敲不出来，
`t.set_font_size(` 也没有补全，参数名写错不报错。文档里却在推荐这套写法
（`t.set_font_size(36).set_fill_color("teal")`），于是「文档教的 API」在 IDE 里
是隐形的，用户的原话是「在 pycharm 中都无法识别出来」。

本工具把缺口补成**显式方法**，写在各元素类体内（真实方法才会被静态分析看见）：

    def set_radius(self, value) -> "CircleElement":
        \"\"\"设置 radius（等价 ``update(radius=value)``）。 / Set radius; the same as
        ``update(radius=value)``.\"\"\"
        return self.update(radius=value)

    def get_radius(self) -> object:
        \"\"\"读取 radius 的当前属性值。 / Read the current raw r attribute.\"\"\"
        return self._get_attr_value("radius")

语义与动态合成的那份**完全一致**（`set_` 就是 `update(参数=值)` 的链式包装，
`get_` 就是 `_get_attr_value(参数)`），所以是纯增量：不改行为，只把成员变成
静态可见。运行时的 `__getattr__` 兜底保留 —— 「直接以参数名调用」那一形式
（`t.font_size(36)`）仍然走它：像 `EllipseElement.rotate` 这种参数名与
`Element.rotate()` 撞名的，没法显式展开。

缺口是**静态**算出来的（不在半途 import 包，避免「文件还没改好就自举失败」）：

    缺口 = 本类 `_update_attrs` 的**专属**参数
           − 本类已有的真实方法（基类 `Element` 的也算已有）

公共样式参数（opacity / fill_color / stroke_width ... 17 个）**不在这里管**：
它们的访问器是 base.py 里手写的真实方法，基类一处就够，子类不用各抄一遍。
唯一的例外是 `get_blend_mode`：混合模式写进 CSS style，节点属性读不回来
（恒 None），故意不写 —— 生成一个永远返回 None 的方法只会误导；用法上它是
只写属性，`set_blend_mode` 就够了。

生成块用纯 ASCII 标记包住。改完 `_update_attrs`（加参数、改名字）重跑本工具；
`--check` 比对生成块，手改或漏跑都会报不同步（`gen_docs --check` 的同一套范式）。

用法 / Usage::

    python tools/gen_attr_accessors.py           # 就地补全所有元素类
    python tools/gen_attr_accessors.py --check   # 只检查是否同步（回归用，退出码 0/1）
"""

from __future__ import print_function

import ast
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if ROOT not in sys.path:                     # 供 --check 的运行时核对 import malight
    sys.path.insert(0, ROOT)
ELEMS = os.path.join(ROOT, "malight", "elements")
BASE = os.path.join(ELEMS, "base.py")

BEGIN = "    # >>> gen_attr_accessors: begin (generated, do not edit by hand)"
END = "    # <<< gen_attr_accessors: end"

#: 有意不生成读取器的：混合模式写进 CSS style，节点属性里读不回来（恒 None），
#: 生成一个永远返回 None 的方法只会误导。动态合成那份仍在，行为不变。
#: （这条是公共样式参数，本来归 base.py 管，留在这里是为了 `--check` 认得它。）
SKIP = {"get_blend_mode"}

HEADER = [
    "    # ------------------------------------------------------------------",
    "    # 参数访问器（显式方法，与动态合成的 set_/get_ 等价）。 / Parameter accessors, written out explicitly; identical to the",
    "    # 展开成真实方法是为了让 IDE 能补全、拼错能报错。 / dynamically synthesized set_/get_. Real methods so the IDE completes them and flags typos.",
    "    # 本区块由 tools/gen_attr_accessors.py 依 _update_attrs 生成。 / Generated from the _update_attrs signature by tools/gen_attr_accessors.py.",
    "    # 手改会被 `python tools/gen_attr_accessors.py --check` 判为不同步。 / Hand edits make that check report it as out of sync.",
    "    # ------------------------------------------------------------------",
]


def read(path):
    return io.open(path, encoding="utf-8", newline="").read()


def element_files():
    """所有元素模块（base.py 是基类，它的公共访问器是手写的）。"""
    return [os.path.join(ELEMS, n) for n in sorted(os.listdir(ELEMS))
            if n.endswith(".py") and n not in ("__init__.py", "base.py")]


def _class_def(src, path):
    """取模块里的元素类定义（每个元素文件只有一个顶层类）。"""
    for node in ast.parse(src, path).body:
        if isinstance(node, ast.ClassDef):
            return node
    return None


def base_method_names():
    """基类 `Element` 里已有的真实方法名（这些不用重复生成）。"""
    cls = _class_def(read(BASE), BASE)
    names = set()
    for sub in cls.body:
        if isinstance(sub, ast.FunctionDef):
            names.add(sub.name)
    return names


def public_params():
    """从 base.py 的 `_COMMON_ATTR_PARAMS` 里取公共样式参数（保持声明顺序）。"""
    tree = ast.parse(read(BASE), BASE)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(t, ast.Name) and t.id == "_COMMON_ATTR_PARAMS"
                   for t in node.targets):
            continue
        text = None
        for sub in ast.walk(node.value):
            if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
                text = sub.value
        if text is None:
            break
        return text.split()
    raise SystemExit("base.py 里找不到 _COMMON_ATTR_PARAMS")


PUBLIC = public_params()


def update_attrs_params(cls):
    """
    取某类 `_update_attrs` 的**专属**参数名（按签名顺序）；没有该方法返回 None。

    公共样式参数（`**kw` 那一半）被滤掉：它们的访问器在 base.py 里手写一次就够，
    子类各抄一遍反而成了 18 份重复。
    """
    fn = None
    for sub in cls.body:
        if isinstance(sub, ast.FunctionDef) and sub.name == "_update_attrs":
            fn = sub
    if fn is None:
        return None
    return [a.arg for a in fn.args.args[1:]
            if a.arg != "kw" and a.arg not in PUBLIC]


def own_method_names(cls, skip_lines=None):
    """
    本类体内已有的名字（方法 / 类属性）。

    ``skip_lines`` 是生成块占用的行号区间（1-based，闭区间）—— 生成块里的方法
    必须**排除**在「已有」之外，否则缺口会被自己填平：跑过一次之后
    ``set_radius`` 成了本类方法，再算缺口就成了 0，块会被判定为多余而删掉。
    """
    lo, hi = (skip_lines or (0, 0))
    names = set()
    for sub in cls.body:
        if isinstance(sub, ast.FunctionDef):
            if lo <= sub.lineno <= hi:
                continue
            names.add(sub.name)
        elif isinstance(sub, ast.Assign):
            if lo <= sub.lineno <= hi:
                continue
            for tgt in sub.targets:
                if isinstance(tgt, ast.Name):
                    names.add(tgt.id)
    return names


def render_block(cls_name, params, missing_set, missing_get):
    """生成访问器区块行（含首尾标记）；没有缺口时返回 None。"""
    if not missing_set and not missing_get:
        return None
    lines = list(HEADER) + [BEGIN]
    for p in params:
        if p in missing_set:
            lines.append('    def set_%s(self, value) -> "%s":' % (p, cls_name))
            lines.append('        """设置 %s（等价 ``update(%s=value)``）。 '
                         '/ Set %s; the same as ``update(%s=value)``."""'
                         % (p, p, p, p))
            lines.append("        return self.update(%s=value)" % p)
            lines.append("")
        if p in missing_get:
            lines.append("    def get_%s(self) -> object:" % p)
            lines.append('        """读取 %s 的当前属性值。 '
                         '/ Read the current raw %s attribute."""' % (p, p))
            lines.append('        return self._get_attr_value("%s")' % p)
            lines.append("")
    while lines and lines[-1] == "":
        lines.pop()
    lines.append(END)
    return lines


def block_span(lines):
    """文件行列表里生成块的下标区间 (起, 止]；没有则返回 None。"""
    begin = end = None
    for i, line in enumerate(lines):
        if line.rstrip("\r\n") == BEGIN:
            begin = i
        elif line.rstrip("\r\n") == END:
            end = i
    if begin is None or end is None or end < begin:
        return None
    # 生成块前面的固定表头注释也一并算进来（重写时整段替换）
    start = begin
    while start > 0 and lines[start - 1].rstrip("\r\n") in \
            [h.rstrip("\r\n") for h in HEADER]:
        start -= 1
    return start, end


def splice(src, cls, block):
    """写入生成块：已有块就整段替换，没有就插到类体末尾；block 为 None 表示删除。"""
    lines = src.splitlines(True)
    span = block_span(lines)
    if span is not None:
        start, end = span
        new = ([] if block is None else [l + "\n" for l in block])
        return "".join(lines[:start] + new + lines[end + 1:])
    if block is None:
        return src
    at = cls.end_lineno                      # 1-based，类体最后一行的下一行
    return "".join(lines[:at] + ["\n"] + [l + "\n" for l in block] + lines[at:])


def process(check):
    """返回 (有改动/不同步的文件, 问题说明)。"""
    changed, stale = [], []
    inherited = base_method_names()
    for path in element_files():
        rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
        src = read(path)
        cls = _class_def(src, path)
        params = update_attrs_params(cls)
        if not params:
            continue
        # 生成块占的行，不能算进「本类已有方法」（详见 own_method_names 的说明）
        span = block_span(src.splitlines(True))
        have = inherited | own_method_names(
            cls, (span[0] + 1, span[1] + 1) if span else None)
        missing_set = [p for p in params if "set_" + p not in have]
        missing_get = [p for p in params
                       if "get_" + p not in have and "get_" + p not in SKIP]
        block = render_block(cls.name, params, set(missing_set), set(missing_get))
        out = splice(src, cls, block)
        if check:
            if out != src:
                stale.append("%s（%s）：缺 set_ %d 个 / get_ %d 个"
                             % (rel, cls.name, len(missing_set), len(missing_get)))
            continue
        if out != src:
            io.open(path, "w", encoding="utf-8", newline="").write(out)
            n = len(missing_set) + len(missing_get)
            changed.append((rel, cls.name, n))
    return changed, stale


def runtime_check():
    """
    运行时核对：每个 `_attr_params` 里的 `set_` / `get_` 必须**是真实方法**。

    静态块同步只能证明「生成块和 _update_attrs 一致」，证明不了「IDE 真的看得见」
    —— 名字对不上、写错缩进进了别的类，静态比对都可能放过。这里直接看 MRO：
    名字必须在某个类的 ``__dict__`` 里，才算是被静态分析看得到的成员。
    """
    import malight                                     # noqa: F401
    from malight.elements import Element
    from malight import ColorName

    problems = []
    for cls in Element.__subclasses__():
        for param in sorted(cls._attr_params):
            for name in ("set_" + param, "get_" + param):
                if name in SKIP:
                    continue
                if not any(name in k.__dict__ for k in cls.__mro__):
                    problems.append("%s.%s 仍是动态合成的（IDE 看不见）"
                                    % (cls.__name__, name))
    if problems:
        return problems

    # 抽一条真实链路走一遍：生成出来的（元素专属）与手写的（公共参数）各一次
    pen = malight.Malight("_acc_probe", width=120, height=120)
    c = pen.circle(10, 10, 5, fill_color=ColorName.RED)
    c.set_radius(60)
    if c.node.attribs.get("r") != 60 or c.get_radius() != 60:
        problems.append("CircleElement.set_radius/get_radius 行为不对：r=%r"
                        % c.node.attribs.get("r"))
    if c.set_opacity(0.5) is not c or c.get_opacity() != 0.5:
        problems.append("公共参数访问器链式/读值不对")
    c.set_filter(pen.fx.shadow(2, 2, 2))
    if not str(c.get_filter()).startswith("url(#"):
        problems.append("get_filter() 读不到滤镜：%r" % c.get_filter())
    return problems


def main(argv):
    check = "--check" in argv
    changed, stale = process(check)
    if check:
        if stale:
            print("元素参数访问器与 _update_attrs 不同步，请运行："
                  "python tools/gen_attr_accessors.py")
            for s in stale:
                print("  - " + s)
            return 1
        bad = runtime_check()
        if bad:
            print("元素参数访问器运行时核对失败 %d 项：" % len(bad))
            for b in bad[:12]:
                print("  - " + b)
            return 1
        print("元素参数访问器与 _update_attrs 同步，且运行时全部是真实方法")
        return 0
    if not changed:
        print("元素参数访问器已是最新，无需写入")
        return 0
    total = 0
    for rel, name, n in changed:
        total += n
        print("已补全 %2d 个参数访问器 -> %s（%s）" % (n, rel, name))
    print("合计 %d 个。" % total)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
