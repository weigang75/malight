"""
运行时多语言 / Runtime message localisation.

malight 的报错、提示与导出信息**默认输出英文**，一行代码即可切成中文::

    import malight
    malight.set_language("zh")      # 切成中文
    malight.set_language("en")      # 切回英文（默认）

不想改代码时可用环境变量，适合 CI 与命令行脚本::

    set MALIGHT_LANG=zh             # Windows
    export MALIGHT_LANG=zh          # macOS / Linux
    set MALIGHT_LANG=auto           # 跟随系统语言

优先级：``set_language()`` > 环境变量 ``MALIGHT_LANG`` > 默认 ``"en"``。

只影响**运行时消息**，不影响 API 名称与返回的数据（``kind`` / ``cmd`` 这类
机器可读的值恒为英文 ASCII，便于程序判断）。

扩展自己的语言（繁体、日语…）::

    from malight import i18n
    i18n.add_messages("zh-TW", {"export.ok": "[malight] {kind} 匯出成功{tail}-> {path}  [{size}]"})
    malight.set_language("zh-TW")   # 未翻译的词条自动回退英文

临时切换（不污染全局，适合测试或文档生成）::

    with malight.use_language("zh"):
        pen.export_png()            # 这几行输出中文
"""

from __future__ import annotations

import os
from enum import Enum


# ---------------------------------------------------------------------------
# 直接运行引导：在 PyCharm 里点绿色三角运行本文件（或命令行 python 本文件路径）时，
# 相对导入需要包上下文，这里自动补上项目根路径与包名。
# 正常 `import malight.xxx` 时这段不会执行，对包本身零影响。
# ---------------------------------------------------------------------------
if __name__ == "__main__" and not __package__:
    import os as _os
    import sys as _sys
    _sys.path.insert(0, _os.path.dirname(_os.path.dirname(
        _os.path.abspath(__file__))))
    __package__ = "malight"


__all__ = [
    "Language", "DEFAULT_LANGUAGE", "ENV_VAR",
    "get_language", "set_language", "use_language", "reset_language",
    "is_chinese", "t", "available_languages", "add_messages", "normalize",
]


# ===========================================================================
# 语言枚举 / Language enum
# ===========================================================================
class Language(str, Enum):
    """
    语言枚举（继承 str，可直接当字符串用）。 / Language enum; it subclasses str so it can be used as a plain string.

    示例::

        Language.EN              # "en"
        str(Language.ZH)         # "zh"
        Language.ZH == "zh"      # True（与裸字符串等价）
        Language.of("zh-CN")     # Language.ZH
    """

    EN = "en"          # 英文 / English（默认）
    ZH = "zh"          # 简体中文 / Simplified Chinese
    ZH_CN = "zh"       # 别名：Language.ZH_CN is Language.ZH
    AUTO = "auto"      # 跟随系统语言（set_language 时解析成 en / zh）

    def __str__(self) -> str:
        """让 f-string 得到 "en" / "zh" 而不是 "Language.EN"。"""
        return self.value

    @classmethod
    def of(cls, value) -> "Language":
        """把任意写法归一成 Language 成员。 / Normalise any spelling into a Language member. 示例:: Language.of("zh_CN")"""
        return cls(normalize(value))


#: 默认语言（英文，与 GitHub / PyPI 用户预期一致）
DEFAULT_LANGUAGE = Language.EN.value

#: 环境变量名，用于不改代码就切换语言
ENV_VAR = "MALIGHT_LANG"


# ===========================================================================
# 语言归一化 / Normalisation
# ===========================================================================
# 非地区写法 -> 语言族；带地区后缀的（zh-CN / en-US / zh-TW）原样保留，
# 这样用户可以先 add_messages("zh-TW", ...) 再 set_language("zh-TW")
_ALIASES = {
    "eng": "en", "english": "en",
    "zh": "zh", "cn": "zh", "chs": "zh", "chinese": "zh",
    "simplified": "zh", "hans": "zh",
    "auto": "auto", "system": "auto",
}


