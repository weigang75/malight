<!-- 本文件由 tools/gen_docs.py 从源码自动生成，请勿手改。
     要改内容请改同目录的 repeat.py 里的文档字符串，然后重跑生成器。 -->

# repeat.py

**简体中文** ｜ [English](repeat.en.md) ｜ [← 返回 README](../../README.md)

重复（网格重复/环绕重复/线性重复）。

本文件只包含 RepeatMixin 一个类（Mixin），由 board/__init__.py 组合进 MagicPen。

---

## 类与方法

### `RepeatMixin`

RepeatMixin —— 重复（网格重复/环绕重复/线性重复）（方法名与 SVG 元素名对应，旧名保留为别名）。

| 方法 | 说明 |
|---|---|
| `repeat_around_circle(el, count, center=None, angle_gap=None, clockwise=True, rotate_with=True)` | 环绕重复（对应中文版 `环绕重复`）：一个元素复制 count 份绕圆分布。 |
| `repeat_grid(el, cols, col_gap, rows, row_gap, grid_type=GridRepeatT…)` | 网格重复（对应中文版 `网格重复`）。 |
| `repeat_horizontal(el, count, gap, align='center', fill_gaps=False)` | 水平重复（对应中文版 `水平方向重复`）。 |
| `repeat_vertical(el, count, gap, align='center', fill_gaps=False)` | 垂直重复（对应中文版 `垂直方向重复`）。示例见 repeat_horizontal。 |

---

## 同级模块

[containers](containers.zh.md) ｜ [core](core.zh.md) ｜ [debug](debug.zh.md) ｜ [effects](effects.zh.md) ｜ [filters](filters.zh.md) ｜ [fx](fx.zh.md) ｜ [gradients_mixin](gradients_mixin.zh.md) ｜ [images](images.zh.md) ｜ [layout](layout.zh.md) ｜ [paths](paths.zh.md) ｜ [shapes](shapes.zh.md) ｜ [style](style.zh.md) ｜ [text_board](text_board.zh.md)
