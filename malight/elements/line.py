# -*- coding: utf-8 -*-
"""
LineElement 元素（每类一文件，含中文注释与示例）。 / LineElement, created by pen.line.
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
from ..definitions import Color, StrokeCap, StrokeJoin, TextHAlign, TextVAlign


class LineElement(Element):
    """
    线元素（对应中文版 `线元素`）。 / Line element.

    示例::
        pen.line((10, 10), (300, 80), stroke_width=2,
                      stroke_style="8 4", stroke_cap=StrokeCap.ROUND)
    """

    def __init__(self, board, parent=None, start=(0, 0), end=(0, 0), **kw):
        super().__init__(board, parent, tag="line")
        self._update_attrs(start=start, end=end, **kw)

    def _update_attrs(self, start=(0, 0), end=(0, 0), **kw):
        """写入线段几何与样式（内部方法）。"""
        self._apply_common(kw)
        self._apply_paint(kw)
        self.node.set("fill", "none")     # 线不填充
        self.node.set("x1", start[0])
        self.node.set("y1", start[1])
        self.node.set("x2", end[0])
        self.node.set("y2", end[1])

    def bbox(self) -> tuple:
        """包围盒。 / Bounding box. """
        x1 = float(self.node.attribs.get("x1", 0))
        y1 = float(self.node.attribs.get("y1", 0))
        x2 = float(self.node.attribs.get("x2", 0))
        y2 = float(self.node.attribs.get("y2", 0))
        return (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))

# ===========================================================================
# 使用示例
# ===========================================================================
# 在 PyCharm 里点绿色三角直接运行本文件即可；也可命令行：
#     python -m malight.elements.line
# ===========================================================================
if __name__ == "__main__":
    import os

    from malight import (Malight, ColorName, StrokeCap, StrokeJoin, DashStyle,
                         VectorEffect)

    _out = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        "..", "..", "output"))
    pen = Malight(os.path.join(_out, "demo_line"), width=620, height=360)
    pen.set_background_color(ColorName.WHITESMOKE)

    # 1) 基本线段：起点 -> 终点 / 1) A basic line from start to end
    pen.line((40, 60), (580, 60), stroke_color=ColorName.NAVY, stroke_width=3)

    # 2) 圆头粗线：画「胶囊线」/ 手绘感粗笔画时最常用 / 2) Thick round-capped line, the usual pick for capsule and hand-drawn strokes
    pen.line((40, 120), (580, 120), stroke_color=ColorName.TOMATO,
             stroke_width=16, stroke_cap=StrokeCap.ROUND)

    # 3) 虚线预设（枚举），不用再手写 "8 4" / 3) Dash presets as enums; no more hand-written "8 4"
    pen.line((40, 180), (580, 180), stroke_color=ColorName.SEAGREEN,
             stroke_width=4, stroke_style=DashStyle.DASH_DOT_DOT)

    # 4) 虚线相位偏移：同样的虚线错开排列，做「流动/进度」效果 / 4) Dash offset staggers one dash pattern for flow or progress effects
    for i in range(6):
        pen.line((60 + i * 90, 220), (60 + i * 90, 280),
                 stroke_color=ColorName.SLATEBLUE, stroke_width=6,
                 stroke_style=DashStyle.DASHED, dash_offset=i * 4)

    # 5) 蚂蚁线流动动画（浏览器打开 SVG 可见） / 5) Marching-ants animation, visible in a browser
    flow = pen.line((40, 320), (580, 320), stroke_color=ColorName.CRIMSON,
                    stroke_width=4, stroke_cap=StrokeCap.ROUND)
    flow.animate_dash_flow(dur=1.5, dash="10 8")

    # 6) 缩放画布时线宽保持不变（工程图/图标内嵌常需要） / 6) Keep the stroke width when the canvas scales, as diagrams and icons need
    ln = pen.line((40, 345), (580, 345), stroke_color=ColorName.INDIGO,
                  stroke_width=2, vector_effect=VectorEffect.NON_SCALING_STROKE)
    print("线包围盒: / line bbox:", tuple(round(v, 1) for v in ln.bbox()))

    # 7) 折角样式：stroke_join 控制两段线的拐角 / 7) stroke_join controls the corner between two segments
    pen.polyline([(40, 292), (90, 262), (140, 292)],
                 stroke_color=ColorName.CHOCOLATE, stroke_width=8,
                 stroke_join=StrokeJoin.ROUND)

    # 8) 局部更新：只改终点坐标 / 8) Partial update: only the end point changes
    l2 = pen.line((420, 250), (500, 250), stroke_color=ColorName.GOLD,
                  stroke_width=6, stroke_cap=StrokeCap.ROUND)
    l2.update(end=(560, 290))
    print("更新后线 d/坐标: / line d/coords after update:", l2.node.attribs)

    pen.finish()
