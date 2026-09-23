# -*- coding: utf-8 -*-
"""滤镜全量冒烟测试：每个工厂方法/链式/元素绑定/旧包 shim。"""
import os
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from malight import Malight, Malight

pen = Malight("fx_smoke", width=1000, height=1000)
fx = pen.fx

methods = [
    ("blur", (4,)), ("sharpen", (0.7,)), ("motion_blur", (10, 30)),
    ("shadow", (5, 6, 4, "#333", 0.4)), ("drop_shadow", (5, 5, 4)),
    ("inner_shadow", (4, 4, 4)), ("glow", (8, "#00b4d8")),
    ("inner_glow", (8, "#ffd60a")), ("bevel", (1.2, 2)),
    ("engrave", (1.5, 0.6)),
    ("outline", (4, "#d62828")), ("roughen", (5, 0.05)),
    ("noise", (0.2,)), ("emboss", (45,)), ("edge_detect", ()),
    ("saturate", (1.5,)), ("hue_rotate", (120,)), ("grayscale", ()),
    ("sepia", ()), ("brightness", (1.3,)), ("contrast", (1.4,)),
    ("gamma", (0.9, 1.0, 1.1)), ("invert", ()), ("posterize", (3,)),
    ("color_overlay", ("#073b4c", 0.7)),
]
y = 50
for name, args in methods:
    f = getattr(fx, name)(*args)
    el = pen.circle(120, y, 35, fill_color="#4e79a7")
    el.set_filter(f)
    assert el.node.attribs.get("filter") == f"url(#{f.id})", name
    y += 38

# 链式
chain = fx.chain().blur(2).shadow(5, 5, 4).saturate(1.3).outline(2, "white")
pen.rect(300, 100, 200, 120, fill_color="#e15759", filter=chain)
# filter= 构造参数 + id 字符串形式
fid = fx.glow(6, "#ffd60a")
pen.text(500, 300, "FILTER", font_size=48, filter=str(fid))
pen.star(700, 200, 60, fill_color="#f4a261", filter=fx.sharpen(0.8))
# 清除滤镜
el = pen.circle(700, 400, 40, fill_color="#333")
el.set_filter(fid).set_filter(None)
assert el.node.attribs.get("filter") is None

pen.finish()

# XML 合法性
ET.parse(pen.file_path)
src = open(pen.file_path, encoding="utf-8").read()
n_filters = src.count("<filter ")
n_refs = src.count("filter=")
print(f"filters: {n_filters}, filter refs: {n_refs}")
assert n_filters >= len(methods) + 3

# ---------------------------------------------------------------------------
# 叠加语义：后续的 set_filter / fx_* 是「叠上去」，不是「覆盖前面的」
# ---------------------------------------------------------------------------
pen2 = Malight("fx_stack", width=420, height=320)
fx2 = pen2.fx


def prims(el):
    """取元素当前链的原语标签列表。"""
    return [c.tag for c in el._current_filter_chain().node.children]


# 1) fx_* 链式叠加：内阴影 + 浮雕，两个效果都要在链上
a = pen2.text(60, 90, "叠", font_size=40, fill_color="#c23b22")
a.fx_inner_shadow(1, 1, 2, "#ffffff", 0.6).fx_emboss()
pa = prims(a)
assert "feFlood" in pa and "feConvolveMatrix" in pa, pa
chain_a = a._current_filter_chain()
convolve = [c for c in chain_a.node.children if c.tag == "feConvolveMatrix"][0]
merge = [c for c in chain_a.node.children if c.tag == "feMerge"][0]
assert merge.attribs.get("result"), "合成结果没有 result 名，后面的效果接不上"
assert convolve.attribs["in"] == merge.attribs["result"], \
    "浮雕没接在内阴影的合成结果之后（老版本会掉回 SourceGraphic）"

# 2) 分两次 set_filter 也要叠加（老版本第二次会把第一次顶掉）
b = pen2.rect(200, 40, 140, 90, fill_color="#457b9d")
b.set_filter(fx2.shadow(6, 6, 4))
b.set_filter(fx2.saturate(0.3))
pb = prims(b)
assert "feOffset" in pb and "feColorMatrix" in pb, pb
assert b.node.attribs["filter"] == b._current_filter_chain().url()

