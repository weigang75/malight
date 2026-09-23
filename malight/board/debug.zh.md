<!-- 本文件由 tools/gen_docs.py 从源码自动生成，请勿手改。
     要改内容请改同目录的 debug.py 里的文档字符串，然后重跑生成器。 -->

# debug.py

**简体中文** ｜ [English](debug.en.md) ｜ [← 返回 README](../../README.md)

调试辅助（网格/图框/测距/关键点）。

本文件只包含 DebugMixin 一个类（Mixin），由 board/__init__.py 组合进 MagicPen。

---

## 类与方法

### `DebugMixin`

DebugMixin —— 调试辅助（网格/图框/测距/关键点）（方法名与 SVG 元素名对应，旧名保留为别名）。

| 方法 | 说明 |
|---|---|
| `measure(p1, p2, color=None, font_size=16, bg_color=None, line_width=3, decimals=2, id_=None)` | 两点间测距标注（对应中文版 `测距`，调试用）。 |
| `grid(spacing=20, color='#b0c4de', opacity=0.6, id_=None)` | 显示网格（对应中文版 `显示网格`，调试用）。 |
| `frame(color='#ff6347', stroke_width=1)` | 显示画布边框（对应中文版 `显示图框`，调试用）。 |
| `mark_point(x, y, color=Color.RED, style=PointStyle.…, font_size=12, label=None, id_=None)` | 画定位点标记（对应中文版 `定位点`/`定位坐标`，调试用）。 |
| `key_points(points, color=Color.BLACK)` | 批量显示关键点坐标（对应中文版 `显示关键点`，调试用）。 |

---

## 同级模块

[containers](containers.zh.md) ｜ [core](core.zh.md) ｜ [effects](effects.zh.md) ｜ [filters](filters.zh.md) ｜ [fx](fx.zh.md) ｜ [gradients_mixin](gradients_mixin.zh.md) ｜ [images](images.zh.md) ｜ [layout](layout.zh.md) ｜ [paths](paths.zh.md) ｜ [repeat](repeat.zh.md) ｜ [shapes](shapes.zh.md) ｜ [style](style.zh.md) ｜ [text_board](text_board.zh.md)
