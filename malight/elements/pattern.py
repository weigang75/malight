# -*- coding: utf-8 -*-
"""
PatternElement 元素（每类一文件，含中文注释与示例）。 / PatternElement: tiling fill textures.
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

from .base import Element, _paint, _fmt_points, _fmt_transform, _Self


class PatternElement(Element):
    """
    图案元素（<pattern>，对应中文版 `元素图案`）：平铺填充纹理。 / Pattern element: a tiling fill texture.

    示例::
        p = pen.pattern(0, 0, 20, 20, id_="dots")
        p.add_element(pen.circle(10, 10, 3, fill_color="gray"))
        pen.rect(20, 20, 200, 100, fill_color="url(#dots)")
    """

    def __init__(self, board, x=0, y=0, width=10, height=10, id_=None, units=None, **kw):
        super().__init__(board, board.defs_node, tag="pattern")
        self._update_attrs(x=x, y=y, width=width, height=height,
                           id_=id_, units=units, **kw)

    def _update_attrs(self, x=0, y=0, width=10, height=10, id_=None, units=None, **kw):
        """写入 pattern 属性（内部方法）。"""
        self._apply_common({"id_": id_ or Element._next_id("pattern")})
        self._apply_common(kw)
        self.node.set("x", x)
        self.node.set("y", y)
        self.node.set("width", width)
        self.node.set("height", height)
        self.node.set("patternUnits", units or "userSpaceOnUse")

    def add_element(self, el) -> _Self:
        """把元素加入图案内容。 / Add a shape to the pattern content. 示例:: p.add_element(shape)"""
        el.change_group(self)
        return self

    def append(self, el) -> _Self:
        """add_element 的别名。 / Alias of add_element. """
        return self.add_element(el)

# ===========================================================================
# 使用示例
# ===========================================================================
# 在 PyCharm 里点绿色三角直接运行本文件即可；也可命令行：
#     python -m malight.elements.pattern
# ===========================================================================
if __name__ == "__main__":
    import os

    from malight import Malight, ColorName, CoordUnits

    _out = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        "..", "..", "output"))
    pen = Malight(os.path.join(_out, "demo_pattern"), width=660, height=380)
    pen.set_background_color(ColorName.WHITESMOKE)

    # -----------------------------------------------------------------
    # 1) 斜条纹图案（做背景 / 填充纹理） / 1) Diagonal stripe pattern for backgrounds and fills
    #    units 决定坐标基准：USER_SPACE（像素，最直观） / units sets the coordinate basis; USER_SPACE in pixels is the obvious one
    # -----------------------------------------------------------------
    stripes = pen.pattern(0, 0, 20, 20, id_="stripes",
                          units=CoordUnits.USER_SPACE)
    stripes.append(pen.rect(0, 0, 20, 20, fill_color=ColorName.LIGHTYELLOW))
    stripes.append(pen.line((0, 20), (20, 0), stroke_color=ColorName.GOLD,
                            stroke_width=4))
    pen.rect(40, 60, 240, 190, fill_color="url(#stripes)",
             stroke_color=ColorName.CHOCOLATE)

    # -----------------------------------------------------------------
    # 2) 圆点图案（波点） / 2) Polka dot pattern
    # -----------------------------------------------------------------
    dots = pen.pattern(0, 0, 24, 24, id_="dots")
    dots.append(pen.rect(0, 0, 24, 24, fill_color="white"))
    dots.append(pen.circle(12, 12, 5, fill_color=ColorName.TOMATO,
                           stroke_color="none"))
    pen.circle(450, 155, 95, fill_color="url(#dots)",
               stroke_color=ColorName.CRIMSON, stroke_width=3)

    # -----------------------------------------------------------------
    # 3) 棋盘格图案 / 3) Checkerboard pattern
    # -----------------------------------------------------------------
    grid = pen.pattern(0, 0, 40, 40, id_="grid")
    grid.append(pen.rect(0, 0, 20, 20, fill_color=ColorName.SNOW))
    grid.append(pen.rect(20, 20, 20, 20, fill_color=ColorName.SNOW))
    grid.append(pen.rect(0, 20, 20, 20, fill_color=ColorName.STEELBLUE))
    grid.append(pen.rect(20, 0, 20, 20, fill_color=ColorName.STEELBLUE))
    pen.rect(320, 60, 300, 190, fill_color="url(#grid)",
             stroke_color=ColorName.NAVY)

    # -----------------------------------------------------------------
    # 4) 图案可以只作为某条描边/文字的填充，也可以叠加在渐变上 / 4) A pattern can fill a stroke or text, or sit on top of a gradient
    # -----------------------------------------------------------------
    pen.text(60, 300, "带图案填充的文字 / text with a pattern fill", font_size=44,
             fill_color="url(#stripes)", stroke_color=ColorName.CHOCOLATE,
             stroke_width=1)
    pen.text(500, 300, "波点字 / polka dot text", font_size=44, fill_color="url(#dots)",
             stroke_color=ColorName.CRIMSON, stroke_width=1)

    # 5) 局部更新：只改图案格子尺寸，内容元素不动 / 5) Partial update: only the tile size changes, the contents stay
    small = pen.pattern(0, 0, 30, 30, id_="small_dots")
    small.append(pen.circle(15, 15, 4, fill_color=ColorName.SEAGREEN))
    small.update(width=60, height=60)
    print("图案 width/height: / pattern width/height:", small.node.attribs.get("width"),
          small.node.attribs.get("height"))
    pen.rect(60, 330, 540, 34, fill_color="url(#small_dots)")

    # 6) 提示：图案定义放在 <defs>，用 url(#id) 引用，不会直接显示 / 6) Pattern definitions live in <defs> and are referenced through url(#id)
    print("图案元素都放在 <defs> 中，用 url(#id) 引用 / Pattern elements live in <defs> and are referenced with url(#id)")
    pen.finish()
