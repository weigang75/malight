<!-- 本文件由 tools/gen_docs.py 从源码自动生成，请勿手改。
     要改内容请改同目录的 marker.py 里的文档字符串，然后重跑生成器。 -->

# marker.py

**简体中文** ｜ [English](marker.en.md) ｜ [← 返回 README](../../README.md)

MarkerElement 元素（每类一文件，含中文注释与示例）。

---

## 类与方法

### `MarkerElement`

标记元素（`<marker>`，对应中文版 `标记元素`）：定义箭头等线端装饰。

| 方法 | 说明 |
|---|---|
| `add_element(el)` | 把图形加入 marker 内容。 |
| `set_id_(value)` | 设置 id_（等价 `update(id_=value)`）。 |
| `get_id_()` | 读取 id_ 的当前属性值。 |
| `set_ref_x(value)` | 设置 ref_x（等价 `update(ref_x=value)`）。 |
| `get_ref_x()` | 读取 ref_x 的当前属性值。 |
| `set_ref_y(value)` | 设置 ref_y（等价 `update(ref_y=value)`）。 |
| `get_ref_y()` | 读取 ref_y 的当前属性值。 |
| `set_marker_width(value)` | 设置 marker_width（等价 `update(marker_width=value)`）。 |
| `get_marker_width()` | 读取 marker_width 的当前属性值。 |
| `set_marker_height(value)` | 设置 marker_height（等价 `update(marker_height=value)`）。 |
| `get_marker_height()` | 读取 marker_height 的当前属性值。 |
| `set_orient(value)` | 设置 orient（等价 `update(orient=value)`）。 |
| `get_orient()` | 读取 orient 的当前属性值。 |
| `set_marker_units(value)` | 设置 marker_units（等价 `update(marker_units=value)`）。 |
| `get_marker_units()` | 读取 marker_units 的当前属性值。 |

---

## 完整示例

在 PyCharm 里点绿色三角直接运行，或命令行：`python malight/elements/marker.py`

```python
if __name__ == "__main__":
    import os

    from malight import Malight, ColorName

    _out = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        "..", "..", "output"))
    pen = Malight(os.path.join(_out, "demo_marker"), width=620, height=380)
    pen.set_background_color(ColorName.WHITESMOKE)

    # -----------------------------------------------------------------
    # 1) 定义箭头标记（<marker> 放在 <defs> 里，可被多条线复用）
    #    ref_x / ref_y 是「参考点」——箭头尖端要对齐线端，所以取 (9, 3) / ref_x
    #    orient="auto" 让箭头自动跟随线条方向（画箭头必选）
    # -----------------------------------------------------------------
    arrow = pen.marker(id_="arrow_end", ref_x=9, ref_y=3,
                       width=10, height=6, orient="auto")
    arrow.add_element(pen.polygon([(0, 0), (9, 3), (0, 6)],
                                  fill_color=ColorName.TOMATO,
                                  stroke_color="none"))

    # 2) 起点用圆点标记
    dot = pen.marker(id_="dot_start", ref_x=4, ref_y=4, width=8, height=8)
    dot.add_element(pen.circle(4, 4, 4, fill_color=ColorName.TEAL,
                               stroke_color="none"))

    # 3) 线条上挂标记：marker_end / marker_start 是 SVG 原生属性， / 3) marker_end
    #    用 extra 直接透传即可
    ln = pen.line((60, 90), (560, 90), stroke_color=ColorName.NAVY,
                  stroke_width=3, extra={"marker_end": "url(#arrow_end)"})
    pen.line((60, 150), (560, 150), stroke_color=ColorName.STEELBLUE,
             stroke_width=3,
             extra={"marker_start": "url(#dot_start)",
                    "marker_end": "url(#arrow_end)"})

    # 4) 曲线路径也能挂标记（箭头会顺着切线方向转）
    p = pen.path(fill_color="none", stroke_color=ColorName.CRIMSON,
                 stroke_width=3, extra={"marker_end": "url(#arrow_end)"})
    p.move_to(60, 300)
    p.cubic_to((180, 190), (360, 380), (560, 260))
    print("箭头线 marker-end =", ln.node.attribs.get("marker-end"))

    # 5) marker_units 控制箭头是否随线宽缩放
    #    "strokeWidth"（默认，随线宽） / "userSpaceOnUse"（固定像素）
    fixed = pen.marker(id_="arrow_fixed", ref_x=9, ref_y=3, width=10, height=6,
                       orient="auto", marker_units="userSpaceOnUse")
    fixed.add_element(pen.polygon([(0, 0), (9, 3), (0, 6)],
                                  fill_color=ColorName.INDIGO))
    pen.line((60, 340), (560, 340), stroke_color=ColorName.INDIGO,
             stroke_width=1, extra={"marker_end": "url(#arrow_fixed)"})

    # 6) 局部更新：改方向策略或参考点
    arrow.update(orient="auto-start-reverse")
    print("箭头方向:", arrow.node.attribs.get("orient"),
          "| refX:", arrow.node.attribs.get("refX"))

    pen.finish()
```

---

## 同级模块

[base](base.zh.md) ｜ [circle](circle.zh.md) ｜ [clippath](clippath.zh.md) ｜ [ellipse](ellipse.zh.md) ｜ [group](group.zh.md) ｜ [image](image.zh.md) ｜ [line](line.zh.md) ｜ [link](link.zh.md) ｜ [mask](mask.zh.md) ｜ [path](path.zh.md) ｜ [pattern](pattern.zh.md) ｜ [polygon](polygon.zh.md) ｜ [polyline](polyline.zh.md) ｜ [rect](rect.zh.md) ｜ [svggroup](svggroup.zh.md) ｜ [svgimage](svgimage.zh.md) ｜ [symbol](symbol.zh.md) ｜ [text](text.zh.md) ｜ [textpath](textpath.zh.md) ｜ [use](use.zh.md)
