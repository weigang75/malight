<!-- 本文件由 tools/gen_docs.py 从源码自动生成，请勿手改。
     要改内容请改同目录的 use.py 里的文档字符串，然后重跑生成器。 -->

# use.py

**简体中文** ｜ [English](use.en.md) ｜ [← 返回 README](../../README.md)

UseElement 元素（每类一文件，含中文注释与示例）。

---

## 类与方法

### `UseElement`

复用元素（`<use>`，对应中文版 `复用元素`）：引用模板/已定义图形。

| 方法 | 说明 |
|---|---|
| `set_href(value)` | 设置 href（等价 `update(href=value)`）。 |
| `get_href()` | 读取 href 的当前属性值。 |
| `set_x(value)` | 设置 x（等价 `update(x=value)`）。 |
| `get_x()` | 读取 x 的当前属性值。 |
| `set_y(value)` | 设置 y（等价 `update(y=value)`）。 |
| `get_y()` | 读取 y 的当前属性值。 |
| `set_width(value)` | 设置 width（等价 `update(width=value)`）。 |
| `get_width()` | 读取 width 的当前属性值。 |
| `set_height(value)` | 设置 height（等价 `update(height=value)`）。 |
| `get_height()` | 读取 height 的当前属性值。 |

---

## 完整示例

在 PyCharm 里点绿色三角直接运行，或命令行：`python malight/elements/use.py`

```python
if __name__ == "__main__":
    import os

    from malight import Malight, ColorName

    _out = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        "..", "..", "output"))
    pen = Malight(os.path.join(_out, "demo_use"), width=620, height=380)
    pen.set_background_color(ColorName.WHITESMOKE)

    # 先准备一个模板（也可以来自外部 SVG，见 import_svg_as_symbol）
    badge = pen.symbol(id_="badge", view_box="0 0 120 60")
    badge.append(pen.rect(0, 0, 120, 60, corner_radius=30,
                          fill_color=ColorName.STEELBLUE))
    badge.append(pen.text(60, 39, "NEW", font_size=26, fill_color="white",
                          h_align="middle"))

    # -----------------------------------------------------------------
    # 1) 最简复用：反复 <use> 同一个模板
    # -----------------------------------------------------------------
    pen.use("badge", x=40, y=40, width=150, height=75)
    pen.use("badge", x=220, y=40, width=150, height=75, opacity=0.85)
    pen.use("badge", x=400, y=40, width=150, height=75)

    # -----------------------------------------------------------------
    # 2) 只给 x / y：按模板原始尺寸放置 / 2) x
    # -----------------------------------------------------------------
    pen.use("badge", x=60, y=150)

    # -----------------------------------------------------------------
    # 3) 每个实例可单独变换、加滤镜、改透明度
    # -----------------------------------------------------------------
    u = pen.use("badge", x=200, y=150, width=200, height=100,
                filter=pen.fx.shadow(6, 8, 6))
    u.update(opacity=0.95)
    u.rotate(-6, cx=300, cy=200)
    print("复用元素引用:", u.node.attribs.get("href"))
    print("复用元素 bbox:", tuple(round(v, 1) for v in u.bbox()))

    # -----------------------------------------------------------------
    # 4) 多个实例可分别做动画（例如依次淡入上浮）
    # -----------------------------------------------------------------
    for i in range(3):
        item = pen.use("badge", x=70 + i * 165, y=290, width=140, height=70)
        item.animate_opacity(0, 1, dur=1.2, repeat_count=1, begin=i)
        item.animate_translate(offset=(0, -8), dur=1.2,
                               repeat_count="indefinite")

    # -----------------------------------------------------------------
    # 5) 局部更新：只改尺寸 / 透明度，引用关系不变
    # -----------------------------------------------------------------
    small = pen.use("badge", x=480, y=290, width=90, height=45)
    small.update(width=120, height=60, opacity=0.6)
    print("更新后 bbox:", tuple(round(v, 1) for v in small.bbox()))

    pen.finish()
```

---

## 同级模块

[base](base.zh.md) ｜ [circle](circle.zh.md) ｜ [clippath](clippath.zh.md) ｜ [ellipse](ellipse.zh.md) ｜ [group](group.zh.md) ｜ [image](image.zh.md) ｜ [line](line.zh.md) ｜ [link](link.zh.md) ｜ [marker](marker.zh.md) ｜ [mask](mask.zh.md) ｜ [path](path.zh.md) ｜ [pattern](pattern.zh.md) ｜ [polygon](polygon.zh.md) ｜ [polyline](polyline.zh.md) ｜ [rect](rect.zh.md) ｜ [svggroup](svggroup.zh.md) ｜ [svgimage](svgimage.zh.md) ｜ [symbol](symbol.zh.md) ｜ [text](text.zh.md) ｜ [textpath](textpath.zh.md)
