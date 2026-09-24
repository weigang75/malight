<!-- 本文件由 tools/gen_docs.py 从源码自动生成，请勿手改。
     要改内容请改同目录的 mask.py 里的文档字符串，然后重跑生成器。 -->

# mask.py

**简体中文** ｜ [English](mask.en.md) ｜ [← 返回 README](../../README.md)

MaskElement 元素（每类一文件，含中文注释与示例）。

---

## 类与方法

### `MaskElement`

遮罩元素（`<mask>`，对应中文版 `遮罩元素`）：按亮度控制可见度。

| 方法 | 说明 |
|---|---|
| `apply_to(targets)` | 把遮罩应用到目标元素。 |
| `set_mask_shape(value)` | 设置 mask_shape（等价 `update(mask_shape=value)`）。 |
| `get_mask_shape()` | 读取 mask_shape 的当前属性值。 |
| `set_units(value)` | 设置 units（等价 `update(units=value)`）。 |
| `get_units()` | 读取 units 的当前属性值。 |
| `set_content_units(value)` | 设置 content_units（等价 `update(content_units=value)`）。 |
| `get_content_units()` | 读取 content_units 的当前属性值。 |
| `set_id_(value)` | 设置 id_（等价 `update(id_=value)`）。 |
| `get_id_()` | 读取 id_ 的当前属性值。 |

---

## 完整示例

在 PyCharm 里点绿色三角直接运行，或命令行：`python malight/elements/mask.py`

```python
if __name__ == "__main__":
    import os

    from malight import Malight, ColorName

    _out = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        "..", "..", "output"))
    pen = Malight(os.path.join(_out, "demo_mask"), width=660, height=380)
    pen.set_background_color(ColorName.WHITESMOKE)

    pen.text(330, 40, "遮罩（mask）：白色显示、黑色隐藏、灰色半透明",
             font_size=16, h_align="middle", fill_color=ColorName.DIMGRAY)

    # -----------------------------------------------------------------
    # 1) 黑白渐变当遮罩 → 图片「淡出」效果（做长图渐隐最常用）
    # -----------------------------------------------------------------
    photo = pen.rect(40, 80, 220, 170, fill_color=ColorName.STEELBLUE)
    fade = pen.linearGradient((0, 0), (1, 0), "white", "black")
    shade = pen.rect(40, 80, 220, 170, fill_color=fade.paint())
    m = pen.mask(shade, targets=[photo])
    print("遮罩元素 id:", m.node.attribs.get("id"))
    pen.text(150, 270, "渐变遮罩（右淡出）", font_size=15, h_align="middle",
             fill_color=ColorName.NAVY)

    # -----------------------------------------------------------------
    # 2) 圆形遮罩 → 「聚光灯 / 圆形取景」效果
    # -----------------------------------------------------------------
    bg = pen.rect(300, 80, 240, 170, fill_color=ColorName.CHOCOLATE)
    spot = pen.circle(420, 165, 70, fill_color="white")
    pen.mask(spot, targets=[bg])
    pen.text(420, 270, "圆形遮罩（聚光灯）", font_size=15, h_align="middle",
             fill_color=ColorName.MAROON)

    # -----------------------------------------------------------------
    # 3) 遮罩自己也可以是一个组（多块形状叠加成遮罩）
    #    白底 + 黑条纹 → 目标被「切成条纹」显示
    # -----------------------------------------------------------------
    strip = pen.rect(60, 300, 240, 50, fill_color=ColorName.TEAL)
    bars = pen.g()
    bars.append(pen.rect(60, 300, 240, 50, fill_color="white"))
    for i in range(6):
        bars.append(pen.line((70 + i * 40, 300), (70 + i * 40, 350),
                             stroke_color="black", stroke_width=6))
    pen.mask(bars, targets=[strip])
    pen.text(180, 370, "条纹遮罩（条纹显示）", font_size=14, h_align="middle",
             fill_color=ColorName.CHOCOLATE)

    # -----------------------------------------------------------------
    # 4) 遮罩也能作用于组（整组一起被遮）
    # -----------------------------------------------------------------
    g = pen.g()
    g.append(pen.circle(450, 325, 26, fill_color=ColorName.GOLD))
    g.append(pen.circle(500, 325, 26, fill_color=ColorName.PLUM))
    curtain = pen.rect(420, 295, 110, 60, fill_color="white")
    pen.mask(curtain, targets=[g])

    pen.finish()
```

---

## 同级模块

[base](base.zh.md) ｜ [circle](circle.zh.md) ｜ [clippath](clippath.zh.md) ｜ [ellipse](ellipse.zh.md) ｜ [group](group.zh.md) ｜ [image](image.zh.md) ｜ [line](line.zh.md) ｜ [link](link.zh.md) ｜ [marker](marker.zh.md) ｜ [path](path.zh.md) ｜ [pattern](pattern.zh.md) ｜ [polygon](polygon.zh.md) ｜ [polyline](polyline.zh.md) ｜ [rect](rect.zh.md) ｜ [svggroup](svggroup.zh.md) ｜ [svgimage](svgimage.zh.md) ｜ [symbol](symbol.zh.md) ｜ [text](text.zh.md) ｜ [textpath](textpath.zh.md) ｜ [use](use.zh.md)
