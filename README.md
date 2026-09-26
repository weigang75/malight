# MaLight —— 神笔码靓 · 英文版绘图工具包

**简体中文** ｜ [English](README.en.md)

「神笔码靓」的完整英文重制版。商品名与绘图板类名 **MaLight**，
包名 **malight = Ma(gic) + light**（Python 包名按惯例全小写，import 用）：
读音贴近「码靓」，含义「魔术之光」，比 magiclight 简短。

全英文 API + **全中文注释与示例**；**方法名与 SVG 元素名一一对应**
（`circle` / `rect` / `text` / `path` / `g` / `clipPath` / `linearGradient`...），
每个类一个 `.py` 文件。基于自研轻量 SVG 序列化后端，零第三方依赖即可绘图
（PNG/PDF 导出可选装 `cairosvg`，文字转路径可选装 `fontTools`、`svgpathtools`）。

```bash
pip install malight                 # 核心：零依赖
pip install malight[export]         # 追加 PNG / PDF 导出（cairosvg）
pip install malight[full]           # 全部可选能力
```

> **0.1.0（首发）**：包名 magicpen → **malight**；新增滤镜工厂 `pen.fx`（参考 PS/AI 常用滤镜，
> 支持链式叠加）；新增扩展机制 `malight.ext`。旧脚本 `import magicpen` 仍可用
> （包内自带兼容 shim），也可用 `python -m malight.compat 旧脚本.py 新脚本.py` 一键迁移。
>
> 同样在 0.1.0：全面「枚举 + 字符串」双写法（字体 / 颜色 / 选项值，防打字错）；
> 新增路径辅助包 `malight.pathkit`（看结构、拖锚点、拖调整点、加点删点、点位存档）；
> 每个类文件都带可直接运行的完整示例；导出会打印**全路径**方便复制；
> 新增运行时多语言 `malight.i18n`（默认英文，一行切中文）；
> 每个模块旁生成同目录双语文档 `xxx.zh.md` / `xxx.en.md`（ISO 639-1 语言码），
> **文档跟着代码走**；源码注释与文档字符串改为**摘要级双语**；
> 英文页**不出现中文**（回归会拦住），示例代码按语言各取一半。
> 元素支持**创建后再设置**：`el.set_font_size(36)`、`el.font_size(36)`
> （无参读值、带参改值、可链式，参数名与创建时一致，`get_font_size()` 读回）；
> 新增 `paint_order=PaintOrder.STROKE` 先描边（空心字必备）与 `fx_engrave()` 雕刻滤镜；
> 新增 `PageSetup` 页面设置（`pen.export_pdf(page=PageSetup("A4", margin=24))`，
> **仅 Chrome 引擎生效**，PNG 是屏幕截图没有纸张概念）；
> 滤镜 / 文字样式等模块文档直接嵌**效果预览图**（`tools/gen_previews.py` 生成）。
>
> **0.2.0（当前版本）**：新增元素模板 `el.to_template()` + `clone()`（原地转
> `<symbol>` 模板、`<use>` 盖章复用）；**资源嵌入**——字体默认自动子集化
> （只打包画面实际用到的字），支持整份内嵌 / 本地外链，图片可内嵌或外链；
> 新增 `pen.svg_image()` 贴 SVG（矢量、可改文本与颜色）；
> 新增 `import_svg_as_group` 导入组（可位移 / 旋转 / 缩放 / 加滤镜）；
> 新增带颜色的控制台消息辅助（`malight.tools` 的 `print_red` / `print_green` 等）。

## 快速上手

```python
from malight import Malight, Color

pen = Malight("hello", width=800, height=600)
pen.set_background_color("#f8f9fa")
pen.circle(200, 150, 80, fill_color=Color.RGB(30, 144, 255),   # <circle>
           stroke_color="navy", stroke_width=3)
pen.rect(300, 60, 160, 110, corner_radius=12, fill_color="gold")
pen.text(400, 50, "你好 malight", font_size=32, bold=True)
pen.circle(600, 300, 70, fill_color="#e63946",
           filter=pen.fx.shadow(6, 8, 6))          # 一行加滤镜
pen.finish()          # 保存 SVG
pen.export_png()      # 可选：导出 PNG（需 cairosvg；滤镜需浏览器查看）
```

`Malight` 与 `MagicPen` 是同一个类的两个名字，写哪个都一样。
深入用法见 [board/core.zh.md](malight/board/core.zh.md)。

## 方法命名 = SVG 元素名

