# -*- coding: utf-8 -*-
"""
示例 2：路径能力 —— 贝塞尔/圆弧/海龟绘图/fill-rule 挖洞
==========================================================

演示 PathElement 的四种绘制方式、弧长取点 / 段长计算、
paste_line 粘贴线（梯形 / 区间）、slice 弧长切片、
z-order 层级调整与 hide / show / delete 显示隐藏与删除。

运行::

    python examples/demo_path.py
"""

import os as _os, sys as _sys
import math

_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))

from malight import MaLight, Color

pen = MaLight("demo_path", width=800, height=560)

# -----------------------------------------------------------------
# 1) 命令式：三次贝塞尔 + 圆弧
# -----------------------------------------------------------------
piano = (pen.path(fill_color="lightyellow", stroke_color="orange", stroke_width=2, id_="piano")
         .move_to(51.1111, 343.6111)
         .cubic_to((140.8333, 100.2778), (228.8889, 269.4444), (298.0556, 120.2778))
         .ellipse_arc_to(70, 70, (538.3333, 230.5556), sweep=1, large_arc=0, x_axis_rotation=0)
         .line_to(417.5, 513.0556)
         .close())

# -----------------------------------------------------------------
# 2) 弧长取点 + 每段长度：point_at 按真弧长定位（修复后与 length 严格自洽）
# -----------------------------------------------------------------
ratios = [0.0, 0.1, 0.2, 0.5, 0.8, 0.9, 1.0]
pts = [(r, piano.point_at(r)) for r in ratios]
p00, p01, p02, p05, p08, p09, p10 = [p for _, p in pts]
total_len = piano.length()
print("路径总长 total_len = %.3f" % total_len)

# 相邻取点之间的两种「长度」：
#   弦距 = 两点直线距离（math.dist），弯得越厉害比真实弧长缩得越多；
#   真实弧长 = 比例差 x total（弧长参数化下精确成立）。
# 弦距总和 <= 弧长总和是数学必然（弦是直线近似），不是 bug。
print("%-10s %10s %10s" % ("段", "弦距", "真实弧长"))
for (r1, q1), (r2, q2) in zip(pts, pts[1:]):
    print("p%02d~p%02d  %10.3f %10.3f"
          % (round(r1 * 10), round(r2 * 10), math.dist(q1, q2), (r2 - r1) * total_len))
print("弦距总和 = %.3f  (<= 弧长总和 %.3f)"
      % (sum(math.dist(a, b) for (_, a), (_, b) in zip(pts, pts[1:])), total_len))

pen.locate(p00, p01, p02, p05, p08, p09, p10,
           labels=["0", "0.1", "0.2", "0.5", "0.8", "0.9", "1"])

# -----------------------------------------------------------------
# 3) paste_line 粘贴线：梯形锥角 + 弧长区间 + z-order 层级调整
#    z-order 由加入画板的先后决定（后画的在上层）；to_group 只是原地
#    包 <g>，不改变层叠顺序。想让谁在上层，用层级四件套调整。
# -----------------------------------------------------------------
# 3a) 矩形花边（taper_angle 缺省 90）铺满全路径，置于底层（不挡 piano）
trim_full = piano.paste_line(20, step=18,
                             stroke_width=1, stroke_style="2,2",
                             fill_color="none", stroke_color="gray")
trim_full.send_to_back()  # 置底：移到父容器第一个（英文版新增）

# 3b) 梯形齿（taper_angle=55）只贴 0.30~0.70 一段，置于顶层
trim_teeth = piano.paste_line(20, step=18, taper_angle=55,
                              start=0.30, end=0.70,
                              stroke_width=1.5, stroke_color="steelblue",
                              fill_color="lightsteelblue")
trim_teeth.bring_to_front()  # 置顶：移到父容器最后一个

# 3c) 逐层微调演示（英文版新增）：bring_forward / send_backward
trim_teeth.send_backward()  # 下移一层（被 piano 盖住一截）
trim_teeth.bring_forward(2)  # 再上移两层回到顶层

# -----------------------------------------------------------------
# 4) fill-rule 挖洞（英文版新增：原版不支持 evenodd）
# -----------------------------------------------------------------
outer = [(60, 300), (300, 300), (300, 500), (60, 500)]
hole = [(120, 360), (240, 360), (240, 440), (120, 440)]
pen.polygon(outer + hole, fill_color="teal", fill_rule="evenodd",
            stroke_color="darkslategray", id_="evenodd_1")

