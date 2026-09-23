<!-- 本文件由 tools/gen_docs.py 从源码自动生成，请勿手改。
     要改内容请改同目录的 text.py 里的文档字符串，然后重跑生成器。 -->

# text.py

**简体中文** ｜ [English](text.en.md) ｜ [← 返回 README](../../README.md)

TextElement 元素（每类一文件，含中文注释与示例）。

![文字样式一览](../assets/images/text_preview.png)

---

## 类与方法

### `TextElement`

文字元素（对应中文版 `文字元素`）。

| 方法 | 说明 |
|---|---|
| `set_text(value)` | 改文字内容。 |
| `get_text()` | 读取当前文字内容。 |
| `set_font(font)` | 改字体（枚举 / 字体名 / 字体文件都行）。 |
| `get_font()` | 读取字体族的当前属性值。 |
| `set_font_size(size)` | 改字号。 |
| `get_font_size()` | 读取字号的当前属性值。 |
| `set_bold(flag=True)` | 加粗开关。 |
| `get_bold()` | 读取字重的当前属性值（如 "bold" / "700"）。 |
| `set_italic(flag=True)` | 斜体开关。 |
| `get_italic()` | 读取字体样式的当前属性值。 |
| `set_underline(flag=True)` | 下划线开关。 |
| `get_underline()` | 读取文字修饰线的当前属性值。 |
| `set_weight(weight)` | 改字重（FontWeight 枚举或 "700"）。 |
| `get_weight()` | 读取字重的当前属性值。 |
| `set_decoration(decoration)` | 改文字修饰线（下划线/删除线）。 |
| `get_decoration()` | 读取文字修饰线的当前属性值。 |
| `set_letter_spacing(spacing)` | 改字间距。 |
| `get_letter_spacing()` | 读取字间距的当前属性值。 |
| `set_word_spacing(spacing)` | 改词间距（西文排版用）。 |
| `get_word_spacing()` | 读取词间距的当前属性值。 |
| `set_h_align(align)` | 改水平对齐（TextHAlign 或 "middle"）。 |
| `get_h_align()` | 读取水平对齐的当前属性值（text-anchor）。 |
| `set_v_align(align)` | 改垂直对齐（TextVAlign 或 "middle"）。 |
| `get_v_align()` | 读取垂直对齐的当前属性值。 |
| `set_char_rotate(angles)` | 改逐字旋转角度（角度列表）。 |
| `get_char_rotate()` | 读取逐字旋转的当前属性值。 |
| `set_text_length(length, adjust=None)` | 改文字总宽压缩；给了 adjust 就一并设置调整方式。 |
| `get_text_length()` | 读取文字总宽的当前属性值（textLength）。 |
| `set_length_adjust(adjust)` | 改宽度调整方式（配合 text_length）。 |
| `get_length_adjust()` | 读取宽度调整方式的当前属性值。 |
| `bbox()` | 估算包围盒（按字号 x 字数近似，精确宽度需渲染后测量）。 |

---

## 完整示例

在 PyCharm 里点绿色三角直接运行，或命令行：`python malight/elements/text.py`

