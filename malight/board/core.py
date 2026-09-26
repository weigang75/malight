# -*- coding: utf-8 -*-
"""
BoardCore —— MagicPen 核心。 / BoardCore: canvas setup, element registry, page config, backgrounds, lifecycle hooks and finish().

画布初始化/元素注册/页面配置/背景/生命周期钩子/finish 保存与
PNG、PDF、DOCX 导出。绘图方法分布在同目录各 Mixin 文件中。

本文件只包含 BoardCore 一个类（Mixin），由 board/__init__.py 组合进 MagicPen。
"""

import os
from typing import Any, Optional, TypeVar
from ..svg_backend import SvgNode, fmt_num
from ..definitions import (Color, PaperSize, PaperSettings,
    StrokeCap, StrokeJoin, ArrowStyle, PointStyle, TextHAlign, TextVAlign,
    GridRepeatType, CoordUnits, PNGMode, PDFMode, DOCXMode, SystemFont,
    FontEmbed, ImageEmbed)
from ..elements import (Element, CircleElement, EllipseElement, RectElement,
    LineElement, PolylineElement, PolygonElement, TextElement, TextPathElement,
    ImageElement, SVGImageElement, GroupElement, TemplateElement, UseElement,
    MarkerElement, ClipPathElement, MaskElement, LinkElement, PatternElement,
    _paint, _fmt_points)
from .. import tools
from .filters import FilterAPI
from .style import StyleAPI
from ..i18n import t


# 绘图板自类型：返回 self 的方法标注 _Pen，
# 子类 MagicPen 调用时 IDE 能推导出准确类型
_Pen = TypeVar("_Pen", bound="MagicPen")


# 绘图方法把「签名之外的参数」收进 extra 传给元素。这些键在元素侧有标准
# 参数名（枚举化选项 / 元素专有参数），创建元素时会被提到顶层，
# 保证落成 stroke-linecap、preserveAspectRatio 之类的规范属性名。
_EXTRA_PARAM_KEYS = {
    # 公共样式
    "opacity", "fill_opacity", "stroke_opacity", "class_name", "style_str",
    "vector_effect", "blend_mode", "filter",
    # 画笔（填充 / 描边）
    "fill_color", "stroke_color", "stroke_width", "stroke_style",
    "dash_offset", "stroke_cap", "stroke_join", "fill_rule",
    # 图像专有
    "aspect", "rendering", "external",
    # 文字专有
    "font", "font_size", "bold", "italic", "underline", "weight",
    "decoration", "letter_spacing", "word_spacing", "h_align", "v_align",
    "char_rotate", "text_length", "length_adjust",
    # 绘制顺序（先描边）
    "paint_order",
}


