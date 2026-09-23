# -*- coding: utf-8 -*-
"""
定义集（Definitions）—— 颜色、字体、纸张、枚举常量
====================================================

Colors, fonts, paper sizes and every option enum.

本模块是英文版的常量定义中心，对应中文版《神笔码靓》的 `定义集.py`。

**设计约定（枚举 + 字符串双写法）**：凡是「可选值就那么几个」的参数，
都提供枚举；同时一律兼容直接写字符串。目的是既方便又不易写错：

===============  ================================  ==========================
参数             推荐写法（枚举）                   兼容写法（字符串）
===============  ================================  ==========================
颜色             ``ColorName.RED``                 ``"red" / "#ff0000" / "红"``
字体             ``Font.SIMHEI``                   ``"SimHei" / "simhei.ttf"``
填充规则          ``FillRule.EVENODD``              ``"evenodd"``
虚线样式          ``DashStyle.DASHED``              ``"8 4"``
端头/拐角         ``StrokeCap.ROUND``               ``"round"``
线条连接          ``StrokeJoin.ROUND``              ``"round"``
水平/垂直对齐      ``TextHAlign.MIDDLE``             ``"middle"``
字重             ``FontWeight.BOLD``               ``"bold" / 700``
文字修饰          ``TextDecoration.UNDERLINE``      ``"underline"``
混合模式          ``BlendMode.MULTIPLY``            ``"multiply"``
箭头样式          ``ArrowStyle.SOLID``              ``"solid"``
定位点样式        ``PointStyle.CROSS``              ``"cross"``
渐变坐标系        ``CoordUnits.USER_SPACE``         ``"userSpaceOnUse"``
导出引擎          ``PDFMode.CHROME``                ``1``
===============  ================================  ==========================

所有接口内部都会用 `value_of()` 归一化，所以两种写法可以混用。

使用示例::

    from malight import Color, ColorName, Font, FillRule, DashStyle

    pen.text(100, 100, "标题", font=Font.SIMHEI, weight=FontWeight.BOLD)
    pen.polygon(pts, fill_color=ColorName.TEAL, fill_rule=FillRule.EVENODD)
    pen.line((0, 0), (100, 0), stroke_style=DashStyle.DASHED)

    print(Color.RED)                 # "red"（完整 140 色常量）
    print(ColorName.RED)             # "red"（常用色枚举）
    print(Color.RGB(30, 144, 255))   # "#1e90ff"
    print(Color.darken("#D75D72"))   # 颜色加深
    w, h = PaperSize.A4_portrait()   # A4 像素尺寸
"""

import random
from dataclasses import dataclass
from typing import Union
from enum import Enum, IntEnum

# 字体枚举（原 SystemFont 已升级为 Font，仍保留旧名兼容）
from .fonts import Font


def value_of(value):
    """
    把枚举成员转换为其值；非枚举原样返回（「枚举 + 字符串」双写法的内部统一入口）。 / Return an enum member's value and pass anything else through unchanged; the internal entry point behind the enum-or-string convention.

    :param value: 枚举成员 / 字符串 / 数字 / None
    :return: 归一化后的值

    示例::
        value_of(ColorName.RED)      # "red"
        value_of("red")              # "red"
        value_of(FillRule.EVENODD)   # "evenodd"
    """
    if isinstance(value, Enum):
        return value.value
    return value



