# -*- coding: utf-8 -*-
"""
术语表（glossary）—— 文档字符串「摘要级双语」的中英对照表
Glossary - Chinese/English pairs for bilingual docstring summaries
==================================================================

用途 / Purpose:
    ``tools/bilingualize.py`` 用本表把源码里文档字符串的**首段**变成
    「中文 / English」形式；``tools/gen_docs.py`` 生成的模块文档也依托
    这些双语摘要。新增 API 时在表里补一行即可，缺条的会被脚本列出来。

约定 / Convention:
    键 = 首段摘要（已去掉「对应中文版 `xxx`」这类迁移提示、折叠空白）。
    值 = 一句话英文摘要，句末带句点。

    Key   = the first summary paragraph, with "对应中文版 `xxx`" migration
            notes stripped and whitespace collapsed.
    Value = a one-sentence English summary ending with a period.
"""

GLOSSARY = {
    "ClipMaskMixin —— 裁剪与遮罩（SVG <clipPath> / <mask>）（方法名与 SVG 元素名对应，旧名保留为别名）。":
        "ClipMaskMixin - clipping and masking (SVG clipPath and mask).",
    "TextMixin —— 文字（SVG <text> / <textPath> / 文字转路径）（方法名与 SVG 元素名对应，旧名保留为别名）。":
        "TextMixin - text: SVG text, textPath and text-to-path conversion.",
    "取全部锚点坐标（纯坐标版，便于打印 / 传参）。":
        "Return every anchor coordinate as plain tuples, handy for printing or passing around.",
    "取出全部锚点坐标（便于打印 / 传给外部算法）。":
        "Return every anchor coordinate, handy for printing or feeding to external algorithms.",
    "取得本路径的编辑器（可查看 / 拖动锚点与控制点）。":
        "Get a PathEditor for this path so you can inspect and drag its anchors and control points.",
    "把「字体枚举名 / 字体族名」字符串转换为枚举成员。":
        "Convert a font enum name or family name into a Font member.",
    "把颜色字符串 / 枚举名转换为枚举成员。":
        "Convert a color string or enum name into a ColorName member.",
    "旋转动画。":
        "Animate rotation.",
    "本段的英文类型名：move / line / cubic / quad / arc / close。":
        "The English kind name of this segment: move / line / cubic / quad / arc / close.",
    "结构发生变化（加点 / 删点 / 反转）后写回并重建点列表。":
        "Write back and rebuild the point list after a structural change such as inserting, removing or reversing.",
    "路径编辑器：查看 / 调整 PathElement 的锚点与控制点。":
        "Path editor: inspect and adjust a PathElement's anchors and control points.",
    "返回**带调整点**的线段序号列表（只有贝塞尔 / 圆弧段才有控制点）。":
        "Return the indices of segments that have control points; only Bezier and arc segments do.",
    "追加任意 SVG 滤镜原语（保留扩展能力，如 feBlend / feTile 等）。":
        "Append any raw SVG filter primitive, such as feBlend or feTile, so the chain stays extensible.",
    "重新从路径元素解析出线段 / 锚点 / 控制点（外部改过 d 后调用）。":
        "Re-parse segments, anchors and control points from the path element, for use after d changed externally.",

    # =====================================================================
    # definitions.py —— 颜色 / 纸张 / 枚举定义
    # =====================================================================
    "颜色常量与颜色运算工具。":
        "Color constants and color-arithmetic helpers.",
    "构造 RGB 颜色，返回 #rrggbb 字符串。":
        "Build an RGB color and return a #rrggbb string.",
    "把颜色名（中/英文）转换为十六进制值；无法识别时原样返回。":
        "Convert a color name (Chinese or English) to hex; unknown input is returned as-is.",
    "查询中文颜色名对应的英文颜色名。":
        "Look up the English color name for a Chinese one.",
    "返回一个随机十六进制颜色。":
        "Return a random hex color.",
    "反色（每个分量取 255 差值）。":
        "Invert the color (each channel becomes 255 minus its value).",
    "颜色加深。":
        "Darken a color.",
    "颜色变浅。":
        "Lighten a color.",
    "多个颜色按 RGB 分量依次相加（上限 255）。":
        "Add several colors channel-wise, clamping each channel at 255.",
    "两种颜色 RGB 分量相加（各分量上限 255）。":
        "Add two colors channel-wise, clamping each channel at 255.",
    "按透明度叠加两种颜色（模拟顶层颜色以 alpha 叠在底层之上）。":
        "Blend two colors by alpha, compositing the top color over the bottom one.",
    "按顺序叠加多个颜色。":
        "Blend several colors in order.",
    "把任意颜色转换为 (r, g, b) 元组（分量 0-255）。":
        "Convert any color to an (r, g, b) tuple with channels 0-255.",
    "把 (r, g, b) 元组转换为 #rrggbb 字符串。":
        "Convert an (r, g, b) tuple to a #rrggbb string.",
    "常用颜色枚举（对应「枚举 + 字符串」双写法中的枚举部分）。":
        "Common color enum - the enum half of the enum-plus-string pattern.",
    "取颜色的十六进制值（中/英文名均可）。":
        "Return a color's hex value; Chinese and English names both work.",
    "列出全部枚举名。示例:: ColorName.list_names()[:3]":
        "List every enum member name.",
    "粉笔色。":
        "Chalk colors - a soft palette that looks like chalk on a blackboard.",
    "返回全部粉笔色列表。":
        "Return the full list of chalk colors.",
    "预置配色方案，每项为颜色列表。":
        "Preset color schemes; each entry is a list of colors.",
    "循环取色：索引超出方案长度时从头再取。":
        "Cyclic color pick - wraps to the start when the index exceeds the scheme length.",
    "元素矢量效果。":
        "SVG vector-effect.",
    "常用屏幕分辨率，返回 (宽, 高)。":
        "Common screen resolutions as (width, height).",
    "常见手机分辨率 1080x2376。":
        "Common phone resolution 1080x2376.",
    "全高清 1920x1080。":
        "Full HD 1920x1080.",
    "高清 1280x720。":
        "HD 1280x720.",
    "华为畅享 60X：1080x2376。":
        "Huawei Enjoy 60X: 1080x2376.",
    "华为 Nova12：1084x2412。":
        "Huawei Nova 12: 1084x2412.",
    "华为 Mate50：1224x2700。":
        "Huawei Mate 50: 1224x2700.",
    "纸张尺寸。":
        "Paper sizes in pixels.",
    "A3 横向（420mm x 297mm）。sheets 为连续纸张页数（高度方向拼接）。":
        "A3 landscape (420mm x 297mm); sheets is the number of pages stacked vertically.",
    "A3 纵向。":
        "A3 portrait.",
    "A4 横向（297mm x 210mm）。":
        "A4 landscape (297mm x 210mm).",
    "A4 纵向。":
        "A4 portrait.",
    "A5 横向。":
        "A5 landscape.",
    "A5 纵向。":
        "A5 portrait.",
    "页面方向。":
        "Page orientation.",
    "文字水平对齐。":
        "Horizontal text alignment (SVG text-anchor).",
    "文字垂直对齐。":
        "Vertical text alignment (SVG alignment-baseline / dominant-baseline).",
    "箭头样式。":
        "Arrowhead styles.",
    "描边拐角连接样式。":
        "Stroke corner join style (SVG stroke-linejoin).",
    "描边线端样式。":
        "Stroke line cap style (SVG stroke-linecap).",
    "图像渲染设置。":
        "Image rendering hints (SVG image-rendering).",
    "调试定位点样式。":
        "Debug point style.",
    "网格重复排布类型。":
        "Grid repeat layout types.",
    "空间坐标系单位。":
        "Coordinate-space units (SVG gradientUnits / clipPathUnits and friends).",
    "页面打印设置，用于 finish() 时的 @page 样式。":
        "Print settings used for the @page rule emitted by finish().",
    "PDF 导出方式。":
        "PDF export engines.",
    "PNG 导出方式。":
        "PNG export engines.",
    "DOCX 导出方式。":
        "DOCX export engines.",
    "填充规则。":
        "Fill rule (SVG fill-rule).",
    "虚线样式预设（SVG stroke-dasharray，英文版新增）。":
        "Dash presets (SVG stroke-dasharray).",
    "混合模式（CSS mix-blend-mode，英文版新增）。":
        "Blend modes (CSS mix-blend-mode).",
    "字重（SVG font-weight，英文版新增）。":
        "Font weights (SVG font-weight).",
    "文字修饰线（SVG text-decoration，英文版新增）。":
        "Text decoration lines (SVG text-decoration).",
    "文字宽度调整方式（SVG lengthAdjust，配合 text_length 使用）。":
        "How text width is adjusted (SVG lengthAdjust, used with text_length).",
    "图片缩放保持比例方式（SVG preserveAspectRatio，英文版新增）。":
        "How an image keeps its aspect ratio (SVG preserveAspectRatio).",
    "自定义对齐方式，如 \"xMinYMin meet\"。":
        "Custom alignment, e.g. \"xMinYMin meet\".",
    "渐变扩散方式（SVG spreadMethod，英文版新增）。":
        "Gradient spread method (SVG spreadMethod).",

    # =====================================================================
    # i18n.py —— 运行时多语言
    # =====================================================================
    "语言枚举（继承 str，可直接当字符串用）。":
        "Language enum; it subclasses str so it can be used as a plain string.",
    "把任意写法归一成 Language 成员。示例:: Language.of(\"zh_CN\")":
        "Normalise any spelling into a Language member.",
    "临时切换语言，退出 ``with`` 后自动恢复（适合测试与文档生成）。":
        "Temporarily switch language; the previous setting is restored on exit.",

    # =====================================================================
    # fonts.py —— 字体
    # =====================================================================
    "系统字体枚举。成员值即 SVG 的 font-family 名。":
        "System font enum; each member value is the SVG font-family name.",
    "判断传入的是不是「字体文件路径」（而不是字体族名）。":
        "Tell whether the argument is a font FILE path rather than a family name.",
    "从字体文件推断「字体族名」（用于生成 @font-face 的 family）。":
        "Infer a font family name from a font file, used for the @font-face family.",
    "列出全部字体枚举名（便于做字体选择器）。":
        "List every font enum member name; handy for building font pickers.",
    "列出全部字体枚举值（字体名）。示例:: Font.list_values()[:5]":
        "List every font enum value, i.e. the font names.",
    "兼容旧版 `SystemFont.chinese_name`：返回字体对应的枚举名。":
        "Back-compat with `SystemFont.chinese_name`: return the enum member name.",

    # =====================================================================
    # svg_backend.py —— 轻量 SVG 后端
    # =====================================================================
    "SVG 节点：标签 + 属性字典 + 子节点列表。":
        "An SVG node: tag, attribute dict and child list.",
    "添加子节点（SvgNode 或原始 XML 字符串）。":
        "Append a child node - either an SvgNode or a raw XML string.",
    "设置属性值。值为 None 时删除该属性（便于条件属性）。":
        "Set an attribute; passing None removes it, which makes conditional attributes easy.",
    "按 id 递归查找子节点；找不到返回 None。":
        "Find a descendant by id recursively; returns None when absent.",
    "移除指定子节点（不抛错）。":
        "Remove a child node, silently ignoring a missing one.",
    "序列化为 XML 字符串。":
        "Serialise the node to an XML string.",

    # =====================================================================
    # gradients.py —— 渐变
    # =====================================================================
    "渐变基类：管理色标（stop）与坐标单位（内部使用）。":
        "Gradient base class managing stops and coordinate units (internal).",
    "渐变 id（引用时用 ``url(#id)``）。":
        "The gradient id; reference it as ``url(#id)``.",
    "返回 paint 引用串，可直接作为 fill_color/stroke_color 使用。":
        "Return the paint reference string, usable directly as fill_color/stroke_color.",
    "添加渐变色标。":
        "Add a gradient color stop.",
    "设置渐变的 gradientTransform（原始变换串）。":
        "Set the gradient's gradientTransform from a raw transform string.",
    "线性渐变。":
        "Linear gradient.",
    "径向渐变。":
        "Radial gradient.",

    # =====================================================================
    # board/core.py —— 绘图板核心
    # =====================================================================
    "MagicPen 绘图板。":
        "The MagicPen drawing board.",
    "BoardCore —— MagicPen 核心类（Mixin）。":
        "BoardCore - the MagicPen core class (a mixin).",
    "按 id 获取元素。":
        "Fetch an element by id.",
    "页面打印设置。":
        "Configure page and print settings.",
    "保存配置项。":
        "Store a config entry.",
    "读取配置项。":
        "Read a config entry.",
    "挂载扩展工具包（英文版新增，配合 malight.ext 扩展机制）。":
        "Mount an extension toolkit, used with the malight.ext mechanism.",
    "修改画布大小。":
        "Resize the canvas.",
    "设置画布背景色。":
        "Set the canvas background color.",
    "添加背景矩形。":
        "Add a background rectangle; unlike set_background_color it takes opacity and returns the element.",
    "添加 JavaScript 代码，嵌入 <script>。":
        "Embed JavaScript by adding a <script> element.",
    "写软件签名信息。":
        "Write a software signature.",
    "作者印章：圆形红印 + 名字。":
        "Author stamp: a round red seal plus a name.",
    "创作前钩子，子类可覆写。":
        "Pre-draw hook; subclasses may override.",
    "创作主钩子，子类可覆写：把绘图代码写在这里。":
        "Main draw hook; subclasses override this and put their drawing code here.",
    "创作后钩子，子类可覆写。":
        "Post-draw hook; subclasses may override.",
    "保存前修改文件名钩子，返回新文件名或 None。":
        "Hook to change the output filename before saving; return a new name or None.",
    "完成并保存 SVG。":
        "Finish drawing and save the SVG.",
    "导出 PNG，需 finish() 先保存。":
        "Export PNG; call finish() first to save the SVG.",
    "导出 PDF，需 finish() 先保存。":
        "Export PDF; call finish() first to save the SVG.",
    "导出 DOCX。":
        "Export DOCX.",

    # =====================================================================
    # board 各 Mixin —— 类摘要
    # =====================================================================
    "ContainerMixin —— 容器元素（g/symbol/use/pattern/marker/a）（方法名与 SVG 元素名对应，旧名保留为别名）。":
        "ContainerMixin - container elements (g / symbol / use / pattern / marker / a).",
    "DebugMixin —— 调试辅助（网格/图框/测距/关键点）（方法名与 SVG 元素名对应，旧名保留为别名）。":
        "DebugMixin - debugging helpers (grids, frames, measurements, key points).",
    "FilterAPI —— 滤镜工厂。":
        "FilterAPI - the filter factory.",
    "GradientMixin —— 渐变（SVG <linearGradient>/<radialGradient> 及彩虹/黄金快捷）（方法名与 SVG 元素名对应，旧名保留为别名）。":
        "GradientMixin - gradients (SVG linearGradient / radialGradient) plus rainbow and gold shortcuts.",
    "ImageMixin —— 图像（<image> 贴图与 SVG 导入）（方法名与 SVG 元素名对应，旧名保留为别名）。":
        "ImageMixin - images (bitmap <image> and SVG import).",
    "LayoutMixin —— 排列（水平/垂直/网格/环绕）（方法名与 SVG 元素名对应，旧名保留为别名）。":
        "LayoutMixin - arranging elements horizontally, vertically, in a grid or around a circle.",
    "PathMixin —— 路径与连线（path/polyline/表格/箭头/波浪线）（方法名与 SVG 元素名对应，旧名保留为别名）。":
        "PathMixin - paths and connectors: path, polyline, tables, arrows, wave lines.",
    "RepeatMixin —— 重复（网格重复/环绕重复/线性重复）（方法名与 SVG 元素名对应，旧名保留为别名）。":
        "RepeatMixin - repetition: grid, circular and linear.",
    "ShapeMixin —— 基本图形（SVG 元素命名：circle/ellipse/rect/...）（方法名与 SVG 元素名对应，旧名保留为别名）。":
        "ShapeMixin - basic shapes, named after their SVG elements (circle / ellipse / rect / ...).",
    "样式子工具（pen.style），对应中文版 `样式工具集`： 管理 CSS 类、全局样式表与**字体文件内嵌**。":
        "Style helper (pen.style) managing CSS classes, the global stylesheet and font-file embedding.",

    # =====================================================================
    # board/containers.py
    # =====================================================================
    "创建组元素。":
        "Create a group element.",
    "创建模板。":
        "Create a symbol (reusable template).",
    "实例化模板。":
        "Instantiate a symbol with a <use> element.",
    "创建平铺图案。":
        "Create a tiling pattern fill.",
    "复制元素，可指定偏移。":
        "Duplicate an element, optionally with an offset.",
    "给元素加超链接。":
        "Wrap an element in a hyperlink.",
    "创建线端标记。":
        "Create a line-end marker such as an arrowhead.",

    # =====================================================================
    # board/debug.py
    # =====================================================================
    "两点间测距标注。":
        "Annotate the distance between two points.",
    "显示网格。":
        "Draw a grid.",
    "显示画布边框。":
        "Draw the canvas frame.",
    "画定位点标记。":
        "Draw a point marker.",
    "批量显示关键点坐标。":
        "Label the coordinates of several key points.",

    # =====================================================================
    # board/effects.py
    # =====================================================================
    "用任意形状裁剪目标元素。":
        "Clip target elements with an arbitrary shape.",
    "圆形裁剪。":
        "Clip with a circle.",
    "矩形裁剪。":
        "Clip with a rectangle.",
    "遮罩：按遮罩亮度决定目标可见度。":
        "Mask: the mask's brightness decides how visible the target is.",

    # =====================================================================
    # board/filters.py + board/fx.py —— 滤镜
    # =====================================================================
    "新建一个空滤镜链，然后自由叠加效果。":
        "Start an empty filter chain and stack effects on it freely.",
    "高斯模糊。示例:: pen.image(\"p.jpg\", filter=pen.fx.blur(4))":
        "Gaussian blur.",
    "锐化（0~1）。示例:: pen.star(500, 300, 120, filter=pen.fx.sharpen(0.8))":
        "Sharpen, amount 0-1.",
    "动感模糊。示例:: pen.circle(200, 500, 40, filter=pen.fx.motion_blur(12, 0))":
        "Motion blur.",
    "投影（= drop_shadow 的短名）。示例:: pen.rect(100, 100, 200, 150, filter=pen.fx.shadow(6, 6, 5))":
        "Drop shadow; a short alias of drop_shadow.",
    "投影（旧参数名兼容版）。示例:: fx = pen.fx.drop_shadow(5, 5, 4)":
        "Drop shadow, kept for the older parameter names.",
    "内阴影。示例:: pen.rect(350, 200, 300, 200, filter=pen.fx.inner_shadow())":
        "Inner shadow.",
    "外发光。示例:: pen.text(500, 150, \"GLOW\", filter=pen.fx.glow(8, \"#00b4d8\"))":
        "Outer glow.",
    "内发光。示例:: pen.circle(700, 400, 100, filter=pen.fx.inner_glow())":
        "Inner glow.",
    "浮雕斜面（PS 斜面和浮雕）。示例:: pen.text(500, 300, \"3D\", filter=pen.fx.bevel())":
        "Bevel and emboss, like the Photoshop layer style.",
    "雕刻凹陷（与 bevel 的凸起相反）。示例:: pen.text(60, 200, \"帅\", filter=pen.fx.engrave())":
        "Engrave, the opposite of a raised bevel.",
    "外描边。示例:: pen.text(500, 200, \"HALO\", filter=pen.fx.outline(4, \"#d62828\"))":
        "Outer stroke growing outwards along the outline.",
    "粗糙化（手绘感）。示例:: pen.heart(500, 300, 160, filter=pen.fx.roughen())":
        "Roughen for a hand-drawn feel.",
    "噪点颗粒。示例:: pen.rect(300, 200, 400, 250, filter=pen.fx.noise(0.2))":
        "Grainy noise overlay.",
    "浮雕灰度。示例:: pen.text(500, 300, \"EM\", filter=pen.fx.emboss())":
        "Grayscale emboss.",
    "边缘检测（线稿感）。示例:: pen.star(500, 300, 140, filter=pen.fx.edge_detect())":
        "Edge detection for a line-art look.",
    "饱和度。示例:: pen.circle(300, 300, 100, filter=pen.fx.saturate(1.6))":
        "Saturation.",
    "色相旋转。示例:: pen.circle(500, 300, 100, filter=pen.fx.hue_rotate(140))":
        "Hue rotation.",
    "去色。示例:: pen.image(\"p.jpg\", filter=pen.fx.grayscale())":
        "Desaturate to grayscale.",
    "褐色怀旧调。示例:: pen.image(\"old.jpg\", filter=pen.fx.sepia())":
        "Sepia tone.",
    "亮度。示例:: pen.rect(0, 0, 500, 300, filter=pen.fx.brightness(1.4))":
        "Brightness.",
    "对比度。示例:: pen.image(\"p.jpg\", filter=pen.fx.contrast(1.5))":
        "Contrast.",
    "伽马校正。示例:: pen.image(\"p.jpg\", filter=pen.fx.gamma(0.8, 0.9, 1.1))":
        "Gamma correction.",
    "反相。示例:: pen.image(\"p.jpg\", filter=pen.fx.invert())":
        "Invert colors.",
    "色调分离。示例:: pen.image(\"p.jpg\", filter=pen.fx.posterize(3))":
        "Posterize; fewer levels means flatter color blocks.",
    "颜色叠加。示例:: pen.polygon(pts, filter=pen.fx.color_overlay(\"#073b4c\", 0.7))":
        "Color overlay.",
    "FilterChain —— 链式滤镜（对应 Photoshop 的「图层样式 + 滤镜」）。":
        "FilterChain - chainable filters, modelled on Photoshop layer styles plus filters.",
    "返回 filter 引用串 \"url(#id)\"。示例:: el.node.set(\"filter\", f.url())":
        "Return the filter reference string \"url(#id)\".",
    "把滤镜应用到元素（等价于 el.set_filter(f)）。示例:: f.apply(circle)":
        "Apply the filter to an element; equivalent to el.set_filter(f).",
    "高斯模糊（对应 PS「高斯模糊」）。":
        "Gaussian blur, matching Photoshop's Gaussian Blur.",
    "锐化（对应 PS「USM 锐化」的简化版，amount 0~1）。":
        "Sharpen, a simplified Photoshop USM Sharpen, amount 0-1.",
    "方向模糊（对应 PS「动感模糊」，distance ≤ 15 效果最佳）。":
        "Directional blur, like Photoshop's Motion Blur; distance up to about 15 works best.",
    "投影（对应 PS「投影 Drop Shadow」）。":
        "Drop shadow.",
    "内阴影（对应 PS「内阴影 Inner Shadow」）。":
        "Inner shadow.",
    "外发光（对应 PS「外发光 Outer Glow」）。":
        "Outer glow.",
    "内发光（对应 PS「内发光 Inner Glow」）。":
        "Inner glow.",
    "浮雕斜面（对应 PS「斜面和浮雕 Bevel & Emboss」的高光部分）。":
        "Bevel and emboss, covering the highlight half of the Photoshop effect.",
    "雕刻凹陷（对应 PS「斜面和浮雕 Bevel & Emboss」的凹陷方向，与 bevel 相反）。":
        "Engrave - the opposite of bevel: the top/left inner edge goes dark and the bottom/right inner edge catches the light, so the shape reads as carved into the surface.",
    "外描边（对应 PS「描边 Stroke」图层样式，沿轮廓向外扩）。":
        "Outer stroke that expands outwards along the outline.",
    "粗糙化（对应 PS「扩散/粗糙化」手绘感，用湍流置换实现）。":
        "Roughen for a hand-drawn look, implemented with turbulence displacement.",
    "噪点颗粒（对应 PS「添加杂色」，叠加在图形上）。":
        "Grainy noise overlaid on the shape.",
    "浮雕灰度（对应 PS「风格化→浮雕效果」，输出灰度浮雕）。":
        "Grayscale emboss, like Photoshop's Stylize - Emboss.",
    "边缘检测（对应 PS「风格化→查找边缘」，输出线稿感灰度）。":
        "Edge detection producing line-art grayscale, like Photoshop's Find Edges.",
    "饱和度（对应 PS「色相/饱和度」）：factor<1 降低，>1 提高。":
        "Saturation: factor below 1 reduces it, above 1 increases it.",
    "色相旋转（对应 PS「色相」滑块，整图换色系）。":
        "Hue rotation, shifting the whole palette like Photoshop's hue slider.",
    "去色（对应 PS「去色/黑白」）。示例:: pen.image(\"p.jpg\").set_filter(pen.fx.grayscale())":
        "Desaturate, like Photoshop's Desaturate / Black and White.",
    "怀旧褐色调（对应 PS「照片滤镜→褐」）。":
        "Warm sepia tone, like Photoshop's Photo Filter.",
    "亮度（对应 PS「亮度」）：factor<1 变暗，>1 变亮。":
        "Brightness: factor below 1 darkens, above 1 brightens.",
    "对比度（对应 PS「对比度」）：factor<1 降低，>1 提高。":
        "Contrast: factor below 1 reduces it, above 1 increases it.",
    "伽马校正（对应 PS「曝光度/曲线」的幂次调整）：>1 提亮中间调，<1 压暗。":
        "Gamma correction: above 1 lifts midtones, below 1 darkens them.",
    "反相（对应 PS「反相 Ctrl+I」）。":
        "Invert colors.",
    "色调分离（对应 PS「色调分离 Posterize」）：levels 越小色块感越强。":
        "Posterize: fewer levels produce flatter color blocks.",
    "颜色叠加（对应 PS「颜色叠加 Color Overlay」）。":
        "Color overlay.",

    # =====================================================================
    # board/gradients_mixin.py
    # =====================================================================
    "创建线性渐变。":
        "Create a linear gradient.",
    "创建径向渐变。":
        "Create a radial gradient.",
    "生成彩虹七色渐变stops。":
        "Build the seven rainbow gradient stops.",
    "创建彩虹线性渐变。":
        "Create a rainbow linear gradient.",
    "创建彩虹径向渐变。":
        "Create a rainbow radial gradient.",
    "创建黄金质感渐变。":
        "Create a gold-textured gradient.",

    # =====================================================================
    # board/images.py
    # =====================================================================
    "贴位图。本地文件自动 base64 内嵌。":
        "Place a bitmap; local files are base64-embedded automatically.",
    "贴 SVG 文件。":
        "Place an SVG file as an image.",
    "把 SVG 文件内容解析为可编辑组。":
        "Parse an SVG file into an editable group.",
    "把 SVG 文件注册为模板，用 pen.template(id) 复用 。":
        "Register an SVG file as a symbol, then reuse it with pen.template(id).",

    # =====================================================================
    # board/layout.py
    # =====================================================================
    "水平排列：按包围盒左右相接。":
        "Lay out horizontally, placing bounding boxes edge to edge.",
    "垂直排列。":
        "Lay out vertically.",
    "网格排列。":
        "Lay out in a grid.",
    "环绕排列：元素沿圆周均匀分布。":
        "Lay out around a circle, spacing the elements evenly.",

    # =====================================================================
    # board/paths.py
    # =====================================================================
    "开始一条路径。返回 PathElement， 之后调用 move_to/line_to/cubic_to/... 组合形状。":
        "Start a path and return a PathElement; then chain move_to / line_to / cubic_to and friends.",
    "把顶点列表连成折线路径。":
        "Connect a list of vertices into a polyline path.",
    "把顶点列表连成光滑曲线。":
        "Connect a list of vertices into a smooth Catmull-Rom curve.",
    "画正弦波浪线。":
        "Draw a sine wave line.",
    "画海浪线。":
        "Draw a sea-wave line.",
    "画多条水平线：在 y1~y2 之间均布 count 条。":
        "Draw several horizontal lines: count of them spread evenly between y1 and y2.",
    "画多条垂直线：在 x1~x2 之间均布 count 条。":
        "Draw several vertical lines: count of them spread evenly between x1 and x2.",
    "画表格。":
        "Draw a table.",
    "计算箭头信息。":
        "Compute the geometry of an arrowhead.",
    "画带箭头的线段。":
        "Draw a line segment with an arrowhead.",

    # =====================================================================
    # board/repeat.py
    # =====================================================================
    "环绕重复：一个元素复制 count 份绕圆分布。":
        "Circular repeat: copy an element count times around a circle.",
    "网格重复。":
        "Grid repeat.",
    "水平重复。":
        "Horizontal repeat.",
    "垂直重复。示例见 repeat_horizontal。":
        "Vertical repeat; see repeat_horizontal for an example.",

    # =====================================================================
    # board/shapes.py
    # =====================================================================
    "画圆。":
        "Draw a circle.",
    "画椭圆。":
        "Draw an ellipse.",
    "画矩形。":
        "Draw a rectangle.",
    "画正方形。":
        "Draw a square.",
    "画一条线段。":
        "Draw a line segment.",
    "画十字标记，常用于标注关键点。":
        "Draw a cross marker, often used to label key points.",
    "画折线元素。":
        "Draw a polyline element.",
    "画多边形。":
        "Draw a polygon.",
    "画正 N 边形。":
        "Draw a regular N-sided polygon.",
    "画正三角形。":
        "Draw an equilateral triangle.",
    "画正五边形。":
        "Draw a regular pentagon.",
    "画正六边形。":
        "Draw a regular hexagon.",
    "画 N 角星。":
        "Draw an N-pointed star.",
    "画菱形。":
        "Draw a diamond.",
    "画爱心。":
        "Draw a heart.",

    # =====================================================================
    # board/style.py
    # =====================================================================
    "定义 CSS 类。":
        "Define a CSS class.",
    "把字体文件内嵌为 @font-face，返回可直接用于 font-family 的族名。":
        "Embed a font file as @font-face and return a family name usable for font-family.",
    "生成 <style> 节点（finish 时调用，内部方法）。":
        "Build the <style> node; called by finish() and considered internal.",

    # =====================================================================
    # board/text_board.py
    # =====================================================================
    "写文字。":
        "Write text.",
    "文字沿路径排列。":
        "Lay text out along a path.",
    "文字转矢量路径。":
        "Convert text into vector paths.",

    # =====================================================================
    # elements/base.py
    # =====================================================================
    "所有元素的基类。":
        "Base class of every element.",
    "设置元素 id（可用于 get_element(id) 反查）。":
        "Set the element id, which get_element(id) can look up later.",
    "给元素绑定滤镜（英文版新增，配合 pen.fx 滤镜工厂）。":
        "Attach a filter, used together with the pen.fx filter factory.",
    "平移元素。":
        "Translate the element.",
    "旋转元素。":
        "Rotate the element.",
    "缩放元素（sy 缺省时等比）。":
        "Scale the element; omitting sy keeps it proportional.",
    "沿 X 轴倾斜（度）。示例:: el.skew_x(15)":
        "Shear along the X axis, in degrees.",
    "沿 Y 轴倾斜（度）。示例:: el.skew_y(15)":
        "Shear along the Y axis, in degrees.",
    "透明度渐变动画。":
        "Animate opacity.",
    "平移动画。":
        "Animate translation.",
    "缩放动画。":
        "Animate scaling.",
    "X 轴倾斜动画。示例:: el.animate_skew_x(20)":
        "Animate a shear along the X axis.",
    "Y 轴倾斜动画。示例:: el.animate_skew_y(20)":
        "Animate a shear along the Y axis.",
    "沿轨迹移动动画。":
        "Animate movement along a motion path.",
    "虚线流动画：蚂蚁线效果。":
        "Animate marching-ants dashes flowing along the stroke.",
    "从画布上删除本元素。":
        "Remove this element from the canvas.",
    "置顶：移到父容器的最后一个。":
        "Bring to front by moving last among siblings.",
    "置底（英文版新增）：移到父容器的第一个。":
        "Send to back by moving first among siblings.",
    "把元素移动到另一个组。":
        "Move the element into another group.",
    "克隆元素，可指定偏移与新 id。":
        "Clone the element, optionally with an offset and a new id.",
    "按需更新元素属性（英文版新增：只改传入的项，其余保持原值）。":
        "Update only the attributes you pass in; everything else keeps its current value.",
    "元素包围盒 (min_x, min_y, max_x, max_y)；无法确定时返回 None。":
        "Element bounding box as (min_x, min_y, max_x, max_y); None when it cannot be determined.",
    "中心点 x。示例:: print(el.center_x)":
        "Center x coordinate.",
    "中心点 y。":
        "Center y coordinate.",
    "宽度。":
        "Width.",
    "高度。":
        "Height.",

    # =====================================================================
    # elements/*.py —— 各元素类
    # =====================================================================
    "圆元素。由 ``pen.circle`` 创建。":
        "Circle element, created by ``pen.circle``.",
    "包围盒。":
        "Bounding box.",
    "转换为 PathElement。":
        "Convert to a PathElement.",
    "裁剪元素。":
        "Clip-path element.",
    "把裁剪应用到目标元素（可为单个或列表）。":
        "Apply the clip to one target element or a list of them.",
    "椭圆元素。":
        "Ellipse element.",
    "包围盒（未考虑旋转）。":
        "Bounding box, ignoring rotation.",
    "组元素：把多个元素打包，便于整体变换/动画。":
        "Group element: bundle elements so they can be transformed or animated together.",
    "把元素加入本组。":
        "Add an element to this group.",
    "add_element 的别名。":
        "Alias of add_element.",
    "从组中移除元素。":
        "Remove an element from the group.",
    "取本组内的直接子元素对象（不含孙辈），对应中文版 `元素列表`。":
        "Return this group's immediate children, excluding grandchildren.",
    "取本组内**所有**后代元素对象（递归展开嵌套组）。":
        "Return every descendant element, recursing into nested groups.",
    "组内所有子元素包围盒的并集 (min_x, min_y, max_x, max_y)。":
        "Union of the bounding boxes of all children, as (min_x, min_y, max_x, max_y).",
    "位图图像元素。":
        "Bitmap image element.",
    "线元素。":
        "Line element.",
    "链接元素：点击元素打开网页。":
        "Link element: clicking the element opens a URL.",
    "把元素包进链接。":
        "Wrap an element in a link.",
    "标记元素：定义箭头等线端装饰。":
        "Marker element defining line-end decorations such as arrowheads.",
    "把图形加入 marker 内容。":
        "Add a shape to the marker content.",
    "遮罩元素：按亮度控制可见度。":
        "Mask element controlling visibility by luminance.",
    "把遮罩应用到目标元素。示例:: m.apply_to(img)":
        "Apply the mask to a target element.",
    "路径元素。":
        "Path element.",
    "获取路径的 d 字符串。":
        "Return the path's d string.",
    "直接设置 SVG path 的 d 字符串（英文版新增，对应原版 `原生path`）。":
        "Set the SVG path d string directly.",
    "抬笔移动到指定点（不画线），并开启新子路径。":
        "Lift the pen, move to a point without drawing, and start a new subpath.",
    "从当前点画直线到目标点。":
        "Draw a straight line from the current point to the target point.",
    "水平线到 end_x。示例:: p.h_line_to(200)":
        "Draw a horizontal line to end_x.",
    "垂直线到 end_y。示例:: p.v_line_to(200)":
        "Draw a vertical line to end_y.",
    "三次贝塞尔曲线。":
        "Cubic Bézier curve.",
    "平滑三次贝塞尔。":
        "Smooth cubic Bézier continuation.",
    "二次贝塞尔曲线。":
        "Quadratic Bézier curve.",
    "平滑二次贝塞尔。":
        "Smooth quadratic Bézier continuation.",
    "椭圆弧。":
        "Elliptical arc.",
    "圆弧。":
        "Circular arc.",
    "在路径中以圆弧画完整圆。":
        "Draw a full circle in the path using arc commands.",
    "闭合当前子路径。":
        "Close the current subpath.",
    "开启新子路径：同一元素里画不相连的多段。":
        "Start a new subpath so one element can hold several disconnected pieces.",
    "沿当前朝向前进并画线。":
        "Move forward along the current heading, drawing a line.",
    "沿当前朝向后退并画线。示例:: p.backward(50)":
        "Move backwards along the current heading, drawing a line.",
    "右转 angle 度后移动（不画线）。":
        "Turn right by angle degrees and move without drawing.",
    "左转 angle 度后移动。示例:: p.turn_left_move(90)":
        "Turn left by angle degrees and move without drawing.",
    "右转 angle 度后画线。":
        "Turn right by angle degrees and draw a line.",
    "左转 angle 度后画线。":
        "Turn left by angle degrees and draw a line.",
    "右转圆弧：画一段向右弯的弧线。":
        "Turn-right arc: draw an arc curving to the right.",
    "左转圆弧。示例:: p.turn_left_arc(90, 40)":
        "Turn-left arc.",
    "两线段之间倒圆角： 从当前点经 p1 拐向 p2，拐角处以 radius 圆弧过渡。":
        "Round the corner between two segments: go from the current point through p1 towards p2 with an arc of radius.",
    "平移路径的所有坐标点。":
        "Translate every coordinate of the path.",
    "反转路径方向：起终点互换，形状不变。":
        "Reverse the path direction, swapping start and end while keeping the shape.",
    "合并另一条路径到本路径。":
        "Merge another path into this one.",
    "并集：返回新路径元素。":
        "Union: return a new path element.",
    "交集。示例:: common = pa.intersect(pb)":
        "Intersection.",
    "差集。示例:: hole = pa.subtract(pb)":
        "Difference.",
    "采样路径为顶点列表，供布尔/测距等使用。":
        "Sample the path into a vertex list for boolean ops and measurements.",
    "路径总长度。":
        "Total path length.",
    "取路径上指定比例位置的坐标。":
        "Return the coordinates at a given fraction along the path.",
    "路径包围盒（按顶点采样近似）。":
        "Path bounding box, approximated from sampled vertices.",
    "取路径的全部线段对象（每段含起点/终点/控制点）。":
        "Return every PathSegment, each carrying its start, end and control points.",
    "取全部锚点对象（曲线的起点、终点、拐点）。":
        "Return every anchor point: the curve start, end and corner points.",
    "取全部控制点对象（贝塞尔曲线的调整点）。":
        "Return every control point, i.e. the Bézier handles.",
    "取全部控制点坐标（纯坐标版）。":
        "Return all control-point coordinates as plain tuples.",
    "移动第 index 个锚点（改完立即生效）。":
        "Move the anchor at index and apply it immediately.",
    "移动「第 seg_index 段」的第 ctrl_index 个调整点（改完立即生效）。":
        "Move control point ctrl_index of segment seg_index and apply it immediately.",
    "生成路径结构说明（每段的起点/调整点/终点 + 全部锚点坐标）。":
        "Build a readable path report: start / controls / end per segment, plus every anchor.",
    "打印路径结构说明（看曲线有几个点、点在哪）。":
        "Print the path report so you can see how many points a curve has and where they sit.",
    "在画布上画出锚点（方块）与调整杆（线 + 圆点），像钢笔工具一样。":
        "Draw anchors as squares and handles as lines with round dots, just like a pen tool.",
    "把路径中的折线顶点平滑为贝塞尔曲线。":
        "Smooth the polyline vertices into a Bézier curve.",
    "更新路径样式属性。":
        "Update the path's style attributes.",
    "图案元素：平铺填充纹理。":
        "Pattern element: a tiling fill texture.",
    "把元素加入图案内容。示例:: p.add_element(shape)":
        "Add a shape to the pattern content.",
    "多边形元素。":
        "Polygon element.",
    "折线元素。":
        "Polyline element.",
    "矩形元素。":
        "Rectangle element.",
    "SVG 图片元素：把另一个 SVG 文件作为图像嵌入。":
        "SVG image element: embed another SVG file as an image.",
    "模板元素：定义可复用的图形。":
        "Symbol element defining a reusable graphic.",
    "把元素加入模板内容。示例:: t.add_element(shape)":
        "Add a shape to the symbol content.",
    "文字元素。":
        "Text element.",
    "估算包围盒（按字号 x 字数近似，精确宽度需渲染后测量）。":
        "Estimate the bounding box from font size times character count; exact width needs rendering.",
    "路径文字元素：文字沿路径排列。":
        "Text-path element: text laid out along a path.",
    "复用元素：引用模板/已定义图形。":
        "Use element: reference a symbol or an already defined shape.",

    # =====================================================================
    # pathkit/editor.py
    # =====================================================================
    "把当前（可能已被拖过的）点序列还原为 d 字符串（不写回路径）。":
        "Rebuild a d string from the current point list without writing back to the path.",
    "把当前点序列写回路径元素（拖点后自动调用，一般不用手动调）。":
        "Write the current point list back to the path element; called automatically after dragging.",
    "路径是否闭合（最后一段是 Z）。示例:: ed.closed":
        "Whether the path is closed, i.e. its last segment is Z.",
    "锚点个数。示例:: ed.anchor_count":
        "Number of anchors.",
    "控制点（调整点）个数。示例:: ed.control_count":
        "Number of control points.",
    "生成可读的路径结构说明（字符串，不打印）。":
        "Build a readable path report as a string, without printing it.",
    "打印路径结构说明（并返回同样内容）。":
        "Print the path report and return the same text.",
    "移动第 index 个锚点到 (x, y)。":
        "Move the anchor at index to (x, y).",
    "移动「第 seg_index 段」的第 ctrl_index 个调整点到 (x, y)。":
        "Move control point ctrl_index of segment seg_index to (x, y).",
    "相对移动锚点。示例:: ed.move_anchor_by(1, 0, -20)":
        "Move an anchor by a relative offset.",
    "批量设置锚点坐标（适合外部算法算好一串新坐标后一次性回填）。":
        "Set all anchor coordinates at once, handy for feeding back computed points.",
    "取出全部控制点坐标。":
        "Return every control-point coordinate.",
    "在第 seg_index 段上插入一个锚点（曲线形状保持不变）。":
        "Insert an anchor on segment seg_index while keeping the curve shape unchanged.",
    "删除一个锚点（把它两侧的直线段合并为一条；曲线段暂不支持）。":
        "Drop an anchor by merging the straight segments on both sides; curved neighbours are not supported yet.",
    "反转路径方向（起终点互换，形状不变）。":
        "Reverse the path direction, swapping start and end while keeping the shape.",
    "以 (cx, cy) 为中心整体缩放所有点（直接改坐标，不是 transform）。":
        "Scale every point about (cx, cy) by rewriting coordinates rather than adding a transform.",
    "导出为可 JSON 序列化的字典（点位存档）。":
        "Export a JSON-serialisable dict of all points.",
    "把路径点位存成 JSON（方便外部工具/脚本批量调点再读回）。":
        "Save the path points as JSON so external tools can tweak and reload them.",
    "读取 JSON 点位并回填到路径（配合 save_json 使用）。":
        "Read JSON points back into the path; pairs with save_json.",
    "在画布上把锚点与调整杆画出来（像钢笔工具那样），方便对照调整。":
        "Draw anchors and handles on the canvas, pen-tool style, so you can check and adjust them.",

    # =====================================================================
    # pathkit/point.py
    # =====================================================================
    "路径上的一个可调点（锚点或控制点）。":
        "A draggable point on a path: an anchor or a control point.",
    "当前坐标 (x, y)。示例:: pt.pos # (120.0, 80.0)":
        "Current position as an (x, y) pair.",
    "当前 x 坐标。示例:: pt.x":
        "Current x coordinate.",
    "当前 y 坐标。示例:: pt.y":
        "Current y coordinate.",
    "把点移动到指定坐标（立即写回路径元素）。":
        "Move the point to a coordinate and write it back to the path immediately.",
    "相对移动（立即写回路径元素）。":
        "Move the point by a relative offset and write it back immediately.",

    # =====================================================================
    # pathkit/segment.py
    # =====================================================================
    "路径中的一段（一个 SVG path 命令，绝对坐标）。":
        "One segment of a path: a single SVG path command in absolute coordinates.",
    "是不是曲线段（三次/二次贝塞尔或圆弧）。":
        "Whether this is a curve segment: cubic, quadratic or arc.",
    "是不是闭合命令 Z。":
        "Whether this is the close command Z.",
    "本段控制点（调整点）个数。":
        "Number of control points in this segment.",
    "返回一行中文说明（打印路径结构时用）。":
        "Return a one-line human-readable description, used in the path report.",
    "本段还原为 d 片段。":
        "Render this segment back to a d fragment.",
    "取本段上参数 t 处（0~1，按线段长度近似）的坐标。":
        "Return the point at parameter t (0-1), approximated by arc length.",
    "圆弧的「端点参数 → 圆心参数」转换（SVG 规范 F.6.5）。":
        "Convert an arc from endpoint parameters to centre parameters, per SVG spec F.6.5.",
    "本段长度（直线精确；曲线按 samples 段折线近似；M/Z 为 0）。":
        "Length of this segment: exact for lines, sampled for curves, zero for M and Z.",
    "本段的包围盒 (min_x, min_y, max_x, max_y)（曲线按采样近似）。":
        "Segment bounding box as (min_x, min_y, max_x, max_y), sampled for curves.",
    "移动本段的一个锚点（起点 index=0，终点 index=1）。":
        "Move one of this segment's anchors: index 0 is the start, 1 the end.",
    "移动本段的一个控制点（调整点）。":
        "Move one of this segment's control points.",
    "在参数 t 处把本段一分为二（新增一个锚点，形状完全不变）。":
        "Split this segment in two at parameter t, adding an anchor without changing the shape.",

    # ---- 模块级函数 / Module-level functions ----
    # 早期版本只双語化了「类 + 类方法」，工具函数整片漏掉，英文页的 API 表
    # 只能回退显示中文。补在这里，bilingualize.py 会自动写回源码。
    '查询中文名称对应的英文版名称。':
        'Look up the English name behind a Chinese one.',
    '迁移中文脚本到英文版（正则批量替换，尽力而为，结果需人工复核）。':
        'Migrate a script that uses Chinese names to the English API with regex rewrites: '
        'best effort, and the result needs a human review.',
    '把枚举成员转换为其值；非枚举原样返回（「枚举 + 字符串」双写法的内部统一入口）。':
        "Return an enum member's value and pass anything else through unchanged; the internal "
        "entry point behind the enum-or-string convention.",
    '注册一个工具包类（内部函数，一般用 @toolkit 装饰器代替）。':
        'Register a toolkit class; internal helper, normally reached through the @toolkit decorator.',
    '校验参数是否为类（内部函数）。':
        'Check that the argument is a class; internal helper.',
    '工具包注册装饰器（推荐用法）。':
        'Toolkit registration decorator; the recommended way to register one.',
    '列出所有已注册工具包名。':
        'List the names of every registered toolkit.',
    '生成字体文件的内嵌 @font-face CSS（把字体 base64 塞进 SVG）。':
        'Build the embedded @font-face CSS for a font file, base64-encoding the font into the SVG.',
    '按实际用到的文字对字体文件做子集化（需要 fontTools），大幅减小内嵌体积。':
        'Subset a font file to the characters actually used (requires fontTools), which shrinks '
        'embedded output a lot.',
    '在系统字体目录中查找字体文件（对应中文版 `字体查找器` 的简化版）。':
        'Find a font file in the system font directories.',
    '把任意语言写法归一成**语言族**（``"en"`` / ``"zh"`` / ``"auto"``）。':
        'Normalise any way of writing a language down to its family: en, zh or auto.',
    '当前**生效**的语言码（已做词条回退，即真正用于取词的那个）。':
        'The language code currently in effect, after message fallback, i.e. the one lookups use.',
    '设置输出语言（全局生效，覆盖环境变量）。':
        'Set the output language globally, taking precedence over the environment variable.',
    '清掉显式设置，回到「环境变量 / 默认英文」的解析结果。':
        'Drop the explicit setting and go back to the environment-variable or default-English result.',
    '当前是否为中文输出。':
        'Whether messages are currently being output in Chinese.',
    '取一条本地化消息并按关键字格式化。':
        'Look up one localised message and format it with keyword arguments.',
    '已注册词条的语言码列表。':
        'The language codes that currently have messages registered.',
    '注册或扩充一种语言的词条（未翻译的词条自动回退到语言族、再回退英文）。':
        'Register or extend the messages of a language; missing keys fall back to the language '
        'family, then to English.',
    '把 d 字符串切成「命令字母 / 数字」记号列表。':
        'Split a d string into a token list of command letters and numbers.',
    '解析 SVG path 的 d 字符串为线段列表（绝对坐标，已展开快捷命令）。':
        'Parse an SVG path d string into segments with absolute coordinates and shortcut '
        'commands expanded.',
    '把线段列表还原为 SVG path 的 d 字符串。':
        'Render a segment list back into an SVG path d string.',
    '反转线段列表（起终点互换、控制点顺序颠倒、圆弧方向取反）。':
        'Reverse a segment list: endpoints swap, control-point order flips and arcs take the '
        'opposite sweep.',
    '数值格式化：保留小数、去掉多余的 0。':
        'Format a number, keeping its decimals and trimming redundant zeros.',
    '把文件大小格式化为易读字符串（如 "88.3 KB"）。':
        'Format a byte count as a readable string such as "88.3 KB".',
    '本地图片转 base64 data URI（内嵌进 SVG，离线可用）。':
        'Turn a local image into a base64 data URI that can be embedded in the SVG and works offline.',
    '获取图片真实宽高（需要 Pillow，读取失败返回 (0, 0)）。':
        "Return an image's real width and height (requires Pillow; returns (0, 0) if unreadable).",
    '读取 SVG 文件的宽高（解析 width/height 或 viewBox）。':
        "Read an SVG file's width and height from its width/height attributes or viewBox.",
    '等比缩放 SVG 文件并另存（对应中文版 `缩放SVG图片`）。':
        'Scale an SVG file proportionally and save the result as a new file.',
    '把 SVG 文件解析为节点组（供绘图板 import_svg_as_group 使用）。':
        "Parse an SVG file into a node group, used by the board's import_svg_as_group.",
    '本机是否装了 cairosvg（英文版新增：用于自动挑选导出引擎）。':
        'Whether cairosvg is available, used to pick the export engine automatically.',
    '用 cairosvg 把 SVG 渲染为 PNG（对应中文版 `生成PNG` 的 cairosvg 方式）。':
        'Render an SVG to PNG with cairosvg.',
    '用 cairosvg 把 SVG 转为 PDF（对应中文版 `生成PDF`）。':
        'Convert an SVG to PDF with cairosvg.',
    '查找本机 Chrome 可执行文件（英文版新增）。':
        'Locate the Chrome executable on this machine.',
    '用 Chrome 无头模式把 SVG 打印为 PDF（英文版新增）。':
        'Print an SVG to PDF using headless Chrome.',
    '用 Chrome 无头模式把 SVG 截图为 PNG（英文版新增，支持 SVG filter）。':
        'Screenshot an SVG to PNG using headless Chrome; SVG filters are supported.',
    '把 PDF 转为 DOCX（需要 pdf2docx 库，对应中文版 `生成DOCX`）。':
        'Convert a PDF to DOCX (requires the pdf2docx library).',
    '计算箭头三角形的三个顶点（对应中文版 `获取箭头路径` 的核心）。':
        'Compute the three vertices of an arrow head triangle.',
    '计算正弦波浪线的采样顶点（对应中文版 `画波浪线` 的核心）。':
        'Sample the vertices of a sine wave line.',
    '正 N 边形顶点（对应中文版 `N边形路径`）。':
        'Vertices of a regular N-sided polygon.',
    'N 角星顶点（外角 + 内角交替，对应中文版 `N角星路径`）。':
        'Vertices of an N-pointed star, alternating outer and inner corners.',
    '爱心曲线顶点（对应中文版 `爱心路径`）。':
        'Vertices of a heart curve.',
    '顶点列表包围盒。':
        'Bounding box of a point list.',
    '创建高斯模糊滤镜定义（对应中文版 `滤镜工具集.模糊滤镜`）。':
        'Create a Gaussian blur filter definition.',
    '创建投影滤镜（英文版新增能力，对应中文版未提供的 drop-shadow）。':
        'Create a drop-shadow filter, which the Chinese edition did not provide.',
    '创建发光滤镜（英文版新增能力）。':
        'Create a glow filter.',
    '估算文字宽度（需要 Pillow 加载系统字体；失败时按 1.0x 字号估算）。':
        'Estimate how wide a text will be using Pillow and a system font, falling back to one em '
        'per character.',
    '在 Windows 字体目录中查找字体文件（对应中文版 `字体查找器` 的简化版）。':
        'Find a font file in the Windows font directory.',
    '文字转路径（对应中文版 `文字转路径`，需要 fontTools 库）。':
        'Convert text into path data (requires the fontTools library).',
}


