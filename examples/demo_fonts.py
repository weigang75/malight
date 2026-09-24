# -*- coding: utf-8 -*-
"""
示例：内嵌字体 —— 使用 malight/assets/fonts 自带的字体文件
==========================================================

包内 ``malight/assets/fonts/`` 随源码带了几个字体文件，``find_font_file()``
会**优先**在这里找（其次才是系统字体目录）。把找到的字体文件路径传给
``font=`` 即可 —— 默认**只内嵌画面上实际用到的字**（自动子集化），
换电脑、发给别人都不会掉字体，SVG 也不会因为整份中文字体而爆掉。

三种嵌入方式（``pen.set_embed(fonts=...)``，也可写在构造参数里）::

    FontEmbed.SUBSET  默认：按用字自动子集化（5.6 MB 的 Android.ttf -> 几 KB）
    FontEmbed.EMBED   整份字体 base64 内嵌（最保险，体积最大）
    FontEmbed.LINK    只写本地字体路径（最小，换电脑/挪路径会掉字）

运行::

    python examples/demo_fonts.py
    # 生成 output/demo_fonts.svg 与 output/demo_fonts.png
"""

import os, os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))

from malight import Malight, Font, TextHAlign, TextVAlign, find_font_file

pen = Malight("demo_fonts", width=900, height=660)
pen.set_background_color("#fbfbfd")

pen.text(450, 42, "Bundled fonts in malight/assets/fonts",
         font=Font.VERDANA, font_size=26, bold=True, fill_color="#263238",
         h_align=TextHAlign.MIDDLE, v_align=TextVAlign.MIDDLE)
pen.text(450, 80, "font=<file path> auto-embeds only the glyphs actually drawn (subset)",
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

# 大小对比：同一支 5.6 MB 的 CJK 字体，三种嵌入方式的实际体积
# Size comparison for one 5.6 MB CJK font across the three embedding modes.
big = find_font_file("Android")
if big:
    sizes = []
    for mode in ("subset", "embed", "link"):
        probe = Malight("_demo_fonts_{}".format(mode), width=400, height=120,
                        fonts=mode)
        probe.text(20, 60, "神笔码靓 MaLight", font=big, font_size=30,
                   fill_color="#1d3557")
        probe.finish()
        sizes.append("{} {:.0f} KB".format(
            mode, os.path.getsize(probe.file_path) / 1024.0))
        # 只留子集化的那张图给用户看，其余探针文件删掉
        if mode != "subset":
            os.remove(probe.file_path)
    pen.text(450, 600, "one 5.6 MB font, three modes:  " + "   |   ".join(sizes),
             font=Font.VERDANA, font_size=13, fill_color="#78909c",
             h_align=TextHAlign.MIDDLE, v_align=TextVAlign.MIDDLE)

# 三种嵌入方式的常用写法 / How to pick an embedding mode
pen.text(450, 626,
         'pen.set_embed(fonts=FontEmbed.EMBED)  # whole font   '
         '|  fonts=FontEmbed.LINK  # path only',
         font=Font.VERDANA, font_size=12, fill_color="#b0bec5",
         h_align=TextHAlign.MIDDLE, v_align=TextVAlign.MIDDLE)

pen.finish()      # 保存 SVG（finish 会打印保存全路径） / Save the SVG
pen.export_png(scale=2)
print("demo_fonts 完成 / done: output/demo_fonts.svg / .png")
