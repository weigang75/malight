# -*- coding: utf-8 -*-
"""
示例 4：SMIL 动画 —— 透明/平移/旋转/缩放/轨迹/虚线流
======================================================

生成的 SVG 用浏览器打开即可看到动画效果。

运行::

    python examples/demo_animation.py
"""

import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))

from malight import MagicPen, Color

pen = MagicPen("demo_animation", width=800, height=500)
pen.set_background_color("#0e1116")

# 1) 旋转动画：地球绕太阳（加速旋转）
pen.circle(400, 250, 70, fill_color="#ffb300")           # 太阳
earth = pen.circle(620, 250, 22, fill_color="#3b82f6")   # 地球
orbit = pen.circle(400, 250, 220, stroke_color="#334", fill_color=Color.TRANSPARENT)
earth.animate_rotate(360, center=(400, 250), dur=6, accelerate=True)

# 2) 平移动画：左右移动的方块
box = pen.rect(60, 60, 60, 60, corner_radius=8, fill_color="#22c55e")
box.animate_translate(offset=(560, 0), dur=3, repeat_count="indefinite")

# 3) 透明度动画：呼吸灯
lamp = pen.circle(700, 80, 26, fill_color="#f43f5e")
lamp.animate_opacity(1.0, 0.15, dur=1.5, repeat_count="indefinite")

# 4) 轨迹移动动画：沿贝塞尔曲线飞的小鸟（三角形代替）
bird = pen.polygon([(700, 300), (720, 330), (680, 330)], fill_color="#eab308")
bird.animate_motion("M80,300 C240,120 480,420 720,220", dur=5, rotate=True)

# 5) 缩放 + 倾斜动画
pulse = pen.star(150, 420, 30, n=4, fill_color="#a78bfa")
pulse.animate_scale(factor=(1.6, 1.6), dur=1.2, repeat_count="indefinite")

# 6) 虚线流动画：蚂蚁线
line = pen.line((300, 440), (620, 440), stroke_color="#38bdf8", stroke_width=3)
line.animate_dash_flow(dur=1.5, dash="12 8")

# 7) 组动画：整组旋转的风车
pinwheel = pen.g()
for i in range(4):
    blade = pen.ellipse(0, 0, radius=(16, 55),
                             fill_color=["#f87171", "#fbbf24", "#34d399", "#60a5fa"][i])
    blade.rotate(i * 90)
    blade.translate(620, 380)
    blade.change_group(pinwheel)
pinwheel.animate_rotate(360, center=(620, 380), dur=4)

pen.finish()
print("示例 4 完成：output/demo_animation.svg （用浏览器打开查看动画）")
