# -*- coding: utf-8 -*-
"""
示例代码译文表（code_en）
=========================

``tools/bilingualize_code.py`` 用它把各模块 ``__main__`` 示例里的**中文注释**
与**中文文案**补成「中文 / English」双语对；``tools/gen_docs.py`` 生成文档时
再按语言各取一半，于是中文页与英文页各自只有一种语言，而源码里两种语言并存。

Translation table for example code. ``bilingualize_code.py`` injects these English
halves into the ``Chinese / English`` pairs found in each module's ``__main__``
demo, and the docs generator splits them per language afterwards.

约定 / Convention:
    键 = 注释正文（去掉 ``#`` 与其后空白的原文）或字符串字面量的内容，**必须逐字符一致**；
    值 = 英文半边，不带引号、不带 ``#``。
    键里已含 ``" / "`` 双语对形式的片段会被跳过，不需要在这里登记。

    Key   = comment text after ``#`` (whitespace trimmed) or the exact string
            literal content. Values are the English half only.
"""

COMMENT_EN = {
    # ------------------------------------------------------------------
    # elements/base.py
    # ------------------------------------------------------------------
    "底部导入：to_group() 的返回注解引用 GroupElement，而 group.py 又继承本模块的":
        "Bottom import: to_group()'s return annotation names GroupElement, which subclasses",
    "Element —— 顶部互相导入会循环；放到文件末尾（Element 已定义完毕）两个问题都解决，":
        "the Element defined in this module - importing both at the top would cycle; putting it",
    "elements.__init__ 保证 base 先于 group 导入，运行时不会触发循环。":
        "at the bottom solves both. elements.__init__ imports base before group, so no cycle.",
    "输出统一放到项目根的 output/ 目录（从哪运行结果都在同一处）":
        "Output always goes to the project-root output/ directory, wherever you run from",
    "1) 元素由绘图板创建，返回的是「具体类型」，PyCharm 能提示":
        "1) The board creates elements and returns concrete types, so PyCharm completes them",
    "2) 设置 id 后可以反查":
        "2) Give it an id and you can look it up again",
    "3) 几何信息（基类提供，所有元素都有）":
        "3) Geometry, provided by the base class for every element",
    "4) 变换：可链式，返回的仍是 CircleElement":
        "4) Transforms chain and still return a CircleElement",
    "平移": "translate",
    "绕指定点旋转": "rotate around a point",
    "缩放": "scale",
    "5) 局部更新：只改传入的项，几何不受影响":
        "5) Partial update: only the keys you pass change, geometry is untouched",
    "6) 滤镜：一行加特效（pen.fx 是滤镜工厂）":
        "6) Filters: one line per effect (pen.fx is the filter factory)",
    "滤镜效果请用浏览器打开输出 SVG 查看，转 PNG 时 cairosvg 不渲染 filters":
        "Open the SVG in a browser for filter effects; cairosvg does not render them",
    "7) 克隆（同类型；可带偏移与新 id）":
        "7) Clone: same type, with an optional offset and a new id",
    "8) 层级调整：后画的元素在上层，可用它们改遮挡关系":
        "8) Z-order: later elements sit on top; these change the overlap",
    "9) 动画（SMIL，用浏览器打开 SVG 才能看到动）":
        "9) Animation (SMIL; open the SVG in a browser to see it move)",
    "10) 透传自定义 SVG 属性（extra 里的键会原样落成属性）":
        "10) Pass through custom SVG attributes: keys in extra become attributes",
    "11) 删除元素（从画布移除）":
        "11) Remove an element from the canvas",
    "保存 SVG，并打印文件全路径（方便直接复制）":
        "Save the SVG and print the full path, ready to copy",

    # ------------------------------------------------------------------
    # elements/circle.py
    # ------------------------------------------------------------------
    "1) 最简写法：圆心 (x, y) + 半径": "1) Minimal form: centre (x, y) plus radius",
    "2) 空心圆：填充设为 none（等价 Color.TRANSPARENT）":
        '2) Hollow circle: fill "none", the same as Color.TRANSPARENT',
    "3) 枚举化选项：圆头线端 + 虚线预设（不必再记 \"8 4\" 这种魔数）":
        '3) Enum options: round caps and dash presets, no more magic strings like "8 4"',
    "4) 逐边框线偏移：同一虚线不同相位，排在一起像「流动的圈」":
        "4) Dash offset per ring: one dash at different phases looks like a flowing circle",
    "5) 半透明叠色：两圆重叠处颜色更深（CSS 混合模式）":
        "5) Translucent stacking: the overlap darkens (CSS blend mode)",
    "6) 一行加投影滤镜（滤镜需用浏览器打开 SVG 查看）":
        "6) One-line drop shadow (open the SVG in a browser to see filters)",
    "7) 拿回元素做后续处理（update 是局部更新，不会动几何）":
        "7) Keep the element for later use; update is partial and leaves geometry alone",
    "8) 圆 → 路径元素（之后可做布尔运算 / 拖动锚点）":
        "8) Circle to path element, ready for boolean ops or anchor dragging",

    # ------------------------------------------------------------------
    # elements/clippath.py
    # ------------------------------------------------------------------
    "1) 圆形裁剪（一步到位）": "1) A circular clip in one call",
    "2) 矩形裁剪": "2) A rectangular clip",
    "3) 任意形状裁剪：用 PathElement 当裁剪路径（异形头像 / 波浪边）":
        "3) Any shape: use a PathElement as the clip path, for avatars or wavy edges",
    "4) 一个裁剪区域可以作用到多个目标（做成「统一取景框」）":
        "4) One clip region can drive several targets, like a shared viewfinder",

    # ------------------------------------------------------------------
    # elements/ellipse.py
    # ------------------------------------------------------------------
    "1) 标准椭圆：radius=(rx, ry)": "1) Standard ellipse: radius=(rx, ry)",
    "2) 只传一个数值 = 正圆（等价 pen.circle）":
        "2) One number means a circle, the same as pen.circle",
    "3) 旋转椭圆（英文版增强能力，中文原版不支持）":
        "3) Rotated ellipse, an addition of this edition",
    "4) 渐变填充 + 阴影，做「立体药丸」效果":
        "4) Gradient fill plus shadow for a 3D pill look",
    "5) 椭圆同样支持枚举化的描边样式": "5) Ellipses take the same enum stroke styles",
    "6) 局部更新：只改 rx/ry，圆心不变":
        "6) Partial update: rx/ry change, the centre stays",

    # ------------------------------------------------------------------
    # elements/group.py
    # ------------------------------------------------------------------
    "1) 建组：把多个元素装进一个 <g>，统一变换 / 统一加特效":
        "1) Put elements in one <g> for a shared transform or effect",
    "方式一：创建后移入组": "option A: create it, then move it into the group",
    "整组一起投影": "shadow applied to the whole group",
    "2) 组支持嵌套组；append 与 add_element 等价":
        "2) Groups nest; append and add_element are equivalent",
    "组里再放组": "a group inside a group",
    "3) 整组变换 + 整组透明度":
        "3) Transform and opacity for the whole group",
    "4) 组的包围盒（会遍历子元素计算）":
        "4) Group bounding box, computed by walking the children",
    "5) 组内元素可以「取出」：换到画布根（传 pen.canvas_node）":
        "5) Take a child out by reparenting it to the canvas root (pen.canvas_node)",
    "放回画布根": "back to the canvas root",
    "6) 从组里移除元素 / 克隆整个组":
        "6) Remove a child, or clone the whole group",

    # ------------------------------------------------------------------
    # elements/image.py
    # ------------------------------------------------------------------
    "准备一张小图（本地图片会自动 base64 内嵌，SVG 离线也能看）":
        "Prepare a small image; local files are base64-embedded so the SVG works offline",
    "1) 只给宽度：高度按原图比例自动算（保持比例最省心）":
        "1) Width only: the height follows the original ratio",
    "2) 宽高都给：默认 AspectRatio.MEET（完整显示，可能留白）":
        "2) Both given: AspectRatio.MEET fits the whole image, possibly with padding",
    "3) AspectRatio.SLICE：铺满裁切（不变形，会裁掉超出部分）":
        "3) AspectRatio.SLICE fills and crops without distorting",
    "4) 拉伸 + 像素化放大（做像素风 / 放大镜效果）":
        "4) Stretch and pixelated zoom, for retro or magnifier looks",
    "5) 外链引用：不内嵌，SVG 体积小（但看图需联网）":
        "5) External reference: smaller SVG, but the image needs a network",
    "6) 局部更新：只改宽高与透明度，位置和内嵌数据都不动":
        "6) Partial update: only size and opacity change; position and data stay",

    # ------------------------------------------------------------------
    # elements/line.py
    # ------------------------------------------------------------------
    "1) 基本线段：起点 -> 终点": "1) A basic line from start to end",
    "2) 圆头粗线：画「胶囊线」/ 手绘感粗笔画时最常用":
        "2) Thick round-capped line, the usual pick for capsule and hand-drawn strokes",
    "3) 虚线预设（枚举），不用再手写 \"8 4\"":
        '3) Dash presets as enums; no more hand-written "8 4"',
    "4) 虚线相位偏移：同样的虚线错开排列，做「流动/进度」效果":
        "4) Dash offset staggers one dash pattern for flow or progress effects",
    "5) 蚂蚁线流动动画（浏览器打开 SVG 可见）":
        "5) Marching-ants animation, visible in a browser",
    "6) 缩放画布时线宽保持不变（工程图/图标内嵌常需要）":
        "6) Keep the stroke width when the canvas scales, as diagrams and icons need",
    "7) 折角样式：stroke_join 控制两段线的拐角":
        "7) stroke_join controls the corner between two segments",
    "8) 局部更新：只改终点坐标": "8) Partial update: only the end point changes",

    # ------------------------------------------------------------------
    # elements/link.py
    # ------------------------------------------------------------------
    "1) 把任意元素包成链接：圆角按钮":
        "1) Wrap any element in a link: a rounded button",
    "2) 文字链接（加下划线更像链接）":
        "2) A text link, underlined to look clickable",
    "3) 图片 / 图形链接；也可以跳内部锚点（如 \"#top\"）":
        '3) Image or shape links, and in-page anchors such as "#top"',
    "4) 链接元素本身也能加滤镜、改透明度":
        "4) A link element takes filters and opacity too",
    "5) wrap：先建链接再往里塞元素（与 pen.a(el, url) 等价）":
        "5) wrap: create the link, then nest elements (the same as pen.a(el, url))",
    "6) 局部更新：换地址 / 换提示":
        "6) Partial update: change the address or the tooltip",

    # ------------------------------------------------------------------
    # elements/marker.py
    # ------------------------------------------------------------------
    "1) 定义箭头标记（<marker> 放在 <defs> 里，可被多条线复用）":
        "1) Define an arrow marker in <defs> so several lines can share it",
    "ref_x / ref_y 是「参考点」——箭头尖端要对齐线端，所以取 (9, 3)":
        "ref_x / ref_y is the reference point; (9, 3) puts the tip on the line end",
    "orient=\"auto\" 让箭头自动跟随线条方向（画箭头必选）":
        'orient="auto" turns the arrow with the line: what you want for arrow heads',
    "2) 起点用圆点标记": "2) A dot marker at the start",
    "3) 线条上挂标记：marker_end / marker_start 是 SVG 原生属性，":
        "3) marker_end / marker_start are native SVG attributes,",
    "用 extra 直接透传即可": "so pass them through with extra",
    "4) 曲线路径也能挂标记（箭头会顺着切线方向转）":
        "4) Curves take markers too; the arrow follows the tangent",
    "5) marker_units 控制箭头是否随线宽缩放":
        "5) marker_units decides whether the arrow scales with the stroke",
    "\"strokeWidth\"（默认，随线宽） / \"userSpaceOnUse\"（固定像素）":
        '"strokeWidth" scales with the stroke (default), "userSpaceOnUse" is fixed pixels',
    "6) 局部更新：改方向策略或参考点":
        "6) Partial update: change the orientation or the reference point",

    # ------------------------------------------------------------------
    # elements/mask.py
    # ------------------------------------------------------------------
    "1) 黑白渐变当遮罩 → 图片「淡出」效果（做长图渐隐最常用）":
        "1) A black-and-white gradient as a mask fades an image out",
    "2) 圆形遮罩 → 「聚光灯 / 圆形取景」效果":
        "2) A circular mask gives a spotlight or round viewfinder",
    "3) 遮罩自己也可以是一个组（多块形状叠加成遮罩）":
        "3) The mask itself can be a group of overlapping shapes",
    "白底 + 黑条纹 → 目标被「切成条纹」显示":
        "White plus black stripes shows the target as stripes",
    "4) 遮罩也能作用于组（整组一起被遮）":
        "4) A mask can cover a whole group",

    # ------------------------------------------------------------------
    # elements/path.py
    # ------------------------------------------------------------------
    "1) 命令式绘制：移动 / 直线 / 贝塞尔 / 圆弧 / 闭合":
        "1) Command-style drawing: move, line, Bezier, arc, close",
    "起笔": "start",
    "直线": "line",
    "三次贝塞尔（2 个控制点）": "cubic Bezier, two control points",
    "二次贝塞尔（1 个控制点）": "quadratic Bezier, one control point",
    "圆弧": "arc",
    "2) 看结构：每一段的起点 / 调整点 / 终点都能打印出来":
        "2) Inspect the structure: every segment's start, control and end point prints",
    "对应中文版「路径元素」的看点能力":
        "The point inspection the original edition's path element offered",
    "3) 调整：拖动锚点与控制点（改完立刻写回路径，无需手动 apply）":
        "3) Edit: drag anchors and control points, written back to the path at once",
    "所有锚点坐标": "every anchor coordinate",
    "所有贝塞尔控制柄坐标": "every Bezier handle coordinate",
    "直线段没有调整点": "line segments have no control points",
    "拖第 3 个锚点": "drag the third anchor",
    "拖第 1 个调整点": "drag the first control point",
    "也可以按索引直接改": "or address it by index",
    "第 2 段（三次贝塞尔）的第 1 个调整点":
        "the first handle of segment 2, a cubic",
    "4) 结构编辑：加点（形状不变）/ 反转方向 / 点位存档":
        "4) Structure edits: insert a point without changing the shape, reverse, save points",
    "等价于 PathEditor(p)": "the same as PathEditor(p)",
    "在第 1 段中点插入锚点（形状不变）":
        "insert an anchor at the middle of segment 1, shape unchanged",
    "起终点互换": "swap start and end",
    "点位存档": "save the points",
    "5) 可视化：把锚点（方块）与调整杆（线 + 圆点）画出来看":
        "5) Visualise: anchors as squares, handles as lines with dots",
    "6) 几何信息：长度 / 弧长取点 / 包围盒 / 平移所有命令":
        "6) Geometry: length, point at arc length, bounding box, translate every command",
    "7) 更多绘制命令：水平/垂直直线、整圆、平滑连接、圆角":
        "7) More commands: horizontal and vertical lines, full circle, smooth joins",
    "水平线": "horizontal line",
    "垂直线": "vertical line",
    "先定一个点（半径 = 它与圆心的距离）":
        "fix one point first: the radius is its distance to the centre",
    "画整圆": "draw the full circle",
    "8) 填充规则：即使是一条 path 也能用 EVENODD 挖洞（多子路径）":
        "8) Fill rule: EVENODD punches holes using several subpaths in one path",
    "外圈（半径 45）": "outer ring, radius 45",
    "起一条新子路径 = 内圈起点": "a new subpath starts the inner ring",
    "内圈（半径 30）→ 与 EVENODD 配合挖出孔洞":
        "inner ring, radius 30: EVENODD turns it into a hole",
    "9) 布尔运算（两个路径求并/交/差，返回新 PathElement）":
        "9) Boolean ops (union, intersection, difference) return a new PathElement",
    "需要 shapely 等可选依赖": "requires optional dependencies such as shapely",

    # ------------------------------------------------------------------
    # elements/pattern.py
    # ------------------------------------------------------------------
    "1) 斜条纹图案（做背景 / 填充纹理）":
        "1) Diagonal stripe pattern for backgrounds and fills",
    "units 决定坐标基准：USER_SPACE（像素，最直观）":
        "units sets the coordinate basis; USER_SPACE in pixels is the obvious one",
    "2) 圆点图案（波点）": "2) Polka dot pattern",
    "3) 棋盘格图案": "3) Checkerboard pattern",
    "4) 图案可以只作为某条描边/文字的填充，也可以叠加在渐变上":
        "4) A pattern can fill a stroke or text, or sit on top of a gradient",
    "5) 局部更新：只改图案格子尺寸，内容元素不动":
        "5) Partial update: only the tile size changes, the contents stay",
    "6) 提示：图案定义放在 <defs>，用 url(#id) 引用，不会直接显示":
        "6) Pattern definitions live in <defs> and are referenced through url(#id)",

    # ------------------------------------------------------------------
    # elements/polygon.py
    # ------------------------------------------------------------------
    "1) 三角形：给顶点列表即可": "1) A triangle: just give the vertices",
    "2) ★ 带孔多边形：外圈顶点 + 内圈顶点拼在一起 + FillRule.EVENODD":
        "2) ★ Polygon with a hole: outer and inner vertices in one list plus FillRule.EVENODD",
    "这是复刻简笔画「挖洞 / 镂空」最关键的技巧（英文版增强能力）":
        "the key trick for hollowed-out line art",
    "3) 对照：同一批顶点用 NONZERO（默认）就不挖空":
        "3) Compare: the same vertices with NONZERO, the default, stay solid",
    "4) 正多边形系列（内部就是 polygon，多了自动算顶点）":
        "4) Regular polygons: plain polygons with the vertices computed for you",
    "5) 星形与爱心（同样返回 PolygonElement）":
        "5) Stars and hearts, also PolygonElement",
    "6) 钻石形": "6) Diamond",
    "7) 局部更新：只换填充色，顶点不动":
        "7) Partial update: only the fill changes; the vertices stay",

    # ------------------------------------------------------------------
    # elements/polyline.py
    # ------------------------------------------------------------------
    "1) 折线：顶点依次直连，首尾不闭合（不做 Z）":
        "1) Polyline: vertices joined in order, not closed with Z",
    "2) 折线也能填充：SVG 会把首尾自动连起来填充，但描边仍不闭合":
        "2) A polyline can be filled: SVG closes it for the fill, the stroke stays open",
    "3) 用折线围成封闭外形（描边不闭合，适合「开口」造型）":
        "3) Wrap points into a shape: the stroke stays open, which suits open outlines",
    "4) 折线同样支持线端/虚线枚举":
        "4) Polylines take the same cap and dash enums",
    "5) 拿回元素改样式 / 量尺寸":
        "5) Keep the element to restyle or measure it",
    "6) 内部数据也能读出来（顶点列表）":
        "6) The underlying data reads back as a vertex list",

    # ------------------------------------------------------------------
    # elements/rect.py
    # ------------------------------------------------------------------
    "1) 普通矩形": "1) A plain rectangle",
    "2) 圆角矩形 + 投影（UI 卡片最常见）":
        "2) Rounded rectangle with a shadow, the usual UI card",
    "3) 旋转矩形（英文版增强能力）": "3) Rotated rectangle, an addition of this edition",
    "4) 虚线圆角「徽章」+ 混合模式":
        "4) Dashed rounded badge with a blend mode",
    "5) 正方形（rect 的便捷封装）": "5) Square, a convenience wrapper over rect",
    "6) 用「外框 + 内框 + EVENODD」画一个镂空方环（不用布尔运算）":
        "6) Hollow square ring from an outer and an inner rect plus EVENODD",
    "7) 局部更新：只改宽高/圆角": "7) Partial update: only size and corner radius change",

    # ------------------------------------------------------------------
    # elements/svgimage.py
    # ------------------------------------------------------------------
    "先造一个外部 SVG 当素材（示例用；实际项目里放你自己的图）":
        "Build an external SVG to work with: demo only, use your own file in a project",
    "1) 把 SVG 文件当图片贴上去：保持矢量，放大不糊":
        "1) Place an SVG file as an image: still vector, sharp at any size",
    "（内部转成 data:image/svg+xml;base64 内嵌，离线可用）":
        "embedded as data:image/svg+xml;base64, so it works offline",
    "2) 只给位置 = 用 SVG 原始尺寸": "2) Position only: the SVG keeps its original size",
    "3) 缩放 + 透明度 + 滤镜": "3) Scale, opacity and a filter",
    "4) 局部更新：只改尺寸，位置与内嵌数据不动":
        "4) Partial update: only the size changes; position and data stay",
    "5) 想「拆开二次编辑」而不是当图片用 → import_svg_as_group":
        "5) To edit the contents instead, use import_svg_as_group",

    # ------------------------------------------------------------------
    # elements/symbol.py
    # ------------------------------------------------------------------
    "1) 定义模板 <symbol>：只定义不显示（放在 <defs> 里）":
        "1) Define a <symbol> template: definitions only, kept in <defs>",
    "view_box 是模板自己的坐标系，用 <use> 复用时再缩放":
        "view_box is the template's own coordinate system, scaled on each <use>",
    "2) 用 <use> 反复复用：改模板一处，全部实例一起变，体积也小":
        "2) Reuse with <use>: one template edit updates every instance",
    "3) 实例可以各自加滤镜 / 动画 / 变换，互不影响":
        "3) Instances take their own filters, animation and transforms",
    "4) 也可以把「外部 SVG 文件」直接注册成模板复用":
        "4) An external SVG file can be registered as a template too",
    "5) 局部更新：改模板的 viewBox（应谨慎，会改变所有实例的比例基准）":
        "5) Partial update: the template viewBox resets every instance's scaling",

    # ------------------------------------------------------------------
    # elements/text.py
    # ------------------------------------------------------------------
    "字体有三种写法，可以混用": "Three ways to name a font; mix them freely",
    "1) 字体枚举（推荐：有补全、拼错立刻报错，不会静默变默认字体）":
        "1) Font enum: completion while typing and a loud failure on a typo",
    "2) 字体名字符串（任何已安装字体都行）":
        "2) Family name as a string: any installed font works",
    "3) 字体文件路径（自动 base64 内嵌，换电脑也不掉字体）":
        "3) Font file path, base64-embedded so it survives a move",
    "字重 / 斜体 / 修饰线（全部有枚举）":
        "Weight, italic and decoration all have enums",
    "描边空心字 / 字间距 / 词间距":
        "Outlined text, letter spacing and word spacing",
    "word_spacing：词间距（英文排版常用）":
        "word_spacing, usually relevant for Latin text",
    "文字按指定宽度铺满（textLength）+ 垂直对齐":
        "Stretch text to a width with textLength, plus vertical alignment",
    "逐字旋转（做弧形/波浪标题的简易替代）":
        "Rotate character by character: a simple stand-in for arc or wave titles",
    "局部更新：只改字号与颜色，文字内容与位置不变":
        "Partial update: only size and colour change; the text and position stay",

    # ------------------------------------------------------------------
    # elements/textpath.py
    # ------------------------------------------------------------------
    "1) 文字沿「顶点折线」排列（最简单）":
        "1) Text along a polyline of points, the simplest form",
    "2) 引导线也可以直接给 PathElement（曲线更顺滑）":
        "2) The guide can be a PathElement, which curves more smoothly",
    "3) start_offset 控制文字起点（\"0%\" 起 / \"50%\" 居中）":
        '3) start_offset moves the text: "0%" at the start, "50%" centred',
    "4) 圆形路径上排文字（做印章 / 徽标）：":
        "4) Text on a circular path, for stamps and badges:",
    "先 move_to 定一个点，再 circle_to 画整圆（半径 = 两点距离）":
        "move_to one point, then circle_to closes the circle at that radius",
    "5) 局部更新：只改字号/字距，文字与引导线都保留":
        "5) Partial update: only size and spacing change; text and guide stay",
    "也可换文字或换路径（会自动重建内部引用，不会累积节点）":
        "You can also swap the text or the path: internal references are rebuilt",

    # ------------------------------------------------------------------
    # elements/use.py
    # ------------------------------------------------------------------
    "先准备一个模板（也可以来自外部 SVG，见 import_svg_as_symbol）":
        "Prepare a template first (an external SVG works too, see import_svg_as_symbol)",
    "1) 最简复用：反复 <use> 同一个模板":
        "1) Simplest reuse: <use> the same template over and over",
    "2) 只给 x / y：按模板原始尺寸放置":
        "2) x / y only: drawn at the template's original size",
    "3) 每个实例可单独变换、加滤镜、改透明度":
        "3) Each instance takes its own transform, filter and opacity",
    "4) 多个实例可分别做动画（例如依次淡入上浮）":
        "4) Instances animate independently, for example fading in one after another",
    "5) 局部更新：只改尺寸 / 透明度，引用关系不变":
        "5) Partial update: only size and opacity change; the reference stays",

    # ------------------------------------------------------------------
    # fonts.py（模块示例）
    # ------------------------------------------------------------------
    "相对导入需要包上下文，这里补上（正常 import malight.fonts 时不执行）":
        "Relative imports need a package context; only runs when executed directly",
    "--- 1) 纯枚举信息，不依赖绘图板 ---":
        "--- 1) Enum information only, no drawing board needed ---",
    "--- 2) 查找本机字体文件 ---": "--- 2) Find font files on this machine ---",
    "--- 3) 真正画一张图，演示三种字体写法 ---":
        "--- 3) Draw a real canvas showing the three ways to name a font ---",
    "浅色背景，方便看字": "Light background so the text is easy to read",
    "写法一：枚举（推荐）": "Style 1: the enum, recommended",
    "写法二：字体名字符串（任意已安装字体）":
        "Style 2: family name as a string, any installed font",
    "写法三：字体文件路径（自动内嵌进 SVG，换电脑不掉字体）":
        "Style 3: font file path, embedded into the SVG",
    "西文枚举 + 加粗": "Latin font enum, bold",
    "保存 SVG（finish 会打印保存全路径）":
        "Save the SVG; finish prints the full path",

    # ------------------------------------------------------------------
    # i18n.py（模块示例）
    # ------------------------------------------------------------------
    "1) 语言枚举：继承 str，可直接与字符串比较，f-string 得到裸值":
        "1) The language enum subclasses str: compare it with plain strings",
    "2) 归一化：各种写法都能认，认不出的回退英文":
        "2) Normalisation accepts every spelling and falls back to English",
    "3) 默认语言是英文，且支持环境变量覆盖":
        "3) English by default, with the environment variable overriding it",
    "4) 同一句话，两种语言：导出信息 + 报错提示":
        "4) The same message in both languages: export info and an error",
    "6) use_language：临时切换，退出后自动恢复（测试/文档生成很有用）":
        "6) use_language switches temporarily and restores on exit",
    "7) 扩展一种自己的语言；没翻的词条自动回退英文":
        "7) Add your own language; untranslated keys fall back to English",
    "8) 复位：回到「环境变量 / 默认英文」":
        "8) Reset: back to the environment variable or default English",

    # ------------------------------------------------------------------
    # pathkit/editor.py
    # ------------------------------------------------------------------
    "1) 先造一条路径：起笔 M -> 直线 L -> 三次贝塞尔 C -> 二次贝塞尔 Q":
        "1) Build a path: move M, line L, cubic C, quadratic Q",
    "段号依次是 0(M) / 1(L) / 2(C) / 3(Q)":
        "the segment numbers are 0(M), 1(L), 2(C), 3(Q)",
    "2) 构造编辑器：PathEditor(p) 与 p.editor() 完全等价":
        "2) PathEditor(p) and p.editor() are the same thing",
    "读统计信息：段数 / 锚点数 / 调整点数 / 是否闭合":
        "read the counts: segments, anchors, control points, closed or not",
    "3) 看结构：describe() 返回字符串，report 是它的别名，":
        "3) describe() returns a string and report is its alias,",
    "print_report() 打印并返回同样内容（三选一即可）":
        "print_report() prints it and returns the same text; pick any one",
    "别名，内容一致": "an alias, same content",
    "想直接打印时用 ed.print_report()": "use ed.print_report() to print it directly",
    "4) 看点位：锚点 / 调整点的纯坐标列表（便于打印或丢给外部算法）":
        "4) Plain coordinate lists for anchors and control points",
    "5) 拖点：锚点按序号拖（支持负数），调整点必须先知道哪几段是曲线":
        "5) Drag anchors by index, negatives allowed; control points need curve indices",
    "直线段没有调整点，move_control 传错段号会给出明确提示":
        "line segments have no control points; a wrong index raises a clear error",
    "例：[2, 3]": "e.g. [2, 3]",
    "把起点拖到 (70,310)": "drag the start anchor to (70,310)",
    "-1 = 最后一个锚点": "-1 means the last anchor",
    "相对移动：上移 15": "move relatively: 15 upwards",
    "第 1 条曲线的第 1 个调整点": "the first control point of the first curve",
    "6) 批量设置锚点坐标（外部算法算好一串新坐标后一次性回填）":
        "6) Set several anchor coordinates at once, after an external algorithm computed them",
    "7) 加点：在曲线上插入一个锚点，**形状保持不变**":
        "7) Insert an anchor on a curve without changing its shape",
    "8) 删点：只对「两侧都是直线段」的拐点有效（曲线请改调整点来简化）":
        "8) Remove only corners between two line segments; simplify curves via handles",
    "去掉中间那个拐点，两条直线合并":
        "drop the middle corner so the two lines merge",
    "9) 反转方向（起终点互换，形状不变）+ 整体缩放（直接改坐标，不是 transform）":
        "9) Reverse the direction, then scale by rewriting coordinates, not by a transform",
    "10) 存档：to_dict() 拿可 JSON 化的数据 → save_json() 落盘 →":
        "10) Persist: to_dict() gives JSON-ready data, save_json() writes it,",
    "外部随便改 → load_json() 读回并立即写回路径":
        "edit it anywhere, load_json() reads it back into the path",
    "模拟外部算法改动": "simulate an external edit",
    "读回并应用到路径": "read it back and apply it",
    "11) 手动重解析：外部直接改过 d 串后，让编辑器重新读一遍":
        "11) Re-parse manually after something else changed the d string",
    "12) apply() / apply_structure()：拖点会**自动**写回，一般不用手动调；":
        "12) Dragging writes back automatically; apply() is rarely called by hand;",
    "apply_structure() 用于结构变化后重建点列表（加点/删点/反转已自动调用）":
        "apply_structure() rebuilds the point list after structural edits",
    "13) 可视化：把锚点（方块）+ 调整杆（线）+ 调整点（圆点）画在画布上":
        "13) Draw anchors as squares, handles as lines and control points as dots",
    "labels=True 时还会标出锚点序号，方便对照微调":
        "labels=True also numbers the anchors for fine-tuning",

    # ------------------------------------------------------------------
    # pathkit/point.py
    # ------------------------------------------------------------------
    "0) 准备一条路径（每段都给足锚点与调整点）":
        "0) Prepare a path whose segments have anchors and control points",
    "1) 锚点对象：常用属性一览": "1) Anchor objects: the everyday attributes",
    "pos=(x,y)  x/y=单轴  kind=类型  index=序号  role=中文角色":
        "pos=(x,y), x/y single axis, kind, index and role",
    "repr 是中文短描述，print 列表时很直观":
        "repr is a short readable description, handy when printing lists",
    "2) 控制点对象：额外带 seg_index / ctrl_index（属于第几段的第几个柄）":
        "2) Control points also carry seg_index / ctrl_index",
    "3) 解包：点对象可以直接 x, y = pt（省去 .pos）":
        "3) Unpack a point: x, y = pt, no .pos needed",
    "4) 拖点：move_to 绝对移动、move_by 相对移动，都会立即写回路径":
        "4) move_to and move_by both write straight back to the path",
    "返回 self，所以可以链式连续拖": "they return self, so drags chain",
    "再下移 15": "then move down another 15",
    "调整点：改变曲线弧度": "a control point changes the curvature",
    "5) 控制点也可以按「第几段第几个」精确定位（与编辑器 move_control 等价）":
        "5) Address a control point by segment and index, like editor move_control",
    "6) 相等与哈希：同坐标同类型的点视为相等；点对象可放进 set / dict":
        "6) Same coordinates and kind mean equal points, so sets and dicts work",
    "7) 可视化：把这些点画出来，序号与坐标一一对应，方便照着手动微调":
        "7) Draw the points, numbered to match, for manual fine-tuning",

    # ------------------------------------------------------------------
    # pathkit/segment.py
    # ------------------------------------------------------------------
    "1) 解析与段的基本信息": "1) Parsing and basic segment information",
    "parse_path_d 会把 H/V/S/T 等快捷命令展开、相对命令转成绝对坐标，":
        "parse_path_d expands shortcuts like H/V/S/T and makes relative commands absolute,",
    "所以下标 0 恒为起笔的 M 段，之后每段都带明确的起点/终点/调整点。":
        "so index 0 is always the starting M and every later segment has explicit points.",
    "由 s 展开来的三次贝塞尔": "the cubic expanded from s",
    "2) describe() / to_d() / repr：一行中文说明、还原 d 片段、调试短描述":
        "2) describe() / to_d() / repr: one-line description, d fragment, debug repr",
    "注意段号：0=M(h 之前) 1=L(h100) 2=L(v50) 3=C(s... 展开) 4=Q 5=A 6=Z":
        "note the numbers: 0=M, 1=L(h100), 2=L(v50), 3=C(expanded), 4=Q, 5=A, 6=Z",
    "3) 几何计算：弧长取点 / 段长 / 包围盒（全部按弧长参数化，定位准）":
        "3) Geometry: point at arc length, length and bbox, all arc-length based",
    "4) 改点：set_anchor（起点 index=0 / 终点 index=1）、set_control":
        "4) set_anchor (index 0 start, 1 end) and set_control",
    "直接改本段坐标，返回 self，可链式":
        "they change this segment's coordinates and return self",
    "注意：段级 to_d() 只输出本段命令（不含起笔 M），要整条路径的 d 串":
        "note: a segment's to_d() emits only its own command, without the leading M;",
    "请用 segments_to_d([...]) 拼装。": "use segments_to_d([...]) for the whole path",
    "5) split()：在 t 处一分为二，新增一个锚点且**形状完全不变**":
        "5) split() cuts a segment at t, adding an anchor with the shape unchanged",
    "直线段、C、Q 都支持；圆弧暂不支持（会抛 NotImplementedError）":
        "lines, C and Q are supported; arcs raise NotImplementedError",
    "6) 圆弧：params 存 (rx, ry, rot, large_arc, sweep)，arc_center() 求圆心":
        "6) Arcs keep (rx, ry, rot, large_arc, sweep); arc_center() gives the centre",
    "7) 直接构造 PathSegment（自己算好坐标时用，不需要画板）":
        "7) Build a PathSegment directly when you already have the coordinates",
}