| Malight 方法 | SVG 元素 | 说明 |
|---|---|---|
| `pen.circle(x, y, r)` | `<circle>` | 圆 |
| `pen.ellipse(x, y, (rx,ry), rotate=)` | `<ellipse>` | 椭圆（含旋转） |
| `pen.rect(x, y, w, h)` | `<rect>` | 矩形 |
| `pen.line(p1, p2)` | `<line>` | 线段 |
| `pen.polyline(pts)` / `pen.polygon(pts)` | `<polyline>` / `<polygon>` | 折线/多边形 |
| `pen.text(x, y, s)` | `<text>` | 文字 |
| `pen.textPath(pts, s)` | `<textPath>` | 沿路径文字 |
| `pen.path(...)` | `<path>` | 路径（贝塞尔/圆弧/海龟绘图/布尔运算） |
| `pen.image(file, x, y)` | `<image>` | 位图贴图（base64 内嵌） |
| `pen.svg_image(file, x, y)` | `<image>` | 贴 SVG（矢量、可改文本与颜色，见下） |
| `pen.g()` | `<g>` | 组 |
| `pen.symbol(id)` + `pen.use(id, x, y)` | `<symbol>` + `<use>` | 模板与复用 |
| `pen.pattern(...)` | `<pattern>` | 图案填充 |
| `pen.marker(...)` | `<marker>` | 箭头/端点标记 |
| `pen.clipPath(shape, targets)` | `<clipPath>` | 裁剪（别名 `pen.clip`） |
| `pen.mask(shape, targets)` | `<mask>` | 遮罩 |
| `pen.a(el, url)` | `<a>` | 超链接 |
| `pen.linearGradient(...)` / `pen.radialGradient(...)` | `<linearGradient>` / `<radialGradient>` | 渐变 |

旧版长名（`draw_circle`、`write_text`、`create_linear_gradient`...）全部保留为别名，老脚本不用改。

## 枚举 + 字符串双写法（防打字错）

字体的名字、颜色的名字、只有几个取值的选项——**都用枚举**。枚举是 `str` 的子类，
`f"{Font.SIMHEI}"` 直接得到 `"SimHei"`，也能和字符串相等比较，所以「用枚举」和
「用字符串」完全等价，写哪种都行。

```python
from malight import (Malight, Font, Color, ColorName, FontWeight,
                     StrokeCap, FillRule)

pen = Malight("demo")

# 字体：三种写法都对 —— 枚举 / 字体名 / 字体文件
pen.text(50, 60, "枚举",    font=Font.SIMHEI)            # 枚举
pen.text(50, 100, "字体名", font="KaiTi")                # 字体名（字符串，任意已安装字体）
pen.text(50, 140, "粗体",   font=Font.MS_YAHEI, weight=FontWeight.BOLD)
# 字体文件（.ttf/.otf/.ttc）：默认只内嵌画面上实际用到的字（自动子集化），
# 换机器不掉字、体积也小；想整份内嵌或只引用路径见下面「字体与图片」一节
# pen.text(50, 180, "字体文件", font="C:/myfonts/MyFont.ttf")

# 颜色：枚举（72 个常用色）+ 字符串 + RGB 都行
pen.circle(200, 200, 60, fill_color=ColorName.TOMATO)
pen.circle(340, 200, 60, fill_color="tomato")             # 同上，等价
pen.circle(480, 200, 60, fill_color=Color.RGB(30, 144, 255))

# 只有几个取值的选项：用枚举就不会拼错
pen.path(fill_color="none", stroke_color="#333", stroke_width=6,
         stroke_cap=StrokeCap.ROUND,       # 线头：ROUND / BUTT / SQUARE
         stroke_join="round")              # 线拐角：也接受字符串
pen.rect(0, 0, 10, 10, fill_rule=FillRule.EVENODD)
pen.finish()
```

全部枚举（`Font` / `ColorName` / `BlendMode` / `FontWeight` / `DashStyle` /
`StrokeCap` / `StrokeJoin` / `FillRule` / `ArrowStyle` / `TextHAlign` / `PDFMode` …）、
每种枚举的成员与用途，见 [definitions.zh.md](malight/definitions.zh.md)；
字体解析与内嵌见 [fonts.zh.md](malight/fonts.zh.md)。

非枚举的通用取值也提供了小写常量：`YES` `NO` `ON` `OFF`。
写错时 IDE 会直接补全，不用再背字符串。

## 字体与图片：内嵌还是引用（`pen.set_embed`）

本地字体文件与本地图片默认都会**装进 SVG**（换电脑、发给别人都不掉），
但「装多少」可以选：

