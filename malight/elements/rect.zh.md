<!-- 本文件由 tools/gen_docs.py 从源码自动生成，请勿手改。
     要改内容请改同目录的 rect.py 里的文档字符串，然后重跑生成器。 -->

# rect.py

**简体中文** ｜ [English](rect.en.md) ｜ [← 返回 README](../../README.md)

RectElement 元素（每类一文件，含中文注释与示例）。

---

## 类与方法

### `RectElement`

矩形元素（对应中文版 `矩形元素`）。

| 方法 | 说明 |
|---|---|
| `bbox()` | 包围盒（未考虑旋转）。 |
| `set_x(value)` | 设置 x（等价 `update(x=value)`）。 |
| `get_x()` | 读取 x 的当前属性值。 |
| `set_y(value)` | 设置 y（等价 `update(y=value)`）。 |
| `get_y()` | 读取 y 的当前属性值。 |
| `set_width(value)` | 设置 width（等价 `update(width=value)`）。 |
| `get_width()` | 读取 width 的当前属性值。 |
| `set_height(value)` | 设置 height（等价 `update(height=value)`）。 |
| `get_height()` | 读取 height 的当前属性值。 |
| `set_corner_radius(value)` | 设置 corner_radius（等价 `update(corner_radius=value)`）。 |
| `get_corner_radius()` | 读取 corner_radius 的当前属性值。 |
| `set_rotate(value)` | 设置 rotate（等价 `update(rotate=value)`）。 |
| `get_rotate()` | 读取 rotate 的当前属性值。 |

---

## 完整示例

在 PyCharm 里点绿色三角直接运行，或命令行：`python malight/elements/rect.py`

```python
if __name__ == "__main__":
    import os

    from malight import Malight, ColorName, DashStyle, FillRule, Font

    _out = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        "..", "..", "output"))
    pen = Malight(os.path.join(_out, "demo_rect"), width=620, height=400)
    pen.set_background_color(ColorName.WHITESMOKE)

    # 1) 普通矩形
    pen.rect(40, 40, 200, 110, fill_color=ColorName.SKYBLUE,
             stroke_color=ColorName.NAVY, stroke_width=2)

    # 2) 圆角矩形 + 投影（UI 卡片最常见）
    pen.rect(280, 40, 220, 110, corner_radius=18,
             fill_color=ColorName.TOMATO, filter=pen.fx.shadow(6, 7, 8))
    pen.text(390, 105, "卡片", font=Font.SIMHEI, font_size=22,
             fill_color="white", h_align="middle")

    # 3) 旋转矩形（英文版增强能力）
    pen.rect(80, 200, 180, 80, corner_radius=10, rotate=-12,
             fill_color=ColorName.KHAKI, stroke_color=ColorName.CHOCOLATE,
             stroke_width=2)

    # 4) 虚线圆角「徽章」+ 混合模式
    badge = pen.rect(320, 200, 200, 80, corner_radius=40,
                     fill_color=ColorName.GOLD, stroke_color="white",
                     stroke_width=3, stroke_style=DashStyle.DASH_DOT,
                     blend_mode="multiply")
    pen.text(420, 248, "BADGE", font_size=22, fill_color=ColorName.MAROON,
             h_align="middle")
    print("徽章 bbox:", tuple(round(v, 1) for v in badge.bbox()))

    # 5) 正方形（rect 的便捷封装）
    pen.square(90, 320, 50, fill_color=ColorName.TEAL, stroke_color="none")

    # 6) 用「外框 + 内框 + EVENODD」画一个镂空方环（不用布尔运算）
    outer = [(300, 310), (420, 310), (420, 390), (300, 390)]
    inner = [(325, 330), (395, 330), (395, 370), (325, 370)]
    pen.polygon(outer + inner, fill_color=ColorName.STEELBLUE,
                fill_rule=FillRule.EVENODD, stroke_color="none")
    pen.text(480, 355, "|", font_size=10, fill_color=ColorName.WHITESMOKE)

    # 7) 局部更新：只改宽高/圆角
    r = pen.rect(470, 310, 100, 40, fill_color=ColorName.PLUM)
    r.update(width=120, corner_radius=12)
    print("更新后矩形宽高:", round(r.width, 1), round(r.height, 1))

    pen.finish()
```

---

## 同级模块

[base](base.zh.md) ｜ [circle](circle.zh.md) ｜ [clippath](clippath.zh.md) ｜ [ellipse](ellipse.zh.md) ｜ [group](group.zh.md) ｜ [image](image.zh.md) ｜ [line](line.zh.md) ｜ [link](link.zh.md) ｜ [marker](marker.zh.md) ｜ [mask](mask.zh.md) ｜ [path](path.zh.md) ｜ [pattern](pattern.zh.md) ｜ [polygon](polygon.zh.md) ｜ [polyline](polyline.zh.md) ｜ [svggroup](svggroup.zh.md) ｜ [svgimage](svgimage.zh.md) ｜ [symbol](symbol.zh.md) ｜ [text](text.zh.md) ｜ [textpath](textpath.zh.md) ｜ [use](use.zh.md)
