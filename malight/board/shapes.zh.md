<!-- 本文件由 tools/gen_docs.py 从源码自动生成，请勿手改。
     要改内容请改同目录的 shapes.py 里的文档字符串，然后重跑生成器。 -->

# shapes.py

**简体中文** ｜ [English](shapes.en.md) ｜ [← 返回 README](../../README.md)

基本图形（SVG 元素命名：circle/ellipse/rect/...）。

本文件只包含 ShapeMixin 一个类（Mixin），由 board/__init__.py 组合进 MagicPen。

---

## 类与方法

### `ShapeMixin`

ShapeMixin —— 基本图形（SVG 元素命名：circle/ellipse/rect/...）（方法名与 SVG 元素名对应，旧名保留为别名）。

| 方法 | 说明 |
|---|---|
| `circle(x, y, radius, fill_color=Color.TRANS…, stroke_color=Color.BLACK, stroke_width=1.0, stroke_style=None, stroke_cap=None, stroke_join=None, fill_rule=None, dash_offset=None, blend_mode=None, filter=None, opacity=1.0, id_=None, **extra)` | 画圆（对应中文版 `画圆`）。 |
| `ellipse(x, y, radius, fill_color=Color.TRANS…, stroke_color=Color.BLACK, stroke_width=1.0, stroke_style=None, stroke_cap=None, stroke_join=None, fill_rule=None, dash_offset=None, blend_mode=None, filter=None, opacity=1.0, rotate=None, id_=None, **extra)` | 画椭圆（对应中文版 `画椭圆`）。 |
| `rect(x, y, width, height, corner_radius=None, fill_color=Color.TRANS…, stroke_color=Color.BLACK, stroke_width=1, stroke_style=None, stroke_cap=None, stroke_join=None, fill_rule=None, dash_offset=None, blend_mode=None, filter=None, opacity=1.0, rotate=None, id_=None, **extra)` | 画矩形（对应中文版 `画矩形`）。 |
| `square(x, y, side, **kw)` | 画正方形（对应中文版 `画正方形`）。 |
| `line(start, end, stroke_color=Color.BLACK, fill_color=Color.TRANS…, stroke_width=1, stroke_style=None, stroke_cap=None, stroke_join=None, dash_offset=None, blend_mode=None, filter=None, opacity=1.0, id_=None, **extra)` | 画一条线段（对应中文版 `画线`/`画直线`）。 |
| `cross(x, y, width=5, height=5, color=Color.BLACK, stroke_width=1, id_=None, **kw)` | 画十字标记（对应中文版 `十字`），常用于标注关键点。 |
| `polyline(points, fill_color=Color.TRANS…, stroke_color=Color.BLACK, stroke_width=1, stroke_style=None, stroke_cap=None, stroke_join=None, dash_offset=None, blend_mode=None, filter=None, opacity=1.0, id_=None, **extra)` | 画折线元素（顶点直连，对应中文版 `画折线`）。 |
| `polygon(points, fill_color=Color.TRANS…, stroke_color=Color.BLACK, stroke_width=1, stroke_style=None, stroke_cap=None, stroke_join=None, fill_rule=None, dash_offset=None, blend_mode=None, filter=None, opacity=1.0, id_=None, **extra)` | 画多边形（自动闭合，对应中文版 `画多边形`）。 |
| `regular_polygon(x, y, radius, n, stroke_color=Color.BLACK, fill_color=Color.TRANS…, stroke_width=1, opacity=1.0, id_=None, **extra)` | 画正 N 边形（对应中文版 `画正N边形`）。 |
| `triangle(x, y, radius, **kw)` | 画正三角形（对应中文版 `画正三边形`）。 |
| `pentagon(x, y, radius, **kw)` | 画正五边形（对应中文版 `画正五边形`）。 |
| `hexagon(x, y, radius, **kw)` | 画正六边形（对应中文版 `画正六边形`）。 |
| `star(x, y, radius, n=5, inner_ratio=None, stroke_color=Color.BLACK, fill_color=Color.TRANS…, stroke_width=1, opacity=1.0, id_=None, **extra)` | 画 N 角星（对应中文版 `画N角星`/`画五角星` 等）。 |
| `diamond(x, y, radius, stroke_color=Color.BLACK, fill_color=Color.TRANS…, stroke_width=1, id_=None, **extra)` | 画菱形（对应中文版 `画菱型`）。 |
| `heart(x, y, size, stroke_color=Color.BLACK, fill_color=Color.TRANS…, stroke_width=1, id_=None, **extra)` | 画爱心（对应中文版 `画爱心`）。 |

---

## 同级模块

[containers](containers.zh.md) ｜ [core](core.zh.md) ｜ [debug](debug.zh.md) ｜ [effects](effects.zh.md) ｜ [filters](filters.zh.md) ｜ [fx](fx.zh.md) ｜ [gradients_mixin](gradients_mixin.zh.md) ｜ [images](images.zh.md) ｜ [layout](layout.zh.md) ｜ [paths](paths.zh.md) ｜ [repeat](repeat.zh.md) ｜ [style](style.zh.md) ｜ [text_board](text_board.zh.md)
