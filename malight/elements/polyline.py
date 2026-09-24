# -*- coding: utf-8 -*-
"""
PolylineElement 元素（每类一文件，含中文注释与示例）。 / PolylineElement, created by pen.polyline.
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

from .base import Element, _paint, _fmt_points, _fmt_transform


class PolylineElement(Element["PolylineElement"]):
    """
    折线元素（对应中文版 `折线元素`）。 / Polyline element.

    示例::
        pen.polyline([(10, 100), (80, 40), (150, 120), (220, 60)],
                          stroke_color="green", stroke_width=3)
    """

    def __init__(self, board, parent=None, points=None, **kw):
        super().__init__(board, parent, tag="polyline")
        self._update_attrs(points=points or [], **kw)

    def _update_attrs(self, points=None, **kw):
        """写入折线顶点与样式（内部方法）。"""
        self._apply_common(kw)
        self._apply_paint(kw)
        self.node.set("points", _fmt_points(points or []))

    def bbox(self) -> tuple:
        """包围盒。 / Bounding box. """
        pts = self.node.attribs.get("points", "")
        xs, ys = [], []
        for pair in pts.split():
            x, y = pair.split(",")
            xs.append(float(x))
            ys.append(float(y))
        if not xs:
            return (0, 0, 0, 0)
        return (min(xs), min(ys), max(xs), max(ys))

    # ------------------------------------------------------------------
    # 参数访问器（显式方法，与动态合成的 set_/get_ 等价）。 / Parameter accessors, written out explicitly; identical to the
    # 展开成真实方法是为了让 IDE 能补全、拼错能报错。 / dynamically synthesized set_/get_. Real methods so the IDE completes them and flags typos.
    # 本区块由 tools/gen_attr_accessors.py 依 _update_attrs 生成。 / Generated from the _update_attrs signature by tools/gen_attr_accessors.py.
    # 手改会被 `python tools/gen_attr_accessors.py --check` 判为不同步。 / Hand edits make that check report it as out of sync.
    # ------------------------------------------------------------------
    # >>> gen_attr_accessors: begin (generated, do not edit by hand)
    def set_points(self, value) -> "PolylineElement":
        """设置 points（等价 ``update(points=value)``）。 / Set points; the same as ``update(points=value)``."""
        return self.update(points=value)

    def get_points(self) -> object:
        """读取 points 的当前属性值。 / Read the current raw points attribute."""
        return self._get_attr_value("points")
    # <<< gen_attr_accessors: end

# ===========================================================================
# 使用示例
# ===========================================================================
# 在 PyCharm 里点绿色三角直接运行本文件即可；也可命令行：
#     python -m malight.elements.polyline
# ===========================================================================
if __name__ == "__main__":
    import os

    from malight import Malight, ColorName, StrokeJoin, StrokeCap, DashStyle

    _out = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        "..", "..", "output"))
    pen = Malight(os.path.join(_out, "demo_polyline"), width=620, height=360)
    pen.set_background_color(ColorName.WHITESMOKE)

    # 1) 折线：顶点依次直连，首尾不闭合（不做 Z） / 1) Polyline: vertices joined in order, not closed with Z
    pen.polyline([(40, 280), (120, 80), (200, 280), (280, 80)],
                 fill_color="none", stroke_color=ColorName.NAVY,
                 stroke_width=3, stroke_join=StrokeJoin.ROUND)

    # 2) 折线也能填充：SVG 会把首尾自动连起来填充，但描边仍不闭合 / 2) A polyline can be filled: SVG closes it for the fill, the stroke stays open
    pen.polyline([(340, 280), (400, 100), (470, 240), (560, 120)],
                 fill_color=ColorName.KHAKI, stroke_color=ColorName.CHOCOLATE,
                 stroke_width=2, opacity=0.9)

    # 3) 用折线围成封闭外形（描边不闭合，适合「开口」造型） / 3) Wrap points into a shape: the stroke stays open, which suits open outlines
    pen.polyline([(60, 335), (160, 305), (260, 335), (160, 355)],
                 fill_color=ColorName.SKYBLUE,
                 stroke_color=ColorName.STEELBLUE, stroke_width=2)

    # 4) 折线同样支持线端/虚线枚举 / 4) Polylines take the same cap and dash enums
    pen.polyline([(340, 340), (420, 315), (500, 345), (560, 320)],
                 fill_color="none", stroke_color=ColorName.CRIMSON,
                 stroke_width=6, stroke_cap=StrokeCap.ROUND,
                 stroke_style=DashStyle.DASHED)

    # 5) 拿回元素改样式 / 量尺寸 / 5) Keep the element to restyle or measure it
    pl = pen.polyline([(300, 60), (360, 60), (360, 140), (300, 140)],
                      fill_color="none", stroke_color=ColorName.TEAL,
                      stroke_width=4)
    pl.update(stroke_color=ColorName.INDIGO, stroke_width=6)
    print("折线包围盒: / polyline bbox:", tuple(round(v, 1) for v in pl.bbox()))
    print("折线顶点串: / polyline points:", pl.node.attribs.get("points"))

    # 6) 内部数据也能读出来（顶点列表） / 6) The underlying data reads back as a vertex list
    print("顶点列表: / vertices:", pl.points if hasattr(pl, "points") else "(见 node.attribs) / (see node.attribs)")

    pen.finish()