# ---------------------------------------------------------------------------
# 颜色表：中文名 -> (英文名, 十六进制值)
# 保留中文键用于兼容迁移（compat 模块会把旧的「颜色.红色」映射到 Color.RED）
# ---------------------------------------------------------------------------
_COLOR_TABLE = {
    "黑色": ("black", "#000000"), "海军色": ("navy", "#000080"),
    "暗蓝色": ("darkblue", "#00008b"), "中兰色": ("mediumblue", "#0000cd"),
    "蓝色": ("blue", "#0000ff"), "暗绿色": ("darkgreen", "#006400"),
    "绿色": ("green", "#008000"), "水鸭色": ("teal", "#008080"),
    "暗青色": ("darkcyan", "#008b8b"), "深天蓝色": ("deepskyblue", "#00bfff"),
    "暗宝石绿": ("darkturquoise", "#00ced1"), "中春绿色": ("mediumspringgreen", "#00fa9a"),
    "酸橙色": ("lime", "#00ff00"), "春绿色": ("springgreen", "#00ff7f"),
    "浅绿色": ("aqua", "#00ffff"), "中灰兰色": ("midnightblue", "#191970"),
    "闪兰色": ("dodgerblue", "#1e90ff"), "亮海蓝色": ("lightseagreen", "#20b2aa"),
    "森林绿": ("forestgreen", "#228b22"), "海绿色": ("seagreen", "#2e8b57"),
    "暗瓦灰色": ("darkslategray", "#2f4f4f"), "橙绿色": ("limegreen", "#32cd32"),
    "中海蓝": ("mediumseagreen", "#3cb371"), "青绿色": ("turquoise", "#40e0d0"),
    "皇家蓝": ("royalblue", "#4169e1"), "钢兰色": ("steelblue", "#4682b4"),
    "暗灰蓝色": ("darkslateblue", "#483d8b"), "中绿宝石": ("mediumturquoise", "#48d1cc"),
    "靛青色": ("indigo", "#4b0082"), "青色": ("cyan", "#00ffff"),
    "暗橄榄绿": ("darkolivegreen", "#556b2f"), "军兰色": ("cadetblue", "#5f9ea0"),
    "菊兰色": ("cornflowerblue", "#6495ed"), "中绿色": ("mediumaquamarine", "#66cdaa"),
    "暗灰色": ("dimgray", "#696969"), "石蓝色": ("slateblue", "#6a5acd"),
    "深绿褐色": ("olivedrab", "#6b8e23"), "灰石色": ("slategray", "#708090"),
    "亮蓝灰": ("lightslategray", "#778899"), "中暗蓝色": ("mediumslateblue", "#7b68ee"),
    "草绿色": ("lawngreen", "#7cfc00"), "黄绿色": ("chartreuse", "#7fff00"),
    "碧绿色": ("aquamarine", "#7fffd4"), "粟色": ("maroon", "#800000"),
    "紫色": ("purple", "#800080"), "橄榄色": ("olive", "#808000"),
    "灰色": ("gray", "#808080"), "天蓝色": ("skyblue", "#87ceeb"),
    "亮天蓝色": ("lightskyblue", "#87cefa"), "紫罗兰蓝色": ("blueviolet", "#8a2be2"),
    "暗红色": ("darkred", "#8b0000"), "暗洋红": ("darkmagenta", "#8b008b"),
    "重褐色": ("saddlebrown", "#8b4513"), "暗海兰色": ("darkseagreen", "#8fbc8f"),
    "亮绿色": ("lightgreen", "#90ee90"), "中紫色": ("mediumpurple", "#9370db"),
    "暗紫罗兰色": ("darkviolet", "#9400d3"), "苍绿色": ("palegreen", "#98fb98"),
    "暗紫色": ("darkorchid", "#9932cc"), "赭色": ("sienna", "#a0522d"),
    "褐色": ("brown", "#a52a2a"), "深灰色": ("darkgray", "#a9a9a9"),
    "亮蓝色": ("lightblue", "#add8e6"), "绿黄色": ("greenyellow", "#adff2f"),
    "苍宝石绿": ("paleturquoise", "#afeeee"), "亮钢兰色": ("lightsteelblue", "#b0c4de"),
    "粉蓝色": ("powderblue", "#b0e0e6"), "火砖色": ("firebrick", "#b22222"),
    "暗金黄色": ("darkgoldenrod", "#b8860b"), "中粉紫色": ("mediumorchid", "#ba55d3"),
    "褐玫瑰红": ("rosybrown", "#bc8f8f"), "暗黄褐色": ("darkkhaki", "#bdb76b"),
    "银色": ("silver", "#c0c0c0"), "中紫罗兰色": ("mediumvioletred", "#c71585"),
    "印第安红": ("indianred", "#cd5c5c"), "秘鲁色": ("peru", "#cd853f"),
    "巧可力色": ("chocolate", "#d2691e"), "茶色": ("tan", "#d2b48c"),
    "亮灰色": ("lightgray", "#d3d3d3"), "蓟色": ("thistle", "#d8bfd8"),
    "淡紫色": ("orchid", "#da70d6"), "金麒麟色": ("goldenrod", "#daa520"),
    "苍紫罗兰色": ("palevioletred", "#db7093"), "暗深红色": ("crimson", "#dc143c"),
    "淡灰色": ("gainsboro", "#dcdcdc"), "洋李色": ("plum", "#dda0dd"),
    "实木色": ("burlywood", "#deb887"), "亮青色": ("lightcyan", "#e0ffff"),
    "薰衣草": ("lavender", "#e6e6fa"), "暗肉色": ("darksalmon", "#e9967a"),
    "紫罗兰色": ("violet", "#ee82ee"), "苍麒麟色": ("palegoldenrod", "#eee8aa"),
    "亮珊瑚色": ("lightcoral", "#f08080"), "黄褐色": ("khaki", "#f0e68c"),
    "艾利斯兰": ("aliceblue", "#f0f8ff"), "蜜色": ("honeydew", "#f0fff0"),
    "蔚蓝色": ("azure", "#f0ffff"), "沙褐色": ("sandybrown", "#f4a460"),
    "浅黄色": ("wheat", "#f5deb3"), "米色": ("beige", "#f5f5dc"),
    "烟白色": ("whitesmoke", "#f5f5f5"), "薄荷色": ("mintcream", "#f5fffa"),
    "幽灵白": ("ghostwhite", "#f8f8ff"), "鲜肉色": ("salmon", "#fa8072"),
    "古董白": ("antiquewhite", "#faebd7"), "亚麻色": ("linen", "#faf0e6"),
    "亮金黄色": ("lightgoldenrodyellow", "#fafad2"), "老花色": ("oldlace", "#fdf5e6"),
    "红色": ("red", "#ff0000"), "紫红色": ("fuchsia", "#ff00ff"),
    "深粉红色": ("deeppink", "#ff1493"), "红橙色": ("orangered", "#ff4500"),
    "西红柿色": ("tomato", "#ff6347"), "热粉红色": ("hotpink", "#ff69b4"),
    "珊瑚色": ("coral", "#ff7f50"), "暗桔黄色": ("darkorange", "#ff8c00"),
    "亮肉色": ("lightsalmon", "#ffa07a"), "橙色": ("orange", "#ffa500"),
    "亮粉红色": ("lightpink", "#ffb6c1"), "粉红色": ("pink", "#ffc0cb"),
    "金色": ("gold", "#ffd700"), "桃色": ("peachpuff", "#ffdab9"),
    "纳瓦白": ("navajowhite", "#ffdead"), "鹿皮色": ("moccasin", "#ffe4b5"),
    "桔黄色": ("bisque", "#ffe4c4"), "浅玫瑰色": ("mistyrose", "#ffe4e1"),
    "白杏色": ("blanchedalmond", "#ffebcd"), "番木色": ("papayawhip", "#ffefd5"),
    "淡紫红": ("lavenderblush", "#fff0f5"), "海贝色": ("seashell", "#fff5ee"),
    "米绸色": ("cornsilk", "#fff8dc"), "柠檬绸色": ("lemonchiffon", "#fffacd"),
    "花白色": ("floralwhite", "#fffaf0"), "雪白色": ("snow", "#fffafa"),
    "黄色": ("yellow", "#ffff00"), "亮黄色": ("lightyellow", "#ffffe0"),
    "象牙色": ("ivory", "#fffff0"), "白色": ("white", "#ffffff"),
}

# 英文常量名 -> 十六进制值（由颜色表自动生成，如 "红色" -> RED = "red"）
_ENGLISH_NAMES = {}
for _cn, (_en, _hexv) in _COLOR_TABLE.items():
    _ENGLISH_NAMES[_en] = _hexv