| 资源 | 默认 | 可选 |
|---|---|---|
| 字体（`font=字体文件`） | `FontEmbed.SUBSET` —— 只内嵌画面上**实际用到的字** | `EMBED` 整份内嵌 / `LINK` 只写本地路径 |
| 图片（`pen.image(...)`） | `ImageEmbed.EMBED` —— base64 内嵌 | `LINK` 只写相对路径 |

```python
from malight import Malight, FontEmbed, ImageEmbed, find_font_file

pen = Malight("poster", fonts="link", images="link")   # 全用引用：文件最小
pen.set_embed(fonts=FontEmbed.SUBSET)                  # 字体回到默认档

# 字体不用把文字写两遍：finish() 时库自己扫描画面上用到的字再子集化
pen.text(300, 100, "神笔码靓", font=find_font_file("小篆体"),
         font_size=40, h_align="middle")
pen.image("assets/bg.jpg", 0, 0, width=600, height=400)   # LINK 时写相对路径
```

实测（5.6 MB 的 `Android.ttf`，画面上只用到 12 个字）：

| 模式 | 生成的 SVG |
|---|---|
| `SUBSET`（默认） | **4.5 KB** |
| `EMBED` | 7.5 MB |
| `LINK` | 0.7 KB |

`LINK` 的代价：字体 / 图片文件必须留在原路径（同一台电脑、同一套目录结构），
只把 SVG 单文件复制走就会掉字 / 缺图。想「拷到哪都不怕」就用默认档。
图片 `LINK` 写的是**相对 SVG 所在目录**的路径，导出 PNG/PDF 时同样能读到。

完整演示见 `examples/demo_embed.py`；自带字体见
[assets/fonts/README.md](malight/assets/fonts/README.md)。

## 同一个 SVG 文件换色（`pen.svg_image`）

`pen.image()` 是把 SVG 当**位图**贴上去的，内容锁在 base64 里改不了；
`pen.svg_image()` 把源文本读进元素，于是可以直接改它 —— 换颜色、换文字：

```python
icon = pen.svg_image("assets/icons/mark.svg", x=40, y=40, width=60)
icon.svg_colors()                           # ['#ffffff', '#4dabf7']：文件里到底写的什么
icon.replace_color("#ffffff", "#ff0000")    # 白底换红（#fff / white / 白色 都认）
icon.replace_text("circle", "ellipse")      # 纯字符串替换

# 同一个文件、三种配色，各改各的互不影响
for i, color in enumerate(("#e63946", "#2a9d8f", "#1d3557")):
    pen.svg_image("assets/icons/mark.svg", x=40 + i * 90, y=200,
                  width=70).replace_color("white", color)
```

`replace_color` 按**颜色**换而不是按字符串换：`#ffffff` / `#FFF` /
`rgb(255,255,255)` / `white` / `白色` 算同一种颜色，一次全命中；`id="orange"`
这类同名标识不动。文件里没有那种颜色时会给出提示并列出实际用到的颜色，
而不是静默地「改了个寂寞」。

### 想拆开二次编辑（`import_svg_as_group` / `import_svg_as_symbol`）

换色只属于上面那个「自带一份文本」的 SVG 图元素。想把 SVG **拆开二次编辑**
（改属性、加动画、套滤镜）就用这两个入口，拿到的是**节点**：

```python
g = pen.import_svg_as_group("assets/icons/mark.svg", x=40, y=40, scale=0.5)
g.bbox()                              # 组该有的能力照常
g.translate(10, 0)
for node in g.walk():                 # 遍历所有节点，想改哪个属性改哪个
    print(node.tag, node.attribs.get("fill"))
```

它们**不带换色方法**——颜色是图形自己的属性，不是「组」这个容器的性质；要换色
就用工具函数就地改节点，连 `<style>` 块里 class 写的颜色也一起换：

```python
from malight.tools import replace_svg_node_color, svg_node_colors

svg_node_colors(g.node)               # ['#ffffff', '#4dabf7']
replace_svg_node_color(g.node, "white", "#ff0000")

tpl = pen.import_svg_as_symbol("assets/icons/mark.svg", id_="mark")
replace_svg_node_color(tpl.node, "white", "#ff0000")   # 改模板一处，<use> 实例全变
pen.use("mark", x=200, y=40, width=80, height=60)
```

想让每份副本各是一种配色，仍用 `pen.svg_image()` 逐个换 —— 模板的语义就是
「一处改、处处变」。

## 运行时可切中英文（默认英文）

库里的**报错、提示与导出信息默认输出英文**；想换中文一行代码即可，
不需要改任何业务代码：

