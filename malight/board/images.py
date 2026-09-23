# -*- coding: utf-8 -*-
"""
图像（<image> 贴图与 SVG 导入）。 / Images: bitmap <image> placement and SVG import.

本文件只包含 ImageMixin 一个类（Mixin），由 board/__init__.py 组合进 MagicPen。
"""

from ..svg_backend import SvgNode, fmt_num
from ..elements import (CircleElement, EllipseElement, RectElement,
    LineElement, PolylineElement, PolygonElement, TextElement, TextPathElement,
    ImageElement, SVGImageElement, GroupElement, TemplateElement, UseElement,
    MarkerElement, ClipPathElement, MaskElement, LinkElement, PatternElement,
    _paint, _fmt_points)
from .. import tools


class ImageMixin:
    """ImageMixin —— 图像（<image> 贴图与 SVG 导入）（方法名与 SVG 元素名对应，旧名保留为别名）。 / ImageMixin - images (bitmap <image> and SVG import). """

    def image(self, image_file, x=0, y=0, width=None, height=None,
                    opacity=1.0, rendering=None, aspect=None, external=False,
                    blend_mode=None, filter=None, id_=None, **extra) -> ImageElement:
        """
        贴位图（对应中文版 `贴图`）。本地文件自动 base64 内嵌。 / Place a bitmap; local files are base64-embedded automatically.

        :param rendering: ImageRendering.CRISP_EDGES / PIXELATED（放大不糊）
        :param aspect: AspectRatio.MEET（完整显示，默认）/ SLICE（铺满裁切）
        :param external: True 只外链不内嵌（SVG 体积小，但需联网）
        :param blend_mode: BlendMode 混合模式
        :param filter: 滤镜
        :param image_file: 图片路径或 http(s) 地址

        示例::
            pen.image("photo.jpg", x=20, y=20, width=400)
        """
        return self._new(ImageElement, href=str(image_file), x=x, y=y,
                         width=width, height=height, opacity=opacity,
                         rendering=rendering, id_=id_, extra=extra or None,
                         aspect=aspect, external=external, blend_mode=blend_mode, filter=filter)

    def paste_svg(self, svg_file, x=0, y=0, width=None, height=None,
                        opacity=None, blend_mode=None, filter=None,
                        id_=None) -> SVGImageElement:
        """
        贴 SVG 文件（对应中文版 `SVG贴图`）。 / Place an SVG file as an image.

        :param opacity: 透明度 0~1
        :param blend_mode: BlendMode 混合模式
        :param filter: 滤镜

        示例::
            pen.paste_svg("icon.svg", x=10, y=10, width=120)
        """
        return self._new(SVGImageElement, svg_file=str(svg_file), x=x, y=y,
                         width=width, height=height, id_=id_,
                         opacity=opacity, blend_mode=blend_mode, filter=filter)

    def import_svg_as_group(self, svg_file, x=0, y=0, scale=None) -> SvgNode:
        """
        把 SVG 文件内容解析为可编辑组（对应中文版 `导入SVG为组`）。 / Parse an SVG file into an editable group.

        与 paste_svg 的区别：导入后每个图形都是独立节点，可二次编辑。

        示例::
            g = pen.import_svg_as_group("icon.svg", x=10, y=10, scale=0.5)
        """
        node, w, h = tools.import_svg_as_nodes(svg_file, x=x, y=y, scale=scale)
        self.canvas_node.add(node)
        return node

    def import_svg_as_symbol(self, svg_file, id_=None) -> TemplateElement:
        """
        把 SVG 文件注册为模板，用 pen.template(id) 复用
        （对应中文版 `导入SVG为模板`）。 / Register an SVG file as a symbol, then reuse it with pen.template(id).

        示例::
            pen.import_svg_as_template("logo.svg", id_="logo")
            pen.template("logo", x=100, y=100)
        """
        node, w, h = tools.import_svg_as_nodes(svg_file)
        sym = self.symbol(id_=id_ or self._gen_id("svg_tpl"),
                                   view_box=f"0 0 {fmt_num(w)} {fmt_num(h)}")
        sym.node.add(node)
        return sym

    # ------------------------------------------------------------------
    # 排列与重复
    # ------------------------------------------------------------------

    # ---- 兼容别名（1.0 早期命名，等价于新名） ----
    paste_image = image
    import_svg_as_template = import_svg_as_symbol
