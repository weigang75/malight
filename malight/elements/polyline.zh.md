<!-- 本文件由 tools/gen_docs.py 从源码自动生成，请勿手改。
     要改内容请改同目录的 polyline.py 里的文档字符串，然后重跑生成器。 -->

# polyline.py

**简体中文** ｜ [English](polyline.en.md) ｜ [← 返回 README](../../README.md)

PolylineElement 元素（每类一文件，含中文注释与示例）。

---

## 类与方法

### `PolylineElement`

折线元素（对应中文版 `折线元素`）。

| 方法 | 说明 |
|---|---|
| `bbox()` | 包围盒。 |
| `set_points(value)` | 设置 points（等价 `update(points=value)`）。 |
| `get_points()` | 读取 points 的当前属性值。 |

---

## 完整示例

在 PyCharm 里点绿色三角直接运行，或命令行：`python malight/elements/polyline.py`

```python
if __name__ == "__main__":
    import os

    from malight import Malight, ColorName, StrokeJoin, StrokeCap, DashStyle

    _out = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        "..", "..", "output"))
    pen = Malight(os.path.join(_out, "demo_polyline"), width=620, height=360)
    pen.set_background_color(ColorName.WHITESMOKE)

    # 1) 折线：顶点依次直连，首尾不闭合（不做 Z）
    pen.polyline([(40, 280), (120, 80), (200, 280), (280, 80)],
                 fill_color="none", stroke_color=ColorName.NAVY,
                 stroke_width=3, stroke_join=StrokeJoin.ROUND)

    # 2) 折线也能填充：SVG 会把首尾自动连起来填充，但描边仍不闭合
    pen.polyline([(340, 280), (400, 100), (470, 240), (560, 120)],
                 fill_color=ColorName.KHAKI, stroke_color=ColorName.CHOCOLATE,
                 stroke_width=2, opacity=0.9)

    # 3) 用折线围成封闭外形（描边不闭合，适合「开口」造型）
    pen.polyline([(60, 335), (160, 305), (260, 335), (160, 355)],
                 fill_color=ColorName.SKYBLUE,
                 stroke_color=ColorName.STEELBLUE, stroke_width=2)

    # 4) 折线同样支持线端/虚线枚举
    pen.polyline([(340, 340), (420, 315), (500, 345), (560, 320)],
                 fill_color="none", stroke_color=ColorName.CRIMSON,
                 stroke_width=6, stroke_cap=StrokeCap.ROUND,
                 stroke_style=DashStyle.DASHED)

    # 5) 拿回元素改样式 / 量尺寸
    pl = pen.polyline([(300, 60), (360, 60), (360, 140), (300, 140)],
                      fill_color="none", stroke_color=ColorName.TEAL,
                      stroke_width=4)
    pl.update(stroke_color=ColorName.INDIGO, stroke_width=6)
    print("折线包围盒:", tuple(round(v, 1) for v in pl.bbox()))
    print("折线顶点串:", pl.node.attribs.get("points"))

    # 6) 内部数据也能读出来（顶点列表）
    print("顶点列表:", pl.points if hasattr(pl, "points") else "(见 node.attribs)")

    pen.finish()
```

---

## 同级模块

[base](base.zh.md) ｜ [circle](circle.zh.md) ｜ [clippath](clippath.zh.md) ｜ [ellipse](ellipse.zh.md) ｜ [group](group.zh.md) ｜ [image](image.zh.md) ｜ [line](line.zh.md) ｜ [link](link.zh.md) ｜ [marker](marker.zh.md) ｜ [mask](mask.zh.md) ｜ [path](path.zh.md) ｜ [pattern](pattern.zh.md) ｜ [polygon](polygon.zh.md) ｜ [rect](rect.zh.md) ｜ [svggroup](svggroup.zh.md) ｜ [svgimage](svgimage.zh.md) ｜ [symbol](symbol.zh.md) ｜ [text](text.zh.md) ｜ [textpath](textpath.zh.md) ｜ [topath](topath.zh.md) ｜ [use](use.zh.md)