def _canon(value) -> str:
    """
    归一成小写标准码并**保留地区后缀**（内部函数）。

    示例:: _canon("zh_CN") -> "zh-cn"   _canon("English") -> "en"
    """
    if value is None:
        return DEFAULT_LANGUAGE
    if isinstance(value, Language):
        return value.value
    key = str(value).strip().lower().replace("_", "-").replace(" ", "-")
    if not key:
        return DEFAULT_LANGUAGE
    if key in _ALIASES:
        return _ALIASES[key]
    return key


def normalize(value) -> str:
    """
    把任意语言写法归一成**语言族**（``"en"`` / ``"zh"`` / ``"auto"``）。 / Normalise any way of writing a language down to its family: en, zh or auto.

    :param value: Language 枚举、字符串，或 None
    :return: 语言族码；认不出时返回 :data:`DEFAULT_LANGUAGE`

    示例::

        normalize("zh_CN")            # "zh"
        normalize("zh-TW")            # "zh"（族），精确码请用 _canon
        normalize(Language.EN)        # "en"
        normalize(None)               # "en"
    """
    code = _canon(value)
    if code in ("en", "zh", "auto"):
        return code
    if code.startswith("zh-"):
        return "zh"
    if code.startswith("en-"):
        return "en"
    return DEFAULT_LANGUAGE


def _detect_system() -> str:
    """跟随系统语言：中文环境返回 "zh"，其余返回 "en"（不抛异常）。"""
    try:
        import locale
        code = None
        try:
            code = locale.getlocale()[0]
        except (ValueError, TypeError):
            code = None
        if not code:
            code = os.environ.get("LANG") or os.environ.get("LC_ALL")
        if code and str(code).lower().startswith("zh"):
            return "zh"
    except Exception:                                    # noqa: BLE001
        pass
    return DEFAULT_LANGUAGE


# ===========================================================================
# 消息目录 / Message catalogue
# ===========================================================================
# 说明：词条按「区域.语义」命名；占位符一律用 {花括号}，由 t() 格式化。
# 新增消息时中英两份都要补，缺失的会回退英文。
_CATALOGUE = {}


