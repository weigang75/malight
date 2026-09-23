# -*- coding: utf-8 -*-
"""
调试辅助（网格/图框/测距/关键点）。 / Debugging helpers: grids, frames, distance measurements and key points.

本文件只包含 DebugMixin 一个类（Mixin），由 board/__init__.py 组合进 MagicPen。
"""

import math
from ..svg_backend import SvgNode, fmt_num
from ..elements import GroupElement, RectElement
from ..definitions import (Color, PaperSize, PaperSettings,
    StrokeCap, StrokeJoin, ArrowStyle, PointStyle, TextHAlign, TextVAlign,
    GridRepeatType, CoordUnits, PNGMode, PDFMode, DOCXMode, SystemFont)


class DebugMixin:
    """DebugMixin —— 调试辅助（网格/图框/测距/关键点）（方法名与 SVG 元素名对应，旧名保留为别名）。 / DebugMixin - debugging helpers (grids, frames, measurements, key points). """

    def measure(self, p1, p2, color=None, font_size=16, bg_color=None,
                     line_width=3, decimals=2, id_=None) -> GroupElement:
        """
        两点间测距标注（对应中文版 `测距`，调试用）。 / Annotate the distance between two points.

        示例::
            pen.draw_measure((50, 50), (350, 150))
        """
        color = color or Color.RED
        x1, y1 = p1
        x2, y2 = p2
        dist = math.hypot(x2 - x1, y2 - y1)
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        g = self.g(id_=id_)
        self.line(p1, p2, stroke_color=color, stroke_width=line_width,
                       stroke_style="6 4").change_group(g)
        label = f"{dist:.{decimals}f}"
        bg = self.rect(mx - len(label) * font_size * 0.35 - 4, my - font_size,
                            len(label) * font_size * 0.7 + 8, font_size + 6,
                            corner_radius=4, fill_color=bg_color or "white",
                            opacity=0.8, stroke_color=color)
        bg.change_group(g)
        t = self.text(mx, my - 4, label, font_size=font_size,
                            fill_color=color, h_align=TextHAlign.MIDDLE)
        t.change_group(g)
        return g

    def grid(self, spacing=20, color="#b0c4de", opacity=0.6, id_=None) -> GroupElement:
        """
        显示网格（对应中文版 `显示网格`，调试用）。 / Draw a grid.

        示例::
            pen.grid(40)
        """
        g = self.g(id_=id_)
        n_x = int(self.width // spacing) + 1
        n_y = int(self.height // spacing) + 1
        for i in range(n_x):
            ln = self.line((i * spacing, 0), (i * spacing, self.height),
                                stroke_color=color, stroke_width=0.5)
            ln.node.set("opacity", opacity)
            ln.change_group(g)
        for j in range(n_y):
            ln = self.line((0, j * spacing), (self.width, j * spacing),
                                stroke_color=color, stroke_width=0.5)
            ln.node.set("opacity", opacity)
            ln.change_group(g)
        return g

    def frame(self, color="#ff6347", stroke_width=1) -> RectElement:
        """
        显示画布边框（对应中文版 `显示图框`，调试用）。 / Draw the canvas frame.

        示例::
            pen.show_frame()
        """
        return self.rect(0, 0, self.width, self.height,
                              stroke_color=color, stroke_width=stroke_width,
                              fill_color=Color.TRANSPARENT)

    def mark_point(self, x, y, color=Color.RED, style=PointStyle.CROSS,
                   font_size=12, label=None, id_=None) -> GroupElement:
        """
        画定位点标记（对应中文版 `定位点`/`定位坐标`，调试用）。 / Draw a point marker.

        :param style: PointStyle 十字/空圆/实圆/空方/实方

        示例::
            pen.mark_point(200, 150, label="(200,150)")
        """
        g = self.g(id_=id_)
        s = 5
        if style == PointStyle.CROSS:
            self.cross(x, y, width=s, height=s, color=color).change_group(g)
        elif style == PointStyle.CIRCLE_HOLLOW:
            self.circle(x, y, s, stroke_color=color, fill_color=Color.TRANSPARENT).change_group(g)
        elif style == PointStyle.CIRCLE_SOLID:
            self.circle(x, y, s, fill_color=color, stroke_color=Color.TRANSPARENT).change_group(g)
        elif style == PointStyle.SQUARE_HOLLOW:
            self.rect(x - s, y - s, 2 * s, 2 * s, stroke_color=color,
                           fill_color=Color.TRANSPARENT).change_group(g)
        elif style == PointStyle.SQUARE_SOLID:
            self.rect(x - s, y - s, 2 * s, 2 * s, fill_color=color,
                           stroke_color=Color.TRANSPARENT).change_group(g)
        if label:
            t = self.text(x + s + 3, y - s, label, font_size=font_size,
                                fill_color=color)
            t.change_group(g)
        return g

    def key_points(self, points, color=Color.BLACK) -> GroupElement:
        """
        批量显示关键点坐标（对应中文版 `显示关键点`，调试用）。 / Label the coordinates of several key points.

        示例::
            pen.show_key_points([(50, 50), (200, 80), (350, 120)])
        """
        g = self.g()
        for i, pt in enumerate(points):
            self.mark_point(pt[0], pt[1], color=color,
                            label=f"{i}:({fmt_num(pt[0])},{fmt_num(pt[1])})").change_group(g)
        return g

    # ------------------------------------------------------------------
    # 组 / 模板 / 复用 / 图案 / 链接
    # ------------------------------------------------------------------

    # ---- 兼容别名（1.0 早期命名，等价于新名） ----
    draw_measure = measure
    show_grid = grid
    show_frame = frame
    show_key_points = key_points
