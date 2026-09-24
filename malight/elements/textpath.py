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
from .base import Element, _paint, _fmt_points, _fmt_transform
from .path import PathElement
from .text import TextElement


class TextPathElement(Element["TextPathElement"]):
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

    # ------------------------------------------------------------------
    # 这三个参数的当前值在内部子节点 <textPath> 与 defs 里的引导路径上，
    # 不在本元素节点上 —— 所以覆写读取器（生成器见本类已有同名方法会自动让位）。
    # text / path / start_offset read back from the inner <textPath> child and the
    # guide path in defs, not from this element's own node, so their getters are
    # overridden here; the generator backs off once it sees them in the class body.
    # ------------------------------------------------------------------
    def _textpath_node(self):
        """取内部 <textPath> 子节点（内部方法）；没有则 None。"""
        for child in self.node.children:
            if child.tag == "textPath":
                return child
        return None

    def get_text(self) -> object:
        """读取当前文字内容（存在内部 <textPath> 上）。 / Read the current text content, which lives on the inner <textPath>."""
        node = self._textpath_node()
        return None if node is None else node.text

    def get_start_offset(self) -> object:
        """读取 startOffset（默认 ``"0%"``）。 / Read the startOffset value (``"0%"`` by default)."""
        node = self._textpath_node()
        return None if node is None else node.attribs.get("startOffset")

    def get_path(self) -> object:
        """读取引导路径的 ``d`` 字符串（引导路径藏在 defs 里，由 id 引用）。 / Read the guide path's ``d`` string; the guide lives in defs and is referenced by id."""
        node = self._textpath_node()
        if node is None:
            return None
        ref = str(node.attribs.get("href", "")).lstrip("#")
        for guide in self.board.defs_node.children:
            if guide.attribs.get("id") == ref:
                return guide.attribs.get("d")
        return None

    # ------------------------------------------------------------------
    # 参数访问器（显式方法，与动态合成的 set_/get_ 等价）。 / Parameter accessors, written out explicitly; identical to the
    # 展开成真实方法是为了让 IDE 能补全、拼错能报错。 / dynamically synthesized set_/get_. Real methods so the IDE completes them and flags typos.
    # 本区块由 tools/gen_attr_accessors.py 依 _update_attrs 生成。 / Generated from the _update_attrs signature by tools/gen_attr_accessors.py.
    # 手改会被 `python tools/gen_attr_accessors.py --check` 判为不同步。 / Hand edits make that check report it as out of sync.
    # ------------------------------------------------------------------
    # >>> gen_attr_accessors: begin (generated, do not edit by hand)
    def set_path(self, value) -> "TextPathElement":
        """设置 path（等价 ``update(path=value)``）。 / Set path; the same as ``update(path=value)``."""
        return self.update(path=value)

    def set_text(self, value) -> "TextPathElement":
        """设置 text（等价 ``update(text=value)``）。 / Set text; the same as ``update(text=value)``."""
        return self.update(text=value)

    def set_start_offset(self, value) -> "TextPathElement":
        """设置 start_offset（等价 ``update(start_offset=value)``）。 / Set start_offset; the same as ``update(start_offset=value)``."""
        return self.update(start_offset=value)

    def set_font(self, value) -> "TextPathElement":
        """设置 font（等价 ``update(font=value)``）。 / Set font; the same as ``update(font=value)``."""
        return self.update(font=value)

    def get_font(self) -> object:
        """读取 font 的当前属性值。 / Read the current raw font attribute."""
        return self._get_attr_value("font")

    def set_font_size(self, value) -> "TextPathElement":
        """设置 font_size（等价 ``update(font_size=value)``）。 / Set font_size; the same as ``update(font_size=value)``."""
        return self.update(font_size=value)

    def get_font_size(self) -> object:
        """读取 font_size 的当前属性值。 / Read the current raw font_size attribute."""
        return self._get_attr_value("font_size")

    def set_weight(self, value) -> "TextPathElement":
        """设置 weight（等价 ``update(weight=value)``）。 / Set weight; the same as ``update(weight=value)``."""
        return self.update(weight=value)

    def get_weight(self) -> object:
        """读取 weight 的当前属性值。 / Read the current raw weight attribute."""
        return self._get_attr_value("weight")

    def set_decoration(self, value) -> "TextPathElement":
        """设置 decoration（等价 ``update(decoration=value)``）。 / Set decoration; the same as ``update(decoration=value)``."""
        return self.update(decoration=value)

    def get_decoration(self) -> object:
        """读取 decoration 的当前属性值。 / Read the current raw decoration attribute."""
        return self._get_attr_value("decoration")

    def set_letter_spacing(self, value) -> "TextPathElement":
        """设置 letter_spacing（等价 ``update(letter_spacing=value)``）。 / Set letter_spacing; the same as ``update(letter_spacing=value)``."""
        return self.update(letter_spacing=value)

    def get_letter_spacing(self) -> object:
        """读取 letter_spacing 的当前属性值。 / Read the current raw letter_spacing attribute."""
        return self._get_attr_value("letter_spacing")

    def set_h_align(self, value) -> "TextPathElement":
        """设置 h_align（等价 ``update(h_align=value)``）。 / Set h_align; the same as ``update(h_align=value)``."""
        return self.update(h_align=value)

    def get_h_align(self) -> object:
        """读取 h_align 的当前属性值。 / Read the current raw h_align attribute."""
        return self._get_attr_value("h_align")
    # <<< gen_attr_accessors: end


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
