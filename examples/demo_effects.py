# -*- coding: utf-8 -*-
"""
示例 3：渐变、滤镜、裁剪、遮罩
================================

运行::

    python examples/demo_effects.py
"""

import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))

from malight import MagicPen, Color, TextHAlign

pen = MagicPen("demo_effects", width=800, height=560)
pen.set_background_color("#101418")

# 1) 线性渐变（含中间色标）
grad1 = pen.linearGradient((0, 0), (1, 0), "#00c6ff", "#0072ff",
                                   stops=[(0.5, "white")])
pen.rect(40, 40, 340, 90, corner_radius=10, fill_color=grad1.paint())

# 2) 径向渐变（太阳感）
sun = pen.radialGradient((0.5, 0.45), 0.55, "#fff7ae", "#ff7b00")
pen.circle(620, 100, 75, fill_color=sun.paint())

# 3) 彩虹渐变 / 黄金渐变
rainbow = pen.rainbow_linear_gradient()
pen.rect(40, 160, 340, 40, corner_radius=6, fill_color=rainbow.paint())
gold = pen.gold_linear_gradient()
pen.text(210, 250, "GOLD", font_size=52, fill_color=gold.paint(),
               h_align=TextHAlign.MIDDLE)

# 4) 滤镜：模糊 / 投影 / 发光（英文版新增完整滤镜支持）
fid_blur = pen.fx.blur(3)
pen.circle(120, 370, 45, fill_color="#5b8def",
                extra={"filter": f"url(#{fid_blur})"})
fid_shadow = pen.filter.drop_shadow(dx=6, dy=6, std_deviation=4)
pen.rect(230, 325, 150, 90, corner_radius=8, fill_color="gold",
              extra={"filter": f"url(#{fid_shadow})"})
fid_glow = pen.filter.glow(6)
pen.text(480, 390, "NEON", font_size=54, fill_color="#00e5ff",
               extra={"filter": f"url(#{fid_glow})"})

# 5) 圆形裁剪照片位（无图片文件时画色块代替）
target = pen.rect(640, 330, 140, 140, fill_color=grad1.paint())
pen.clip_circle(710, 400, 62, targets=target)

# 6) 遮罩：线性透明遮罩
mask_grad = pen.linearGradient((0, 0), (0, 1), "white", "black")
shade = pen.rect(40, 470, 720, 60, fill_color=mask_grad.paint())
m = pen.mask(shade)
bar = pen.rect(40, 470, 720, 60, fill_color="#39d353",
                    extra={"mask": f"url(#{m.node.attribs['id']})"})

pen.finish()
pen.export_png(scale=2)
print("示例 3 完成：output/demo_effects.svg / .png")