```python
from malight import set_language, use_language, get_language, t

print(get_language())                # "en"（默认）

set_language("zh")                   # 全局切成中文
set_language("zh-TW")                # 也接受区域写法，未注册时回落到中文
set_language("auto")                 # 跟随系统语言

with use_language("en"):             # 只在某个代码块里切，出块自动还原
    pen.export_png()

print(t("export.ok", kind="SVG", tail="", path="a.svg", size="1 KB"))
```

- 环境变量 `MALIGHT_LANG=zh` 可在进程启动前设定，适合容器/CI；
- 查找顺序是「精确语言码 → 同语言族 → 英文兜底」，任何缺词都不会报错；
- 想追加自己的语言或覆盖词条：`malight.i18n.add_messages("ja", {...})`。

完整 API 与全部消息键见 [i18n.zh.md](malight/i18n.zh.md)。

## 文档跟着代码走

每个模块旁边就有它自己的双语文档，**改 API 时顺手改旁边那篇**：

| 文件 | 内容 |
|---|---|
| `malight/elements/path.py` | 源码（文档字符串即唯一内容源） |
| `malight/elements/path.zh.md` | 中文说明：摘要 + 类与方法表 + 完整可运行示例 |
| `malight/elements/path.en.md` | English page，页首一键切回中文 |

命名用 ISO 639-1 语言码：`xxx.zh.md` / `xxx.en.md`，与 `malight.i18n` 的
`Language.ZH`、`MALIGHT_LANG=zh` 一致。仓库根的 `README.md` 保留中文（GitHub / Gitee
只自动渲染这个名字），英文入口是 `README.en.md`。

文档是**自动生成**的，不是手写的：

```bash
python tools/gen_docs.py            # 从源码文档字符串刷新全部 46 个模块的双语文档
python tools/gen_docs.py --check    # CI 用：与源码不同步时退出码 1
python tools/gen_docs.py path       # 只刷新名字匹配的模块
```

所以文档不会和代码脱节；README 下面的模块索引也是同一个脚本重建的。

## 模块速查

<!-- DOCS-INDEX:START -->
### malight（顶层模块）

| 模块 / Module | 说明 / Description |
|---|---|
| [compat](malight/compat.zh.md) | 兼容迁移（compat）—— 中文 API → 英文 API 对照与迁移工具 |
| [definitions](malight/definitions.zh.md) | 定义集（Definitions）—— 颜色、字体、纸张、枚举常量 |
| [ext](malight/ext.zh.md) | ext —— malight 扩展机制（让第三方工具包无缝挂进绘图板）。 |
| [fonts](malight/fonts.zh.md) | 字体（fonts）—— 字体枚举 Font + 字体解析/查找/内嵌工具 |
| [gradients](malight/gradients.zh.md) | 渐变色（gradients）—— 线性/径向渐变定义 |
| [i18n](malight/i18n.zh.md) | 运行时多语言 |
| [page](malight/page.zh.md) | 页面设置（page）—— 打印与 PDF 的纸张、页边距、缩放 |
| [svg_backend](malight/svg_backend.zh.md) | SVG 轻量后端（svg_backend）—— 内部模块 |
| [tools](malight/tools.zh.md) | 工具集（tools）—— 图像/导出/几何/滤镜/字体辅助 |

### malight/board

| 模块 / Module | 说明 / Description |
|---|---|
| [containers](malight/board/containers.zh.md) | 容器元素（g/symbol/use/pattern/marker/a）。 |
| [core](malight/board/core.zh.md) | BoardCore —— MagicPen 核心。 |
| [debug](malight/board/debug.zh.md) | 调试辅助（网格/图框/测距/关键点）。 |
| [effects](malight/board/effects.zh.md) | 裁剪与遮罩（SVG `<clipPath>` / `<mask>`）。 |
| [filters](malight/board/filters.zh.md) | FilterAPI —— 滤镜工厂（pen.fx / pen.filter）。 |
| [fx](malight/board/fx.zh.md) | FilterChain —— 链式滤镜构建器（参考 Photoshop / Illustrator 常用滤镜）。 |
| [gradients_mixin](malight/board/gradients_mixin.zh.md) | 渐变（SVG `<linearGradient>`/`<radialGradient>` 及彩虹/黄金快捷）。 |
| [images](malight/board/images.zh.md) | 图像（`<image>` 贴图与 SVG 导入）。 |
| [layout](malight/board/layout.zh.md) | 排列（水平/垂直/网格/环绕）。 |
| [paths](malight/board/paths.zh.md) | 路径与连线（path/polyline/表格/箭头/波浪线）。 |
| [repeat](malight/board/repeat.zh.md) | 重复（网格重复/环绕重复/线性重复）。 |
| [shapes](malight/board/shapes.zh.md) | 基本图形（SVG 元素命名：circle/ellipse/rect/...）。 |
| [style](malight/board/style.zh.md) | 样式表 API（pen.style.add_class(...)），SVG `<style>`。 |
| [text_board](malight/board/text_board.zh.md) | 文字（SVG `<text>` / `<textPath>` / 文字转路径）。 |

