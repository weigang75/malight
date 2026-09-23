# -*- coding: utf-8 -*-
"""
malight —— 《神笔码靓》英文版工具包（码靓 / Magic Light）
=========================================================

由中文版「神笔码靓」完整移植并增强而来的 SVG 矢量绘图工具包。
包名 malight = Ma(gic) + light，读音贴近「码靓」，含义「魔术之光」。

特性 / Features:
    1. 全英文 API，文档字符串「摘要级双语」（首行中文 / English 对照），
       每个类文件都能直接运行看示例；
    2. 不依赖 svgwrite，内置轻量 SVG 序列化后端，完整支持 SVG 规范能力
       （fill-rule 挖洞、旋转、虚线偏移、滤镜、SMIL 动画等原版缺失的特性）;
    3. 滤镜工厂 pen.fx（参考 PS/AI 常用滤镜）：投影/内阴影/外发光/内发光/
       斜面浮雕/外描边/高斯模糊/锐化/动感模糊/粗糙化/噪点/浮雕/边缘检测/
       饱和度/色相/亮度/对比度/伽马/反相/色调分离/颜色叠加，支持链式叠加；
    4. 扩展机制 malight.ext：第三方工具包用 @toolkit 装饰器注册，
       pen.use_toolkit("名字") 一行挂载到绘图板；
    5. 兼容迁移：malight.compat 提供中文→英文名称对照表与脚本迁移工具；
       旧脚本中的 `import magicpen` 会被迁移为 `import malight`，
       同时包内自带 magicpen 兼容 shim（旧脚本不改也能跑）;
    6. 运行时多语言 malight.i18n：报错/提示/导出信息**默认英文**，
       `malight.set_language("zh")` 一行切中文（也可用环境变量 MALIGHT_LANG）；
    7. 终端提示带颜色：导出消息整行加粗、**文件路径绿色**（一眼就能找到文件），
       重定向/管道时自动不上色，也可 `malight.set_color(False)` 关掉
       （环境变量 NO_COLOR / MALIGHT_COLOR 同样有效）。

快速上手:
    from malight import Malight, Color

    pen = Malight("hello", width=800, height=600)    # 创建绘图板
    pen.set_background_color(Color.WHITE)            # 白色背景
    pen.circle(x=400, y=300, radius=150,             # 画一个圆（SVG 命名）
               fill_color=Color.RGB(30, 144, 255),
               stroke_color=Color.NAVY, stroke_width=5)
    pen.text(x=400, y=300, text="Hello malight!", font_size=48,
             fill_color=Color.WHITE, h_align=TextHAlign.MIDDLE)
    pen.circle(650, 450, 60, fill_color="#e63946",
               filter=pen.fx.shadow(6, 8, 6))        # 一行加滤镜
    pen.finish()                                     # 保存 SVG

模块地图:
    definitions   —— 颜色/字体/纸张/枚举常量定义
    svg_backend   —— 轻量 SVG 元素与序列化（内部使用）
    i18n          —— 运行时多语言（默认英文，可切中文）
    elements      —— 全部图形元素类（圆/矩形/路径/文字/组/渐变...）
    elements.path —— 路径元素（贝塞尔/圆弧/海龟绘图/布尔运算）
    board         —— MagicPen 绘图板（主入口，约 130 个绘图方法）
    board.fx      —— FilterChain 链式滤镜引擎
    pathkit       —— 路径辅助（看结构、拖锚点与调整点、点位存档）
    ext           —— 扩展机制（@toolkit 注册第三方工具包）
    tools         —— SVG 导入导出/几何工具/字体工具
    compat        —— 中文 API 对照与迁移工具

文档 / Docs:
    总览见仓库根 README.md（中文）/ README.en.md（English）；
    每个模块的详细用法就在**同目录的同名 .md 文件**里，例如
    `malight/elements/path.py` 对应 `malight/elements/path.md` 与
    `malight/elements/path.en.md`。改 API 时顺手改旁边那篇，文档永不脱节。
"""