_CATALOGUE["en"] = {
    # ---- 导出信息 / export report ----
    "export.ok": "[malight] {kind} exported{tail}-> {path}  [{size}]",
    "export.tail": " ({tags})",
    "export.tags_sep": ", ",
    "size.unknown": "unknown size",
    "kind.svg": "SVG",
    "kind.svg_scaled": "SVG (scaled)",
    "kind.png": "PNG",
    "kind.pdf": "PDF",
    "kind.docx": "DOCX",
    "engine.chrome": "Chrome engine",
    "engine.cairosvg": "cairosvg",
    "engine.pdf2docx": "pdf2docx",
    "extra.scale": "{n}x",
    "extra.scale_fx": "{n}x, filters fully rendered",
    "extra.no_svg_filter": "SVG filters not rendered",
    "extra.fx_full": "filters fully rendered",

    # ---- 一般提示 / notices ----
    "info.font_subset_done": "[malight] font subset done: {src} -> {dst}  [{size}]",
    "info.font_embedded": ("[malight] note: font file {name} ({mb:.1f} MB) embedded — "
                           "the SVG grows accordingly. For a smaller file, use a subset "
                           "font (fontTools subset) or a .woff2 font."),
    "info.png_fallback_chrome": ("[malight] cairosvg not found; falling back to headless "
                                 "Chrome for PNG (better SVG filter support)"),

    # ---- 代码迁移工具 / compat migrator ----
    "compat.migrated": "migration done -> {target}",
    "compat.no_mapping": "no mapping found: {name}",

    # ---- 缺少可选依赖 / missing optional deps ----
    "err.need_fonttools_subset": "font subsetting needs fontTools: pip install fonttools",
    "err.need_fonttools_path": ("converting text to path needs fontTools: "
                                "pip install fonttools"),
    "err.need_shapely": "boolean path operations need shapely: pip install shapely",
    "err.need_pdf2docx": "DOCX export needs pdf2docx: pip install pdf2docx",
    "err.need_cairosvg": (
        "cairosvg is not installed, so the cairosvg renderer is unavailable. Pick one:\n"
        "  1) pip install cairosvg                     (enables this renderer)\n"
        "  2) export_png(mode=PNGMode.CHROME)          (headless Chrome, renders SVG filters)\n"
        "  3) export_png()                             (AUTO: falls back to Chrome)"),
    "err.need_png_engine": (
        "PNG export needs either cairosvg or Chrome; neither was found.\n"
        "  1) pip install cairosvg\n"
        "  2) install Chrome / Edge, or set the MALIGHT_CHROME environment variable "
        "to chrome.exe"),

    # ---- 滤镜 / filters ----
    "err.attr_no_dynamic": (
        "'{cls}' has no dynamic method '{name}'. set_*/get_* only accept "
        "parameter names of that element (see its creating call), e.g. "
        "set_font_size / get_fill_color."),
    "err.attr_one_arg": (
        "'{name}()' takes no arguments to read the value, or exactly one "
        "value to set it."),
    "err.fx_unknown": (
        "no such filter effect: '{name}'. See the effect list in "
        "malight/board/filters.py (pen.fx), e.g. blur / shadow / inner_shadow / "
        "glow / bevel / emboss / saturate."),
    "err.fx_other_board": (
        "this filter chain belongs to another drawing board; the <filter> it "
        "references lives in that board's <defs>, so the element would render "
        "without any filter. Build the chain from the same board: "
        "pen2.fx.shadow(...) rather than pen1.fx.shadow(...)."),

    # ---- Chrome 相关 / Chrome related ----
    "err.chrome_missing_pdf": (
        "Chrome not found, cannot export PDF with Chrome. Install Chrome, or set the "
        "MALIGHT_CHROME environment variable, or use engine=PDFMode.CAIROSVG."),
    "err.chrome_missing_pdf_tools": (
        "Chrome not found, cannot export PDF with Chrome. Install Chrome or set the "
        "MALIGHT_CHROME environment variable, or use export_pdf_cairo() instead."),
    "err.chrome_missing_png_tools": (
        "Chrome not found, cannot export PNG with Chrome. Install Chrome or set the "
        "MALIGHT_CHROME environment variable, or use export_png_cairo() instead."),
    "err.chrome_pdf_failed": "Chrome PDF export failed (exit={code}): {path}",
    "err.chrome_png_failed": "Chrome PNG export failed (exit={code}): {path}",
    "err.page_size_unknown": (
        "unknown paper size '{name}'. Use A2/A3/A4/A5/A6/B4/B5/LETTER/LEGAL "
        "(optionally with 'landscape'/'portrait'), or a (width_mm, height_mm) "
        "tuple."),
    "err.page_need_chrome": (
        "page setup (paper size / margin / zoom) needs the Chrome engine: "
        "cairosvg does no browser layout. Use export_pdf_chrome(...) or "
        "export_pdf(engine=PDFMode.CHROME)."),

    # ---- 字体相关 / fonts ----
    "err.font_file_missing": (
        "font file not found: {path}\n"
        "  checks: (1) to use a font NAME do not pass a path, e.g. font=\"KaiTi\";\n"
        "          (2) to use a font FILE pass the full path, e.g. "
        "font=r\"C:\\Windows\\Fonts\\simhei.ttf\";\n"
        "          (3) Font.list_values() lists all built-in font enum values."
    ),
    "err.font_not_found": ("font file not found: {font}; pass the name of an installed "
                           "font instead"),

    # ---- 扩展机制 / extension ----
    "err.toolkit_name_empty": "the toolkit name must be a non-empty string",
    "err.toolkit_not_class": "toolkit {name} must be a class, got {type}",
    "err.toolkit_not_found": ("toolkit '{name}' not found; registered: {names}. "
                              "Import the toolkit module first."),

    # ---- 路径编辑 / pathkit ----
    "err.seg_no_ctrl": ("segment {index} is {cmd} ({kind}) and has no control points; "
                        "segments that do have control points: {avail}."),
    "err.ctrl_index_range": ("segment {index} has only {count} control point(s); "
                             "ctrl_index={given} is out of range (valid 0~{last})."),
    "err.anchor_is_endpoint": "this anchor is a path endpoint and cannot be removed",
    "err.remove_anchor_curve": ("an anchor can only be dropped when both neighbouring "
                                "segments are straight lines; for curves, adjust the "
                                "control points to simplify the shape"),
    "err.arc_split": "arc segments cannot be split; use line/cubic/quad curves",
    "err.no_board": "no board found; pass board=pen explicitly",
    "info.points_exported": "path points exported: {file}",

    # ---- HTML path editor (pathkit.htmleditor) ----
    #      These labels are embedded into the generated page for BOTH languages,
    #      so the exported file carries its own 中文 / English switch.
    "html.title": "Path editor - drag the points, copy the code",
    "html.subtitle": ("Drag the squares (anchors) and the dots (control points); "
                      "the d string and the malight code update as you go."),
    "html.hint": ("Double-click a segment to insert an anchor at its midpoint. "
                  "Arrow keys nudge the selected point (hold Shift for 10px)."),
    "html.segments": "segments",
    "html.anchors": "anchors",
    "html.controls": "control points",
    "html.d_label": "d string",
    "html.code_label": "malight code",
    "html.copy": "Copy",
    "html.copied": "Copied",
    "html.copy_fail": "Select and copy manually",
    "html.reset": "Reset",
    "html.handles": "Handles",
    "html.link_handles": "Move handles with the anchor",
    "html.json": "Download points.json",
    "html.json_hint": ("The downloaded JSON matches PathEditor.to_dict(); read it back "
                       "with ed.load_json(\"points.json\")."),
    "html.arc_no_split": ("Arc segments cannot be split; use line, cubic or quad curves."),
    "html.saved": "HTML path editor written: {file}",
    "err.html_no_source": "give one of path=, d= or points=",

    # ---- 路径结构说明 / path structure report ----
    "seg.kind.M": "move",
    "seg.kind.L": "line",
    "seg.kind.C": "cubic",
    "seg.kind.Q": "quad",
    "seg.kind.A": "arc",
    "seg.kind.Z": "close",
    "seg.word.start": "start",
    "seg.word.ctrl": "ctrls",
    "seg.word.end": "end",
    "seg.word.radius": "radius",
    "seg.arrow": " -> ",
    "pt.anchor": "anchor#{index}",
    "pt.control": "seg{seg}.ctrl{ctrl}",
    "editor.title": ("path structure: {segs} segment(s) / {anchors} anchor(s) / "
                     "{ctrls} control point(s) / {closed}"),
    "editor.closed": "closed",
    "editor.open": "open",
    "editor.table_head": ("  idx   cmd   kind    start            ctrls"
                          "                        end"),
    "editor.anchors_head": "  anchors (draggable):",
    "editor.controls_head": "  control points (drag to change curvature):",
}


