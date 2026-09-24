# -*- coding: utf-8 -*-
"""
示例：资源嵌入方式 —— 字体与图片「内嵌」还是「引用」
====================================================

SVG 里的字体和图片都有两种来源：**把数据装进文件**（内嵌，随文件走）或
**只写一个路径**（引用，文件小但依赖外部文件）。malight 两种都支持，
默认选「又小又保险」的那档：

| 资源 | 默认 | 可选 |
|---|---|---|
| 字体（font=字体文件） | ``FontEmbed.SUBSET`` 只内嵌画面用到的字 | ``EMBED`` 整份内嵌 / ``LINK`` 只写路径 |
| 图片（image()） | ``ImageEmbed.EMBED`` base64 内嵌 | ``LINK`` 只写相对路径 |

设置方式（构造参数或 set_embed 都行）::

    pen = Malight("poster", fonts="link", images="link")   # 全用引用，文件最小
    pen.set_embed(fonts=FontEmbed.SUBSET, images=ImageEmbed.EMBED)

要点：字体**不需要**把文字写两遍 —— 库在 finish() 时自己扫描画面上用到的
字（含模板 / 克隆里的文字），子集化后内嵌。

运行::

    python examples/demo_embed.py
    # 生成 output/demo_embed*.svg 与 output/demo_embed.png
"""

import os, os as _os, struct, sys as _sys, zlib
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))

from malight import (Malight, FontEmbed, ImageEmbed, Font, TextHAlign,
                     TextVAlign, find_font_file)

OUT = os.path.join(os.path.dirname(_os.path.abspath(__file__)), "..", "output")
os.makedirs(OUT, exist_ok=True)

# 自带的一支 5.6 MB CJK 字体：最能说明「为什么默认要子集化」
# A bundled 5.6 MB CJK font - the best case for why subsetting is the default.
BIG = find_font_file("Android")


def kb(path):
    """文件大小（KB 文本）。 / File size as a KB string."""
    return "%.1f KB" % (os.path.getsize(path) / 1024.0)


print("=" * 66)
print("1) 字体：默认 SUBSET —— 文字只写一遍，库自己收集用字")
print("=" * 66)
if BIG:
    pen = Malight("demo_embed_subset", width=560, height=200)
    pen.set_background_color("#ffffff")
    pen.text(280, 70, "神笔码靓", font=BIG, font_size=40, fill_color="#1d3557",
             h_align=TextHAlign.MIDDLE, v_align=TextVAlign.MIDDLE)
    pen.text(280, 140, "码靓 MaLight", font=BIG, font_size=30, fill_color="#457b9d",
             h_align=TextHAlign.MIDDLE, v_align=TextVAlign.MIDDLE)   # 同字体的第二段
    pen.finish()
    used = len(set("神笔码靓" + "码靓 MaLight"))     # 两段文字合并后的实际用字
    print("   -> 源字体 %s，SVG %s（只内嵌用到的 %d 个字）"
          % (kb(BIG), kb(pen.file_path), used))

print()
print("=" * 66)
print("2) 字体：EMBED 整份内嵌 / LINK 只写路径")
print("=" * 66)
if BIG:
    full = Malight("demo_embed_full", width=560, height=120, fonts=FontEmbed.EMBED)
    full.text(280, 60, "神笔码靓", font=BIG, font_size=40, fill_color="#1d3557",
              h_align=TextHAlign.MIDDLE, v_align=TextVAlign.MIDDLE)
    full.finish()
    print("   EMBED -> SVG %s（整份字体在内）" % kb(full.file_path))

    # LINK：只写一句 file:/// 路径，体积最小，但字体挪位置就掉字
    # LINK writes one file:/// reference: smallest, but the font must stay put.
    linked = Malight("demo_embed_link", width=560, height=120)
    linked.set_embed(fonts=FontEmbed.LINK)
    linked.text(280, 60, "神笔码靓", font=BIG, font_size=40, fill_color="#1d3557",
                h_align=TextHAlign.MIDDLE, v_align=TextVAlign.MIDDLE)
    linked.finish()
    print("   LINK  -> SVG %s（只引用本地字体路径）" % kb(linked.file_path))

print()
print("=" * 66)
print("3) 图片：默认 EMBED 内嵌 / LINK 只引用相对路径")
print("=" * 66)
# 用标准库造一张小图，示例自带素材（不依赖 Pillow）
# Build a tiny PNG with the standard library so the demo needs no Pillow.
IMG = os.path.join(OUT, "demo_embed_sample.png")
_w, _h = 96, 64
_raw = b"".join(b"\x00" + bytes((230, 57, 70)) * _w for _ in range(_h))


def _chunk(tag, data):
    body = tag + data
    return (struct.pack(">I", len(data)) + body
            + struct.pack(">I", zlib.crc32(body) & 0xffffffff))


with open(IMG, "wb") as f:
    f.write(b"\x89PNG\r\n\x1a\n"
            + _chunk(b"IHDR", struct.pack(">IIBBBBB", _w, _h, 8, 2, 0, 0, 0))
            + _chunk(b"IDAT", zlib.compress(_raw)) + _chunk(b"IEND", b""))

emb = Malight("demo_embed_image_embed", width=560, height=160)
emb.set_background_color("#f8f9fa")
emb.text(280, 28, "ImageEmbed.EMBED (default) - bytes inside the SVG",
         font=Font.VERDANA, font_size=13, fill_color="#78909c",
         h_align=TextHAlign.MIDDLE, v_align=TextVAlign.MIDDLE)
emb.image(IMG, x=180, y=50, width=200, height=90)
emb.finish()
print("   EMBED -> SVG %s（图片 base64 在文件里，离线可看）" % kb(emb.file_path))

lnk = Malight("demo_embed_image_link", width=560, height=160,
              images=ImageEmbed.LINK)
lnk.set_background_color("#f8f9fa")
lnk.text(280, 28, "ImageEmbed.LINK - only a relative path",
         font=Font.VERDANA, font_size=13, fill_color="#78909c",
         h_align=TextHAlign.MIDDLE, v_align=TextVAlign.MIDDLE)
lnk.image(IMG, x=180, y=50, width=200, height=90)
lnk.finish()
print("   LINK  -> SVG %s（只写相对路径 %s）"
      % (kb(lnk.file_path), os.path.basename(IMG)))

# 导出 PNG 验证：LINK 引用的图片在 Chrome 导出时也能读到（相对 SVG 目录解析）
# Export a PNG to prove linked images still render: the temp HTML gets a
# <base href> pointing at the SVG folder.
lnk.export_png(scale=1)
print()
print("完成 / done: output/demo_embed*.svg / .png")
