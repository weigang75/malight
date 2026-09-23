<!-- 本文件由 tools/gen_docs.py 从源码自动生成，请勿手改。
     要改内容请改同目录的 style.py 里的文档字符串，然后重跑生成器。 -->

# style.py

**简体中文** ｜ [English](style.en.md) ｜ [← 返回 README](../../README.md)

样式表 API（pen.style.add_class(...)），SVG `<style>`。

本文件只包含 StyleAPI 一个类。

---

## 类与方法

### `StyleAPI`

样式子工具（pen.style），对应中文版 `样式工具集`： 管理 CSS 类、全局样式表与**字体文件内嵌**。

| 方法 | 说明 |
|---|---|
| `add_class(class_name, styles)` | 定义 CSS 类。 |
| `add_font_face(font_file, family=None)` | 把字体文件内嵌为 @font-face，返回可直接用于 font-family 的族名。 |
| `build_style_node()` | 生成 `<style>` 节点（finish 时调用，内部方法）。 |

---

## 同级模块

[containers](containers.zh.md) ｜ [core](core.zh.md) ｜ [debug](debug.zh.md) ｜ [effects](effects.zh.md) ｜ [filters](filters.zh.md) ｜ [fx](fx.zh.md) ｜ [gradients_mixin](gradients_mixin.zh.md) ｜ [images](images.zh.md) ｜ [layout](layout.zh.md) ｜ [paths](paths.zh.md) ｜ [repeat](repeat.zh.md) ｜ [shapes](shapes.zh.md) ｜ [text_board](text_board.zh.md)
