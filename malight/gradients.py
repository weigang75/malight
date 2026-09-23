# -*- coding: utf-8 -*-
"""
渐变色（gradients）—— 线性/径向渐变定义
==========================================

Linear and radial gradient definitions.

对应中文版《神笔码靓》的 `元素库/渐变色.py`。
渐变定义放入 <defs>，返回值可作为填充/描边颜色直接使用。

示例::

    from malight import MagicPen
    pen = MagicPen("demo_gradient", width=500, height=300)

    # 线性渐变：从左上到右下，红到蓝
    grad = pen.linearGradient((0, 0), (1, 1), "red", "blue")

    # 径向渐变：金色太阳
    sun = pen.radialGradient((250, 120), 90, "white", "orange")

    pen.rect(50, 180, 400, 80, fill_color=grad)
    pen.circle(250, 120, 90, fill_color=sun)
    pen.finish()
"""

from .svg_backend import SvgNode, fmt_num
from .definitions import value_of


class _GradientBase:
    """渐变基类：管理色标（stop）与坐标单位（内部使用）。 / Gradient base class managing stops and coordinate units (internal). """

    def __init__(self, board, tag, units=None, id_=None, spread=None):
        """
        :param board: 所属绘图板
        :param tag: "linearGradient" 或 "radialGradient"
        :param units: CoordUnits.USER_SPACE / OBJECT_BOUNDING_BOX
        :param id_: 显式指定渐变 id
        :param spread: SpreadMethod 扩散方式（英文版新增，可写枚举或字符串）
        """
        self.board = board
        self.node = SvgNode(tag)
        self.node.set("id", id_ or board._gen_id("grad"))
        self.node.set("gradientUnits", value_of(units) or "objectBoundingBox")
        if spread is not None:
            self.node.set("spreadMethod", value_of(spread))
        board.defs_node.add(self.node)

    @property
    def id(self) -> str:
        """渐变 id（引用时用 ``url(#id)``）。 / The gradient id; reference it as ``url(#id)``. """
        return self.node.attribs["id"]

    def paint(self) -> str:
        """
        返回 paint 引用串，可直接作为 fill_color/stroke_color 使用。 / Return the paint reference string, usable directly as fill_color/stroke_color.

        示例::
            pen.rect(0, 0, 100, 50, fill_color=grad.paint())
        """
        return f"url(#{self.id})"

    def add_stop(self, offset, color, opacity=1.0) -> "_GradientBase":
        """
        添加渐变色标（对应中文版 `增加渐变中间点` 的单点操作）。 / Add a gradient color stop.

        :param offset: 位置，0~1 或 "35%"
        :param color: 颜色值
        :param opacity: 该色标透明度

        示例::
            grad.add_stop(0.5, "yellow")
        """
        stop = SvgNode("stop")
        stop.set("offset", offset if isinstance(offset, str) else f"{fmt_num(offset * 100)}%")
        stop.set("stop-color", color)
        if opacity < 1.0:
            stop.set("stop-opacity", opacity)
        self.node.add(stop)
        return self

    # 渐变自身的几何变换（对应中文版 渐变色的 变换方法）
    def gradient_transform(self, transform_str) -> "_GradientBase":
        """
        设置渐变的 gradientTransform（原始变换串）。 / Set the gradient's gradientTransform from a raw transform string.

        示例::
            grad.gradient_transform("rotate(45 0.5 0.5)")
        """
        self.node.set("gradientTransform", transform_str)
        return self


class LinearGradient(_GradientBase):
    """
    线性渐变（对应中文版 `线性渐变色`）。 / Linear gradient.

    由 ``pen.linearGradient(...)`` 创建。

    示例::
        grad = pen.linearGradient((0, 0), (1, 0),
                                          "deepskyblue", "navy",
                                          stops=[(0.5, "white")])
    """

    def __init__(self, board, start=(0, 0), end=(1, 0), units=None, id_=None,
                 spread=None):
        super().__init__(board, "linearGradient", units, id_, spread)
        self.node.set("x1", start[0] if isinstance(start[0], str) else fmt_num(start[0]))
        self.node.set("y1", start[1] if isinstance(start[1], str) else fmt_num(start[1]))
        self.node.set("x2", end[0] if isinstance(end[0], str) else fmt_num(end[0]))
        self.node.set("y2", end[1] if isinstance(end[1], str) else fmt_num(end[1]))


class RadialGradient(_GradientBase):
    """
    径向渐变（对应中文版 `径向渐变色`）。 / Radial gradient.

    由 ``pen.radialGradient(...)`` 创建。

    示例::
        grad = pen.radialGradient((0.5, 0.5), 0.6, "white", "black")
        pen.circle(100, 100, 80, fill_color=grad.paint())
    """

    def __init__(self, board, center=(0.5, 0.5), radius=0.5, focal=None,
                 units=None, id_=None, spread=None):
        super().__init__(board, "radialGradient", units, id_, spread)
        cx, cy = center
        self.node.set("cx", cx if isinstance(cx, str) else fmt_num(cx))
        self.node.set("cy", cy if isinstance(cy, str) else fmt_num(cy))
        self.node.set("r", radius if isinstance(radius, str) else fmt_num(radius))
        if focal:
            fx, fy = focal
            self.node.set("fx", fmt_num(fx))
            self.node.set("fy", fmt_num(fy))
