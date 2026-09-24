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

import base64
import math
import os
import re
import stat
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
#: 导出提示用的**加粗**色系（``paint_path`` / ``report`` 一直用它，取值别改）
_COLORS = {
    "green": "\x1b[1;32m", "red": "\x1b[1;31m", "yellow": "\x1b[1;33m",
    "blue": "\x1b[1;34m", "cyan": "\x1b[1;36m", "grey": "\x1b[1;30m",
    "magenta": "\x1b[1;35m", "white": "\x1b[1;37m",
}
#: 亮色系（ANSI 90-97）：比加粗系更鲜艳，彩色消息默认用它
_BRIGHT = {
    "black": "\x1b[90m", "red": "\x1b[91m", "green": "\x1b[92m",
    "yellow": "\x1b[93m", "blue": "\x1b[94m", "magenta": "\x1b[95m",
    "cyan": "\x1b[96m", "white": "\x1b[97m", "grey": "\x1b[90m",
}
#: 颜色名别名：``purple`` 与 ``magenta`` 同色，``gray`` 与 ``grey`` 同色
_COLOR_ALIAS = {"purple": "magenta", "gray": "grey"}

#: 环境变量里视为「关」的取值（空串也算关）
_FALSEY = ("", "0", "false", "no", "off")

#: 「不是终端、却照样会渲染 ANSI」的宿主标记：IDE 的运行/调试窗口。
#: 这类窗口把标准输出接成管道（``isatty()`` 恒为 False），但窗口本身会解析
#: 转义序列 —— 只认 isatty 的话，用户在 PyCharm 里一条彩色消息都看不到。
#: Host markers for consoles that render ANSI even though stdout is a pipe
#: (IDE run/debug windows). Without them PyCharm users never see any color.
_ANSI_HOST_ENV = ("PYCHARM_HOSTED", "TERM_PROGRAM", "VSCODE_PID",
                  "JETBRAINS_IDE", "TERMINAL_EMULATOR")

#: None = 自动（跟随 stdout 是否终端）；True / False = set_color() 强制
_COLOR_FORCED = None
_VT_READY = False


def _windows_ansi() -> None:
    """Windows 控制台打开 VT 转义支持（内部方法，只需一次）。 / Enable VT escape processing on the Windows console once (internal)."""
    global _VT_READY
    if _VT_READY or os.name != "nt":
        return
    _VT_READY = True
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        # -11 = STD_OUTPUT_HANDLE，-12 = STD_ERROR_HANDLE：两个都开，
        # 彩色消息既能进 stdout 也能进 stderr。
        for std_handle in (-11, -12):
            handle = kernel32.GetStdHandle(std_handle)
            mode = ctypes.c_uint32()
            if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
                kernel32.SetConsoleMode(handle, mode.value | 0x0004)   # ENABLE_VT
    except Exception:                                # noqa: BLE001
        pass                                         # 老控制台：退化成无色


def set_color(enabled=None) -> None:
    """
    打开/关闭终端颜色；``None`` 表示回到自动判断。 / Turn terminal colors on or off; None restores auto-detection.

    自动判断 = 输出是终端或「会渲染 ANSI 的宿主窗口（PyCharm 运行窗口等）」，
    且没被重定向到磁盘文件、也没设 ``NO_COLOR``。

    也可以用环境变量控制：``MALIGHT_COLOR=1`` 开、``=0`` 关；
    ``FORCE_COLOR`` / ``CLICOLOR_FORCE`` 强制开；``NO_COLOR``（事实标准，
    设了就关）优先级最高。

    颜色只影响提示文字，**不影响任何返回值与文件内容**。

    示例::
        malight.set_color(False)     # 日志重定向时彻底关掉转义
        malight.set_color(None)      # 交回自动判断
    """
    global _COLOR_FORCED
    _COLOR_FORCED = None if enabled is None else bool(enabled)


def _env_forced_on() -> bool:
    """
    环境变量是否强制上色（内部方法）。 / Whether an env var forces colors on (internal).

    ``FORCE_COLOR`` / ``CLICOLOR_FORCE`` 是社区事实标准：设了非空且不是
    ``0/false/no/off`` 就上色，哪怕输出被接成管道。
    """
    for name in ("FORCE_COLOR", "CLICOLOR_FORCE"):
        value = os.environ.get(name)
        if value is not None and value.strip().lower() not in _FALSEY:
            return True
    return False


def _fd_stat_mode(stream):
    """
    取输出流对应文件描述符的 stat mode（内部方法）。 / stat mode of the stream's file descriptor (internal).

    内存缓冲（``io.StringIO``、测试框架的输出捕获）没有真实 fd，返回 None。
    """
    try:
        fileno = getattr(stream, "fileno", None)
        fd = fileno() if callable(fileno) else None
        if fd is None:
            return None
        return os.fstat(fd).st_mode
    except Exception:                                # noqa: BLE001
        return None


def _host_renders_ansi(stream) -> bool:
    """
    宿主（IDE 运行窗口等）虽非终端但会渲染 ANSI 时返回 True（内部方法）。 / True when a non-tty host still renders ANSI (internal).

    只认「进程真实的标准输出」——两类情况仍然判无色：

    * 内存缓冲（没有文件描述符）：测试捕获、``io.StringIO`` 之类的容器不会
      渲染任何东西，染色只会污染断言里的字符串；
    * 重定向到磁盘文件（``> out.txt``）：宁可无色，也不要把转义码写进日志。
    """
    if not any(os.environ.get(name) for name in _ANSI_HOST_ENV):
        return False
    mode = _fd_stat_mode(stream)
    if mode is None or stat.S_ISREG(mode):
        return False
    _windows_ansi()
    return True