from malight import i18n

from malight.i18n import (
    Language, get_language, set_language, use_language, reset_language,
    is_chinese, t, available_languages, add_messages,
)

from malight.fonts import Font, find_font_file, font_face_css, subset_font

from malight.page import PageSetup, paper_css

from malight.tools import set_color, color_enabled, paint, asset_path, asset_dir

from malight.definitions import (
    Color, ColorName, ChalkColor, ColorScheme, SystemFont,
    PaperSize, PaperOrientation, PaperSettings,
    StrokeCap, StrokeJoin, ArrowStyle, PointStyle,
    TextHAlign, TextVAlign, GridRepeatType, CoordUnits,
    ImageRendering, VectorEffect, ScreenResolution,
    FillRule, DashStyle, BlendMode, FontWeight, TextDecoration,
    LengthAdjust, AspectRatio, SpreadMethod, PaintOrder,
    PDFMode, PNGMode, DOCXMode, value_of,
)

from malight.elements import (
    Element, CircleElement, EllipseElement, RectElement, LineElement,
    PolylineElement, PolygonElement, TextElement, TextPathElement,
    ImageElement, SVGImageElement, GroupElement, TemplateElement,
    UseElement, MarkerElement, ClipPathElement, MaskElement,
    LinkElement, PatternElement,
)

from malight.elements.path import PathElement

from malight.pathkit import PathEditor, PathPoint, PathSegment

from malight.gradients import LinearGradient, RadialGradient

from malight.board import MagicPen, MaLight, Malight, FilterAPI, FilterChain

from malight import ext

__version__ = "2.2.0"

__all__ = [
    # 绘图板（MaLight 为正式类名 / 商品名，Malight 兼容旧写法）
    "MagicPen", "MaLight", "Malight", "FilterAPI", "FilterChain",
    # 页面设置（打印/PDF，仅 Chrome 引擎）
    "PageSetup", "paper_css",
    # 元素类
    "Element", "CircleElement", "EllipseElement", "RectElement", "LineElement",
    "PolylineElement", "PolygonElement", "TextElement", "TextPathElement",
    "ImageElement", "SVGImageElement", "GroupElement", "TemplateElement",
    "UseElement", "MarkerElement", "ClipPathElement", "MaskElement",
    "LinkElement", "PatternElement", "PathElement",
    # 路径辅助（英文版新增）
    "PathEditor", "PathPoint", "PathSegment",
    # 渐变
    "LinearGradient", "RadialGradient",
    # 定义集：颜色
    "Color", "ColorName", "ChalkColor", "ColorScheme",
    # 定义集：字体
    "Font", "SystemFont", "find_font_file", "font_face_css", "subset_font",
    # 定义集：纸张
    "PaperSize", "PaperOrientation", "PaperSettings",
    # 定义集：枚举（枚举 + 字符串双写法）
    "StrokeCap", "StrokeJoin", "ArrowStyle", "PointStyle",
    "TextHAlign", "TextVAlign", "GridRepeatType", "CoordUnits",
    "ImageRendering", "VectorEffect", "ScreenResolution",
    "FillRule", "DashStyle", "BlendMode", "FontWeight", "TextDecoration",
    "LengthAdjust", "AspectRatio", "SpreadMethod",
    "PDFMode", "PNGMode", "DOCXMode", "value_of",
    # 运行时多语言（默认英文，可一行切中文）
    "i18n", "Language", "get_language", "set_language", "use_language",
    "reset_language", "is_chinese", "t", "available_languages", "add_messages",
    # 终端颜色（提示更醒目：整体加粗、路径绿色；可一键关掉）
    "set_color", "color_enabled", "paint",
    # 包内资源（assets/images 预览图、assets/fonts 字体文件）查找
    "asset_path", "asset_dir",
]
