<!-- 本文件由 tools/gen_docs.py 从源码自动生成，请勿手改。
     要改内容请改同目录的 definitions.py 里的文档字符串，然后重跑生成器。 -->

# definitions.py

**简体中文** ｜ [English](definitions.en.md) ｜ [← 返回 README](../README.md)

定义集（Definitions）—— 颜色、字体、纸张、枚举常量

本模块是英文版的常量定义中心，对应中文版《神笔码靓》的 `定义集.py`。

**设计约定（枚举 + 字符串双写法）**：凡是「可选值就那么几个」的参数，
都提供枚举；同时一律兼容直接写字符串。目的是既方便又不易写错：

| 参数 | 推荐写法（枚举） | 兼容写法（字符串） |
|---|---|---|
| 颜色 | `ColorName.RED` | `"red" / "#ff0000" / "红"` |
| 字体 | `Font.SIMHEI` | `"SimHei" / "simhei.ttf"` |
| 填充规则 | `FillRule.EVENODD` | `"evenodd"` |
| 虚线样式 | `DashStyle.DASHED` | `"8 4"` |
| 端头/拐角 | `StrokeCap.ROUND` | `"round"` |
| 线条连接 | `StrokeJoin.ROUND` | `"round"` |
| 水平/垂直对齐 | `TextHAlign.MIDDLE` | `"middle"` |
| 字重 | `FontWeight.BOLD` | `"bold" / 700` |
| 文字修饰 | `TextDecoration.UNDERLINE` | `"underline"` |
| 混合模式 | `BlendMode.MULTIPLY` | `"multiply"` |
| 箭头样式 | `ArrowStyle.SOLID` | `"solid"` |
| 定位点样式 | `PointStyle.CROSS` | `"cross"` |
| 渐变坐标系 | `CoordUnits.USER_SPACE` | `"userSpaceOnUse"` |
| 导出引擎 | `PDFMode.CHROME` | `1` |


所有接口内部都会用 `value_of()` 归一化，所以两种写法可以混用。

使用示例

```python
from malight import Color, ColorName, Font, FillRule, DashStyle

pen.text(100, 100, "标题", font=Font.SIMHEI, weight=FontWeight.BOLD)
pen.polygon(pts, fill_color=ColorName.TEAL, fill_rule=FillRule.EVENODD)
pen.line((0, 0), (100, 0), stroke_style=DashStyle.DASHED)

print(Color.RED)                 # "#ff0000"（138 种具名颜色 + 2 个无色常量）
print(ColorName.RED)             # "red"（常用色枚举）
print(Color.RGB(30, 144, 255))   # "#1e90ff"
print(Color.darken("#D75D72"))   # 颜色加深
w, h = PaperSize.A4_portrait()   # A4 像素尺寸
```


---

## 类与方法

### 函数

| 函数 | 说明 |
|---|---|
| `value_of` | 把枚举成员转换为其值；非枚举原样返回（「枚举 + 字符串」双写法的内部统一入口）。 |

### `Color`

颜色常量与颜色运算工具（对应中文版 `颜色` 类）。

| 方法 | 说明 |
|---|---|
| `RGB(R=None, G=None, B=None)` | 构造 RGB 颜色，返回 #rrggbb 字符串。 |
| `hex_of(name)` | 把颜色名（中/英文）转换为十六进制值；无法识别时原样返回。 |
| `english_name(chinese_name)` | 查询中文颜色名对应的英文颜色名。 |
| `random()` | 返回一个随机十六进制颜色。 |
| `invert(color)` | 反色（每个分量取 255 差值）。 |
| `darken(color, amount=0.08)` | 颜色加深。 |
| `lighten(color, amount=0.08)` | 颜色变浅。 |
| `add_colors(colors, keep_alpha=False)` | 多个颜色按 RGB 分量依次相加（上限 255）。 |
| `add(color1, color2, keep_alpha=False)` | 两种颜色 RGB 分量相加（各分量上限 255）。 |
| `blend(base, top, alpha=0.5)` | 按透明度叠加两种颜色（模拟顶层颜色以 alpha 叠在底层之上）。 |
| `blend_many(colors, alphas=None)` | 按顺序叠加多个颜色。 |
| `to_rgb(color)` | 把任意颜色转换为 (r, g, b) 元组（分量 0-255）。 |
| `rgb_to_hex(rgb)` | 把 (r, g, b) 元组转换为 #rrggbb 字符串。 |

### `ColorName`

常用颜色枚举（对应「枚举 + 字符串」双写法中的枚举部分）。

| 方法 | 说明 |
|---|---|
| `of(value)` | 把颜色字符串 / 枚举名转换为枚举成员。 |
| `hex_of(color)` | 取颜色的十六进制值（中/英文名均可）。 |
| `list_names()` | 列出全部枚举名。 |

### `ChalkColor`

粉笔色（黑板上柔和的粉笔质感色板，对应中文版 `粉笔色`）。

