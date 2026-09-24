# -*- coding: utf-8 -*-
"""
兼容迁移（compat）—— 中文 API → 英文 API 对照与迁移工具
==========================================================

Mapping tables and a script migrator from the Chinese API to the English one.

帮助老用户把「神笔码靓」中文脚本迁移到 magicpen 英文版。

提供两种用法：

    1. 在线兼容层（零改动运行旧代码思路的参考）::

        import malight.compat as compat
        compat.print_mapping("画圆")     # 查询单个映射

    2. 离线迁移脚本::

        python -m malight.compat 旧脚本.py 新脚本.py
        # 自动把中文名称替换为英文版名称（正则批量替换，改动处人工复核）
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

import re
from .i18n import t

# ---------------------------------------------------------------------------
# 类名映射：中文类 -> 英文类
# ---------------------------------------------------------------------------
CLASS_MAP = {
    "神笔绘图板": "Malight",
    "路径元素": "PathElement",
    "圆元素": "CircleElement",
    "椭圆元素": "EllipseElement",
    "矩形元素": "RectElement",
    "线元素": "LineElement",
    "折线元素": "PolylineElement",
    "多边形元素": "PolygonElement",
    "文字元素": "TextElement",
    "路径文字元素": "TextPathElement",
    "图元素": "ImageElement",
    "SVG图元素": "SVGImageElement",
    "元素组": "GroupElement",
    "元素模板": "TemplateElement",
    "复用元素": "UseElement",
    "标记元素": "MarkerElement",
    "裁剪元素": "ClipPathElement",
    "遮罩元素": "MaskElement",
    "链接元素": "LinkElement",
    "元素图案": "PatternElement",
    "线性渐变色": "LinearGradient",
    "径向渐变色": "RadialGradient",
    "颜色": "Color",
    "粉笔色": "ChalkColor",
    "颜色方案": "ColorScheme",
    "系统字体": "SystemFont",
    "纸张大小": "PaperSize",
    "纸张方向": "PaperOrientation",
    "纸张设置": "PaperSettings",
    "描边线端样式": "StrokeCap",
    "描边线连接样式": "StrokeJoin",
    "箭头样式": "ArrowStyle",
    "定位点类型": "PointStyle",
    "文字水平基线对齐": "TextHAlign",
    "文字垂直基线对齐": "TextVAlign",
    "网格重复类型": "GridRepeatType",
    "空间坐标系单位": "CoordUnits",
    "图像渲染设置": "ImageRendering",
    "元素矢量效果": "VectorEffect",
    "屏幕分辨率": "ScreenResolution",
    "PDF生成方式": "PDFMode",
    "PNG生成方式": "PNGMode",
    "DOCX生成方式": "DOCXMode",
}

# ---------------------------------------------------------------------------
# 绘图板方法映射：中文方法 -> 英文方法
# ---------------------------------------------------------------------------
METHOD_MAP = {
    # 基本图形
    "画圆": "circle", "画椭圆": "ellipse", "画矩形": "rect",
    "画正方形": "square", "画线": "line", "画直线": "line",
    "画折线": "polyline", "画多边形": "polygon",
    "画正N边形": "regular_polygon", "画正三边形": "triangle",
    "画正五边形": "pentagon", "画正六边形": "hexagon",
    "画N角星": "star", "画五角星": "star",
    "画菱型": "diamond", "画爱心": "heart", "十字": "cross",
    # 连线/路径
    "路径": "path", "连直线": "connect_points", "连线": "connect_points",
    "连曲线": "connect_curve", "画波浪线": "wave_line",
    "画海浪线": "wavy_line", "画水平线": "h_lines",
    "画垂直线": "v_lines", "画表格": "table",
    "矩形背景": "add_background_rect",
    # 文字
    "写字": "text", "路径文字": "textPath", "文字转路径": "text_to_path",
    # 箭头
    "箭头线": "arrow_line", "获取箭头路径": "arrow_path",
    # 裁剪遮罩
    "裁剪": "clipPath", "圆形裁剪": "clip_circle", "矩形裁剪": "clip_rect",
    "遮罩": "mask",
    # 调试
    "测距": "measure", "显示网格": "grid", "显示图框": "frame",
    "定位点": "mark_point", "定位坐标": "mark_point",
    "显示关键点": "key_points",
    # 容器
    "创建组合": "g", "创建模板": "symbol",
    "神笔模板": "use", "创建图案": "pattern",
    "复制元素": "copy", "创建链接": "a",
    "创建标记": "marker", "获取元素": "get_element",
    # 图像
    "贴图": "image", "SVG贴图": "svg_image",
    "导入SVG为组": "import_svg_as_group", "导入SVG为模板": "import_svg_as_symbol",
    # 排列重复
    "水平排列": "arrange_horizontal", "垂直排列": "arrange_vertical",
    "网格水平排列": "arrange_grid_by_cols", "网格垂直排列": "arrange_grid_by_rows",
    "环绕排列": "arrange_circle", "环绕重复": "repeat_around_circle",
    "网格重复": "repeat_grid", "水平方向重复": "repeat_horizontal",
    "垂直方向重复": "repeat_vertical",
    # 渐变
    "创建线性渐变色": "linearGradient",
    "创建径向渐变色": "radialGradient",
    "创建彩虹线性渐变色": "rainbow_linear_gradient",
    "创建彩虹径向渐变色": "rainbow_radial_gradient",
    "创建黄金线性渐变色": "gold_linear_gradient",
    "彩虹渐变点": "rainbow_stops",
    # 画布
    "设置背景色": "set_background_color", "修改绘图板大小": "resize",
    "增加JS代码": "add_js", "写软件信息": "write_app_info",
    "作者印章": "author_seal",
    # 生命周期
    "完成": "finish", "生成PNG": "export_png", "生成图片": "export_png",
    "生成PDF": "export_pdf", "生成DOCX": "export_docx",
    "页面设置": "page_setup", "增加配置项": "set_config",
    "获取配置项": "get_config",
}

# ---------------------------------------------------------------------------
# PathElement 方法映射
# ---------------------------------------------------------------------------
PATH_METHOD_MAP = {
    "移动到": "move_to", "落笔": "move_to", "画直线": "line",
    "画水平线": "h_lines", "画垂直线": "v_lines",
    "三次贝塞尔曲线": "cubic_to", "画曲线": "cubic_to", "平滑曲线": "smooth_cubic_to",
    "二次贝塞尔曲线": "quad_to", "平滑的二次贝塞尔曲线": "smooth_quad_to",
    "画圆弧": "arc_to", "画椭圆弧": "ellipse_arc_to", "画圆": "circle",
    "闭合": "close", "新路径": "new_subpath", "反向路径": "reverse",
    "并集": "union", "交集": "intersect", "差集": "subtract",
    "合并路径": "merge", "坐标平移": "translate_cmds", "坐标缩放": "scale_cmds",
    "坐标旋转": "rotate_cmds", "平滑路径": "smooth",
    "右转弧线": "turn_right_arc", "左转弧线": "turn_left_arc",
    "右转直线": "turn_right_line", "左转直线": "turn_left_line",
    "右转移动": "turn_right_move", "左转移动": "turn_left_move",
    "前进直线": "forward", "后退直线": "backward", "倒圆角直线": "fillet",
    "获取路径d": "get_d", "原生path": "set_d", "路径点列表": "to_point_list",
    "路径长度": "length", "位置坐标": "point_at",
}

# ---------------------------------------------------------------------------
# 元素方法映射：中文元素方法 -> 英文元素方法
# ---------------------------------------------------------------------------
ELEMENT_METHOD_MAP = {
    # 中文版只有 SVG图元素（图片通道）有「颜色替换」，英文版图片 / 节点树 /
    # 模板三条路都能换色，方法同名。
    "颜色替换": "replace_color",
}

# ---------------------------------------------------------------------------
# 关键字参数映射：中文参数 -> 英文参数
# ---------------------------------------------------------------------------
KWARG_MAP = {
    "作品文件路径": "file_path", "宽": "width", "高": "height",
    "画布宽": "width", "画布高": "height",
    "半径": "radius", "横半径": "rx", "纵半径": "ry", "旋转角": "rotation",
    "宽高": "side", "起点": "start", "终点": "end", "坐标": "points",
    "填充颜色": "fill_color", "描边颜色": "stroke_color", "描边宽度": "stroke_width",
    "线宽": "stroke_width", "透明度": "opacity", "描边透明度": "stroke_opacity",
    "虚线间隔": "dasharray", "虚线偏移": "dashoffset",
    "字号": "font_size", "字体": "font", "文字": "text",
    "水平对齐": "h_align", "垂直对齐": "v_align", "加粗": "bold", "斜体": "italic",
    "行距": "line_spacing", "字间距": "letter_spacing",
    "开始角": "start_angle", "结束角": "end_angle", "内半径": "inner_radius",
    "角数": "points", "外接圆半径": "radius", "排列数量": "count", "排列间距": "gap",
    "重复数量": "count", "行数": "rows", "列数": "cols", "间隔": "gap",
    "排列角度": "arc_angle", "开始半径": "start_radius", "结束半径": "end_radius",
    "图片路径": "path", "路径d": "d", "填充规则": "fill_rule",
    "边距": "margin", "颜色数": "colors",
}

# ---------------------------------------------------------------------------
# 枚举成员映射（常用项）
# ---------------------------------------------------------------------------
ENUM_MEMBER_MAP = {
    "颜色.透明": "Color.TRANSPARENT", "颜色.无": "Color.NONE",
    "颜色.RGB": "Color.RGB", "颜色.随机色": "Color.random",
    "描边线端样式.半圆": "StrokeCap.ROUND", "描边线端样式.直角": "StrokeCap.BUTT",
    "描边线端样式.正方形": "StrokeCap.SQUARE",
    "文字水平基线对齐.中点对齐": "TextHAlign.MIDDLE",
    "文字水平基线对齐.起始点对齐": "TextHAlign.START",
    "文字水平基线对齐.结束点对齐": "TextHAlign.END",
    "是": "True", "否": "False", "开": "True", "关": "False", "空": "None",
}

# 颜色成员映射（颜色.红色 -> Color.RED）—— 由中文颜色表自动生成
_COLOR_MEMBER_MAP = {}


def _build_color_members():
    """构建「颜色.中文名」->「Color.ENGLISH」映射（内部方法）。"""
    from .definitions import Color
    for cn, (en, _hex) in Color._cn_dict.items():
        _COLOR_MEMBER_MAP[f"颜色.{cn}"] = f"Color.{en.upper()}"


_build_color_members()


def print_mapping(name):
    """
    查询中文名称对应的英文版名称。 / Look up the English name behind a Chinese one.

    :param name: 中文类名/方法名/成员名

    示例::
        import malight.compat as compat
        compat.print_mapping("画圆")      # draw_circle（MagicPen 方法）
        compat.print_mapping("颜色.红色")  # Color.RED
    """
    if name in ENUM_MEMBER_MAP:
        print(f"{name} -> {ENUM_MEMBER_MAP[name]}")
        return
    if name in _COLOR_MEMBER_MAP:
        print(f"{name} -> {_COLOR_MEMBER_MAP[name]}")
        return
    if name in CLASS_MAP:
        print(f"{name} -> {CLASS_MAP[name]}")
        return
    if name in METHOD_MAP:
        print(f"{name} -> MagicPen.{METHOD_MAP[name]}")
        return
    if name in PATH_METHOD_MAP:
        print(f"{name} -> PathElement.{PATH_METHOD_MAP[name]}")
        return
    if name in ELEMENT_METHOD_MAP:
        print(f"{name} -> {ELEMENT_METHOD_MAP[name]}"
              "（SVGImageElement / SvgNode / TemplateElement）")
        return
    print(t("compat.no_mapping", name=name))


def migrate(source, target=None):
    """
    迁移中文脚本到英文版（正则批量替换，尽力而为，结果需人工复核）。 / Migrate a script that uses Chinese names to the English API with regex rewrites: best effort, and the result needs a human review.

    :param source: 旧脚本路径
    :param target: 新脚本路径（缺省为 原名_migrated.py）

    :return: 新脚本路径

    示例（命令行）::
        python -m malight.compat 旧绘图.py 新绘图.py
    """
    if target is None:
        base, ext = source.rsplit(".", 1) if "." in source else (source, "py")
        target = f"{base}_migrated.{ext}"
    code = open(source, encoding="utf-8").read()

    # 1) 导入语句
    code = code.replace("from 神笔码靓.神笔库 import 神笔绘图板",
                        "from malight import Malight")
    # 旧版英文包名 magicpen -> malight（v2.0 起更名）
    code = code.replace("from magicpen import MagicPen",
                        "from malight import Malight")
    code = code.replace("from magicpen import", "from malight import")
    code = re.sub(r"\bimport magicpen\b", "import malight", code)
    code = code.replace("from 神笔码靓.神笔库.元素库 import *",
                        "from malight import *")
    code = code.replace("from 神笔码靓.神笔库.定义集 import *",
                        "from malight import *")
    code = code.replace("from 神笔码靓.神笔库.定义集 import 颜色, 系统字体, 纸张大小",
                        "from malight import Color, SystemFont, PaperSize")
    code = re.sub(r"from 神笔码靓[^\n]*", "from malight import *", code)

    # 2) 枚举成员（先长键后短键，避免子串误替换）
    for k in sorted(list(ENUM_MEMBER_MAP) + list(_COLOR_MEMBER_MAP),
                    key=len, reverse=True):
        code = code.replace(k, ENUM_MEMBER_MAP.get(k) or _COLOR_MEMBER_MAP.get(k))

    # 3) 类名与方法名（词边界替换）
    def _sub_word(mapping):
        """按词边界批量替换（长键优先，内部函数）。"""
        nonlocal_code = _sub_word_code
        for k in sorted(mapping, key=len, reverse=True):
            nonlocal_code[0] = re.sub(
                rf"(?<![\w\u4e00-\u9fff]){re.escape(k)}(?![\w\u4e00-\u9fff])",
                mapping[k], nonlocal_code[0])

    _sub_word_code = [code]
    _sub_word(CLASS_MAP)
    # 方法调用形式：神笔.画圆(...) / pen.写字(...) —— 中文变量名也会被换，
    # 先把常见变量名神笔/画板/画布 换成 pen
    _sub_word_code[0] = re.sub(r"(?<![\w\u4e00-\u9fff])(神笔|画板|画布|画笔)(?![\w\u4e00-\u9fff])",
                               "pen", _sub_word_code[0])
    _sub_word(METHOD_MAP)
    _sub_word(PATH_METHOD_MAP)
    _sub_word(ELEMENT_METHOD_MAP)
    # 4) 关键字参数（长键优先，如 画布宽 须先于 宽 替换）
    for k in sorted(KWARG_MAP, key=len, reverse=True):
        _sub_word_code[0] = re.sub(
            rf"(?<![\w\u4e00-\u9fff]){re.escape(k)}(\s*=)", rf"{KWARG_MAP[k]}\1",
            _sub_word_code[0])
    code = _sub_word_code[0]

    with open(target, "w", encoding="utf-8") as f:
        f.write("# 本文件由 `python -m malight.compat` 自动迁移，请人工复核\n")
        f.write(code)
    print(t("compat.migrated", target=target))
    return target


if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 3:
        migrate(sys.argv[1], sys.argv[2])
    else:
        print("用法: python -m malight.compat <旧脚本.py> [新脚本.py] / Usage: python -m malight.compat <old_script.py> [new_script.py]")
