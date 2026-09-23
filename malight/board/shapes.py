# -*- coding: utf-8 -*-
"""
基本图形（SVG 元素命名：circle/ellipse/rect/...）。 / Basic shapes, each method named after its SVG element.

本文件只包含 ShapeMixin 一个类（Mixin），由 board/__init__.py 组合进 MagicPen。
"""

from ..definitions import (Color, PaperSize, PaperSettings,
    StrokeCap, StrokeJoin, ArrowStyle, PointStyle, TextHAlign, TextVAlign,
    GridRepeatType, CoordUnits, PNGMode, PDFMode, DOCXMode, SystemFont)
from ..elements import (CircleElement, EllipseElement, RectElement,
    LineElement, PolylineElement, PolygonElement, TextElement, TextPathElement,
    ImageElement, SVGImageElement, GroupElement, TemplateElement, UseElement,
    MarkerElement, ClipPathElement, MaskElement, LinkElement, PatternElement,
    _paint, _fmt_points)
from .. import tools


class ShapeMixin:
    """ShapeMixin —— 基本图形（SVG 元素命名：circle/ellipse/rect/...）（方法名与 SVG 元素名对应，旧名保留为别名）。 / ShapeMixin - basic shapes, named after their SVG elements (circle / ellipse / rect / ...). """

    def circle(self, x, y, radius, fill_color=Color.TRANSPARENT,
                    stroke_color=Color.BLACK, stroke_width=1.0,
                    stroke_style=None, stroke_cap=None, stroke_join=None,
                    fill_rule=None, dash_offset=None, blend_mode=None,
                    filter=None, opacity=1.0, id_=None, **extra) -> CircleElement:
        """
        画圆（对应中文版 `画圆`）。 / Draw a circle.

        :param x: 圆心 x
        :param y: 圆心 y
        :param radius: 半径
        :param fill_color: 填充色（Color.TRANSPARENT 表示不填充）
        :param stroke_color: 描边色
        :param stroke_width: 描边宽
        :param stroke_style: 虚线样式，如 "8 4"
        :param stroke_cap: StrokeCap.BUTT / ROUND / SQUARE（线端形状）
        :param stroke_join: StrokeJoin.MITER / ROUND / BEVEL（拐角形状）
        :param fill_rule: FillRule.EVENODD 可挖洞（甜甜圈/镂空字）
        :param dash_offset: 虚线相位偏移（蚂蚁线动画起点）
        :param blend_mode: BlendMode.MULTIPLY 等（CSS 混合模式）
        :param filter: pen.fx.shadow(...) 等滤镜，一行加特效
        :param opacity: 整体透明度 0~1
        :param id_: 元素 id
        :param extra: 任意 SVG 属性（英文版新增），如 filter="url(#f1)"

        :return: CircleElement

        示例::
            pen.circle(200, 150, 80, fill_color=Color.RGB(30, 144, 255),
                            stroke_color="navy", stroke_width=3)
        """
        return self._new(CircleElement, x=x, y=y, radius=radius,
                         fill_color=fill_color, stroke_color=stroke_color,
                         stroke_width=stroke_width, stroke_style=stroke_style,
                         opacity=opacity, id_=id_, extra=extra or None,
                         stroke_cap=stroke_cap, stroke_join=stroke_join, fill_rule=fill_rule,
                         blend_mode=blend_mode, filter=filter, dash_offset=dash_offset)

    def ellipse(self, x, y, radius, fill_color=Color.TRANSPARENT,
                     stroke_color=Color.BLACK, stroke_width=1.0,
                     stroke_style=None, stroke_cap=None, stroke_join=None,
                     fill_rule=None, dash_offset=None, blend_mode=None,
                     filter=None, opacity=1.0, rotate=None,
                     id_=None, **extra) -> EllipseElement:
        """
        画椭圆（对应中文版 `画椭圆`）。 / Draw an ellipse.

        :param radius: (rx, ry)；传单个数值则为正圆
        :param rotate: 旋转角度（度）—— 英文版新增，原版不支持旋转椭圆

        :param stroke_cap: StrokeCap 线端形状
        :param stroke_join: StrokeJoin 拐角形状
        :param fill_rule: FillRule.EVENODD 可挖洞
        :param dash_offset: 虚线相位偏移
        :param blend_mode: BlendMode 混合模式
        :param filter: 滤镜，如 pen.fx.blur(3)

        示例::
            pen.ellipse(300, 150, radius=(120, 50), rotate=-20,
                             fill_color="skyblue")
        """
        return self._new(EllipseElement, x=x, y=y, radius=radius,
                         fill_color=fill_color, stroke_color=stroke_color,
                         stroke_width=stroke_width, stroke_style=stroke_style,
                         opacity=opacity, rotate=rotate, id_=id_, extra=extra or None,
                         stroke_cap=stroke_cap, stroke_join=stroke_join, fill_rule=fill_rule,
                         blend_mode=blend_mode, filter=filter, dash_offset=dash_offset)

    def rect(self, x, y, width, height, corner_radius=None,
                  fill_color=Color.TRANSPARENT, stroke_color=Color.BLACK,
                  stroke_width=1, stroke_style=None, stroke_cap=None,
                  stroke_join=None, fill_rule=None, dash_offset=None,
                  blend_mode=None, filter=None, opacity=1.0, rotate=None,
                  id_=None, **extra) -> RectElement:
        """
        画矩形（对应中文版 `画矩形`）。 / Draw a rectangle.

        :param corner_radius: 圆角半径
        :param stroke_cap: StrokeCap 线端形状
        :param stroke_join: StrokeJoin 拐角形状
        :param fill_rule: FillRule.EVENODD 可挖洞
        :param dash_offset: 虚线相位偏移
        :param blend_mode: BlendMode 混合模式
        :param filter: 滤镜，如 pen.fx.shadow(6, 7, 8)
        :param rotate: 旋转角度（度，绕矩形中心）—— 英文版新增

        示例::
            pen.rect(50, 50, 220, 120, corner_radius=14,
                          fill_color="cornflowerblue", rotate=6)
        """
        return self._new(RectElement, x=x, y=y, width=width, height=height,
                         corner_radius=corner_radius, fill_color=fill_color,
                         stroke_color=stroke_color, stroke_width=stroke_width,
                         stroke_style=stroke_style, opacity=opacity,
                         rotate=rotate, id_=id_, extra=extra or None,
                         stroke_cap=stroke_cap, stroke_join=stroke_join, fill_rule=fill_rule,
                         blend_mode=blend_mode, filter=filter, dash_offset=dash_offset)

    def square(self, x, y, side, **kw) -> RectElement:
        """
        画正方形（对应中文版 `画正方形`）。 / Draw a square.

        示例::
            pen.draw_square(50, 50, 120, fill_color="teal")
        """
        return self.rect(x, y, side, side, **kw)

    def line(self, start, end, stroke_color=Color.BLACK,
                  fill_color=Color.TRANSPARENT, stroke_width=1,
                  stroke_style=None, stroke_cap=None, stroke_join=None,
                  dash_offset=None, blend_mode=None, filter=None,
                  opacity=1.0, id_=None, **extra) -> LineElement:
        """
        画一条线段（对应中文版 `画线`/`画直线`）。 / Draw a line segment.

        :param stroke_cap: StrokeCap.ROUND 可画圆头「胶囊线」
        :param stroke_join: StrokeJoin 拐角形状
        :param dash_offset: 虚线相位偏移
        :param blend_mode: BlendMode 混合模式
        :param filter: 滤镜，如 pen.fx.glow(4, "gold")
        :param start: 起点 (x, y)
        :param end: 终点 (x, y)

        示例::
            pen.line((50, 300), (400, 300), stroke_width=3,
                          stroke_style="10 5", stroke_cap=StrokeCap.ROUND)
        """
        return self._new(LineElement, start=start, end=end,
                         stroke_color=stroke_color, fill_color=fill_color,
                         stroke_width=stroke_width, stroke_style=stroke_style,
                         stroke_cap=stroke_cap, stroke_join=stroke_join,
                         opacity=opacity, id_=id_, extra=extra or None,
                         blend_mode=blend_mode, filter=filter, dash_offset=dash_offset)

    def cross(self, x, y, width=5, height=5, color=Color.BLACK,
                   stroke_width=1, id_=None) -> GroupElement:
        """
        画十字标记（对应中文版 `十字`），常用于标注关键点。 / Draw a cross marker, often used to label key points.

        示例::
            pen.draw_cross(200, 150, width=8, color=Color.RED)
        """
        g = self.g(id_=id_)
        self.line((x - width, y), (x + width, y),
                       stroke_color=color, stroke_width=stroke_width).change_group(g)
        self.line((x, y - height), (x, y + height),
                       stroke_color=color, stroke_width=stroke_width).change_group(g)
        return g

    def polyline(self, points, fill_color=Color.TRANSPARENT,
                      stroke_color=Color.BLACK, stroke_width=1,
                      stroke_style=None, stroke_cap=None, stroke_join=None,
                      dash_offset=None, blend_mode=None, filter=None,
                      opacity=1.0, id_=None, **extra) -> PolylineElement:
        """
        画折线元素（顶点直连，对应中文版 `画折线`）。 / Draw a polyline element.

        :param stroke_cap: StrokeCap 线端形状
        :param stroke_join: StrokeJoin 拐角形状
        :param dash_offset: 虚线相位偏移
        :param blend_mode: BlendMode 混合模式
        :param filter: 滤镜

        示例::
            pen.polyline([(20, 200), (100, 80), (180, 200), (260, 100)],
                              stroke_color="green", stroke_width=3)
        """
        return self._new(PolylineElement, points=points,
                         fill_color=fill_color, stroke_color=stroke_color,
                         stroke_width=stroke_width, stroke_style=stroke_style,
                         opacity=opacity, id_=id_, extra=extra or None,
                         stroke_cap=stroke_cap, stroke_join=stroke_join,
                         blend_mode=blend_mode, filter=filter, dash_offset=dash_offset)

    def polygon(self, points, fill_color=Color.TRANSPARENT,
                     stroke_color=Color.BLACK, stroke_width=1,
                     stroke_style=None, stroke_cap=None, stroke_join=None,
                     fill_rule=None, dash_offset=None, blend_mode=None,
                     filter=None, opacity=1.0, id_=None, **extra) -> PolygonElement:
        """
        画多边形（自动闭合，对应中文版 `画多边形`）。 / Draw a polygon.

        英文版增强：``fill_rule="evenodd"`` 可实现带孔多边形
        （原版不支持，这是复刻简笔画挖洞效果的关键能力）。

        :param stroke_cap: StrokeCap 线端形状
        :param stroke_join: StrokeJoin 拐角形状
        :param fill_rule: FillRule.EVENODD 可挖洞
        :param dash_offset: 虚线相位偏移
        :param blend_mode: BlendMode 混合模式
        :param filter: 滤镜

        示例::
            outer = [(50, 50), (250, 50), (250, 200), (50, 200)]
            hole = [(100, 90), (200, 90), (200, 160), (100, 160)]
            pen.polygon(outer + hole, fill_color="teal", fill_rule="evenodd")
        """
        return self._new(PolygonElement, points=points,
                         fill_color=fill_color, stroke_color=stroke_color,
                         stroke_width=stroke_width, stroke_style=stroke_style,
                         opacity=opacity, fill_rule=fill_rule,
                         id_=id_, extra=extra or None,
                         stroke_cap=stroke_cap, stroke_join=stroke_join,
                         blend_mode=blend_mode, filter=filter, dash_offset=dash_offset)

    def regular_polygon(self, x, y, radius, n, stroke_color=Color.BLACK,
                             fill_color=Color.TRANSPARENT, stroke_width=1,
                             opacity=1.0, id_=None, **extra) -> PolygonElement:
        """
        画正 N 边形（对应中文版 `画正N边形`）。 / Draw a regular N-sided polygon.

        :param n: 边数（3 以上）

        示例::
            pen.draw_regular_polygon(200, 150, 90, 6, fill_color="honeydew",
                                     stroke_color="seagreen")   # 正六边形
        """
        pts = tools.regular_polygon_points(x, y, radius, n)
        return self.polygon(pts, fill_color=fill_color,
                                 stroke_color=stroke_color,
                                 stroke_width=stroke_width, opacity=opacity,
                                 id_=id_, **extra)

    def triangle(self, x, y, radius, **kw) -> PolygonElement:
        """画正三角形（对应中文版 `画正三边形`）。 / Draw an equilateral triangle.

        示例:: pen.draw_triangle(150, 150, 80, fill_color="lightblue")
        """
        return self.regular_polygon(x, y, radius, 3, **kw)

    def pentagon(self, x, y, radius, **kw) -> PolygonElement:
        """画正五边形（对应中文版 `画正五边形`）。 / Draw a regular pentagon.

        示例:: pen.draw_pentagon(150, 150, 80, fill_color="wheat")
        """
        return self.regular_polygon(x, y, radius, 5, **kw)

    def hexagon(self, x, y, radius, **kw) -> PolygonElement:
        """画正六边形（对应中文版 `画正六边形`）。 / Draw a regular hexagon.

        示例:: pen.draw_hexagon(150, 150, 80, fill_color="lavender")
        """
        return self.regular_polygon(x, y, radius, 6, **kw)

    def star(self, x, y, radius, n=5, inner_ratio=None,
                  stroke_color=Color.BLACK, fill_color=Color.TRANSPARENT,
                  stroke_width=1, opacity=1.0, id_=None, **extra) -> PolygonElement:
        """
        画 N 角星（对应中文版 `画N角星`/`画五角星` 等）。 / Draw an N-pointed star.

        :param n: 角数（5 = 五角星）
        :param inner_ratio: 内角点半径比（默认按角数自动取值）

        示例::
            pen.star(200, 150, 100, n=5, fill_color="gold")     # 五角星
            pen.star(400, 150, 80, n=6, fill_color="red")       # 六角星
        """
        if inner_ratio is None:
            inner_ratio = {3: 0.3, 4: 0.35, 5: 0.382, 6: 0.6}.get(n, 0.382)
        pts = tools.star_points(x, y, radius, n, inner_ratio)
        return self.polygon(pts, fill_color=fill_color,
                                 stroke_color=stroke_color,
                                 stroke_width=stroke_width, opacity=opacity,
                                 id_=id_, **extra)

    def diamond(self, x, y, radius, stroke_color=Color.BLACK,
                     fill_color=Color.TRANSPARENT, stroke_width=1, id_=None, **extra) -> PolygonElement:
        """
        画菱形（对应中文版 `画菱型`）。 / Draw a diamond.

        示例::
            pen.draw_diamond(200, 150, 90, fill_color="crimson")
        """
        pts = [(x, y - radius), (x + radius, y), (x, y + radius), (x - radius, y)]
        return self.polygon(pts, fill_color=fill_color,
                                 stroke_color=stroke_color,
                                 stroke_width=stroke_width, id_=id_, **extra)

    def heart(self, x, y, size, stroke_color=Color.BLACK,
                   fill_color=Color.TRANSPARENT, stroke_width=1, id_=None, **extra) -> PolygonElement:
        """
        画爱心（对应中文版 `画爱心`）。 / Draw a heart.

        :param size: 尺寸量级（半径感）

        示例::
            pen.heart(200, 150, 80, fill_color=Color.RED)
        """
        pts = tools.heart_points(x, y, size)
        return self.polygon(pts, fill_color=fill_color,
                                 stroke_color=stroke_color,
                                 stroke_width=stroke_width, id_=id_, **extra)

    # ------------------------------------------------------------------
    # 路径与连线
    # ------------------------------------------------------------------

    # ---- 兼容别名（1.0 早期命名，等价于新名） ----
    draw_circle = circle
    draw_ellipse = ellipse
    draw_rect = rect
    draw_square = square
    draw_line = line
    draw_cross = cross
    draw_polyline = polyline
    draw_polygon = polygon
    draw_regular_polygon = regular_polygon
    draw_triangle = triangle
    draw_pentagon = pentagon
    draw_hexagon = hexagon
    draw_star = star
    draw_diamond = diamond
    draw_heart = heart
