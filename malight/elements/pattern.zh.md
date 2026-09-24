<!-- 本文件由 tools/gen_docs.py 从源码自动生成，请勿手改。
     要改内容请改同目录的 pattern.py 里的文档字符串，然后重跑生成器。 -->

# pattern.py

**简体中文** ｜ [English](pattern.en.md) ｜ [← 返回 README](../../README.md)

PatternElement 元素（每类一文件，含中文注释与示例）。

---

## 类与方法

### `PatternElement`

图案元素（`<pattern>`，对应中文版 `元素图案`）：平铺填充纹理。

| 方法 | 说明 |
|---|---|
| `add_element(el)` | 把元素加入图案内容。 |
| `append(el)` | add_element 的别名。 |
| `set_x(value)` | 设置 x（等价 `update(x=value)`）。 |
| `get_x()` | 读取 x 的当前属性值。 |
| `set_y(value)` | 设置 y（等价 `update(y=value)`）。 |
| `get_y()` | 读取 y 的当前属性值。 |
| `set_width(value)` | 设置 width（等价 `update(width=value)`）。 |
| `get_width()` | 读取 width 的当前属性值。 |
| `set_height(value)` | 设置 height（等价 `update(height=value)`）。 |
| `get_height()` | 读取 height 的当前属性值。 |
| `set_id_(value)` | 设置 id_（等价 `update(id_=value)`）。 |
| `get_id_()` | 读取 id_ 的当前属性值。 |
| `set_units(value)` | 设置 units（等价 `update(units=value)`）。 |
| `get_units()` | 读取 units 的当前属性值。 |

---

## 完整示例

在 PyCharm 里点绿色三角直接运行，或命令行：`python malight/elements/pattern.py`

```python
if __name__ == "__main__":
    import os

    from malight import Malight, ColorName, CoordUnits

    _out = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        "..", "..", "output"))
    pen = Malight(os.path.join(_out, "demo_pattern"), width=660, height=380)
    pen.set_background_color(ColorName.WHITESMOKE)

    # -----------------------------------------------------------------
    # 1) 斜条纹图案（做背景 / 填充纹理）
    #    units 决定坐标基准：USER_SPACE（像素，最直观）
    # -----------------------------------------------------------------
    stripes = pen.pattern(0, 0, 20, 20, id_="stripes",
                          units=CoordUnits.USER_SPACE)
    stripes.append(pen.rect(0, 0, 20, 20, fill_color=ColorName.LIGHTYELLOW))
    stripes.append(pen.line((0, 20), (20, 0), stroke_color=ColorName.GOLD,
                            stroke_width=4))
    pen.rect(40, 60, 240, 190, fill_color="url(#stripes)",
             stroke_color=ColorName.CHOCOLATE)

    # -----------------------------------------------------------------
    # 2) 圆点图案（波点）
    # -----------------------------------------------------------------
    dots = pen.pattern(0, 0, 24, 24, id_="dots")
    dots.append(pen.rect(0, 0, 24, 24, fill_color="white"))
    dots.append(pen.circle(12, 12, 5, fill_color=ColorName.TOMATO,
                           stroke_color="none"))
    pen.circle(450, 155, 95, fill_color="url(#dots)",
               stroke_color=ColorName.CRIMSON, stroke_width=3)

    # -----------------------------------------------------------------
    # 3) 棋盘格图案
    # -----------------------------------------------------------------
    grid = pen.pattern(0, 0, 40, 40, id_="grid")
    grid.append(pen.rect(0, 0, 20, 20, fill_color=ColorName.SNOW))
    grid.append(pen.rect(20, 20, 20, 20, fill_color=ColorName.SNOW))
    grid.append(pen.rect(0, 20, 20, 20, fill_color=ColorName.STEELBLUE))
    grid.append(pen.rect(20, 0, 20, 20, fill_color=ColorName.STEELBLUE))
    pen.rect(320, 60, 300, 190, fill_color="url(#grid)",
             stroke_color=ColorName.NAVY)

    # -----------------------------------------------------------------
    # 4) 图案可以只作为某条描边/文字的填充，也可以叠加在渐变上
    # -----------------------------------------------------------------
    pen.text(60, 300, "带图案填充的文字", font_size=44,
             fill_color="url(#stripes)", stroke_color=ColorName.CHOCOLATE,
             stroke_width=1)
    pen.text(500, 300, "波点字", font_size=44, fill_color="url(#dots)",
             stroke_color=ColorName.CRIMSON, stroke_width=1)

    # 5) 局部更新：只改图案格子尺寸，内容元素不动
    small = pen.pattern(0, 0, 30, 30, id_="small_dots")
    small.append(pen.circle(15, 15, 4, fill_color=ColorName.SEAGREEN))
    small.update(width=60, height=60)
    print("图案 width/height:", small.node.attribs.get("width"),
          small.node.attribs.get("height"))
    pen.rect(60, 330, 540, 34, fill_color="url(#small_dots)")

    # 6) 提示：图案定义放在 <defs>，用 url(#id) 引用，不会直接显示
    print("图案元素都放在 <defs> 中，用 url(#id) 引用")
    pen.finish()
```

---

## 同级模块

[base](base.zh.md) ｜ [circle](circle.zh.md) ｜ [clippath](clippath.zh.md) ｜ [ellipse](ellipse.zh.md) ｜ [group](group.zh.md) ｜ [image](image.zh.md) ｜ [line](line.zh.md) ｜ [link](link.zh.md) ｜ [marker](marker.zh.md) ｜ [mask](mask.zh.md) ｜ [path](path.zh.md) ｜ [polygon](polygon.zh.md) ｜ [polyline](polyline.zh.md) ｜ [rect](rect.zh.md) ｜ [svggroup](svggroup.zh.md) ｜ [svgimage](svgimage.zh.md) ｜ [symbol](symbol.zh.md) ｜ [text](text.zh.md) ｜ [textpath](textpath.zh.md) ｜ [use](use.zh.md)
