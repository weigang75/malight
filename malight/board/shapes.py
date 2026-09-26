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


def _var_name_for(value):
    """
    在调用方的局部/全局变量里找 value 是哪个变量名（`locate` 的标签用）。 / Find which variable name in the caller's scope refers to value (used by `locate` labels).

    只认「同一个对象」（``is``）；字面量元组查不到，返回 None。
    / Identity-based (``is``) lookup; literal tuples are not found and yield None.
    """
    import inspect
    frame = inspect.currentframe()
    try:
        caller = frame.f_back.f_back if frame and frame.f_back else None
        if caller is None:
            return None
        for scope in (caller.f_locals, caller.f_globals):
            for name, val in scope.items():
                if name.startswith("_") or callable(val):
                    continue
                if val is value:
                    return name
        return None
    finally:
        del frame


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
                   stroke_width=1, id_=None, **kw) -> GroupElement:
        """
        画十字标记（对应中文版 `十字`），常用于标注关键点。 / Draw a cross marker, often used to label key points.

        :param kw: 组的公共样式参数（opacity / blend_mode / filter 等）

        示例::
            pen.draw_cross(200, 150, width=8, color=Color.RED)
        """
        g = self.g(id_=id_, **kw)
        self.line((x - width, y), (x + width, y),
                       stroke_color=color, stroke_width=stroke_width).change_group(g)
        self.line((x, y - height), (x, y + height),
                       stroke_color=color, stroke_width=stroke_width).change_group(g)
        return g

    def locate(self, *points, labels=None, color=Color.RED, size=8,
               font_size=12, offset=None, font_color=None,
               stroke_width=1, id_=None, **kw) -> GroupElement:
        """
        在给定点画定位十字光标（对应中文版 `定位`），用于调试时查看点在画面上的位置。 / Draw locating crosshairs at the given points (the Chinese edition's locate), for debugging point positions.

        每个点 = 十字光标 + 文本标签。标签文本按优先级取：
        ``labels`` 里指定的名称 > 调用处**变量名**（如 ``pen.locate(a, b)``
        会标出 "a"、"b"，用 ``inspect`` 读调用帧实现）> 坐标文本 ``(x, y)``。
        标记大小（``size``）、字号（``font_size``）、颜色（``color``）、
        文字偏移（``offset``）均可调。

        :param points: 任意个 (x, y) 元组
        :param labels: 与 points 等长的名称列表；缺省时先取变量名，再退坐标文本
        :param color: 十字与文字颜色（默认红）
        :param size: 十字臂长（像素），即十字总宽的 1/2
        :param font_size: 标签字号
        :param offset: 标签相对点的偏移 (dx, dy)；缺省 (size + 2, size + 2)
        :param font_color: 文字颜色；缺省跟随 color
        :param stroke_width: 十字线宽
        :param id_: 元素 id
        :param kw: 组的公共样式参数（opacity / blend_mode / filter 等）

        :return: GroupElement（所有定位标记的组合）

        示例::

            a, b = (60, 320), (380, 190)
            pen.locate(a, b)                          # 十字旁标出 a、b
            pen.locate(a, labels=["起点"])             # 自定义名称
            pen.locate((10, 20), size=12, color=Color.BLUE, font_size=14)
        """
        outer = self.g(id_=id_, **kw)
        for i, p in enumerate(points):
            x, y = float(p[0]), float(p[1])
            if labels is not None and i < len(labels):
                label = labels[i]
            else:
                label = _var_name_for(p) or "({:g}, {:g})".format(x, y)
            self.cross(x, y, width=size, height=size, color=color,
                       stroke_width=stroke_width).change_group(outer)
            dx, dy = offset if offset is not None else (size + 2, size + 2)
            self.text(x + dx, y + dy, label, font_size=font_size,
                      fill_color=font_color or color).change_group(outer)
        return outer

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