class BoardCore:
    """
    BoardCore —— MagicPen 核心类（Mixin）。 / BoardCore - the MagicPen core class (a mixin).

    包含：画布初始化、元素注册与反查、页面/配置、背景色、
    生命周期钩子、finish() 保存、export_png/pdf/docx 导出。
    """

    def __init__(self, file_path, width=None, height=None, view_box=None,
                 fonts=None, images=None):
        """
        :param file_path: 保存的 SVG 文件路径（不带 .svg 后缀会自动补全）；
                          相对路径会存到 ``./output/`` 目录（自动创建，
                          修复原版强制要求手工建「输出文件」目录的问题）
        :param width: 画布宽（默认 1000）
        :param height: 画布高（默认 1000）
        :param view_box: SVG viewBox 字符串，如 "0 0 800 600"
        :param fonts: 字体嵌入方式 FontEmbed.SUBSET（默认）/ EMBED / LINK
                      —— 见 :meth:`set_embed`
        :param images: 图片嵌入方式 ImageEmbed.EMBED（默认）/ LINK

        示例::
            pen = MagicPen("poster", width=1080, height=1920)
            pen = MagicPen("poster", fonts="link", images="link")   # 文件最小
        """
        self._registry = {}         # id -> 元素 反查表
        self._filter_chains = {}    # 滤镜 id -> FilterChain（元素的 filter 属性可反查回链）
        self._id_no = 0
        if height is None:
            height = 1000
        if width is None:
            width = 1000
        if not str(file_path).lower().endswith(".svg"):
            file_path = str(file_path) + ".svg"
        if not os.path.isabs(file_path):
            # 相对路径 → ./output/ 目录（自动创建，修复原版痛点）
            out_dir = os.path.join(os.getcwd(), "output")
            os.makedirs(out_dir, exist_ok=True)
            file_path = os.path.join(out_dir, file_path)

        self.file_path = file_path
        self.width, self.height = width, height
        # 页面设置（PageSetup）：设在这里，之后每次 export_pdf 都用；
        # 也可以临时用 export_pdf(page=...) 覆盖。只对 Chrome 引擎生效。
        self.page = None

        # 根节点与 defs
        self.root_node = SvgNode("svg", {
            "xmlns": "http://www.w3.org/2000/svg",
            "xmlns:xlink": "http://www.w3.org/1999/xlink",
            "version": "1.1",
            "width": width,
            "height": height,
        })
        if view_box:
            self.root_node.set("viewBox", view_box)
        self.defs_node = SvgNode("defs")
        self.root_node.add(self.defs_node)
        self.canvas_node = SvgNode("g", {"id": "canvas"})   # 画布图层
        self.root_node.add(self.canvas_node)
        self._debug_nodes = []      # 调试元素最后统一追加（保持在最上层）

        Element._id_counter = 0
        self._configs = {}
        self._js = []

        # 资源嵌入方式（英文版新增，见 set_embed）：字体默认按用字自动子集化，
        # 图片默认 base64 内嵌 —— 都内嵌，但尽量小。
        self.font_embed = str(fonts) if fonts is not None else FontEmbed.SUBSET
        self.image_embed = str(images) if images is not None else ImageEmbed.EMBED

        # 便捷子工具（对应中文版 board.滤镜 / board.变换 等）
        self.filter = FilterAPI(self)
        self.fx = self.filter        # 短名别名（推荐）：pen.fx.shadow(...)
        self.style = StyleAPI(self)

    # ------------------------------------------------------------------
    # 元素注册与查找
    # ------------------------------------------------------------------

    def _gen_id(self, prefix) -> str:
        """生成自增 id（内部方法）。"""
        self._id_no += 1
        return f"{prefix}_{self._id_no}"

    def get_element(self, id_) -> "Optional[Element]":
        """
        按 id 获取元素（对应中文版 `获取元素`）。 / Fetch an element by id.

        示例::
            pen.circle(0, 0, 5, id_="sun")
            pen.get_element("sun")
        """
        return self._registry.get(id_)

    def _register(self, id_, el) -> None:
        """注册元素到反查表（内部方法）。"""
        if id_:
            self._registry[id_] = el

    def _new(self, cls, parent=None, **kw) -> "Element":
        """创建元素并注册（内部统一入口）。parent=None 时交给元素自行决定挂载点（如 defs 类元素）。"""
        # extra 归位：把「有标准参数名」的键提为顶层参数（元素内部按规范属性处理），
        # 其余键仍留在 extra 中作为裸 SVG 属性透传。
        extra = kw.get("extra")
        if extra:
            plain = {}
            for k, v in extra.items():
                if k in _EXTRA_PARAM_KEYS:
                    kw.setdefault(k, v)
                else:
                    plain[k] = v
            kw["extra"] = plain or None
        if parent is not None:
            el = cls(self, parent=parent, **kw)
        else:
            el = cls(self, **kw)
        id_ = el.node.attribs.get("id")
        self._register(id_, el)
        return el

    @staticmethod
    def _opts(extra, **opts):
        """
        把「可选的枚举类样式参数」并入 extra（值为 None 的忽略）。

        供各绘图方法把 ``stroke_cap=`` 这类显式参数统一往下传。

        示例（内部）::
            extra = self._opts(extra, stroke_cap=stroke_cap, fill_rule=fill_rule)
        """
        for k, v in opts.items():
            if v is not None:
                extra[k] = v
        return extra or None

    # ------------------------------------------------------------------
    # 页面与配置
    # ------------------------------------------------------------------

    def page_setup(self, settings) -> None:
        """
        页面打印设置（对应中文版 `页面设置`）。 / Configure page and print settings.

        示例::
            from malight import PaperSettings
            pen.page_setup(PaperSettings(margin_top=10, margin_left=10))
        """
        self._paper = settings

    def set_config(self, name, data) -> None:
        """
        保存配置项（对应中文版 `增加配置项`）。 / Store a config entry.

        示例::
            pen.set_config("author", "Zhang")
        """
        self._configs[name] = data

    def get_config(self, name) -> "Any":
        """
        读取配置项（对应中文版 `获取配置项`）。 / Read a config entry.

        示例::
            pen.get_config("author")
        """
        return self._configs.get(name)

    def use_toolkit(self, *names) -> None:
        """
        挂载扩展工具包（英文版新增，配合 malight.ext 扩展机制）。 / Mount an extension toolkit, used with the malight.ext mechanism.

        第三方包用 ``@malight.ext.toolkit("名字")`` 注册后，
        即可用本方法把其全部公开方法挂到当前绘图板上。

        :param names: 工具包注册名（可一次传多个）

        示例::
            import my_charts            # 内部有 @ext.toolkit("charts")
            pen = MagicPen("report")
            pen.use_toolkit("charts")   # 挂载
            pen.bar_chart([3, 7, 5], 100, 100, 400, 300)   # 调用扩展方法
        """
        from .. import ext
        for name in names:
            ext._bind(self, name)

    def resize(self, width=None, height=None) -> _Pen:
        """
        修改画布大小（对应中文版 `修改绘图板大小`）。 / Resize the canvas.

        示例::
            pen.resize(width=1200, height=900)
        """
        if width is not None:
            self.width = width
            self.root_node.set("width", width)
        if height is not None:
            self.height = height
            self.root_node.set("height", height)
        return self

    # ------------------------------------------------------------------
    # 裁剪 / 遮罩
    # ------------------------------------------------------------------

    def set_embed(self, fonts=None, images=None) -> _Pen:
        """
        设置「资源嵌入方式」（英文版新增）：字体与图片要不要写进 SVG。 / Choose how fonts and images are written into the SVG (English-edition addition).

        本地字体文件 / 本地图片默认都是**内嵌**的（SVG 自带资源、换电脑不掉）。
        这两个开关让你按需选择：

        * ``fonts=FontEmbed.SUBSET``（默认）—— 只内嵌画面上**实际用到的字**，
          11 MB 的中文字体通常能降到几 KB，同时仍然随 SVG 走、换电脑不掉字；
          没装 fontTools 时自动退回整份内嵌（宁可变大也不掉字）。
        * ``fonts=FontEmbed.EMBED`` —— 整份字体 base64 内嵌（最保险）。
        * ``fonts=FontEmbed.LINK`` —— 只写字体文件的本地路径，文件最小；
          同一台电脑（字体路径不变）正常显示，换电脑 / 挪字体就掉字。
        * ``images=ImageEmbed.EMBED``（默认）—— 图片 base64 内嵌，离线可看。
        * ``images=ImageEmbed.LINK`` —— 只引用图片路径（相对 SVG 所在目录），
          SVG 最小；图片挪走 / 换电脑就看不到。

        :param fonts: FontEmbed.SUBSET / EMBED / LINK（也接受字符串）
        :param images: ImageEmbed.EMBED / LINK（也接受字符串）
        :return: self（可链式）

        示例::

            pen = Malight("poster", fonts=FontEmbed.LINK, images=ImageEmbed.LINK)
            pen.set_embed(fonts="subset")        # 只有字体要内嵌
            pen.set_embed(images="link")         # 图片只引用，不撑大文件

        Three modes per asset type; the defaults (SUBSET fonts, EMBED images)
        keep the SVG self-contained while staying as small as possible.
        """
        if fonts is not None:
            self.font_embed = str(fonts)
        if images is not None:
            self.image_embed = str(images)
        return self

    def set_background_color(self, color) -> _Pen:
        """
        设置画布背景色（对应中文版 `设置背景色`）。 / Set the canvas background color.

        修复说明：原版只写 CSS 的 background-color（多数渲染器不生效），
        本版直接在画布最底层插入一个全画布矩形，任何查看器都正确显示。

        示例::
            pen.set_background_color("#f0f8ff")
        """
        c = _paint(color)
        rect = SvgNode("rect", {
            "id": "background", "x": 0, "y": 0,
            "width": self.width, "height": self.height, "fill": c,
        })
        # 插到 canvas 层的最前面（背景必须在最底）
        self.canvas_node.children.insert(0, rect)
        return self

    def add_background_rect(self, fill_color, opacity=1.0, id_=None,
                            **kw) -> RectElement:
        """
        添加背景矩形（对应中文版 `矩形背景`，与 set_background_color 等价，
        但可控制透明度并返回元素）。 / Add a background rectangle; unlike set_background_color it takes opacity and returns the element.

        :param kw: 其它公共样式与描边参数（blend_mode / stroke_color 等）

        示例::
            pen.add_background_rect("#fffbe6", opacity=0.9)
        """
        el = self.rect(0, 0, self.width, self.height,
                            fill_color=fill_color, opacity=opacity, id_=id_, **kw)
        el.send_to_back()
        return el

    # ------------------------------------------------------------------
    # 基本图形
    # ------------------------------------------------------------------

    def add_js(self, code) -> _Pen:
        """
        添加 JavaScript 代码（对应中文版 `增加JS代码`），嵌入 <script>。 / Embed JavaScript by adding a <script> element.

        示例::
            pen.add_js("alert('SVG loaded!')")
        """
        self._js.append(code)
        return self

    def write_app_info(self, x, y, font_size=14, fill_color=Color.BLACK, id_=None) -> TextElement:
        """
        写软件签名信息（对应中文版 `写软件信息`）。 / Write a software signature.

        示例::
            pen.write_app_info(780, 590)
        """
        return self.text(x, y, "Created with MagicPen (magicpen SVG toolkit)",
                               font_size=font_size, fill_color=fill_color,
                               h_align=TextHAlign.END, id_=id_)

    def author_seal(self, x=None, y=None, color="#c8102e", name="MagicPen", id_=None) -> GroupElement:
        """
        作者印章（对应中文版 `作者印章`）：圆形红印 + 名字。 / Author stamp: a round red seal plus a name.

        示例::
            pen.author_seal(700, 520, name="王二")
        """
        x = x if x is not None else self.width - 80
        y = y if y is not None else self.height - 80
        g = self.g(id_=id_, opacity=0.85)
        c = self.circle(x, y, 34, fill_color=Color.TRANSPARENT,
                             stroke_color=color, stroke_width=3)
        c.change_group(g)
        t = self.text(x, y + 8, name, font=SystemFont.KAITI, font_size=22,
                            fill_color=color, h_align=TextHAlign.MIDDLE)
        t.change_group(g)
        return g

    # ------------------------------------------------------------------
    # 生命周期钩子与保存
    # ------------------------------------------------------------------

    def before_create(self) -> None:
        """创作前钩子（对应中文版 `创作前执行`），子类可覆写。 / Pre-draw hook; subclasses may override. """
        pass

    def on_create(self) -> None:
        """创作主钩子（对应中文版 `创作`），子类可覆写：把绘图代码写在这里。 / Main draw hook; subclasses override this and put their drawing code here. """
        pass

    def after_create(self) -> None:
        """创作后钩子（对应中文版 `完成前执行`），子类可覆写。 / Post-draw hook; subclasses may override. """
        pass

    def rename_file(self, filename) -> "Optional[str]":
        """保存前修改文件名钩子（对应中文版 `修改文件名`），返回新文件名或 None。 / Hook to change the output filename before saving; return a new name or None. """
        return None

    def finish(self) -> str:
        """
        完成并保存 SVG（对应中文版 `完成`）。 / Finish drawing and save the SVG.

        修复说明：原版保存前 os.remove 旧文件，旧文件被占用时会抛错；
        本版直接覆盖写入，稳定可靠。

        示例::
            pen.finish()   # 保存并打印路径
        """
        self.before_create()
        self.on_create()
        self.after_create()

        # CSS 样式表
        style_node = self.style.build_style_node()
        if style_node is not None:
            self.root_node.add(style_node)

        # 调试元素统一放到最上层
        for node in self._debug_nodes:
            self.canvas_node.add(node)

        # JavaScript
        if self._js:
            script = SvgNode("script", {"type": "text/javascript"})
            script.text = "\n".join(self._js)
            self.root_node.add(script)

        new_name = self.rename_file(self.file_path)
        if new_name:
            self.file_path = new_name

        os.makedirs(os.path.dirname(os.path.abspath(self.file_path)), exist_ok=True)
        with open(self.file_path, "w", encoding="utf-8") as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            # 英文 remark：标明生成工具与项目地址（GitHub/Gitee 上也能直接溯源）
            # English remark: which tool made this file and where the project lives
            f.write('<!-- Generated by MaLight '
                    '(https://github.com/weigang75/malight) -->\n')
            f.write(self.root_node.to_xml())
        # 打印保存全路径（方便直接复制）；尺寸走 fmt_num 保留 2 位小数，
        # 免得 772.8 这类画布打印成 772.8000000000001
        self.file_path = tools.report(
            "SVG", self.file_path,
            extra="{}x{}".format(fmt_num(self.width), fmt_num(self.height)))
        return self.file_path

    def _collect_path_nodes(self) -> list:
        """收集画面上的全部路径节点（跳过 defs/symbol 等定义容器，内部方法）。

        给没有 id 的路径节点补上 id —— 页面靠 id 隐藏「正在编辑的那条」背景副本。
        / Collect every path node on the canvas (skipping defs/symbol/...), and
        assign ids to id-less ones - the page hides the edited path by id.
        """
        skip_tags = {"defs", "symbol", "clippath", "mask", "marker", "pattern",
                     "style", "script"}
        out = []
        counter = [0]

        def walk(node, inside_defs):
            for child in node.children:
                tag = (child.tag or "").lower()
                if tag == "path" and not inside_defs and child.attribs.get("d"):
                    counter[0] += 1
                    if not child.attribs.get("id"):
                        child.attribs["id"] = "bg_path_%d" % counter[0]
                    out.append({
                        "id": child.attribs["id"],
                        "name": child.attribs["id"],
                        "d": child.attribs["d"],
                        "fill": child.attribs.get("fill", "none"),
                        "stroke": child.attribs.get("stroke", "#e63946"),
                        "strokeWidth": child.attribs.get("stroke-width", 3),
                    })
                walk(child, inside_defs or tag in skip_tags)

        walk(self.root_node, False)
        return out

    def svg_editor(self, path=None, file=None, background=True,
                   stroke_color="#e63946", stroke_width=3, fill_color="none",
                   grid=20, title=None) -> str:
        """
        生成「SVG 编辑器」专用 HTML：调路径 + 取点定位二合一（对应中文版 `获取坐标点.html` 的加强版）。 / Generate the dedicated SVG-editor HTML: path editing plus point picking in one page.

        页面能力（未来还会扩展）：
        * **调路径**——拖锚点/调整杆、双击段线加锚点、双击锚点删锚点（有确认）、
          改段线类型与平滑/尖角，d 串与代码实时更新（`PathHTMLEditor` 全部功能）；
        * **多路径选择**——不传 ``path`` 时自动收集画面上全部路径，页面右上
          下拉选择要编辑的那条（背景里的原路径自动隐藏避免重影），逐条编辑；
        * **取点**——开启「取点」后点画布即记录坐标，显示 x/y 与相邻两点
          dx/dy/d，自动生成链式代码（同 y → ``h_line_to``、同 x → ``v_line_to``）；
        * **背景图层**——把已保存的 SVG（`finish()` 的产物）内嵌进页面垫底，
          路径就叠在原图上拖，所见即所得；透明度滑条可调；
        * 代码面板 set_d / 链式 / 取点三个页签，一键复制。

        :param path: 要编辑的 PathElement；缺省时收集画面上全部路径供页面选择，
            一条都没有则是纯取点模式
        :param file: 输出 HTML 路径；缺省为 ``<SVG文件名>.editor.html``（同目录）
        :param background: 是否内嵌已保存的 SVG 作背景（需先 `finish()`）
        :param stroke_color: 编辑路径的默认描边色
        :param stroke_width: 编辑路径的默认线宽
        :param fill_color: 编辑路径的默认填充色
        :param grid: 网格间距（像素）；``0`` 关闭
        :param title: 页面标题
        :return: 生成的 HTML 绝对路径

        示例::

            p = pen.path(fill_color="none", stroke_width=3)
            p.move_to((60, 320)).line_to((380, 190))
            pen.finish()
            pen.svg_editor(p)          # 只编辑这一条 / edit just this path
            pen.svg_editor()           # 收集全部路径，页面里下拉选择 / all paths
        """
        from ..pathkit import PathHTMLEditor   # 延迟导入避免循环 / lazy import

        # 先收集路径（给无 id 的补 id），再渲染背景 —— 页面靠 id 隐藏
        # 「正在编辑的那条」背景副本，顺序反了背景里就没有 id。
        # / Collect first (assigning ids), render the background after - the
        # page hides the edited path by id, so the order matters.
        paths_data = None
        if path is not None and not path.node.attribs.get("id"):
            # 显式路径缺 id 时补一个：页面靠 id 隐藏背景里正在编辑的副本，
            # 必须在渲染背景**之前**落属性。/ Assign an id to a bare path before
            # the background renders - the page hides the bg copy by that id.
            path.node.set("id", "path0")
        if path is None:
            paths_data = self._collect_path_nodes()
        bg_svg = None
        if background:
            if not self.file_path or not os.path.exists(self.file_path):
                raise ValueError(t("err.svg_editor_need_finish"))
            bg_svg = self.root_node.to_xml()
        common = dict(width=self.width, height=self.height,
                      stroke_color=stroke_color, stroke_width=stroke_width,
                      fill_color=fill_color, grid=grid, title=title,
                      background_svg=bg_svg)
        if path is not None:
            editor = PathHTMLEditor(path, **common)
        elif paths_data:
            editor = PathHTMLEditor(paths=paths_data, **common)
        else:
            # 无路径：纯取点模式（空段列表，页面上没有锚点）/ no path: pure picking
            editor = PathHTMLEditor(points={"segments": []}, **common)
        if file is None:
            stem = os.path.splitext(self.file_path)[0] if self.file_path else "svg"
            file = stem + ".editor.html"
        return editor.save(file)

    # ------------------------------------------------------------------
    # 导出
    # ------------------------------------------------------------------

    def export_png(self, scale=3, out_file=None, mode=PNGMode.AUTO) -> str:
        """
        导出 PNG（对应中文版 `生成PNG`），需 finish() 先保存。 / Export PNG; call finish() first to save the SVG.

        完成后会打印「PNG 导出成功 + 文件全路径 + 大小」，返回值也是绝对路径。

        :param scale: 放大倍数（默认 3 倍高清）
        :param mode: PNGMode.AUTO（默认：装了 cairosvg 就用它，没装自动改用
                     Chrome）/ CAIROSVG（强制 cairosvg，不渲染 SVG filter）/
                     CHROME（无头 Chrome 截图，支持 SVG filter）

        示例::
            pen.finish()
            pen.export_png(scale=2)
            pen.export_png(mode=PNGMode.CHROME)   # 滤镜效果正确导出
        """
        mode = int(mode)
        if mode == int(PNGMode.CHROME):
            return tools.export_png_chrome(self.file_path, out_file, scale=scale)
        if mode == int(PNGMode.AUTO) and not tools.has_cairosvg():
            # 没装 cairosvg：自动改用 Chrome，避免一句 ModuleNotFoundError 卡住
            if tools.find_chrome():
                print(t("info.png_fallback_chrome"))
                return tools.export_png_chrome(self.file_path, out_file,
                                               scale=scale)
            raise RuntimeError(t("err.need_png_engine"))
        return tools.export_png_cairo(self.file_path, out_file, scale)

    def export_pdf(self, out_file=None, engine=PDFMode.AUTO, page=None) -> str:
        """
        导出 PDF（对应中文版 `生成PDF`），需 finish() 先保存。 / Export PDF; call finish() first to save the SVG.

        完成后会打印「PDF 导出成功 + 文件全路径 + 大小」，返回值也是绝对路径。

        :param engine: PDFMode.AUTO（默认：优先 Chrome，找不到自动回退
                       cairosvg）/ CHROME（强制 Chrome，渲染与浏览器一致、
                       支持 SVG filter）/ CAIROSVG（强制 cairosvg，不渲染
                       filter 但无需浏览器）
        :param page: 页面设置 ``PageSetup``（纸张 / 页边距 / 缩放）。
                     不传就用 ``self.page``（构造后设置过一次即长期生效）。
                     **仅 Chrome 引擎支持**：cairosvg 不做浏览器排版，
                     传了会当场报错而不是静默忽略

        示例::

            pen.finish()
            pen.export_pdf()                        # 自动选引擎
            pen.export_pdf(engine=PDFMode.CHROME)   # 强制 Chrome
            pen.page = PageSetup("A4", margin=24)   # 铺到 A4 纸
            pen.export_pdf(page=PageSetup("A4 landscape"))
        """
        if out_file is None:
            out_file = os.path.splitext(self.file_path)[0] + ".pdf"
        if page is None:
            page = self.page
        if int(engine) == int(PDFMode.CAIROSVG):
            return tools.export_pdf_cairo(self.file_path, out_file, page=page)
        if int(engine) in (int(PDFMode.AUTO), int(PDFMode.CHROME)):
            chrome = tools.find_chrome()
            if chrome is not None:
                return tools.export_pdf_chrome(self.file_path, out_file,
                                               chrome=chrome, page=page)
            if int(engine) == int(PDFMode.CHROME):
                raise RuntimeError(t("err.chrome_missing_pdf"))
        return tools.export_pdf_cairo(self.file_path, out_file, page=page)

    def export_docx(self, out_file=None) -> str:
        """
        导出 DOCX（对应中文版 `生成DOCX`，需 pdf2docx）。 / Export DOCX.

        完成后会打印「DOCX 导出成功 + 文件全路径 + 大小」。

        示例::
            pen.finish()
            pen.export_docx()
        """
        pdf = self.export_pdf()
        return tools.export_docx_from_pdf(pdf, out_file)


# ===========================================================================
# 子工具 API（pen.filter.* / pen.style.*）
# ===========================================================================

    def _dbg(self, node) -> "Element":
        """登记调试节点（finish 时统一放到最上层，内部方法）。"""
        self._debug_nodes.append(node)
        return node