### malight/elements

| 模块 / Module | 说明 / Description |
|---|---|
| [base](malight/elements/base.zh.md) | 元素基类与共享辅助函数（所有元素的公共能力）。 |
| [circle](malight/elements/circle.zh.md) | CircleElement 元素（每类一文件，含中文注释与示例）。 |
| [clippath](malight/elements/clippath.zh.md) | ClipPathElement 元素（每类一文件，含中文注释与示例）。 |
| [ellipse](malight/elements/ellipse.zh.md) | EllipseElement 元素（每类一文件，含中文注释与示例）。 |
| [group](malight/elements/group.zh.md) | GroupElement 元素（每类一文件，含中文注释与示例）。 |
| [image](malight/elements/image.zh.md) | ImageElement 元素（每类一文件，含中文注释与示例）。 |
| [line](malight/elements/line.zh.md) | LineElement 元素（每类一文件，含中文注释与示例）。 |
| [link](malight/elements/link.zh.md) | LinkElement 元素（每类一文件，含中文注释与示例）。 |
| [marker](malight/elements/marker.zh.md) | MarkerElement 元素（每类一文件，含中文注释与示例）。 |
| [mask](malight/elements/mask.zh.md) | MaskElement 元素（每类一文件，含中文注释与示例）。 |
| [path](malight/elements/path.zh.md) | PathElement 路径元素（对应中文版 路径元素）。 |
| [pattern](malight/elements/pattern.zh.md) | PatternElement 元素（每类一文件，含中文注释与示例）。 |
| [polygon](malight/elements/polygon.zh.md) | PolygonElement 元素（每类一文件，含中文注释与示例）。 |
| [polyline](malight/elements/polyline.zh.md) | PolylineElement 元素（每类一文件，含中文注释与示例）。 |
| [rect](malight/elements/rect.zh.md) | RectElement 元素（每类一文件，含中文注释与示例）。 |
| [svggroup](malight/elements/svggroup.zh.md) | SvgGroupElement 元素（每类一文件，含中文注释与示例）。 |
| [svgimage](malight/elements/svgimage.zh.md) | SVGImageElement 元素（每类一文件，含中文注释与示例）。 |
| [symbol](malight/elements/symbol.zh.md) | TemplateElement 元素（每类一文件，含中文注释与示例）。 |
| [text](malight/elements/text.zh.md) | TextElement 元素（每类一文件，含中文注释与示例）。 |
| [textpath](malight/elements/textpath.zh.md) | TextPathElement 元素（每类一文件，含中文注释与示例）。 |
| [topath](malight/elements/topath.zh.md) | 元素转 PathElement（topath）—— `Element.to_path_element()` 的实现层 |
| [use](malight/elements/use.zh.md) | UseElement 元素（每类一文件，含中文注释与示例）。 |

### malight/pathkit

| 模块 / Module | 说明 / Description |
|---|---|
| [editor](malight/pathkit/editor.zh.md) | 路径编辑器（pathkit.editor）—— PathEditor 类 |
| [htmleditor](malight/pathkit/htmleditor.zh.md) | 路径 UI 编辑器（pathkit.htmleditor）—— PathHTMLEditor 类 |
| [parser](malight/pathkit/parser.zh.md) | 路径坐标解析（pathkit.parser）—— SVG path d 串 <-> 结构化线段列表 |
| [point](malight/pathkit/point.zh.md) | 路径可调点（pathkit.point）—— PathPoint 类 |
| [segment](malight/pathkit/segment.zh.md) | 路径线段（pathkit.segment）—— PathSegment 类 |
<!-- DOCS-INDEX:END -->

## 主题深入

