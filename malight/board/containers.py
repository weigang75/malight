# -*- coding: utf-8 -*-
"""
容器元素（g/symbol/use/pattern/marker/a）。 / Container elements: g, symbol, use, pattern, marker and a.

本文件只包含 ContainerMixin 一个类（Mixin），由 board/__init__.py 组合进 MagicPen。
"""

from ..elements import (Element, CircleElement, EllipseElement, RectElement,
    LineElement, PolylineElement, PolygonElement, TextElement, TextPathElement,
    ImageElement, SVGImageElement, GroupElement, TemplateElement, UseElement,
    MarkerElement, ClipPathElement, MaskElement, LinkElement, PatternElement,
    _paint, _fmt_points)


class ContainerMixin:
    """ContainerMixin —— 容器元素（g/symbol/use/pattern/marker/a）（方法名与 SVG 元素名对应，旧名保留为别名）。 / ContainerMixin - container elements (g / symbol / use / pattern / marker / a). """

    def g(self, class_name=None, style_str=None, opacity=None,
               blend_mode=None, filter=None, id_=None, **kw) -> GroupElement:
        """
        创建组元素（对应中文版 `创建组合`）。 / Create a group element.

        :param opacity: 整组透明度
        :param blend_mode: BlendMode 整组混合模式
        :param filter: 整组共用一个滤镜（如统一投影）

        示例::
            g = pen.g(id="car")
            # 把多个元素 change_group(g) 或 g.add_element(el)
        """
        return self._new(GroupElement, class_name=class_name,
                         style_str=style_str, id_=id_,
                         opacity=opacity, blend_mode=blend_mode, filter=filter,
                         **kw)

    def symbol(self, id_=None, view_box=None) -> TemplateElement:
        """
        创建模板（<symbol>，对应中文版 `创建模板`）。 / Create a symbol (reusable template).

        示例::
            t = pen.symbol(id="icon_star", view_box="0 0 40 40")
            t.add_element(pen.polygon([(20, 2), (38, 36), (2, 36)], fill_color="gold"))
            pen.template("icon_star", x=60, y=60, width=40, height=40)
        """
        return self._new(TemplateElement, view_box=view_box, id_=id_)

    def use(self, template_id, x=None, y=None, width=None, height=None, **kw) -> UseElement:
        """
        实例化模板（<use>，对应中文版 `神笔模板`）。 / Instantiate a symbol with a <use> element.

        示例::
            pen.template("icon_star", x=120, y=60, width=40, height=40)
        """
        return self._new(UseElement, href=f"#{template_id}", x=x, y=y,
                         width=width, height=height, **kw)

    def pattern(self, x, y, width, height, id_=None, **kw) -> PatternElement:
        """
        创建平铺图案（对应中文版 `创建图案`）。 / Create a tiling pattern fill.

        示例::
            p = pen.pattern(0, 0, 20, 20, id_="dots")
            p.add_element(pen.circle(10, 10, 3, fill_color="gray"))
            pen.rect(20, 20, 200, 100, fill_color="url(#dots)")
        """
        return self._new(PatternElement, x=x, y=y, width=width, height=height,
                         id_=id_, **kw)

    def copy(self, el, x=None, y=None, opacity=1.0, id_=None) -> "Element":
        """
        复制元素（对应中文版 `复制元素`），可指定偏移。 / Duplicate an element, optionally with an offset.

        示例::
            twin = pen.copy(shape, x=120, y=0)
        """
        dx = (x - el.bbox()[0]) if (x is not None and el.bbox()) else 0
        dy = (y - el.bbox()[1]) if (y is not None and el.bbox()) else 0
        return el.clone(dx=dx, dy=dy, id_=id_)

    def a(self, el, url, tooltip=None, description=None, id_=None) -> LinkElement:
        """
        给元素加超链接（对应中文版 `创建链接`）。 / Wrap an element in a hyperlink.

        :param el: 要包成链接的元素；传 None 则只建一个空 ``<a>``，
                   之后用 ``link.wrap(元素)`` 塞进去
        :param tooltip: 鼠标悬停提示（用 SVG 原生 <title> 实现）
        :param description: 无障碍说明（用 SVG 原生 <desc> 实现）

        示例::
            btn = pen.rect(50, 50, 120, 40, fill_color="steelblue")
            pen.a(btn, "https://example.com", tooltip="点我")
        """
        link = self._new(LinkElement, href=url, tooltip=tooltip,
                         description=description, id_=id_)
        if el is not None:
            link.wrap(el)
        return link

    def marker(self, id_=None, ref_x=0, ref_y=0, width=10, height=10,
               orient="auto", marker_units=None) -> MarkerElement:
        """
        创建线端标记（<marker>，对应中文版 `创建标记`）。 / Create a line-end marker such as an arrowhead.

        :param ref_x, ref_y: 参考点（箭头尖端位置，如箭头三角形尖端取 (9, 3)）
        :param width, height: 标记视口尺寸（对应 markerWidth / markerHeight）
        :param orient: 方向。``"auto"`` 跟随线方向（默认，画箭头必选）；
                       ``"auto-start-reverse"`` 起点自动反向；也可写角度 ``"45"``
        :param marker_units: ``"strokeWidth"``（默认，随线宽缩放）或
                             ``"userSpaceOnUse"``（固定像素，线宽变化时不缩放）

        示例::
            m = pen.marker(id_="arrow", ref_x=9, ref_y=3, width=10, height=6)
            m.add_element(pen.polygon([(0, 0), (9, 3), (0, 6)], fill_color="black"))
            pen.line((10, 10), (250, 10), extra={"marker_end": "url(#arrow)"})
        """
        return self._new(MarkerElement, id_=id_, ref_x=ref_x, ref_y=ref_y,
                         marker_width=width, marker_height=height,
                         orient=orient, marker_units=marker_units)

    # ------------------------------------------------------------------
    # 图像
    # ------------------------------------------------------------------

    # ---- 兼容别名（1.0 早期命名，等价于新名） ----
    create_group = g
    create_template = symbol
    template = use
    create_pattern = pattern
    copy_element = copy
    create_link = a
    create_marker = marker
