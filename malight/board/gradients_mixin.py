# -*- coding: utf-8 -*-
"""
渐变（SVG <linearGradient>/<radialGradient> 及彩虹/黄金快捷）。 / Gradients: SVG linearGradient and radialGradient, plus rainbow and gold shortcuts.

本文件只包含 GradientMixin 一个类（Mixin），由 board/__init__.py 组合进 MagicPen。
"""

from ..elements import (CircleElement, EllipseElement, RectElement,
    LineElement, PolylineElement, PolygonElement, TextElement, TextPathElement,
    ImageElement, SVGImageElement, GroupElement, TemplateElement, UseElement,
    MarkerElement, ClipPathElement, MaskElement, LinkElement, PatternElement,
    _paint, _fmt_points)
from ..definitions import ColorScheme, value_of
from ..gradients import LinearGradient, RadialGradient


class GradientMixin:
    """GradientMixin —— 渐变（SVG <linearGradient>/<radialGradient> 及彩虹/黄金快捷）（方法名与 SVG 元素名对应，旧名保留为别名）。 / GradientMixin - gradients (SVG linearGradient / radialGradient) plus rainbow and gold shortcuts. """

    def linearGradient(self, start, end, start_color, end_color,
                               stops=None, units=None, spread=None,
                               id_=None) -> LinearGradient:
        """
        创建线性渐变（对应中文版 `创建线性渐变色`）。 / Create a linear gradient.

        :param start, end: 渐变向量，如 (0,0)->(1,0)（相对边界框）或像素坐标（配合 units）
        :param stops: 中间色标列表 [(偏移, 颜色, 透明度?), ...]
        :param units: CoordUnits.OBJECT_BOUNDING_BOX（默认）/ USER_SPACE
        :param spread: SpreadMethod.PAD（默认）/ REFLECT / REPEAT

        :return: LinearGradient（直接当 fill_color 用）

        示例::
            grad = pen.linearGradient((0, 0), (1, 0),
                                              "deepskyblue", "navy",
                                              stops=[(0.5, "white")])
            pen.rect(50, 50, 300, 100, fill_color=grad.paint())
        """
        grad = LinearGradient(self, start, end, value_of(units), id_,
                              value_of(spread))
        grad.add_stop(0, _paint(start_color))
        for s in (stops or []):
            grad.add_stop(*s[:2], **({"opacity": s[2]} if len(s) > 2 else {}))
        grad.add_stop(1, _paint(end_color))
        return grad

    def radialGradient(self, center, radius, start_color, end_color,
                               stops=None, focal=None, units=None, spread=None,
                               id_=None) -> RadialGradient:
        """
        创建径向渐变（对应中文版 `创建径向渐变色`）。 / Create a radial gradient.

        示例::
            sun = pen.radialGradient((0.5, 0.5), 0.5,
                                             "white", "orange")
            pen.circle(250, 120, 90, fill_color=sun.paint())
        """
        grad = RadialGradient(self, center, radius, focal, value_of(units),
                              id_, value_of(spread))
        grad.add_stop(0, _paint(start_color))
        for s in (stops or []):
            grad.add_stop(*s[:2])
        grad.add_stop(1, _paint(end_color))
        return grad

    def rainbow_stops(self, colors=None) -> list:
        """
        生成彩虹七色渐变stops（对应中文版 `彩虹渐变点`）。 / Build the seven rainbow gradient stops.

        示例::
            grad = pen.linearGradient((0, 0), (1, 0), "red", "violet")
            # 七色版：
            grad = pen.linearGradient((0, 0), (1, 0), *pen.rainbow_stops()[:2])
        """
        colors = colors or ColorScheme.RAINBOW
        n = len(colors)
        return [(i / (n - 1), c) for i, c in enumerate(colors)]

    def rainbow_linear_gradient(self, start=(0, 0), end=(1, 0),
                                       colors=None, id_=None) -> LinearGradient:
        """
        创建彩虹线性渐变（对应中文版 `创建彩虹线性渐变色`）。 / Create a rainbow linear gradient.

        示例::
            grad = pen.create_rainbow_linear_gradient()
            pen.rect(50, 50, 300, 80, fill_color=grad.paint())
        """
        colors = colors or ["#FF0000", "#FF7F00", "#FFFF00", "#00FF00",
                            "#0000FF", "#4B0082", "#8B00FF"]
        grad = LinearGradient(self, start, end, id_=id_)
        n = len(colors)
        for i, c in enumerate(colors):
            grad.add_stop(i / (n - 1), c)
        return grad

    def rainbow_radial_gradient(self, center=(0.5, 0.5), radius=0.5,
                                       colors=None, id_=None) -> RadialGradient:
        """
        创建彩虹径向渐变（对应中文版 `创建彩虹径向渐变色`）。 / Create a rainbow radial gradient.

        示例::
            grad = pen.create_rainbow_radial_gradient()
            pen.circle(250, 150, 120, fill_color=grad.paint())
        """
        colors = colors or ["#FF0000", "#FF7F00", "#FFFF00", "#00FF00",
                            "#0000FF", "#4B0082", "#8B00FF"]
        grad = RadialGradient(self, center, radius, id_=id_)
        n = len(colors)
        for i, c in enumerate(colors):
            grad.add_stop(i / (n - 1), c)
        return grad

    def gold_linear_gradient(self, start=(0, 0), end=(0, 1), id_=None) -> LinearGradient:
        """
        创建黄金质感渐变（对应中文版 `创建黄金线性渐变色`）。 / Create a gold-textured gradient.

        示例::
            grad = pen.create_gold_linear_gradient()
            pen.text(100, 150, "GOLD", font_size=64,
                           fill_color=grad.paint())
        """
        grad = LinearGradient(self, start, end, id_=id_)
        for off, c in [(0, "#8a6d1d"), (0.25, "#ffe066"), (0.5, "#b8860b"),
                       (0.75, "#fff3b0"), (1, "#8a6d1d")]:
            grad.add_stop(off, c)
        return grad

    # ------------------------------------------------------------------
    # JavaScript / 信息
    # ------------------------------------------------------------------

    # ---- 兼容别名（1.0 早期命名，等价于新名） ----
    create_linear_gradient = linearGradient
    create_radial_gradient = radialGradient
    create_rainbow_linear_gradient = rainbow_linear_gradient
    create_rainbow_radial_gradient = rainbow_radial_gradient
    create_gold_linear_gradient = gold_linear_gradient
