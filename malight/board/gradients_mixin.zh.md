<!-- 本文件由 tools/gen_docs.py 从源码自动生成，请勿手改。
     要改内容请改同目录的 gradients_mixin.py 里的文档字符串，然后重跑生成器。 -->

# gradients_mixin.py

**简体中文** ｜ [English](gradients_mixin.en.md) ｜ [← 返回 README](../../README.md)

渐变（SVG `<linearGradient>`/`<radialGradient>` 及彩虹/黄金快捷）。

本文件只包含 GradientMixin 一个类（Mixin），由 board/__init__.py 组合进 MagicPen。

---

## 类与方法

### `GradientMixin`

GradientMixin —— 渐变（SVG `<linearGradient>`/`<radialGradient>` 及彩虹/黄金快捷）（方法名与 SVG 元素名对应，旧名保留为别名）。

| 方法 | 说明 |
|---|---|
| `linearGradient(start, end, start_color, end_color, stops=None, units=None, spread=None, id_=None)` | 创建线性渐变（对应中文版 `创建线性渐变色`）。 |
| `radialGradient(center, radius, start_color, end_color, stops=None, focal=None, units=None, spread=None, id_=None)` | 创建径向渐变（对应中文版 `创建径向渐变色`）。 |
| `rainbow_stops(colors=None)` | 生成彩虹七色渐变stops（对应中文版 `彩虹渐变点`）。 |
| `rainbow_linear_gradient(start=(0, 0), end=(1, 0), colors=None, id_=None)` | 创建彩虹线性渐变（对应中文版 `创建彩虹线性渐变色`）。 |
| `rainbow_radial_gradient(center=(0.5, 0.5), radius=0.5, colors=None, id_=None)` | 创建彩虹径向渐变（对应中文版 `创建彩虹径向渐变色`）。 |
| `gold_linear_gradient(start=(0, 0), end=(0, 1), id_=None)` | 创建黄金质感渐变（对应中文版 `创建黄金线性渐变色`）。 |

---

## 同级模块

[containers](containers.zh.md) ｜ [core](core.zh.md) ｜ [debug](debug.zh.md) ｜ [effects](effects.zh.md) ｜ [filters](filters.zh.md) ｜ [fx](fx.zh.md) ｜ [images](images.zh.md) ｜ [layout](layout.zh.md) ｜ [paths](paths.zh.md) ｜ [repeat](repeat.zh.md) ｜ [shapes](shapes.zh.md) ｜ [style](style.zh.md) ｜ [text_board](text_board.zh.md)