def _auto_color(stream) -> bool:
    """
    自动判断某个输出流要不要上色（内部方法）。 / Decide whether a given stream should be colored when nothing is forced (internal).

    优先级：``NO_COLOR``（事实标准，设了就关）→ ``MALIGHT_COLOR`` 环境变量
    → ``FORCE_COLOR`` / ``CLICOLOR_FORCE`` → 该流是不是终端
    → 该流是不是「非终端但会渲染 ANSI」的宿主（IDE 运行窗口，且没被重定向到文件）。
    """
    if "NO_COLOR" in os.environ:                     # 事实标准：设了就关
        return False
    env = os.environ.get("MALIGHT_COLOR", "").strip().lower()
    if env:
        return env not in _FALSEY
    if _env_forced_on():
        return True
    try:
        if stream.isatty():
            _windows_ansi()
            return True
    except Exception:                                # noqa: BLE001
        return False
    return _host_renders_ansi(stream)


def _stream_enabled(stream) -> bool:
    """
    按指定的输出流判断是否上色（内部方法）。 / Whether the given output stream should be colored (internal).

    ``stream`` 为 None 时等同于 stdout —— 与 :func:`color_enabled` 完全一致，
    所以 ``print_red("x")`` 与 ``color_enabled()`` 永远同一个答案。
    """
    if _COLOR_FORCED is not None:
        return _COLOR_FORCED
    return _auto_color(sys.stdout if stream is None else stream)


def color_enabled() -> bool:
    """
    当前是否给终端输出上色（按 stdout 判断）。 / Whether terminal colors are currently on, judged by stdout.

    自动判断 = stdout 是终端，或「非终端但会渲染 ANSI 的宿主窗口」
    （PyCharm 运行窗口等，``isatty()`` 为 False 却有颜色），且没被重定向到
    磁盘文件、也没设 ``NO_COLOR``。
    也可以用环境变量控制：``MALIGHT_COLOR=1`` 开、``=0`` 关；
    ``FORCE_COLOR`` / ``CLICOLOR_FORCE`` 强制开；``NO_COLOR``（事实标准，
    设了就关）优先级最高。

    颜色只影响打印出来的文字，**不影响任何返回值与文件内容**。

    示例::
        print(malight.tools.color_enabled())
    """
    if _COLOR_FORCED is not None:
        return _COLOR_FORCED
    return _auto_color(sys.stdout)


def _code(color, bright=False) -> str:
    """
    取颜色对应的 ANSI 序列（内部方法）。 / ANSI escape for a color name (internal).

    认不出颜色名时返回空串（= 不上色），而不是抛异常 —— 颜色只是装饰，
    不该让程序挂掉；``purple`` / ``gray`` 这类别名在这里归一化。
    """
    name = _COLOR_ALIAS.get(color, color)
    if bright:
        return _BRIGHT.get(name, _COLORS.get(name, ""))
    return _COLORS.get(name, "")


def paint(text, color=None, bold=False, bright=False) -> str:
    """
    给一段文字加 ANSI 样式（未启用颜色时原样返回）。 / Wrap text in ANSI styling, or return it unchanged when colors are off.

    :param text: 原文字
    :param color: "green" / "red" / "yellow" / "blue" / "magenta"（或 "purple"）/
                  "cyan" / "white" / "grey"（或 "gray"）
    :param bold: 是否加粗
    :param bright: 是否用亮色系（ANSI 90-97，比加粗系更鲜艳）
    :return: 可直接 print 的字符串

    示例::
        print(paint("导出成功", color="green", bold=True))
        print(paint("导出失败", color="red", bright=True))
    """
    if not color_enabled():
        return text
    return "{}{}{}".format(_code(color, bright) if color else "",
                           _BOLD if bold else "", text) + _RESET