| 主题 | 一句话 | 详细文档 |
|---|---|---|
| 路径辅助 `pathkit` | 把路径变成**可以看的点**：看结构、拖锚点/调整点、加点删点、反转缩放、点位存档 | [pathkit/editor.md](malight/pathkit/editor.zh.md) ｜ [point.md](malight/pathkit/point.zh.md) ｜ [segment.md](malight/pathkit/segment.zh.md) |
| 滤镜 `pen.fx` | 参考 PS / AI 常用滤镜，链式叠加，只收录渲染稳定的效果 | [board/fx.md](malight/board/fx.zh.md) ｜ [board/filters.md](malight/board/filters.zh.md) |
| 扩展 `malight.ext` | 不改源码给绘图板加装工具包（图表包 / 图标包 / 特效包） | [ext.md](malight/ext.zh.md) |
| 导出 chrome / cairo | PNG、PDF 双引擎，导出后打印全路径 | [tools.md](malight/tools.zh.md) |
| 枚举与常量 | 颜色、字体、纸张、全部选项枚举 | [definitions.md](malight/definitions.zh.md) |
| 兼容与迁移 | 中文 API → 英文 API 对照表与一键迁移脚本 | [compat.md](malight/compat.zh.md) |
| 内部后端 | 自研轻量 SVG 元素树与序列化（一般无需直接使用） | [svg_backend.md](malight/svg_backend.zh.md) |

### 路径辅助 pathkit（看得见、拖得动）

`PathElement` 本身命令很多，写起来不直观。`malight.pathkit` 把路径变成**可以看的点**：
每条曲线有几个点、点在哪、拖完什么样，一目了然（就像钢笔工具）。

```python
from malight import Malight
from malight.pathkit import PathEditor

pen = Malight("path_demo", width=660, height=400)
p = pen.path(fill_color="none", stroke_color="#e63946", stroke_width=3)
p.move_to(60, 300)
p.cubic_to((120, 80), (260, 80), (320, 300))
p.quad_to((420, 120), (520, 300))

print(p.describe())                   # 1) 看结构：每段的起点 / 调整点 / 终点
ed = p.editor()                       # 2) 取编辑器（等价于 PathEditor(p)）
ed.anchors[1].move_to(200, 60)        #    拖锚点（即刻写回路径）
ed.controls[0].move_by(0, -30)        #    拖调整点
ed.insert_anchor(ed.curve_indices()[0], 0.5)   # 3) 曲线上加点（形状不变）
ed.scale_all(0.9, 0.9, cx=300, cy=200)
ed.show(labels=True)                  # 4) 可视化：方块=锚点、圆点=调整点
ed.save_json("points.json")           # 5) 存档：点位导出 → 外部算 → 读回
pen.finish()
```

`PathElement` 上还有一批便捷方法直接透传：`path.describe()` /
`path.anchor_points()` / `path.control_points()` / `path.move_anchor(i, x, y)` /
`path.move_control(seg, i, x, y)` / `path.show_points()` / `path.editor()`。

### 滤镜 pen.fx（参考 PS / AI 常用滤镜）

**8 种用法**（可叠加、可复用；图解见
[assets/images/filters_preview.png](malight/assets/images/filters_preview.png)，
左边代码右边结果）：

| # | 用法 | 写法 |
|---|---|---|
| 1 | 元素方法链式（`fx_*` 返回自身，可无限接） | `el.fx_inner_shadow(1, 1, 2, "#ffffff", 0.6).fx_emboss().fx_blur(1.5)` |
| 2 | 按名字叠加（等价 `el.fx_blur(3)`） | `el.fx("blur", 3)` |
| 3 | 追加任意 SVG 滤镜原语 | `el.fx("custom", "feBlend", mode="screen", in2="SourceGraphic")` |
| 4 | 取元素已有的链继续加 | `el.fx_chain().blur(2).saturate(1.4)` |
| 5 | 工厂一步到位（`filter=` 直接传） | `filter=pen.fx.shadow(6, 8, 6)` |
| 6 | 工厂建链再绑定（一条链可复用给多个元素） | `f = pen.fx.chain().blur(1).shadow(5, 5, 4)` → `a.set_filter(f)` / `f.apply(b)` |
| 7 | 叠加 / 替换 / 清除（`set_filter` 默认是叠加） | 多次 `set_filter` 叠加；`merge=False` 整条替换；`set_filter(None)` 清除 |
| 8 | 底层工具（tools.create_*_filter） | `fid = create_glow_filter(pen, 6)` + `extra={"filter": "url(#%s)" % fid}` |

```python
fx = pen.fx          # pen.filter 是它的别名

# 像 PS 图层样式一样叠着开（内阴影 + 浮雕 + 微模糊）
pen.text(60, 200, "帅", font_size=44, fill_color="#c23b22") \
   .fx_inner_shadow(1, 1, 2, "#ffffff", 0.6).fx_emboss().fx_blur(1.5)

# 工厂建链，一条链复用给多个元素
f = fx.chain().outline(3, "#fff").shadow(8, 10, 6).saturate(1.4)
pen.star(500, 400, 140, fill_color="#f4a261").set_filter(f)
pen.circle(620, 400, 90, fill_color="#2a9d8f").set_filter(f)
```