# 3) 合并进旧链的临时链要回收，defs 里不堆孤儿 <filter>
n_filters = sum(1 for c in pen2.defs_node.children
                if getattr(c, "tag", "") == "filter")
assert n_filters == 2, f"孤儿 <filter> 没回收：{n_filters}"

# 4) 想真的替换就用 merge=False
c = pen2.circle(340, 90, 32, fill_color="#e15759")
c.set_filter(fx2.glow(5))
c.set_filter(fx2.invert(), merge=False)
assert "feMerge" not in prims(c) and "feComponentTransfer" in prims(c), prims(c)

# 5) 克隆体叠加不串改原件（共用一条链时先私有化）
d = pen2.rect(40, 220, 110, 60, fill_color="#2a9d8f")
d.set_filter(fx2.shadow(5, 5, 4))
e = d.clone(dx=130)
before = len(prims(d))
e.set_filter(fx2.invert())
assert d.node.attribs["filter"] != e.node.attribs["filter"], \
    "克隆体叠加时串改了原件的链"
assert len(prims(d)) == before, "原件的链被追加了效果"

# 6) 跨画板的链要当场报错（否则会绑上一条本画板不存在的 <filter>，静默失效）
f = pen2.rect(40, 120, 60, 40, fill_color="#333")
try:
    f.set_filter(fx.blur(3))          # fx 属于另一个画板
    raise AssertionError("跨画板的滤镜链应当报错")
except ValueError as err:
    assert "另一个绘图板" in str(err) or "another drawing board" in str(err), err

# 7) 名字写错的效果要报错
try:
    pen2.text(0, 0, "x").fx("no_such_effect")
    raise AssertionError("不存在的效果名应当报错")
except AttributeError as err:
    assert "no_such_effect" in str(err), err

# 8) 两个「带合成」的效果叠加，前一个不能被丢掉（engrave 本质就是内阴影 x2）
g = pen2.text(40, 300, "刻", font_size=30, fill_color="#333333")
g.fx_engrave()
merges = [c for c in g._current_filter_chain().node.children
          if c.tag == "feMerge"]
assert len(merges) == 2, "engrave 应该是两次内阴影合成"
assert merges[-1].children[0].attribs["in"] == merges[0].attribs.get("result"), \
    "第二次合成的底图没接在第一次合成的结果上（老版本会掉回 SourceGraphic）"

# ---------------------------------------------------------------------------
# 用法全覆盖：文档承诺的每一种写法都要能跑（漏测过的 fx("custom") 曾真坏过）
# ---------------------------------------------------------------------------
h = pen2.text(200, 300, "法", font_size=30, fill_color="#4e79a7")
h.fx("blur", 2)                                   # 按名字叠加
tags = [c.tag for c in h._current_filter_chain().node.children]
assert "feGaussianBlur" in tags, tags
h.fx("custom", "feBlend", mode="screen", in2="SourceGraphic")   # 自定义原语
tags = [c.tag for c in h._current_filter_chain().node.children]
assert "feBlend" in tags, tags
h.fx_chain().saturate(1.5)                        # 取元素已有的链继续加
assert "feColorMatrix" in [c.tag for c in
                           h._current_filter_chain().node.children], "fx_chain 断链"
i_el = pen2.circle(360, 300, 20, fill_color="#e15759")
pen2.filter.glow(5).apply(i_el)                   # pen.filter 别名 + f.apply(el)
assert i_el.node.attribs.get("filter"), "f.apply(el) 没绑上滤镜"

pen2.finish()
ET.parse(pen2.file_path)
print("fx stack OK: 链式 fx_* / 多次 set_filter / 无孤儿 filter / 克隆隔离 / 跨板报错")

# ---- 旧包 shim 验证（仓库根的 magicpen/ 兼容包，源码目录专用）----
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, repo_root)
try:
    import magicpen  # noqa
    assert magicpen.Malight is Malight
    assert hasattr(magicpen, "Color")
    print("magicpen shim OK:", magicpen.__version__)
except ImportError:
    print("magicpen shim 未安装（发布包不含，仅源码仓库提供），跳过")

# ---- compat 迁移工具验证（含 import magicpen -> import malight）----
from malight import compat
print("compat OK:", hasattr(compat, "MIGRATE") or hasattr(compat, "migrate") or dir(compat)[:5])

print("ALL FILTER SMOKE TESTS PASSED")
