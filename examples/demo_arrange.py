# -*- coding: utf-8 -*-
"""
示例 5：排列 / 重复 / 模板复用 / 渐变文字
============================================

运行::

    python examples/demo_arrange.py
"""

import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))

from malight import MagicPen, ColorScheme

pen = MagicPen("demo_arrange", width=800, height=560)
pen.set_background_color("#fafafa")

# 1) 模板 + 复用：定义一次，多处使用
t = pen.symbol(id_="icon_heart", view_box="0 0 40 40")
heart = pen.polygon(
    [(20, 34), (6, 20), (6, 12), (12, 6), (20, 12), (28, 6), (34, 12), (34, 20)],
    fill_color="red")
t.add_element(heart)
for i, c in enumerate(["red", "orange", "gold", "green", "blue", "purple"]):
    pen.template("icon_heart", x=60 + i * 70, y=60, width=40, height=40,
                 extra={"opacity": 0.85})

# 2) 网格重复（砖型交错）：蜂窝
tile = pen.hexagon(0, 0, 22, fill_color="#fde68a",
                        stroke_color="#d97706")
pen.repeat_grid(tile, cols=8, col_gap=58, rows=4, row_gap=50,
                grid_type=1)   # GridRepeatType.BRICK_OFFSET

# 3) 环绕排列：花瓣组成的花朵
petals = []
for c in ["#f9a8d4", "#f472b6", "#ec4899"]:
    for _ in range(4):
        petals.append(pen.ellipse(400, 250, radius=(16, 46), fill_color=c))
petals.append(pen.circle(400, 250, 24, fill_color="gold"))
pen.arrange_circle(petals[:-1], center=(400, 250))

# 4) 水平排列一排星星（按配色方案循环取色）
stars = []
for i in range(6):
    stars.append(pen.star(0, 0, 26,
                               fill_color=ColorScheme.cyclic(i, ColorScheme.RAINBOW)))
pen.arrange_horizontal(stars, gap=26)
pen.arrange_vertical(stars, gap=26)
# 统一移到指定位置
for s in stars:
    s.translate(180, 480)

# 5) 图案填充（pattern）
dots = pen.pattern(0, 0, 18, 18, id_="dotgrid")
dots.add_element(pen.circle(9, 9, 3, fill_color="#94a3b8"))
pen.rect(560, 420, 200, 110, corner_radius=10, fill_color="url(#dotgrid)",
              stroke_color="#64748b")

pen.finish()
pen.export_png(scale=2)
print("示例 5 完成：output/demo_arrange.svg / .png")
