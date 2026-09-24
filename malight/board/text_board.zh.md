<!-- 本文件由 tools/gen_docs.py 从源码自动生成，请勿手改。
     要改内容请改同目录的 text_board.py 里的文档字符串，然后重跑生成器。 -->

# text_board.py

**简体中文** ｜ [English](text_board.en.md) ｜ [← 返回 README](../../README.md)

文字（SVG `<text>` / `<textPath>` / 文字转路径）。

本文件只包含 TextMixin 一个类（Mixin），由 board/__init__.py 组合进 MagicPen。

---

## 类与方法

### `TextMixin`

TextMixin —— 文字（SVG `<text>` / `<textPath>` / 文字转路径）（方法名与 SVG 元素名对应，旧名保留为别名）。

| 方法 | 说明 |
|---|---|
| `text(x, y, text, font=SystemFont.…, font_size=16, fill_color=Color.BLACK, stroke_color=None, stroke_width=None, bold=False, italic=False, underline=False, weight=None, decoration=None, letter_spacing=None, word_spacing=None, h_align=None, v_align=None, char_rotate=None, text_length=None, length_adjust=None, paint_order=None, blend_mode=None, filter=None, opacity=None, id_=None, **extra)` | 写文字（对应中文版 `写字`）。 |
| `textPath(points, text, start_offset='0%', font=SystemFont.…, font_size=16, fill_color=Color.BLACK, letter_spacing=None, weight=None, decoration=None, h_align=None, blend_mode=None, filter=None, id_=None, **extra)` | 文字沿路径排列（对应中文版 `路径文字`）。 |
| `text_to_path(x, y, text, font=SystemFont.…, font_size=16, fill_color=Color.BLACK, letter_spacing=0, id_=None, **kw)` | 文字转矢量路径（对应中文版 `文字转路径`，需要 fontTools 库）。 |

---

## 同级模块

[containers](containers.zh.md) ｜ [core](core.zh.md) ｜ [debug](debug.zh.md) ｜ [effects](effects.zh.md) ｜ [filters](filters.zh.md) ｜ [fx](fx.zh.md) ｜ [gradients_mixin](gradients_mixin.zh.md) ｜ [images](images.zh.md) ｜ [layout](layout.zh.md) ｜ [paths](paths.zh.md) ｜ [repeat](repeat.zh.md) ｜ [shapes](shapes.zh.md) ｜ [style](style.zh.md)
