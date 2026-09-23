# -*- coding: utf-8 -*-
"""
导出演示（PDF / PNG / DOCX，Chrome 与 cairo 双引擎）
===================================================

要点：
- **Chrome 引擎**（推荐）：渲染与浏览器 100% 一致，SVG filter
  （投影/发光/模糊/浮雕…）正确输出；
- **cairo 引擎**：无需浏览器、速度快，但 **不渲染 SVG filter**；
- 默认 ``engine=PDFMode.AUTO``：有 Chrome 用 Chrome，没有自动回退 cairo。

运行::

    python demo_export.py

输出（examples/output/）::

    export_demo.svg / export_demo_chrome.pdf / export_demo_cairo.pdf
    export_demo_chrome.png / export_demo_cairo.png
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from malight import Malight, PDFMode, PNGMode          # noqa: E402
from malight.tools import find_chrome                  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------------------
# 画一张带滤镜的图（滤镜正是两个引擎差异最大的地方）
# ---------------------------------------------------------------------------
pen = Malight(os.path.join(OUT, "export_demo"), width=640, height=400)
pen.set_background_color("#f8f9fa")

pen.rect(40, 40, 560, 320, corner_radius=18, fill_color="white",
         filter=pen.fx.shadow(10, 12, 10, "#495057", 0.35))
pen.circle(190, 200, 80, fill_color="#e63946", filter=pen.fx.glow(10, "#ffd60a"))
pen.text(190, 210, "MAGIC", font_size=26, fill_color="white",
         h_align="middle", v_align="middle", bold=True)
pen.star(400, 200, 85, n=5, fill_color="#f4a261",
         filter=pen.fx.chain().bevel(1.2, 3).outline(3, "#264653"))
pen.text(60, 340, "Chrome 引擎会渲染上面的阴影 / 发光 / 浮雕，cairo 不会",
         font_size=15, fill_color="#6c757d")
pen.finish()

# ---------------------------------------------------------------------------
# PDF：三种引擎
# ---------------------------------------------------------------------------
pdf_auto = pen.export_pdf(os.path.join(OUT, "export_demo_auto.pdf"))
print("PDF(AUTO)  ->", os.path.basename(pdf_auto),
      os.path.getsize(pdf_auto), "bytes")

if find_chrome():
    p = pen.export_pdf(os.path.join(OUT, "export_demo_chrome.pdf"),
                       engine=PDFMode.CHROME)
    print("PDF(CHROME)->", os.path.basename(p), os.path.getsize(p), "bytes",
          "（含滤镜）")
else:
    print("未检测到 Chrome，跳过 CHROME 引擎演示")

try:
    p = pen.export_pdf(os.path.join(OUT, "export_demo_cairo.pdf"),
                       engine=PDFMode.CAIROSVG)
    print("PDF(CAIRO) ->", os.path.basename(p), os.path.getsize(p), "bytes",
          "（无滤镜）")
except Exception as e:                                  # noqa: BLE001
    print("cairo 引擎不可用（pip install cairosvg）:", e)

# ---------------------------------------------------------------------------
# PNG：cairo（默认）与 Chrome（带滤镜）
# ---------------------------------------------------------------------------
try:
    p = pen.export_png(scale=2, out_file=os.path.join(OUT, "export_demo_cairo.png"))
    print("PNG(CAIRO) ->", os.path.basename(p), os.path.getsize(p), "bytes")
except Exception as e:                                  # noqa: BLE001
    print("cairo PNG 不可用:", e)

if find_chrome():
    p = pen.export_png(2, os.path.join(OUT, "export_demo_chrome.png"),
                       mode=PNGMode.CHROME)
    print("PNG(CHROME)->", os.path.basename(p), os.path.getsize(p), "bytes")

print("导出演示完成，产物在 examples/output/")
