<!-- 本文件由 tools/gen_docs.py 从源码自动生成，请勿手改。
     要改内容请改同目录的 polygon.py 里的文档字符串，然后重跑生成器。 -->

# polygon.py

**简体中文** ｜ [English](polygon.en.md) ｜ [← 返回 README](../../README.md)

PolygonElement 元素（每类一文件，含中文注释与示例）。

---

## 类与方法

### `PolygonElement`

多边形元素（对应中文版 `多边形元素`，自动闭合）。

| 方法 | 说明 |
|---|---|
| `bbox()` | 包围盒。 |
| `set_points(value)` | 设置 points（等价 `update(points=value)`）。 |
| `get_points()` | 读取 points 的当前属性值。 |

---

## 完整示例

在 PyCharm 里点绿色三角直接运行，或命令行：`python malight/elements/polygon.py`

```python
if __name__ == "__main__":
    import os

    from malight import Malight, ColorName, FillRule

    _out = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        "..", "..", "output"))
    pen = Malight(os.path.join(_out, "demo_polygon"), width=660, height=380)
    pen.set_background_color(ColorName.WHITESMOKE)

    # 1) 三角形：给顶点列表即可
    pen.polygon([(50, 260), (150, 60), (250, 260)],
                fill_color=ColorName.TOMATO, stroke_color=ColorName.MAROON,
                stroke_width=2)

    # 2) ★ 带孔多边形：外圈顶点 + 内圈顶点拼在一起 + FillRule.EVENODD
    #    这是复刻简笔画「挖洞 / 镂空」最关键的技巧（英文版增强能力）
    outer = [(300, 60), (560, 60), (560, 260), (300, 260)]
    inner = [(355, 105), (505, 105), (505, 215), (355, 215)]
    pen.polygon(outer + inner, fill_color=ColorName.TEAL,
                fill_rule=FillRule.EVENODD, stroke_color="none")

    # 3) 对照：同一批顶点用 NONZERO（默认）就不挖空
    pen.polygon(outer + inner, fill_color="none",
                stroke_color=ColorName.WHITESMOKE, stroke_width=1)

    # 4) 正多边形系列（内部就是 polygon，多了自动算顶点）
    pen.hexagon(80, 320, 45, fill_color=ColorName.LAVENDER,
                stroke_color=ColorName.INDIGO, stroke_width=2)
    pen.pentagon(200, 320, 45, fill_color=ColorName.KHAKI,
                 stroke_color=ColorName.CHOCOLATE, stroke_width=2)
    pen.triangle(310, 320, 45, fill_color=ColorName.PLUM,
                 stroke_color=ColorName.INDIGO, stroke_width=2)

    # 5) 星形与爱心（同样返回 PolygonElement）
    pen.star(450, 320, 48, n=5, fill_color=ColorName.GOLD,
             stroke_color=ColorName.GOLDENROD)
    pen.heart(570, 318, 48, fill_color=ColorName.CRIMSON,
              stroke_color=ColorName.MAROON)

    # 6) 钻石形
    pen.diamond(160, 180, 42, stroke_color=ColorName.NAVY,
                fill_color=ColorName.SKYBLUE)

    # 7) 局部更新：只换填充色，顶点不动
    poly = pen.polygon([(240, 140), (290, 140), (265, 200)],
                       fill_color=ColorName.CHOCOLATE)
    poly.update(fill_color=ColorName.SEAGREEN, stroke_width=3)
    print("多边形包围盒:", tuple(round(v, 1) for v in poly.bbox()))
    print("evenodd 的取值是:", FillRule.EVENODD.value)

    pen.finish()
```

---

## 同级模块

[base](base.zh.md) ｜ [circle](circle.zh.md) ｜ [clippath](clippath.zh.md) ｜ [ellipse](ellipse.zh.md) ｜ [group](group.zh.md) ｜ [image](image.zh.md) ｜ [line](line.zh.md) ｜ [link](link.zh.md) ｜ [marker](marker.zh.md) ｜ [mask](mask.zh.md) ｜ [path](path.zh.md) ｜ [pattern](pattern.zh.md) ｜ [polyline](polyline.zh.md) ｜ [rect](rect.zh.md) ｜ [svggroup](svggroup.zh.md) ｜ [svgimage](svgimage.zh.md) ｜ [symbol](symbol.zh.md) ｜ [text](text.zh.md) ｜ [textpath](textpath.zh.md) ｜ [topath](topath.zh.md) ｜ [use](use.zh.md)
