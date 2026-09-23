<!-- 本文件由 tools/gen_docs.py 从源码自动生成，请勿手改。
     要改内容请改同目录的 layout.py 里的文档字符串，然后重跑生成器。 -->

# layout.py

**简体中文** ｜ [English](layout.en.md) ｜ [← 返回 README](../../README.md)

排列（水平/垂直/网格/环绕）。

本文件只包含 LayoutMixin 一个类（Mixin），由 board/__init__.py 组合进 MagicPen。

---

## 类与方法

### `LayoutMixin`

LayoutMixin —— 排列（水平/垂直/网格/环绕）（方法名与 SVG 元素名对应，旧名保留为别名）。

| 方法 | 说明 |
|---|---|
| `arrange_horizontal(elements, gap=10)` | 水平排列（对应中文版 `水平排列`）：按包围盒左右相接。 |
| `arrange_vertical(elements, gap=10)` | 垂直排列（对应中文版 `垂直排列`）。 |
| `arrange_grid_by_cols(elements, max_cols, col_gap=10, row_gap=10)` | 网格排列（按列数换行，对应中文版 `网格水平排列`）。 |
| `arrange_grid_by_rows(elements, max_rows, row_gap=10, col_gap=10)` | 网格排列（按行数换列，对应中文版 `网格垂直排列`）。 |
| `arrange_circle(elements, center=None, angle_gap=None, clockwise=True, rotate_with=True)` | 环绕排列（对应中文版 `环绕排列`）：元素沿圆周均匀分布。 |

---

## 同级模块

[containers](containers.zh.md) ｜ [core](core.zh.md) ｜ [debug](debug.zh.md) ｜ [effects](effects.zh.md) ｜ [filters](filters.zh.md) ｜ [fx](fx.zh.md) ｜ [gradients_mixin](gradients_mixin.zh.md) ｜ [images](images.zh.md) ｜ [paths](paths.zh.md) ｜ [repeat](repeat.zh.md) ｜ [shapes](shapes.zh.md) ｜ [style](style.zh.md) ｜ [text_board](text_board.zh.md)
