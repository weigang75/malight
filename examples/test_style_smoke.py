# -*- coding: utf-8 -*-
"""
公共样式冒烟测试（不透明度 / 透明度族 + edge_detect 线宽）
=========================================================

背景（都是真踩过的坑）：
1. text 的 opacity 曾被 ``_update_attrs`` 签名显式捕获后丢弃 —— 参数存在、
   节点却没有任何 opacity 属性，且 set_opacity() 走 update() 重放同一条
   路同样失效（circle/rect 都正常，只有 text 中招）。
2. FilterAPI（pen.fx 工厂）的方法包装层曾不转发新加的参数
   （edge_detect(width=2) 报 TypeError）。

运行::

    python test_style_smoke.py

期望输出::

    opacity / fill_opacity / stroke_opacity 全通过
    edge_detect(width) 全通过
    ALL STYLE SMOKE TESTS PASSED
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import malight                                   # noqa: E402
from malight import Malight                      # noqa: E402

pen = Malight("style_smoke", width=600, height=400)

# ---------------------------------------------------------------------------
# 1) opacity：创建参数、set_opacity、update 重放，三条路都必须落到节点属性
# ---------------------------------------------------------------------------
t1 = pen.text(60, 60, "A", font_size=30, fill_color="#345", opacity=0.1)
assert t1.node.attribs.get("opacity") == 0.1, "text 的 opacity= 创建参数被吞了"

t2 = pen.text(60, 120, "B", font_size=30, fill_color="#345").set_opacity(0.2)
assert t2.node.attribs.get("opacity") == 0.2, "text.set_opacity() 没生效"

t3 = pen.text(60, 180, "C", font_size=30, fill_color="#345")
t3.update(font_size=48).set_opacity(0.3)         # 先改别的再设透明度（重放路径）
assert t3.node.attribs.get("opacity") == 0.3 and \
       t3.node.attribs.get("font-size") == 48, "text.update 重放后 opacity 丢失"

t4 = pen.text(60, 240, "D", font_size=30, fill_color="#345")
assert "opacity" not in t4.node.attribs, "未设置 opacity 时不应写属性"

# 其余元素的三条路（此前就正常，钉住别再坏）
c1 = pen.circle(420, 80, 30, fill_color="red", opacity=0.25)
c2 = pen.circle(420, 160, 30, fill_color="red").set_opacity(0.25)
c3 = pen.circle(420, 240, 30, fill_color="red")
c3.update(opacity=0.25)
for i, c in enumerate((c1, c2, c3), 1):
    assert c.node.attribs.get("opacity") == 0.25, "circle 第 %d 条路 opacity 失效" % i

# fill_opacity / stroke_opacity（text 与 circle 各测一条）
t5 = pen.text(60, 300, "E", font_size=30, fill_color="#345").set_fill_opacity(0.4)
assert t5.node.attribs.get("fill-opacity") == 0.4, "text.set_fill_opacity 没生效"
c4 = pen.circle(420, 320, 30, fill_color="none", stroke_color="red",
                stroke_width=4).set_stroke_opacity(0.5)
assert c4.node.attribs.get("stroke-opacity") == 0.5, "circle.set_stroke_opacity 没生效"

print("  opacity / fill_opacity / stroke_opacity 全通过")

# ---------------------------------------------------------------------------
# 2) edge_detect(width)：FilterChain 本体 + FilterAPI 工厂包装都要转发参数
# ---------------------------------------------------------------------------
e1 = pen.fx.edge_detect()
assert [c.tag for c in e1.node.children] == ["feConvolveMatrix"], \
    "默认 edge_detect 只应有一个 feConvolveMatrix"

e2 = pen.fx.edge_detect(2.5)
tags = [(c.tag, c.attribs.get("operator"), c.attribs.get("radius"))
        for c in e2.node.children]
assert tags == [("feConvolveMatrix", None, None),
                ("feMorphology", "dilate", 2.5)], "edge_detect(2.5) 结构不对: %s" % tags

e3 = pen.fx.chain().edge_detect(2).grayscale()   # 链上继续叠加不受影响
assert [c.tag for c in e3.node.children] == \
    ["feConvolveMatrix", "feMorphology", "feColorMatrix"], "链式叠加被破坏"

el = pen.star(300, 200, 100, fill_color="#fca311", filter=pen.fx.edge_detect(2))
assert el.node.attribs.get("filter"), "edge_detect(width) 作为 filter= 没绑上"

print("  edge_detect(width) 全通过")

# ---------------------------------------------------------------------------
# 3) to_group()：原地包组、层叠位置不变、元素滤镜与组滤镜各一条链
# ---------------------------------------------------------------------------
a = pen.circle(60, 360, 20, fill_color="red")
m = pen.circle(120, 360, 20, fill_color="green")
z = pen.circle(180, 360, 20, fill_color="blue")
gw = m.fx_glow(4).to_group()
assert type(gw).__name__ == "GroupElement", "to_group 应返回 GroupElement"
assert m.parent_node is gw.node, "原元素应在新组里"
assert m.node.attribs.get("filter"), "元素自身滤镜丢了"
assert not gw.node.attribs.get("filter"), "to_group 时组本身不应带滤镜"
kids = pen.canvas_node.children
assert kids.index(gw.node) == kids.index(a.node) + 1, "组应顶替原元素的层叠位置"
gw.fx_shadow(1, 1, 0.5, "#000000", 0.6)          # 组级滤镜（独立于元素滤镜）
assert gw.node.attribs.get("filter") != m.node.attribs.get("filter"),     "元素滤镜与组滤镜应是两条链"

# ---------------------------------------------------------------------------
# 4) to_template() + clone()：元素转 <symbol> 模板并盖章 <use> 实例
# ---------------------------------------------------------------------------
r = pen.rect(300, 60, 120, 60, corner_radius=10, fill_color="#e63946")
box = r.bbox()                                   # (300, 60, 420, 120)
tpl = r.to_template()
assert type(tpl).__name__ == "TemplateElement", "to_template 应返回 TemplateElement"
assert r.parent_node is tpl.node, "原元素应已移入 <symbol>"
assert tpl.node.attribs.get("viewBox") == "300 60 120 60", \
    "viewBox 应按包围盒推算: %r" % tpl.node.attribs.get("viewBox")
tid = tpl.node.attribs.get("id")
assert tid and tid.startswith("template-"), "未给 id 时应自动生成 template-N"

u1 = tpl.clone()                                 # 原位原尺寸盖章
assert type(u1).__name__ == "UseElement", "clone 应返回 UseElement"
assert u1.node.attribs.get("href") == "#%s" % tid, "实例应引用模板 id"
assert (u1.node.attribs.get("x"), u1.node.attribs.get("y"),
        u1.node.attribs.get("width"), u1.node.attribs.get("height")) == \
       (300, 60, 120, 60), "clone() 缺省应在原位按原尺寸盖章"

u2 = tpl.clone(x=450, width=80).fx_shadow(1, 1, 2)   # 移动缩放 + 实例滤镜
assert u2.node.attribs.get("x") == 450 and u2.node.attribs.get("width") == 80, \
    "clone(x=, width=) 应生效"
assert u2.node.attribs.get("filter"), "实例应可继续链式加滤镜"

# 画布上不应再有原 rect（已进 defs），实例应挂在画布上
assert not pen.canvas_node.children or all(
    c is not r.node for c in pen.canvas_node.children), "原元素不应留在画布上"
sym_nodes = [c for c in pen.defs_node.children if c.tag == "symbol"]
assert any(c is tpl.node for c in sym_nodes), "模板应挂在 <defs> 里"
use_nodes = [c for c in pen.canvas_node.children if c.tag == "use"]
assert len(use_nodes) == 2, "应有两个 <use> 实例: %d" % len(use_nodes)

print("  to_template / clone 全通过")

# ---------------------------------------------------------------------------
# 5) 资源嵌入模式：字体默认「按用字自动子集化」，可选整份内嵌 / 只引用路径；
#    图片可选只引用路径（不 base64）。字体用仓库自带的两支：Android.ttf 够大
#    （5.6 MB）能看出子集化收益，Digital-7Mono.TTF 够小适合测整份内嵌。
# ---------------------------------------------------------------------------
import io                                                    # noqa: E402
import re                                                    # noqa: E402

from malight import FontEmbed, ImageEmbed, find_font_file     # noqa: E402

big_font = find_font_file("Android")          # 5.6 MB CJK
small_font = find_font_file("Digital-7Mono") or find_font_file("MusicStaff")

if big_font:
    base = os.path.dirname(os.path.abspath(big_font))
    # --- 默认 SUBSET：文字只写一遍，库自己收集画面用字 ---
    p_sub = Malight("smoke_embed_subset", width=400, height=200)
    p_sub.text(200, 60, "神笔码靓", font=big_font, font_size=36)
    p_sub.text(200, 140, "碼亮", font=big_font, font_size=36)   # 同字体第二段文字
    p_sub.finish()
    svg_sub = open(p_sub.file_path, encoding="utf-8").read()
    assert svg_sub.count("@font-face") == 1, "同一字体文件只应生成一条 @font-face"
    b64 = re.search(r"base64,([A-Za-z0-9+/=]+)\)", svg_sub)
    assert b64, "SUBSET 模式应内嵌 base64 字体"
    sub_bytes = len(b64.group(1)) * 3 // 4
    full_bytes = os.path.getsize(big_font)
    assert sub_bytes < full_bytes * 0.02, (
        "子集化后应远小于原字体：%d vs %d" % (sub_bytes, full_bytes))
    try:
        from fontTools.ttLib import TTFont
        cmap = set(TTFont(io.BytesIO(__import__("base64").b64decode(
            b64.group(1)))).getBestCmap())
        want = {ord(c) for c in "神笔码靓碼亮"}
        assert want <= cmap, "子集字体缺少画面用字: %r" % (want - cmap)
    except ImportError:
        pass                                    # 没装 fontTools 就跳过字形核对

    # --- EMBED：整份内嵌（字节数与源文件一致） ---
    p_emb = Malight("smoke_embed_full", width=400, height=200, fonts=FontEmbed.EMBED)
    p_emb.text(200, 100, "神笔码靓", font=big_font, font_size=36)
    p_emb.finish()
    svg_emb = open(p_emb.file_path, encoding="utf-8").read()
    emb_b64 = re.search(r"base64,([A-Za-z0-9+/=]+)\)", svg_emb).group(1)
    assert abs(len(emb_b64) * 3 // 4 - full_bytes) <= 4, \
        "EMBED 模式应整份内嵌（大小与源文件一致）"

    # --- LINK：不内嵌，只写本地路径 ---
    p_link = Malight("smoke_embed_link", width=400, height=200, fonts="link")
    p_link.text(200, 100, "神笔码靓", font=big_font, font_size=36)
    p_link.finish()
    svg_link = open(p_link.file_path, encoding="utf-8").read()
    assert "@font-face" in svg_link and "base64" not in svg_link, \
        "LINK 模式不应内嵌任何字体数据"
    assert re.search(r'src: url\("file:///[^"]+\.ttf"\)', svg_link), \
        "LINK 模式应写 file:/// 本地路径"
    assert os.path.getsize(p_link.file_path) < 4096, "LINK 模式 SVG 应该很小"

    # --- 族名稳定：三种模式的 font-family 必须一致，否则文字会掉字体 ---
    fams = set()
    for svg in (svg_sub, svg_emb, svg_link):
        fams.add(re.search(r"font-family=\"([^\"]+)\"", svg).group(1))
    assert len(fams) == 1, "同一字体在三种模式下的族名应一致: %r" % fams
    print("  字体嵌入模式（subset / embed / link）全通过")

if small_font:
    p_set = Malight("smoke_embed_setter", width=300, height=150)
    p_set.set_embed(fonts=FontEmbed.LINK, images=ImageEmbed.LINK)
    assert p_set.font_embed == FontEmbed.LINK and p_set.image_embed == ImageEmbed.LINK, \
        "set_embed 应同时改字体与图片的嵌入方式"
    p_set.text(150, 75, "1234", font=small_font, font_size=32)
    p_set.finish()
    assert "base64" not in open(p_set.file_path, encoding="utf-8").read(), \
        "set_embed(fonts=LINK) 后不应再内嵌字体"

# --- 图片 LINK：只引用路径（相对 SVG 所在目录），SVG 里不应出现 data:image ---
import struct                                                # noqa: E402
import zlib                                                  # noqa: E402

_out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output")
os.makedirs(_out, exist_ok=True)
_img = os.path.join(_out, "smoke_embed_sample.png")
_w, _h = 16, 12
_raw = b"".join(b"\x00" + bytes((230, 57, 70)) * _w for _ in range(_h))


def _chunk(tag, data):
    body = tag + data
    return (struct.pack(">I", len(data)) + body
            + struct.pack(">I", zlib.crc32(body) & 0xffffffff))


with open(_img, "wb") as _f:
    _f.write(b"\x89PNG\r\n\x1a\n"
             + _chunk(b"IHDR", struct.pack(">IIBBBBB", _w, _h, 8, 2, 0, 0, 0))
             + _chunk(b"IDAT", zlib.compress(_raw)) + _chunk(b"IEND", b""))

p_img = Malight("smoke_embed_image", width=300, height=200,
                images=ImageEmbed.LINK)
p_img.image(_img, x=20, y=20, width=120, height=90)
p_img.finish()
svg_img = open(p_img.file_path, encoding="utf-8").read()
assert "data:image" not in svg_img, "LINK 模式不应把图片 base64 内嵌"
_href = re.search(r'href="([^"]+)"', svg_img).group(1)
# 引用路径可以是相对路径（不同运行时布局下形态不同），但解析后必须指向同一张图
_ref = os.path.normpath(os.path.join(os.path.dirname(p_img.file_path), _href))
assert _ref == os.path.normpath(_img), \
    "LINK 模式应引用到同一张图片：%r -> %r" % (_href, _ref)

p_img2 = Malight("smoke_embed_image_default", width=300, height=200)
p_img2.image(_img, x=20, y=20, width=120, height=90)
p_img2.finish()
assert "data:image" in open(p_img2.file_path, encoding="utf-8").read(), \
    "默认（EMBED）应把图片 base64 内嵌"
_e = p_img2.image(_img, x=200, y=20, width=60, height=45)
assert str(_e.node.attribs.get("href")).startswith("data:image"), \
    "单张图也走默认 EMBED"
print("  图片嵌入模式（embed / link）全通过")

pen.finish()
print("ALL STYLE SMOKE TESTS PASSED")