# -*- coding: utf-8 -*-
"""
CircleElement 元素（每类一文件，含中文注释与示例）。 / CircleElement, created by pen.circle.
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
from .path import PathElement


class CircleElement(Element):
    """
    圆元素（对应中文版 `圆元素`）。由 ``pen.circle`` 创建。 / Circle element, created by ``pen.circle``.

    示例::
        c = pen.circle(100, 100, 50, fill_color="red", stroke_width=2)
        print(c.center_x, c.center_y)   # 100 100
        path = c.to_path_element()      # 转为路径元素（英文版新增）
    """

    def __init__(self, board, parent=None, x=0, y=0, radius=0, **kw):
        super().__init__(board, parent, tag="circle")
        self._update_attrs(x=x, y=y, radius=radius, **kw)

    def _update_attrs(self, x=0, y=0, radius=0, **kw):
        """写入圆的几何与样式属性（内部方法）。"""
        self._apply_common(kw)
        self._apply_paint(kw)
        self.node.set("cx", x)
        self.node.set("cy", y)
        self.node.set("r", radius)

    def bbox(self) -> tuple:
        """包围盒。 / Bounding box. """
        cx = float(self.node.attribs.get("cx", 0))
        cy = float(self.node.attribs.get("cy", 0))
        r = float(self.node.attribs.get("r", 0))
        return (cx - r, cy - r, cx + r, cy + r)

    def to_path_element(self) -> "PathElement":
        """
        转换为 PathElement（对应中文版 `转路径元素`）。 / Convert to a PathElement.

        示例::
            p = c.to_path_element()
            p.union(other_path)   # 之后可做布尔运算
        """
        cx = float(self.node.attribs.get("cx", 0))
        cy = float(self.node.attribs.get("cy", 0))
        r = float(self.node.attribs.get("r", 0))
        p = PathElement(self.board, self.parent_node)
        p.circle_to((cx, cy))
        p._copy_paint_from(self)
        return p

# ===========================================================================
# 使用示例
# ===========================================================================
# 在 PyCharm 里点绿色三角直接运行本文件即可；也可命令行：
#     python -m malight.elements.circle
# ===========================================================================
if __name__ == "__main__":
    import os

    from malight import Malight, ColorName, StrokeCap, DashStyle

    _out = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        "..", "..", "output"))
    pen = Malight(os.path.join(_out, "demo_circle"), width=620, height=360)
    pen.set_background_color(ColorName.WHITESMOKE)

    # 1) 最简写法：圆心 (x, y) + 半径 / 1) Minimal form: centre (x, y) plus radius
    pen.circle(90, 90, 50, fill_color=ColorName.DODGERBLUE)

    # 2) 空心圆：填充设为 none（等价 Color.TRANSPARENT） / 2) Hollow circle: fill "none", the same as Color.TRANSPARENT
    pen.circle(230, 90, 50, fill_color="none", stroke_color=ColorName.TOMATO,
               stroke_width=6)

    # 3) 枚举化选项：圆头线端 + 虚线预设（不必再记 "8 4" 这种魔数） / 3) Enum options: round caps and dash presets, no more magic strings like "8 4"
    pen.circle(370, 90, 50, fill_color="none", stroke_color=ColorName.SEAGREEN,
               stroke_width=6, stroke_cap=StrokeCap.ROUND,
               stroke_style=DashStyle.DASHED)

    # 4) 逐边框线偏移：同一虚线不同相位，排在一起像「流动的圈」 / 4) Dash offset per ring: one dash at different phases looks like a flowing circle
    for i in range(3):
        pen.circle(500 + 0, 40 + i * 45, 18, fill_color="none",
                   stroke_color=ColorName.INDIGO, stroke_width=4,
                   stroke_style=DashStyle.DASH_DOT, dash_offset=i * 6)

    # 5) 半透明叠色：两圆重叠处颜色更深（CSS 混合模式） / 5) Translucent stacking: the overlap darkens (CSS blend mode)
    pen.circle(90, 250, 55, fill_color=ColorName.TEAL, opacity=0.75,
               blend_mode="multiply")
    pen.circle(150, 250, 55, fill_color=ColorName.GOLD, opacity=0.75,
               blend_mode="multiply")

    # 6) 一行加投影滤镜（滤镜需用浏览器打开 SVG 查看） / 6) One-line drop shadow (open the SVG in a browser to see filters)
    pen.circle(330, 250, 55, fill_color=ColorName.PLUM,
               filter=pen.fx.shadow(6, 8, 8))

    # 7) 拿回元素做后续处理（update 是局部更新，不会动几何） / 7) Keep the element for later use; update is partial and leaves geometry alone
    c = pen.circle(470, 250, 40, fill_color=ColorName.SKYBLUE)
    c.update(radius=46, stroke_color=ColorName.NAVY, stroke_width=3)
    print("圆的包围盒: / circle bbox:", tuple(round(v, 1) for v in c.bbox()))
    print("圆心: / centre:", round(c.center_x, 1), round(c.center_y, 1))

    # 8) 圆 → 路径元素（之后可做布尔运算 / 拖动锚点） / 8) Circle to path element, ready for boolean ops or anchor dragging
    path_el = c.to_path_element()
    print("圆转路径 d = / circle as path d =", path_el.get_d())

    pen.finish()
