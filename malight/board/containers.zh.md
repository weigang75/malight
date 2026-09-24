<!-- 本文件由 tools/gen_docs.py 从源码自动生成，请勿手改。
     要改内容请改同目录的 containers.py 里的文档字符串，然后重跑生成器。 -->

# containers.py

**简体中文** ｜ [English](containers.en.md) ｜ [← 返回 README](../../README.md)

容器元素（g/symbol/use/pattern/marker/a）。

本文件只包含 ContainerMixin 一个类（Mixin），由 board/__init__.py 组合进 MagicPen。

---

## 类与方法

### `ContainerMixin`

ContainerMixin —— 容器元素（g/symbol/use/pattern/marker/a）（方法名与 SVG 元素名对应，旧名保留为别名）。

| 方法 | 说明 |
|---|---|
| `g(class_name=None, style_str=None, opacity=None, blend_mode=None, filter=None, id_=None, **kw)` | 创建组元素（对应中文版 `创建组合`）。 |
| `symbol(id_=None, view_box=None, **kw)` | 创建模板（`<symbol>`，对应中文版 `创建模板`）。 |
| `use(template_id, x=None, y=None, width=None, height=None, **kw)` | 实例化模板（`<use>`，对应中文版 `神笔模板`）。 |
| `pattern(x, y, width, height, id_=None, **kw)` | 创建平铺图案（对应中文版 `创建图案`）。 |
| `copy(el, x=None, y=None, opacity=1.0, id_=None)` | 复制元素（对应中文版 `复制元素`），可指定偏移。 |
| `a(el, url, tooltip=None, description=None, id_=None)` | 给元素加超链接（对应中文版 `创建链接`）。 |
| `marker(id_=None, ref_x=0, ref_y=0, width=10, height=10, orient='auto', marker_units=None, **kw)` | 创建线端标记（`<marker>`，对应中文版 `创建标记`）。 |

---

## 同级模块

[core](core.zh.md) ｜ [debug](debug.zh.md) ｜ [effects](effects.zh.md) ｜ [filters](filters.zh.md) ｜ [fx](fx.zh.md) ｜ [gradients_mixin](gradients_mixin.zh.md) ｜ [images](images.zh.md) ｜ [layout](layout.zh.md) ｜ [paths](paths.zh.md) ｜ [repeat](repeat.zh.md) ｜ [shapes](shapes.zh.md) ｜ [style](style.zh.md) ｜ [text_board](text_board.zh.md)
