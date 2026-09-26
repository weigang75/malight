<!-- 本文件由 tools/gen_docs.py 从源码自动生成，请勿手改。
     要改内容请改同目录的 clippath.py 里的文档字符串，然后重跑生成器。 -->

# clippath.py

**简体中文** ｜ [English](clippath.en.md) ｜ [← 返回 README](../../README.md)

ClipPathElement 元素（每类一文件，含中文注释与示例）。

---

## 类与方法

### `ClipPathElement`

裁剪元素（`<clipPath>`，对应中文版 `裁剪元素`）。

| 方法 | 说明 |
|---|---|
| `apply_to(targets)` | 把裁剪应用到目标元素（可为单个或列表）。 |
| `set_clip_shape(value)` | 设置 clip_shape（等价 `update(clip_shape=value)`）。 |
| `get_clip_shape()` | 读取 clip_shape 的当前属性值。 |
| `set_units(value)` | 设置 units（等价 `update(units=value)`）。 |
| `get_units()` | 读取 units 的当前属性值。 |
| `set_id_(value)` | 设置 id_（等价 `update(id_=value)`）。 |
| `get_id_()` | 读取 id_ 的当前属性值。 |

---

## 完整示例

在 PyCharm 里点绿色三角直接运行，或命令行：`python malight/elements/clippath.py`

```python
if __name__ == "__main__":
    import os

    from malight import Malight, ColorName, CoordUnits

    _out = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        "..", "..", "output"))
    pen = Malight(os.path.join(_out, "demo_clippath"), width=660, height=380)
    pen.set_background_color(ColorName.WHITESMOKE)

    pen.text(330, 40, "裁剪（clipPath）：只显示裁剪形状内部的内容",
             font_size=16, h_align="middle", fill_color=ColorName.DIMGRAY)

    # -----------------------------------------------------------------
    # 1) 圆形裁剪（一步到位）
    # -----------------------------------------------------------------
    big = pen.rect(40, 70, 190, 190, fill_color=ColorName.TOMATO)
    pen.clip_circle(135, 165, 90, targets=[big])
    pen.text(135, 285, "圆形裁剪", font_size=15, h_align="middle",
             fill_color=ColorName.MAROON)

    # -----------------------------------------------------------------
    # 2) 矩形裁剪
    # -----------------------------------------------------------------
    box = pen.rect(270, 70, 190, 190, fill_color=ColorName.STEELBLUE)
    pen.clip_rect(310, 115, 110, 100, targets=[box])
    pen.text(365, 285, "矩形裁剪", font_size=15, h_align="middle",
             fill_color=ColorName.NAVY)

    # -----------------------------------------------------------------
    # 3) 任意形状裁剪：用 PathElement 当裁剪路径（异形头像 / 波浪边）
    # -----------------------------------------------------------------
    wave = pen.path(fill_color="none")
    wave.move_to(500, 115)
    wave.cubic_to((520, 60), (560, 60), (580, 115))
    wave.line_to(580, 250)
    wave.line_to(500, 250)
    wave.close()
    target = pen.rect(480, 70, 130, 190, fill_color=ColorName.GOLD)
    cp = pen.clipPath(wave, targets=[target],
                      units=CoordUnits.USER_SPACE)
    print("裁剪元素 id:", cp.node.attribs.get("id"))
    pen.text(545, 285, "异形裁剪", font_size=15, h_align="middle",
             fill_color=ColorName.CHOCOLATE)

    # -----------------------------------------------------------------
    # 4) 一个裁剪区域可以作用到多个目标（做成「统一取景框」）
    # -----------------------------------------------------------------
    tile_a = pen.rect(60, 315, 120, 55, fill_color=ColorName.TEAL)
    tile_b = pen.rect(200, 315, 120, 55, fill_color=ColorName.PLUM)
    pen.clip_circle(100, 342, 30, targets=[tile_a])
    pen.clip_circle(240, 342, 30, targets=[tile_b])
    print("提示：裁剪形状本身会被移入 <defs>，不会显示在画布上")

    pen.finish()
```

---

## 同级模块

[base](base.zh.md) ｜ [circle](circle.zh.md) ｜ [ellipse](ellipse.zh.md) ｜ [group](group.zh.md) ｜ [image](image.zh.md) ｜ [line](line.zh.md) ｜ [link](link.zh.md) ｜ [marker](marker.zh.md) ｜ [mask](mask.zh.md) ｜ [path](path.zh.md) ｜ [pattern](pattern.zh.md) ｜ [polygon](polygon.zh.md) ｜ [polyline](polyline.zh.md) ｜ [rect](rect.zh.md) ｜ [svggroup](svggroup.zh.md) ｜ [svgimage](svgimage.zh.md) ｜ [symbol](symbol.zh.md) ｜ [text](text.zh.md) ｜ [textpath](textpath.zh.md) ｜ [topath](topath.zh.md) ｜ [use](use.zh.md)
