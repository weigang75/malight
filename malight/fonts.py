# -*- coding: utf-8 -*-
"""
字体（fonts）—— 字体枚举 Font + 字体解析/查找/内嵌工具
=======================================================

Font enum plus font lookup, embedding and subsetting helpers.

英文版 malight 的字体统一入口，对应中文版《神笔码靓》的 `系统字体`，
并在其基础上增加了「字体文件内嵌」能力。

**三种写法随你方便，可混用**::

    from malight import Malight, Font

    pen = Malight("demo", width=600, height=400)

    # 1) 枚举（推荐：IDE 有自动补全，拼错立刻报错，不用记字体名）
    pen.text(300, 60,  "黑体标题", font=Font.SIMHEI, font_size=32)

    # 2) 字体名（字符串，适合任意已安装字体）
    pen.text(300, 120, "微软雅黑", font="Microsoft YaHei", font_size=28)

    # 3) 字体文件（.ttf/.otf/.ttc/.woff —— 自动 base64 内嵌进 SVG，
    #    换电脑/发给别人也不会掉字体，导出 PDF/PNG 效果一致）
    pen.text(300, 180, "楷体", font=r"C:\\Windows\\Fonts\\simkai.ttf", font_size=28)

为什么推荐用枚举：字体名写错时浏览器只会「静默回退成默认字体」，
不报错、很难查；用枚举有补全提示、拼错即报错。

常用辅助::

    Font.SIMHEI.value             # "SimHei"     取字体名
    Font.of("SimHei")             # Font.SIMHEI  字符串 -> 枚举
    Font.list_names()             # 全部枚举名的列表
    Font.is_font_file("a.ttf")    # True         判断是不是字体文件
    Font.family_of("c:/a.ttf")    # "a"          从文件猜字体族名
    find_font_file("KaiTi")       # 字体文件完整路径（找不到返回 None）

**字体文件目录约定** ``assets/fonts``：把 ``.ttf`` / ``.otf`` / ``.ttc`` 放进
包内 ``malight/assets/fonts/``（随包分发）或项目的 ``<项目>/assets/fonts/``，
:func:`find_font_file` 会**优先**在这里找，其次才是系统字体目录；
也可以用环境变量 ``MALIGHT_FONTS`` 指定更多目录（``;`` 分隔）。
资源目录统一用 :func:`malight.asset_path` / :func:`malight.asset_dir` 查找。
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

import os
import base64
from enum import Enum
from .i18n import t
from .tools import asset_dir

# 字体文件常见后缀（含 Windows/macOS/Linux 常见格式）
FONT_FILE_EXTS = (".ttf", ".otf", ".ttc", ".otc", ".woff", ".woff2", ".eot")

#: 项目字体目录约定：把 .ttf/.otf/.ttc 放进 ``<项目>/assets/fonts/``，
#: :func:`find_font_file` 会**优先**在这里找 —— 字体随项目分发，换机器不缺字。
ASSET_FONT_DIR = os.path.join("assets", "fonts")

# @font-face 里声明的字体格式名
_FORMAT_BY_EXT = {
    ".ttf": "truetype", ".otf": "opentype", ".ttc": "truetype",
    ".otc": "opentype", ".woff": "woff", ".woff2": "woff2", ".eot": "embedded-opentype",
}


class Font(str, Enum):
    """
    系统字体枚举（对应中文版 `系统字体`）。成员值即 SVG 的 font-family 名。 / System font enum; each member value is the SVG font-family name.

    用法::

        from malight import Font
        pen.text(100, 100, "标题", font=Font.SIMHEI, font_size=32)
        pen.text(100, 160, "ABC",  font=Font.ARIAL,  font_size=24)

    说明：枚举继承自 str，因此 ``Font.KAITI == "KaiTi"`` 为 True，
    也可以直接当字符串用（拼接、格式化、传参都行）。
    """

    # ---- 特殊 ----
    DEFAULT = ""                  # 不指定字体（由查看器/浏览器决定默认字体）

    # ---- 中文字体（Windows 常见）----
    SIMHEI = "SimHei"                        # 黑体
    SIMSUN = "SimSun"                        # 宋体
    NSIMSUN = "NSimSun"                      # 新宋体
    KAITI = "KaiTi"                          # 楷体
    FANGSONG = "FangSong"                    # 仿宋
    YOUYUAN = "YouYuan"                      # 幼圆
    LISU = "LiSu"                            # 隶书
    DENGXIAN = "DengXian"                    # 等线
    MS_YAHEI = "Microsoft YaHei"             # 微软雅黑（最常用）
    MS_YAHEI_LIGHT = "Microsoft YaHei Light"  # 微软雅黑 Light
    # ---- 中文字体（macOS / Office 常见）----
    STXIHEI = "STXihei"                      # 华文细黑
    STZHONGSONG = "STZhongsong"              # 华文中宋
    STKAITI = "STKaiti"                      # 华文楷体
    STFANGSONG = "STFangsong"                # 华文仿宋
    STHUPO = "STHupo"                        # 华文琥珀
    STXINGKAI = "STXingkai"                  # 华文行楷
    STXINWEI = "STXinwei"                    # 华文新魏
    FZSHUTI = "FZShuTi"                      # 方正舒体
    FZYAOTI = "FZYaoTi"                      # 方正姚体

    # ---- 西文字体 ----
    ARIAL = "Arial"
    ARIAL_BLACK = "Arial Black"
    BAHNSCHRIFT = "Bahnschrift"
    BEBAS_NEUE = "Bebas Neue"
    BROADWAY = "Broadway"
    CALIBRI = "Calibri"
    CAMBRIA = "Cambria"
    COMIC_SANS = "Comic Sans MS"
    CONSOLAS = "Consolas"
    COURIER_NEW = "Courier New"
    GEORGIA = "Georgia"
    MONTSERRAT = "Montserrat"
    ROBOTO = "Roboto"
    SEGOE_UI = "Segoe UI"
    TAHOMA = "Tahoma"
    TIMES_NEW_ROMAN = "Times New Roman"
    TREBUCHET_MS = "Trebuchet MS"
    VERDANA = "Verdana"
    WIDE_LATIN = "Wide Latin"

    def __str__(self):
        """让 f-string / print 直接输出字体名，如 f"{Font.KAITI}" -> "KaiTi"。"""
        return self.value

    # ---------------------------------------------------------------
    # 辅助方法
    # ---------------------------------------------------------------
    @staticmethod
    def of(value):
        """
        把「字体枚举名 / 字体族名」字符串转换为枚举成员。 / Convert a font enum name or family name into a Font member.

        :param value: 如 "SIMHEI"、"SimHei"、"KaiTi"，或已是 Font 成员
        :return: Font 成员；找不到时返回 None

        示例::
            Font.of("SimHei")      # Font.SIMHEI
            Font.of("SIMHEI")      # Font.SIMHEI（枚举名也认）
            Font.of("不存在")       # None
        """
        if isinstance(value, Font):
            return value
        if not isinstance(value, str):
            return None
        try:
            return Font(value)              # 按值（字体名）查
        except ValueError:
            pass
        try:
            return Font[value.upper()]      # 按枚举名查
        except KeyError:
            return None

    @staticmethod
    def is_font_file(value):
        """
        判断传入的是不是「字体文件路径」（而不是字体族名）。 / Tell whether the argument is a font FILE path rather than a family name.

        :return: True / False

        示例::
            Font.is_font_file(r"C:\\Windows\\Fonts\\simkai.ttf")   # True
            Font.is_font_file("KaiTi")                            # False
        """
        if not isinstance(value, str):
            return False
        return value.lower().endswith(FONT_FILE_EXTS)

    @staticmethod
    def family_of(font_file):
        """
        从字体文件推断「字体族名」（用于生成 @font-face 的 family）。 / Infer a font family name from a font file, used for the @font-face family.

        有 fontTools 时读取真实字体名（最准确）；没有时退化为文件名（去掉后缀）。
        生成的族名带 ``malight-`` 前缀，避免与系统同名字体冲突。

        示例::
            Font.family_of(r"C:\\Windows\\Fonts\\simkai.ttf")   # "malight-simkai"
        """
        stem = os.path.splitext(os.path.basename(str(font_file)))[0]
        name = stem
        try:
            from fontTools.ttLib import TTFont
            tt = TTFont(str(font_file), fontNumber=0, lazy=True)
            for rec in tt["name"].names:
                if rec.nameID in (1, 4):          # 1=Family 4=Full name
                    try:
                        name = rec.toUnicode()
                        break
                    except Exception:
                        pass
        except Exception:
            pass
        safe = "".join(c if (c.isalnum() or c in "-_") else "-" for c in name)
        return f"malight-{safe}"

    @staticmethod
    def list_names():
        """
        列出全部字体枚举名（便于做字体选择器）。 / List every font enum member name; handy for building font pickers.

        示例::
            for n in Font.list_names():
                print(n, "=", getattr(Font, n))
        """
        return [m.name for m in Font]

    @staticmethod
    def list_values():
        """列出全部字体枚举值（字体名）。 / List every font enum value, i.e. the font names. 示例:: Font.list_values()[:5]"""
        return [m.value for m in Font]

    @classmethod
    def chinese_name(cls, font_value):
        """
        兼容旧版 `SystemFont.chinese_name`：返回字体对应的枚举名。 / Back-compat with `SystemFont.chinese_name`: return the enum member name.

        示例::
            Font.chinese_name("KaiTi")    # "KAITI"
        """
        f = cls.of(font_value)
        return f.name if f is not None else font_value


def font_face_css(font_file, family=None):
    """
    生成字体文件的内嵌 @font-face CSS（把字体 base64 塞进 SVG）。 / Build the embedded @font-face CSS for a font file, base64-encoding the font into the SVG.

    这样 SVG/PDF 换电脑、发给别人都能正常显示，不会掉字体。

    :param font_file: 字体文件路径
    :param family: 自定义族名（默认用 Font.family_of 生成）
    :return: (family 名, CSS 文本)
    :raises FileNotFoundError: 字体文件不存在（附带排查提示）

    示例::
        family, css = font_face_css(r"C:\\Windows\\Fonts\\simkai.ttf")
        print(family)   # "malight-simkai"
    """
    if not os.path.isfile(str(font_file)):
        raise FileNotFoundError(t("err.font_file_missing",
                                  path=os.path.abspath(str(font_file))))
    ext = os.path.splitext(str(font_file))[1].lower()
    fmt = _FORMAT_BY_EXT.get(ext, "truetype")
    mime = {"woff": "font/woff", "woff2": "font/woff2",
            "eot": "application/vnd.ms-fontobject"}.get(ext.lstrip("."), "font/ttf")
    with open(font_file, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    family = family or Font.family_of(font_file)
    css = ("@font-face { font-family: '" + family + "'; src: url(data:" + mime +
           ";base64," + b64 + ") format('" + fmt + "'); }")
    return family, css


def subset_font(font_file, text, out_file=None):
    """
    按实际用到的文字对字体文件做子集化（需要 fontTools），大幅减小内嵌体积。 / Subset a font file to the characters actually used (requires fontTools), which shrinks embedded output a lot.

    完整中文字体约 5~15 MB，内嵌后 SVG 会很大；只保留用到的字形通常能降到
    几十 KB。做法：先用本函数生成子集字体文件，再把该文件传给 ``font=``。

    :param font_file: 原始字体文件
    :param text: 用到的全部文字（把所有要显示的字拼成一个字符串）
    :param out_file: 输出文件（默认原名加 ``_subset``）
    :return: 子集字体文件路径

    示例::
        sub = subset_font(r"C:\\Windows\\Fonts\\simkai.ttf", "你好世界 ABC")
        pen.text(100, 100, "你好世界 ABC", font=sub)     # 内嵌体积小很多
    """
    try:
        from fontTools import subset
    except ImportError:
        raise NotImplementedError(t("err.need_fonttools_subset"))
    if out_file is None:
        base, ext = os.path.splitext(str(font_file))
        out_file = "{}_subset{}".format(base, ext or ".ttf")
    args = [str(font_file), "--text={}".format(text), "--output-file={}".format(out_file),
            "--layout-features=*", "--no-hinting", "--desubroutinize"]
    subset.main(args)
    print(t("info.font_subset_done",
                src=os.path.basename(str(font_file)),
                dst=os.path.abspath(out_file),
                size="%.1f KB" % (os.path.getsize(out_file) / 1024.0)))
    return os.path.abspath(out_file)


def font_search_dirs() -> list:
    """
    字体文件的搜索目录（按优先级，系统字体目录之前）。 / Font-file search directories, by priority, before the system font folders.

    1. 环境变量 ``MALIGHT_FONTS``（可用 ``;`` / ``:`` 分隔多个目录）；
    2. 字体目录约定 ``assets/fonts`` —— 包内 ``malight/assets/fonts`` 优先，
       再从当前目录逐级向上找项目里的 ``assets/fonts``
       （把字体文件放进去即可随项目分发，换机器不缺字，见
       ``malight/assets/fonts/README.md``）。

    :return: 目录列表（可能为空，目录暂不存在也不报错）

    示例::
        font_search_dirs()     # ['D:/proj/assets/fonts', '.../malight/assets/fonts']
    """
    dirs = []
    env = os.environ.get("MALIGHT_FONTS", "")
    for part in env.split(os.pathsep):
        part = part.strip()
        if part:
            dirs.append(part)
    found = asset_dir("fonts")
    if found and found not in dirs:
        dirs.append(found)
    return dirs


def find_font_file(family, font_dirs=None):
    """
    在字体目录中查找字体文件（对应中文版 `字体查找器` 的简化版）。 / Find a font file in the font directories.

    查找顺序：先 :func:`font_search_dirs`（环境变量 ``MALIGHT_FONTS``、
    包内与项目的 ``assets/fonts``），再系统字体目录 —— 项目自带的字体
    优先于系统字体。

    :param family: 字体族名（可用 Font 枚举 / 枚举名 / 字体名）
    :param font_dirs: 自定义搜索目录；None = font_search_dirs() + 系统目录
    :return: 字体文件完整路径；找不到返回 None

    示例::
        find_font_file("KaiTi")            # C:\\Windows\\Fonts\\simkai.ttf
        find_font_file(Font.MS_YAHEI)      # C:\\Windows\\Fonts\\msyh.ttc
    """
    # 传入的本来就是文件路径，直接校验存在性
    if isinstance(family, str) and Font.is_font_file(family):
        return family if os.path.exists(family) else None

    if font_dirs is None:
        font_dirs = font_search_dirs() + [
            r"C:\Windows\Fonts",
            "/System/Library/Fonts", "/Library/Fonts",
            "/usr/share/fonts", "/usr/local/share/fonts",
            os.path.expanduser("~/AppData/Local/Microsoft/Windows/Fonts"),
            os.path.expanduser("~/.fonts")]
    # 常见字体的文件名表（Windows 为主，兼顾 macOS）
    aliases = {
        "SimHei": ["simhei.ttf"],
        "SimSun": ["simsun.ttc", "simsun.ttf"],
        "NSimSun": ["simsunb.ttf"],
        "KaiTi": ["simkai.ttf"],
        "FangSong": ["simfang.ttf"],
        "LiSu": ["SIMLI.TTF"],
        "YouYuan": ["SIMYOU.TTF"],
        "DengXian": ["Deng.ttf"],
        "Microsoft YaHei": ["msyh.ttc", "msyh.ttf"],
        "Microsoft YaHei Light": ["msyhl.ttc", "msyhl.ttf"],
        "STXihei": ["STXIHEI.TTF"],
        "STKaiti": ["STKAITI.TTF"],
        "STFangsong": ["STFANGSO.TTF"],
        "STXingkai": ["STXINGKA.TTF"],
        "STXinwei": ["STXINWEI.TTF"],
        "STHupo": ["STHUPO.TTF"],
        "STZhongsong": ["STZHONGS.TTF"],
        "FZShuTi": ["FZSTK.TTF"],
        "FZYaoTi": ["FZYTK.TTF"],
        "Arial": ["arial.ttf", "Arial.ttf"],
        "Arial Black": ["ariblk.ttf"],
        "Times New Roman": ["times.ttf"],
        "Courier New": ["cour.ttf"],
        "Verdana": ["verdana.ttf"],
        "Tahoma": ["tahoma.ttf"],
        "Georgia": ["georgia.ttf"],
        "Consolas": ["consola.ttf"],
        "Calibri": ["calibri.ttf"],
        "Cambria": ["cambria.ttc"],
        "Segoe UI": ["segoeui.ttf"],
        "Comic Sans MS": ["comic.ttf"],
        "Impact": ["impact.ttf"],
        "Roboto": ["Roboto-Regular.ttf"],
    }
    name = family.value if isinstance(family, Font) else str(family)
    candidates = aliases.get(name, [name + ".ttf", name.replace(" ", "") + ".ttf",
                                    name + ".ttc", name + ".otf"])
    # 传入的是枚举名（如 "MS_YAHEI"）时，先转成字体名
    f = Font.of(name)
    if f is not None and f.value and f.value != name:
        candidates = aliases.get(f.value, [f.value + ".ttf"]) + candidates

    for cand in candidates:
        for d in font_dirs:
            if os.path.isabs(cand):
                if os.path.exists(cand):
                    return cand
                continue
            # 目录不存在时跳过；字体目录内部可能有子目录，做一层浅遍历
            if not os.path.isdir(d):
                continue
            p = os.path.join(d, cand)
            if os.path.exists(p):
                return p
    return None


# ===========================================================================
# 使用示例（直接在 PyCharm 里点绿色三角运行本文件即可）
# ===========================================================================
if __name__ == "__main__":
    # 相对导入需要包上下文，这里补上（正常 import malight.fonts 时不执行） / Relative imports need a package context; only runs when executed directly
    import sys as _sys
    _sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # --- 1) 纯枚举信息，不依赖绘图板 --- / --- 1) Enum information only, no drawing board needed ---
    print("=== 字体枚举 === / === font enums ===")
    print("枚举成员数： / enum members: ", len(Font.list_names()))
    print("Font.SIMHEI       ->", repr(Font.SIMHEI.value))          # 'SimHei'
    print("Font.of('KaiTi') ->", Font.of("KaiTi"))                  # Font.KAITI
    print("Font.of('KAITI') ->", Font.of("KAITI"))                  # Font.KAITI
    print("是字体文件吗： / is it a font file: ", Font.is_font_file("a.ttf"),
          Font.is_font_file("KaiTi"))                              # True False

    # --- 2) 查找本机字体文件 --- / --- 2) Find font files on this machine ---
    print("\n=== 本机字体查找 === / \n=== local font lookup ===")
    for fam in ("KaiTi", "Microsoft YaHei", "Arial"):
        print(f"  {fam:18s} -> {find_font_file(fam)}")

    # --- 3) 真正画一张图，演示三种字体写法 --- / --- 3) Draw a real canvas showing the three ways to name a font ---
    from malight import Malight, Color

    pen = Malight("demo_font", width=640, height=360)
    pen.set_background_color("#fbfbfd")          # 浅色背景，方便看字 / Light background so the text is easy to read

    # 写法一：枚举（推荐） / Style 1: the enum, recommended
    pen.text(320, 70, "枚举 Font.SIMHEI（黑体） / enum Font.SIMHEI", font=Font.SIMHEI,
             font_size=26, fill_color="#1d3557", h_align="middle")
    # 写法二：字体名字符串（任意已安装字体） / Style 2: family name as a string, any installed font
    pen.text(320, 130, "字符串 font='Microsoft YaHei' / string font='Microsoft YaHei'", font="Microsoft YaHei",
             font_size=24, fill_color="#457b9d", h_align="middle")
    # 写法三：字体文件路径（自动内嵌进 SVG，换电脑不掉字体） / Style 3: font file path, embedded into the SVG
    kai = find_font_file(Font.KAITI)
    if kai:
        pen.text(320, 190, "字体文件（已 base64 内嵌） / font file (base64-embedded)", font=kai,
                 font_size=24, fill_color="#e63946", h_align="middle")
    else:
        pen.text(320, 190, "本机未找到楷体文件，跳过示例 / KaiTi not found on this machine, skipping", font_size=20,
                 fill_color="#e63946", h_align="middle")
    # 西文枚举 + 加粗 / Latin font enum, bold
    pen.text(320, 260, "ABJ malight 1234", font=Font.ARIAL, font_size=30,
             bold=True, fill_color="#2a9d8f", h_align="middle")

    pen.finish()      # 保存 SVG（finish 会打印保存全路径） / Save the SVG; finish prints the full path
