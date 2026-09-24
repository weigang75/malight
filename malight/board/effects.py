# -*- coding: utf-8 -*-
"""
裁剪与遮罩（SVG <clipPath> / <mask>）。 / Clipping and masking with SVG clipPath and mask.

本文件只包含 ClipMaskMixin 一个类（Mixin），由 board/__init__.py 组合进 MagicPen。
"""

from ..definitions import (Color, PaperSize, PaperSettings,
    StrokeCap, StrokeJoin, ArrowStyle, PointStyle, TextHAlign, TextVAlign,
    GridRepeatType, CoordUnits, PNGMode, PDFMode, DOCXMode, SystemFont)
from ..elements import (CircleElement, EllipseElement, RectElement,
    LineElement, PolylineElement, PolygonElement, TextElement, TextPathElement,
    ImageElement, SVGImageElement, GroupElement, TemplateElement, UseElement,
    MarkerElement, ClipPathElement, MaskElement, LinkElement, PatternElement,
    _paint, _fmt_points)


class ClipMaskMixin:
    """ClipMaskMixin —— 裁剪与遮罩（SVG <clipPath> / <mask>）（方法名与 SVG 元素名对应，旧名保留为别名）。 / ClipMaskMixin - clipping and masking (SVG clipPath and mask). """

    def clipPath(self, clip_shape, targets=None, units=None, id_=None,
                 **kw) -> ClipPathElement:
        """
        用任意形状裁剪目标元素（对应中文版 `裁剪`）。 / Clip target elements with an arbitrary shape.

        :param clip_shape: 作为裁剪区域的元素（会从画布移入 defs）
        :param targets: 被裁元素（单个或列表）
        :param units: CoordUnits，默认用户空间
        :param kw: 公共样式参数（opacity / class_name / style_str 等）
        :return: ClipPathElement

        示例::
            shape = pen.ellipse(200, 150, radius=(150, 100))
            photo = pen.image("p.jpg", 0, 0, width=400, height=300)
            pen.clip(shape, photo)
        """
        return self._new(ClipPathElement, clip_shape=clip_shape,
                         targets=targets, units=units, id_=id_, **kw)

    def clip_circle(self, x, y, radius, targets=None, units=None, id_=None,
                    **kw) -> ClipPathElement:
        """
        圆形裁剪（对应中文版 `圆形裁剪`）。 / Clip with a circle.

        示例::
            pen.clip_circle(200, 150, 120, target_img)
        """
        shape = self.circle(x, y, radius)
        return self.clipPath(shape, targets, units, id_, **kw)

    def clip_rect(self, x, y, width, height, targets=None, units=None, id_=None,
                  **kw) -> ClipPathElement:
        """
        矩形裁剪（对应中文版 `矩形裁剪`）。 / Clip with a rectangle.

        示例::
            pen.clip_rect(0, 0, 300, 200, target_img)
        """
        shape = self.rect(x, y, width, height)
        return self.clipPath(shape, targets, units, id_, **kw)

    def mask(self, mask_shape, targets=None, units=None, content_units=None,
             id_=None, **kw) -> MaskElement:
        """
        遮罩（对应中文版 `遮罩`）：按遮罩亮度决定目标可见度。 / Mask: the mask's brightness decides how visible the target is.

        :param kw: 公共样式参数（opacity / class_name / style_str 等）
        :return: MaskElement

        示例::
            grad = pen.linearGradient((0, 0), (0, 1), "white", "black")
            shade = pen.rect(0, 0, 400, 300, fill_color=grad.paint())
            m = pen.mask(shade)
            m.apply_to(img)
        """
        return self._new(MaskElement, mask_shape=mask_shape, targets=targets,
                         units=units, content_units=content_units, id_=id_, **kw)

    # ------------------------------------------------------------------
    # 背景与画布
    # ------------------------------------------------------------------

    # ---- 兼容别名（1.0 早期命名，等价于新名） ----
    clip = clipPath
