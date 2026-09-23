<!-- 本文件由 tools/gen_docs.py 从源码自动生成，请勿手改。
     要改内容请改同目录的 gradients.py 里的文档字符串，然后重跑生成器。 -->

# gradients.py

**简体中文** ｜ [English](gradients.en.md) ｜ [← 返回 README](../README.md)

渐变色（gradients）—— 线性/径向渐变定义

对应中文版《神笔码靓》的 `元素库/渐变色.py`。
渐变定义放入 `<defs>`，返回值可作为填充/描边颜色直接使用。

示例

```python
from malight import MagicPen
pen = MagicPen("demo_gradient", width=500, height=300)

# 线性渐变：从左上到右下，红到蓝
grad = pen.linearGradient((0, 0), (1, 1), "red", "blue")

# 径向渐变：金色太阳
sun = pen.radialGradient((250, 120), 90, "white", "orange")

pen.rect(50, 180, 400, 80, fill_color=grad)
pen.circle(250, 120, 90, fill_color=sun)
pen.finish()
```


---

## 类与方法

### `_GradientBase`

渐变基类：管理色标（stop）与坐标单位（内部使用）。

| 方法 | 说明 |
|---|---|
| `paint()` | 返回 paint 引用串，可直接作为 fill_color/stroke_color 使用。 |
| `add_stop(offset, color, opacity=1.0)` | 添加渐变色标（对应中文版 `增加渐变中间点` 的单点操作）。 |
| `gradient_transform(transform_str)` | 设置渐变的 gradientTransform（原始变换串）。 |
| `id`（属性） | 渐变 id（引用时用 `url(#id)`）。 |

### `LinearGradient`

线性渐变（对应中文版 `线性渐变色`）。

### `RadialGradient`

径向渐变（对应中文版 `径向渐变色`）。

---

## 同级模块

[compat](compat.zh.md) ｜ [definitions](definitions.zh.md) ｜ [ext](ext.zh.md) ｜ [fonts](fonts.zh.md) ｜ [i18n](i18n.zh.md) ｜ [page](page.zh.md) ｜ [svg_backend](svg_backend.zh.md) ｜ [tools](tools.zh.md)