def paint_path(message, path) -> str:
    """
    让一行「文件已保存」提示更醒目：整行加粗、其中的路径绿色。 / Emphasise a message line: bold it and paint the file path green.

    未启用颜色（重定向到磁盘文件 / 非终端 / ``NO_COLOR``）时原样返回。
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
# 彩色消息（英文版新增：print_red / print_green ... 一行打印醒目提示）
# ===========================================================================
def print_color(message, color="white", bold=False, bright=True, *,
                end="\n", file=None) -> None:
    """
    打印一行彩色消息（未启用颜色时原样打印）。 / Print one colored message line, or plain text when colors are off.

    :param message: 消息文字（不是字符串会自动 ``str()``）
    :param color: "red" / "green" / "yellow" / "blue" / "magenta"（或 "purple"）/
                  "cyan" / "white" / "grey"（或 "gray"）/ "black"
    :param bold: 是否加粗
    :param bright: 是否用亮色系（ANSI 90-97，彩色消息默认用它）
    :param end: 行尾字符（同内置 ``print``）
    :param file: 输出流（None = stdout；传 ``sys.stderr`` 时按那个流判断上色）
    :return: None

    是否上色由 :func:`set_color` / ``NO_COLOR`` / ``MALIGHT_COLOR`` 与目标流
    共同决定：**IDE 的运行窗口（PyCharm 等）虽然是管道、``isatty()`` 为
    False，但窗口本身会渲染 ANSI，所以照样上色**；只有把输出重定向到磁盘
    文件（``> out.txt``）时才自动退化成纯文本，不会混进转义码。
    想要「带色字符串」自己组装（不打印）就用 :func:`paint`。

    ``print_red`` 等速写函数只是把 ``color`` 固定住而已，``end`` / ``file``
    同样是**关键字参数**（与内置 ``print`` 的 ``end`` / ``file`` 一致）：
    ``print_red("x", end="")`` 不换行，而 ``print_red("x", True)`` 会当场报
    TypeError，不会把 True 悄悄当成别的参数。

    示例::

        print_color("构建失败", color="red")
        print_color("构建失败", color="red", file=sys.stderr, bold=True)
    """
    text = str(message)
    if _stream_enabled(file):
        text = "{}{}{}".format(_code(color, bright),
                               _BOLD if bold else "", text) + _RESET
    print(text, end=end, file=file)


def print_red(message, *, end="\n", file=None) -> None:
    """
    用红色打印一行消息。 / Print one message line in red.

    等价 ``print_color(message, color="red")``（亮色系、不加粗）。

    示例::
        print_red("构建失败")
    """
    print_color(message, color="red", end=end, file=file)


def print_green(message, *, end="\n", file=None) -> None:
    """
    用绿色打印一行消息。 / Print one message line in green.

    等价 ``print_color(message, color="green")``。

    示例::
        print_green("导出完成")
    """
    print_color(message, color="green", end=end, file=file)


def print_yellow(message, *, end="\n", file=None) -> None:
    """
    用黄色打印一行消息。 / Print one message line in yellow.

    等价 ``print_color(message, color="yellow")``。

    示例::
        print_yellow("字体缺失，已回退默认字体")
    """
    print_color(message, color="yellow", end=end, file=file)


def print_blue(message, *, end="\n", file=None) -> None:
    """
    用蓝色打印一行消息。 / Print one message line in blue.

    等价 ``print_color(message, color="blue")``。

    示例::
        print_blue("当前引擎：Chrome")
    """
    print_color(message, color="blue", end=end, file=file)


def print_magenta(message, *, end="\n", file=None) -> None:
    """
    用紫红色打印一行消息（``purple`` 与之同色）。 / Print one message line in magenta; "purple" is the same color.

    等价 ``print_color(message, color="magenta")``。

    示例::
        print_magenta("彩蛋")
    """
    print_color(message, color="magenta", end=end, file=file)


def print_cyan(message, *, end="\n", file=None) -> None:
    """
    用青色打印一行消息。 / Print one message line in cyan.

    等价 ``print_color(message, color="cyan")``。

    示例::
        print_cyan("调试信息")
    """
    print_color(message, color="cyan", end=end, file=file)


def print_white(message, *, end="\n", file=None) -> None:
    """
    用白色打印一行消息。 / Print one message line in white.

    等价 ``print_color(message, color="white")``。

    示例::
        print_white("普通提示")
    """
    print_color(message, color="white", end=end, file=file)


def print_grey(message, *, end="\n", file=None) -> None:
    """
    用灰色打印一行消息（``gray`` 同义）。 / Print one message line in grey; "gray" is the same color.

    等价 ``print_color(message, color="grey")``。

    示例::
        print_grey("（可忽略）")
    """
    print_color(message, color="grey", end=end, file=file)


# ---------------------------------------------------------------------------
# 中文别名：沿用中文版《神笔码靓》的名字（打印红色消息、打印绿色消息 …），
# 方便老脚本零改动搬过来。它们**指向上面同一批函数**，行为完全一致 ——
# 因为是普通赋值，名字写错会在导入时直接 NameError，不会静默失效。
# Chinese aliases carrying the Chinese edition's names so that old scripts keep
# working unchanged. They are the very same function objects; a typo here would
# raise NameError at import time instead of failing silently.
# ---------------------------------------------------------------------------
打印红色消息 = print_red
打印绿色消息 = print_green
打印黄色消息 = print_yellow
打印蓝色消息 = print_blue
打印紫色消息 = print_magenta
打印青色消息 = print_cyan
打印白色消息 = print_white
打印灰色消息 = print_grey
打印彩色消息 = print_color


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
    路径绿色**（重定向到文件时自动不上色，见 :func:`set_color`）::

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


def linked_path(path, base_file=None):
    """
    把本地资源路径转成「SVG 里引用的路径」（不内嵌时用）。 / Turn a local asset path into the reference written into the SVG when it is not embedded.

    同一磁盘时给**相对路径**（相对 SVG 所在目录，如 ``../../assets/bg.jpg``）：
    整个目录一起搬走仍然有效。跨磁盘（Windows 的 C: 与 D:）算不出相对路径，
    退回 ``file:///`` 形式的绝对地址。 / A relative path when the asset and the
    SVG share a drive, otherwise an absolute ``file:///`` URL.

    :param path: 资源文件路径
    :param base_file: 引用它的 SVG 文件路径（None = 直接用绝对 file:/// 地址）
    :return: 写进 href 的路径字符串（总是用 / 分隔）

    示例::
        url = linked_path("assets/bg.jpg", "output/poster.svg")
        # -> "../assets/bg.jpg"
    """
    target = os.path.abspath(str(path))
    if base_file:
        base = os.path.dirname(os.path.abspath(str(base_file)))
        try:
            rel = os.path.relpath(target, base)
        except ValueError:              # 跨盘（Windows）算不出相对路径
            rel = None
        if rel is not None:
            return rel.replace("\\", "/")
    return "file:///" + target.replace("\\", "/")


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

    返回的是**解析后的节点树**：换色 / 改文本可以直接调用
    `replace_svg_node_color` / `replace_svg_node_text`（或拿到组之后用
    ``group.replace_color(...)``），不必回改文本再重新内嵌。

    :return: (SvgNode 组, 原始宽, 原始高)

    示例（一般通过绘图板调用）::
        g = pen.import_svg_as_group("icon.svg", x=10, y=10, scale=0.5)
        replace_svg_node_color(g, "white", "#ff0000")
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
# SVG 文本工具（读源文本 / 按颜色改写：同一个 SVG 文件反复复用）
# ===========================================================================
#: SVG 里的颜色字面量：#rgb / #rgba / #rrggbb / #rrggbbaa / rgb() / rgba()
_COLOR_TOKEN_RE = re.compile(
    r"#[0-9a-fA-F]{8}\b|#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{4}\b|#[0-9a-fA-F]{3}\b|"
    r"rgba?\(\s*[0-9.]+%?\s*[, ]\s*[0-9.]+%?\s*[, ]\s*[0-9.]+%?"
    r"(?:\s*[,/]\s*[0-9.]+%?)?\s*\)")

#: 颜色属性（fill / stroke / stop-color …）后面那个具名颜色（white / teal …）。
#: 限定在颜色属性位置，避免把 id="orange" 这类同名标识一起换掉；
#: 允许属性写法 ``fill="white"`` 与样式写法 ``fill:white``。
_COLOR_NAMED_ATTR_RE = re.compile(
    r"(?P<pre>\b(?:fill|stroke|stop-color|flood-color|lighting-color"
    r"|solid-color|color)\s*[:=]\s*[\"']?\s*)(?P<val>[A-Za-z]{3,})\b")

#: 可以直接写进颜色属性、但不是「具名颜色」的取值（换色时允许写进去）
_PAINT_VALUES = frozenset(["currentcolor", "none", "transparent"])


def _in_url(text, pos):
    """
    这个位置前面是不是 ``url(`` —— ``url(#fff)`` 里的 #fff 是 id 不是颜色（内部辅助）。 / True when the match sits inside url(#...), where #fff is an id rather than a colour.
    """
    return text[max(0, pos - 4):pos].lower() == "url("


def _norm_color(value):
    """
    颜色归一化：把各种写法都变成小写 ``#rrggbb``（内部辅助）。 / Normalise any colour spelling to a lowercase ``#rrggbb``.

    ``#fff`` / ``#FFFFFF`` / ``#ffffffff`` / ``rgb(255,255,255)`` / ``white`` /
    ``白色`` 都会归一成 ``#ffffff``，这样「同一个颜色」才能被认出来；
    认不出的值原样返回小写，不会凭空匹配。
    """
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return s
    low = s.lower()
    if low.startswith("#"):
        h = low[1:]
        if len(h) in (3, 4):                    # #rgb / #rgba -> 每位翻倍
            h = "".join(c * 2 for c in h)
        if len(h) == 8 and h.endswith("ff"):    # 不透明 alpha 视同不带 alpha
            h = h[:6]
        return "#" + h
    m = re.fullmatch(r"rgba?\(([^)]*)\)", low)
    if m:
        parts = [p for p in re.split(r"[,/\s]+", m.group(1)) if p]
        if len(parts) >= 3:
            vals = []
            for p in parts[:3]:
                v = float(p[:-1]) * 255.0 / 100.0 if p.endswith("%") else float(p)
                vals.append(max(0, min(255, int(round(v)))))
            return "#{:02x}{:02x}{:02x}".format(*vals)
    # 延迟导入：definitions -> fonts -> tools 是环，模块顶部 import 会炸
    from .definitions import _COLOR_TABLE, _ENGLISH_NAMES
    if low in _ENGLISH_NAMES:
        return _ENGLISH_NAMES[low]
    if s in _COLOR_TABLE:
        return _COLOR_TABLE[s][1]
    return low


def _colors_in_text(text):
    """
    扫一段 SVG / CSS 文本里用到的颜色（归一化后以 ``#`` 开头的才算，内部辅助）。 / Scan the colours used in a piece of SVG or CSS text; only values that normalise to #rrggbb count.
    """
    src = str(text)
    found = []
    for m in _COLOR_TOKEN_RE.finditer(src):
        if _in_url(src, m.start()):
            continue                    # url(#abc) 里的 #abc 是 id，不是颜色
        c = _norm_color(m.group(0))
        if c.startswith("#") and c not in found:
            found.append(c)
    for m in _COLOR_NAMED_ATTR_RE.finditer(src):
        # 认出来的具名颜色会归一成 #rrggbb；none / url(…) / 未知名字直接跳过
        c = _norm_color(m.group("val"))
        if c.startswith("#") and c not in found:
            found.append(c)
    return found


def _replace_color_in_text(src, target, repl, count=-1, state=None):
    """
    在一段文本里按「颜色语义」替换（内部辅助）。 / Replace colours inside a piece of text by meaning.

    文本可以是整份 SVG，也可以是**一个** ``style`` 属性值或 ``<style>`` 块里的
    CSS —— 后者让「导入成节点树」的那条路也能改到 class 里的颜色。

    :param src: 待处理文本
    :param target: 目标色（已归一化的 ``#rrggbb``）
    :param repl: 新色（已归一化的 ``#rrggbb``，或 currentColor 这类合法取值）
    :param count: 最多替换几处（-1 = 全部）
    :param state: 跨多次调用的计数容器 ``[0]``（节点树里用来共用同一个 count）
    :return: ``(新文本, 本次替换处数)``
    """
    st = state if state is not None else [0]
    before = st[0]

    def _sub(m, value, write):
        """命中就替换（受 count 限制），返回新片段。"""
        if _norm_color(value) != target:
            return m.group(0)
        if 0 <= count <= st[0]:
            return m.group(0)
        st[0] += 1
        return write()

    def _sub_token(m):
        """hex / rgb() 字面量；url(#abc) 里的 #abc 是 id，不动。"""
        if _in_url(src, m.start()):
            return m.group(0)
        return _sub(m, m.group(0), lambda: repl)

    def _sub_named(m):
        """具名颜色（只在颜色属性位置）。"""
        return _sub(m, m.group("val"), lambda: m.group("pre") + repl)

    out = _COLOR_TOKEN_RE.sub(_sub_token, src)
    out = _COLOR_NAMED_ATTR_RE.sub(_sub_named, out)
    return out, st[0] - before


def read_svg_text(path):
    """
    读 SVG 文件的源文本（UTF-8 优先，退回 GBK，去 BOM）。 / Read an SVG file's source text; UTF-8 first, with a GBK fallback and BOM removed.

    :param path: SVG 文件路径
    :return: 文本内容

    示例::
        text = read_svg_text("icon.svg")
        print(text[:40])          # <svg xmlns="http://www.w3.org/2000/svg" ...
    """
    with open(path, "rb") as f:
        raw = f.read()
    for enc in ("utf-8-sig", "utf-8", "gbk"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", "replace")


def svg_text_to_data_uri(text):
    """
    SVG 文本转 ``data:image/svg+xml;base64,...``（内嵌用）。 / Turn SVG text into a ``data:image/svg+xml;base64,...`` URI.

    :param text: SVG 源文本
    :return: data URI 字符串

    示例::
        url = svg_text_to_data_uri('<svg xmlns="..."/>')
    """
    data = base64.b64encode(str(text).encode("utf-8")).decode()
    return "data:image/svg+xml;base64," + data


def svg_intrinsic_size(text):
    """
    从 SVG 文本读内在尺寸 (宽, 高)，读不到返回 (0, 0)。 / Read the intrinsic size (width, height) from SVG text; (0, 0) when it cannot be determined.

    先看根标签的 width/height，再看 viewBox；``width="100%"`` 这类百分比
    无法换算成像素，视为读不到。改过颜色的文本也能直接算（不必回读文件）。

    示例::
        svg_intrinsic_size('<svg width="120" height="80">')   # (120.0, 80.0)
        svg_intrinsic_size('<svg viewBox="0 0 24 24">')       # (24.0, 24.0)
    """
    m = re.search(r"<svg\b[^>]*>", str(text), re.I)
    if not m:
        return (0, 0)
    head = m.group(0)

    def _num(value):
        """属性值里的数字（"120px" -> 120.0，百分比/缺失返回 0.0）。"""
        if not value or value.strip().endswith("%"):
            return 0.0
        hit = re.match(r"\s*(-?(?:\d+\.?\d*|\.\d+))", value)
        return float(hit.group(1)) if hit else 0.0

    w = re.search(r'\bwidth\s*=\s*"([^"]*)"', head, re.I)
    h = re.search(r'\bheight\s*=\s*"([^"]*)"', head, re.I)
    iw = _num(w.group(1)) if w else 0.0
    ih = _num(h.group(1)) if h else 0.0
    if iw and ih:
        return (iw, ih)
    vb = re.search(r'\bviewBox\s*=\s*"([^"]*)"', head, re.I)
    if vb:
        parts = vb.group(1).replace(",", " ").split()
        if len(parts) == 4:
            try:
                return (float(parts[2]), float(parts[3]))
            except ValueError:
                pass
    return (iw, ih) if (iw or ih) else (0, 0)


def svg_colors(text):
    """
    列出 SVG 文本里用到的颜色（归一成小写 ``#rrggbb``，按首次出现顺序去重）。 / List the colours used in SVG text, normalised to lowercase ``#rrggbb`` in order of first appearance.

    :param text: SVG 源文本
    :return: 颜色列表，如 ``['#4dabf7', '#ffd43b', '#ffffff']``

    改色前先跑一次，就知道文件里到底写的是哪种写法。 / Run it before
    recolouring to see which spellings the file actually uses.

    示例::
        svg_colors('<rect fill="#FFF"/><circle fill="teal"/>')
        # ['#ffffff', '#008080']
    """
    return _colors_in_text(text)


def replace_svg_color(text, old, new, count=-1):
    """
    按「颜色」替换 SVG 文本里的颜色（同一个 SVG 文件换色复用）。 / Replace a colour inside SVG text by meaning rather than by raw string.

    与 ``str.replace`` 的区别有两点：

    1. **认写法**：``#fff`` / ``#ffffff`` / ``rgb(255,255,255)`` / ``white`` /
       ``白色`` 是同一种颜色，写成哪种都会命中；
    2. **不误伤**：具名颜色只在 ``fill`` / ``stroke`` / ``stop-color`` 这类
       **颜色属性**位置替换，``id="orange"`` 这种同名标识不动。

    :param text: 原始 SVG 文本
    :param old: 要被换掉的颜色（任意写法）
    :param new: 新颜色（任意写法，写回规范形式 ``#rrggbb``）
    :param count: 最多替换几处（-1 = 全部）
    :return: ``(新文本, 替换处数)``

    示例::
        used = svg_colors(text)        # see which spellings the file uses
        text, n = replace_svg_color(text, "#ffffff", "#ff0000")
    """
    target = _norm_color(old)
    repl = _norm_color(new)
    if not target or not repl:
        raise ValueError(t("err.svg_color_empty"))
    if not repl.startswith("#") and repl not in _PAINT_VALUES:
        # 新颜色认不出来就别写进去：写进 SVG 只会得到非法取值（静默出错）
        raise ValueError(t("err.svg_unknown_color", color=new))
    src = str(text)
    if not target.startswith("#"):
        # 老颜色没认出来（例如写成 "红" 而不是 "红色"）：一处都不动，
        # 让调用方给提示，而不是照字面乱换 —— 认不出≠不匹配
        return src, 0
    return _replace_color_in_text(src, target, repl, count)


# ===========================================================================
# SVG 节点树工具（导入成节点后改色 / 改文本）
# ===========================================================================
#: 直接写颜色的属性名。节点树改色只看这些属性 —— 属性名与值一一对应，比正则扫
#: 文本准，``id="orange"`` / ``<text>white</text>`` 这类同名内容天然不会误伤。
_SVG_COLOR_ATTRS = frozenset([
    "fill", "stroke", "stop-color", "flood-color", "lighting-color",
    "solid-color", "color"])


def walk_svg_nodes(node):
    """
    深度优先遍历节点树（含自身）。 / Walk a node tree depth first, including the node itself.

    遍历是节点自己的能力（`SvgNode.walk`），本函数只是同名的函数式写法，
    方便「手里只有节点、不想写方法调用」的场合。 / Walking is the node's own
    ability (SvgNode.walk); this is the same thing in function form.

    :param node: SvgNode（如 ``pen.import_svg_as_group`` 返回元素内含的节点）
    :return: 生成器，逐个产出 SvgNode

    示例::
        for n in walk_svg_nodes(group.node):
            print(n.tag, n.attribs.get("fill"))
    """
    return node.walk()


def _node_color_fields(n):
    """
    节点上「按颜色处理」的字段：产出 ``(当前取值, 写回函数)``（内部辅助）。 / Yield (value, setter) pairs for the colour-bearing fields of one node.
    """
    fields = []
    for key, value in list(getattr(n, "attribs", {}).items()):
        lk = str(key).lower()
        if lk in _SVG_COLOR_ATTRS or lk == "style":
            fields.append((value, lambda v, k=key: n.set(k, v)))
    if str(getattr(n, "tag", "")).lower() == "style" and n.text is not None:
        # <style> 块整块是 CSS，class 选择器里的颜色也在这里
        fields.append((n.text, lambda v: setattr(n, "text", v)))
    return fields


def _recolor_value(value, target, repl, count, state):
    """
    改一个属性值 / 一段样式文本里的颜色（内部辅助）。返回 ``(新值, 本次替换处数)``。 / Recolour a single attribute value or CSS snippet, returning (new value, hits).
    """
    if value is None:
        return value, 0
    s = str(value)
    if _norm_color(s) == target:
        # 整个值就是这一个颜色：fill="white" / stroke="#FFF" 这种最常见的写法
        if 0 <= count <= state[0]:
            return s, 0
        state[0] += 1
        return repl, 1
    # 值里混着别的东西：url(#grad) #fff、style="fill:#fff;stroke:white" 这类
    return _replace_color_in_text(s, target, repl, count, state)


def svg_node_colors(node):
    """
    列出节点树里用到的颜色（归一成小写 ``#rrggbb``，按首次出现顺序去重）。 / List the colours used inside a node tree, normalised to lowercase #rrggbb in order of first appearance.

    :param node: SvgNode（组 / 模板内容）
    :return: 颜色列表，如 ``['#4dabf7', '#ffd43b', '#ffffff']``

    颜色属性、``style="fill:..."`` 以及 ``<style>`` 块里 class 写的颜色都算。
    改色前先跑一次，就知道这份图到底用了哪几种颜色。 / Run it before
    recolouring to see which colours and spellings the graphic actually uses.

    示例::
        grp = pen.import_svg_as_group("icon.svg")
        print(svg_node_colors(grp))         # ['#ffffff', '#4dabf7']
    """
    found = []
    for n in walk_svg_nodes(node):
        for value, _setter in _node_color_fields(n):
            for c in _colors_in_text(value):
                if c not in found:
                    found.append(c)
    return found


def replace_svg_node_color(node, old, new, count=-1):
    """
    在**节点树**里按颜色替换（``import_svg_as_group`` / ``import_svg_as_symbol`` 拿到的节点）。 / Replace a colour inside a node tree, i.e. in the nodes returned by import_svg_as_group / import_svg_as_symbol.

    与 ``replace_svg_color``（改文本）的区别：这里改的是**解析后的属性**
    —— ``fill`` / ``stroke`` / ``stop-color`` / ``style`` 以及 ``<style>``
    块里的 CSS，改完立刻反映到生成的 SVG 上，不必重新内嵌。写法照样互认
    （``#fff`` / ``#ffffff`` / ``white`` / ``白色`` 是同一种颜色）。

    :param node: SvgNode（组 / 模板内容）
    :param old: 要被换掉的颜色（任意写法）
    :param new: 新颜色（任意写法，写回规范形式 ``#rrggbb``）
    :param count: 最多替换几处（-1 = 全部）
    :return: 替换处数（0 = 一处都没匹配上）

    示例::
        grp = pen.import_svg_as_group("icon.svg")
        n = replace_svg_node_color(grp, "#ffffff", "#ff0000")
    """
    target = _norm_color(old)
    repl = _norm_color(new)
    if not target or not repl:
        raise ValueError(t("err.svg_color_empty"))
    if not repl.startswith("#") and repl not in _PAINT_VALUES:
        # 新颜色认不出来就别写进去：写进 SVG 只会得到非法取值（静默出错）
        raise ValueError(t("err.svg_unknown_color", color=new))
    if not target.startswith("#"):
        return 0                        # 老颜色没认出来：一处都不动（认不出≠不匹配）
    state = [0]
    for n in walk_svg_nodes(node):
        for value, setter in _node_color_fields(n):
            new_value, hits = _recolor_value(value, target, repl, count, state)
            if hits:
                setter(new_value)
    return state[0]


def replace_svg_node_text(node, old, new, count=-1):
    """
    在**节点树**里做纯字符串替换：标签名 + 节点文本 + 所有属性值。 / Replace a raw substring across a node tree: tag names, node text and every attribute value.

    ``old`` 写什么就找什么（不认颜色写法，换颜色用 `replace_svg_node_color`）。
    标签名也在替换范围内，``replace_svg_node_text(grp, "circle", "ellipse")``
    和文本版的 ``replace_text`` 效果一致；但注意换标签不会自动补属性。

    :param node: SvgNode（组 / 模板内容）
    :param old: 要被替换的字符串
    :param new: 新字符串
    :param count: 最多替换几处（-1 = 全部）
    :return: 替换处数

    示例::
        replace_svg_node_text(grp, "circle", "ellipse")
    """
    old_s = str(old)
    new_s = str(new)
    if not old_s:
        return 0
    state = [0]

    def _rep(s):
        """替换一个字符串（受 count 限制），返回 (新串, 本次处数)。"""
        if not isinstance(s, str):
            return s, 0
        room = -1 if count < 0 else count - state[0]
        if room == 0:
            return s, 0
        hits = s.count(old_s)
        if not hits:
            return s, 0
        take = hits if room < 0 else min(hits, room)
        state[0] += take
        return s.replace(old_s, new_s, take), take

    for n in walk_svg_nodes(node):
        if isinstance(getattr(n, "tag", None), str):
            new_tag, hits = _rep(n.tag)
            if hits:
                n.tag = new_tag
        if isinstance(getattr(n, "text", None), str):
            n.text, _hits = _rep(n.text)
        for key in list(getattr(n, "attribs", {})):
            value = n.attribs[key]
            if isinstance(value, str):
                new_value, hits = _rep(value)
                if hits:
                    n.attribs[key] = new_value
        for i, child in enumerate(list(getattr(n, "children", None) or [])):
            if isinstance(child, str):      # 子节点也可以是原始 XML 字符串
                new_child, hits = _rep(child)
                if hits:
                    n.children[i] = new_child
    return state[0]


# ===========================================================================
# SVG 变换（transform）小工具
# ===========================================================================
# 只做「把点按 transform 列表映射一遍」这一件事：导入的 SVG 组算包围盒时用得上
# —— 导入进来的是裸节点，没有各自的元素对象，算不了逐图形的并集，只能量外框。
#: transform 片段里的数字（支持 1.5 / .5 / 1e-3 这些写法）
_TRANSFORM_NUM_RE = re.compile(r"-?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")


def _matrix_mul(m, n):
    """
    两个仿射矩阵相乘 ``m·n``（内部辅助）。 / Multiply two affine matrices, internal.

    矩阵用 SVG 的 2x3 六元组写法 ``(a, b, c, d, e, f)``。
    """
    a1, b1, c1, d1, e1, f1 = m
    a2, b2, c2, d2, e2, f2 = n
    return (a1 * a2 + c1 * b2, b1 * a2 + d1 * b2,
            a1 * c2 + c1 * d2, b1 * c2 + d1 * d2,
            a1 * e2 + c1 * f2 + e1, b1 * e2 + d1 * f2 + f1)


def _transform_matrix(items):
    """
    transform 列表 -> 仿射矩阵 ``(a, b, c, d, e, f)``（内部辅助）。 / Turn a transform list into an affine matrix, internal.

    支持 SVG 规范的 ``matrix`` / ``translate`` / ``scale`` / ``rotate`` /
    ``skewX`` / ``skewY``；认不出的片段照规范忽略（浏览器也是这么做的）。
    """
    m = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)
    for item in items or []:
        name, _, rest = str(item).strip().partition("(")
        args = [float(v) for v in _TRANSFORM_NUM_RE.findall(rest)]
        name = name.strip()
        if name == "matrix" and len(args) >= 6:
            t = tuple(args[:6])
        elif name == "translate" and args:
            t = (1.0, 0.0, 0.0, 1.0, args[0],
                 args[1] if len(args) > 1 else 0.0)
        elif name == "scale" and args:
            t = (args[0], 0.0, 0.0, args[1] if len(args) > 1 else args[0],
                 0.0, 0.0)
        elif name == "rotate" and args:
            rad = math.radians(args[0])
            ca, sa = math.cos(rad), math.sin(rad)
            t = (ca, sa, -sa, ca, 0.0, 0.0)
            if len(args) >= 3:      # rotate(a,cx,cy) = 移到中心 -> 转 -> 移回来
                t = _matrix_mul(_matrix_mul(
                    (1.0, 0.0, 0.0, 1.0, args[1], args[2]), t),
                    (1.0, 0.0, 0.0, 1.0, -args[1], -args[2]))
        elif name == "skewX" and args:
            t = (1.0, 0.0, math.tan(math.radians(args[0])), 1.0, 0.0, 0.0)
        elif name == "skewY" and args:
            t = (1.0, math.tan(math.radians(args[0])), 0.0, 1.0, 0.0, 0.0)
        else:
            continue
        m = _matrix_mul(m, t)
    return m


def svg_transform_points(points, transform):
    """
    把一组点按 SVG 的 transform 映射一遍。 / Map a list of points through an SVG transform.

    变换按列表顺序依次作用（与浏览器一致：``translate(5,5) scale(2)`` 是
    「先平移再缩放」，点 (0,0) 落到 (5,5)）。 / Transforms apply left to
    right, exactly as in a browser.

    :param points: 点列表 ``[(x, y), ...]``
    :param transform: transform 字符串（如 ``"translate(10,20) rotate(45)"``）
                      或已经拆好的片段列表
    :return: 变换后的点列表 ``[(x, y), ...]``

    支持 ``matrix`` / ``translate`` / ``scale`` / ``rotate`` / ``skewX`` /
    ``skewY``，认不出的片段忽略。 / Supports matrix, translate, scale,
    rotate, skewX and skewY; unknown pieces are ignored.

    示例::
        svg_transform_points([(0, 0), (10, 0)], "translate(5,5) scale(2)")
        # [(5.0, 5.0), (25.0, 5.0)]
    """
    if isinstance(transform, str):
        items = re.findall(r"[A-Za-z]+\s*\([^)]*\)", transform)
    else:
        items = list(transform or [])
    a, b, c, d, e, f = _transform_matrix(items)
    return [(a * float(x) + c * float(y) + e, b * float(x) + d * float(y) + f)
            for x, y in points]


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

    另外补一条 ``<base href>`` 指向 SVG 所在目录：SVG 用 LINK 模式引用本地
    图片（相对路径）时，临时 HTML 在系统临时目录里，不补 base 就解析不到图，
    PNG/PDF 会丢图。 / A <base href> pinned to the SVG folder keeps relative
    image references (ImageEmbed.LINK) working from the temp HTML.

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
    base_uri = ("file:///" + os.path.dirname(os.path.abspath(svg_file))
                .replace("\\", "/") + "/")

    html = (
        "<!DOCTYPE html><html><head><meta charset='utf-8'>"
        "<base href='{base}'>"
        "<style>"
        "@page {{ size: {page}; margin: 0; }}"
        "html, body {{ margin: 0; padding: 0; background: {bg}; }}"
        "svg {{ display: block; }}"
        "{print_css}"
        "</style></head><body>{svg}</body></html>"
    ).format(base=base_uri, page=page_css, bg=background, svg=svg_text,
             print_css=print_css)
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


def _chrome_wait_flags(svg_file):
    """
    内嵌字体的 SVG 需要「等字体激活再输出」的 Chrome 附加参数。 / Extra Chrome
    flags that let embedded web fonts finish activating before capture.

    ``@font-face`` 字体是异步激活的，而 --screenshot / --print-to-pdf 在页面
    load 事件就动手：截图一旦跑赢字体激活，文字正处于 font-display 的
    block 期，**整段消失**（偶发，SVG 越小越容易输掉竞态）。探测到 SVG 带
    ``@font-face`` 且没有 SMIL 动画时，追加虚拟时间预算，等字体就绪再截图；
    有动画的保持原行为（虚拟时间会推进动画相位，2026-09-23 验证过要用
    begin="-3s" 定相位，不能在这里引入）。

    ``@font-face`` fonts activate asynchronously while headless Chrome
    captures at the load event; when the screenshot wins the race, text in
    the font-display block period vanishes entirely. If the SVG embeds
    fonts and carries no SMIL animation, drain virtual time first; animated
    SVGs keep the old behavior (virtual time would advance their phase).
    """
    try:
        with open(svg_file, "r", encoding="utf-8") as f:
            probe = f.read()
    except OSError:
        return []
    if "@font-face" not in probe or "<animate" in probe:
        return []
    return ["--virtual-time-budget=5000",
            "--run-all-compositor-stages-before-draw"]


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
        ] + _chrome_wait_flags(svg_file))
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
        args += _chrome_wait_flags(svg_file)   # 等内嵌字体激活再截 / wait for fonts
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


# ---------------------------------------------------------------------------
# 直接运行示例：命令行 `python malight/tools.py`，也可以在 PyCharm 里点绿色三角。
# Run it from the command line, or start it from PyCharm's green triangle.
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import malight

    # --- 1) 彩色消息：八种颜色各有一个同名函数 --- / --- 1) Colored messages: one function per color ---
    malight.print_red("错误：导出失败 / error: export failed")
    malight.print_green("成功：已导出 3 个文件 / ok: 3 files exported")
    malight.print_yellow("警告：字体缺失，已回退默认字体 / warn: font missing, fallback used")
    malight.print_blue("信息：正在用 Chrome 引擎 / info: using the Chrome engine")
    malight.print_magenta("紫红色，与 purple 同色 / magenta, the same as purple")
    malight.print_cyan("青色，适合打印调试信息 / cyan, handy for debug output")
    malight.print_white("白色，普通提示 / white, plain notice")
    malight.print_grey("灰色，可以忽略 / grey, safe to ignore")

    # --- 2) 通用写法：颜色与样式随你组合 --- / --- 2) Generic form: any color, any styling ---
    malight.print_color("加粗的普通红色 / bold, non-bright red",
                        color="red", bold=True, bright=False)
    malight.print_color("写进 stderr，并按 stderr 判断上色 / written to stderr",
                        color="yellow", file=sys.stderr)

    # --- 3) paint 只返回带色字符串，不打印 --- / --- 3) paint() returns a styled string, it does not print ---
    print("paint ->", malight.paint("styled text", color="green", bold=True))

    # --- 4) 重定向到磁盘文件时自动不上色（运行窗口仍上色），也可手动关闭 --- / --- 4) Colors go off when redirected to a file; IDE consoles stay colored ---
    malight.set_color(False)
    malight.print_red("这行没有转义码 / no escape codes on this line")
    malight.set_color(None)                    # None 交回自动判断 / None restores auto-detection

    # --- 5) 中文别名（与中文版《神笔码靓》同名）与英文名指向同一函数 --- / --- 5) Chinese aliases are the same function objects as the English names ---
    print("color_enabled() ->", malight.color_enabled())
