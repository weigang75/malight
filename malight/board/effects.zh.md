<!-- 本文件由 tools/gen_docs.py 从源码自动生成，请勿手改。
     要改内容请改同目录的 effects.py 里的文档字符串，然后重跑生成器。 -->

# effects.py

**简体中文** ｜ [English](effects.en.md) ｜ [← 返回 README](../../README.md)

裁剪与遮罩（SVG `<clipPath>` / `<mask>`）。

本文件只包含 ClipMaskMixin 一个类（Mixin），由 board/__init__.py 组合进 MagicPen。

---

## 类与方法

### `ClipMaskMixin`

ClipMaskMixin —— 裁剪与遮罩（SVG `<clipPath>` / `<mask>`）（方法名与 SVG 元素名对应，旧名保留为别名）。

| 方法 | 说明 |
|---|---|
| `clipPath(clip_shape, targets=None, units=None, id_=None)` | 用任意形状裁剪目标元素（对应中文版 `裁剪`）。 |
| `clip_circle(x, y, radius, targets=None, units=None, id_=None)` | 圆形裁剪（对应中文版 `圆形裁剪`）。 |
| `clip_rect(x, y, width, height, targets=None, units=None, id_=None)` | 矩形裁剪（对应中文版 `矩形裁剪`）。 |
| `mask(mask_shape, targets=None, units=None, content_units=None, id_=None)` | 遮罩（对应中文版 `遮罩`）：按遮罩亮度决定目标可见度。 |

---

## 同级模块

[containers](containers.zh.md) ｜ [core](core.zh.md) ｜ [debug](debug.zh.md) ｜ [filters](filters.zh.md) ｜ [fx](fx.zh.md) ｜ [gradients_mixin](gradients_mixin.zh.md) ｜ [images](images.zh.md) ｜ [layout](layout.zh.md) ｜ [paths](paths.zh.md) ｜ [repeat](repeat.zh.md) ｜ [shapes](shapes.zh.md) ｜ [style](style.zh.md) ｜ [text_board](text_board.zh.md)
