# -*- coding: utf-8 -*-
"""
元素属性落位闸门：创建元素时传的样式参数，必须真的落到 SVG 上。
================================================================

有元素会「接受参数但不写进 SVG」或「直接 TypeError」，用户在 PyCharm 里
看不到任何提示，只在导出的图里发现 opacity 没生效 —— 这类静默丢参
（silent attribute drop）没法靠读文档发现，只能逐个入口实测。

本工具对每一个「创建元素」的公开入口，逐个传入标准样式参数，然后检查
节点属性 / style 里是否出现对应值。任何一项没落地就报错。

排除说明（有意为之，不算丢参）：
- ``image`` / ``paste_svg``：SVG 的 <image> 本来就没有 fill/stroke，
  只检查公共样式（opacity 等）这一半。
- ``cross`` / ``grid`` 等组合型 helper：描边参数被有意下发给内部图形，
  只检查「组上的公共样式」是否生效。

命令行::

    python tools/check_element_attrs.py          # 打印表格
    python tools/check_element_attrs.py --quiet  # 只报错（回归用）
"""

import os
import struct
import sys
import zlib

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from malight import (Malight, StrokeCap, StrokeJoin, FillRule,    # noqa: E402
                     SystemFont, find_font_file)

OUT = os.path.join(_ROOT, "output")

# ---------------------------------------------------------------------------
# 标准样式参数：键名 -> (值, 期望落到的 SVG 属性；None 表示落进 style)
# ---------------------------------------------------------------------------
COMMON = [
    ("opacity",        0.42, "opacity"),
    ("fill_opacity",   0.42, "fill-opacity"),
    ("stroke_opacity", 0.42, "stroke-opacity"),
    ("blend_mode",     "multiply", None),          # -> style: mix-blend-mode
    ("vector_effect",  "non-scaling-stroke", "vector-effect"),
    ("class_name",     "cc", "class"),
    ("style_str",      "isolation:isolate", "style"),
]
PAINT = [
    ("stroke_width",   4.2,  "stroke-width"),
    ("stroke_cap",     StrokeCap.ROUND, "stroke-linecap"),
    ("stroke_join",    StrokeJoin.BEVEL, "stroke-linejoin"),
    ("fill_rule",      FillRule.EVENODD, "fill-rule"),
    ("dash_offset",    3.3,  "stroke-dashoffset"),
    ("paint_order",    "stroke", "paint-order"),
    ("stroke_style",   "4 2", "stroke-dasharray"),
]

# 只有公共样式的一半会被检查的入口（见模块 docstring）
COMMON_ONLY = {"image", "svg_image", "paste_svg"}

# 有意把参数下发给内部图形、自己不写的「入口 -> 参数」对（不算丢参）
DELEGATED = {
    "cross": {"stroke_width"},     # 十字的两条线各自带 stroke-width
    "grid":  {"opacity"},          # 每条网格线各自带 opacity
}


def _make_sample_png(path):
    """用标准库造一张 4x4 PNG，供 image 类入口使用。"""
    w = h = 4
    raw = b"".join(b"\x00" + bytes((200, 30, 30)) * w for _ in range(h))

    def chunk(tag, data):
        body = tag + data
        return (struct.pack(">I", len(data)) + body
                + struct.pack(">I", zlib.crc32(body) & 0xffffffff))

    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n"
                + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
                + chunk(b"IDAT", zlib.compress(raw))
                + chunk(b"IEND", b""))
    return path


def _make_sample_svg(path):
    with open(path, "w", encoding="utf-8") as f:
        f.write('<svg xmlns="http://www.w3.org/2000/svg" '
                'width="10" height="10"></svg>')
    return path