_CATALOGUE["zh"] = {
    # ---- 导出信息 ----
    "export.ok": "[malight] {kind} 导出成功{tail}→ {path}  [{size}]",
    "export.tail": "（{tags}）",
    "export.tags_sep": "、",
    "size.unknown": "大小未知",
    "kind.svg": "SVG",
    "kind.svg_scaled": "SVG（缩放后）",
    "kind.png": "PNG",
    "kind.pdf": "PDF",
    "kind.docx": "DOCX",
    "engine.chrome": "Chrome 引擎",
    "engine.cairosvg": "cairosvg",
    "engine.pdf2docx": "pdf2docx",
    "extra.scale": "{n} 倍",
    "extra.scale_fx": "{n} 倍、滤镜完整",
    "extra.no_svg_filter": "不渲染 SVG 滤镜",
    "extra.fx_full": "滤镜完整",

    # ---- 一般提示 ----
    "info.font_subset_done": "[malight] 字体子集化完成：{src} -> {dst}  [{size}]",
    "info.font_embedded": ("[malight] 提示：已内嵌字体文件 {name}（{mb:.1f} MB），"
                           "SVG 体积会相应变大；如需小体积，建议改用子集化字体"
                           "（fontTools subset）或 .woff2 字体。"),
    "info.png_fallback_chrome": ("[malight] 未检测到 cairosvg，自动改用无头 Chrome 导出 PNG"
                                 "（对 SVG 滤镜的支持更好）"),

    # ---- 代码迁移工具 ----
    "compat.migrated": "迁移完成 -> {target}",
    "compat.no_mapping": "未找到映射: {name}",

    # ---- 缺少可选依赖 ----
    "err.need_fonttools_subset": "字体子集化需要 fontTools：pip install fonttools",
    "err.need_fonttools_path": "文字转路径需要 fontTools：pip install fonttools",
    "err.need_shapely": "布尔运算需要 shapely 库：pip install shapely",
    "err.need_pdf2docx": "DOCX 导出需要 pdf2docx：pip install pdf2docx",
    "err.need_cairosvg": (
        "未安装 cairosvg，无法用 cairosvg 导出 PNG。三种解法任选：\n"
        "  1) pip install cairosvg        （装好后本方式可用）\n"
        "  2) export_png(mode=PNGMode.CHROME)   （用无头 Chrome，支持 SVG 滤镜）\n"
        "  3) export_png()                （AUTO：没装 cairosvg 会自动改用 Chrome）"),
    "err.need_png_engine": (
        "导出 PNG 需要 cairosvg 或 Chrome，两者都没找到。\n"
        "  1) pip install cairosvg\n"
        "  2) 安装 Chrome / Edge，或设置环境变量 MALIGHT_CHROME 指向 chrome.exe"),

    # ---- 滤镜 ----
    "err.fx_unknown": (
        "没有这个滤镜效果：'{name}'。可用效果见 malight/board/filters.py（pen.fx），"
        "例如 blur / shadow / inner_shadow / glow / bevel / emboss / saturate。"),
    "err.fx_other_board": (
        "这条滤镜链属于另一个绘图板：它引用的 <filter> 在那个画板的 <defs> 里，"
        "绑上去元素会完全没有滤镜效果。请用同一个画板的工厂造链，"
        "例如 pen2.fx.shadow(...)，而不是 pen1.fx.shadow(...)。"),
    "err.attr_no_dynamic": (
        "'{cls}' 没有动态方法 '{name}'。set_*/get_* 和直接参数名调用只认该"
        "元素自己的参数名（与创建时的参数一致），例如 set_font_size / "
        "get_fill_color / font_size(24)。"),
    "err.attr_one_arg": (
        "'{name}()' 不带参数是读值，带且只带一个参数是改值。"),

    # ---- Chrome 相关 ----
    "err.chrome_missing_pdf": ("未找到 Chrome，无法使用 Chrome 导出 PDF；"
                               "请安装 Chrome 或设置环境变量 MALIGHT_CHROME，"
                               "或改用 engine=PDFMode.CAIROSVG"),
    "err.chrome_missing_pdf_tools": ("未找到 Chrome，无法使用 Chrome 导出 PDF；"
                                     "请安装 Chrome 或设置环境变量 MALIGHT_CHROME，"
                                     "或改用 export_pdf_cairo()。"),
    "err.chrome_missing_png_tools": ("未找到 Chrome，无法使用 Chrome 导出 PNG；"
                                     "请安装 Chrome 或设置环境变量 MALIGHT_CHROME，"
                                     "或改用 export_png_cairo()。"),
    "err.chrome_pdf_failed": "Chrome 导出 PDF 失败（exit={code}）: {path}",
    "err.chrome_png_failed": "Chrome 导出 PNG 失败（exit={code}）: {path}",
    "err.page_size_unknown": (
        "不认识的纸张规格 '{name}'。可用 A2/A3/A4/A5/A6/B4/B5/LETTER/LEGAL"
        "（可加 landscape 横向 / portrait 纵向），或直接给 (宽mm, 高mm) 元组。"),
    "err.page_need_chrome": (
        "页面设置（纸张 / 页边距 / 缩放）需要 Chrome 引擎：cairosvg 不参与"
        "浏览器排版，给不了纸张概念。请改用 export_pdf_chrome(...) 或"
        " export_pdf(engine=PDFMode.CHROME)。"),

    # ---- 字体相关 ----
    "err.font_file_missing": (
        "字体文件不存在：{path}\n"
        "  排查：① font= 想用「字体名」时不要带路径，例如 font=\"KaiTi\"；\n"
        "        ② 用字体文件时给完整路径，例如 font=r\"C:\\Windows\\Fonts\\simhei.ttf\"；\n"
        "        ③ 可用 Font.list_values() 查看内置字体枚举取值。"),
    "err.font_not_found": "未找到字体文件: {font}，请指定已安装字体",

    # ---- 扩展机制 ----
    "err.toolkit_name_empty": "toolkit 注册名必须是非空字符串",
    "err.toolkit_not_class": "工具包 {name} 必须是一个类，收到 {type}",
    "err.toolkit_not_found": "未找到工具包 '{name}'，已注册: {names}。请先 import 对应的工具包模块。",

    # ---- 路径编辑 ----
    "err.seg_no_ctrl": "第 {index} 段是 {cmd}（{kind}），没有调整点；带调整点的段号是 {avail}。",
    "err.ctrl_index_range": "第 {index} 段只有 {count} 个调整点，ctrl_index={given} 越界（可用 0~{last}）。",
    "err.anchor_is_endpoint": "该锚点是路径端点，无法删除",
    "err.remove_anchor_curve": "只有两侧都是直线段时才能直接删除锚点；曲线段请调整控制点来简化形状",
    "err.arc_split": "圆弧暂不支持拆分锚点，请用 line/cubic/quad 曲线",
    "err.no_board": "找不到绘图板，请显式传入 board=pen",
    "info.points_exported": "路径点位已导出：{file}",

    # ---- 路径 HTML 编辑器（pathkit.htmleditor）----
    #      这些文案会按 en / zh **两套一起**内嵌进生成的页面，所以导出的一份
    #      HTML 自带中英切换，不用为了换语言再导一次。
    "html.title": "路径编辑器 —— 拖点、复制代码",
    "html.subtitle": "拖动方块（锚点）与圆点（调整点），右侧的 d 串与 malight 代码会实时更新。",
    "html.hint": "双击某段可在中点插入一个锚点；选中点后用方向键微调（按住 Shift 走 10 像素）。",
    "html.segments": "段数",
    "html.anchors": "锚点",
    "html.controls": "调整点",
    "html.d_label": "d 串",
    "html.code_label": "malight 代码",
    "html.copy": "复制",
    "html.copied": "已复制",
    "html.copy_fail": "请手动选中复制",
    "html.reset": "复位",
    "html.handles": "调整杆",
    "html.link_handles": "锚点连动调整杆",
    "html.json": "下载 points.json",
    "html.json_hint": "下载的 JSON 与 PathEditor.to_dict() 同结构，可用 ed.load_json(\"points.json\") 读回。",
    "html.arc_no_split": "圆弧段不支持拆分锚点，请用直线 / 三次 / 二次曲线。",
    "html.saved": "路径 HTML 编辑器已生成：{file}",
    "err.html_no_source": "path= / d= / points= 至少要给一个",

    # ---- 路径结构说明 ----
    "seg.kind.M": "移动（起点）",
    "seg.kind.L": "直线",
    "seg.kind.C": "三次贝塞尔",
    "seg.kind.Q": "二次贝塞尔",
    "seg.kind.A": "圆弧",
    "seg.kind.Z": "闭合",
    "seg.word.start": "起点",
    "seg.word.ctrl": "调整点",
    "seg.word.end": "终点",
    "seg.word.radius": "半径",
    "seg.arrow": " → ",
    "pt.anchor": "锚点#{index}",
    "pt.control": "第{seg}段·调整点{ctrl}",
    "editor.title": "路径结构：{segs} 段 / {anchors} 个锚点 / {ctrls} 个调整点 / {closed}",
    "editor.closed": "已闭合",
    "editor.open": "未闭合",
    "editor.table_head": "  段号  命令  类型          起点            调整点(控制柄)                 终点",
    "editor.anchors_head": "  锚点（可整体拖动）：",
    "editor.controls_head": "  调整点（拖动改变弧度）：",
}


