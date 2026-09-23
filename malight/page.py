# -*- coding: utf-8 -*-
"""
页面设置（page）—— 打印与 PDF 的纸张、页边距、缩放
====================================================

Page setup for printing and PDF export: paper, margins and scaling.

**只对 Chrome 引擎生效**：纸张（``@page``）与缩放（``zoom``）是浏览器排版
能力，cairosvg 引擎没有这个概念。所以 ``PageSetup`` 只作用于
``export_pdf_chrome``（以及绘图板 ``export_pdf(engine=PDFMode.CHROME)``）；
PNG 是屏幕截图，没有纸张概念，输出尺寸恒为「画布 x scale」。
如果传了页面设置却选了 cairosvg 引擎，导出会**当场报错**而不是静默忽略。

**Chrome engine only**: paper size (``@page``) and zoom are browser layout
features that cairosvg cannot honour. ``PageSetup`` therefore applies to
``export_pdf_chrome`` (and ``export_pdf(engine=PDFMode.CHROME)``) only. PNG
is a screen screenshot with no notion of paper: its size is always canvas x
scale. Passing page settings to the cairosvg engine raises instead of
silently doing nothing.

示例 / Example::

    from malight import PageSetup

    # 1) 一次性设置在画板上，之后每次导出都用
    pen.page = PageSetup("A4", margin=24)
    pen.export_pdf()

    # 2) 也可以只在某一次导出时给
    pen.export_pdf(page=PageSetup("A4 landscape"))
    page = PageSetup("A4", margin=24)          # 铺到 A4，四边留 24px
    pen.export_pdf(page=page)                  # 内容等比缩放并居中留边
"""

import os as _os
import sys as _sys

# ---------------------------------------------------------------------------
# 直接运行引导：在 PyCharm 里点绿色三角运行本文件（或命令行 python 本文件路径）时，
# 相对导入需要包上下文，这里自动补上项目根路径与包名。
# 正常 `import malight.xxx` 时这段不会执行，对包本身零影响。
# ---------------------------------------------------------------------------
if __name__ == "__main__" and not __package__:
    import os as _os
    import sys as _sys
    _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
    __package__ = "malight"

from .i18n import t
from .svg_backend import fmt_num


# 常用纸张规格（毫米）。打印用 mm 写 @page 比 px 精确：210mm 就是真正的 A4。
PAGE_SIZES_MM = {
    "A2": (420, 594), "A3": (297, 420), "A4": (210, 297), "A5": (148, 210),
    "A6": (105, 148), "B4": (250, 353), "B5": (176, 250),
    "LETTER": (215.9, 279.4), "LEGAL": (215.9, 355.6),
}

MM_TO_PX = 96.0 / 25.4          # CSS 标准换算：1mm = 96/25.4 px


def paper_css(spec) -> tuple:
    """
    把纸张规格解析成 ``(CSS 尺寸串, 宽px, 高px)``。 / Parse a paper spec into (CSS size string, width px, height px).

    接受 "A4" / "A4 landscape" / "A4 横向" / "A3 portrait"，
    也接受 ``(宽mm, 高mm)`` 元组。

    :raises ValueError: 纸张名不认识（err.page_size_unknown）

    示例 / Example::

        paper_css("A4")             # -> ('210mm 297mm', 793.7, 1122.5)
        paper_css("A4 landscape")   # -> ('297mm 210mm', 1122.5, 793.7)
        paper_css((100, 50))        # -> ('100mm 50mm', 377.9, 188.9)
    """
    if isinstance(spec, str):
        text = spec.strip()
        upper = text.upper()
        landscape = "LANDSCAPE" in upper or "横向" in text
        portrait = "PORTRAIT" in upper or "纵向" in text
        key = (upper.replace("LANDSCAPE", "").replace("PORTRAIT", "")
               .replace("横向", "").replace("纵向", "").strip())
        if key not in PAGE_SIZES_MM:
            raise ValueError(t("err.page_size_unknown", name=spec))
        mm_w, mm_h = PAGE_SIZES_MM[key]
        if landscape and mm_w < mm_h:
            mm_w, mm_h = mm_h, mm_w
        elif portrait and mm_w > mm_h:
            mm_w, mm_h = mm_h, mm_w
    else:
        mm_w, mm_h = spec
    return (f"{fmt_num(mm_w)}mm {fmt_num(mm_h)}mm",
            mm_w * MM_TO_PX, mm_h * MM_TO_PX)