| 分类 | 方法 | 对应 PS/AI |
|---|---|---|
| 图层样式 | `shadow` `inner_shadow` `glow` `inner_glow` `bevel` `engrave` `outline` `color_overlay` | 投影/内阴影/外发光/内发光/斜面浮雕/雕刻凹陷/描边/颜色叠加 |
| 模糊锐化 | `blur` `sharpen` `motion_blur` | 高斯模糊/USM 锐化/动感模糊 |
| 风格化 | `roughen` `noise` `emboss` `edge_detect(width)` | 粗糙化/添加杂色/浮雕/查找边缘（width&gt;1 加粗边缘线） |
| 颜色调整 | `saturate` `hue_rotate` `brightness` `contrast` `gamma` `grayscale` `sepia` `invert` `posterize` | 色相饱和度/亮度对比度/曲线/去色/反相/色调分离 |

每个方法返回 `FilterChain`，可继续链式叠加；也支持 `f.apply(el)`、
`el.set_filter(f)`（默认叠加，`merge=False` 整条替换）、
`el.set_filter(None)`（清除），以及
`f.custom("feBlend", mode="screen", ...)` 追加任意 SVG 原语。
工厂方法与元素快捷方法一一对应（`pen.fx.blur(x)` 等价 `el.fx_blur(x)`）。
滤镜在浏览器/支持 SVG filter 的查看器中生效（cairosvg 导出 PNG 不渲染滤镜）。

## 类型提示（PyCharm / VSCode 自动补全）

全库 **314 个公共方法都带返回类型注解**，写完 `pen.` 立刻能看到每个方法返回什么，
链式调用也有提示：

```python
p = pen.path(fill_color="none", stroke_width=2)   # p: PathElement
p.move_to(50, 50).line_to(200, 80).close()        # 链式方法返回自身，提示不断链

c = pen.circle(100, 100, 50)                      # c: CircleElement
c.set_filter(pen.fx.shadow(6, 6, 5)).translate(10, 0)

g = pen.g()                                       # g: GroupElement
pen.linearGradient((0, 0), (1, 0), "red", "blue") # -> LinearGradient
pen.repeat_grid(tile, 3, 40, 2, 40)               # -> list[Element]
```

- 元素方法（`move_to`/`translate`/`set_filter`…）用 `TypeVar("_Self")` 标注，
  子类调用时推导出**子类本身**的类型（`PathElement.move_to()` 返回 `PathElement`）；
- 绘图板返回自身的方法（`resize`/`set_background_color`/`add_js`）标注 `_Pen`；
- 包内含 `py.typed`（PEP 561），`pip install malight` 后依然有提示；
- `examples/test_types.py` 会检查「有无漏注解 / 注解能否求值 / 运行时类型是否一致」，
  新增方法忘了写注解会直接测试失败。

## 导出：Chrome 引擎 与 cairo 引擎

```python
pen.finish()

pen.export_pdf()                                  # 默认 AUTO：有 Chrome 用 Chrome，否则回退 cairo
pen.export_pdf("out.pdf", engine=PDFMode.CHROME)  # 强制 Chrome（渲染与浏览器一致，含 SVG filter）
pen.export_pdf("out.pdf", engine=PDFMode.CAIROSVG)# 强制 cairo（无需浏览器）
pen.export_png(scale=2)                           # PNG AUTO：有 cairosvg 用它，没装自动改用 Chrome
pen.export_png(scale=2, mode=PNGMode.CHROME)      # PNG 走 Chrome（滤镜效果正确）
```

**导出后会把完整路径打印出来**，直接复制就能用（返回值也是绝对路径，方便脚本串联）：

```
[malight] SVG 导出成功（800x500）→ C:\proj\output\demo_basic.svg  [7.3 KB]
[malight] 未检测到 cairosvg，自动改用无头 Chrome 导出 PNG（对 SVG 滤镜的支持更好）
[malight] PNG 导出成功（Chrome 引擎、2 倍、滤镜完整）→ C:\proj\output\demo_basic.png  [45.9 KB]
[malight] PDF 导出成功（Chrome 引擎）→ C:\proj\output\demo_basic.pdf  [88.3 KB]
```

（以上为中文输出；默认是英文，`set_language("zh")` 即得。见 [i18n.zh.md](malight/i18n.zh.md)。）