# ===========================================================================
# 语言状态 / Language state
# ===========================================================================
_explicit = None          # set_language() 设定的语言；None 表示还没设过


def _pick(code) -> str:
    """
    从候选码中挑出**真正有词条**的那个：精确码 > 语言族 > 英文（内部函数）。

    这样 add_messages("zh-TW", ...) 之后 set_language("zh-TW") 才会生效；
    没注册 zh-TW 时自动落到 zh，没注册 zh 时落到 en。
    """
    code = _canon(code)
    if code in _CATALOGUE:
        return code
    fam = normalize(code)
    if fam in _CATALOGUE:
        return fam
    return DEFAULT_LANGUAGE


def _resolve() -> str:
    """解析当前生效的词条键：显式设置 > 环境变量 > 默认英文（内部函数）。"""
    if _explicit is not None:
        return _pick(_explicit)
    raw = os.environ.get(ENV_VAR)
    if raw:
        code = _canon(raw)
        if code == "auto":
            return _detect_system()
        return _pick(code)
    return DEFAULT_LANGUAGE


def get_language() -> str:
    """
    当前**生效**的语言码（已做词条回退，即真正用于取词的那个）。 / The language code currently in effect, after message fallback, i.e. the one lookups use.

    示例::

        malight.get_language()        # "en"（默认）
    """
    return _resolve()


