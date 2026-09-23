# -*- coding: utf-8 -*-
"""
TextPathElement 元素（每类一文件，含中文注释与示例）。 / TextPathElement: text laid out along a path.
"""


# ---------------------------------------------------------------------------
# 直接运行引导：在 PyCharm 里点绿色三角运行本文件（或命令行 python 本文件路径）时，
# 相对导入需要包上下文，这里自动补上项目根路径与包名。
# 正常 `import malight.xxx` 时这段不会执行，对包本身零影响。
# ---------------------------------------------------------------------------
if __name__ == "__main__" and not __package__:
    import os as _os
    import sys as _sys
    _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.dirname(
        _os.path.abspath(__file__)))))
    __package__ = "malight.elements"

from ..svg_backend import SvgNode, fmt_num
from ..definitions import value_of
from .base import Element, _paint, _fmt_points, _fmt_transform, _Self
from .path import PathElement
from .text import TextElement


class TextPathElement(Element):
    """
    路径文字元素（对应中文版 `路径文字元素`）：文字沿路径排列。 / Text-path element: text laid out along a path.

    示例::
        pen.textPath([(50, 150), (150, 80), (250, 150), (350, 80)],
                         "沿曲线流动的文字", font_size=24, fill_color="purple")
    """

    def __init__(self, board, parent=None, path=None, text="", **kw):
        super().__init__(board, parent, tag="text")
        self._update_attrs(path=path, text=text, **kw)

    def _update_attrs(self, path=None, text="", start_offset="0%", font=None,
                      font_size=16, fill_color="black", stroke_color=None,
                      weight=None, decoration=None,
                      letter_spacing=None, h_align=None, **kw):
        """构建 <path> 引用与文字（内部方法）。"""
        self._apply_common({"id_": kw.pop("id_", None)})
        self._apply_common(kw)
        self._apply_paint(kw)
        self.node.set("fill", _paint(fill_color))
        if stroke_color is not None:
            self.node.set("stroke", _paint(stroke_color))
        # 字体：枚举 / 字体名 / 字体文件（文件自动内嵌 @font-face）
        family = self._font_family(font)
        if family:
            self.node.set("font-family", family)
        self.node.set("font-size", font_size)
        w = value_of(weight)
        if w is not None:
            self.node.set("font-weight", w)
        deco = value_of(decoration)
        if deco is not None:
            self.node.set("text-decoration", deco)
        if letter_spacing is not None:
            self.node.set("letter-spacing", letter_spacing)
        if h_align is not None:
            self.node.set("text-anchor", value_of(h_align))

        if isinstance(path, PathElement):
            d = path.get_d()
        elif isinstance(path, (list, tuple)):
            d = "M " + " L ".join(f"{fmt_num(x)},{fmt_num(y)}" for x, y in path)
        else:
            d = path
        # 重复调用（update）时先清空旧的 <textPath>，保证幂等
        for child in list(self.node.children):
            self.node.remove_child(child)
        # 隐藏的引导路径放 defs
        path_id = Element._next_id("textpath")
        guide = SvgNode("path", {"id": path_id, "d": d, "fill": "none"})
        self.board.defs_node.add(guide)
        tp = SvgNode("textPath", {"href": f"#{path_id}", "startOffset": start_offset})
        tp.set("{http://www.w3.org/1999/xlink}href", f"#{path_id}")
        tp.text = text
        self.node.add(tp)


# ===========================================================================
# 图像元素
# ===========================================================================

# ===========================================================================
# 使用示例
# ===========================================================================
# 在 PyCharm 里点绿色三角直接运行本文件即可；也可命令行：
#     python -m malight.elements.textpath
# ===========================================================================
if __name__ == "__main__":
    import os

    from malight import Malight, ColorName, Font, FontWeight

    _out = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        "..", "..", "output"))
    pen = Malight(os.path.join(_out, "demo_textpath"), width=660, height=380)
    pen.set_background_color(ColorName.WHITESMOKE)

    # 1) 文字沿「顶点折线」排列（最简单） / 1) Text along a polyline of points, the simplest form
    pen.textPath([(60, 100), (200, 50), (340, 100), (480, 50)],
                 "沿折线排列的文字 / text along a polyline", font=Font.SIMHEI, font_size=24,
                 fill_color=ColorName.NAVY)

    # 2) 引导线也可以直接给 PathElement（曲线更顺滑） / 2) The guide can be a PathElement, which curves more smoothly
    guide = pen.path(fill_color="none", stroke_color=ColorName.LIGHTGRAY,
                     stroke_width=1, stroke_style="4 4")
    guide.move_to(60, 210)
    guide.cubic_to((180, 110), (320, 310), (460, 210))
    pen.textPath(guide, "沿三次贝塞尔曲线流动的文字（力度顺着曲线走） / text flowing along a cubic Bezier",
                 font_size=20, fill_color=ColorName.CRIMSON,
                 weight=FontWeight.SEMI_BOLD)

    # 3) start_offset 控制文字起点（"0%" 起 / "50%" 居中） / 3) start_offset moves the text: "0%" at the start, "50%" centred
    pen.textPath([(60, 300), (600, 300)], "start_offset=50% 从中间开始写 / start_offset=50% starts in the middle",
                 start_offset="50%", font_size=19,
                 fill_color=ColorName.TEAL)

    # 4) 圆形路径上排文字（做印章 / 徽标）： / 4) Text on a circular path, for stamps and badges:
    #    先 move_to 定一个点，再 circle_to 画整圆（半径 = 两点距离） / move_to one point, then circle_to closes the circle at that radius
    ring = pen.path(fill_color="none", stroke_color=ColorName.LIGHTGRAY,
                    stroke_width=1)
    ring.move_to(330, 260)
    ring.circle_to((330, 330))
    pen.textPath(ring, "· 沿圆环排列的文字 · / · text around a circle ·", font_size=16,
                 fill_color=ColorName.INDIGO)
    print("提示：引导路径自动放进 <defs>，本身不会显示在画布上 / Note: the guide path moves into <defs> and is not drawn")

    # 5) 局部更新：只改字号/字距，文字与引导线都保留 / 5) Partial update: only size and spacing change; text and guide stay
    tp = pen.textPath([(60, 360), (600, 360)], "局部更新演示 / partial update demo", font_size=16)
    tp.update(font_size=22, letter_spacing=6, fill_color=ColorName.SEAGREEN)
    # 也可换文字或换路径（会自动重建内部引用，不会累积节点） / You can also swap the text or the path: internal references are rebuilt
    tp.update(text="换一段文字 / replacement text")
    tp.update(path=[(60, 360), (330, 345), (600, 360)])
    print("textPath 子节点数: / textPath children:", len(tp.node.children),
          "| 文字: / | text:", tp.node.children[0].text if tp.node.children else None)

    pen.finish()
