# -*- coding: utf-8 -*-
"""
图像（<image> 贴图与 SVG 导入）。 / Images: bitmap <image> placement and SVG import.

本文件只包含 ImageMixin 一个类（Mixin），由 board/__init__.py 组合进 MagicPen。
"""

from ..svg_backend import SvgNode, fmt_num
from ..elements import (CircleElement, EllipseElement, RectElement,
    LineElement, PolylineElement, PolygonElement, TextElement, TextPathElement,
    ImageElement, SVGImageElement, SvgGroupElement, GroupElement,
    TemplateElement, UseElement,
    MarkerElement, ClipPathElement, MaskElement, LinkElement, PatternElement,
    _paint, _fmt_points)
from .. import tools


class ImageMixin:
    """ImageMixin —— 图像（<image> 贴图与 SVG 导入）（方法名与 SVG 元素名对应，旧名保留为别名）。 / ImageMixin - images (bitmap <image> and SVG import). """

    def image(self, image_file, x=0, y=0, width=None, height=None,
                    opacity=1.0, rendering=None, aspect=None, external=False,
                    embed=None, blend_mode=None, filter=None, id_=None, **extra) -> ImageElement:
        """
        贴位图（对应中文版 `贴图`）。本地文件默认 base64 内嵌。 / Place a bitmap; local files are base64-embedded automatically.

        :param rendering: ImageRendering.CRISP_EDGES / PIXELATED（放大不糊）
        :param aspect: AspectRatio.MEET（完整显示，默认）/ SLICE（铺满裁切）
        :param external: True 只外链不内嵌（SVG 体积小，但需联网）
        :param embed: 单张覆盖画板的嵌入方式：ImageEmbed.EMBED / LINK
                      （LINK = 只引用图片路径，不撑大 SVG；见 pen.set_embed）
        :param blend_mode: BlendMode 混合模式
        :param filter: 滤镜
        :param image_file: 图片路径或 http(s) 地址（贴 **SVG 文件**请用
                           `svg_image`，那样元素能改自身的文本与颜色）

        示例::
            pen.image("photo.jpg", x=20, y=20, width=400)
            pen.image("bg.jpg", 0, 0, width=800,
                      embed=ImageEmbed.LINK)      # 这张只引用、不内嵌
        """
        return self._new(ImageElement, href=str(image_file), x=x, y=y,
                         width=width, height=height, opacity=opacity,
                         rendering=rendering, id_=id_, extra=extra or None,
                         aspect=aspect, external=external, embed=embed,
                         blend_mode=blend_mode, filter=filter)

    def svg_image(self, svg_file="", x=0, y=0, width=None, height=None,
                        opacity=None, blend_mode=None, filter=None,
                        svg_text=None, id_=None, **kw) -> SVGImageElement:
        """
        贴 SVG 文件并返回「可改源文本」的 SVG 图元素（对应中文版 `SVG贴图`）。 / Place an SVG file and return an SVG image element whose source text can be rewritten.

        拿到的元素上能直接改它自己那份 SVG 文本（换颜色、换文字），所以**同一个
        SVG 文件可以贴出好几种配色**，不必为每种颜色各存一个文件：换色方法见
        `SVGImageElement.replace_color` / `replace_text` / `svg_colors`。

        （0.2.0 起本方法叫 `svg_image`，旧名 `paste_svg` 仍可用。）

        :param svg_file: SVG 文件路径
        :param svg_text: 直接给 SVG 源文本（与 svg_file 二选一）
        :param opacity: 透明度 0~1
        :param blend_mode: BlendMode 混合模式
        :param filter: 滤镜
        :param width: 宽度；只给宽时高度按 SVG 自身比例自动算
        :param kw: 其它公共样式参数（class_name / style_str / fill_opacity 等）

        示例::
            icon = pen.svg_image("icon.svg", x=10, y=10, width=120)
            icon.replace_color("#ffffff", "#ff0000")   # white -> red

            # 同一个文件、三种配色：各改各的，互不影响
            for i, color in enumerate(("#ff0000", "#00a651", "#1e90ff")):
                pen.svg_image("icon.svg", x=40 + i * 140, y=200,
                              width=120).replace_color("white", color)
        """
        return self._new(SVGImageElement, svg_file=str(svg_file or ""), x=x, y=y,
                         width=width, height=height, id_=id_,
                         opacity=opacity, blend_mode=blend_mode, filter=filter,
                         svg_text=svg_text, **kw)

    def import_svg_as_group(self, svg_file, x=0, y=0, scale=None,
                            **kw) -> SvgGroupElement:
        """
        把 SVG 文件内容导入为可编辑的组元素（对应中文版 `导入SVG为组`）。 / Import an SVG file as an editable group element.

        返回的是 `SvgGroupElement`，与 `pen.g()` 造的普通组同一家族：能平移 /
        旋转 / 缩放 / 加滤镜 / 克隆 / 做动画（`bbox()` 也有）。它**不带换色
        方法** —— 换色目前只属于 `pen.svg_image()` 返回的 SVG 图元素（那个元素
        内嵌着自己那份 SVG 文本）；这里的内容是一棵节点树，颜色写在节点属性上，
        要换色就用 tools 里的函数就地改（``<style>`` 块里 class 写的颜色也一起
        换）::

            from malight.tools import replace_svg_node_color, svg_node_colors
            g = pen.import_svg_as_group("icon.svg", x=10, y=10)
            print(svg_node_colors(g.node))                  # ['#ffffff', ...]
            replace_svg_node_color(g.node, "#ffffff", "#ff0000")

        / The returned SvgGroupElement is the same family as pen.g(): it
        transforms, filters, clones and animates. It carries no recolour
        methods, because recolouring belongs to elements holding their own
        text - currently only the SVG image element from pen.svg_image(). Here
        the content is a node tree, so recolour it with the tools functions.

        与 svg_image 的区别：svg_image 把整份 SVG 当**一张图片**贴上去（内部
        base64 内嵌），换色改的是「它自己那份文本」，所以几份不同配色就贴几份；
        本方法把内容**拆成节点**交给你（`walk()` 可逐个查看、逐个改），适合
        导入后继续二次编辑。 / Difference: svg_image embeds the file as a
        single picture holding its own text, so each recolour needs its own
        copy; this one hands you the nodes for further editing.

        :param scale: 缩放倍数（缺省 1.0）
        :param kw: 其它公共样式参数（opacity / class_name / filter 等）

        示例::
            g = pen.import_svg_as_group("icon.svg", x=10, y=10, scale=0.5)
            g.translate(5, 0)                    # 组该有的能力照常
            print(g.bbox())                      # 内容占的位置
        """
        return self._new(SvgGroupElement, svg_file=str(svg_file), x=x, y=y,
                         scale=scale, **kw)

    def import_svg_as_symbol(self, svg_file, id_=None, **kw) -> TemplateElement:
        """
        把 SVG 文件注册为模板，用 pen.template(id) 复用
        （对应中文版 `导入SVG为模板`）。 / Register an SVG file as a symbol, then reuse it with pen.template(id).

        模板内容是一棵节点树，**不带换色方法** —— 换色目前只属于
        `pen.svg_image()` 返回的 SVG 图元素。要改模板内容的颜色，用 tools 里的
        函数就地改它的节点树；改的是 ``<symbol>`` 的内容，所以**所有 ``<use>``
        实例一起变**。想让每份副本各是一种配色，改用 `svg_image` 逐个换。
        / The template content is a node tree and carries no recolour methods;
        recolouring belongs to the SVG image element from pen.svg_image(). Use
        the tools functions on its node instead - editing the symbol updates
        every <use> instance.

        :param kw: 公共样式参数（opacity / class_name / style_str 等）

        示例::
            from malight.tools import replace_svg_node_color
            icon = pen.import_svg_as_template("logo.svg", id_="logo")
            replace_svg_node_color(icon.node, "white", "#ff0000")   # 所有实例一起变红 / every instance turns red
            pen.template("logo", x=100, y=100)
        """
        node, w, h = tools.import_svg_as_nodes(svg_file)
        sym = self.symbol(id_=id_ or self._gen_id("svg_tpl"),
                                   view_box=f"0 0 {fmt_num(w)} {fmt_num(h)}", **kw)
        sym.node.add(node)
        return sym

    # ------------------------------------------------------------------
    # 排列与重复
    # ------------------------------------------------------------------

    # ---- 兼容别名（早期命名，等价于新名） ----
    paste_image = image
    paste_svg = svg_image                  # 0.2.0 起正式名为 svg_image
    import_svg_as_template = import_svg_as_symbol
