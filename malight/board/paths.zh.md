<!-- 本文件由 tools/gen_docs.py 从源码自动生成，请勿手改。
     要改内容请改同目录的 paths.py 里的文档字符串，然后重跑生成器。 -->

# paths.py

**简体中文** ｜ [English](paths.en.md) ｜ [← 返回 README](../../README.md)

路径与连线（path/polyline/表格/箭头/波浪线）。

本文件只包含 PathMixin 一个类（Mixin），由 board/__init__.py 组合进 MagicPen。

---

## 类与方法

### `PathMixin`

PathMixin —— 路径与连线（path/polyline/表格/箭头/波浪线）（方法名与 SVG 元素名对应，旧名保留为别名）。

| 方法 | 说明 |
|---|---|
| `path(fill_color=Color.TRANS…, stroke_color=Color.BLACK, stroke_width=1, stroke_style=None, stroke_cap=None, stroke_join=None, fill_rule=None, dash_offset=None, blend_mode=None, filter=None, opacity=1.0, id_=None, **extra)` | 开始一条路径（对应中文版 `路径`）。返回 PathElement， 之后调用 move_to/line_to/cubic_to/... 组合形状。 |
| `connect_points(points, stroke_color=Color.BLACK, fill_color=Color.TRANS…, stroke_width=1, close=False, opacity=1.0, stroke_style=None, id_=None, **extra)` | 把顶点列表连成折线路径（对应中文版 `连直线`/`连线`）。 |
| `connect_curve(points, stroke_color=Color.BLACK, fill_color=Color.TRANS…, stroke_width=1, close=False, opacity=1.0, id_=None, **extra)` | 把顶点列表连成光滑曲线（Catmull-Rom 样条， 对应中文版 `连曲线`）。 |
| `wave_line(start, end, amplitude, periods, stroke_color=Color.BLACK, stroke_width=1, id_=None, **extra)` | 画正弦波浪线（对应中文版 `画波浪线`）。 |
| `wavy_line(start, end, periods, amplitude_scale=1, stroke_color=Color.BLACK, stroke_width=1, id_=None, **extra)` | 画海浪线（对应中文版 `画海浪线`，波幅随距离衰减的正弦线）。 |
| `h_lines(x1, y1, x2, y2=None, count=2, stroke_color=Color.BLACK, stroke_width=1, id_=None, **extra)` | 画多条水平线（对应中文版 `画水平线`）：在 y1~y2 之间均布 count 条。 |
| `v_lines(y1, x1, y2, x2=None, count=2, stroke_color=Color.BLACK, stroke_width=1, id_=None, **extra)` | 画多条垂直线（对应中文版 `画垂直线`）：在 x1~x2 之间均布 count 条。 |
| `table(x, y, col_widths, row_heights, rows=1, cols=1, stroke_color=Color.BLACK, stroke_width=1, id_=None, **extra)` | 画表格（对应中文版 `画表格`）。 |
| `arrow_path(start, end, style=None, arrow_length=10, arrow_angle=30, shrink_line=True)` | 计算箭头信息（对应中文版 `获取箭头路径`）。 |
| `arrow_line(start, end, style=ArrowStyle.…, arrow_length=10, arrow_angle=25, fill_color=Color.TRANS…, stroke_color=Color.BLACK, stroke_width=1, id_=None, **extra)` | 画带箭头的线段（对应中文版 `箭头线`）。 |

---

## 同级模块

[containers](containers.zh.md) ｜ [core](core.zh.md) ｜ [debug](debug.zh.md) ｜ [effects](effects.zh.md) ｜ [filters](filters.zh.md) ｜ [fx](fx.zh.md) ｜ [gradients_mixin](gradients_mixin.zh.md) ｜ [images](images.zh.md) ｜ [layout](layout.zh.md) ｜ [repeat](repeat.zh.md) ｜ [shapes](shapes.zh.md) ｜ [style](style.zh.md) ｜ [text_board](text_board.zh.md)