STRING_EN = {
    # ------------------------------------------------------------------
    # 顶层模块
    # ------------------------------------------------------------------
    "用法: python -m malight.compat <旧脚本.py> [新脚本.py]":
        "Usage: python -m malight.compat <old_script.py> [new_script.py]",

    # ------------------------------------------------------------------
    # elements/base.py
    # ------------------------------------------------------------------
    "Element 基类：所有元素的共同能力":
        "Element base class: capabilities shared by every element",
    "元素类型:": "element type:",
    "按 id 反查同一个对象:": "looked up by id, same object:",
    "包围盒 bbox:": "bounding box:",
    "中心点:": "centre:",
    "宽高:": "size:",
    "克隆体类型:": "clone type:",

    # ------------------------------------------------------------------
    # elements/circle.py
    # ------------------------------------------------------------------
    "圆的包围盒:": "circle bbox:",
    "圆心:": "centre:",
    "圆转路径 d =": "circle as path d =",

    # ------------------------------------------------------------------
    # elements/clippath.py
    # ------------------------------------------------------------------
    "裁剪（clipPath）：只显示裁剪形状内部的内容":
        "Clipping: only what is inside the clip shape shows",
    "圆形裁剪": "circle clip",
    "矩形裁剪": "rect clip",
    "裁剪元素 id:": "clip element id:",
    "异形裁剪": "custom clip",
    "提示：裁剪形状本身会被移入 <defs>，不会显示在画布上":
        "Note: the clip shape itself moves into <defs> and is not drawn",

    # ------------------------------------------------------------------
    # elements/ellipse.py
    # ------------------------------------------------------------------
    "旋转椭圆 bbox:": "rotated ellipse bbox:",
    "更新后椭圆的宽高:": "ellipse size after update:",

    # ------------------------------------------------------------------
    # elements/group.py
    # ------------------------------------------------------------------
    "组内元素数:": "children in group:",
    "嵌套组": "nested group",
    "统一旋转 / 统一透明": "shared rotation and opacity",
    "组的 bbox:": "group bbox:",
    "组中心:": "group centre:",
    "取出后组内元素数:": "children left in the group:",
    "克隆组的 id:": "cloned group id:",

    # ------------------------------------------------------------------
    # elements/image.py
    # ------------------------------------------------------------------
    "用标准库生成一张纯色 PNG（示例自备素材，避免依赖 Pillow）。":
        "Build a solid-colour PNG with the standard library, so the demo needs no Pillow.",
    "只给宽，自动算出的高:": "width only, computed height:",
    "MEET 完整显示": "MEET, whole image",
    "SLICE 铺满裁切": "SLICE, filled and cropped",
    "图片包围盒:": "image bbox:",

    # ------------------------------------------------------------------
    # elements/line.py
    # ------------------------------------------------------------------
    "线包围盒:": "line bbox:",
    "更新后线 d/坐标:": "line d/coords after update:",

    # ------------------------------------------------------------------
    # elements/link.py
    # ------------------------------------------------------------------
    "链接元素 <a>：点元素即可跳转（用浏览器打开 SVG 时生效）":
        "Link element <a>: clicking it navigates, in a browser",
    "点我": "Click me",
    "打开 Python 官网": "Open the Python website",
    "外部链接示例": "external link demo",
    "链接 href:": "link href:",
    "点这里访问文档": "Read the docs here",
    "Python 文档": "Python docs",
    "回到顶部": "Back to top",
    "示例": "demo",
    "另一个链接": "another link",
    "第二个链接 href:": "second link href:",
    "换成 Python 官网": "back to the Python website",
    "更新后 href:": "href after update:",

    # ------------------------------------------------------------------
    # elements/marker.py
    # ------------------------------------------------------------------
    "箭头线 marker-end =": "arrow line marker-end =",
    "箭头方向:": "arrow orientation:",

    # ------------------------------------------------------------------
    # elements/mask.py
    # ------------------------------------------------------------------
    "遮罩（mask）：白色显示、黑色隐藏、灰色半透明":
        "Masking: white shows, black hides, grey is translucent",
    "遮罩元素 id:": "mask element id:",
    "渐变遮罩（右淡出）": "gradient mask, fading right",
    "圆形遮罩（聚光灯）": "circle mask, spotlight",
    "条纹遮罩（条纹显示）": "stripe mask",

    # ------------------------------------------------------------------
    # elements/path.py
    # ------------------------------------------------------------------
    "锚点:": "anchors:",
    "调整点:": "control points:",
    "带调整点的段号:": "segments with control points:",
    "路径长度 ≈ %.2f": "path length ≈ %.2f",
    "弧长 30%% 处坐标:": "point at 30%% of arc length:",
    "包围盒:": "bounding box:",
    "布尔并集结果 d 长度:": "union result d length:",
    "布尔运算需要可选依赖，跳过:": "boolean ops need an optional dependency, skipping:",

    # ------------------------------------------------------------------
    # elements/pattern.py
    # ------------------------------------------------------------------
    "带图案填充的文字": "text with a pattern fill",
    "波点字": "polka dot text",
    "图案 width/height:": "pattern width/height:",
    "图案元素都放在 <defs> 中，用 url(#id) 引用":
        "Pattern elements live in <defs> and are referenced with url(#id)",

    # ------------------------------------------------------------------
    # elements/polygon.py
    # ------------------------------------------------------------------
    "多边形包围盒:": "polygon bbox:",
    "evenodd 的取值是:": "evenodd resolves to:",

    # ------------------------------------------------------------------
    # elements/polyline.py
    # ------------------------------------------------------------------
    "折线包围盒:": "polyline bbox:",
    "折线顶点串:": "polyline points:",
    "顶点列表:": "vertices:",
    "(见 node.attribs)": "(see node.attribs)",

    # ------------------------------------------------------------------
    # elements/rect.py
    # ------------------------------------------------------------------
    "卡片": "Card",
    "徽章 bbox:": "badge bbox:",
    "更新后矩形宽高:": "rect size after update:",

    # ------------------------------------------------------------------
    # elements/svgimage.py
    # ------------------------------------------------------------------
    "SVG 图元素 bbox:": "SVG image bbox:",
    "更新后 bbox:": "bbox after update:",
    "导入为组后的节点数:": "nodes after importing as a group:",
    "导入为组后 bbox:": "bbox after importing as a group:",

    # ------------------------------------------------------------------
    # elements/svggroup.py
    # ------------------------------------------------------------------
    "用到的颜色:": "colours used:",
    "换色后:": "after recolouring:",
    "组内容的包围盒:": "bounding box:",
    "内容节点:": "content nodes:",
    "移动后包围盒:": "bbox after moving:",

    # ------------------------------------------------------------------
    # elements/symbol.py
    # ------------------------------------------------------------------
    "模板 id:": "template id:",

    # ------------------------------------------------------------------
    # elements/text.py
    # ------------------------------------------------------------------
    "① 字体枚举 Font.SIMHEI": "(1) font enum Font.SIMHEI",
    "② 字体名字符串 Microsoft YaHei": "(2) family name string Microsoft YaHei",
    "③ 字体文件内嵌（楷体）": "(3) embedded font file KaiTi",
    "③ 未找到楷体文件，跳过": "(3) KaiTi file not found, skipping",
    "字重 W900 + 斜体": "weight W900 and italic",
    "下划线 underline": "underline",
    "删除线 line-through": "line-through",
    "描边空心字": "outlined text",
    "用 text_length 把文字拉到 460px 宽": "text stretched to 460px with text_length",
    "逐字旋转": "per-character rotation",
    "局部更新演示": "partial update demo",
    "文字包围盒(估算):": "text bbox (estimated):",
    "当前 font-size:": "current font-size:",

    # ------------------------------------------------------------------
    # elements/textpath.py
    # ------------------------------------------------------------------
    "沿折线排列的文字": "text along a polyline",
    "沿三次贝塞尔曲线流动的文字（力度顺着曲线走）":
        "text flowing along a cubic Bezier",
    "start_offset=50% 从中间开始写": "start_offset=50% starts in the middle",
    "· 沿圆环排列的文字 ·": "· text around a circle ·",
    "提示：引导路径自动放进 <defs>，本身不会显示在画布上":
        "Note: the guide path moves into <defs> and is not drawn",
    "换一段文字": "replacement text",
    "textPath 子节点数:": "textPath children:",
    "| 文字:": "| text:",

    # ------------------------------------------------------------------
    # elements/use.py
    # ------------------------------------------------------------------
    "复用元素引用:": "reused element reference:",
    "复用元素 bbox:": "reused element bbox:",

    # ------------------------------------------------------------------
    # fonts.py
    # ------------------------------------------------------------------
    "=== 字体枚举 ===": "=== font enums ===",
    "枚举成员数：": "enum members: ",
    "是字体文件吗：": "is it a font file: ",
    "\\n=== 本机字体查找 ===": "\\n=== local font lookup ===",
    "枚举 Font.SIMHEI（黑体）": "enum Font.SIMHEI",
    "字符串 font='Microsoft YaHei'": "string font='Microsoft YaHei'",
    "字体文件（已 base64 内嵌）": "font file (base64-embedded)",
    "本机未找到楷体文件，跳过示例": "KaiTi not found on this machine, skipping",

    # ------------------------------------------------------------------
    # i18n.py
    # ------------------------------------------------------------------
    "已内置语言  :": "built-in languages :",
    "[malight] {kind} 匯出成功{tail}-> {path}  [{size}]":
        "[malight] {kind} export OK{tail} -> {path}  [{size}]",
    "大小未知": "size unknown",
    "未翻译回退  :": "untranslated fallback :",
    "  <- 回退英文": "  <- fell back to English",
    "现在语言集  :": "languages now :",
    "reset 后    :": "after reset   :",

    # ------------------------------------------------------------------
    # pathkit/editor.py
    # ------------------------------------------------------------------
    "段数:": "segments:",
    "| 锚点数:": "| anchors:",
    "| 调整点数:": "| control points:",
    "| 是否闭合:": "| closed:",
    "锚点坐标:": "anchor coordinates:",
    "调整点坐标:": "control point coordinates:",
    "拖动后 d:": "d after dragging:",
    "加点后锚点数:": "anchors after inserting:",
    "删点前:": "before removing:",
    "删点后:": "after removing:",
    "反转+缩放后:": "after reversing and scaling:",
    "存档字典键:": "saved dict keys:",
    "读回后 d:": "d after loading back:",
    "reload 后段数:": "segments after reload:",
    "apply 后锚点数:": "anchors after apply:",

    # ------------------------------------------------------------------
    # pathkit/parser.py
    # ------------------------------------------------------------------
    "=== 1) 解析（含相对命令 / 快捷命令展开）===":
        "=== 1) parse, with relative commands and shortcuts expanded ===",
    "\\n=== 2) 还原为 d 串（H/V/S/T 已展开为 L/C/Q，坐标等价）===":
        "\\n=== 2) back to a d string, H/V/S/T expanded to L/C/Q with equal coordinates ===",
    "\\n=== 3) 反转路径方向 ===": "\\n=== 3) reverse the path direction ===",
    "   原:": "   before:",
    "   后:": "   after:",
    "\\n=== 4) 曲线取点（弧长参数化，用于定位/测长）===":
        "\\n=== 4) points on a curve, arc-length parameterised ===",
    "   曲线长度 ≈ %.2f": "   curve length ≈ %.2f",
    "   1/4 处坐标:": "   point at 1/4:",

    # ------------------------------------------------------------------
    # pathkit/point.py
    # ------------------------------------------------------------------
    "=== 锚点 ===": "=== anchors ===",
    "=== 调整点 ===": "=== control points ===",
    "解包第 1 个锚点:": "first anchor unpacked:",

    # ------------------------------------------------------------------
    # pathkit/segment.py
    # ------------------------------------------------------------------
    "把坐标打印成 (x, y) 两位小数的样子。":
        "Print coordinates as (x, y) with two decimals.",
    "=== 1) 解析结果（共 %d 段）===": "=== 1) parsed (%d segments) ===",
    "\\n=== 2) 单段说明 ===": "\\n=== 2) one segment described ===",
    "  起点/终点:": "  start/end:",
    "  调整点   :": "  controls :",
    "  是否曲线:": "  is curve:",
    " 是否闭合段:": " is closed:",
    "\\n=== 3) 几何计算（三次贝塞尔 0,0 -> 100,0）===":
        "\\n=== 3) geometry (cubic from 0,0 to 100,0) ===",
    "  曲线长度 ≈ %.2f": "  curve length ≈ %.2f",
    "  包围盒     :": "  bbox     :",
    "\\n=== 4) 改点 ===": "\\n=== 4) edit points ===",
    "  改后 d:": "  d after:",
    "  整条路径:": "  whole path:",
    "\\n=== 5) 拆分 ===": "\\n=== 5) split ===",
    "  前半段:": "  first half:",
    "  后半段:": "  second half:",
    "  拼回去:": "  rejoined:",
    "  直线拆分:": "  line split:",
    "\\n=== 6) 圆弧 ===": "\\n=== 6) arc ===",
    "  圆心:": "  centre:",
    "| 半径 50 → 圆心应在弧的垂直平分线上":
        "| radius 50 -> the centre sits on the perpendicular bisector",
    "  弧长 ≈ %.2f （半圆）": "  arc length ≈ %.2f (half circle)",
    "\\n=== 7) 直接构造 ===": "\\n=== 7) constructed by hand ===",
    "  自建路径:": "  hand-built path:",
    "  第 3 段类型/调整点数:": "  segment 3 kind / control count:",
}
