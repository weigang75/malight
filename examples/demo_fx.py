# -*- coding: utf-8 -*-
"""
滤镜全家福演示 —— malight.fx 参考 PS/AI 常用滤镜的效果一览。

运行: python demo_fx.py   输出到 ../output/fx_demo.svg
提示: 滤镜效果需在浏览器 / 支持 SVG filter 的查看器中查看
     （cairosvg 导出 PNG 时不渲染滤镜）。
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from malight import Malight, Color, Font

pen = Malight("fx_demo", width=1200, height=1450)
pen.set_background_color("#f8f9fa")
pen.text(600, 50, "malight 滤镜全家福（参考 PS / AI 常用滤镜）",
         font_size=30, fill_color="#343a40", h_align="middle")

fx = pen.fx
CARD = "#4e79a7"

def card(x, y, title, draw):
    """每个滤镜一张示例卡片。"""
    pen.rect(x, y, 260, 190, corner_radius=12, fill_color="#ffffff",
             stroke_color="#dee2e6", stroke_width=1)
    pen.text(x + 130, y + 26, title, font_size=18, fill_color="#495057",
             h_align="middle")
    draw(x + 130, y + 110)   # 中心点

# ---- 第一行：图层样式 ----
card(30, 90, "shadow 投影",
     lambda cx, cy: pen.circle(cx, cy, 55, fill_color=CARD,
                               filter=fx.shadow(6, 8, 6, "#1d3557", 0.45)))
card(310, 90, "inner_shadow 内阴影",
     lambda cx, cy: pen.rect(cx - 65, cy - 55, 130, 110, corner_radius=12,
                             fill_color="#f1faee",
                             filter=fx.inner_shadow(5, 5, 5, "#1d3557", 0.5)))
card(590, 90, "glow 外发光",
     lambda cx, cy: pen.circle(cx, cy, 50, fill_color="#003049",
                               filter=fx.glow(9, "#00b4d8", 0.95)))
card(870, 90, "inner_glow 内发光",
     lambda cx, cy: pen.circle(cx, cy, 55, fill_color="#003049",
                               filter=fx.inner_glow(9, "#ffd60a", 0.95)))

# ---- 第二行：立体与描边 ----
card(30, 300, "bevel 斜面浮雕",
     lambda cx, cy: pen.text(cx, cy + 22, "3D", font_size=64,
                             fill_color="#e76f51",
                             h_align="middle", filter=fx.bevel(1.2, 2)))
card(310, 300, "outline 外描边",
     lambda cx, cy: pen.text(cx, cy + 22, "HALO", font_size=44,
                             fill_color="#ffffff", h_align="middle",
                             filter=fx.outline(4, "#d62828")))
card(590, 300, "sharpen 锐化",
     lambda cx, cy: pen.star(cx, cy, 60, fill_color="#f4a261",
                             filter=fx.sharpen(0.9)))
card(870, 300, "motion_blur 动感模糊",
     lambda cx, cy: pen.circle(cx, cy, 40, fill_color="#2a9d8f",
                               filter=fx.motion_blur(14, 0)))

# ---- 第三行：风格化 ----
card(30, 510, "blur 高斯模糊",
     lambda cx, cy: pen.circle(cx, cy, 55, fill_color=CARD,
                               filter=fx.blur(5)))
card(310, 510, "roughen 粗糙化",
     lambda cx, cy: pen.heart(cx, cy, 70, fill_color="#e63946",
                              filter=fx.roughen(6, 0.04)))
card(590, 510, "noise 噪点颗粒",
     lambda cx, cy: pen.rect(cx - 70, cy - 60, 140, 120,
                             fill_color="#e9c46a", filter=fx.noise(0.25)))
card(870, 510, "emboss / edge_detect",
     lambda cx, cy: pen.polygon(
         [(cx, cy - 60), (cx + 55, cy + 45), (cx - 55, cy + 45)],
         fill_color="#adb5bd", filter=fx.emboss()))

# ---- 第四行：颜色调整 ----
card(30, 720, "hue_rotate 色相",
     lambda cx, cy: pen.circle(cx, cy, 55, fill_color="#e63946",
                               filter=fx.hue_rotate(140)))
card(310, 720, "saturate 饱和度",
     lambda cx, cy: pen.circle(cx, cy, 55, fill_color="#e63946",
                               filter=fx.saturate(0.4)))
card(590, 720, "grayscale / sepia",
     lambda cx, cy: pen.circle(cx, cy, 55, fill_color="#e76f51",
                               filter=fx.sepia()))
card(870, 720, "color_overlay 颜色叠加",
     lambda cx, cy: pen.rect(cx - 70, cy - 55, 140, 110,
                             fill_color="#118ab2",
                             filter=fx.color_overlay("#073b4c", 0.6)))

# ---- 第五行：效果叠加（后续的滤镜是叠上去的，不是覆盖前面的）----
pen.text(600, 950, "效果叠加 —— 后加的效果接在前一个的输出之后，两者都保留"
                   "（想只留最后一个用 merge=False）",
         font_size=20, fill_color="#343a40", h_align="middle")

card(30, 980, "叠加: 内阴影 + 浮雕 + 模糊",
     lambda cx, cy: pen.text(cx, cy + 18, "叠", font=Font.LISU, font_size=54,
                             fill_color="#c23b22", h_align="middle")
     .fx_inner_shadow(1, 1, 2, "#ffffff", 0.6).fx_emboss().fx_blur(1.5))
card(310, 980, "叠加: 投影 + 去色",
     lambda cx, cy: pen.circle(cx, cy, 52, fill_color="#4e79a7")
     .set_filter(fx.shadow(6, 8, 6, "#1d3557", 0.45))
     .set_filter(fx.saturate(0.25)))
card(590, 980, "叠加: 发光 + 描边 + 投影",
     lambda cx, cy: pen.star(cx, cy, 56, fill_color="#e76f51")
     .fx_chain().glow(6, "#ffd60a").outline(3, "#ffffff")
     .shadow(6, 6, 5, "#212529", 0.4))
card(870, 980, "对照: 只留最后一个（merge=False）",
     lambda cx, cy: pen.circle(cx, cy, 52, fill_color="#4e79a7")
     .set_filter(fx.shadow(6, 8, 6, "#1d3557", 0.45))
     .set_filter(fx.saturate(0.25), merge=False))

# ---- 第六行：雕刻 vs 凸起（同一光源，凹凸方向正好相反）----
pen.text(600, 1195, "雕刻 vs 凸起 —— 同样左上打光，engrave 是刻进去，bevel 是鼓出来",
         font_size=20, fill_color="#343a40", h_align="middle")

card(30, 1225, "engrave 雕刻凹陷",
     lambda cx, cy: pen.text(cx, cy + 22, "刻", font=Font.LISU, font_size=60,
                             fill_color="#C23B22", h_align="middle")
     .fx_engrave(2, 0.6, "#3E2410", "#FFFFFF"))
card(310, 1225, "bevel 斜面（凸起，对照）",
     lambda cx, cy: pen.text(cx, cy + 22, "刻", font=Font.LISU, font_size=60,
                             fill_color="#C23B22", h_align="middle")
     .fx_bevel(1.2, 2))
card(590, 1225, "叠加: 投影 + 雕刻",
     lambda cx, cy: pen.text(cx, cy + 22, "刻", font=Font.LISU, font_size=60,
                             fill_color="#2F2F2F", h_align="middle")
     .fx_shadow(2, 3, 3, "#212529", 0.4).fx_engrave(1.6, 0.6))
card(870, 1225, "内阴影 + 内高光（原型）",
     lambda cx, cy: pen.text(cx, cy + 22, "刻", font=Font.LISU, font_size=60,
                             fill_color="#2F2F2F", h_align="middle")
     .fx_inner_shadow(1.5, 1.5, 0.6, "#000000", 0.8)
     .fx_inner_shadow(-1.2, -1.2, 0.5, "#ffffff", 0.95))

pen.finish()
pen.export_png(scale=1)
print("已生成:", pen.file_path)
