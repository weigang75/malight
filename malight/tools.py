# -*- coding: utf-8 -*-
"""
工具集（tools）—— 图像/导出/几何/滤镜/字体辅助
================================================

Image, export, geometry, filter and font helpers.

对应中文版《神笔码靓》的 通用工具集/图像处理工具/cairosvg工具集/
路径工具集/滤镜工具集 等模块的公共部分。

示例::

    from malight.tools import image_to_data_uri, wave_line_points
    uri = image_to_data_uri("photo.jpg")            # 图片转 base64 内嵌
    pts = wave_line_points((0, 0), (200, 0), 20, 4) # 波浪线顶点
"""

import base64
import math
import os
import sys

from .i18n import t
from .page import PageSetup
from .svg_backend import SvgNode, fmt_num


# ===========================================================================
# 终端颜色（让导出提示更醒目：整行加粗、路径绿色）
# ===========================================================================
#: ANSI 转义：粗体 / 复位；路径用「加粗绿」，浅色与深色终端都够醒目
_BOLD = "\x1b[1m"
_RESET = "\x1b[0m"
_COLORS = {
    "green": "\x1b[1;32m", "red": "\x1b[1;31m", "yellow": "\x1b[1;33m",
    "blue": "\x1b[1;34m", "cyan": "\x1b[1;36m", "grey": "\x1b[1;30m",
}

#: None = 自动（跟随 stdout 是否终端）；True / False = set_color() 强制
_COLOR_FORCED = None
_VT_READY = False


def _windows_ansi() -> None:
    """Windows 控制台打开 VT 转义支持（内部方法，只需一次）。"""
    global _VT_READY
    if _VT_READY or os.name != "nt":
        return
    _VT_READY = True
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)          # STD_OUTPUT_HANDLE
        mode = ctypes.c_uint32()
        if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            kernel32.SetConsoleMode(handle, mode.value | 0x0004)   # ENABLE_VT
    except Exception:                                # noqa: BLE001
        pass                                         # 老控制台：退化成无色


def set_color(enabled=None) -> None:
    """
    打开/关闭终端颜色；``None`` 表示回到自动判断。 / Turn terminal colors on or off; None restores auto-detection.

    自动判断 = stdout 是终端（不是重定向/管道）且没设 ``NO_COLOR``。
    也可以用环境变量强制：``MALIGHT_COLOR=1`` 开、``=0`` 关；
    ``NO_COLOR``（事实标准，设了就关）优先级最高。

    颜色只影响提示文字，**不影响任何返回值与文件内容**。

    示例::
        malight.set_color(False)     # 日志重定向时彻底关掉转义
        malight.set_color(None)      # 交回自动判断
    """
    global _COLOR_FORCED
    _COLOR_FORCED = None if enabled is None else bool(enabled)


def color_enabled() -> bool:
    """
    当前是否给终端输出上色。 / Whether terminal colors are currently on.

    示例::
        print(malight.tools.color_enabled())
    """
    if _COLOR_FORCED is not None:
        return _COLOR_FORCED
    if "NO_COLOR" in os.environ:                     # 事实标准：设了就关
        return False
    env = os.environ.get("MALIGHT_COLOR", "").strip().lower()
    if env:
        return env not in ("0", "false", "no", "off")
    try:
        if not sys.stdout.isatty():
            return False
    except Exception:                                # noqa: BLE001
        return False
    _windows_ansi()
    return True


def paint(text, color=None, bold=False) -> str:
    """
    给一段文字加 ANSI 样式（未启用颜色时原样返回）。 / Wrap text in ANSI styling, or return it unchanged when colors are off.

    :param text: 原文字
    :param color: "green" / "red" / "yellow" / "blue" / "cyan" / "grey"
    :param bold: 是否加粗
    :return: 可直接 print 的字符串

    示例::
        print(paint("导出成功", color="green", bold=True))
    """
    if not color_enabled():
        return text
    return "{}{}{}".format(_COLORS.get(color, "") if color else "",
                           _BOLD if bold else "", text) + _RESET


def paint_path(message, path) -> str:
    """
    让一行「文件已保存」提示更醒目：整行加粗、其中的路径绿色。 / Emphasise a message line: bold it and paint the file path green.

    未启用颜色（重定向/管道/``NO_COLOR``）时原样返回。
    路径用「替换后恢复加粗」的写法，避免嵌套样式被内层复位清掉。

    :param message: 完整提示文字
    :param path: 其中要标绿的路径（不在 message 里则不加色）
    :return: 可直接 print 的字符串

    示例::
        print(paint_path("[malight] PNG exported->  D:/out/a.png", "D:/out/a.png"))
    """
    if not color_enabled() or not path or path not in message:
        return message
    return _BOLD + message.replace(path, _COLORS["green"] + path + _BOLD) + _RESET


# ===========================================================================
# 包内资源（assets）查找：预览图、字体文件等都集中在这里
# ===========================================================================
#: 资源目录名。包内是 ``malight/assets/``（随包分发）；用户项目里也可以放一个
#: ``<项目>/assets/`` 放自己的图与字体 —— 查找时包内优先、再逐级向上找。
ASSETS_DIR = "assets"


