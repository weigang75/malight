<!-- 本文件由 tools/gen_docs.py 从源码自动生成，请勿手改。
     要改内容请改同目录的 core.py 里的文档字符串，然后重跑生成器。 -->

# core.py

**简体中文** ｜ [English](core.en.md) ｜ [← 返回 README](../../README.md)

BoardCore —— MagicPen 核心。

画布初始化/元素注册/页面配置/背景/生命周期钩子/finish 保存与
PNG、PDF、DOCX 导出。绘图方法分布在同目录各 Mixin 文件中。

本文件只包含 BoardCore 一个类（Mixin），由 board/__init__.py 组合进 MagicPen。

---

## 类与方法

### `BoardCore`

BoardCore —— MagicPen 核心类（Mixin）。

| 方法 | 说明 |
|---|---|
| `get_element(id_)` | 按 id 获取元素（对应中文版 `获取元素`）。 |
| `page_setup(settings)` | 页面打印设置（对应中文版 `页面设置`）。 |
| `set_config(name, data)` | 保存配置项（对应中文版 `增加配置项`）。 |
| `get_config(name)` | 读取配置项（对应中文版 `获取配置项`）。 |
| `use_toolkit(*names)` | 挂载扩展工具包（英文版新增，配合 malight.ext 扩展机制）。 |
| `resize(width=None, height=None)` | 修改画布大小（对应中文版 `修改绘图板大小`）。 |
| `set_embed(fonts=None, images=None)` | 设置「资源嵌入方式」（英文版新增）：字体与图片要不要写进 SVG。 |
| `set_background_color(color)` | 设置画布背景色（对应中文版 `设置背景色`）。 |
| `add_background_rect(fill_color, opacity=1.0, id_=None, **kw)` | 添加背景矩形（对应中文版 `矩形背景`，与 set_background_color 等价， 但可控制透明度并返回元素）。 |
| `add_js(code)` | 添加 JavaScript 代码（对应中文版 `增加JS代码`），嵌入 `<script>`。 |
| `write_app_info(x, y, font_size=14, fill_color=Color.BLACK, id_=None)` | 写软件签名信息（对应中文版 `写软件信息`）。 |
| `author_seal(x=None, y=None, color='#c8102e', name='MagicPen', id_=None)` | 作者印章（对应中文版 `作者印章`）：圆形红印 + 名字。 |
| `before_create()` | 创作前钩子（对应中文版 `创作前执行`），子类可覆写。 |
| `on_create()` | 创作主钩子（对应中文版 `创作`），子类可覆写：把绘图代码写在这里。 |
| `after_create()` | 创作后钩子（对应中文版 `完成前执行`），子类可覆写。 |
| `rename_file(filename)` | 保存前修改文件名钩子（对应中文版 `修改文件名`），返回新文件名或 None。 |
| `finish()` | 完成并保存 SVG（对应中文版 `完成`）。 |
| `svg_editor(path=None, file=None, background=True, stroke_color='#e63946', stroke_width=3, fill_color='none', grid=20, title=None)` | 生成「SVG 编辑器」专用 HTML：调路径 + 取点定位二合一（对应中文版 `获取坐标点.html` 的加强版）。 |
| `export_png(scale=3, out_file=None, mode=PNGMode.AUTO)` | 导出 PNG（对应中文版 `生成PNG`），需 finish() 先保存。 |
| `export_pdf(out_file=None, engine=PDFMode.AUTO, page=None)` | 导出 PDF（对应中文版 `生成PDF`），需 finish() 先保存。 |
| `export_docx(out_file=None)` | 导出 DOCX（对应中文版 `生成DOCX`，需 pdf2docx）。 |

---

## 同级模块

[containers](containers.zh.md) ｜ [debug](debug.zh.md) ｜ [effects](effects.zh.md) ｜ [filters](filters.zh.md) ｜ [fx](fx.zh.md) ｜ [gradients_mixin](gradients_mixin.zh.md) ｜ [images](images.zh.md) ｜ [layout](layout.zh.md) ｜ [paths](paths.zh.md) ｜ [repeat](repeat.zh.md) ｜ [shapes](shapes.zh.md) ｜ [style](style.zh.md) ｜ [text_board](text_board.zh.md)
