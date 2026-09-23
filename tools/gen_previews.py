# -*- coding: utf-8 -*-
"""
生成模块文档里的效果预览图（tools/gen_previews.py）
====================================================

为「不看图看不出来」的效果生成预览图，统一输出到**包内资源目录**
``malight/assets/images/``（随包分发，pip 装完也有），供
`xxx.zh.md` / `xxx.en.md` 用相对链接直接引用（GitHub/Gitee 都能显示）。

图里的标签一律用英文 —— 中英两页共用同一张图，英文页里不能出现中文。

改了效果实现（滤镜、文字样式等）就重跑一次，让图和实现一起更新。

运行 / Run::

    python tools/gen_previews.py            # 生成全部预览图
    python tools/gen_previews.py --check    # 只检查图在不在（不重新生成）
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

#: 预览图统一放这里（包内 malight/assets/images/）；md 用相对链接引用
IMAGES_DIR = os.path.join(ROOT, "malight", "assets", "images")

# 模块（相对仓库根）-> (图片文件名, 中文题注, 英文题注)
# 图片都在 assets/ 下，md 里的相对链接由 gen_docs.py 按所在目录算出来
PREVIEWS = {
    "malight/board/fx.py": ("fx_preview.png", "滤镜效果一览",
                            "All filters at a glance"),
    "malight/board/filters.py": ("filters_preview.png", "滤镜的 8 种用法",
                                 "Filters: 8 ways to use them"),
    "malight/elements/text.py": ("text_preview.png", "文字样式一览",
                                 "Text styles at a glance"),
    "malight/fonts.py": ("fonts_preview.png", "字体效果一览",
                         "Fonts at a glance"),
}


# 每张卡片：效果名 -> 应用方式（lambda 收元素、返回元素）
FX_ITEMS = [
    ("shadow", lambda el: el.fx_shadow(4, 4, 5)),
    ("inner_shadow", lambda el: el.fx_inner_shadow(4, 4, 4)),
    ("glow", lambda el: el.fx_glow(5)),
    ("inner_glow", lambda el: el.fx_inner_glow(7)),
    ("bevel", lambda el: el.fx_bevel(1.2, 3)),
    ("engrave", lambda el: el.fx_engrave(2.4, 1.2, "#5A3A16", "#FFF6E0")),
    ("emboss", lambda el: el.fx_emboss()),
    ("outline", lambda el: el.fx_outline(4, "#1D3557")),
    ("blur", lambda el: el.fx_blur(4)),
    ("motion_blur", lambda el: el.fx_motion_blur(12, 20)),
    ("sharpen", lambda el: el.fx_sharpen(0.9)),
    ("noise", lambda el: el.fx_noise(0.4)),
    ("roughen", lambda el: el.fx_roughen(6, 0.06)),
    ("edge_detect", lambda el: el.fx_edge_detect()),
    ("color_overlay", lambda el: el.fx_color_overlay("#E4572E", 0.75)),
    ("saturate", lambda el: el.fx_saturate(1.8)),
    ("hue_rotate", lambda el: el.fx_hue_rotate(120)),
    ("grayscale", lambda el: el.fx_grayscale()),
    ("sepia", lambda el: el.fx_sepia()),
    ("brightness", lambda el: el.fx_brightness(1.5)),
    ("contrast", lambda el: el.fx_contrast(1.8)),
    ("gamma", lambda el: el.fx_gamma(1.8, 0.7, 0.6)),
    ("invert", lambda el: el.fx_invert()),
    ("posterize", lambda el: el.fx_posterize(3)),
]


def _finish(pen, out_png):
    """导出预览图：Chrome 引擎（滤镜才渲染得出来），2 倍高清；中间 SVG 不留。"""
    from malight import PNGMode
    pen.finish()
    pen.export_png(out_file=out_png, scale=2, mode=PNGMode.CHROME)
    if os.path.isfile(pen.file_path):
        os.remove(pen.file_path)          # 预览图只要 png，svg 是中间产物
    return out_png


def build_fx_preview(out_png):
    """滤镜效果一览：24 个效果，每个一张卡片（圆片 + 英文标签）。"""
    from malight import Font, Malight, TextHAlign, TextVAlign

    cols, cw, ch = 4, 210, 170
    rows = (len(FX_ITEMS) + cols - 1) // cols
    pad, top = 20, 58
    w = cols * cw + pad * 2
    h = top + rows * ch + pad

    pen = Malight(out_png[:-4], width=w, height=h)
    pen.set_background_color("#FFFFFF")
    pen.text(w / 2, 30, "MaLight filter effects", font=Font.VERDANA,
             font_size=24, bold=True, fill_color="#263238",
             h_align=TextHAlign.MIDDLE, v_align=TextVAlign.MIDDLE)

    for i, (label, apply) in enumerate(FX_ITEMS):
        cx = pad + (i % cols) * cw + cw / 2
        cy = top + (i // cols) * ch + 60
        pen.rect(cx - cw / 2 + 8, cy - 58, cw - 16, ch - 26,
                 fill_color="#FAFAFA", stroke_color="#E4E4E4")
        el = pen.circle(cx, cy, 40, fill_color="#E8A33D",
                        stroke_color="#B4762A", stroke_width=1.5)
        apply(el)
        pen.text(cx, cy + 82, label, font=Font.VERDANA, font_size=15,
                 fill_color="#37474F", h_align=TextHAlign.MIDDLE,
                 v_align=TextVAlign.MIDDLE)
    return _finish(pen, out_png)


#: 滤镜的 8 种用法（与 fx.py / filters.py / README 的「用法」说明一一对应）。
#: 每条 = (标题, [代码行], 画法)；画法收 (pen, cx, cy)，在卡片右侧画示意元素。
#: 代码行就是真实可跑的写法，不自造语法 —— 改 API 时这里跟着改，图才会和文档一致。
FILTER_USAGE_ITEMS = [
    ("1  element method chain",
     ['el.fx_inner_shadow(1, 1, 2, "#ffffff", 0.6)',
      '  .fx_emboss().fx_blur(1.5)'],
     lambda p, x, y: p.text(
         x, y, "M", font="Georgia", font_size=54, bold=True,
         fill_color="#9E3B2E", h_align="middle", v_align="middle"
     ).fx_inner_shadow(1, 1, 2, "#ffffff", 0.6).fx_emboss().fx_blur(1.5)),

    ('2  el.fx("name", ...)',
     ['el.fx("blur", 3)',
      'el.fx("saturate", 1.6)'],
     lambda p, x, y: p.circle(
         x, y, 34, fill_color="#E8A33D", stroke_color="#B4762A",
         stroke_width=1.5).fx("blur", 3).fx("saturate", 1.6)),

    ('3  raw SVG primitive',
     ['el.fx("custom", "feBlend",',
      '       mode="screen", in2="SourceGraphic")'],
     lambda p, x, y: p.circle(
         x, y, 34, fill_color="#4E79A7", stroke_color="#35597C",
         stroke_width=1.5).fx("custom", "feBlend", mode="screen",
                              in2="SourceGraphic")),

    ("4  el.fx_chain()",
     ['el.fx_chain().blur(2).saturate(1.4)'],
     lambda p, x, y: p.circle(
         x, y, 34, fill_color="#E8A33D", stroke_color="#B4762A",
         stroke_width=1.5).fx_chain().blur(2).saturate(1.4)),

    ("5  factory, inline",
     ['pen.rect(x, y, w, h,',
      '         filter=pen.fx.glow(6))'],
     lambda p, x, y: p.rect(
         x - 42, y - 30, 84, 60, fill_color="#E15759",
         filter=p.fx.glow(6))),

    ("6  factory chain, shared",
     ['f = pen.fx.chain().blur(1).shadow(5, 5, 4)',
      'a.set_filter(f);  f.apply(b)'],
     lambda p, x, y: _fx_shared(p, x, y)),

    ("7  stack / replace / clear",
     ['el.set_filter(pen.fx.shadow(6, 8, 6))',
      'el.set_filter(pen.fx.saturate(0.4))     # stacks',
      'el.set_filter(fx2.glow(8), merge=False) # replaces',
      'el.set_filter(None)                     # clears'],
     lambda p, x, y: _fx_three_states(p, x, y)),

    ("8  low-level helpers",
     ['fid = create_glow_filter(pen, 6)',
      'pen.text(60, 150, "NEON", font_size=40,',
      '         extra={"filter": "url(#%s)" % fid})'],
     lambda p, x, y: _fx_low_level(p, x, y)),
]


def _fx_shared(p, x, y):
    """用法 6：一条链绑给两个元素（a 用 set_filter，b 用 apply）。"""
    a = p.circle(x - 30, y, 24, fill_color="#4E79A7", stroke_color="#35597C",
                 stroke_width=1.5)
    b = p.rect(x + 8, y - 23, 46, 46, fill_color="#E15759",
               stroke_color="#B03A50", stroke_width=1.5)
    f = p.fx.chain().blur(1).shadow(5, 5, 4)
    a.set_filter(f)
    f.apply(b)


def _fx_three_states(p, x, y):
    """用法 7：叠加（左）/ 整条替换（中）/ 清除（右）。"""
    a = p.circle(x - 52, y, 20, fill_color="#E63946", stroke_color="#A52836")
    a.set_filter(p.fx.shadow(6, 8, 6))
    a.set_filter(p.fx.saturate(0.4))            # 叠加：投影 + 去色
    b = p.circle(x, y, 20, fill_color="#E63946", stroke_color="#A52836")
    b.set_filter(p.fx.glow(8))
    b.set_filter(p.fx.invert(), merge=False)    # 替换：只剩反相
    c = p.circle(x + 52, y, 20, fill_color="#E63946", stroke_color="#A52836")
    c.set_filter(p.fx.glow(8))
    c.set_filter(None)                          # 清除：恢复原样


def _fx_low_level(p, x, y):
    """用法 8：tools.create_*_filter 拿到 id，再用 extra 挂到元素上。"""
    from malight.tools import create_glow_filter
    fid = create_glow_filter(p, 6)
    p.text(x, y, "NEON", font="Verdana", font_size=28, bold=True,
           fill_color="#00BCD4", h_align="middle", v_align="middle",
           extra={"filter": "url(#%s)" % fid})


def build_filters_preview(out_png):
    """滤镜用法一览：8 种写法各一张卡片（左边真实代码，右边渲染结果）。"""
    from malight import Font, Malight, TextHAlign, TextVAlign

    cols, cw, ch = 2, 560, 214
    rows = (len(FILTER_USAGE_ITEMS) + cols - 1) // cols
    pad, top = 20, 66
    w = cols * cw + pad * 2
    h = top + rows * ch + pad

    pen = Malight(out_png[:-4], width=w, height=h)
    pen.set_background_color("#FFFFFF")
    pen.text(w / 2, 26, "MaLight filters - 8 ways to use them",
             font=Font.VERDANA, font_size=24, bold=True, fill_color="#263238",
             h_align=TextHAlign.MIDDLE, v_align=TextVAlign.MIDDLE)
    pen.text(w / 2, 48, "element methods / factory chains / low-level helpers "
                        "- all verified against the code",
             font=Font.VERDANA, font_size=13, fill_color="#78909C",
             h_align=TextHAlign.MIDDLE, v_align=TextVAlign.MIDDLE)

    for i, (title, code, draw) in enumerate(FILTER_USAGE_ITEMS):
        card_x = pad + (i % cols) * cw + 8
        card_y = top + (i // cols) * ch + 8
        pen.rect(card_x, card_y, cw - 16, ch - 16,
                 fill_color="#FAFAFA", stroke_color="#E4E4E4")
        pen.text(card_x + 16, card_y + 20, title, font=Font.VERDANA,
                 font_size=13, bold=True, fill_color="#B4762A",
                 v_align=TextVAlign.MIDDLE)
        for k, line in enumerate(code):
            pen.text(card_x + 16, card_y + 52 + k * 21, line,
                     font=Font.CONSOLAS, font_size=13, fill_color="#37474F",
                     v_align=TextVAlign.MIDDLE)
        draw(pen, card_x + cw - 82, card_y + 99)
    return _finish(pen, out_png)


def build_text_preview(out_png):
    """文字样式一览：字体 / 字重 / 对齐 / 描边 / 压缩 / 旋转 / 雕刻。"""
    from malight import (Font, FontWeight, LengthAdjust, Malight, PaintOrder,
                         TextDecoration, TextHAlign, TextVAlign)

    w, h = 860, 604
    pen = Malight(out_png[:-4], width=w, height=h)
    pen.set_background_color("#FFFFFF")
    ink = "#263238"
    pen.text(w / 2, 30, "MaLight text styles", font=Font.VERDANA, font_size=24,
             bold=True, fill_color=ink, h_align=TextHAlign.MIDDLE,
             v_align=TextVAlign.MIDDLE)

    def section(y, title):
        pen.line((40, y - 18), (w - 40, y - 18), stroke_color="#DDDDDD")
        pen.text(40, y, title, font=Font.VERDANA, font_size=15,
                 fill_color="#78909C", v_align=TextVAlign.MIDDLE)

    # 1) 字体
    section(84, "font / font_size")
    pen.text(40, 116, "隶书 LISU", font=Font.LISU, font_size=30, fill_color=ink)
    pen.text(230, 116, "华文楷体", font=Font.STKAITI, font_size=30,
             fill_color=ink)
    pen.text(430, 116, "黑体 HEI", font=Font.SIMHEI, font_size=30,
             fill_color=ink)
    pen.text(590, 116, "雅黑 YaHei", font=Font.MS_YAHEI, font_size=30,
             fill_color=ink)
    pen.text(750, 116, "44pt", font=Font.VERDANA, font_size=44,
             fill_color="#B4762A")

    # 2) 字重与修饰线
    section(186, "weight / decoration / spacing")
    pen.text(40, 220, "normal", font_size=22, fill_color=ink)
    pen.text(160, 220, "bold", font_size=22, bold=True, fill_color=ink)
    pen.text(250, 220, "weight 700", font_size=22, weight=FontWeight.BOLD,
             fill_color=ink)
    pen.text(420, 220, "underline", font_size=22, fill_color=ink,
             decoration=TextDecoration.UNDERLINE)
    pen.text(570, 220, "line-through", font_size=22, fill_color=ink,
             decoration=TextDecoration.LINE_THROUGH)
    pen.text(40, 258, "letter-spacing 8", font_size=22, fill_color=ink,
             letter_spacing=8)
    pen.text(400, 258, "italic", font_size=22, italic=True, fill_color=ink)

    # 3) 对齐（带辅助线）
    section(320, "h_align / v_align")
    pen.line((430, 300), (430, 340), stroke_color="#FF8A65", stroke_width=1)
    pen.text(430, 330, "middle", font_size=20, fill_color=ink,
             h_align=TextHAlign.MIDDLE, v_align=TextVAlign.MIDDLE)
    pen.line((560, 300), (560, 340), stroke_color="#FF8A65", stroke_width=1)
    pen.text(560, 330, "start", font_size=20, fill_color=ink, v_align=TextVAlign.MIDDLE)
    pen.line((830, 300), (830, 340), stroke_color="#FF8A65", stroke_width=1)
    pen.text(830, 330, "end", font_size=20, fill_color=ink,
             h_align=TextHAlign.END, v_align=TextVAlign.MIDDLE)

    # 4) 描边与先描边
    section(400, "stroke / paint_order")
    pen.text(40, 430, "stroke eats face", font_size=30, fill_color="#FFFFFF",
             stroke_color="#C23B22", stroke_width=5)
    pen.text(360, 430, "paint_order=STROKE", font_size=30, fill_color="#FFFFFF",
             stroke_color="#C23B22", stroke_width=5,
             paint_order=PaintOrder.STROKE)

    # 5) 宽度压缩
    section(492, "text_length / length_adjust")
    pen.text(40, 522, "AAAAAAAAAA", font_size=22, fill_color=ink,
             text_length=460, length_adjust=LengthAdjust.SPACING_AND_GLYPHS)
    pen.text(560, 522, "squeezed to 460px", font_size=18,
             fill_color="#78909C")

    # 6) 文字滤镜
    section(560, "fx_engrave / fx_shadow")
    pen.text(60, 584, "ENGRAVED", font=Font.VERDANA, font_size=34,
             bold=True, fill_color="#7B4B16",
             v_align=TextVAlign.MIDDLE).fx_engrave(2.2, 1.0, "#3E2410",
                                                   "#FFF6E0")
    pen.text(430, 584, "SHADOWED", font=Font.VERDANA, font_size=34,
             bold=True, fill_color="#263238",
             v_align=TextVAlign.MIDDLE).fx_shadow(3, 4, 4, "#90A4AE", 0.8)
    return _finish(pen, out_png)


#: 字体预览用到的样板（中文字体 + 西文字体）；装没装由系统决定，
#: 没装的会被浏览器静默回退 —— 本地装了才会看到差别
CN_FONT_SAMPLES = [
    ("SimHei", "黑体 SimHei"), ("SimSun", "宋体 SimSun"),
    ("KaiTi", "楷体 KaiTi"), ("FangSong", "仿宋 FangSong"),
    ("YouYuan", "幼圆 YouYuan"), ("LiSu", "隶书 LiSu"),
    ("DengXian", "等线 DengXian"), ("Microsoft YaHei", "雅黑 YaHei"),
]
LATIN_FONT_SAMPLES = [
    ("Arial", "Arial"), ("Verdana", "Verdana"), ("Georgia", "Georgia"),
    ("Times New Roman", "Times New Roman"), ("Courier New", "Courier New"),
    ("Consolas", "Consolas"), ("Impact", "Impact"),
    ("Comic Sans MS", "Comic Sans MS"),
]


#: assets/fonts 自带字体（标签与样例一律英文 —— 中英两页共用同一张图）
BUNDLED_FONT_SAMPLES = [
    ("Digital-7Mono.TTF", "8.8.8.8  12:34"),
    ("MusicStaff.ttf", "ABCDEFG"),
    ("mahjong.ttf", "ABCDEFGH"),
    ("Android.ttf", "MaLight ABC 123"),
]


def build_fonts_preview(out_png):
    """字体效果一览：中文字体与西文字体各一栏，外加 assets/fonts 自带字体一栏。"""
    from malight import Font, Malight, TextVAlign
    from malight.fonts import find_font_file

    ink, grey = "#263238", "#78909C"
    w, h = 900, 700
    pen = Malight(out_png[:-4], width=w, height=h)
    pen.set_background_color("#FFFFFF")
    pen.text(w / 2, 30, "MaLight fonts", font=Font.VERDANA, font_size=24,
             bold=True, fill_color=ink, h_align="middle", v_align=TextVAlign.MIDDLE)

    def column(x, title, samples, sample_text):
        pen.line((x, 62), (x + 400, 62), stroke_color="#DDDDDD")
        pen.text(x, 82, title, font=Font.VERDANA, font_size=15,
                 fill_color=grey, v_align=TextVAlign.MIDDLE)
        for i, (family, _label) in enumerate(samples):
            y = 124 + i * 44
            pen.text(x, y, family, font=Font.VERDANA, font_size=15,
                     fill_color=grey, v_align=TextVAlign.MIDDLE)
            pen.text(x + 160, y, sample_text, font=family, font_size=27,
                     fill_color=ink, v_align=TextVAlign.MIDDLE)

    column(40, "Chinese fonts (system)", CN_FONT_SAMPLES, "汉字示例 ABC")
    column(460, "Latin fonts (system)", LATIN_FONT_SAMPLES, "Sphinx 1234")

    # 自带字体一栏：真实读包内 assets/fonts，走 find_font_file + @font-face 内嵌
    pen.line((40, 500), (w - 40, 500), stroke_color="#DDDDDD")
    pen.text(40, 522, "Bundled fonts (assets/fonts) — embedded via @font-face",
             font=Font.VERDANA, font_size=15, fill_color=grey,
             v_align=TextVAlign.MIDDLE)
    for i, (filename, sample) in enumerate(BUNDLED_FONT_SAMPLES):
        bx = 40 if i % 2 == 0 else 460
        by = 562 + (i // 2) * 52
        path = find_font_file(os.path.splitext(filename)[0])
        pen.text(bx, by, filename, font=Font.VERDANA, font_size=14,
                 fill_color=grey, v_align=TextVAlign.MIDDLE)
        pen.text(bx + 190, by, sample, font=path if path else Font.VERDANA,
                 font_size=26, fill_color=ink, v_align=TextVAlign.MIDDLE)

    pen.text(40, 672, "font file (.ttf/.otf/.ttc): embed via @font-face — "
                      "find_font_file() / assets/fonts, see examples/demo_fonts.py",
             font=Font.VERDANA, font_size=15, fill_color=grey,
             v_align=TextVAlign.MIDDLE)
    return _finish(pen, out_png)


BUILDERS = {
    "malight/board/fx.py": build_fx_preview,
    "malight/board/filters.py": build_filters_preview,
    "malight/elements/text.py": build_text_preview,
    "malight/fonts.py": build_fonts_preview,
}


def preview_link(src, fname):
    """
    算出「从某个模块的 .md 指向 malight/assets/images/xxx.png」的相对链接。 / Build the relative link from a module's .md to malight/assets/images/xxx.png.

    文档在各子包目录里、图片集中在包内 assets/ 下，所以链接形如
    ``../assets/images/fx_preview.png``；统一在这里算，改目录结构只动一处。

    示例::
        preview_link("malight/board/fx.py", "fx_preview.png")
        # -> "../assets/images/fx_preview.png"
    """
    rel = os.path.relpath(os.path.join("malight", "assets", "images", fname),
                          os.path.dirname(src))
    return rel.replace(os.sep, "/")


def main(argv):
    check = "--check" in argv
    bad = 0
    if not check:
        os.makedirs(IMAGES_DIR, exist_ok=True)
    for mod, (fname, _cn, _en) in sorted(PREVIEWS.items()):
        out_png = os.path.join(IMAGES_DIR, fname)
        if check:
            ok = os.path.isfile(out_png) and os.path.getsize(out_png) > 1000
            print(("  OK   " if ok else "  缺失 MISSING ") + os.path.relpath(
                out_png, ROOT))
            bad += 0 if ok else 1
            continue
        BUILDERS[mod](out_png)
        print("已生成 / written:", os.path.relpath(out_png, ROOT))
    if check and bad:
        raise SystemExit("有 %d 张预览图缺失，请运行 tools/gen_previews.py" % bad)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
