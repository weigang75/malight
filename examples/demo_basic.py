# -*- coding: utf-8 -*-
"""
示例 1：基础绘图 —— 图形、颜色、文字、背景
=============================================

运行::

    python examples/demo_basic.py
    # 生成 output/demo_basic.svg 与 output/demo_basic.png
"""

import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))

from malight import MagicPen, Color, StrokeCap, TextHAlign, SystemFont

pen = MagicPen("demo_basic", width=800, height=500)

# 1) 背景色（英文版修复：真正生成背景矩形）
pen.set_background_color("#f8f9fa")

# 2) 网格与图框（调试辅助）
pen.grid(50)
pen.frame()

# 3) 基本图形
pen.circle(120, 130, 70, fill_color=Color.RGB(30, 144, 255),
                stroke_color=Color.NAVY, stroke_width=3)
pen.rect(240, 70, 160, 110, corner_radius=12,
              fill_color="gold", stroke_color="darkgoldenrod")
pen.ellipse(530, 125, radius=(95, 55), rotate=-12,
                 fill_color="lightseagreen")
pen.star(700, 125, 65, n=5, fill_color=Color.RED)
pen.heart(120, 330, 60, fill_color="crimson")
pen.diamond(280, 330, 70, fill_color="mediumpurple")
pen.regular_polygon(470, 330, 65, 6, fill_color="honeydew",
                         stroke_color="seagreen", stroke_width=2)
pen.polygon([(560, 400), (640, 260), (720, 400)],
                 fill_color="peachpuff", stroke_color="sandybrown")

# 4) 线条：实线 / 虚线 / 波浪 / 箭头
pen.line((40, 450), (400, 450), stroke_width=2)
pen.line((40, 465), (400, 465), stroke_width=2,
              stroke_style="10 6", stroke_cap=StrokeCap.ROUND, dash_offset=4)
pen.wave_line((420, 450), (760, 450), amplitude=10, periods=4)
pen.arrow_line((420, 470), (760, 470), stroke_width=2)

# 5) 文字（含对齐与字体）
pen.text(400, 45, "MagicPen 基础示例", font=SystemFont.MS_YAHEI,
               font_size=28, bold=True, fill_color=Color.NAVY,
               h_align=TextHAlign.MIDDLE)
pen.text(400, 490, "Created with MagicPen —— 全英文 API + 中文注释",
               font_size=14, fill_color="#888", h_align=TextHAlign.MIDDLE)

pen.finish()
pen.export_png(scale=2)
print("示例 1 完成：output/demo_basic.svg / .png")