class Color:
    """
    颜色常量与颜色运算工具（对应中文版 `颜色` 类）。 / Color constants and color-arithmetic helpers.

    属性为 140 种 SVG 具名颜色的英文名常量（值即 SVG 认可的颜色串），
    另有 NONE（空串）与 TRANSPARENT（"none"，不填充/不描边）。

    示例::
        Color.RED                     # "red"
        Color.RGB(255, 0, 0)          # "#ff0000"
        Color.hex_of("black")         # "#000000"
        Color.random()                # 随机颜色 "#3af192"
        Color.blend("#000000", "#FFFFFF", 0.5)  # 灰色 "#808080"
    """

    NONE = ""            # 空（不设置）
    TRANSPARENT = "none"  # 透明（SVG fill/stroke 的 none）

    # 由颜色表自动生成的英文常量：Color.BLACK = "black" ...
    locals().update({en.upper(): v for en, v in _ENGLISH_NAMES.items()})

    # 兼容别名（与中文版习惯一致）: AQUA/CYAN 同色
    AQUA = "#00ffff"

    _cn_dict = _COLOR_TABLE

    # ---------------------------------------------------------------
    # 颜色构造与转换
    # ---------------------------------------------------------------
    @staticmethod
    def RGB(R=None, G=None, B=None):
        """
        构造 RGB 颜色，返回 #rrggbb 字符串。 / Build an RGB color and return a #rrggbb string.

        :param R: 红色分量 0-255；若传入非数值（中/英文颜色名），则按颜色名查表返回十六进制值
        :param G: 绿色分量 0-255
        :param B: 蓝色分量 0-255
        :return:  "#rrggbb" 字符串；分量缺失时返回 None

        示例::
            Color.RGB(30, 144, 255)   # "#1e90ff"（闪兰色）
            Color.RGB("红色")          # "#ff0000"（按中文名查表）
        """
        if R is None or G is None or B is None:
            # 允许 Color.RGB("灰色") 这种按名字查询的用法（兼容中文版）
            if isinstance(R, str) and (R in _COLOR_TABLE):
                return _COLOR_TABLE[R][1]
            if isinstance(R, str) and (R in _ENGLISH_NAMES):
                return _ENGLISH_NAMES[R]
            return None
        # 数值钳位到 0-255，防止浮点越界生成非法颜色（修复原版 #100100100 问题）
        r = max(0, min(255, int(round(R))))
        g = max(0, min(255, int(round(G))))
        b = max(0, min(255, int(round(B))))
        return "#{:02x}{:02x}{:02x}".format(r, g, b)

    @staticmethod
    def hex_of(name):
        """
        把颜色名（中/英文）转换为十六进制值；无法识别时原样返回。 / Convert a color name (Chinese or English) to hex; unknown input is returned as-is.

        :param name: 颜色名，如 "红色"、"black"、"#ABC"
        :return: 十六进制颜色串

        示例::
            Color.hex_of("金色")      # "#ffd700"
            Color.hex_of("gold")     # "#ffd700"
            Color.hex_of("#123")     # "#123"（原样返回）
        """
        if name is None:
            return None
        if name in _COLOR_TABLE:
            return _COLOR_TABLE[name][1]
        if name in _ENGLISH_NAMES:
            return _ENGLISH_NAMES[name]
        return name

    @staticmethod
    def english_name(chinese_name):
        """
        查询中文颜色名对应的英文颜色名。 / Look up the English color name for a Chinese one.

        :param chinese_name: 中文颜色名，如 "黑色"
        :return: 英文名，如 "black"；未找到返回 None

        示例::
            Color.english_name("黑色")   # "black"
        """
        item = _COLOR_TABLE.get(chinese_name)
        return item[0] if item else None

    @staticmethod
    def random():
        """
        返回一个随机十六进制颜色。 / Return a random hex color.

        示例::
            c = Color.random()   # 例如 "#3af192"
        """
        return "#{:02x}{:02x}{:02x}".format(
            random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    # ---------------------------------------------------------------
    # 颜色运算
    # ---------------------------------------------------------------
    @staticmethod
    def invert(color):
        """
        反色（每个分量取 255 差值）。 / Invert the color (each channel becomes 255 minus its value).

        :param color: 任意可识别颜色
        :return: 反色后的十六进制值

        示例::
            Color.invert("#FF0000")   # "#00FFFF"
        """
        r, g, b = Color.to_rgb(color)
        return "#{:02X}{:02X}{:02X}".format(255 - r, 255 - g, 255 - b)

    @staticmethod
    def darken(color, amount=0.08):
        """
        颜色加深。 / Darken a color.

        :param color: 任意可识别颜色
        :param amount: 加深比例 0~1，默认 0.08
        :return: 加深后的十六进制值

        示例::
            Color.darken("red", 0.3)   # "#B30000"
        """
        r, g, b = Color.to_rgb(color)
        f = 1.0 - max(0.0, min(1.0, amount))
        return "#{:02X}{:02X}{:02X}".format(max(0, int(r * f)),
                                            max(0, int(g * f)),
                                            max(0, int(b * f)))

    @staticmethod
    def lighten(color, amount=0.08):
        """
        颜色变浅。 / Lighten a color.

        :param color: 任意可识别颜色
        :param amount: 变浅比例 0~1，默认 0.08
        :return: 变浅后的十六进制值

        示例::
            Color.lighten("navy", 0.2)
        """
        r, g, b = Color.to_rgb(color)
        f = 1.0 - max(0.0, min(0.99, amount))
        return "#{:02X}{:02X}{:02X}".format(min(255, int(r / f)),
                                            min(255, int(g / f)),
                                            min(255, int(b / f)))

    @staticmethod
    def add_colors(colors, keep_alpha=False):
        """
        多个颜色按 RGB 分量依次相加（上限 255）。 / Add several colors channel-wise, clamping each channel at 255.

        :param colors: 颜色列表
        :param keep_alpha: 是否保留透明度分量
        :return: 相加后的十六进制值

        示例::
            Color.add_colors(["#400000", "#004000", "#000040"])  # "#404040"
        """
        if not colors:
            return None
        result = colors[0]
        for c in colors[1:]:
            result = Color.add(result, c, keep_alpha)
        return result

    @staticmethod
    def add(color1, color2, keep_alpha=False):
        """
        两种颜色 RGB 分量相加（各分量上限 255）。 / Add two colors channel-wise, clamping each channel at 255.

        示例::
            Color.add("#800000", "#008000")   # "#808000"（橄榄色）
        """
        rgb1 = Color.to_rgb(color1)
        rgb2 = Color.to_rgb(color2)
        r = min(rgb1[0] + rgb2[0], 255)
        g = min(rgb1[1] + rgb2[1], 255)
        b = min(rgb1[2] + rgb2[2], 255)
        if keep_alpha and len(rgb1) == 4 and len(rgb2) == 4:
            a = min(rgb1[3] + rgb2[3], 255)
            return "#{:02x}{:02x}{:02x}{:02x}".format(r, g, b, a)
        return "#{:02x}{:02x}{:02x}".format(r, g, b)

    @staticmethod
    def blend(base, top, alpha=0.5):
        """
        按透明度叠加两种颜色（模拟顶层颜色以 alpha 叠在底层之上）。 / Blend two colors by alpha, compositing the top color over the bottom one.

        :param base: 底层颜色
        :param top: 顶层颜色
        :param alpha: 顶层透明度 0.0~1.0
        :return: 叠加后的十六进制值

        示例::
            Color.blend("#000000", "#FFFFFF", 0.5)   # "#808080"
        """
        rgb1 = Color.to_rgb(base)
        rgb2 = Color.to_rgb(top)
        a = max(0.0, min(1.0, float(alpha)))
        r = int(rgb1[0] * (1 - a) + rgb2[0] * a)
        g = int(rgb1[1] * (1 - a) + rgb2[1] * a)
        b = int(rgb1[2] * (1 - a) + rgb2[2] * a)
        return "#{:02x}{:02x}{:02x}".format(r, g, b)

    @staticmethod
    def blend_many(colors, alphas=None):
        """
        按顺序叠加多个颜色。 / Blend several colors in order.

        :param colors: 颜色列表
        :param alphas: 每层的透明度列表（默认全 0.5）
        :return: 叠加后的十六进制值

        示例::
            Color.blend_many(["#FF0000", "#0000FF"], [0.5, 0.5])
        """
        if not colors:
            return None
        if len(colors) == 1:
            return Color.hex_of(colors[0])
        if alphas is None:
            alphas = [0.5] * len(colors)
        alphas = list(alphas) + [1.0] * (len(colors) - len(alphas))
        result = colors[0]
        for i in range(1, len(colors)):
            result = Color.blend(result, colors[i], alphas[i])
        return result

    # ---------------------------------------------------------------
    # 内部工具
    # ---------------------------------------------------------------
    @staticmethod
    def to_rgb(color):
        """
        把任意颜色转换为 (r, g, b) 元组（分量 0-255）。 / Convert any color to an (r, g, b) tuple with channels 0-255.

        :param color: 任意可识别颜色（中/英名或十六进制）
        :return: (r, g, b) 元组

        示例::
            Color.to_rgb("#FF8000")   # (255, 128, 0)
        """
        if color is None:
            return (0, 0, 0)
        h = str(color).lstrip("#")
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        if len(h) != 6:
            h = Color.hex_of(color) or "#000000"
            h = str(h).lstrip("#")
            if len(h) == 3:
                h = "".join(c * 2 for c in h)
        try:
            return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
        except (ValueError, TypeError):
            return (0, 0, 0)

    @staticmethod
    def rgb_to_hex(rgb):
        """
        把 (r, g, b) 元组转换为 #rrggbb 字符串。 / Convert an (r, g, b) tuple to a #rrggbb string.

        示例::
            Color.rgb_to_hex((255, 128, 0))   # "#ff8000"
        """
        r, g, b = rgb
        return "#{:02x}{:02x}{:02x}".format(
            max(0, min(255, int(round(r)))),
            max(0, min(255, int(round(g)))),
            max(0, min(255, int(round(b)))))


class ColorName(str, Enum):
    """
    常用颜色枚举（对应「枚举 + 字符串」双写法中的枚举部分）。 / Common color enum - the enum half of the enum-plus-string pattern.

    收录 70 余种日常最常用的颜色；需要更冷门的颜色时直接写字符串
    （``"#7fffd4"`` 或 ``"aquamarine"``）即可，两种写法完全等价。

    为什么推荐枚举：``"gery"`` 这种拼错的颜色浏览器会静默忽略，
    颜色直接不对；用枚举有 IDE 补全，拼错立刻报错。

    示例::
        from malight import ColorName

        pen.circle(100, 100, 50, fill_color=ColorName.TOMATO)     # 枚举
        pen.circle(200, 100, 50, fill_color="#7fffd4")            # 字符串（等价）
        pen.circle(300, 100, 50, fill_color=Color.TRANSPARENT)    # 不填充

        ColorName.RED.value        # "red"
        ColorName.of("tomato")     # ColorName.TOMATO
        ColorName.hex_of("red")    # "#ff0000"
    """

    # ---- 无 / 透明 ----
    TRANSPARENT = "none"      # 不填充、不描边（SVG 的 none）

    # ---- 基础色 ----
    BLACK = "black"
    WHITE = "white"
    RED = "red"
    GREEN = "green"
    BLUE = "blue"
    YELLOW = "yellow"
    ORANGE = "orange"
    PURPLE = "purple"
    PINK = "pink"
    GRAY = "gray"
    BROWN = "brown"
    CYAN = "cyan"
    MAGENTA = "magenta"       # 品红（= fuchsia）
    LIME = "lime"
    NAVY = "navy"
    TEAL = "teal"
    OLIVE = "olive"
    MAROON = "maroon"         # 栗色
    SILVER = "silver"
    GOLD = "gold"

    # ---- 深浅变体（最常用） ----
    DARKRED = "darkred"
    DARKBLUE = "darkblue"
    DARKGREEN = "darkgreen"
    DARKGRAY = "darkgray"
    DARKORANGE = "darkorange"
    LIGHTBLUE = "lightblue"
    LIGHTGREEN = "lightgreen"
    LIGHTGRAY = "lightgray"
    LIGHTYELLOW = "lightyellow"
    LIGHTPINK = "lightpink"

    # ---- 设计常用色 ----
    TOMATO = "tomato"                 # 番茄红
    CORAL = "coral"                   # 珊瑚色
    SALMON = "salmon"                 # 鲑肉色
    CRIMSON = "crimson"               # 猩红
    ORANGERED = "orangered"           # 红橙
    DEEPPINK = "deeppink"             # 深粉
    HOTPINK = "hotpink"               # 亮粉
    ORCHID = "orchid"                 # 淡紫
    PLUM = "plum"                     # 洋李紫
    VIOLET = "violet"                 # 紫罗兰
    INDIGO = "indigo"                 # 靛青
    TURQUOISE = "turquoise"           # 青绿
    AQUAMARINE = "aquamarine"         # 碧绿
    SKYBLUE = "skyblue"               # 天蓝
    STEELBLUE = "steelblue"           # 钢蓝
    SEAGREEN = "seagreen"             # 海绿
    CHOCOLATE = "chocolate"           # 巧克力
    KHAKI = "khaki"                   # 黄褐
    WHEAT = "wheat"                   # 浅黄
    BEIGE = "beige"                   # 米色
    IVORY = "ivory"                   # 象牙
    SNOW = "snow"                     # 雪白
    WHITESMOKE = "whitesmoke"         # 烟白

    # ---- 扩展常用色（英文版补充，均是设计里最常敲到的） ----
    DODGERBLUE = "dodgerblue"         # 道奇蓝（比 skyblue 更饱和）
    ROYALBLUE = "royalblue"           # 宝蓝
    SLATEBLUE = "slateblue"           # 石板蓝
    MIDNIGHTBLUE = "midnightblue"     # 午夜蓝
    LAVENDER = "lavender"             # 薰衣草（浅紫底）
    ALICEBLUE = "aliceblue"           # 极浅蓝底
    MINT_CREAM = "mintcream"          # 薄荷白底
    GAINSBORO = "gainsboro"           # 浅灰底（做卡片底常用）
    DIMGRAY = "dimgray"               # 暗灰（次要文字）
    SLATEGRAY = "slategray"           # 石板灰
    DARKSLATEGRAY = "darkslategray"   # 深石板灰
    FORESTGREEN = "forestgreen"       # 森林绿
    FIREBRICK = "firebrick"           # 砖红
    GOLDENROD = "goldenrod"           # 金菊黄
    SANDYBROWN = "sandybrown"         # 沙棕（肤色近似）
    PERU = "peru"                     # 秘鲁棕
    HONEYDEW = "honeydew"             # 蜜露白底
    SEASHELL = "seashell"             # 贝壳白底

    def __str__(self):
        """让 f-string / print 直接输出颜色值，如 f"{ColorName.RED}" -> "red"。"""
        return self.value

    # ---------------------------------------------------------------
    # 辅助方法
    # ---------------------------------------------------------------
    @staticmethod
    def of(value):
        """
        把颜色字符串 / 枚举名转换为枚举成员。 / Convert a color string or enum name into a ColorName member.

        :return: ColorName 成员；不是常用色时返回 None（此时直接用原字符串即可）

        示例::
            ColorName.of("tomato")     # ColorName.TOMATO
            ColorName.of("TOMATO")     # ColorName.TOMATO（枚举名也认）
            ColorName.of("#7fffd4")    # None（自定义色，直接用字符串）
        """
        if isinstance(value, ColorName):
            return value
        if not isinstance(value, str):
            return None
        try:
            return ColorName(value)
        except ValueError:
            pass
        try:
            return ColorName[value.upper()]
        except KeyError:
            return None

    @staticmethod
    def hex_of(color):
        """
        取颜色的十六进制值（中/英文名均可）。 / Return a color's hex value; Chinese and English names both work.

        示例::
            ColorName.hex_of("red")       # "#ff0000"
            ColorName.hex_of("金色")      # "#ffd700"
            ColorName.hex_of("#abc")      # "#abc"（原样返回）
        """
        return Color.hex_of(color)

    @staticmethod
    def list_names():
        """列出全部枚举名。 / List every enum member name. 示例:: ColorName.list_names()[:3]"""
        return [m.name for m in ColorName]


class ChalkColor:
    """
    粉笔色（黑板上柔和的粉笔质感色板，对应中文版 `粉笔色`）。 / Chalk colors - a soft palette that looks like chalk on a blackboard.

    示例::
        from malight import ChalkColor
        pen.circle(100, 100, 50, fill_color=ChalkColor.PINK)
        palette = ChalkColor.list()   # 全部 13 种粉笔色
    """
    WHITE = "#ffffff"
    RED = "#F98A88"
    PEACH = "#FFABD2"
    YELLOW = "#FFF000"
    GRASS_GREEN = "#D3E6A7"
    GREEN = "#BDEBD0"
    TEAL = "#408A76"
    LIGHT_BLUE = "#ADD2FA"
    BLUE = "#A8CCF5"
    DEEP_BLUE = "#66C5FB"
    ORANGE = "#FDC799"
    PINK = "#FCB5DF"
    PURPLE = "#E4B6FF"

    @staticmethod
    def list():
        """返回全部粉笔色列表。 / Return the full list of chalk colors.

        示例::
            for c in ChalkColor.list():
                print(c)
        """
        return [ChalkColor.WHITE, ChalkColor.RED, ChalkColor.PEACH, ChalkColor.YELLOW,
                ChalkColor.GRASS_GREEN, ChalkColor.GREEN, ChalkColor.TEAL,
                ChalkColor.LIGHT_BLUE, ChalkColor.BLUE, ChalkColor.DEEP_BLUE,
                ChalkColor.ORANGE, ChalkColor.PINK, ChalkColor.PURPLE]


class ColorScheme:
    """
    预置配色方案（对应中文版 `颜色方案`），每项为颜色列表。 / Preset color schemes; each entry is a list of colors.

    示例::
        from malight import ColorScheme, Color
        colors = ColorScheme.RAINBOW
        for i, c in enumerate(colors):
            pen.rect(x=i * 50, y=0, width=50, height=100, fill_color=c)
    """
    RAINBOW = ["red", "orange", "yellow", "green", "cyan", "blue", "purple"]
    RAINBOW_2 = ["#FF0000", "#FF6D00", "#FFFF00", "#59FB46", "#59D5EF", "#5E7EF7", "#B359F6"]
    RGB_PRIMARY = ["#FF0000", "#00FF00", "#0000FF"]
    WARM_EARTH = ["#D2691E", "#8B4513", "#A0522D", "#F4A460", "#DEB887"]
    FRESH_SKY = ["#87CEEB", "#4682B4", "#B0E0E6", "#E0FFFF", "#AFEEEE"]
    ROMANTIC_PINK = ["#FFC0CB", "#FF69B4", "#DA70D6", "#9370DB", "#8A2BE2", "#4B0082"]
    DEEP_OCEAN = ["#000080", "#0000CD", "#1E90FF", "#4169E1", "#6495ED"]
    GOLDEN_HARVEST = ["#FFD700", "#DAA520", "#B8860B", "#CD853F", "#FFA500"]
    FOREST_GREEN = ["#228B22", "#32CD32", "#006400", "#008000", "#2E8B57", "#3CB371"]
    VIVID_ORANGE = ["#FFA07A", "#FF7F50", "#FF6347", "#FF4500", "#FFDAB9", "#FFFF00"]
    ELEGANT_MONO = ["#FFFFFF", "#000000", "#D3D3D3", "#C0C0C0", "#A9A9A9"]
    MYSTIC_NIGHT = ["#000000", "#191970", "#4682B4", "#6495ED", "#87CEFA"]
    DREAM_RAINBOW = ["#FF0000", "#FF7F00", "#FFFF00", "#00FF00", "#0000FF", "#4B0082", "#8B00FF"]
    RETRO_BROWN = ["#8B4513", "#A0522D", "#BC8F8F", "#D2691E", "#F4A460", "#FFA07A"]
    TRANQUIL_LAKE = ["#00FFFF", "#40E0D0", "#7FFFD4", "#48D1CC", "#00CED1"]
    SAKURA_SPRING = ["#FFB6C1", "#FFC0CB", "#FFD1DC", "#FFE1E6", "#FFF5EE"]
    DESERT_CAMEL = ["#F5DEB3", "#FFDEAD", "#D2B48C", "#DEB887", "#CD853F", "#B8860B"]
    COOL_BLACK = ["#000000", "#2F4F4F", "#483D8B", "#696969", "#808080"]
    BLUE_PORCELAIN = ["#000080", "#0000CD", "#4169E1", "#6495ED", "#87CEEB", "#B0E0E6", "#FFFFFF"]
    PASTURE_GREEN = ["#98FB98", "#90EE90", "#7CFC00", "#32CD32", "#228B22"]
    NEON = ["#FF00FF", "#FF6D00", "#00FF00", "#00FFFF", "#8B0082"]
    ICE_WHITE = ["#F0FFFF", "#E0FFFF", "#AFEEEE", "#DCDCDC", "#C0C0C0"]

    @staticmethod
    def cyclic(index, scheme):
        """
        循环取色：索引超出方案长度时从头再取。 / Cyclic color pick - wraps to the start when the index exceeds the scheme length.

        :param index: 索引（可为任意整数）
        :param scheme: 颜色方案列表
        :return: 对应颜色

        示例::
            ColorScheme.cyclic(7, ColorScheme.RAINBOW)   # 取第 1 个（循环）
        """
        return scheme[index % len(scheme)]


# ---------------------------------------------------------------------------
# 字体：旧名 SystemFont 保留为 Font 的别名（v2 起统一用 Font，语义同「系统字体」）
# ---------------------------------------------------------------------------
# 用法（三种写法可混用，详见 malight/fonts.py）：
#     font=Font.SIMHEI                        # 1) 枚举（推荐，有补全、拼错即报错）
#     font="Microsoft YaHei"                  # 2) 字体名字符串（任意已安装字体）
#     font=r"C:\Windows\Fonts\simkai.ttf"     # 3) 字体文件（自动 base64 内嵌）
SystemFont = Font


class VectorEffect(str, Enum):
    """
    元素矢量效果（SVG vector-effect，对应中文版 `元素矢量效果`）。 / SVG vector-effect.

    示例::
        pen.line((10, 10), (300, 10), stroke_width=2,
                      vector_effect=VectorEffect.NON_SCALING_STROKE)
    """

    NONE = "none"
    NON_SCALING_STROKE = "non-scaling-stroke"  # 缩放时线宽不变
    NON_SCALING_SIZE = "non-scaling-size"  # 缩放时图形大小不变
    NON_ROTATION = "non-rotation"  # 抑制旋转/倾斜
    FIXED_POSITION = "fixed-position"  # 固定位置

    def __str__(self):
        """让 f-string / print 直接输出取值（枚举 + 字符串双写法）。"""
        return self.value
class ScreenResolution:
    """
    常用屏幕分辨率（对应中文版 `屏幕分辨率`），返回 (宽, 高)。 / Common screen resolutions as (width, height).

    示例::
        w, h = ScreenResolution.PHONE()
        pen = MagicPen("wallpaper", width=w, height=h)
    """

    @staticmethod
    def PHONE():
        """常见手机分辨率 1080x2376。 / Common phone resolution 1080x2376. """
        return 1080, 2376

    @staticmethod
    def FULL_HD():
        """全高清 1920x1080。 / Full HD 1920x1080. """
        return 1920, 1080

    @staticmethod
    def HD():
        """高清 1280x720。 / HD 1280x720. """
        return 1280, 720

    @staticmethod
    def HUAWEI_ENJOY_60X():
        """华为畅享 60X：1080x2376。 / Huawei Enjoy 60X: 1080x2376. """
        return 1080, 2376

    @staticmethod
    def HUAWEI_NOVA12():
        """华为 Nova12：1084x2412。 / Huawei Nova 12: 1084x2412. """
        return 1084, 2412

    @staticmethod
    def HUAWEI_MATE50():
        """华为 Mate50：1224x2700。 / Huawei Mate 50: 1224x2700. """
        return 1224, 2700


class PaperSize:
    """
    纸张尺寸（像素，对应中文版 `纸张大小`）。 / Paper sizes in pixels.

    以 A4 为基准（缩放系数 3.68 像素/毫米），返回 (宽, 高)。

    示例::
        w, h = PaperSize.A4_portrait()
        pen = MagicPen("report", width=w, height=h)
    """
    SCALE_FACTOR = 3.68   # 像素/毫米

    @staticmethod
    def A3_landscape(sheets=1):
        """A3 横向（420mm x 297mm）。sheets 为连续纸张页数（高度方向拼接）。 / A3 landscape (420mm x 297mm); sheets is the number of pages stacked vertically. """
        return 420 * PaperSize.SCALE_FACTOR, 297 * PaperSize.SCALE_FACTOR * sheets

    @staticmethod
    def A3_portrait(sheets=1):
        """A3 纵向。 / A3 portrait. """
        return 297 * PaperSize.SCALE_FACTOR, 420 * PaperSize.SCALE_FACTOR * sheets

    @staticmethod
    def A4_landscape(sheets=1):
        """A4 横向（297mm x 210mm）。 / A4 landscape (297mm x 210mm). """
        return 297 * PaperSize.SCALE_FACTOR, 210 * PaperSize.SCALE_FACTOR * sheets

    @staticmethod
    def A4_portrait(sheets=1):
        """A4 纵向。 / A4 portrait. """
        return 210 * PaperSize.SCALE_FACTOR, 297 * PaperSize.SCALE_FACTOR * sheets

    @staticmethod
    def A5_landscape(sheets=1):
        """A5 横向。 / A5 landscape. """
        return 210 * PaperSize.SCALE_FACTOR, 148 * PaperSize.SCALE_FACTOR * sheets

    @staticmethod
    def A5_portrait(sheets=1):
        """A5 纵向。 / A5 portrait. """
        return 148 * PaperSize.SCALE_FACTOR, 210 * PaperSize.SCALE_FACTOR * sheets


class PaperOrientation:
    """页面方向（对应中文版 `纸张方向`）。 / Page orientation.

    示例::
        PaperOrientation.AUTO   # 自动（按宽高比判断）
    """
    AUTO = None
    LANDSCAPE = True
    PORTRAIT = False


class TextHAlign(str, Enum):
    """
    文字水平对齐（SVG text-anchor，对应中文版 `文字水平基线对齐`）。 / Horizontal text alignment (SVG text-anchor).

    示例::
        pen.text(400, 100, "居中标题", h_align=TextHAlign.MIDDLE)
    """

    START = "start"  # 左对齐（默认）
    MIDDLE = "middle"  # 居中
    END = "end"  # 右对齐

    def __str__(self):
        """让 f-string / print 直接输出取值（枚举 + 字符串双写法）。"""
        return self.value


class TextVAlign(str, Enum):
    """
    文字垂直对齐（SVG alignment-baseline / dominant-baseline，
    对应中文版 `文字垂直基线对齐`）。 / Vertical text alignment (SVG alignment-baseline / dominant-baseline).

    示例::
        pen.text(100, 300, "中线对齐", v_align=TextVAlign.MIDDLE)
    """

    BASELINE = "text-after-edge"  # 底线对齐（默认）
    MIDDLE = "middle"  # 中线对齐
    TOP = "text-before-edge"  # 顶线对齐

    def __str__(self):
        """让 f-string / print 直接输出取值（枚举 + 字符串双写法）。"""
        return self.value


class ArrowStyle(str, Enum):
    """
    箭头样式（对应中文版 `箭头样式`）。 / Arrowhead styles.

    示例::
        pen.draw_arrow_line((50, 50), (250, 50), style=ArrowStyle.SOLID)
    """

    SOLID = "solid"  # 实心三角箭头
    HOLLOW = "hollow"  # 空心三角箭头
    BARBED = "barbed"  # 倒钩形箭头（默认）

    def __str__(self):
        """让 f-string / print 直接输出取值（枚举 + 字符串双写法）。"""
        return self.value


class StrokeJoin(str, Enum):
    """
    描边拐角连接样式（SVG stroke-linejoin，对应中文版 `描边线连接样式`）。 / Stroke corner join style (SVG stroke-linejoin).

    示例::
        pen.polyline([(10, 10), (100, 60), (50, 120)],
                          stroke_join=StrokeJoin.ROUND)
    """

    MITER = "miter"  # 尖角（默认）
    ROUND = "round"  # 圆角
    BEVEL = "bevel"  # 斜角

    def __str__(self):
        """让 f-string / print 直接输出取值（枚举 + 字符串双写法）。"""
        return self.value


class StrokeCap(str, Enum):
    """
    描边线端样式（SVG stroke-linecap，对应中文版 `描边线端样式`）。 / Stroke line cap style (SVG stroke-linecap).

    示例::
        pen.line((10, 50), (200, 50), stroke_cap=StrokeCap.ROUND, stroke_width=8)
    """

    BUTT = "butt"  # 直角截断（默认）
    ROUND = "round"  # 半圆头（画胶囊线常用）
    SQUARE = "square"  # 方形延伸

    def __str__(self):
        """让 f-string / print 直接输出取值（枚举 + 字符串双写法）。"""
        return self.value


class ImageRendering(str, Enum):
    """
    图像渲染设置（SVG image-rendering，对应中文版 `图像渲染设置`）。 / Image rendering hints (SVG image-rendering).

    示例::
        pen.image("logo.png", 0, 0, rendering=ImageRendering.PIXELATED)
    """

    AUTO = "auto"
    SMOOTH = "smooth"
    HIGH_QUALITY = "high-quality"
    CRISP_EDGES = "crisp-edges"
    PIXELATED = "pixelated"
    OPTIMIZE_QUALITY = "optimizeQuality"

    def __str__(self):
        """让 f-string / print 直接输出取值（枚举 + 字符串双写法）。"""
        return self.value


class PointStyle(str, Enum):
    """
    调试定位点样式（对应中文版 `定位点类型`）。 / Debug point style.

    示例::
        pen.mark_point(100, 100, style=PointStyle.CIRCLE_SOLID)
    """

    CROSS = "cross"  # 十字线
    CIRCLE_HOLLOW = "circle_hollow"  # 空心圆
    CIRCLE_SOLID = "circle_solid"  # 实心圆
    SQUARE_HOLLOW = "square_hollow"  # 空心方
    SQUARE_SOLID = "square_solid"  # 实心方

    def __str__(self):
        """让 f-string / print 直接输出取值（枚举 + 字符串双写法）。"""
        return self.value


class GridRepeatType(IntEnum):
    """
    网格重复排布类型（对应中文版 `网格重复类型`）。 / Grid repeat layout types.

    示例::
        pen.repeat_grid(star, cols=4, col_gap=60, rows=3, row_gap=60,
                        grid_type=GridRepeatType.BRICK_OFFSET)
    """

    PLAIN = 0  # 普通网格
    BRICK_OFFSET = 1  # 横向砖型交错（奇数行偏移半格）
    BRICK_VERTICAL = 2  # 纵向砖型交错（奇数列偏移半格）

    def __str__(self):
        """让 f-string / print 直接输出取值（枚举 + 字符串双写法）。"""
        return str(self.value)


class CoordUnits(str, Enum):
    """
    空间坐标系单位（SVG gradientUnits/clipPathUnits 等，对应中文版 `空间坐标系单位`）。 / Coordinate-space units (SVG gradientUnits / clipPathUnits and friends).

    示例::
        pen.clip(clip_shape, target, units=CoordUnits.USER_SPACE)
    """

    USER_SPACE = "userSpaceOnUse"  # 用户空间坐标
    OBJECT_BOUNDING_BOX = "objectBoundingBox"  # 物体边界框相对坐标

    def __str__(self):
        """让 f-string / print 直接输出取值（枚举 + 字符串双写法）。"""
        return self.value
@dataclass
class PaperSettings:
    """
    页面打印设置（对应中文版 `纸张设置`），用于 finish() 时的 @page 样式。 / Print settings used for the @page rule emitted by finish().

    示例::
        settings = PaperSettings(margin_top=10, margin_right=10,
                                 margin_bottom=10, margin_left=10)
        pen.page_setup(settings)
    """
    margin_top: Union[float, int] = 0
    margin_bottom: Union[float, int] = 0
    margin_left: Union[float, int] = 0
    margin_right: Union[float, int] = 0
    orientation: bool = PaperOrientation.AUTO   # 自动识别
    paper_size: str = "A4"
    page_scale: float = 1.0


class PDFMode(IntEnum):
    """PDF 导出方式（对应中文版 `PDF生成方式`）。 / PDF export engines. """

    AUTO = 0
    CHROME = 1  # 调用本机 Chrome 打印
    CAIROSVG = 2

    def __str__(self):
        """让 f-string / print 直接输出取值（枚举 + 字符串双写法）。"""
        return str(self.value)


class PNGMode(IntEnum):
    """PNG 导出方式（对应中文版 `PNG生成方式`）。 / PNG export engines. """

    AUTO = 0
    CAIROSVG = 1
    CHROME = 2

    def __str__(self):
        """让 f-string / print 直接输出取值（枚举 + 字符串双写法）。"""
        return str(self.value)


class DOCXMode(IntEnum):
    """DOCX 导出方式（对应中文版 `DOCX生成方式`）。 / DOCX export engines. """

    AUTO = 0
    PDF2DOCX = 1
    ASPOSE_WORDS = 2

    def __str__(self):
        """让 f-string / print 直接输出取值（枚举 + 字符串双写法）。"""
        return str(self.value)


# ===========================================================================
# 更多「值就那么几个」的枚举（英文版新增，全部为 枚举 + 字符串 双写法）
# ===========================================================================

class FillRule(str, Enum):
    """
    填充规则（SVG fill-rule，对应中文版 `填充规则`）。 / Fill rule (SVG fill-rule).

    做「带孔洞」的图形（甜甜圈、镂空字、简笔画挖洞）时必须用它：
    外圈 + 内圈顶点合在一起 + EVENODD，中间自动挖空。

    示例::
        outer = [(60, 60), (240, 60), (240, 240), (60, 240)]
        inner = [(110, 110), (190, 110), (190, 190), (110, 190)]
        pen.polygon(outer + inner, fill_color="teal",
                    fill_rule=FillRule.EVENODD)     # 中间挖空
    """

    NONZERO = "nonzero"     # 非零环绕（默认，中间不挖空）
    EVENODD = "evenodd"     # 奇偶环绕（中间挖空）

    def __str__(self):
        """让 f-string / print 直接输出取值（枚举 + 字符串双写法）。"""
        return self.value


class DashStyle(str, Enum):
    """
    虚线样式预设（SVG stroke-dasharray，英文版新增）。 / Dash presets (SVG stroke-dasharray).

    以前要手写 ``stroke_style="8 4"`` 这种谜之字符串，现在可以直接选预设；
    需要任意间距时仍然可以写字符串。

    示例::
        pen.rect(50, 50, 200, 100, stroke_style=DashStyle.DASHED)
        pen.rect(50, 200, 200, 100, stroke_style="12 3 2 3")   # 自定义也可以
    """

    SOLID = ""                     # 实线（不设虚线）
    DOTTED = "2 4"                 # 点线
    DENSE = "4 3"                  # 密虚线
    DASHED = "8 4"                 # 标准虚线
    LONG_DASH = "16 6"             # 长虚线
    DASH_DOT = "12 4 2 4"          # 点划线
    DASH_DOT_DOT = "12 4 2 4 2 4"  # 双点划线（工程图常用）

    def __str__(self):
        """让 f-string / print 直接输出取值（枚举 + 字符串双写法）。"""
        return self.value


class PaintOrder(str, Enum):
    """
    绘制顺序（SVG paint-order，英文版新增）。 / Paint order (SVG paint-order).

    默认先填充后描边，描边会盖住填充的边缘；做「空心字」或细线加粗时
    用 ``PAINT_ORDER.STROKE`` 让描边先画、填充后画，字面保持完整粗细。

    示例::
        pen.text(200, 100, "空心字", font_size=48, fill_color="white",
                 stroke_color="black", stroke_width=3,
                 paint_order=PaintOrder.STROKE)      # 先描边，填充不被吃掉
    """

    FILL = "fill"                  # 先填充后描边（SVG 默认）
    STROKE = "stroke"              # 先描边后填充（空心字常用）
    FILL_STROKE = "fill stroke"    # 同 FILL（显式写法）
    STROKE_FILL = "stroke fill"    # 同 STROKE（显式写法）
    STROKE_MARKERS = "stroke markers fill"   # 含标记的完整顺序

    def __str__(self):
        """让 f-string / print 直接输出取值（枚举 + 字符串双写法）。"""
        return self.value


class BlendMode(str, Enum):
    """
    混合模式（CSS mix-blend-mode，英文版新增）。 / Blend modes (CSS mix-blend-mode).

    写在元素的 ``blend_mode=`` 参数上，效果等同 PS 的图层混合模式。

    示例::
        pen.circle(200, 150, 100, fill_color="red",
                   blend_mode=BlendMode.MULTIPLY)      # 正片叠底
    """

    NORMAL = "normal"                # 正常
    MULTIPLY = "multiply"            # 正片叠底（最常用，做阴影/加深）
    SCREEN = "screen"                # 滤色（提亮）
    OVERLAY = "overlay"              # 叠加
    DARKEN = "darken"                # 变暗
    LIGHTEN = "lighten"              # 变亮
    COLOR_DODGE = "color-dodge"      # 颜色减淡
    COLOR_BURN = "color-burn"        # 颜色加深
    HARD_LIGHT = "hard-light"        # 强光
    SOFT_LIGHT = "soft-light"        # 柔光
    DIFFERENCE = "difference"        # 差值
    EXCLUSION = "exclusion"          # 排除
    HUE = "hue"                      # 色相
    SATURATION = "saturation"        # 饱和度
    COLOR = "color"                  # 颜色
    LUMINOSITY = "luminosity"        # 明度

    def __str__(self):
        """让 f-string / print 直接输出取值（枚举 + 字符串双写法）。"""
        return self.value


class FontWeight(str, Enum):
    """
    字重（SVG font-weight，英文版新增）。 / Font weights (SVG font-weight).

    也可以用 ``bold=True``；需要「特粗/极细」这类档位时用本枚举，
    或者直接写数字字符串 ``weight="700"``。

    示例::
        pen.text(100, 100, "常规", weight=FontWeight.NORMAL)
        pen.text(100, 160, "加粗", weight=FontWeight.BOLD)
        pen.text(100, 220, "特粗", weight=FontWeight.W900)
    """

    THIN = "100"
    EXTRA_LIGHT = "200"
    LIGHT = "300"
    NORMAL = "normal"
    MEDIUM = "500"
    SEMI_BOLD = "600"
    BOLD = "bold"
    EXTRA_BOLD = "800"
    BLACK = "900"
    LIGHTER = "lighter"      # 相对父元素更细
    BOLDER = "bolder"        # 相对父元素更粗
    # 数字档位别名（W400 与 NORMAL 等价，写哪个都行）
    W100 = "100"
    W200 = "200"
    W300 = "300"
    W400 = "normal"
    W500 = "500"
    W600 = "600"
    W700 = "bold"
    W800 = "800"
    W900 = "900"

    def __str__(self):
        """让 f-string / print 直接输出取值（枚举 + 字符串双写法）。"""
        return self.value


class TextDecoration(str, Enum):
    """
    文字修饰线（SVG text-decoration，英文版新增）。 / Text decoration lines (SVG text-decoration).

    示例::
        pen.text(100, 100, "下划线", decoration=TextDecoration.UNDERLINE)
        pen.text(100, 160, "删除线", decoration=TextDecoration.LINE_THROUGH)
    """

    NONE = "none"
    UNDERLINE = "underline"           # 下划线
    OVERLINE = "overline"             # 上划线
    LINE_THROUGH = "line-through"     # 删除线

    def __str__(self):
        """让 f-string / print 直接输出取值（枚举 + 字符串双写法）。"""
        return self.value


class LengthAdjust(str, Enum):
    """
    文字宽度调整方式（SVG lengthAdjust，配合 text_length 使用）。 / How text width is adjusted (SVG lengthAdjust, used with text_length).

    示例::
        pen.text(100, 100, "正好铺满 300 宽", text_length=300,
                 length_adjust=LengthAdjust.SPACING_AND_GLYPHS)
    """

    SPACING = "spacing"                       # 只调字间距（默认）
    SPACING_AND_GLYPHS = "spacingAndGlyphs"   # 字间距与字形一起拉伸

    def __str__(self):
        """让 f-string / print 直接输出取值（枚举 + 字符串双写法）。"""
        return self.value


class AspectRatio(str, Enum):
    """
    图片缩放保持比例方式（SVG preserveAspectRatio，英文版新增）。 / How an image keeps its aspect ratio (SVG preserveAspectRatio).

    示例::
        pen.image("logo.png", 0, 0, 200, 100, aspect=AspectRatio.SLICE)
    """

    STRETCH = "none"                 # 拉满（可能变形）
    MEET = "xMidYMid meet"           # 完整显示（可能留白，默认）
    SLICE = "xMidYMid slice"         # 铺满裁切（可能裁边）

    def __str__(self):
        """让 f-string / print 直接输出取值（枚举 + 字符串双写法）。"""
        return self.value

    @staticmethod
    def custom(align_x="Mid", align_y="Mid", meet=True):
        """
        自定义对齐方式，如 "xMinYMin meet"。 / Custom alignment, e.g. "xMinYMin meet".

        :param align_x: Min / Mid / Max
        :param align_y: Min / Mid / Max
        :param meet: True=meet（完整显示）；False=slice（裁切铺满）

        示例::
            pen.image("p.png", 0, 0, 200, 200, aspect=AspectRatio.custom("Min", "Min"))
        """
        return "x{}Y{} {}".format(align_x, align_y, "meet" if meet else "slice")


class SpreadMethod(str, Enum):
    """
    渐变扩散方式（SVG spreadMethod，英文版新增）。 / Gradient spread method (SVG spreadMethod).

    当渐变范围小于图形时，决定「超出部分」怎么取色。

    示例::
        pen.linearGradient((0, 0), (0.3, 0), "red", "blue", spread=SpreadMethod.REFLECT)
    """

    PAD = "pad"           # 用两端颜色填充（默认）
    REFLECT = "reflect"   # 镜像重复
    REPEAT = "repeat"     # 直接重复

    def __str__(self):
        """让 f-string / print 直接输出取值（枚举 + 字符串双写法）。"""
        return self.value


# ---------------------------------------------------------------------------
# 布尔便捷常量（中文版 是/否/开/关 的英文对应，便于迁移）
# ---------------------------------------------------------------------------
YES = True
NO = False
ON = True
OFF = False

# 全角空格（中文排版常用）
FULL_WIDTH_SPACE = "\u3000"
