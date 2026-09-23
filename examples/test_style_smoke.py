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

pen.finish()
print("ALL STYLE SMOKE TESTS PASSED")