def set_language(value) -> str:
    """
    设置输出语言（全局生效，覆盖环境变量）。 / Set the output language globally, taking precedence over the environment variable.

    :param value: ``"en"`` / ``"zh"`` / ``"zh-CN"`` / ``Language.ZH`` / ``"auto"``
    :return: 生效后的语言码（若该语言没有词条，会回退到中文族或英文）

    示例::

        malight.set_language("zh")            # 中文
        malight.set_language("zh-CN")         # 同上
        malight.set_language(Language.ZH)     # 枚举写法
        malight.set_language("auto")          # 跟随系统语言
        malight.set_language("en")            # 英文（默认）
    """
    global _explicit
    code = _canon(value)
    _explicit = _detect_system() if code == "auto" else code
    return _resolve()


def reset_language() -> str:
    """
    清掉显式设置，回到「环境变量 / 默认英文」的解析结果。 / Drop the explicit setting and go back to the environment-variable or default-English result.

    :return: 复位后的语言码

    示例::

        malight.reset_language()      # 又变回英文（除非设了 MALIGHT_LANG）
    """
    global _explicit
    _explicit = None
    return _resolve()


class use_language(object):
    """
    临时切换语言，退出 ``with`` 后自动恢复（适合测试与文档生成）。 / Temporarily switch language; the previous setting is restored on exit.

    示例::

        with malight.use_language("zh"):
            print(malight.t("size.unknown"))     # 大小未知

        with malight.use_language(Language.EN):
            pen.export_png()                     # 输出英文
    """

    __slots__ = ("_code", "_saved")

    def __init__(self, value):
        code = _canon(value)
        self._code = _detect_system() if code == "auto" else code
        self._saved = None

    def __enter__(self):
        global _explicit
        self._saved = _explicit
        _explicit = self._code
        return _resolve()

    def __exit__(self, *exc):
        global _explicit
        _explicit = self._saved
        return False