| 引擎 | 依赖 | SVG filter（投影/发光/模糊/浮雕） | 适用场景 |
|---|---|---|---|
| **Chrome**（无头） | 本机 Chrome/Edge | ✅ 完整渲染 | 带滤镜成品、与浏览器一致的 PDF |
| **cairo** | `cairosvg` | ❌ 忽略 filter | 纯矢量图、无浏览器环境、快速导出 |

- Chrome 路径自动查找（注册表 → 常见安装目录 → PATH → Edge 兜底）；
  便携版/绿色版可用环境变量指定：`set MALIGHT_CHROME=D:\chrome\chrome.exe`；
- PDF 页边距为 0、页面尺寸与画布像素一一对应；PNG 按 `scale` 精确输出
  （480×320 的画布 `scale=2` 得到 960×640）；
- **两个引擎都找不到时会明确报错并给出两条安装建议**，不会只丢一句
  `ModuleNotFoundError`。完整对比见 `examples/demo_export.py` 与 [tools.md](malight/tools.zh.md)。

## 兼容与迁移

- **旧中文脚本**：`python -m malight.compat 旧脚本.py 新脚本.py`
  （中文 API → 英文短名，含 `import magicpen` → `import malight`）。
- **v1 英文脚本**：`import magicpen` 仍可运行（仓库根的 magicpen shim 自动转发），
  建议逐步改为 `from malight import Malight`。shim 仅随源码仓库提供，不进 whl。

对照表与全部映射规则见 [compat.md](malight/compat.zh.md)。

## 示例

`examples/` 下 13 个可运行示例：`demo_basic` `demo_path` `demo_effects`
`demo_animation` `demo_arrange` `demo_advanced` `demo_fx`（滤镜全家福）
`demo_ext`（扩展机制）`demo_export`（Chrome / cairo 双引擎导出对比），
子目录 `board_games/` 收棋类样例：`chinese_chess.py`（中国象棋）、
`international_chess.py`（国际象棋），
以及两个测试：`test_fx_smoke.py`（滤镜冒烟）、`test_types.py`（类型注解校验）。

**每个类文件里也带可直接运行的完整示例**（`if __name__ == "__main__":`）——
在 PyCharm 里点绿色三角，或命令行 `python malight/elements/circle.py` 就能跑，
示例覆盖该类的全部方法，注释写清了每一步在做什么：

```bash
python malight/elements/circle.py     # 圆：样式 / 变换 / 动画 / 克隆
python malight/elements/path.py       # 路径：全部命令 + pathkit 看点拖点
python malight/elements/group.py      # 组：嵌套 / 变换 / 包围盒 / 克隆
python malight/pathkit/editor.py      # 路径编辑器：看结构 / 拖点 / 加点删点 / 存档
python malight/pathkit/point.py       # 可调点：属性 / 移动 / 解包 / 相等
python malight/pathkit/segment.py     # 路径段：解析 / 取点 / 测长 / 拆分（纯几何）
# ... 或等价地用 python -m malight.elements.circle 运行
```

支持直接运行的范围：`malight/elements/*.py`（20 个元素类）+
`malight/pathkit/*.py`（解析器 / 编辑器 / 点 / 段）。
每个模块页的「完整示例」小节贴的就是这段代码。

## 打包发布（whl）

仓库自带一键脚本 `build_release.py`（在项目根目录，即 pyproject.toml 所在处运行）：

```bash
python build_release.py            # 构建 dist/malight-x.y.z-py3-none-any.whl + .tar.gz，并自动干净环境自检
python build_release.py --check    # 构建后追加 twine check 元数据校验
python build_release.py --upload   # 构建校验后直接上传 PyPI（需先 pip install twine）
python build_release.py --offline  # 不自动安装缺失工具（build/twine），whl 走 pip wheel 回退
```

上传 PyPI 的完整流程（脚本已内置，也可手动执行）：

```bash
pip install -U twine
python build_release.py --check
twine upload dist/*                          # 正式环境
twine upload --repository testpypi dist/*    # 建议先传 TestPyPI 验证
```

- 版本号唯一来源是 `malight/__init__.py` 的 `__version__`，pyproject 动态读取，改一处即可。
- 核心绘图**零依赖**；可选增强用 extras 安装：`pip install malight[export]`（PNG/PDF）、
  `malight[fontpath]`（文字转路径）、`malight[full]`。
- 发布前脚本会新建干净 venv 安装 whl 并实测绘图/滤镜/扩展，确保开箱即用。
- 模块的双语 `.md` 会随 sdist 一起发布（便于离线查阅），但不进 whl。

## 许可

见 [LICENSE](LICENSE)。
