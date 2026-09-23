# -*- coding: utf-8 -*-
"""
示例 6：图像嵌入、超链接、文字转路径、继承扩展、导出
======================================================

运行::

    python examples/demo_advanced.py
"""

import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))

from malight import MagicPen, Color, TextHAlign, PDFMode


# 1) 继承扩展：把作品内容写在 on_create 钩子里（对应中文版 创作 钩子）
class MyPoster(MagicPen):
    """子类化绘图板：绘图逻辑集中在 on_create，可复用版式。"""

    def on_create(self):
        # 渐变标题
        grad = self.gold_linear_gradient()
        self.text(400, 80, "MyPoster 模板", font_size=44, bold=True,
                        fill_color=grad.paint(), h_align=TextHAlign.MIDDLE)
        # 投影卡片
        fid = self.filter.drop_shadow(4, 6, 5)
        self.rect(80, 130, 640, 300, corner_radius=14,
                       fill_color="white", stroke_color="#e2e8f0",
                       extra={"filter": f"url(#{fid})"})
        # 可点击按钮（超链接）
        btn = self.rect(320, 360, 160, 50, corner_radius=25,
                             fill_color="#2563eb")
        self.text(400, 393, "点我访问", font_size=20,
                        fill_color="white", h_align=TextHAlign.MIDDLE)
        self.a(btn, "https://example.com", tooltip="示例链接")


pen = MyPoster("demo_advanced", width=800, height=460)
pen.finish()

# 2) 文字转路径（矢量文字，不依赖系统字体，需 fontTools）
try:
    pen2 = MagicPen("demo_textpath", width=600, height=200)
    pen2.set_background_color("white")
    pen2.text_to_path(60, 120, "MAGIC", font="Arial", font_size=90,
                      fill_color="navy")

    pen2.finish()
    pen2.export_png(scale=2)
    pen2.export_pdf(engine=PDFMode.CHROME)
except NotImplementedError as e:
    print("跳过文字转路径演示：", e)

# 3) 统一导出 PDF（cairosvg）
try:
    pen.export_pdf()
    print("PDF 导出成功")
except Exception as e:
    print("PDF 导出失败（cairosvg 未安装？）:", e)

print("示例 6 完成：output/demo_advanced.svg 等")
