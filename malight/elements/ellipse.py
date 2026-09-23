# -*- coding: utf-8 -*-
"""
EllipseElement 元素（每类一文件，含中文注释与示例）。 / EllipseElement, created by pen.ellipse.
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
from ..svg_backend import SvgNode, fmt_num


class EllipseElement(Element):
    """
    椭圆元素（对应中文版 `椭圆元素`）。 / Ellipse element.

    英文版增强：支持 ``rotate`` 旋转角度（原版不支持旋转椭圆）。

    示例::
        pen.ellipse(200, 100, radius=(80, 40), fill_color="skyblue",
                         rotate=-15)   # 逆时针旋转 15 度
    """

    def __init__(self, board, parent=None, x=0, y=0, radius=(10, 10), rotate=None, **kw):
        super().__init__(board, parent, tag="ellipse")
        self._update_attrs(x=x, y=y, radius=radius, rotate=rotate, **kw)

    def _update_attrs(self, x=0, y=0, radius=(10, 10), rotate=None, **kw):
        """写入椭圆几何与样式（内部方法）。"""
        self._apply_common(kw)
        self._apply_paint(kw)
        if isinstance(radius, (int, float)):
            radius = (radius, radius)
        self.node.set("cx", x)
        self.node.set("cy", y)
        self.node.set("rx", radius[0])
        self.node.set("ry", radius[1])
        if rotate:
            self.node.set("transform",
                          f"rotate({fmt_num(rotate)},{fmt_num(x)},{fmt_num(y)})")

    def bbox(self) -> tuple:
        """包围盒（未考虑旋转）。 / Bounding box, ignoring rotation. """
        cx = float(self.node.attribs.get("cx", 0))
        cy = float(self.node.attribs.get("cy", 0))
        rx = float(self.node.attribs.get("rx", 0))
        ry = float(self.node.attribs.get("ry", 0))
        return (cx - rx, cy - ry, cx + rx, cy + ry)

# ===========================================================================
# 使用示例
# ===========================================================================
# 在 PyCharm 里点绿色三角直接运行本文件即可；也可命令行：
#     python -m malight.elements.ellipse
# ===========================================================================
if __name__ == "__main__":
    import os

    from malight import Malight, ColorName, Color

    _out = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        "..", "..", "output"))
    pen = Malight(os.path.join(_out, "demo_ellipse"), width=620, height=360)
    pen.set_background_color(ColorName.WHITESMOKE)

    # 1) 标准椭圆：radius=(rx, ry) / 1) Standard ellipse: radius=(rx, ry)
    pen.ellipse(140, 100, radius=(110, 60), fill_color=ColorName.SKYBLUE,
                stroke_color=ColorName.NAVY, stroke_width=2)

    # 2) 只传一个数值 = 正圆（等价 pen.circle） / 2) One number means a circle, the same as pen.circle
    pen.ellipse(340, 100, radius=55, fill_color=ColorName.KHAKI,
                stroke_color=ColorName.CHOCOLATE, stroke_width=3)

    # 3) 旋转椭圆（英文版增强能力，中文原版不支持） / 3) Rotated ellipse, an addition of this edition
    e = pen.ellipse(500, 100, radius=(90, 30), rotate=-25,
                    fill_color=ColorName.PLUM, stroke_color=ColorName.INDIGO,
                    stroke_width=2, opacity=0.9)
    print("旋转椭圆 bbox: / rotated ellipse bbox:", tuple(round(v, 1) for v in e.bbox()))

    # 4) 渐变填充 + 阴影，做「立体药丸」效果 / 4) Gradient fill plus shadow for a 3D pill look
    grad = pen.radialGradient((0.5, 0.3), 0.7, "white", ColorName.STEELBLUE)
    pen.ellipse(160, 260, radius=(120, 45), fill_color=grad.paint(),
                stroke_color=Color.TRANSPARENT,
                filter=pen.fx.shadow(4, 6, 6))

    # 5) 椭圆同样支持枚举化的描边样式 / 5) Ellipses take the same enum stroke styles
    from malight import StrokeCap, DashStyle
    pen.ellipse(430, 260, radius=(120, 45), fill_color="none",
                stroke_color=ColorName.SEAGREEN, stroke_width=5,
                stroke_cap=StrokeCap.ROUND, stroke_style=DashStyle.DASH_DOT)

    # 6) 局部更新：只改 rx/ry，圆心不变 / 6) Partial update: rx/ry change, the centre stays
    e2 = pen.ellipse(160, 340, radius=(40, 20), fill_color=ColorName.TOMATO)
    e2.update(radius=(80, 24))
    print("更新后椭圆的宽高: / ellipse size after update:", round(e2.width, 1), round(e2.height, 1))

    pen.finish()