def is_chinese() -> bool:
    """当前是否为中文输出。 / Whether messages are currently being output in Chinese. 示例:: malight.is_chinese()"""
    return normalize(_resolve()) == "zh"


# ===========================================================================
# 取词 / Lookup
# ===========================================================================
def t(key, **kwargs):
    """
    取一条本地化消息并按关键字格式化。 / Look up one localised message and format it with keyword arguments.

    :param key: 词条名，如 ``"export.ok"``
    :param kwargs: 占位符取值
    :return: 消息文本；词条不存在时返回 key 本身（便于发现漏配）

    示例::

        malight.t("export.ok", kind="PNG", tail="", path="a.png", size="1 KB")
        # 英文：[malight] PNG exported-> ...  [1 KB]
        # 中文：[malight] PNG 导出成功→ ...  [1 KB]
    """
    cat = _CATALOGUE.get(_resolve()) or {}
    text = cat.get(key)
    if text is None:
        text = _CATALOGUE[DEFAULT_LANGUAGE].get(key)
    if text is None:
        return key
    if not kwargs:
        return text
    try:
        return text.format(**kwargs)
    except (KeyError, IndexError, ValueError):
        # 译文写错占位符也不能让正常流程崩掉
        return text


def available_languages() -> list:
    """
    已注册词条的语言码列表。 / The language codes that currently have messages registered.

    示例::

        malight.available_languages()     # ['en', 'zh']
    """
    return sorted(_CATALOGUE)


