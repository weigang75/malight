# -*- coding: utf-8 -*-
"""
元素转 PathElement（topath）—— `Element.to_path_element()` 的实现层
====================================================================

`convert_to_path()` turns geometry elements into an equivalent `PathElement`;
unsupported kinds raise `NotImplementedError`. / `convert_to_path()` 把几何元素
（矩形 / 圆 / 椭圆 / 直线 / 多边形 / 折线）转换成等价的 `PathElement`，原元素
保留；`PathElement` 自身直接原样返回。图片 / 文字等需要轮廓提取的类型抛
`NotImplementedError`（i18n 词条 ``err.to_path_todo``，提示暂未实现）。

样式（填充 / 描边等）会带到新路径上；``kw`` 可覆盖。 / Styles (fill / stroke
and so on) carry over to the new path; ``kw`` overrides them.
"""


# ---------------------------------------------------------------------------
# 直接运行引导：在 PyCharm 里点绿色三角运行本文件（或命令行 python 本文件路径）时，
# 相对导入需要包上下文，这里自动补上项目根路径与包名。
# 正常 `import malight.xxx` 时这段不会执行，对包本身零影响。
# ---------------------------------------------------------------------------
if __name__ == "__main__" and not __package__:
    import os as _os
    import sys as _sys
    _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.dirname(
        _os.path.abspath(__file__)))))
    __package__ = "malight.elements"

import math

from ..i18n import t
from .path import PathElement


def _num(el, key, default=0.0) -> float:
    """读节点属性并转 float（缺省值兜底，内部函数）。"""
    v = el.node.attribs.get(key, None)
    if v is None:
        return float(default)
    try:
        return float(v)
    except (TypeError, ValueError):
        return float(default)


def _copy_style(new_path, src, kw) -> "PathElement":
    """把源元素样式带到新路径；kw 里给了的类别以 kw 为准（内部函数）。"""
    skip = set()
    if any(k in kw for k in ("fill", "fill_color")):
        skip.add("fill")
    if any(k in kw for k in ("stroke", "stroke_color")):
        skip.update(("stroke", "stroke-dasharray", "stroke-linecap",
                     "stroke-linejoin"))
    if "stroke_width" in kw or "stroke-width" in kw:
        skip.add("stroke-width")
    for k in ("fill", "stroke", "stroke-width", "stroke-dasharray",
              "stroke-linecap", "stroke-linejoin", "fill-rule", "opacity"):
        if k in skip:
            continue
        if k in src.node.attribs:
            new_path.node.set(k, src.node.attribs[k])
    return new_path


def _poly_points(el) -> list:
    """解析 points 属性字符串为 [(x, y), ...]（内部函数）。"""
    raw = str(el.node.attribs.get("points", "") or "").replace(",", " ").split()
    vals = []
    for tok in raw:
        try:
            vals.append(float(tok))
        except ValueError:
            continue
    return list(zip(vals[0::2], vals[1::2]))


def convert_to_path(el, **kw) -> PathElement:
    """
    把几何元素转换为等价 PathElement（原元素保留）。 / Convert a geometry element into an equivalent PathElement (the original stays).

    :param el: RectElement / CircleElement / EllipseElement / LineElement /
               PolygonElement / PolylineElement（PathElement 原样返回）
    :param kw: 新路径的样式覆盖（fill_color / stroke_color 等）
    :return: PathElement
    """
    if isinstance(el, PathElement):
        return el
    new = PathElement(el.board, el.parent_node, **kw)
    name = type(el).__name__

    if name == "RectElement":
        x, y = _num(el, "x"), _num(el, "y")
        w, h = _num(el, "width"), _num(el, "height")
        r = _num(el, "rx")
        r = min(r, w / 2.0, h / 2.0)
        new.move_to(x + r, y)
        new.line_to(x + w - r, y)
        if r > 1e-9:
            new.arc_to(r, (x + w, y + r), sweep=1)
        new.line_to(x + w, y + h - r)
        if r > 1e-9:
            new.arc_to(r, (x + w - r, y + h), sweep=1)
        new.line_to(x + r, y + h)
        if r > 1e-9:
            new.arc_to(r, (x, y + h - r), sweep=1)
        new.line_to(x, y + r)
        if r > 1e-9:
            new.arc_to(r, (x + r, y), sweep=1)
        new.close()
    elif name == "CircleElement":
        cx, cy, r = _num(el, "cx"), _num(el, "cy"), _num(el, "r")
        new.move_to(cx - r, cy)
        new.arc_to(r, (cx + r, cy), sweep=1)
        new.arc_to(r, (cx - r, cy), sweep=1)
        new.close()
    elif name == "EllipseElement":
        cx, cy = _num(el, "cx"), _num(el, "cy")
        rx, ry = _num(el, "rx"), _num(el, "ry")
        new.move_to(cx - rx, cy)
        new.ellipse_arc_to(rx, ry, (cx + rx, cy), sweep=1)
        new.ellipse_arc_to(rx, ry, (cx - rx, cy), sweep=1)
        new.close()
    elif name == "LineElement":
        new.move_to(_num(el, "x1"), _num(el, "y1"))
        new.line_to(_num(el, "x2"), _num(el, "y2"))
    elif name in ("PolygonElement", "PolylineElement"):
        pts = _poly_points(el)
        if not pts:
            raise ValueError(t("err.to_path_todo").format(name))
        new.move_to(*pts[0])
        for px, py in pts[1:]:
            new.line_to(px, py)
        if name == "PolygonElement":
            new.close()
    else:
        raise NotImplementedError(t("err.to_path_todo").format(name))

    _copy_style(new, el, kw)
    new._heading = math.degrees(math.atan2(
        new._cur[1] - (new._start[1] if new._start else new._cur[1]),
        new._cur[0] - (new._start[0] if new._start else new._cur[0])))
    return new


# ===========================================================================
# 使用示例
# ===========================================================================
# 在 PyCharm 里点绿色三角直接运行本文件即可；也可命令行：
#     python -m malight.elements.topath
# ===========================================================================
if __name__ == "__main__":
    import os

    from malight import Malight, ColorName

    _out = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        "..", "..", "output"))
    pen = Malight(os.path.join(_out, "demo_topath"), width=420, height=300)
    pen.set_background_color(ColorName.WHITESMOKE)

    rect = pen.rect(40, 40, 120, 80, fill_color=ColorName.TEAL,
                    stroke_color="gray")
    rp = rect.to_path_element()
    print("rect ->", type(rp).__name__, "| d:", rp.get_d())   # 圆角 / rounded

    circle = pen.circle(240, 80, 40, fill_color="none",
                        stroke_color=ColorName.CRIMSON, stroke_width=3)
    cp = circle.to_path_element()
    print("circle -> d:", cp.get_d()[:60], "...")

    poly = pen.polygon([(60, 180), (150, 180), (105, 260)],
                       fill_color=ColorName.GOLD)
    pp = poly.to_path_element()
    print("polygon -> d:", pp.get_d())

    try:
        pen.text(240, 220, "hi").to_path_element()
    except NotImplementedError as exc:
        print("text -> NotImplementedError（符合预期 / expected）:", exc)

    pen.finish()
