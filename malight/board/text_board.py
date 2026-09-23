# -*- coding: utf-8 -*-
"""
文字（SVG <text> / <textPath> / 文字转路径）。 / Text: SVG text, textPath and text-to-path conversion.

本文件只包含 TextMixin 一个类（Mixin），由 board/__init__.py 组合进 MagicPen。
"""

from ..svg_backend import SvgNode, fmt_num
from ..definitions import (Color, PaperSize, PaperSettings,
    StrokeCap, StrokeJoin, ArrowStyle, PointStyle, TextHAlign, TextVAlign,
    GridRepeatType, CoordUnits, PNGMode, PDFMode, DOCXMode, SystemFont,
    FontWeight, TextDecoration, LengthAdjust, value_of)
from ..elements import (CircleElement, EllipseElement, RectElement,
    LineElement, PolylineElement, PolygonElement, TextElement, TextPathElement,
    ImageElement, SVGImageElement, GroupElement, TemplateElement, UseElement,
    MarkerElement, ClipPathElement, MaskElement, LinkElement, PatternElement,
    _paint, _fmt_points)
from ..elements.path import PathElement
from .. import tools
from ..i18n import t


class TextMixin:
    """TextMixin —— 文字（SVG <text> / <textPath> / 文字转路径）（方法名与 SVG 元素名对应，旧名保留为别名）。 / TextMixin - text: SVG text, textPath and text-to-path conversion. """

    def text(self, x, y, text, font=SystemFont.DEFAULT, font_size=16,
                   fill_color=Color.BLACK, stroke_color=None, stroke_width=None,
                   bold=False, italic=False, underline=False,
                   weight=None, decoration=None, letter_spacing=None,
                   word_spacing=None, h_align=None, v_align=None,
                   char_rotate=None, text_length=None, length_adjust=None,
                   paint_order=None,
                   blend_mode=None, filter=None, opacity=None,
                   id_=None, **extra) -> TextElement:
        """
        写文字（对应中文版 `写字`）。 / Write text.

        :param word_spacing: 词间距（英文排版常用）
        :param paint_order: PaintOrder.STROKE 先描边后填充（空心字必备，
                            否则描边会盖住填充的边缘）；所有元素都支持
        :param blend_mode: BlendMode 混合模式
        :param filter: 滤镜，如 pen.fx.shadow(2, 2, 2)
        :param opacity: 整体不透明度 0-1（默认不写属性）；等价于链上再调 set_opacity()
        :param x, y: 基线起点（配合对齐方式）
        :param font: 字体，三种写法都行 —— 见下方「字体写法」
        :param font_size: 字号
        :param bold: 加粗（等价 weight=FontWeight.BOLD）
        :param weight: 字重，FontWeight 枚举或 "700"
        :param underline: 下划线（等价 decoration=TextDecoration.UNDERLINE）
        :param decoration: 文字修饰线，TextDecoration 枚举或字符串
        :param h_align: TextHAlign 水平对齐
        :param v_align: TextVAlign 垂直对齐
        :param char_rotate: 逐字旋转角度列表
        :param text_length: 文字总宽压缩（英文版新增）
        :param length_adjust: LengthAdjust 宽度调整方式（英文版新增）

        **字体写法（三种可混用）**::

            font=Font.SIMHEI                        # 1) 枚举，推荐（有补全）
            font="Microsoft YaHei"                  # 2) 字体名，任意已安装字体
            font=r"C:\\Windows\\Fonts\\simkai.ttf"  # 3) 字体文件，自动内嵌

        示例::
            from malight import Font, FontWeight, TextHAlign

            pen.text(400, 80, "会议纪要", font=Font.KAITI, font_size=42,
                     weight=FontWeight.BOLD, h_align=TextHAlign.MIDDLE)
            pen.text(400, 140, "下划线备注", decoration=TextDecoration.UNDERLINE)
            pen.text(400, 200, "内嵌字体不掉字", font=r"C:\\Windows\\Fonts\\simhei.ttf")
        """
        return self._new(TextElement, x=x, y=y, text=text, font=font,
                         font_size=font_size, fill_color=fill_color,
                         stroke_color=stroke_color, stroke_width=stroke_width,
                         bold=bold, italic=italic, underline=underline,
                         weight=weight, decoration=decoration,
                         letter_spacing=letter_spacing, h_align=h_align,
                         v_align=v_align, char_rotate=char_rotate,
                         text_length=text_length, length_adjust=length_adjust,
                         paint_order=paint_order,
                         opacity=opacity, id_=id_, extra=extra or None,
                         word_spacing=word_spacing, blend_mode=blend_mode, filter=filter)

    def textPath(self, points, text, start_offset="0%",
                     font=SystemFont.DEFAULT, font_size=16,
                     fill_color=Color.BLACK, letter_spacing=None,
                     weight=None, decoration=None, h_align=None,
                     blend_mode=None, filter=None,
                     id_=None, **extra) -> TextPathElement:
        """
        文字沿路径排列（对应中文版 `路径文字`）。 / Lay text out along a path.

        :param blend_mode: BlendMode 混合模式
        :param filter: 滤镜
        :param points: 引导路径顶点列表（也可传 PathElement 或 d 串）
        :param font: 字体（枚举 / 字体名 / 字体文件，同 text()）

        示例::
            pen.textPath([(80, 300), (200, 220), (320, 300), (440, 220)],
                         "文字沿曲线起伏流动", font_size=22, fill_color="purple")
        """
        return self._new(TextPathElement, path=points, text=text,
                         start_offset=start_offset, font=font,
                         font_size=font_size, fill_color=fill_color,
                         letter_spacing=letter_spacing, weight=weight,
                         decoration=decoration, h_align=h_align,
                         id_=id_, extra=extra or None,
                         blend_mode=blend_mode, filter=filter)

    def text_to_path(self, x, y, text, font=SystemFont.DEFAULT, font_size=16,
                     fill_color=Color.BLACK, letter_spacing=0, id_=None) -> GroupElement:
        """
        文字转矢量路径（对应中文版 `文字转路径`，需要 fontTools 库）。 / Convert text into vector paths.

        与 write_text 的区别：转出的文字是纯路径，任何环境渲染一致（不依赖系统字体）。

        示例::
            pen.text_to_path(50, 200, "HELLO", font=SystemFont.ARIAL,
                             font_size=64, fill_color="navy")
        """
        font_file = tools.find_font_file(font) if font else None
        if not font_file:
            raise FileNotFoundError(t("err.font_not_found", font=font))
        glyphs, transform, w, h = tools.text_to_path_d(text, font_file, font_size,
                                                       letter_spacing)
        g = self.g(id_=id_)
        g.node.set("transform", f"translate({x},{y}) {transform}")
        for d, off in glyphs:
            node = SvgNode("path", {"d": d, "fill": _paint(fill_color),
                                    "transform": f"translate({fmt_num(off, 4)},0)"})
            g.node.add(node)
        return g

    # ------------------------------------------------------------------
    # 调试辅助
    # ------------------------------------------------------------------

    # ---- 兼容别名（1.0 早期命名，等价于新名） ----
    write_text = text
    text_on_path = textPath
