# -*- coding: utf-8 -*-
"""
重复（网格重复/环绕重复/线性重复）。 / Repetition: grid, circular and linear.

本文件只包含 RepeatMixin 一个类（Mixin），由 board/__init__.py 组合进 MagicPen。
"""

from ..definitions import (Color, PaperSize, PaperSettings,
    StrokeCap, StrokeJoin, ArrowStyle, PointStyle, TextHAlign, TextVAlign,
    GridRepeatType, CoordUnits, PNGMode, PDFMode, DOCXMode, SystemFont)


class RepeatMixin:
    """RepeatMixin —— 重复（网格重复/环绕重复/线性重复）（方法名与 SVG 元素名对应，旧名保留为别名）。 / RepeatMixin - repetition: grid, circular and linear. """

    def repeat_around_circle(self, el, count, center=None, angle_gap=None,
                             clockwise=True, rotate_with=True) -> list:
        """
        环绕重复（对应中文版 `环绕重复`）：一个元素复制 count 份绕圆分布。 / Circular repeat: copy an element count times around a circle.

        示例::
            petal = pen.ellipse(200, 80, radius=(22, 45), fill_color="pink")
            pen.repeat_around_circle(petal, 8, center=(200, 160))
        """
        copies = [el]
        for i in range(1, count):
            copies.append(el.clone(id_=None))
        return self.arrange_circle(copies, center=center, angle_gap=angle_gap,
                                   clockwise=clockwise, rotate_with=rotate_with)

    def repeat_grid(self, el, cols, col_gap, rows, row_gap, grid_type=GridRepeatType.PLAIN) -> list:
        """
        网格重复（对应中文版 `网格重复`）。 / Grid repeat.

        :param grid_type: GridRepeatType.PLAIN / BRICK_OFFSET（砖型交错）/ BRICK_VERTICAL

        示例::
            tile = pen.draw_hexagon(0, 0, 20, fill_color="teal")
            pen.repeat_grid(tile, cols=6, col_gap=44, rows=4, row_gap=38,
                            grid_type=GridRepeatType.BRICK_OFFSET)
        """
        copies = []
        for r in range(rows):
            for c in range(cols):
                item = el if (r == 0 and c == 0) else el.clone()
                dx = c * col_gap
                dy = r * row_gap
                if grid_type == GridRepeatType.BRICK_OFFSET and r % 2 == 1:
                    dx += col_gap / 2
                elif grid_type == GridRepeatType.BRICK_VERTICAL and c % 2 == 1:
                    dy += row_gap / 2
                if dx or dy:
                    item.translate(dx, dy)
                copies.append(item)
        return copies

    def repeat_horizontal(self, el, count, gap, align="center", fill_gaps=False) -> list:
        """
        水平重复（对应中文版 `水平方向重复`）。 / Horizontal repeat.

        :param align: "left"/"center"/"right" —— 第一个元素相对画布的位置

        示例::
            star = pen.star(0, 0, 20, fill_color="gold")
            pen.repeat_horizontal(star, 7, gap=50, align="center")
        """
        b = el.bbox() or (0, 0, 0, 0)
        total_w = count * (b[2] - b[0]) + (count - 1) * gap
        start = {"left": 0, "center": (self.width - total_w) / 2,
                 "right": self.width - total_w}[align]
        el.translate(start - b[0], 0)
        copies = [el]
        for i in range(1, count):
            c = el.clone()
            c.translate(i * ((b[2] - b[0]) + gap), 0)
            copies.append(c)
        return copies

    def repeat_vertical(self, el, count, gap, align="center", fill_gaps=False) -> list:
        """垂直重复（对应中文版 `垂直方向重复`）。示例见 repeat_horizontal。 / Vertical repeat; see repeat_horizontal for an example. """
        b = el.bbox() or (0, 0, 0, 0)
        total_h = count * (b[3] - b[1]) + (count - 1) * gap
        start = {"top": 0, "center": (self.height - total_h) / 2,
                 "bottom": self.height - total_h}[align if align in ("top", "bottom") else "center"]
        el.translate(0, start - b[1])
        copies = [el]
        for i in range(1, count):
            c = el.clone()
            c.translate(0, i * ((b[3] - b[1]) + gap))
            copies.append(c)
        return copies

    # ------------------------------------------------------------------
    # 渐变
    # ------------------------------------------------------------------

