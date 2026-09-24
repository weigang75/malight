<!-- 本文件由 tools/gen_docs.py 从源码自动生成，请勿手改。
     要改内容请改同目录的 group.py 里的文档字符串，然后重跑生成器。 -->

# group.py

**简体中文** ｜ [English](group.en.md) ｜ [← 返回 README](../../README.md)

GroupElement 元素（每类一文件，含中文注释与示例）。

---

## 类与方法

### `GroupElement`

组元素（对应中文版 `元素组`）：把多个元素打包，便于整体变换/动画。

| 方法 | 说明 |
|---|---|
| `add_element(el)` | 把元素加入本组（对应中文版 `添加元素`）。 |
| `append(el)` | add_element 的别名（对应中文版 `append`）。 |
| `remove_element(el)` | 从组中移除元素（对应中文版 `移除元素`）。 |
| `elements()` | 取本组内的直接子元素对象（不含孙辈），对应中文版 `元素列表`。 |
| `all_elements()` | 取本组内**所有**后代元素对象（递归展开嵌套组）。 |
| `bbox()` | 组内所有子元素包围盒的并集 (min_x, min_y, max_x, max_y)。 |

---

## 完整示例

在 PyCharm 里点绿色三角直接运行，或命令行：`python malight/elements/group.py`

```python
if __name__ == "__main__":
    import os

    from malight import Malight, ColorName

    _out = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        "..", "..", "output"))
    pen = Malight(os.path.join(_out, "demo_group"), width=620, height=380)
    pen.set_background_color(ColorName.WHITESMOKE)

    # -----------------------------------------------------------------
    # 1) 建组：把多个元素装进一个 <g>，统一变换 / 统一加特效
    # -----------------------------------------------------------------
    g = pen.g(id_="row")
    for i, c in enumerate([ColorName.TOMATO, ColorName.TEAL, ColorName.GOLD,
                           ColorName.STEELBLUE]):
        el = pen.circle(110 + i * 70, 100, 26, fill_color=c)
        el.change_group(g)                      # 方式一：创建后移入组
    g.set_filter(pen.fx.shadow(5, 6, 6))        # 整组一起投影
    print("组内元素数:", len(g.node.children))

    # -----------------------------------------------------------------
    # 2) 组支持嵌套组；append 与 add_element 等价
    # -----------------------------------------------------------------
    card = pen.g(id_="card")
    card.append(pen.rect(70, 180, 190, 110, corner_radius=14,
                         fill_color=ColorName.WHITESMOKE,
                         stroke_color=ColorName.LIGHTGRAY))
    inner = pen.g()
    inner.append(pen.text(165, 225, "嵌套组", font_size=20,
                          fill_color=ColorName.NAVY, h_align="middle"))
    inner.append(pen.text(165, 258, "统一旋转 / 统一透明", font_size=13,
                          fill_color=ColorName.DIMGRAY, h_align="middle"))
    card.append(inner)                          # 组里再放组

    # -----------------------------------------------------------------
    # 3) 整组变换 + 整组透明度
    # -----------------------------------------------------------------
    card.rotate(-8, cx=165, cy=235)
    card.update(opacity=0.95)

    # -----------------------------------------------------------------
    # 4) 组的包围盒（会遍历子元素计算）
    # -----------------------------------------------------------------
    print("组的 bbox:", tuple(round(v, 1) for v in card.bbox()))
    print("组中心:", round(card.center_x, 1), round(card.center_y, 1))

    # -----------------------------------------------------------------
    # 5) 组内元素可以「取出」：换到画布根（传 pen.canvas_node）
    # -----------------------------------------------------------------
    box = pen.rect(360, 60, 90, 90, fill_color=ColorName.KHAKI)
    tmp = pen.g()
    box.change_group(tmp)
    box.change_group(pen.canvas_node)           # 放回画布根
    print("取出后组内元素数:", len(tmp.node.children))

    # -----------------------------------------------------------------
    # 6) 从组里移除元素 / 克隆整个组
    # -----------------------------------------------------------------
    g2 = pen.g()
    extra = pen.circle(430, 250, 30, fill_color=ColorName.PLUM)
    g2.append(extra)
    g2.remove_element(extra)
    clone = g.clone(dx=0, dy=170, id_="row_copy")
    print("克隆组的 id:", clone.node.attribs.get("id"))

    pen.finish()
```

---

## 同级模块

[base](base.zh.md) ｜ [circle](circle.zh.md) ｜ [clippath](clippath.zh.md) ｜ [ellipse](ellipse.zh.md) ｜ [image](image.zh.md) ｜ [line](line.zh.md) ｜ [link](link.zh.md) ｜ [marker](marker.zh.md) ｜ [mask](mask.zh.md) ｜ [path](path.zh.md) ｜ [pattern](pattern.zh.md) ｜ [polygon](polygon.zh.md) ｜ [polyline](polyline.zh.md) ｜ [rect](rect.zh.md) ｜ [svggroup](svggroup.zh.md) ｜ [svgimage](svgimage.zh.md) ｜ [symbol](symbol.zh.md) ｜ [text](text.zh.md) ｜ [textpath](textpath.zh.md) ｜ [use](use.zh.md)