| 方法 | 说明 |
|---|---|
| `list()` | 返回全部粉笔色列表。 |

### `ColorScheme`

预置配色方案（对应中文版 `颜色方案`），每项为颜色列表。

| 方法 | 说明 |
|---|---|
| `cyclic(index, scheme)` | 循环取色：索引超出方案长度时从头再取。 |

### `VectorEffect`

元素矢量效果（SVG vector-effect，对应中文版 `元素矢量效果`）。

### `ScreenResolution`

常用屏幕分辨率（对应中文版 `屏幕分辨率`），返回 (宽, 高)。

| 方法 | 说明 |
|---|---|
| `PHONE()` | 常见手机分辨率 1080x2376。 |
| `FULL_HD()` | 全高清 1920x1080。 |
| `HD()` | 高清 1280x720。 |
| `HUAWEI_ENJOY_60X()` | 华为畅享 60X：1080x2376。 |
| `HUAWEI_NOVA12()` | 华为 Nova12：1084x2412。 |
| `HUAWEI_MATE50()` | 华为 Mate50：1224x2700。 |

### `PaperSize`

纸张尺寸（像素，对应中文版 `纸张大小`）。

| 方法 | 说明 |
|---|---|
| `A3_landscape(sheets=1)` | A3 横向（420mm x 297mm）。sheets 为连续纸张页数（高度方向拼接）。 |
| `A3_portrait(sheets=1)` | A3 纵向。 |
| `A4_landscape(sheets=1)` | A4 横向（297mm x 210mm）。 |
| `A4_portrait(sheets=1)` | A4 纵向。 |
| `A5_landscape(sheets=1)` | A5 横向。 |
| `A5_portrait(sheets=1)` | A5 纵向。 |

### `PaperOrientation`

页面方向（对应中文版 `纸张方向`）。

### `TextHAlign`

文字水平对齐（SVG text-anchor，对应中文版 `文字水平基线对齐`）。

### `TextVAlign`

文字垂直对齐（SVG alignment-baseline / dominant-baseline， 对应中文版 `文字垂直基线对齐`）。

### `ArrowStyle`

箭头样式（对应中文版 `箭头样式`）。

### `StrokeJoin`

描边拐角连接样式（SVG stroke-linejoin，对应中文版 `描边线连接样式`）。

### `StrokeCap`

描边线端样式（SVG stroke-linecap，对应中文版 `描边线端样式`）。

### `ImageRendering`

图像渲染设置（SVG image-rendering，对应中文版 `图像渲染设置`）。

### `PointStyle`

调试定位点样式（对应中文版 `定位点类型`）。

### `GridRepeatType`

网格重复排布类型（对应中文版 `网格重复类型`）。

### `CoordUnits`

空间坐标系单位（SVG gradientUnits/clipPathUnits 等，对应中文版 `空间坐标系单位`）。

### `PaperSettings`

页面打印设置（对应中文版 `纸张设置`），用于 finish() 时的 @page 样式。

### `PDFMode`

PDF 导出方式（对应中文版 `PDF生成方式`）。

### `PNGMode`

PNG 导出方式（对应中文版 `PNG生成方式`）。

### `FontEmbed`

字体嵌入方式（英文版新增，对应 `pen.set_embed(fonts=...)`）。

### `ImageEmbed`

图片嵌入方式（英文版新增，对应 `pen.set_embed(images=...)`）。

### `DOCXMode`

DOCX 导出方式（对应中文版 `DOCX生成方式`）。

### `FillRule`

填充规则（SVG fill-rule，对应中文版 `填充规则`）。

### `DashStyle`

虚线样式预设（SVG stroke-dasharray，英文版新增）。

### `PaintOrder`

绘制顺序（SVG paint-order，英文版新增）。

### `BlendMode`

混合模式（CSS mix-blend-mode，英文版新增）。

### `FontWeight`

字重（SVG font-weight，英文版新增）。

### `TextDecoration`

文字修饰线（SVG text-decoration，英文版新增）。

### `LengthAdjust`

文字宽度调整方式（SVG lengthAdjust，配合 text_length 使用）。

### `AspectRatio`

图片缩放保持比例方式（SVG preserveAspectRatio，英文版新增）。

| 方法 | 说明 |
|---|---|
| `custom(align_x='Mid', align_y='Mid', meet=True)` | 自定义对齐方式，如 "xMinYMin meet"。 |

### `SpreadMethod`

渐变扩散方式（SVG spreadMethod，英文版新增）。

---

## 同级模块

[compat](compat.zh.md) ｜ [ext](ext.zh.md) ｜ [fonts](fonts.zh.md) ｜ [gradients](gradients.zh.md) ｜ [i18n](i18n.zh.md) ｜ [page](page.zh.md) ｜ [svg_backend](svg_backend.zh.md) ｜ [tools](tools.zh.md)
