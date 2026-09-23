# -*- coding: utf-8 -*-
"""
board 包 —— MagicPen 绘图板（对应中文版 神笔绘图板）。 / The MagicPen drawing board, composed from BoardCore plus one mixin per feature file.

MagicPen 由 core + 各功能 Mixin 组合而成（每文件一个类），
方法名与 SVG 元素名对应：circle/rect/ellipse/text/path/g/a/clipPath/...
旧名（draw_circle 等）保留为兼容别名。
"""

from .core import BoardCore
from .effects import ClipMaskMixin
from .shapes import ShapeMixin
from .paths import PathMixin
from .text_board import TextMixin
from .debug import DebugMixin
from .containers import ContainerMixin
from .images import ImageMixin
from .layout import LayoutMixin
from .repeat import RepeatMixin
from .gradients_mixin import GradientMixin
from .filters import FilterAPI
from .fx import FilterChain
from .style import StyleAPI


class MagicPen(BoardCore, ShapeMixin, PathMixin, TextMixin, DebugMixin,
               ContainerMixin, ImageMixin, ClipMaskMixin, LayoutMixin,
               RepeatMixin, GradientMixin):
    """
    MagicPen 绘图板（对应中文版 `神笔绘图板`，包名 malight，「码靓」）。 / The MagicPen drawing board.

    用法：创建 → 绘图 → finish() 保存。

    方法名参考 SVG 元素名::

        from malight import Malight, Color
        pen = Malight("demo", width=800, height=600)
        pen.circle(400, 300, 200, fill_color=Color.GOLD)     # <circle>
        pen.rect(50, 50, 300, 200, fill_color="navy")        # <rect>
        pen.text(400, 60, "Hello", font_size=32)             # <text>
        pen.path(fill_color="none").move_to(0, 0).line_to(100, 100)  # <path>
        pen.g().append(pen.circle(10, 10, 5))                # <g>
        pen.circle(600, 400, 80, fill_color="#e63946",
                   filter=pen.fx.shadow(6, 8, 6))            # 滤镜
        pen.finish()   # 保存 demo.svg
    """


# 品牌名：包名 malight（小写是 Python 包名惯例，import 用），
# 商品名 / 类名用 MaLight —— README、文档与导出 remark 都写 MaLight。
# Malight 是兼容别名（早期文档示例用过），两者完全同一个类。
MaLight = MagicPen
Malight = MagicPen

__all__ = ["MagicPen", "MaLight", "Malight", "BoardCore", "FilterAPI",
           "FilterChain", "StyleAPI"]