def _find_asset(rel, check):
    """按「包内 → 当前目录逐级向上」找一个资源（内部方法）。"""
    bundled = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           ASSETS_DIR, rel)
    if check(bundled):
        return bundled
    here = os.path.abspath(os.getcwd())
    for _ in range(8):
        cand = os.path.join(here, ASSETS_DIR, rel)
        if check(cand):
            return cand
        parent = os.path.dirname(here)
        if parent == here:
            break
        here = parent
    return None


def asset_path(*parts):
    """
    找一个包内/项目资源文件，返回绝对路径；找不到返回 None。 / Locate an asset file inside the package or the project, absolute path; None when missing.

    查找顺序（找到即返回）：

    1. **包内** ``malight/assets/<parts>`` —— 随包分发，pip 装完也在；
    2. 从当前目录**逐级向上**找 ``<目录>/assets/<parts>``
       （源码工程、用户项目里放自己的资源）。

    :param parts: 相对 assets 的路径片段，如 ``("images", "logo.png")``
    :return: 绝对路径；不存在返回 None

    示例::

        from malight import asset_path
        asset_path("images", "fx_preview.png")   # 包内预览图
        asset_path("fonts", "my.ttf")            # 项目自带字体
    """
    return _find_asset(os.path.join(*parts), os.path.isfile)


def asset_dir(*parts):
    """
    找一个资源**目录**（查找顺序同 :func:`asset_path`）；不存在返回 None。 / Locate an asset directory (same lookup order as asset_path); None when missing.

    示例::

        from malight import asset_dir
        asset_dir("fonts")       # malight/assets/fonts（或项目里的 assets/fonts）
    """
    return _find_asset(os.path.join(*parts), os.path.isdir)


# ===========================================================================
# 导出提示（英文版新增：统一打印全路径，方便直接复制）
# ===========================================================================
def human_size(path):
    """
    把文件大小格式化为易读字符串（如 "88.3 KB"）。 / Format a byte count as a readable string such as "88.3 KB".

    示例::
        human_size("report.pdf")     # "88.3 KB"
    """
    try:
        n = float(os.path.getsize(path))
    except OSError:
        return t("size.unknown")
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return "{} {}".format(int(n), unit) if unit == "B" else "{:.1f} {}".format(n, unit)
        n /= 1024.0
    return "{} B".format(int(n))


def report(kind, file, engine=None, extra=None):
    """
    统一打印「导出成功 + 全路径 + 大小」，方便复制路径直接用；全路径既是返回值，
    也是各导出函数的返回值。 / Print a uniform "export succeeded + full path + size"
    line; the full path is both the return value and what the export helpers return.

    :param kind: 文件类型名，建议用 t("kind.pdf") 之类的本地化名
    :param file: 文件路径
    :param engine: 生成引擎说明，如 t("engine.chrome") / t("engine.cairosvg")
    :param extra: 额外说明，如 t("extra.scale", n=3)
    :return: 文件**绝对路径**

    消息语言由 :mod:`malight.i18n` 决定（默认英文）；终端里**整行加粗、
    路径绿色**（重定向/管道时自动不上色，见 :func:`set_color`）::

        path = report("PDF", "out/a.pdf", engine=t("engine.chrome"))
        # 英文: [malight] PDF exported (Chrome engine)-> C:\\...\\a.pdf  [88.3 KB]
        # 中文: [malight] PDF 导出成功（Chrome 引擎）→ C:\\...\\a.pdf  [88.3 KB]
    """
    full = os.path.abspath(file)
    tags = t("export.tags_sep").join([s for s in (engine, extra) if s])
    tail = t("export.tail", tags=tags) if tags else ""
    line = t("export.ok", kind=kind, tail=tail, path=full, size=human_size(full))
    print(paint_path(line, full))
    return full


# ===========================================================================
# 图像工具
# ===========================================================================
def image_to_data_uri(path):
    """
    本地图片转 base64 data URI（内嵌进 SVG，离线可用）。 / Turn a local image into a base64 data URI that can be embedded in the SVG and works offline.

    :param path: 图片文件路径
    :return: "data:image/png;base64,..." 字符串

    示例::
        uri = image_to_data_uri("logo.png")
    """
    ext = os.path.splitext(path)[1].lower().lstrip(".")
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
            "gif": "image/gif", "webp": "image/webp", "bmp": "image/bmp",
            "svg": "image/svg+xml"}.get(ext, "application/octet-stream")
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    return f"data:{mime};base64,{data}"


def image_size(path):
    """
    获取图片真实宽高（需要 Pillow，读取失败返回 (0, 0)）。 / Return an image's real width and height (requires Pillow; returns (0, 0) if unreadable).

    示例::
        w, h = image_size("photo.jpg")
    """
    try:
        from PIL import Image
        with Image.open(path) as im:
            return im.size
    except Exception:
        return (0, 0)


# ===========================================================================
# SVG 文件工具
# ===========================================================================
def get_svg_size(svg_file):
    """
    读取 SVG 文件的宽高（解析 width/height 或 viewBox）。 / Read an SVG file's width and height from its width/height attributes or viewBox.

    示例::
        w, h = get_svg_size("icon.svg")
    """
    import xml.etree.ElementTree as ET
    tree = ET.parse(svg_file)
    root = tree.getroot()
    w, h = root.get("width"), root.get("height")
    if w and h:
        return float(str(w).strip("px")), float(str(h).strip("px"))
    vb = root.get("viewBox")
    if vb:
        _, _, w, h = vb.split()
        return float(w), float(h)
    return (0, 0)


