<!-- 本文件由 tools/gen_docs.py 从源码自动生成，请勿手改。
     要改内容请改同目录的 textpath.py 里的文档字符串，然后重跑生成器。 -->

# textpath.py

**简体中文** ｜ [English](textpath.en.md) ｜ [← 返回 README](../../README.md)

TextPathElement 元素（每类一文件，含中文注释与示例）。

---

## 类与方法

### `TextPathElement`

路径文字元素（对应中文版 `路径文字元素`）：文字沿路径排列。

| 方法 | 说明 |
|---|---|
| `get_text()` | 读取当前文字内容（存在内部 `<textPath>` 上）。 |
| `get_start_offset()` | 读取 startOffset（默认 `"0%"`）。 |
| `get_path()` | 读取引导路径的 `d` 字符串（引导路径藏在 defs 里，由 id 引用）。 |
| `set_path(value)` | 设置 path（等价 `update(path=value)`）。 |
| `set_text(value)` | 设置 text（等价 `update(text=value)`）。 |
| `set_start_offset(value)` | 设置 start_offset（等价 `update(start_offset=value)`）。 |
| `set_font(value)` | 设置 font（等价 `update(font=value)`）。 |
| `get_font()` | 读取 font 的当前属性值。 |
| `set_font_size(value)` | 设置 font_size（等价 `update(font_size=value)`）。 |
| `get_font_size()` | 读取 font_size 的当前属性值。 |
| `set_weight(value)` | 设置 weight（等价 `update(weight=value)`）。 |
| `get_weight()` | 读取 weight 的当前属性值。 |
| `set_decoration(value)` | 设置 decoration（等价 `update(decoration=value)`）。 |
| `get_decoration()` | 读取 decoration 的当前属性值。 |
| `set_letter_spacing(value)` | 设置 letter_spacing（等价 `update(letter_spacing=value)`）。 |
| `get_letter_spacing()` | 读取 letter_spacing 的当前属性值。 |
| `set_h_align(value)` | 设置 h_align（等价 `update(h_align=value)`）。 |
| `get_h_align()` | 读取 h_align 的当前属性值。 |

---

## 完整示例

在 PyCharm 里点绿色三角直接运行，或命令行：`python malight/elements/textpath.py`

```python
if __name__ == "__main__":
    import os

    from malight import Malight, ColorName, Font, FontWeight

    _out = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        "..", "..", "output"))
    pen = Malight(os.path.join(_out, "demo_textpath"), width=660, height=380)
    pen.set_background_color(ColorName.WHITESMOKE)

    # 1) 文字沿「顶点折线」排列（最简单）
    pen.textPath([(60, 100), (200, 50), (340, 100), (480, 50)],
                 "沿折线排列的文字", font=Font.SIMHEI, font_size=24,
                 fill_color=ColorName.NAVY)

    # 2) 引导线也可以直接给 PathElement（曲线更顺滑）
    guide = pen.path(fill_color="none", stroke_color=ColorName.LIGHTGRAY,
                     stroke_width=1, stroke_style="4 4")
    guide.move_to(60, 210)
    guide.cubic_to((180, 110), (320, 310), (460, 210))
    pen.textPath(guide, "沿三次贝塞尔曲线流动的文字（力度顺着曲线走）",
                 font_size=20, fill_color=ColorName.CRIMSON,
                 weight=FontWeight.SEMI_BOLD)

    # 3) start_offset 控制文字起点（"0%" 起 / "50%" 居中）
    pen.textPath([(60, 300), (600, 300)], "start_offset=50% 从中间开始写",
                 start_offset="50%", font_size=19,
                 fill_color=ColorName.TEAL)

    # 4) 圆形路径上排文字（做印章 / 徽标）：
    #    先 move_to 定一个点，再 circle_to 画整圆（半径 = 两点距离）
    ring = pen.path(fill_color="none", stroke_color=ColorName.LIGHTGRAY,
                    stroke_width=1)
    ring.move_to(330, 260)
    ring.circle_to((330, 330))
    pen.textPath(ring, "· 沿圆环排列的文字 ·", font_size=16,
                 fill_color=ColorName.INDIGO)
    print("提示：引导路径自动放进 <defs>，本身不会显示在画布上")

    # 5) 局部更新：只改字号/字距，文字与引导线都保留
    tp = pen.textPath([(60, 360), (600, 360)], "局部更新演示", font_size=16)
    tp.update(font_size=22, letter_spacing=6, fill_color=ColorName.SEAGREEN)
    # 也可换文字或换路径（会自动重建内部引用，不会累积节点）
    tp.update(text="换一段文字")
    tp.update(path=[(60, 360), (330, 345), (600, 360)])
    print("textPath 子节点数:", len(tp.node.children),
          "| 文字:", tp.node.children[0].text if tp.node.children else None)

    pen.finish()
```

---

## 同级模块

[base](base.zh.md) ｜ [circle](circle.zh.md) ｜ [clippath](clippath.zh.md) ｜ [ellipse](ellipse.zh.md) ｜ [group](group.zh.md) ｜ [image](image.zh.md) ｜ [line](line.zh.md) ｜ [link](link.zh.md) ｜ [marker](marker.zh.md) ｜ [mask](mask.zh.md) ｜ [path](path.zh.md) ｜ [pattern](pattern.zh.md) ｜ [polygon](polygon.zh.md) ｜ [polyline](polyline.zh.md) ｜ [rect](rect.zh.md) ｜ [svggroup](svggroup.zh.md) ｜ [svgimage](svgimage.zh.md) ｜ [symbol](symbol.zh.md) ｜ [text](text.zh.md) ｜ [topath](topath.zh.md) ｜ [use](use.zh.md)
