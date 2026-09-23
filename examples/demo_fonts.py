# -*- coding: utf-8 -*-
"""
示例：内嵌字体 —— 使用 malight/assets/fonts 自带的字体文件
==========================================================

包内 ``malight/assets/fonts/`` 随源码带了几个字体文件，``find_font_file()``
会**优先**在这里找（其次才是系统字体目录）。把找到的字体文件路径传给
``font=``，会自动 base64 内嵌进 SVG —— 换电脑、发给别人都不会掉字体。

运行::

    python examples/demo_fonts.py
    # 生成 output/demo_fonts.svg 与 output/demo_fonts.png
"""

import os, os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))

from malight import Malight, Font, TextHAlign, TextVAlign, find_font_file

pen = Malight("demo_fonts", width=900, height=640)
pen.set_background_color("#fbfbfd")

pen.text(450, 42, "Bundled fonts in malight/assets/fonts",
         font=Font.VERDANA, font_size=26, bold=True, fill_color="#263238",
         h_align=TextHAlign.MIDDLE, v_align=TextVAlign.MIDDLE)
pen.text(450, 80, "font=<file path> auto-embeds a base64 @font-face into the SVG",
         font=Font.VERDANA, font_size=14, fill_color="#90a4ae",
         h_align=TextHAlign.MIDDLE, v_align=TextVAlign.MIDDLE)

# 每行一个自带字体：(字体文件名, 说明, 样例文本, 字号)
# One row per bundled font: (font file name, note, sample text, size)
ROWS = [
    ("Digital-7Mono.TTF", "Digital-7 / seven-segment digit style",
     "8.8.8.8  12:34  9527", 46),
    ("MusicStaff.ttf", "akvo / music notation glyphs",
     "ABCDEFG", 46),
    ("mahjong.ttf", "mahjong tiles mapped to A-Z",
     "ABCDEFGH", 46),
    ("Android.ttf", "Droid Sans Fallback / CJK fallback text",
     "MaLight ABC abc 123", 34),
]

y = 150
for filename, note, sample, size in ROWS:
    # find_font_file 先查包内 assets/fonts，再查系统字体目录；
    # 传文件名（不带后缀也可）即可命中自带字体。 / The in-package assets/fonts
    # folder is searched first, so the bare file name is enough.
    path = find_font_file(os.path.splitext(filename)[0])
    label = "{}  —  {}".format(filename, note) if path else \
        "{}  (not found, skipped / 未找到，跳过)".format(filename)
    pen.text(70, y, label, font=Font.VERDANA, font_size=14,
             fill_color="#78909c", v_align=TextVAlign.MIDDLE)
    pen.text(70, y + 48, sample, font=path if path else Font.VERDANA,
             font_size=size, fill_color="#1d3557", v_align=TextVAlign.MIDDLE)
    y += 118

# 大字体内嵌前建议先子集化，体积能降一到两个数量级：
#   from malight import subset_font
#   sub = subset_font(path, "只保留用到的字")
# Subset a big font first to keep the embedded SVG small.
pen.text(450, 620, "subset_font() shrinks big fonts before embedding",
         font=Font.VERDANA, font_size=13, fill_color="#b0bec5",
         h_align=TextHAlign.MIDDLE, v_align=TextVAlign.MIDDLE)

pen.finish()      # 保存 SVG（finish 会打印保存全路径） / Save the SVG
pen.export_png(scale=2)
print("demo_fonts 完成 / done: output/demo_fonts.svg / .png")
