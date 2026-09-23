# -*- coding: utf-8 -*-
"""
排列（水平/垂直/网格/环绕）。 / Arranging elements horizontally, vertically, in a grid or around a circle.

本文件只包含 LayoutMixin 一个类（Mixin），由 board/__init__.py 组合进 MagicPen。
"""

import math


class LayoutMixin:
    """LayoutMixin —— 排列（水平/垂直/网格/环绕）（方法名与 SVG 元素名对应，旧名保留为别名）。 / LayoutMixin - arranging elements horizontally, vertically, in a grid or around a circle. """

    def arrange_horizontal(self, elements, gap=10) -> list:
        """
        水平排列（对应中文版 `水平排列`）：按包围盒左右相接。 / Lay out horizontally, placing bounding boxes edge to edge.

        :param gap: 元素间距

        示例::
            shapes = [pen.circle(0, 0, 30, fill_color=c) for c in colors]
            pen.arrange_horizontal(shapes, gap=20)
        """
        cursor = 0
        for el in elements:
            b = el.bbox()
            if b:
                el.translate(cursor - b[0], 0)
                cursor += (b[2] - b[0]) + gap
        return elements

    def arrange_vertical(self, elements, gap=10) -> list:
        """
        垂直排列（对应中文版 `垂直排列`）。 / Lay out vertically.

        示例::
            pen.arrange_vertical(labels, gap=8)
        """
        cursor = 0
        for el in elements:
            b = el.bbox()
            if b:
                el.translate(0, cursor - b[1])
                cursor += (b[3] - b[1]) + gap
        return elements

    def arrange_grid_by_cols(self, elements, max_cols, col_gap=10, row_gap=10) -> list:
        """
        网格排列（按列数换行，对应中文版 `网格水平排列`）。 / Lay out in a grid.

        示例::
            pen.arrange_grid_by_cols(shapes, max_cols=4, col_gap=30, row_gap=30)
        """
        col, row = 0, 0
        row_h = 0
        for el in elements:
            b = el.bbox()
            if b:
                el.translate(col * col_gap, row * row_gap)
                row_h = max(row_h, b[3] - b[1])
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
                row_gap += 0  # 行高取实测的最大值会更精确，这里用均匀行距
        return elements

    def arrange_grid_by_rows(self, elements, max_rows, row_gap=10, col_gap=10) -> list:
        """网格排列（按行数换列，对应中文版 `网格垂直排列`）。 / Lay out in a grid. """
        col, row = 0, 0
        for el in elements:
            b = el.bbox()
            if b:
                el.translate(col * col_gap, row * row_gap)
            row += 1
            if row >= max_rows:
                row = 0
                col += 1
        return elements

    def arrange_circle(self, elements, center=None, angle_gap=None,
                       clockwise=True, rotate_with=True) -> list:
        """
        环绕排列（对应中文版 `环绕排列`）：元素沿圆周均匀分布。 / Lay out around a circle, spacing the elements evenly.

        :param center: 圆心（默认画布中心）
        :param angle_gap: 相邻元素夹角（默认自动均分）
        :param rotate_with: 元素是否跟随角度旋转

        示例::
            petals = [pen.ellipse(200, 60, radius=(24, 50),
                                       fill_color=c) for c in pinks]
            pen.arrange_circle(petals, center=(200, 150))
        """
        cx, cy = center or (self.width / 2, self.height / 2)
        n = len(elements)
        if n == 0:
            return elements
        step = angle_gap if angle_gap else 360.0 / n
        # 每个元素先平移到 (cx, cy - 半径感高度)，再绕中心旋转
        for i, el in enumerate(elements):
            b = el.bbox()
            if not b:
                continue
            ang = math.radians(step * i * (1 if clockwise else -1))
            # 元素中心到旋转中心的初始向量
            ex, ey = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
            radius = math.hypot(ex - cx, ey - cy) or (b[3] - b[1])
            base_ang = math.atan2(ey - cy, ex - cx) if (ex != cx or ey != cy) else -math.pi / 2
            target = base_ang + (step * i * (1 if clockwise else -1)) * math.pi / 180
            # 平移到初始位置（保持输入的相对半径）
            tx = cx + radius * math.cos(target) - ex
            ty = cy + radius * math.sin(target) - ey
            el.translate(tx, ty)
            if rotate_with:
                el.rotate(math.degrees(target - base_ang), cx=cx, cy=cy)
        return elements