def add_messages(code, mapping):
    """
    注册或扩充一种语言的词条（未翻译的词条自动回退到语言族、再回退英文）。 / Register or extend the messages of a language; missing keys fall back to the language family, then to English.

    :param code: 语言码，如 ``"zh-TW"``
    :param mapping: ``{词条名: 文本}``

    示例::

        add_messages("zh-TW", {"export.ok": "[malight] {kind} 匯出成功{tail}-> {path}"})
        set_language("zh-TW")        # 之后就能生效
    """
    if not code:
        raise ValueError("language code must be a non-empty string")
    key = _canon(code)
    cat = _CATALOGUE.setdefault(key, {})
    cat.update(dict(mapping))
    return key


# ===========================================================================
# 使用示例 / Usage example
# ===========================================================================
# 在 PyCharm 里点绿色三角直接运行本文件即可；也可命令行：
#     python -m malight.i18n
# 本示例覆盖：Language 枚举 / normalize / get_language / set_language /
#             reset_language / use_language / is_chinese / t /
#             available_languages / add_messages
# Run directly in PyCharm (green triangle) or: python -m malight.i18n
if __name__ == "__main__":
    import malight
    from malight import i18n

    # 1) 语言枚举：继承 str，可直接与字符串比较，f-string 得到裸值 / 1) The language enum subclasses str: compare it with plain strings
    print("枚举    : / enum    :", Language.EN, Language.ZH, "| ZH_CN is ZH:", Language.ZH_CN is Language.ZH)
    print("比较    : / compare :", Language.ZH == "zh", Language.EN == "en")

    # 2) 归一化：各种写法都能认，认不出的回退英文 / 2) Normalisation accepts every spelling and falls back to English
    for raw in ("zh", "zh-CN", "zh_CN", "chs", "Chinese", "en-US", "japanese", None):
        print("  normalize({!r:>10}) -> {}".format(raw, i18n.normalize(raw)))

    # 3) 默认语言是英文，且支持环境变量覆盖 / 3) English by default, with the environment variable overriding it
    print("默认    : / default :", malight.get_language(), "(ENV {}={!r})".format(
        i18n.ENV_VAR, os.environ.get(i18n.ENV_VAR)))

    # 4) 同一句话，两种语言：导出信息 + 报错提示 / 4) The same message in both languages: export info and an error
    key = "export.ok"
    kw = dict(kind="PNG", tail="", path=r"C:\out\demo.png", size="12.3 KB")
    for code in ("en", "zh"):
        malight.set_language(code)
        ok, err = malight.t(key, **kw), malight.t("err.need_shapely")
        print("[{}] 导出信息 : {} / [{}] export : {}".format(code, ok, code, ok))
        print("[{}] 报错提示 : {} / [{}] error : {}".format(code, err, code, err))

    # 5) is_chinese / available_languages
    malight.set_language("zh")
    print("is_chinese  :", malight.is_chinese())
    print("已内置语言  : / built-in languages :", malight.available_languages())

    # 6) use_language：临时切换，退出后自动恢复（测试/文档生成很有用） / 6) use_language switches temporarily and restores on exit
    with malight.use_language("en"):
        print("with 内 : / inside :", malight.t("size.unknown"))
    print("with 后 : / after  :", malight.t("size.unknown"))

    # 7) 扩展一种自己的语言；没翻的词条自动回退英文 / 7) Add your own language; untranslated keys fall back to English
    malight.add_messages("zh-TW", {
        "export.ok": "[malight] {kind} 匯出成功{tail}-> {path}  [{size}] / [malight] {kind} export OK{tail} -> {path}  [{size}]",
        "size.unknown": "大小未知 / size unknown",
    })
    malight.set_language("zh-TW")
    print("zh-TW       :", malight.t(key, **kw))
    print("未翻译回退  : / untranslated fallback :", malight.t("err.no_board"), "  <- 回退英文 /   <- fell back to English")
    print("现在语言集  : / languages now :", malight.available_languages())

    # 8) 复位：回到「环境变量 / 默认英文」 / 8) Reset: back to the environment variable or default English
    print("reset 后    : / after reset   :", malight.reset_language())
