<!-- 本文件由 tools/gen_docs.py 从源码自动生成，请勿手改。
     要改内容请改同目录的 line.py 里的文档字符串，然后重跑生成器。 -->

# line.py

**简体中文** ｜ [English](line.en.md) ｜ [← 返回 README](../../README.md)

LineElement 元素（每类一文件，含中文注释与示例）。

---

## 类与方法

### `LineElement`

线元素（对应中文版 `线元素`）。

| 方法 | 说明 |
|---|---|
| `bbox()` | 包围盒。 |
| `set_start(value)` | 设置 start（等价 `update(start=value)`）。 |
| `get_start()` | 读取 start 的当前属性值。 |
| `set_end(value)` | 设置 end（等价 `update(end=value)`）。 |
| `get_end()` | 读取 end 的当前属性值。 |

---

## 完整示例

在 PyCharm 里点绿色三角直接运行，或命令行：`python malight/elements/line.py`

```python
if __name__ == "__main__":
    import os

    from malight import (Malight, ColorName, StrokeCap, StrokeJoin, DashStyle,
                         VectorEffect)

    _out = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        "..", "..", "output"))
    pen = Malight(os.path.join(_out, "demo_line"), width=620, height=360)
    pen.set_background_color(ColorName.WHITESMOKE)

    # 1) 基本线段：起点 -> 终点
    pen.line((40, 60), (580, 60), stroke_color=ColorName.NAVY, stroke_width=3)

    # 2) 圆头粗线：画「胶囊线」/ 手绘感粗笔画时最常用
    pen.line((40, 120), (580, 120), stroke_color=ColorName.TOMATO,
             stroke_width=16, stroke_cap=StrokeCap.ROUND)

    # 3) 虚线预设（枚举），不用再手写 "8 4"
    pen.line((40, 180), (580, 180), stroke_color=ColorName.SEAGREEN,
             stroke_width=4, stroke_style=DashStyle.DASH_DOT_DOT)

    # 4) 虚线相位偏移：同样的虚线错开排列，做「流动/进度」效果
    for i in range(6):
        pen.line((60 + i * 90, 220), (60 + i * 90, 280),
                 stroke_color=ColorName.SLATEBLUE, stroke_width=6,
                 stroke_style=DashStyle.DASHED, dash_offset=i * 4)

    # 5) 蚂蚁线流动动画（浏览器打开 SVG 可见）
    flow = pen.line((40, 320), (580, 320), stroke_color=ColorName.CRIMSON,
                    stroke_width=4, stroke_cap=StrokeCap.ROUND)
    flow.animate_dash_flow(dur=1.5, dash="10 8")

    # 6) 缩放画布时线宽保持不变（工程图/图标内嵌常需要）
    ln = pen.line((40, 345), (580, 345), stroke_color=ColorName.INDIGO,
                  stroke_width=2, vector_effect=VectorEffect.NON_SCALING_STROKE)
    print("线包围盒:", tuple(round(v, 1) for v in ln.bbox()))

    # 7) 折角样式：stroke_join 控制两段线的拐角
    pen.polyline([(40, 292), (90, 262), (140, 292)],
                 stroke_color=ColorName.CHOCOLATE, stroke_width=8,
                 stroke_join=StrokeJoin.ROUND)

    # 8) 局部更新：只改终点坐标
    l2 = pen.line((420, 250), (500, 250), stroke_color=ColorName.GOLD,
                  stroke_width=6, stroke_cap=StrokeCap.ROUND)
    l2.update(end=(560, 290))
    print("更新后线 d/坐标:", l2.node.attribs)

    pen.finish()
```

---

## 同级模块

[base](base.zh.md) ｜ [circle](circle.zh.md) ｜ [clippath](clippath.zh.md) ｜ [ellipse](ellipse.zh.md) ｜ [group](group.zh.md) ｜ [image](image.zh.md) ｜ [link](link.zh.md) ｜ [marker](marker.zh.md) ｜ [mask](mask.zh.md) ｜ [path](path.zh.md) ｜ [pattern](pattern.zh.md) ｜ [polygon](polygon.zh.md) ｜ [polyline](polyline.zh.md) ｜ [rect](rect.zh.md) ｜ [svggroup](svggroup.zh.md) ｜ [svgimage](svgimage.zh.md) ｜ [symbol](symbol.zh.md) ｜ [text](text.zh.md) ｜ [textpath](textpath.zh.md) ｜ [topath](topath.zh.md) ｜ [use](use.zh.md)
