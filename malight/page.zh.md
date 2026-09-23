<!-- 本文件由 tools/gen_docs.py 从源码自动生成，请勿手改。
     要改内容请改同目录的 page.py 里的文档字符串，然后重跑生成器。 -->

# page.py

**简体中文** ｜ [English](page.en.md) ｜ [← 返回 README](../README.md)

页面设置（page）—— 打印与 PDF 的纸张、页边距、缩放

**只对 Chrome 引擎生效**：纸张（`@page`）与缩放（`zoom`）是浏览器排版
能力，cairosvg 引擎没有这个概念。所以 `PageSetup` 只作用于
`export_pdf_chrome`（以及绘图板 `export_pdf(engine=PDFMode.CHROME)`）；
PNG 是屏幕截图，没有纸张概念，输出尺寸恒为「画布 x scale」。
如果传了页面设置却选了 cairosvg 引擎，导出会**当场报错**而不是静默忽略。

**Chrome engine only**: paper size (`@page`) and zoom are browser layout
features that cairosvg cannot honour. `PageSetup` therefore applies to
`export_pdf_chrome` (and `export_pdf(engine=PDFMode.CHROME)`) only. PNG
is a screen screenshot with no notion of paper: its size is always canvas x
scale. Passing page settings to the cairosvg engine raises instead of
silently doing nothing.

示例 / Example

```python
from malight import PageSetup

# 1) 一次性设置在画板上，之后每次导出都用
pen.page = PageSetup("A4", margin=24)
pen.export_pdf()

# 2) 也可以只在某一次导出时给
pen.export_pdf(page=PageSetup("A4 landscape"))
page = PageSetup("A4", margin=24)          # 铺到 A4，四边留 24px
pen.export_pdf(page=page)                  # 内容等比缩放并居中留边
```


---

## 类与方法

### 函数

| 函数 | 说明 |
|---|---|
| `paper_css` | 把纸张规格解析成 `(CSS 尺寸串, 宽px, 高px)`。 |

### `PageSetup`

页面设置：纸张 / 页边距 / 内容缩放（对应中文版 `页面设置`）。

| 方法 | 说明 |
|---|---|
| `resolve(svg_w, svg_h)` | 算出 `(纸张尺寸串, 纸张宽px, 纸张高px, 内容缩放)`。 |
| `print_css(svg_w, svg_h)` | 生成 `@media print` 里那段缩放与页边距样式（空串 = 不需要）。 |

---

## 完整示例

在 PyCharm 里点绿色三角直接运行，或命令行：`python malight/page.py`

```python
if __name__ == "__main__":
    # 直接运行本文件：看各纸张解析尺寸（不依赖 Chrome）
    for _spec in ("A4", "A4 landscape", "A3", "LETTER", (100, 50)):
        _css, _w, _h = paper_css(_spec)
        print("%-16s -> %-14s %8.1f x %8.1f px" % (str(_spec), _css, _w, _h))
    _page = PageSetup("A4", margin=24)
    # 画布 800x600 铺到 A4
    print("A4 fit 800x600:", _page.resolve(800, 600))
    print(_page.print_css(800, 600))
```

---

## 同级模块

[compat](compat.zh.md) ｜ [definitions](definitions.zh.md) ｜ [ext](ext.zh.md) ｜ [fonts](fonts.zh.md) ｜ [gradients](gradients.zh.md) ｜ [i18n](i18n.zh.md) ｜ [svg_backend](svg_backend.zh.md) ｜ [tools](tools.zh.md)