def scale_svg_file(svg_file, scale, out_file=None):
    """
    等比缩放 SVG 文件并另存（对应中文版 `缩放SVG图片`）。 / Scale an SVG file proportionally and save the result as a new file.

    :param svg_file: 源 SVG 文件
    :param scale: 缩放倍数
    :param out_file: 输出路径（默认在原名后加 _scaled）

    示例::
        scale_svg_file("icon.svg", 2.0)   # 生成 icon_scaled.svg
    """
    import xml.etree.ElementTree as ET
    tree = ET.parse(svg_file)
    root = tree.getroot()
    w, h = get_svg_size(svg_file)
    root.set("width", str(w * scale))
    root.set("height", str(h * scale))
    if out_file is None:
        base, ext = os.path.splitext(svg_file)
        out_file = f"{base}_scaled{ext}"
    tree.write(out_file, encoding="utf-8", xml_declaration=True)
    return report(t("kind.svg_scaled"), out_file,
                  extra=t("extra.scale", n=fmt_num(scale)))


def import_svg_as_nodes(svg_file, x=0, y=0, scale=None):
    """
    把 SVG 文件解析为节点组（供绘图板 import_svg_as_group 使用）。 / Parse an SVG file into a node group, used by the board's import_svg_as_group.

    :return: (SvgNode 组, 原始宽, 原始高)

    示例（一般通过绘图板调用）::
        g = pen.import_svg_as_group("icon.svg", x=10, y=10, scale=0.5)
    """
    import xml.etree.ElementTree as ET
    tree = ET.parse(svg_file)
    root = tree.getroot()
    ns = "{http://www.w3.org/2000/svg}"

    def _conv(el):
        """递归把 ElementTree 节点转换为 SvgNode。"""
        tag = el.tag.replace(ns, "")
        node = SvgNode(tag, {k.replace(ns, "").replace("{http://www.w3.org/1999/xlink}", "xlink:"): v
                             for k, v in el.attrib.items()})
        if el.text and el.text.strip():
            node.text = el.text.strip()
        for child in el:
            node.add(_conv(child))
        return node

    w, h = get_svg_size(svg_file)
    sx = sy = scale if scale else 1.0
    group = SvgNode("g")
    group.set("transform", f"translate({x},{y}) scale({sx},{sy})")
    inner = SvgNode("g", {
        "xmlns": "http://www.w3.org/2000/svg",
        "xmlns:xlink": "http://www.w3.org/1999/xlink",
    })
    inner.set("viewBox", f"0 0 {w} {h}") if False else None
    inner.add(_conv(root))
    group.add(inner)
    return group, w, h


# ===========================================================================
# 导出工具（PNG / PDF / DOCX）
# ===========================================================================
def has_cairosvg():
    """
    本机是否装了 cairosvg（英文版新增：用于自动挑选导出引擎）。 / Whether cairosvg is available, used to pick the export engine automatically.

    :return: True / False

    示例::
        from malight.tools import has_cairosvg, find_chrome
        has_cairosvg()      # False（没装）
        find_chrome()       # 'C:\\...\\chrome.exe'（可用 Chrome 顶上）
    """
    import importlib.util
    return importlib.util.find_spec("cairosvg") is not None


def export_png_cairo(svg_file, out_png=None, scale=3):
    """
    用 cairosvg 把 SVG 渲染为 PNG（对应中文版 `生成PNG` 的 cairosvg 方式）。 / Render an SVG to PNG with cairosvg.

    没装 cairosvg 时抛 RuntimeError 并给出三条替代方案（含自动改用 Chrome）。

    :param svg_file: SVG 文件
    :param out_png: 输出路径（默认同名 .png）
    :param scale: 放大倍数（默认 3 倍高清导出）
    :raises RuntimeError: 未安装 cairosvg

    示例::
        export_png_cairo("demo.svg", scale=2)
    """
    if not has_cairosvg():
        raise RuntimeError(t("err.need_cairosvg"))
    import cairosvg
    if out_png is None:
        out_png = os.path.splitext(svg_file)[0] + ".png"
    cairosvg.svg2png(url=svg_file, write_to=out_png, scale=scale,
                     background_color="white")
    return report(t("kind.png"), out_png, engine=t("engine.cairosvg"),
                  extra=t("extra.scale", n=fmt_num(scale)))


def export_pdf_cairo(svg_file, out_pdf=None, page=None):
    """
    用 cairosvg 把 SVG 转为 PDF（对应中文版 `生成PDF`）。 / Convert an SVG to PDF with cairosvg.

    页面固定为 SVG 自身尺寸：cairosvg 不参与浏览器排版，**不支持页面设置**
    （纸张 / 页边距 / 缩放）。需要这些就用 ``export_pdf_chrome``；
    传了 ``page`` 会当场报错，而不是静默忽略。

    :raises ValueError: 传了页面设置（err.page_need_chrome）

    示例::

        export_pdf_cairo("report.svg", "report.pdf")
    """
    if page is not None:
        # 先判页面设置：哪怕本机没装 cairosvg，也要给出正确的原因
        raise ValueError(t("err.page_need_chrome"))
    import cairosvg
    if out_pdf is None:
        out_pdf = os.path.splitext(svg_file)[0] + ".pdf"
    cairosvg.svg2pdf(url=svg_file, write_to=out_pdf)
    return report(t("kind.pdf"), out_pdf, engine=t("engine.cairosvg"),
                  extra=t("extra.no_svg_filter"))