```python
if __name__ == "__main__":
    import os

    from malight import (Malight, ColorName, Font, FontWeight, TextDecoration,
                         TextHAlign, TextVAlign, LengthAdjust, PaintOrder)

    _out = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        "..", "..", "output"))
    pen = Malight(os.path.join(_out, "demo_text"), width=680, height=420)
    pen.set_background_color(ColorName.WHITESMOKE)

    # -----------------------------------------------------------------
    # 字体有三种写法，可以混用
    # -----------------------------------------------------------------
    # 1) 字体枚举（推荐：有补全、拼错立刻报错，不会静默变默认字体）
    pen.text(340, 55, "① 字体枚举 Font.SIMHEI", font=Font.SIMHEI, font_size=26,
             h_align=TextHAlign.MIDDLE, fill_color=ColorName.NAVY)

    # 2) 字体名字符串（任何已安装字体都行）
    pen.text(340, 100, "② 字体名字符串 Microsoft YaHei",
             font="Microsoft YaHei", font_size=22, h_align="middle",
             fill_color=ColorName.STEELBLUE)

    # 3) 字体文件路径（自动 base64 内嵌，换电脑也不掉字体）
    from malight.fonts import find_font_file
    kai = find_font_file(Font.KAITI)
    if kai:
        pen.text(340, 145, "③ 字体文件内嵌（楷体）", font=kai, font_size=22,
                 h_align="middle", fill_color=ColorName.CHOCOLATE)
    else:
        pen.text(340, 145, "③ 未找到楷体文件，跳过", font_size=18,
                 h_align="middle", fill_color=ColorName.DIMGRAY)

    # -----------------------------------------------------------------
    # 字重 / 斜体 / 修饰线（全部有枚举）
    # -----------------------------------------------------------------
    pen.text(340, 195, "字重 W900 + 斜体", font=Font.ARIAL,
             weight=FontWeight.W900, italic=True, font_size=24,
             h_align="middle")
    pen.text(340, 235, "下划线 underline", font_size=20, h_align="middle",
             decoration=TextDecoration.UNDERLINE, fill_color=ColorName.TEAL)
    pen.text(340, 270, "删除线 line-through", font_size=20, h_align="middle",
             decoration=TextDecoration.LINE_THROUGH,
             fill_color=ColorName.CRIMSON)

    # -----------------------------------------------------------------
    # 描边空心字 / 字间距 / 词间距
    # -----------------------------------------------------------------
    pen.text(190, 340, "描边空心字", font=Font.MS_YAHEI, font_size=42,
             fill_color="none", stroke_color=ColorName.ORANGERED,
             stroke_width=1.5, letter_spacing=8, h_align="middle")

    # word_spacing：词间距（英文排版常用）
    pen.text(520, 340, "word spacing", font=Font.ARIAL, font_size=22,
             word_spacing=10, h_align="middle", fill_color=ColorName.INDIGO)

    # -----------------------------------------------------------------
    # 文字按指定宽度铺满（textLength）+ 垂直对齐
    # -----------------------------------------------------------------
    # -----------------------------------------------------------------
    # 先描边后填充 + 创建后逐项再设置（set_* 与参数名两种写法都支持）
    # -----------------------------------------------------------------
    word = pen.text(340, 385, "111111", font_size=20,
                    h_align="middle", v_align=TextVAlign.MIDDLE,
                    fill_color=ColorName.CHOCOLATE)
    word.set_paint_order(PaintOrder.STROKE)   # set_ 风格：链式逐项改
    word.set_stroke_color(ColorName.ORANGERED).set_stroke_width(3)
    # 参数名风格：无参读值、带参改值（可链式）
    word.text_length(460).length_adjust(
        LengthAdjust.SPACING_AND_GLYPHS).font_size(24)
    print("font-size =", word.font_size(),
          "| stroke =", word.stroke_color())

    # -----------------------------------------------------------------
    # 逐字旋转（做弧形/波浪标题的简易替代）
    # -----------------------------------------------------------------
    pen.text(340, 415, "逐字旋转", font_size=24, h_align="middle",
             char_rotate=[-14, -7, 0, 7, 14], fill_color=ColorName.SEAGREEN)

    # -----------------------------------------------------------------
    # 局部更新：只改字号与颜色，文字内容与位置不变
    # -----------------------------------------------------------------
    t = pen.text(40, 55, "局部更新演示", font_size=16)
    t.update(font_size=20, fill_color=ColorName.CRIMSON, bold=True)
    print("文字包围盒(估算):", tuple(round(v, 1) for v in t.bbox()))
    print("当前 font-size:", t.node.attribs.get("font-size"),
          "| text:", t.node.text)

    pen.finish()
```

---

## 同级模块

[base](base.zh.md) ｜ [circle](circle.zh.md) ｜ [clippath](clippath.zh.md) ｜ [ellipse](ellipse.zh.md) ｜ [group](group.zh.md) ｜ [image](image.zh.md) ｜ [line](line.zh.md) ｜ [link](link.zh.md) ｜ [marker](marker.zh.md) ｜ [mask](mask.zh.md) ｜ [path](path.zh.md) ｜ [pattern](pattern.zh.md) ｜ [polygon](polygon.zh.md) ｜ [polyline](polyline.zh.md) ｜ [rect](rect.zh.md) ｜ [svgimage](svgimage.zh.md) ｜ [symbol](symbol.zh.md) ｜ [textpath](textpath.zh.md) ｜ [use](use.zh.md)
