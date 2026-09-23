# -*- coding: utf-8 -*-
"""
路径与连线（path/polyline/表格/箭头/波浪线）。 / Paths and connectors: path, polyline, tables, arrows and wave lines.

本文件只包含 PathMixin 一个类（Mixin），由 board/__init__.py 组合进 MagicPen。
"""

import math
from ..definitions import (Color, PaperSize, PaperSettings,
    StrokeCap, StrokeJoin, ArrowStyle, PointStyle, TextHAlign, TextVAlign,
    GridRepeatType, CoordUnits, PNGMode, PDFMode, DOCXMode, SystemFont)
from ..elements import (GroupElement, PolylineElement, PolygonElement)
from ..elements.path import PathElement
from .. import tools


class PathMixin:
    """PathMixin —— 路径与连线（path/polyline/表格/箭头/波浪线）（方法名与 SVG 元素名对应，旧名保留为别名）。 / PathMixin - paths and connectors: path, polyline, tables, arrows, wave lines. """

    def path(self, fill_color=Color.TRANSPARENT, stroke_color=Color.BLACK,
                  stroke_width=1, stroke_style=None, stroke_cap=None,
                  stroke_join=None, fill_rule=None, dash_offset=None,
                  blend_mode=None, filter=None, opacity=1.0,
                  id_=None, **extra) -> PathElement:
        """
        开始一条路径（对应中文版 `路径`）。返回 PathElement，
        之后调用 move_to/line_to/cubic_to/... 组合形状。 / Start a path and return a PathElement; then chain move_to / line_to / cubic_to and friends.

        :param stroke_cap: StrokeCap 线端形状
        :param stroke_join: StrokeJoin 拐角形状
        :param fill_rule: FillRule.EVENODD 可挖洞
        :param dash_offset: 虚线相位偏移
        :param blend_mode: BlendMode 混合模式
        :param filter: 滤镜

        示例::
            p = pen.path(fill_color="lightyellow", stroke_width=2)
            p.move_to(100, 100)
            p.line_to(300, 100)
            p.line_to(200, 250)
            p.close()
        """
        return self._new(PathElement, fill_color=fill_color,
                         stroke_color=stroke_color, stroke_width=stroke_width,
                         stroke_style=stroke_style, stroke_cap=stroke_cap,
                         stroke_join=stroke_join, opacity=opacity,
                         fill_rule=fill_rule, id_=id_, extra=extra or None,
                         blend_mode=blend_mode, filter=filter, dash_offset=dash_offset)

    def connect_points(self, points, stroke_color=Color.BLACK,
                       fill_color=Color.TRANSPARENT, stroke_width=1,
                       close=False, opacity=1.0, stroke_style=None,
                       id_=None, **extra) -> PathElement:
        """
        把顶点列表连成折线路径（对应中文版 `连直线`/`连线`）。 / Connect a list of vertices into a polyline path.

        :param close: True 时闭合（等效 draw_polygon，但以 path 表达）

        示例::
            pen.connect_points([(30, 250), (120, 120), (220, 260)],
                               stroke_color="purple", stroke_width=2)
        """
        p = self.path(fill_color=fill_color, stroke_color=stroke_color,
                            stroke_width=stroke_width, stroke_style=stroke_style,
                            opacity=opacity, id_=id_, **extra)
        p.move_to(*points[0])
        for pt in points[1:]:
            p.line_to(*pt)
        if close:
            p.close()
        return p

    def connect_curve(self, points, stroke_color=Color.BLACK,
                      fill_color=Color.TRANSPARENT, stroke_width=1,
                      close=False, opacity=1.0, id_=None, **extra) -> PathElement:
        """
        把顶点列表连成光滑曲线（Catmull-Rom 样条，
        对应中文版 `连曲线`）。 / Connect a list of vertices into a smooth Catmull-Rom curve.

        示例::
            pen.connect_curve([(30, 250), (120, 120), (220, 260), (330, 140)],
                              stroke_color="orangered", stroke_width=3)
        """
        p = self.connect_points(points, stroke_color=stroke_color,
                                fill_color=fill_color, stroke_width=stroke_width,
                                close=close, opacity=opacity, id_=id_, **extra)
        p.smooth()
        return p

    def wave_line(self, start, end, amplitude, periods,
                       stroke_color=Color.BLACK, stroke_width=1, id_=None, **extra) -> PolylineElement:
        """
        画正弦波浪线（对应中文版 `画波浪线`）。 / Draw a sine wave line.

        :param amplitude: 波幅（像素）
        :param periods: 波峰数

        示例::
            pen.draw_wave_line((50, 100), (450, 100), amplitude=15, periods=5,
                               stroke_color="teal", stroke_width=2)
        """
        pts = tools.wave_line_points(start, end, amplitude, periods)
        return self.polyline(pts, stroke_color=stroke_color,
                                  stroke_width=stroke_width, id_=id_, **extra)

    def wavy_line(self, start, end, periods, amplitude_scale=1,
                       stroke_color=Color.BLACK, stroke_width=1, id_=None, **extra) -> PolylineElement:
        """
        画海浪线（对应中文版 `画海浪线`，波幅随距离衰减的正弦线）。 / Draw a sea-wave line.

        示例::
            pen.draw_wavy_line((50, 150), (450, 150), periods=6)
        """
        x1, y1 = start
        x2, y2 = end
        length = math.hypot(x2 - x1, y2 - y1)
        base = length / max(periods, 1) / 4 * amplitude_scale
        pts = []
        n = int(periods) * 24
        ang = math.atan2(y2 - y1, x2 - x1)
        for i in range(n + 1):
            t = i / n
            along = t * length
            off = base * (1 - t) * math.sin(t * periods * 2 * math.pi)
            pts.append((x1 + along * math.cos(ang) - off * math.sin(ang),
                        y1 + along * math.sin(ang) + off * math.cos(ang)))
        return self.polyline(pts, stroke_color=stroke_color,
                                  stroke_width=stroke_width, id_=id_, **extra)

    def h_lines(self, x1, y1, x2, y2=None, count=2, stroke_color=Color.BLACK,
                     stroke_width=1, id_=None, **extra) -> GroupElement:
        """
        画多条水平线（对应中文版 `画水平线`）：在 y1~y2 之间均布 count 条。 / Draw several horizontal lines: count of them spread evenly between y1 and y2.

        示例::
            pen.draw_h_lines(50, 100, 450, 200, count=4)   # 4 条水平线
        """
        if y2 is None:
            y2 = y1
        g = self.g(id_=id_)
        step = (y2 - y1) / max(count - 1, 1) if count > 1 else 0
        for i in range(count):
            ln = self.line((x1, y1 + i * step), (x2, y1 + i * step),
                                stroke_color=stroke_color, stroke_width=stroke_width, **extra)
            ln.change_group(g)
        return g

    def v_lines(self, y1, x1, y2, x2=None, count=2, stroke_color=Color.BLACK,
                     stroke_width=1, id_=None, **extra) -> GroupElement:
        """
        画多条垂直线（对应中文版 `画垂直线`）：在 x1~x2 之间均布 count 条。 / Draw several vertical lines: count of them spread evenly between x1 and x2.

        示例::
            pen.draw_v_lines(100, 50, 300, 350, count=5)
        """
        if x2 is None:
            x2 = x1
        g = self.g(id_=id_)
        step = (x2 - x1) / max(count - 1, 1) if count > 1 else 0
        for i in range(count):
            ln = self.line((x1 + i * step, y1), (x1 + i * step, y2),
                                stroke_color=stroke_color, stroke_width=stroke_width, **extra)
            ln.change_group(g)
        return g

    def table(self, x, y, col_widths, row_heights, rows=1, cols=1,
                   stroke_color=Color.BLACK, stroke_width=1, id_=None, **extra) -> GroupElement:
        """
        画表格（对应中文版 `画表格`）。 / Draw a table.

        :param col_widths: 列宽列表或统一值
        :param row_heights: 行高列表或统一值
        :param rows: 行数
        :param cols: 列数

        示例::
            pen.draw_table(50, 50, [120, 80, 100], 36, rows=5, cols=3)
        """
        if not isinstance(col_widths, (list, tuple)):
            col_widths = [col_widths] * cols
        if not isinstance(row_heights, (list, tuple)):
            row_heights = [row_heights] * rows
        g = self.g(id_=id_)
        # 横线
        yy = float(y)
        ys = [yy]
        for r in range(rows):
            yy += float(row_heights[r % len(row_heights)])
            ys.append(yy)
        for yy2 in ys:
            ln = self.line((x, yy2), (x + sum(col_widths[:cols]), yy2),
                                stroke_color=stroke_color, stroke_width=stroke_width, **extra)
            ln.change_group(g)
        # 竖线
        xx = float(x)
        xs = [xx]
        for c in range(cols):
            xx += float(col_widths[c % len(col_widths)])
            xs.append(xx)
        for xx2 in xs:
            ln = self.line((xx2, y), (xx2, yy),
                                stroke_color=stroke_color, stroke_width=stroke_width, **extra)
            ln.change_group(g)
        return g

    # ------------------------------------------------------------------
    # 箭头
    # ------------------------------------------------------------------

    def arrow_path(self, start, end, style=None, arrow_length=10,
                       arrow_angle=30, shrink_line=True) -> tuple:
        """
        计算箭头信息（对应中文版 `获取箭头路径`）。 / Compute the geometry of an arrowhead.

        :return: (箭头三角形顶点, 线段终点)

        示例::
            tri, line_end = pen.get_arrow_path((50, 50), (300, 50))
        """
        return tools.arrow_path_points(start, end,
                                       style or ArrowStyle.BARBED,
                                       arrow_length, arrow_angle)

    def arrow_line(self, start, end, style=ArrowStyle.BARBED,
                        arrow_length=10, arrow_angle=25,
                        fill_color=Color.TRANSPARENT, stroke_color=Color.BLACK,
                        stroke_width=1, id_=None, **extra) -> GroupElement:
        """
        画带箭头的线段（对应中文版 `箭头线`）。 / Draw a line segment with an arrowhead.

        :param style: ArrowStyle.SOLID（实心）/ HOLLOW（空心）/ BARBED（倒钩）

        示例::
            pen.draw_arrow_line((80, 380), (420, 380), style=ArrowStyle.SOLID,
                                stroke_width=2)
        """
        g = self.g(id_=id_)
        tri, line_end = self.arrow_path(start, end, style, arrow_length, arrow_angle)
        ln = self.line(start, line_end, stroke_color=stroke_color,
                            stroke_width=stroke_width, **extra)
        ln.change_group(g)
        if style == ArrowStyle.SOLID:
            arrow = self.polygon(tri, fill_color=stroke_color,
                                      stroke_color=stroke_color)
        else:
            arrow = self.connect_points(tri, stroke_color=stroke_color,
                                        stroke_width=stroke_width, close=True)
        arrow.change_group(g)
        return g

    # ------------------------------------------------------------------
    # 文字
    # ------------------------------------------------------------------

    # ---- 兼容别名（1.0 早期命名，等价于新名） ----
    begin_path = path
    draw_wave_line = wave_line
    draw_wavy_line = wavy_line
    draw_h_lines = h_lines
    draw_v_lines = v_lines
    draw_table = table
    get_arrow_path = arrow_path
    draw_arrow_line = arrow_line
