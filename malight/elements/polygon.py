# -*- coding: utf-8 -*-
"""
PolygonElement 元素（每类一文件，含中文注释与示例）。 / PolygonElement, created by pen.polygon.
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


class PolygonElement(Element["PolygonElement"]):
    """
    多边形元素（对应中文版 `多边形元素`，自动闭合）。 / Polygon element.

    英文版增强：支持 ``fill_rule``（evenodd 可实现带孔多边形）。

    示例::
        # 带孔多边形：外圈 + 内圈（evenodd 挖洞）
        outer = [(50, 50), (250, 50), (250, 200), (50, 200)]
        inner = [(100, 90), (200, 90), (200, 160), (100, 160)]
        pen.polygon(outer + inner, fill_color="teal", fill_rule="evenodd")
    """

    def __init__(self, board, parent=None, points=None, **kw):
        super().__init__(board, parent, tag="polygon")
        self._update_attrs(points=points or [], **kw)

    def _update_attrs(self, points=None, **kw):
        """写入多边形顶点与样式（内部方法）。"""
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
    def set_points(self, value) -> "PolygonElement":
        """设置 points（等价 ``update(points=value)``）。 / Set points; the same as ``update(points=value)``."""
        return self.update(points=value)

    def get_points(self) -> object:
        """读取 points 的当前属性值。 / Read the current raw points attribute."""
        return self._get_attr_value("points")
    # <<< gen_attr_accessors: end


# ===========================================================================
# 文字元素
# ===========================================================================

# ===========================================================================
# 使用示例
# ===========================================================================
# 在 PyCharm 里点绿色三角直接运行本文件即可；也可命令行：
#     python -m malight.elements.polygon
# ===========================================================================
if __name__ == "__main__":
    import os

    from malight import Malight, ColorName, FillRule

    _out = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        "..", "..", "output"))
    pen = Malight(os.path.join(_out, "demo_polygon"), width=660, height=380)
    pen.set_background_color(ColorName.WHITESMOKE)

    # 1) 三角形：给顶点列表即可 / 1) A triangle: just give the vertices
    pen.polygon([(50, 260), (150, 60), (250, 260)],
                fill_color=ColorName.TOMATO, stroke_color=ColorName.MAROON,
                stroke_width=2)

    # 2) ★ 带孔多边形：外圈顶点 + 内圈顶点拼在一起 + FillRule.EVENODD / 2) ★ Polygon with a hole: outer and inner vertices in one list plus FillRule.EVENODD
    #    这是复刻简笔画「挖洞 / 镂空」最关键的技巧（英文版增强能力） / the key trick for hollowed-out line art
    outer = [(300, 60), (560, 60), (560, 260), (300, 260)]
    inner = [(355, 105), (505, 105), (505, 215), (355, 215)]
    pen.polygon(outer + inner, fill_color=ColorName.TEAL,
                fill_rule=FillRule.EVENODD, stroke_color="none")

    # 3) 对照：同一批顶点用 NONZERO（默认）就不挖空 / 3) Compare: the same vertices with NONZERO, the default, stay solid
    pen.polygon(outer + inner, fill_color="none",
                stroke_color=ColorName.WHITESMOKE, stroke_width=1)

    # 4) 正多边形系列（内部就是 polygon，多了自动算顶点） / 4) Regular polygons: plain polygons with the vertices computed for you
    pen.hexagon(80, 320, 45, fill_color=ColorName.LAVENDER,
                stroke_color=ColorName.INDIGO, stroke_width=2)
    pen.pentagon(200, 320, 45, fill_color=ColorName.KHAKI,
                 stroke_color=ColorName.CHOCOLATE, stroke_width=2)
    pen.triangle(310, 320, 45, fill_color=ColorName.PLUM,
                 stroke_color=ColorName.INDIGO, stroke_width=2)

    # 5) 星形与爱心（同样返回 PolygonElement） / 5) Stars and hearts, also PolygonElement
    pen.star(450, 320, 48, n=5, fill_color=ColorName.GOLD,
             stroke_color=ColorName.GOLDENROD)
    pen.heart(570, 318, 48, fill_color=ColorName.CRIMSON,
              stroke_color=ColorName.MAROON)

    # 6) 钻石形 / 6) Diamond
    pen.diamond(160, 180, 42, stroke_color=ColorName.NAVY,
                fill_color=ColorName.SKYBLUE)

    # 7) 局部更新：只换填充色，顶点不动 / 7) Partial update: only the fill changes; the vertices stay
    poly = pen.polygon([(240, 140), (290, 140), (265, 200)],
                       fill_color=ColorName.CHOCOLATE)
    poly.update(fill_color=ColorName.SEAGREEN, stroke_width=3)
    print("多边形包围盒: / polygon bbox:", tuple(round(v, 1) for v in poly.bbox()))
    print("evenodd 的取值是: / evenodd resolves to:", FillRule.EVENODD.value)

    pen.finish()
