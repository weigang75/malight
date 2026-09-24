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

from .base import Element, _paint, _fmt_points, _fmt_transform


class PatternElement(Element["PatternElement"]):
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
        self._apply_paint(kw)   # 填充/描边会被图案内容继承（英文版修正）
        self.node.set("x", x)
        self.node.set("y", y)
        self.node.set("width", width)
        self.node.set("height", height)
        self.node.set("patternUnits", units or "userSpaceOnUse")

    def add_element(self, el) -> "PatternElement":
        """把元素加入图案内容。 / Add a shape to the pattern content. 示例:: p.add_element(shape)"""
        el.change_group(self)
        return self

    def append(self, el) -> "PatternElement":
        """add_element 的别名。 / Alias of add_element. """
        return self.add_element(el)

    # ------------------------------------------------------------------
    # 参数访问器（显式方法，与动态合成的 set_/get_ 等价）。 / Parameter accessors, written out explicitly; identical to the
    # 展开成真实方法是为了让 IDE 能补全、拼错能报错。 / dynamically synthesized set_/get_. Real methods so the IDE completes them and flags typos.
    # 本区块由 tools/gen_attr_accessors.py 依 _update_attrs 生成。 / Generated from the _update_attrs signature by tools/gen_attr_accessors.py.
    # 手改会被 `python tools/gen_attr_accessors.py --check` 判为不同步。 / Hand edits make that check report it as out of sync.
    # ------------------------------------------------------------------
    # >>> gen_attr_accessors: begin (generated, do not edit by hand)
    def set_x(self, value) -> "PatternElement":
        """设置 x（等价 ``update(x=value)``）。 / Set x; the same as ``update(x=value)``."""
        return self.update(x=value)

    def get_x(self) -> object:
        """读取 x 的当前属性值。 / Read the current raw x attribute."""
        return self._get_attr_value("x")

    def set_y(self, value) -> "PatternElement":
        """设置 y（等价 ``update(y=value)``）。 / Set y; the same as ``update(y=value)``."""
        return self.update(y=value)

    def get_y(self) -> object:
        """读取 y 的当前属性值。 / Read the current raw y attribute."""
        return self._get_attr_value("y")

    def set_width(self, value) -> "PatternElement":
        """设置 width（等价 ``update(width=value)``）。 / Set width; the same as ``update(width=value)``."""
        return self.update(width=value)

    def get_width(self) -> object:
        """读取 width 的当前属性值。 / Read the current raw width attribute."""
        return self._get_attr_value("width")

    def set_height(self, value) -> "PatternElement":
        """设置 height（等价 ``update(height=value)``）。 / Set height; the same as ``update(height=value)``."""
        return self.update(height=value)

    def get_height(self) -> object:
        """读取 height 的当前属性值。 / Read the current raw height attribute."""
        return self._get_attr_value("height")

    def set_id_(self, value) -> "PatternElement":
        """设置 id_（等价 ``update(id_=value)``）。 / Set id_; the same as ``update(id_=value)``."""
        return self.update(id_=value)

    def get_id_(self) -> object:
        """读取 id_ 的当前属性值。 / Read the current raw id_ attribute."""
        return self._get_attr_value("id_")

    def set_units(self, value) -> "PatternElement":
        """设置 units（等价 ``update(units=value)``）。 / Set units; the same as ``update(units=value)``."""
        return self.update(units=value)

    def get_units(self) -> object:
        """读取 units 的当前属性值。 / Read the current raw units attribute."""
        return self._get_attr_value("units")
    # <<< gen_attr_accessors: end

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