# ===========================================================================
# 模块级英文标题 / Module-level English titles
# ===========================================================================
# tools/bilingualize.py 把这里的英文插进各模块的文档字符串：
#   · 标题带 ``====`` 下划线的模块 -> 插在下划线之后，作为英文摘要段；
#   · 普通模块 -> 追加到首行末尾，形成「中文标题 / English title」。
# 未列出的模块（如已双语的 i18n.py、由 README 覆盖的 __init__.py）会自动跳过。
MODULE_EN = {
    # ---- board 包 ----
    "malight/board/__init__.py":
        "The MagicPen drawing board, composed from BoardCore plus one mixin per feature file.",
    "malight/board/core.py":
        "BoardCore: canvas setup, element registry, page config, backgrounds, lifecycle hooks and finish().",
    "malight/board/shapes.py":
        "Basic shapes, each method named after its SVG element.",
    "malight/board/paths.py":
        "Paths and connectors: path, polyline, tables, arrows and wave lines.",
    "malight/board/containers.py":
        "Container elements: g, symbol, use, pattern, marker and a.",
    "malight/board/images.py":
        "Images: bitmap <image> placement and SVG import.",
    "malight/board/text_board.py":
        "Text: SVG text, textPath and text-to-path conversion.",
    "malight/board/layout.py":
        "Arranging elements horizontally, vertically, in a grid or around a circle.",
    "malight/board/repeat.py":
        "Repetition: grid, circular and linear.",
    "malight/board/debug.py":
        "Debugging helpers: grids, frames, distance measurements and key points.",
    "malight/board/effects.py":
        "Clipping and masking with SVG clipPath and mask.",
    "malight/board/filters.py":
        "The filter factory behind pen.fx and pen.filter.",
    "malight/board/fx.py":
        "FilterChain, a chainable builder for Photoshop-style filter stacks.",
    "malight/board/gradients_mixin.py":
        "Gradients: SVG linearGradient and radialGradient, plus rainbow and gold shortcuts.",
    "malight/board/style.py":
        "The style helper (pen.style) for CSS classes, the global stylesheet and font embedding.",

    # ---- elements 包 ----
    "malight/elements/__init__.py":
        "The element library: one file per SVG element class.",
    "malight/elements/base.py":
        "The Element base class and the helpers shared by every element.",
    "malight/elements/path.py":
        "PathElement: move / line / curve / arc commands, turtle drawing and boolean operations.",
    "malight/elements/circle.py":
        "CircleElement, created by pen.circle.",
    "malight/elements/ellipse.py":
        "EllipseElement, created by pen.ellipse.",
    "malight/elements/rect.py":
        "RectElement, created by pen.rect.",
    "malight/elements/line.py":
        "LineElement, created by pen.line.",
    "malight/elements/polyline.py":
        "PolylineElement, created by pen.polyline.",
    "malight/elements/polygon.py":
        "PolygonElement, created by pen.polygon.",
    "malight/elements/text.py":
        "TextElement, created by pen.text.",
    "malight/elements/textpath.py":
        "TextPathElement: text laid out along a path.",
    "malight/elements/image.py":
        "ImageElement: a bitmap image.",
    "malight/elements/svgimage.py":
        "SVGImageElement: embed another SVG file as an image.",
    "malight/elements/group.py":
        "GroupElement: bundle elements so they transform and animate together.",
    "malight/elements/symbol.py":
        "TemplateElement: define a reusable symbol.",
    "malight/elements/use.py":
        "UseElement: reference a symbol or an already defined shape.",
    "malight/elements/marker.py":
        "MarkerElement: line-end decorations such as arrowheads.",
    "malight/elements/clippath.py":
        "ClipPathElement: clip-path definitions.",
    "malight/elements/mask.py":
        "MaskElement: control visibility by luminance.",
    "malight/elements/link.py":
        "LinkElement: click the element to open a URL.",
    "malight/elements/pattern.py":
        "PatternElement: tiling fill textures.",

    # ---- pathkit 包 ----
    "malight/pathkit/__init__.py":
        "pathkit: inspect and edit the anchors and control points of a path.",
    "malight/pathkit/editor.py":
        "PathEditor: read the structure, drag anchors and control points, insert or drop points, save point data.",
    "malight/pathkit/parser.py":
        "Parse an SVG path d string into structured segments, and render segments back to d.",
    "malight/pathkit/point.py":
        "PathPoint: a single draggable anchor or control point.",
    "malight/pathkit/segment.py":
        "PathSegment: one SVG path command in absolute coordinates, with geometry helpers.",

    # ---- 顶层模块 ----
    "malight/definitions.py":
        "Colors, fonts, paper sizes and every option enum.",
    "malight/fonts.py":
        "Font enum plus font lookup, embedding and subsetting helpers.",
    "malight/gradients.py":
        "Linear and radial gradient definitions.",
    "malight/svg_backend.py":
        "A tiny SVG element and serialisation backend (internal).",
    "malight/tools.py":
        "Image, export, geometry, filter and font helpers.",
    "malight/ext.py":
        "The extension mechanism: register a third-party toolkit with @toolkit and mount it on a board.",
    "malight/compat.py":
        "Mapping tables and a script migrator from the Chinese API to the English one.",
}
