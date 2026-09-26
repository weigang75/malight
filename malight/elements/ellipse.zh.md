<!-- 本文件由 tools/gen_docs.py 从源码自动生成，请勿手改。
     要改内容请改同目录的 ellipse.py 里的文档字符串，然后重跑生成器。 -->

# ellipse.py

**简体中文** ｜ [English](ellipse.en.md) ｜ [← 返回 README](../../README.md)

EllipseElement 元素（每类一文件，含中文注释与示例）。

---

## 类与方法

### `EllipseElement`

椭圆元素（对应中文版 `椭圆元素`）。

| 方法 | 说明 |
|---|---|
| `bbox()` | 包围盒（未考虑旋转）。 |
| `set_x(value)` | 设置 x（等价 `update(x=value)`）。 |
| `get_x()` | 读取 x 的当前属性值。 |
| `set_y(value)` | 设置 y（等价 `update(y=value)`）。 |
| `get_y()` | 读取 y 的当前属性值。 |
| `set_radius(value)` | 设置 radius（等价 `update(radius=value)`）。 |
| `get_radius()` | 读取 radius 的当前属性值。 |
| `set_rotate(value)` | 设置 rotate（等价 `update(rotate=value)`）。 |
| `get_rotate()` | 读取 rotate 的当前属性值。 |

---

## 完整示例

在 PyCharm 里点绿色三角直接运行，或命令行：`python malight/elements/ellipse.py`

```python
if __name__ == "__main__":
    import os

    from malight import Malight, ColorName, Color

    _out = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        "..", "..", "output"))
    pen = Malight(os.path.join(_out, "demo_ellipse"), width=620, height=360)
    pen.set_background_color(ColorName.WHITESMOKE)

    # 1) 标准椭圆：radius=(rx, ry)
    pen.ellipse(140, 100, radius=(110, 60), fill_color=ColorName.SKYBLUE,
                stroke_color=ColorName.NAVY, stroke_width=2)

    # 2) 只传一个数值 = 正圆（等价 pen.circle）
    pen.ellipse(340, 100, radius=55, fill_color=ColorName.KHAKI,
                stroke_color=ColorName.CHOCOLATE, stroke_width=3)

    # 3) 旋转椭圆（英文版增强能力，中文原版不支持）
    e = pen.ellipse(500, 100, radius=(90, 30), rotate=-25,
                    fill_color=ColorName.PLUM, stroke_color=ColorName.INDIGO,
                    stroke_width=2, opacity=0.9)
    print("旋转椭圆 bbox:", tuple(round(v, 1) for v in e.bbox()))

    # 4) 渐变填充 + 阴影，做「立体药丸」效果
    grad = pen.radialGradient((0.5, 0.3), 0.7, "white", ColorName.STEELBLUE)
    pen.ellipse(160, 260, radius=(120, 45), fill_color=grad.paint(),
                stroke_color=Color.TRANSPARENT,
                filter=pen.fx.shadow(4, 6, 6))

    # 5) 椭圆同样支持枚举化的描边样式
    from malight import StrokeCap, DashStyle
    pen.ellipse(430, 260, radius=(120, 45), fill_color="none",
                stroke_color=ColorName.SEAGREEN, stroke_width=5,
                stroke_cap=StrokeCap.ROUND, stroke_style=DashStyle.DASH_DOT)

    # 6) 局部更新：只改 rx/ry，圆心不变
    e2 = pen.ellipse(160, 340, radius=(40, 20), fill_color=ColorName.TOMATO)
    e2.update(radius=(80, 24))
    print("更新后椭圆的宽高:", round(e2.width, 1), round(e2.height, 1))

    pen.finish()
```

---

## 同级模块

[base](base.zh.md) ｜ [circle](circle.zh.md) ｜ [clippath](clippath.zh.md) ｜ [group](group.zh.md) ｜ [image](image.zh.md) ｜ [line](line.zh.md) ｜ [link](link.zh.md) ｜ [marker](marker.zh.md) ｜ [mask](mask.zh.md) ｜ [path](path.zh.md) ｜ [pattern](pattern.zh.md) ｜ [polygon](polygon.zh.md) ｜ [polyline](polyline.zh.md) ｜ [rect](rect.zh.md) ｜ [svggroup](svggroup.zh.md) ｜ [svgimage](svgimage.zh.md) ｜ [symbol](symbol.zh.md) ｜ [text](text.zh.md) ｜ [textpath](textpath.zh.md) ｜ [topath](topath.zh.md) ｜ [use](use.zh.md)