# ---------------------------------------------------------------------------
# Chrome 渲染导出（英文版新增：SVG filter/字体/文字排版与浏览器一致）
# ---------------------------------------------------------------------------
def find_chrome():
    """
    查找本机 Chrome 可执行文件（英文版新增）。 / Locate the Chrome executable on this machine.

    查找顺序：环境变量 MALIGHT_CHROME -> 注册表 App Paths ->
    常见安装目录 -> PATH -> Edge（同为 Chromium 内核，渲染一致）。

    :return: chrome.exe 完整路径；找不到返回 None

    示例::
        chrome = find_chrome()
        if chrome:
            export_pdf_chrome("demo.svg", chrome=chrome)
    """
    # 1) 环境变量优先，便于用户指定绿色版/便携版路径
    env_path = os.environ.get("MALIGHT_CHROME")
    if env_path and os.path.exists(env_path):
        return env_path

    candidates = []
    # 2) Windows 注册表（安装版必写）
    try:
        import winreg
        for root in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
            try:
                with winreg.OpenKey(
                        root,
                        r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe") as k:
                    val = winreg.QueryValue(k, None)
                    if val and os.path.exists(val):
                        return val
            except OSError:
                pass
    except ImportError:
        pass

    # 3) 常见安装目录（Windows / macOS / Linux）
    import shutil
    local = os.environ.get("LOCALAPPDATA", "")
    candidates += [
        os.path.join(local, r"Google\Chrome\Application\chrome.exe"),
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/usr/bin/google-chrome", "/usr/bin/google-chrome-stable",
        "/usr/bin/chromium", "/usr/bin/chromium-browser",
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return c

    # 4) PATH
    for name in ("chrome", "google-chrome", "chromium"):
        which = shutil.which(name)
        if which:
            return which

    # 5) Edge 兜底（同为 Chromium 内核，PDF/截图渲染结果与 Chrome 一致）
    for c in (os.path.join(local, r"Microsoft\Edge\Application\msedge.exe"),
              r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
              r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"):
        if os.path.exists(c):
            return c
    return None


def _chrome_html_wrapper(svg_file, background="white", page=None):
    """
    把 SVG 内嵌进一个临时 HTML（供 Chrome 打印/截图）。

    内嵌（而非 <img> 引用）保证 SVG filter / 动画 / 字体完整生效；
    ``@page size`` 默认取 SVG 自身尺寸，PDF 页边距为 0、不会截断。

    :param page: 页面设置（PageSetup）；None = 页面就是画布尺寸。
                 纸张与缩放只写进 ``@media print``，所以 PNG 截图不受影响。
    """
    import xml.etree.ElementTree as ET
    w, h = get_svg_size(svg_file)
    with open(svg_file, "r", encoding="utf-8") as f:
        svg_text = f.read()
    # 去掉 XML 声明行，SVG 内容可直接内嵌进 HTML
    if svg_text.lstrip().startswith("<?xml"):
        svg_text = svg_text.lstrip()[svg_text.lstrip().index("?>") + 2:]

    if page is None:
        page = PageSetup()
    page_css, _, _, _ = page.resolve(w, h)
    print_css = page.print_css(w, h)

    html = (
        "<!DOCTYPE html><html><head><meta charset='utf-8'>"
        "<style>"
        "@page {{ size: {page}; margin: 0; }}"
        "html, body {{ margin: 0; padding: 0; background: {bg}; }}"
        "svg {{ display: block; }}"
        "{print_css}"
        "</style></head><body>{svg}</body></html>"
    ).format(page=page_css, bg=background, svg=svg_text, print_css=print_css)
    return html, w, h


def _run_chrome(chrome, args, timeout=60):
    """调起 Chrome headless 执行命令（内部方法）。"""
    import subprocess
    cmd = [chrome, "--headless", "--disable-gpu", "--disable-extensions",
           "--no-first-run", "--no-default-browser-check"] + args
    result = subprocess.run(cmd, capture_output=True, timeout=timeout)
    return result.returncode


# Chrome 的 --window-size 指的是「窗口外框」，页面视口比它小一圈
# （Windows 上约等于标题栏高度 + 左右边框）。按画布尺寸开窗时，页面只
# 渲染在更小的视口里，而 --screenshot 输出的是整个外框尺寸 ——
# 于是画布底部被截掉、多出一条空白（2026-09 修复）。
# 做法：先探测这个差值，把窗口开大一圈；截完再把多出的边裁掉。
_CHROME_PAD_CACHE = {}


def _chrome_viewport_pad(chrome, probe_w=800, probe_h=800):
    """
    探测 headless Chrome「窗口外框 − 页面视口」的差值 (pad_x, pad_y)（内部方法）。 / Probe the (window frame − viewport) delta of headless Chrome (internal).

    结果按 Chrome 路径缓存在进程内，同一进程多次导出只探测一次。
    探测失败、或结果落在明显不合理的范围外，回退到 Windows 常见值 (16, 95)。
    """
    import re as _re
    import subprocess
    import tempfile
    if chrome in _CHROME_PAD_CACHE:
        return _CHROME_PAD_CACHE[chrome]
    pad = (16, 95)
    html = ("<!DOCTYPE html><html><head><meta charset='utf-8'></head><body>"
            "<script>document.body.textContent='padprobe='+innerWidth+'x'"
            "+innerHeight;</script></body></html>")
    tmp = tempfile.NamedTemporaryFile("w", suffix=".html", delete=False,
                                      encoding="utf-8")
    try:
        tmp.write(html)
        tmp.close()
        result = subprocess.run(
            [chrome, "--headless", "--disable-gpu", "--disable-extensions",
             "--no-first-run", "--no-default-browser-check", "--hide-scrollbars",
             "--dump-dom", f"--window-size={probe_w},{probe_h}",
             "file:///" + tmp.name.replace("\\", "/")],
            capture_output=True, timeout=60)
        text = (result.stdout or b"").decode("utf-8", "replace")
        m = _re.search(r"padprobe=(\d+)x(\d+)", text)
        if m:
            dx = probe_w - int(m.group(1))
            dy = probe_h - int(m.group(2))
            if 0 <= dx <= 80 and 0 <= dy <= 240:
                pad = (dx, dy)
    except (OSError, subprocess.SubprocessError):
        pass
    finally:
        try:
            os.remove(tmp.name)
        except OSError:
            pass
    _CHROME_PAD_CACHE[chrome] = pad
    return pad


def _png_crop_topleft(path, width, height):
    """
    把 PNG 原地裁成 width x height，保留左上角（纯标准库，内部方法）。 / Crop a PNG in place to width x height, keeping the top-left corner (pure stdlib, internal).

    PNG 的行过滤只引用「本行左侧」与「上一行」的像素，所以裁掉右侧和底部
    以后，留下的像素连同它们原本的过滤字节依然自洽 —— 不必解码、也无需
    重算 filter，纯字节搬运即可（很快）。

    仅支持 8 位、非隔行的灰度 / RGB / 带 alpha 图（Chrome 截图正是这一类）；
    其它格式返回 False，由调用方决定忽略（画面完整、只是多一圈边）。
    """
    import struct
    import zlib
    try:
        with open(path, "rb") as f:
            data = f.read()
    except OSError:
        return False
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return False
    ihdr = None
    idat = []
    pos = 8
    while pos + 12 <= len(data):
        (length,) = struct.unpack(">I", data[pos:pos + 4])
        ctype = data[pos + 4:pos + 8]
        if ctype == b"IHDR":
            ihdr = data[pos + 8:pos + 8 + length]
        elif ctype == b"IDAT":
            idat.append(data[pos + 8:pos + 8 + length])
        elif ctype == b"IEND":
            break
        pos += 12 + length
    if ihdr is None or not idat:
        return False
    w, h, depth, color, comp, filt, interlace = struct.unpack(">IIBBBBB", ihdr)
    channels = {0: 1, 2: 3, 4: 2, 6: 4}.get(color)
    if depth != 8 or interlace != 0 or channels is None:
        return False
    nw, nh = min(int(width), w), min(int(height), h)
    if nw <= 0 or nh <= 0 or (nw == w and nh == h):
        return False
    try:
        raw = zlib.decompress(b"".join(idat))
    except zlib.error:
        return False
    stride = w * channels
    keep = nw * channels
    if len(raw) < (stride + 1) * nh:
        return False
    body = bytearray()
    for y in range(nh):
        off = y * (stride + 1)
        body += raw[off:off + 1 + keep]      # 过滤字节 + 本行前 keep 个字节
    new_ihdr = struct.pack(">IIBBBBB", nw, nh, depth, color, comp, filt, interlace)

    def _chunk(tag, payload):
        return (struct.pack(">I", len(payload)) + tag + payload
                + struct.pack(">I", zlib.crc32(tag + payload) & 0xFFFFFFFF))
    out = (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", new_ihdr)
           + _chunk(b"IDAT", zlib.compress(bytes(body), 6))
           + _chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(out)
    return True


def export_pdf_chrome(svg_file, out_pdf=None, chrome=None, page=None,
                      page_size=None, page_scale=None, page_margin=0):
    """
    用 Chrome 无头模式把 SVG 打印为 PDF（英文版新增）。 / Print an SVG to PDF using headless Chrome.

    与 cairosvg 相比：SVG filter（投影/发光/模糊等）、文字排版、
    系统字体渲染与浏览器完全一致 —— cairosvg 不渲染 filter。

    默认 PDF 页面就等于画布尺寸（页边距 0），内容不会被截断。
    想印到真实纸张上（例如把任意画布铺到 A4）就传 ``page`` 或
    ``page_size``：此时页面按纸张设定，内容等比缩放到纸张内并留出页边距。

    :param svg_file: SVG 文件
    :param out_pdf: 输出路径（默认同名 .pdf）
    :param chrome: Chrome 路径（默认自动查找，可用环境变量 MALIGHT_CHROME 指定）
    :param page: 页面设置 ``PageSetup``（纸张 / 页边距 / 缩放）；最高优先级
    :param page_size: 纸张的快捷写法（"A4" / "A4 landscape" / (宽mm, 高mm)）；
                      None = 跟随画布
    :param page_scale: 内容缩放（None = 按纸张自动适配，且不放大）
    :param page_margin: 页边距（px，配合 page_size 使用）
    :raises RuntimeError: 找不到 Chrome 或打印失败
    :raises ValueError: 纸张名不认识（err.page_size_unknown）

    示例::

        export_pdf_chrome("fx_demo.svg")           # 页面 = 画布尺寸
        export_pdf_chrome("fx_demo.svg", page_size="A4")           # 铺到 A4 纸
        export_pdf_chrome("fx_demo.svg", page_size="A4",
                          page_margin=20)          # A4 + 20px 页边距
        export_pdf_chrome("fx_demo.svg", page=PageSetup("A4", margin=24))
    """
    import tempfile
    if chrome is None:
        chrome = find_chrome()
    if not chrome:
        raise RuntimeError(t("err.chrome_missing_pdf_tools"))
    if out_pdf is None:
        out_pdf = os.path.splitext(svg_file)[0] + ".pdf"
    out_pdf = os.path.abspath(out_pdf)

    if page is None and (page_size is not None or page_scale is not None
                         or page_margin):
        page = PageSetup(page_size, margin=page_margin, scale=page_scale)

    html, _, _ = _chrome_html_wrapper(svg_file, page=page)
    tmp = tempfile.NamedTemporaryFile("w", suffix=".html", delete=False,
                                      encoding="utf-8")
    try:
        tmp.write(html)
        tmp.close()
        code = _run_chrome(chrome, [
            "--no-pdf-header-footer",
            f"--print-to-pdf={out_pdf}",
            "file:///" + tmp.name.replace("\\", "/"),
        ])
    finally:
        try:
            os.remove(tmp.name)
        except OSError:
            pass
    if code != 0 or not os.path.exists(out_pdf) or os.path.getsize(out_pdf) == 0:
        raise RuntimeError(t("err.chrome_pdf_failed", code=code, path=out_pdf))
    return report(t("kind.pdf"), out_pdf, engine=t("engine.chrome"),
                  extra=t("extra.fx_full"))


def export_png_chrome(svg_file, out_png=None, scale=1, background="white",
                      chrome=None):
    """
    用 Chrome 无头模式把 SVG 截图为 PNG（英文版新增，支持 SVG filter）。 / Screenshot an SVG to PNG using headless Chrome; SVG filters are supported.

    :param scale: 放大倍数（输出 = SVG 尺寸 x scale）
    :param background: 页面背景色（"white" / "transparent"）

    示例::
        export_png_chrome("fx_demo.svg", scale=2)   # 2 倍高清截图
    """
    import math as _math
    import tempfile
    if chrome is None:
        chrome = find_chrome()
    if not chrome:
        raise RuntimeError(t("err.chrome_missing_png_tools"))
    if out_png is None:
        out_png = os.path.splitext(svg_file)[0] + ".png"
    out_png = os.path.abspath(out_png)

    bg = "transparent" if background == "transparent" else background
    html, w, h = _chrome_html_wrapper(svg_file, background=bg)

    # --window-size 是窗口外框：视口比它小一圈，按画布尺寸开窗会渲染不全
    # （画布底部被截、下方留白）。补上探测到的差值，截完再裁回精确尺寸。
    pad_x, pad_y = _chrome_viewport_pad(chrome)
    win_w = int(_math.ceil(w)) + pad_x
    win_h = int(_math.ceil(h)) + pad_y

    tmp = tempfile.NamedTemporaryFile("w", suffix=".html", delete=False,
                                      encoding="utf-8")
    try:
        tmp.write(html)
        tmp.close()
        args = ["--hide-scrollbars",
                f"--window-size={win_w},{win_h}",
                # 用设备缩放因子放大整页渲染；只放大窗口的话 SVG 仍按原始
                # 尺寸画在左上角，其余全是白边（真 bug，2026-09 修复）
                f"--force-device-scale-factor={scale}",
                f"--screenshot={out_png}",
                "file:///" + tmp.name.replace("\\", "/")]
        if background == "transparent":
            args.insert(0, "--default-background-color=00000000")
        code = _run_chrome(chrome, args)
    finally:
        try:
            os.remove(tmp.name)
        except OSError:
            pass
    if code != 0 or not os.path.exists(out_png) or os.path.getsize(out_png) == 0:
        raise RuntimeError(t("err.chrome_png_failed", code=code, path=out_png))
    # 裁掉补偿多出来的那圈外框，输出严格 = 画布尺寸 x scale
    _png_crop_topleft(out_png, int(_math.ceil(w * scale)),
                      int(_math.ceil(h * scale)))
    return report(t("kind.png"), out_png, engine=t("engine.chrome"),
                  extra=t("extra.scale_fx", n=fmt_num(scale)))


def export_docx_from_pdf(pdf_file, out_docx=None):
    """
    把 PDF 转为 DOCX（需要 pdf2docx 库，对应中文版 `生成DOCX`）。 / Convert a PDF to DOCX (requires the pdf2docx library).

    示例::
        export_docx_from_pdf("report.pdf", "report.docx")
    """
    if out_docx is None:
        out_docx = os.path.splitext(pdf_file)[0] + ".docx"
    try:
        from pdf2docx import parse
    except ImportError:
        raise NotImplementedError(t("err.need_pdf2docx"))
    parse(pdf_file, out_docx)
    return report("DOCX", out_docx, engine="pdf2docx")


# ===========================================================================
# 几何工具
# ===========================================================================
def arrow_path_points(start, end, style="倒钩", arrow_length=10, arrow_angle=30):
    """
    计算箭头三角形的三个顶点（对应中文版 `获取箭头路径` 的核心）。 / Compute the three vertices of an arrow head triangle.

    :param start: 起点元组
    :param end: 终点元组（箭头指向）
    :param style: ArrowStyle 样式串
    :param arrow_length: 箭头长度
    :param arrow_angle: 张角（度，半角）

    :return: (箭头三角形顶点列表, 线段实际终点) —— 线段终点按箭头长度回缩

    示例::
        tri, line_end = arrow_path_points((0, 0), (100, 0))
    """
    x1, y1 = start
    x2, y2 = end
    ang = math.atan2(y2 - y1, x2 - x1)
    half = math.radians(arrow_angle)
    bx, by = x2 - arrow_length * math.cos(ang), y2 - arrow_length * math.sin(ang)
    p1 = (bx + arrow_length * math.sin(half) * math.sin(ang),
          by - arrow_length * math.sin(half) * math.cos(ang))
    p2 = (bx - arrow_length * math.sin(half) * math.sin(ang),
          by + arrow_length * math.sin(half) * math.cos(ang))
    return [end, p1, p2], (bx, by)


def wave_line_points(start, end, amplitude, periods):
    """
    计算正弦波浪线的采样顶点（对应中文版 `画波浪线` 的核心）。 / Sample the vertices of a sine wave line.

    :param start: 起点
    :param end: 终点
    :param amplitude: 波幅
    :param periods: 波峰数
    :return: 顶点列表（每周期 24 段）

    示例::
        pts = wave_line_points((50, 100), (350, 100), 15, 4)
        pen.polyline(pts)
    """
    x1, y1 = start
    x2, y2 = end
    length = math.hypot(x2 - x1, y2 - y1)
    ang = math.atan2(y2 - y1, x2 - x1)
    n = max(int(periods) * 24, 8)
    pts = []
    for i in range(n + 1):
        t = i / n
        along = t * length
        off = amplitude * math.sin(t * periods * 2 * math.pi)
        # 沿方向平移 + 法向偏移
        px = x1 + along * math.cos(ang) - off * math.sin(ang)
        py = y1 + along * math.sin(ang) + off * math.cos(ang)
        pts.append((px, py))
    return pts


def regular_polygon_points(cx, cy, radius, n, start_angle=-90):
    """
    正 N 边形顶点（对应中文版 `N边形路径`）。 / Vertices of a regular N-sided polygon.

    示例::
        pts = regular_polygon_points(200, 150, 80, 6)   # 正六边形
        pen.polygon(pts)
    """
    return [(cx + radius * math.cos(math.radians(start_angle + i * 360 / n)),
             cy + radius * math.sin(math.radians(start_angle + i * 360 / n)))
            for i in range(n)]


def star_points(cx, cy, radius, n, inner_ratio=0.382, start_angle=-90):
    """
    N 角星顶点（外角 + 内角交替，对应中文版 `N角星路径`）。 / Vertices of an N-pointed star, alternating outer and inner corners.

    :param inner_ratio: 内角点半径占外径的比例

    示例::
        pts = star_points(200, 150, 100, 5)   # 五角星
        pen.polygon(pts, fill_color="gold")
    """
    pts = []
    for i in range(n * 2):
        r = radius if i % 2 == 0 else radius * inner_ratio
        a = math.radians(start_angle + i * 180.0 / n)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def heart_points(cx, cy, size, samples=60):
    """
    爱心曲线顶点（对应中文版 `爱心路径`）。 / Vertices of a heart curve.

    :param size: 爱心尺寸（半径量级）
    :return: 顶点列表

    示例::
        pen.polygon(heart_points(200, 150, 80), fill_color="red")
    """
    pts = []
    for i in range(samples):
        t = math.pi * 2 * i / samples
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        pts.append((cx + x * size / 18.0, cy + y * size / 18.0))
    return pts


def point_list_bbox(points):
    """
    顶点列表包围盒。 / Bounding box of a point list.

    示例::
        print(point_list_bbox([(0, 0), (10, 5)]))   # (0, 0, 10, 5)
    """
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return (min(xs), min(ys), max(xs), max(ys))


# ===========================================================================
# 滤镜工具（英文版完整支持，SVG filter）
# ===========================================================================
def create_blur_filter(board, std_deviation=3, id_=None):
    """
    创建高斯模糊滤镜定义（对应中文版 `滤镜工具集.模糊滤镜`）。 / Create a Gaussian blur filter definition.

    :param board: 绘图板
    :param std_deviation: 模糊强度
    :return: 滤镜 id（用于 el.update(extra={"filter": f"url(#{fid})"})）

    示例::
        fid = create_blur_filter(pen, 4)
        pen.circle(100, 100, 50, fill_color="red",
                        extra={"filter": f"url(#{fid})"})
    """
    fid = id_ or f"filter_blur_{len(board.defs_node.children)}"
    fe = SvgNode("filter", {"id": fid, "x": "-50%", "y": "-50%",
                            "width": "200%", "height": "200%"})
    fe.add(SvgNode("feGaussianBlur", {"stdDeviation": std_deviation}))
    board.defs_node.add(fe)
    return fid


def create_drop_shadow_filter(board, dx=3, dy=3, std_deviation=3,
                              shadow_color="black", opacity=0.5, id_=None):
    """
    创建投影滤镜（英文版新增能力，对应中文版未提供的 drop-shadow）。 / Create a drop-shadow filter, which the Chinese edition did not provide.

    示例::
        fid = create_drop_shadow_filter(pen, dx=5, dy=5)
        pen.rect(50, 50, 150, 80, fill_color="gold",
                      extra={"filter": f"url(#{fid})"})
    """
    fid = id_ or f"filter_shadow_{len(board.defs_node.children)}"
    fe = SvgNode("filter", {"id": fid, "x": "-50%", "y": "-50%",
                            "width": "200%", "height": "200%"})
    fe.add(SvgNode("feDropShadow", {"dx": dx, "dy": dy, "stdDeviation": std_deviation,
                                    "flood-color": shadow_color, "flood-opacity": opacity}))
    board.defs_node.add(fe)
    return fid


def create_glow_filter(board, std_deviation=4, id_=None):
    """
    创建发光滤镜（英文版新增能力）。 / Create a glow filter.

    示例::
        fid = create_glow_filter(pen, 6)
        pen.text(100, 100, "NEON", font_size=48, fill_color="#0ff",
                       extra={"filter": f"url(#{fid})"})
    """
    fid = id_ or f"filter_glow_{len(board.defs_node.children)}"
    fe = SvgNode("filter", {"id": fid, "x": "-50%", "y": "-50%",
                            "width": "200%", "height": "200%"})
    blur = SvgNode("feGaussianBlur", {"stdDeviation": std_deviation, "result": "blur"})
    merge = SvgNode("feMerge")
    merge.add(SvgNode("feMergeNode", {"in": "blur"}))
    merge.add(SvgNode("feMergeNode", {"in": "SourceGraphic"}))
    fe.add(blur)
    fe.add(merge)
    board.defs_node.add(fe)
    return fid


# ===========================================================================
# 文字工具
# ===========================================================================
def text_width(font_name, font_size, text):
    """
    估算文字宽度（需要 Pillow 加载系统字体；失败时按 1.0x 字号估算）。 / Estimate how wide a text will be using Pillow and a system font, falling back to one em per character.

    示例::
        w = text_width("msyh.ttc", 24, "你好世界")
    """
    try:
        from PIL import ImageFont
        f = ImageFont.truetype(font_name, int(font_size))
        return f.getbbox(text)[2]
    except Exception:
        return font_size * len(text)


def find_font_file(family):
    """
    在 Windows 字体目录中查找字体文件（对应中文版 `字体查找器` 的简化版）。 / Find a font file in the Windows font directory.

    :param family: 字体族名，如 "KaiTi"
    :return: 字体文件完整路径；找不到返回 None

    示例::
        path = find_font_file("KaiTi")   # C:/Windows/Fonts/simkai.ttf
    """
    font_dirs = [r"C:\Windows\Fonts", os.path.expanduser("~/AppData/Local/Microsoft/Windows/Fonts")]
    aliases = {"KaiTi": ["simkai.ttf"], "SimHei": ["simhei.ttf"],
               "SimSun": ["simsun.ttc"], "FangSong": ["simfang.ttf"],
               "Microsoft YaHei": ["msyh.ttc", "msyh.ttf"],
               "Microsoft YaHei Light": ["msyhl.ttc"],
               "Arial": ["arial.ttf"], "Times New Roman": ["times.ttf"],
               "Courier New": ["cour.ttf"], "Verdana": ["verdana.ttf"],
               "Tahoma": ["tahoma.ttf"], "Georgia": ["georgia.ttf"]}
    for name in aliases.get(family, [family.lower() + ".ttf"]):
        for d in font_dirs:
            p = os.path.join(d, name)
            if os.path.exists(p):
                return p
    return None


def text_to_path_d(text, font_file, font_size, letter_spacing=0):
    """
    文字转路径（对应中文版 `文字转路径`，需要 fontTools 库）。 / Convert text into path data (requires the fontTools library).

    :param text: 文字内容
    :param font_file: 字体文件路径（可用 find_font_file 查询）
    :param font_size: 字号
    :param letter_spacing: 额外字间距
    :return: (字形列表 [(字形d, x偏移), ...], 变换串, 总宽, 总高)

    字形 d 是字体单位坐标，需配合返回的变换串使用
    （board.text_to_path 已封装好，一般直接调用它）。

    示例（底层用法）::
        glyphs, transform, w, h = text_to_path_d("Hi", font_path, 48)
    """
    try:
        from fontTools.ttLib import TTFont
        from fontTools.pens.svgPathPen import SVGPathPen
    except ImportError:
        raise NotImplementedError(t("err.need_fonttools_path"))
    font = TTFont(font_file)
    glyph_set = font.getGlyphSet()
    cmap = font.getBestCmap()
    upm = font["head"].unitsPerEm
    scale = font_size / upm
    pen_x = 0.0
    glyphs = []
    for ch in text:
        glyph_name = cmap.get(ord(ch))
        if glyph_name is None:
            pen_x += font_size * 0.5 + letter_spacing
            continue
        glyph = glyph_set[glyph_name]
        spen = SVGPathPen(glyph_set)
        glyph.draw(spen)
        d = spen.getCommands()
        if d:
            glyphs.append((d, pen_x))
        pen_x += glyph.width * scale + letter_spacing
    transform = f"scale({fmt_num(scale, 6)},{fmt_num(-scale, 6)})"
    return glyphs, transform, pen_x, font_size