# 原版等价做法对照：begin_path 同样支持 fill_rule
p2 = pen.path(fill_color="salmon", fill_rule="evenodd",
              stroke_color="firebrick", id_="evenodd_2")
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

# -----------------------------------------------------------------
# 5) 海龟式：五角星 + 圆角正方形
# -----------------------------------------------------------------
star = pen.path(fill_color="gold", stroke_color="darkorange", id_="star")
star.move_to(650, 320)
for _ in range(5):
    star.forward(90)
    star.turn_right_line(144, 0.01)

round_square = pen.path(fill_color="aliceblue", stroke_color="steelblue",
                        stroke_width=2, id_="round_square")
a = (660, 440)
b = (660, 520)
c = (740, 520)
d = (740, 440)
r = 16
s = (a[0], a[1] + r)
round_square.move_to(s)
round_square.fillet(b, c, r)
round_square.fillet(c, d, r)
round_square.fillet(d, a, r)
round_square.fillet(a, b, r)
pen.locate(a, b, c, d)
round_square.close()

# -----------------------------------------------------------------
# 6) d 字符串直接设置（英文版新增）
# -----------------------------------------------------------------
p3 = pen.path(fill_color="orchid", stroke_color="purple", id_="d_str")
p3.set_d("M 380 60 C 420 20, 480 20, 520 60 C 480 100, 420 100, 380 60 Z")

# -----------------------------------------------------------------
# 7) 连点成光滑曲线
# -----------------------------------------------------------------
pen.connect_curve([(60, 60), (150, 120), (240, 50), (330, 110)],
                  stroke_color="orangered", stroke_width=3, id_="connect_curve")

p4 = pen.path(fill_color=Color.ALICEBLUE, stroke_color="darkslategray", id_="p4")
c = pen.width / 2, pen.height / 2
pt2 = c[0] + 50, c[1] + 50
p4.move_to(*c).turn_left_arc(angle=90, radius=50).turn_right_line(-90, 50)
p4.move_to(*c).line_to(pt2).turn_right_line(-90, 50)
p4.forward(100)
p4.backward(200)
pen.locate(c, pt2)

# -----------------------------------------------------------------
# 8) slice 弧长切片：复制指定区间的一段路径（英文版新增）
#    边界落在段中间也会精确切分（直线插值 / 贝塞尔 de Casteljau /
#    圆弧按 F.6.5 拆同椭圆子弧），切出来与原路径逐点重合。
# -----------------------------------------------------------------
piano2 = piano.slice(0.3, 0.7, stroke_color="red", fill_color="blue", stroke_width=4)
piano2.set_stroke_style("2,2")
piano2.set_fill_opacity(0.5)
piano2.translate(0, 50)  # 复制出的就是普通路径，随便改 / a plain PathElement now
print("slice(0.3, 0.7) 长度 = %.3f（原路径 %.3f）"
      % (piano2.length(), total_len))

# -----------------------------------------------------------------
# 9) 显示 / 隐藏 / 删除（英文版新增，所有元素都有）
#    hide = display:none（可用 show 恢复）；delete = 从画布摘除、
#    不进导出的 SVG，但元素对象还在，几何计算照常可用——
#    适合「拿元素算一算、算完就扔」的辅助元素。
# -----------------------------------------------------------------
# 辅助线：用来算一算，算完立刻删掉（画面上不会出现）
guide = pen.line((60, 40), (740, 40), stroke_color="gray", stroke_style="4,4")
g0, g1 = (60, 40), (740, 40)  # 线段两端点 / the two endpoints of the guide
dist_piano = min(min(math.dist(p, g0), math.dist(p, g1))
                 for p in piano.to_point_list(60))
print("piano 到辅助线的最短距离 = %.3f" % dist_piano)
guide.delete()

# 隐藏 / 显示：元素还在画布上（能计算），只是不渲染
star.hide()
star.show()  # 又回来了；hide 前有 display 值也会原样恢复

pen.finish()
pen.export_png(scale=2)
pen.svg_editor(p4)

print("示例 2 完成：output/demo_path.svg / .png")
