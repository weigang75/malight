# -*- coding: utf-8 -*-
"""
示例 2：路径能力 —— 贝塞尔/圆弧/海龟绘图/fill-rule 挖洞
==========================================================

演示 PathElement 的四种绘制方式与英文版新增能力。

运行::

    python examples/demo_path.py
"""

import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))

from malight import MagicPen

pen = MagicPen("demo_path", width=800, height=560)

# 1) 命令式：三次贝塞尔 + 圆弧
p1 = pen.path(fill_color="lightyellow", stroke_color="orange", stroke_width=2)
p1.move_to(40, 220)
p1.cubic_to((120, 60), (240, 300), (330, 130))
p1.arc_to(70, (430, 150), sweep=1)
p1.line_to(430, 220)
p1.close()

# 2) fill-rule 挖洞（英文版新增：原版不支持 evenodd）
outer = [(60, 300), (300, 300), (300, 500), (60, 500)]
hole = [(120, 360), (240, 360), (240, 440), (120, 440)]
pen.polygon(outer + hole, fill_color="teal", fill_rule="evenodd",
                 stroke_color="darkslategray")

# 原版等价做法对照：begin_path 同样支持 fill_rule
p2 = pen.path(fill_color="salmon", fill_rule="evenodd",
                    stroke_color="firebrick")
p2.move_to(340, 300)
p2.line_to(580, 300)
p2.line_to(580, 500)
p2.line_to(340, 500)
p2.close()
p2.new_subpath(390, 360)
p2.line_to(530, 360)
p2.line_to(530, 440)
p2.line_to(390, 440)
p2.close()

# 3) 海龟式：五角星 + 圆角正方形
star = pen.path(fill_color="gold", stroke_color="darkorange")
star.move_to(650, 320)
for _ in range(5):
    star.forward(90)
    star.turn_right_line(144, 0.01)

round_square = pen.path(fill_color="aliceblue", stroke_color="steelblue",
                              stroke_width=2)
round_square.move_to(660, 440)
round_square.fillet((660, 520), (740, 520), 16)
round_square.fillet((740, 520), (740, 440), 16)
round_square.fillet((740, 440), (660, 440), 16)
round_square.fillet((660, 440), (660, 520), 16)
round_square.close()

# 4) d 字符串直接设置（英文版新增）
p3 = pen.path(fill_color="orchid", stroke_color="purple")
p3.set_d("M 380 60 C 420 20, 480 20, 520 60 C 480 100, 420 100, 380 60 Z")

# 5) 连点成光滑曲线
pen.connect_curve([(60, 60), (150, 120), (240, 50), (330, 110)],
                  stroke_color="orangered", stroke_width=3)

pen.finish()
pen.export_png(scale=2)
print("示例 2 完成：output/demo_path.svg / .png")