class PageSetup:
    """
    页面设置：纸张 / 页边距 / 内容缩放（对应中文版 `页面设置`）。 / Page setup: paper, margin and content scale.

    **只对 Chrome 引擎（浏览器排版）生效**，见模块说明。

    :param size: 纸张；None = 跟随画布尺寸（默认，页面就是画布那么大）。
                 可用 "A4" / "A4 landscape" / "A3" / "LETTER"，
                 或直接给 ``(宽mm, 高mm)``
    :param margin: 页边距（px），仅在指定了纸张时生效
    :param scale: 内容缩放；None = 按纸张自动等比适配（只缩小、不放大）
    :param background: 页面背景色（None = 跟随画布）

    示例 / Example::

        pen.page = PageSetup("A4", margin=24)
        pen.export_pdf()                       # 铺到 A4 纸，四边 24px 边距
    """

    def __init__(self, size=None, margin=0, scale=None, background=None):
        self.size = size
        self.margin = margin
        self.scale = scale
        self.background = background

    def __repr__(self):
        return (f"PageSetup(size={self.size!r}, margin={self.margin!r}, "
                f"scale={self.scale!r})")

    def resolve(self, svg_w, svg_h) -> tuple:
        """
        算出 ``(纸张尺寸串, 纸张宽px, 纸张高px, 内容缩放)``。 / Resolve into (page size CSS, width px, height px, content scale).

        没指定纸张时页面大小就是画布大小、缩放 1。
        """
        if self.size is None:
            scale = 1.0 if self.scale is None else float(self.scale)
            return (f"{fmt_num(svg_w)}px {fmt_num(svg_h)}px",
                    svg_w, svg_h, scale)
        css, pw, ph = paper_css(self.size)
        if self.scale is None:
            avail_w = max(1.0, pw - 2 * self.margin)
            avail_h = max(1.0, ph - 2 * self.margin)
            scale = min(avail_w / svg_w, avail_h / svg_h, 1.0)
        else:
            scale = float(self.scale)
        return css, pw, ph, scale

    def print_css(self, svg_w, svg_h) -> str:
        """
        生成 ``@media print`` 里那段缩放与页边距样式（空串 = 不需要）。 / Build the @media print rule for scale and margin (empty when not needed).

        只写进 ``@media print`` —— PNG 截图走 screen 媒体，完全不受影响。
        """
        _, _, _, scale = self.resolve(svg_w, svg_h)
        if self.size is None and not self.margin and scale == 1.0:
            return ""
        return ("@media print { svg { zoom: %s; margin: %spx 0 0 %spx; } }"
                % (fmt_num(scale), fmt_num(self.margin), fmt_num(self.margin)))


if __name__ == "__main__":
    # 直接运行本文件：看各纸张解析尺寸（不依赖 Chrome） / Run directly: print resolved paper sizes (no Chrome needed)
    for _spec in ("A4", "A4 landscape", "A3", "LETTER", (100, 50)):
        _css, _w, _h = paper_css(_spec)
        print("%-16s -> %-14s %8.1f x %8.1f px" % (str(_spec), _css, _w, _h))
    _page = PageSetup("A4", margin=24)
    # 画布 800x600 铺到 A4 / fit an 800x600 canvas onto A4
    print("A4 fit 800x600:", _page.resolve(800, 600))
    print(_page.print_css(800, 600))
