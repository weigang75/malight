<!-- 本文件由 tools/gen_docs.py 从源码自动生成，请勿手改。
     要改内容请改同目录的 circle.py 里的文档字符串，然后重跑生成器。 -->

# circle.py

**简体中文** ｜ [English](circle.en.md) ｜ [← 返回 README](../../README.md)

CircleElement 元素（每类一文件，含中文注释与示例）。

---

## 类与方法

### `CircleElement`

圆元素（对应中文版 `圆元素`）。由 `pen.circle` 创建。

| 方法 | 说明 |
|---|---|
| `bbox()` | 包围盒。 |
| `to_path_element()` | 转换为 PathElement（对应中文版 `转路径元素`）。 |

---

## 完整示例

在 PyCharm 里点绿色三角直接运行，或命令行：`python malight/elements/circle.py`

```python
if __name__ == "__main__":
    import os

    from malight import Malight, ColorName, StrokeCap, DashStyle

    _out = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        "..", "..", "output"))
    pen = Malight(os.path.join(_out, "demo_circle"), width=620, height=360)
    pen.set_background_color(ColorName.WHITESMOKE)

    # 1) 最简写法：圆心 (x, y) + 半径
    pen.circle(90, 90, 50, fill_color=ColorName.DODGERBLUE)

    # 2) 空心圆：填充设为 none（等价 Color.TRANSPARENT）
    pen.circle(230, 90, 50, fill_color="none", stroke_color=ColorName.TOMATO,
               stroke_width=6)

    # 3) 枚举化选项：圆头线端 + 虚线预设（不必再记 "8 4" 这种魔数）
    pen.circle(370, 90, 50, fill_color="none", stroke_color=ColorName.SEAGREEN,
               stroke_width=6, stroke_cap=StrokeCap.ROUND,
               stroke_style=DashStyle.DASHED)

    # 4) 逐边框线偏移：同一虚线不同相位，排在一起像「流动的圈」
    for i in range(3):
        pen.circle(500 + 0, 40 + i * 45, 18, fill_color="none",
                   stroke_color=ColorName.INDIGO, stroke_width=4,
                   stroke_style=DashStyle.DASH_DOT, dash_offset=i * 6)

    # 5) 半透明叠色：两圆重叠处颜色更深（CSS 混合模式）
    pen.circle(90, 250, 55, fill_color=ColorName.TEAL, opacity=0.75,
               blend_mode="multiply")
    pen.circle(150, 250, 55, fill_color=ColorName.GOLD, opacity=0.75,
               blend_mode="multiply")

    # 6) 一行加投影滤镜（滤镜需用浏览器打开 SVG 查看）
    pen.circle(330, 250, 55, fill_color=ColorName.PLUM,
               filter=pen.fx.shadow(6, 8, 8))

    # 7) 拿回元素做后续处理（update 是局部更新，不会动几何）
    c = pen.circle(470, 250, 40, fill_color=ColorName.SKYBLUE)
    c.update(radius=46, stroke_color=ColorName.NAVY, stroke_width=3)
    print("圆的包围盒:", tuple(round(v, 1) for v in c.bbox()))
    print("圆心:", round(c.center_x, 1), round(c.center_y, 1))

    # 8) 圆 → 路径元素（之后可做布尔运算 / 拖动锚点）
    path_el = c.to_path_element()
    print("圆转路径 d =", path_el.get_d())

    pen.finish()
```

---

## 同级模块

[base](base.zh.md) ｜ [clippath](clippath.zh.md) ｜ [ellipse](ellipse.zh.md) ｜ [group](group.zh.md) ｜ [image](image.zh.md) ｜ [line](line.zh.md) ｜ [link](link.zh.md) ｜ [marker](marker.zh.md) ｜ [mask](mask.zh.md) ｜ [path](path.zh.md) ｜ [pattern](pattern.zh.md) ｜ [polygon](polygon.zh.md) ｜ [polyline](polyline.zh.md) ｜ [rect](rect.zh.md) ｜ [svgimage](svgimage.zh.md) ｜ [symbol](symbol.zh.md) ｜ [text](text.zh.md) ｜ [textpath](textpath.zh.md) ｜ [use](use.zh.md)
