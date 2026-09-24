# -*- coding: utf-8 -*-
"""
RectElement 元素（每类一文件，含中文注释与示例）。 / RectElement, created by pen.rect.
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
from ..svg_backend import SvgNode, fmt_num


class RectElement(Element["RectElement"]):
    """
    矩形元素（对应中文版 `矩形元素`）。 / Rectangle element.

    支持圆角半径与旋转（rotate 为英文版增强）。

    示例::
        pen.rect(50, 50, 200, 100, corner_radius=12,
                      fill_color="cornflowerblue", rotate=5)
    """

    def __init__(self, board, parent=None, x=0, y=0, width=10, height=10,
                 corner_radius=None, rotate=None, **kw):
        super().__init__(board, parent, tag="rect")
        self._update_attrs(x=x, y=y, width=width, height=height,
                           corner_radius=corner_radius, rotate=rotate, **kw)

    def _update_attrs(self, x=0, y=0, width=10, height=10,
                      corner_radius=None, rotate=None, **kw):
        """写入矩形几何与样式（内部方法）。"""
        self._apply_common(kw)
        self._apply_paint(kw)
        self.node.set("x", x)
        self.node.set("y", y)
        self.node.set("width", width)
        self.node.set("height", height)
        self.node.set("rx", corner_radius)
        self.rotate_angle = rotate
        if rotate:
            cx, cy = x + float(width) / 2, y + float(height) / 2
            self.node.set("transform",
                          f"rotate({fmt_num(rotate)},{fmt_num(cx)},{fmt_num(cy)})")

    def bbox(self) -> tuple:
        """包围盒（未考虑旋转）。 / Bounding box, ignoring rotation. """
        x = float(self.node.attribs.get("x", 0))
        y = float(self.node.attribs.get("y", 0))
        w = float(self.node.attribs.get("width", 0))
        h = float(self.node.attribs.get("height", 0))
        return (x, y, x + w, y + h)

    # ------------------------------------------------------------------
    # 参数访问器（显式方法，与动态合成的 set_/get_ 等价）。 / Parameter accessors, written out explicitly; identical to the
    # 展开成真实方法是为了让 IDE 能补全、拼错能报错。 / dynamically synthesized set_/get_. Real methods so the IDE completes them and flags typos.
    # 本区块由 tools/gen_attr_accessors.py 依 _update_attrs 生成。 / Generated from the _update_attrs signature by tools/gen_attr_accessors.py.
    # 手改会被 `python tools/gen_attr_accessors.py --check` 判为不同步。 / Hand edits make that check report it as out of sync.
    # ------------------------------------------------------------------
    # >>> gen_attr_accessors: begin (generated, do not edit by hand)
    def set_x(self, value) -> "RectElement":
        """设置 x（等价 ``update(x=value)``）。 / Set x; the same as ``update(x=value)``."""
        return self.update(x=value)

    def get_x(self) -> object:
        """读取 x 的当前属性值。 / Read the current raw x attribute."""
        return self._get_attr_value("x")

    def set_y(self, value) -> "RectElement":
        """设置 y（等价 ``update(y=value)``）。 / Set y; the same as ``update(y=value)``."""
        return self.update(y=value)

    def get_y(self) -> object:
        """读取 y 的当前属性值。 / Read the current raw y attribute."""
        return self._get_attr_value("y")

    def set_width(self, value) -> "RectElement":
        """设置 width（等价 ``update(width=value)``）。 / Set width; the same as ``update(width=value)``."""
        return self.update(width=value)

    def get_width(self) -> object:
        """读取 width 的当前属性值。 / Read the current raw width attribute."""
        return self._get_attr_value("width")

    def set_height(self, value) -> "RectElement":
        """设置 height（等价 ``update(height=value)``）。 / Set height; the same as ``update(height=value)``."""
        return self.update(height=value)

    def get_height(self) -> object:
        """读取 height 的当前属性值。 / Read the current raw height attribute."""
        return self._get_attr_value("height")

    def set_corner_radius(self, value) -> "RectElement":
        """设置 corner_radius（等价 ``update(corner_radius=value)``）。 / Set corner_radius; the same as ``update(corner_radius=value)``."""
        return self.update(corner_radius=value)

    def get_corner_radius(self) -> object:
        """读取 corner_radius 的当前属性值。 / Read the current raw corner_radius attribute."""
        return self._get_attr_value("corner_radius")

    def set_rotate(self, value) -> "RectElement":
        """设置 rotate（等价 ``update(rotate=value)``）。 / Set rotate; the same as ``update(rotate=value)``."""
        return self.update(rotate=value)

    def get_rotate(self) -> object:
        """读取 rotate 的当前属性值。 / Read the current raw rotate attribute."""
        return self._get_attr_value("rotate")
    # <<< gen_attr_accessors: end

# ===========================================================================
# 使用示例
# ===========================================================================
# 在 PyCharm 里点绿色三角直接运行本文件即可；也可命令行：
#     python -m malight.elements.rect
# ===========================================================================
if __name__ == "__main__":
    import os

    from malight import Malight, ColorName, DashStyle, FillRule, Font

    _out = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        "..", "..", "output"))
    pen = Malight(os.path.join(_out, "demo_rect"), width=620, height=400)
    pen.set_background_color(ColorName.WHITESMOKE)

    # 1) 普通矩形 / 1) A plain rectangle
    pen.rect(40, 40, 200, 110, fill_color=ColorName.SKYBLUE,
             stroke_color=ColorName.NAVY, stroke_width=2)

    # 2) 圆角矩形 + 投影（UI 卡片最常见） / 2) Rounded rectangle with a shadow, the usual UI card
    pen.rect(280, 40, 220, 110, corner_radius=18,
             fill_color=ColorName.TOMATO, filter=pen.fx.shadow(6, 7, 8))
    pen.text(390, 105, "卡片 / Card", font=Font.SIMHEI, font_size=22,
             fill_color="white", h_align="middle")

    # 3) 旋转矩形（英文版增强能力） / 3) Rotated rectangle, an addition of this edition
    pen.rect(80, 200, 180, 80, corner_radius=10, rotate=-12,
             fill_color=ColorName.KHAKI, stroke_color=ColorName.CHOCOLATE,
             stroke_width=2)

    # 4) 虚线圆角「徽章」+ 混合模式 / 4) Dashed rounded badge with a blend mode
    badge = pen.rect(320, 200, 200, 80, corner_radius=40,
                     fill_color=ColorName.GOLD, stroke_color="white",
                     stroke_width=3, stroke_style=DashStyle.DASH_DOT,
                     blend_mode="multiply")
    pen.text(420, 248, "BADGE", font_size=22, fill_color=ColorName.MAROON,
             h_align="middle")
    print("徽章 bbox: / badge bbox:", tuple(round(v, 1) for v in badge.bbox()))

    # 5) 正方形（rect 的便捷封装） / 5) Square, a convenience wrapper over rect
    pen.square(90, 320, 50, fill_color=ColorName.TEAL, stroke_color="none")

    # 6) 用「外框 + 内框 + EVENODD」画一个镂空方环（不用布尔运算） / 6) Hollow square ring from an outer and an inner rect plus EVENODD
    outer = [(300, 310), (420, 310), (420, 390), (300, 390)]
    inner = [(325, 330), (395, 330), (395, 370), (325, 370)]
    pen.polygon(outer + inner, fill_color=ColorName.STEELBLUE,
                fill_rule=FillRule.EVENODD, stroke_color="none")
    pen.text(480, 355, "|", font_size=10, fill_color=ColorName.WHITESMOKE)

    # 7) 局部更新：只改宽高/圆角 / 7) Partial update: only size and corner radius change
    r = pen.rect(470, 310, 100, 40, fill_color=ColorName.PLUM)
    r.update(width=120, corner_radius=12)
    print("更新后矩形宽高: / rect size after update:", round(r.width, 1), round(r.height, 1))

    pen.finish()
