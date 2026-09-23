# -*- coding: utf-8 -*-
"""
MarkerElement 元素（每类一文件，含中文注释与示例）。 / MarkerElement: line-end decorations such as arrowheads.
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

from ..definitions import value_of
from .base import Element, _paint, _fmt_points, _fmt_transform, _Self


class MarkerElement(Element):
    """
    标记元素（<marker>，对应中文版 `标记元素`）：定义箭头等线端装饰。 / Marker element defining line-end decorations such as arrowheads.

    通常通过 ``pen.draw_arrow_line`` 间接使用。

    示例::
        m = pen.marker(id="arrow", ref_x=9, ref_y=3)
        m.add_element(pen.polygon([(0, 0), (9, 3), (0, 6)], fill_color="black"))
        pen.line((10, 10), (200, 100), marker_end="#arrow")
    """

    def __init__(self, board, id_=None, ref_x=0, ref_y=0,
                 marker_width=10, marker_height=10, orient="auto",
                 marker_units=None, **kw):
        super().__init__(board, board.defs_node, tag="marker")
        self._update_attrs(id_=id_, ref_x=ref_x, ref_y=ref_y,
                           marker_width=marker_width, marker_height=marker_height,
                           orient=orient, marker_units=marker_units, **kw)

    def _update_attrs(self, id_=None, ref_x=0, ref_y=0, marker_width=10,
                      marker_height=10, orient="auto", marker_units=None, **kw):
        """写入 marker 属性（内部方法）。"""
        self._apply_common({"id_": id_ or Element._next_id("marker")})
        self._apply_common(kw)
        self.node.set("refX", ref_x)
        self.node.set("refY", ref_y)
        self.node.set("markerWidth", marker_width)
        self.node.set("markerHeight", marker_height)
        self.node.set("orient", orient)
        if marker_units is not None:
            self.node.set("markerUnits", value_of(marker_units))
        self._apply_paint(kw)

    def add_element(self, el) -> _Self:
        """把图形加入 marker 内容。 / Add a shape to the marker content. """
        el.change_group(self)
        return self

# ===========================================================================
# 使用示例
# ===========================================================================
# 在 PyCharm 里点绿色三角直接运行本文件即可；也可命令行：
#     python -m malight.elements.marker
# ===========================================================================
if __name__ == "__main__":
    import os

    from malight import Malight, ColorName

    _out = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        "..", "..", "output"))
    pen = Malight(os.path.join(_out, "demo_marker"), width=620, height=380)
    pen.set_background_color(ColorName.WHITESMOKE)

    # -----------------------------------------------------------------
    # 1) 定义箭头标记（<marker> 放在 <defs> 里，可被多条线复用） / 1) Define an arrow marker in <defs> so several lines can share it
    #    ref_x / ref_y 是「参考点」——箭头尖端要对齐线端，所以取 (9, 3) / ref_x / ref_y is the reference point; (9, 3) puts the tip on the line end
    #    orient="auto" 让箭头自动跟随线条方向（画箭头必选） / orient="auto" turns the arrow with the line: what you want for arrow heads
    # -----------------------------------------------------------------
    arrow = pen.marker(id_="arrow_end", ref_x=9, ref_y=3,
                       width=10, height=6, orient="auto")
    arrow.add_element(pen.polygon([(0, 0), (9, 3), (0, 6)],
                                  fill_color=ColorName.TOMATO,
                                  stroke_color="none"))

    # 2) 起点用圆点标记 / 2) A dot marker at the start
    dot = pen.marker(id_="dot_start", ref_x=4, ref_y=4, width=8, height=8)
    dot.add_element(pen.circle(4, 4, 4, fill_color=ColorName.TEAL,
                               stroke_color="none"))

    # 3) 线条上挂标记：marker_end / marker_start 是 SVG 原生属性， / 3) marker_end / marker_start are native SVG attributes,
    #    用 extra 直接透传即可 / so pass them through with extra
    ln = pen.line((60, 90), (560, 90), stroke_color=ColorName.NAVY,
                  stroke_width=3, extra={"marker_end": "url(#arrow_end)"})
    pen.line((60, 150), (560, 150), stroke_color=ColorName.STEELBLUE,
             stroke_width=3,
             extra={"marker_start": "url(#dot_start)",
                    "marker_end": "url(#arrow_end)"})

    # 4) 曲线路径也能挂标记（箭头会顺着切线方向转） / 4) Curves take markers too; the arrow follows the tangent
    p = pen.path(fill_color="none", stroke_color=ColorName.CRIMSON,
                 stroke_width=3, extra={"marker_end": "url(#arrow_end)"})
    p.move_to(60, 300)
    p.cubic_to((180, 190), (360, 380), (560, 260))
    print("箭头线 marker-end = / arrow line marker-end =", ln.node.attribs.get("marker-end"))

    # 5) marker_units 控制箭头是否随线宽缩放 / 5) marker_units decides whether the arrow scales with the stroke
    #    "strokeWidth"（默认，随线宽） / "userSpaceOnUse"（固定像素） / "strokeWidth" scales with the stroke (default), "userSpaceOnUse" is fixed pixels
    fixed = pen.marker(id_="arrow_fixed", ref_x=9, ref_y=3, width=10, height=6,
                       orient="auto", marker_units="userSpaceOnUse")
    fixed.add_element(pen.polygon([(0, 0), (9, 3), (0, 6)],
                                  fill_color=ColorName.INDIGO))
    pen.line((60, 340), (560, 340), stroke_color=ColorName.INDIGO,
             stroke_width=1, extra={"marker_end": "url(#arrow_fixed)"})

    # 6) 局部更新：改方向策略或参考点 / 6) Partial update: change the orientation or the reference point
    arrow.update(orient="auto-start-reverse")
    print("箭头方向: / arrow orientation:", arrow.node.attribs.get("orient"),
          "| refX:", arrow.node.attribs.get("refX"))

    pen.finish()
