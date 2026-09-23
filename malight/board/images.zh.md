<!-- 本文件由 tools/gen_docs.py 从源码自动生成，请勿手改。
     要改内容请改同目录的 images.py 里的文档字符串，然后重跑生成器。 -->

# images.py

**简体中文** ｜ [English](images.en.md) ｜ [← 返回 README](../../README.md)

图像（`<image>` 贴图与 SVG 导入）。

本文件只包含 ImageMixin 一个类（Mixin），由 board/__init__.py 组合进 MagicPen。

---

## 类与方法

### `ImageMixin`

ImageMixin —— 图像（`<image>` 贴图与 SVG 导入）（方法名与 SVG 元素名对应，旧名保留为别名）。

| 方法 | 说明 |
|---|---|
| `image(image_file, x=0, y=0, width=None, height=None, opacity=1.0, rendering=None, aspect=None, external=False, blend_mode=None, filter=None, id_=None, **extra)` | 贴位图（对应中文版 `贴图`）。本地文件自动 base64 内嵌。 |
| `paste_svg(svg_file, x=0, y=0, width=None, height=None, opacity=None, blend_mode=None, filter=None, id_=None)` | 贴 SVG 文件（对应中文版 `SVG贴图`）。 |
| `import_svg_as_group(svg_file, x=0, y=0, scale=None)` | 把 SVG 文件内容解析为可编辑组（对应中文版 `导入SVG为组`）。 |
| `import_svg_as_symbol(svg_file, id_=None)` | 把 SVG 文件注册为模板，用 pen.template(id) 复用 （对应中文版 `导入SVG为模板`）。 |

---

## 同级模块

[containers](containers.zh.md) ｜ [core](core.zh.md) ｜ [debug](debug.zh.md) ｜ [effects](effects.zh.md) ｜ [filters](filters.zh.md) ｜ [fx](fx.zh.md) ｜ [gradients_mixin](gradients_mixin.zh.md) ｜ [layout](layout.zh.md) ｜ [paths](paths.zh.md) ｜ [repeat](repeat.zh.md) ｜ [shapes](shapes.zh.md) ｜ [style](style.zh.md) ｜ [text_board](text_board.zh.md)