def entries(pen, png, svg, font):
    """返回 [(名称, 构造 lambda)]，覆盖板级所有会创建元素的入口。"""
    return [
        ("path",          lambda **s: pen.path(stroke_color="red", **s)),
        ("connect_points", lambda **s: pen.connect_points([(0, 0), (9, 9)], **s)),
        ("connect_curve", lambda **s: pen.connect_curve([(0, 0), (9, 9)], **s)),
        ("circle",        lambda **s: pen.circle(20, 20, 10, **s)),
        ("ellipse",       lambda **s: pen.ellipse(20, 20, (10, 6), **s)),
        ("rect",          lambda **s: pen.rect(10, 10, 20, 20, **s)),
        ("square",        lambda **s: pen.square(10, 10, 20, **s)),
        ("line",          lambda **s: pen.line((0, 0), (10, 10), **s)),
        ("polyline",      lambda **s: pen.polyline([(0, 0), (10, 10)], **s)),
        ("polygon",       lambda **s: pen.polygon([(0, 0), (10, 0), (5, 8)], **s)),
        ("regular_polygon", lambda **s: pen.regular_polygon(20, 20, 10, 6, **s)),
        ("star",          lambda **s: pen.star(20, 20, 10, **s)),
        ("heart",         lambda **s: pen.heart(20, 20, 10, **s)),
        ("text",          lambda **s: pen.text(10, 10, "hi", **s)),
        ("textPath",      lambda **s: pen.textPath([(0, 0), (50, 0)], "hi", **s)),
        ("text_to_path",  lambda **s: pen.text_to_path(0, 0, "hi", font=font, **s)),
        ("g",             lambda **s: pen.g(**s)),
        ("image",         lambda **s: pen.image(png, 0, 0, 10, 10, **s)),
        ("svg_image",     lambda **s: pen.svg_image(svg, 0, 0, 10, 10, **s)),
        ("paste_svg",     lambda **s: pen.paste_svg(svg, 0, 0, 10, 10, **s)),
        ("use",           lambda **s: pen.use("nope", 0, 0, **s)),
        ("symbol",        lambda **s: pen.symbol(**s)),
        ("pattern",       lambda **s: pen.pattern(0, 0, 10, 10, **s)),
        ("marker",        lambda **s: pen.marker(**s)),
        ("clipPath",      lambda **s: pen.clipPath("url(#x)", **s)),
        ("mask",          lambda **s: pen.mask("url(#x)", **s)),
        ("cross",         lambda **s: pen.cross(20, 20, **s)),
        ("frame",         lambda **s: pen.frame(**s)),
        ("grid",          lambda **s: pen.grid(20, **s)),
        ("measure",       lambda **s: pen.measure((0, 0), (10, 10), **s)),
        ("key_points",    lambda **s: pen.key_points([(1, 1)], **s)),
        ("mark_point",    lambda **s: pen.mark_point(5, 5, **s)),
        ("add_background_rect",
         lambda **s: pen.add_background_rect("white", **s)),
    ]


def _landed(el, attr, val):
    """节点上是否出现了期望值（style 类参数看 style 里有没有 mix-blend-mode）。"""
    if attr is None:
        return "mix-blend-mode" in (el.node.attribs.get("style") or "")
    got = el.node.attribs.get(attr)
    return got is not None and str(got) == str(val)


def audit():
    """返回 (行列表, 问题列表)。"""
    os.makedirs(OUT, exist_ok=True)
    png = _make_sample_png(os.path.join(OUT, "_attrcheck.png"))
    svg = _make_sample_svg(os.path.join(OUT, "_attrcheck.svg"))
    font = find_font_file("Android") or find_font_file("Arial")

    pen = Malight("_attrcheck", width=600, height=400)
    rows, problems = [], []
    for name, make in entries(pen, png, svg, font):
        checks = COMMON + ([] if name in COMMON_ONLY else PAINT)
        skip = DELEGATED.get(name, set())
        lost = []
        for key, val, attr in checks:
            if key in skip:
                continue
            try:
                el = make(**{key: val})
            except Exception as exc:                      # noqa: BLE001
                lost.append("%s(%s)" % (key, type(exc).__name__))
                continue
            if not _landed(el, attr, val):
                lost.append(key)
        total = len(checks) - len(skip)
        rows.append((name, total - len(lost), total, lost))
        if lost:
            problems.append("%s: 没落地 -> %s" % (name, ", ".join(lost)))
    return rows, problems


def main():
    quiet = "--quiet" in sys.argv
    rows, problems = audit()
    if not quiet:
        print("=" * 74)
        print("元素属性落位检查：创建时传样式参数，是否真的写进 SVG")
        print("=" * 74)
        for name, ok, total, lost in rows:
            mark = "OK " if not lost else "FAIL"
            print("%-22s %s %2d/%d  %s"
                  % (name, mark, ok, total, ",".join(lost) if lost else ""))
        print()
    if problems:
        print("属性落位失败 %d 项：" % len(problems))
        for p in problems:
            print("  - " + p)
        return 1
    print("属性落位全部通过（%d 个入口）。" % len(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
