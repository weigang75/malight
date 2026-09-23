# -*- coding: utf-8 -*-
"""
TextElement 元素（每类一文件，含中文注释与示例）。 / TextElement, created by pen.text.
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
from ..definitions import (Color, StrokeCap, StrokeJoin, TextHAlign, TextVAlign,
                           value_of)
from .base import Element, _paint, _fmt_points, _fmt_transform, _Self


class TextElement(Element):
    """
    文字元素（对应中文版 `文字元素`）。 / Text element.

    支持字体、字号、粗体、斜体、字间距、水平/垂直对齐、逐字旋转、
    文字总宽压缩（textLength，英文版新增）。

    示例::
        pen.text(200, 100, "标题文字", font=SystemFont.KAITI,
                       font_size=36, bold=True, h_align=TextHAlign.MIDDLE,
                       letter_spacing=4)
    """

    def __init__(self, board, parent=None, x=0, y=0, text="", **kw):
        super().__init__(board, parent, tag="text")
        self._update_attrs(x=x, y=y, text=text, **kw)

    def _update_attrs(self, x=0, y=0, text="", font=None, font_size=16,
                      fill_color="black", stroke_color=None, stroke_width=None,
                      bold=False, italic=False, underline=False,
                      weight=None, decoration=None,
                      letter_spacing=None, word_spacing=None,
                      h_align=None, v_align=None, char_rotate=None,
                      text_length=None, length_adjust=None, **kw):
        """写入文字属性（内部方法）。"""
        # 注意：opacity / fill_opacity / stroke_opacity / filter / blend_mode 等
        # 公共样式参数**不要**写进本签名 —— 它们必须留在 **kw 里才能被
        # _apply_common 处理（写进签名会静默吞掉，text 的 opacity 曾因此失效）。
        # Common style params (opacity, filter, ...) must stay in **kw so that
        # _apply_common picks them up; naming them here silently drops them.
        self._apply_common({"id_": kw.pop("id_", None)})
        self._apply_common(kw)
        self._apply_paint(kw)

        def _put(name, value):
            """写属性；value 为 None 时移除它（这样 set_* 才能关掉已设样式）。"""
            if value is None:
                self.node.attribs.pop(name, None)
            else:
                self.node.set(name, value)

        self.node.set("fill", _paint(fill_color))
        _put("stroke", None if stroke_color is None else _paint(stroke_color))
        _put("stroke-width", stroke_width)
        self.node.set("x", x)
        self.node.set("y", y)
        # 字体：枚举 / 字体名 / 字体文件（文件会自动内嵌 @font-face）
        family = self._font_family(font)
        if family:
            self.node.set("font-family", family)
        self.node.set("font-size", font_size)
        # 字重：bold=True 或 weight=FontWeight.BOLD / "700"
        # （两者都关掉时移除 font-weight，否则 set_bold(False) 关不掉加粗）
        w = value_of(weight)
        _put("font-weight", w if w is not None else ("bold" if bold else None))
        _put("font-style", "italic" if italic else None)
        # 文字修饰线：underline=True 或 decoration=TextDecoration.LINE_THROUGH
        deco = value_of(decoration)
        if deco is None and underline:
            deco = "underline"
        _put("text-decoration", deco)
        _put("letter-spacing", letter_spacing)
        _put("word-spacing", word_spacing)
        _put("text-anchor", None if h_align is None else value_of(h_align))
        if v_align is None:
            self.node.attribs.pop("alignment-baseline", None)
            self.node.attribs.pop("dominant-baseline", None)
        else:
            # 同时写两种基线属性，兼容各渲染器
            self.node.set("alignment-baseline", value_of(v_align))
            self.node.set("dominant-baseline", value_of(v_align))
        _put("rotate", " ".join(fmt_num(a) for a in char_rotate)
             if isinstance(char_rotate, (list, tuple)) else char_rotate)
        _put("textLength", text_length)          # 英文版新增
        _put("lengthAdjust",
             None if length_adjust is None else value_of(length_adjust))
        self.node.text = text

    # ------------------------------------------------------------------
    # 文字参数的显式访问器（英文版新增）
    # ------------------------------------------------------------------
    # 与 __getattr__ 动态合成的 set_<参数> / get_<参数> 行为一致，写成显式
    # 方法只为了 IDE 能补全。fill_color / stroke_color / stroke_width /
    # opacity / paint_order 等公共样式在基类 Element 上，这里不重复。
    # Explicit accessors for the text parameters; they behave exactly like
    # the dynamic ones and exist so IDEs can autocomplete them.

    def set_text(self, value) -> _Self:
        """改文字内容。 / Change the text content.

        示例 / Example::
            t.set_text("新标题")
        """
        return self.update(text=value)

    def get_text(self) -> object:
        """读取当前文字内容。 / Read the current text content."""
        return self._get_attr_value("text")

    def set_font(self, font) -> _Self:
        """改字体（枚举 / 字体名 / 字体文件都行）。 / Change the font (enum, family name or font file).

        示例 / Example::
            t.set_font(Font.LISU)
        """
        return self.update(font=font)

    def get_font(self) -> object:
        """读取字体族的当前属性值。 / Read the current raw font-family attribute."""
        return self._get_attr_value("font")

    def set_font_size(self, size) -> _Self:
        """改字号。 / Change the font size.

        示例 / Example::
            t.set_font_size(36)
        """
        return self.update(font_size=size)

    def get_font_size(self) -> object:
        """读取字号的当前属性值。 / Read the current raw font-size attribute."""
        return self._get_attr_value("font_size")

    def set_bold(self, flag=True) -> _Self:
        """加粗开关。 / Turn bold on or off.

        示例 / Example::
            t.set_bold(True)
        """
        return self.update(bold=flag)

    def get_bold(self) -> object:
        """读取字重的当前属性值（如 "bold" / "700"）。 / Read the current raw font-weight attribute."""
        return self._get_attr_value("bold")

    def set_italic(self, flag=True) -> _Self:
        """斜体开关。 / Turn italic on or off.

        示例 / Example::
            t.set_italic(True)
        """
        return self.update(italic=flag)

    def get_italic(self) -> object:
        """读取字体样式的当前属性值。 / Read the current raw font-style attribute."""
        return self._get_attr_value("italic")

    def set_underline(self, flag=True) -> _Self:
        """下划线开关。 / Turn underline on or off.

        示例 / Example::
            t.set_underline(True)
        """
        return self.update(underline=flag)

    def get_underline(self) -> object:
        """读取文字修饰线的当前属性值。 / Read the current raw text-decoration attribute."""
        return self._get_attr_value("underline")

    def set_weight(self, weight) -> _Self:
        """改字重（FontWeight 枚举或 "700"）。 / Set the font weight (FontWeight enum or "700").

        示例 / Example::
            t.set_weight(FontWeight.BOLD)
        """
        return self.update(weight=weight)

    def get_weight(self) -> object:
        """读取字重的当前属性值。 / Read the current raw font-weight attribute."""
        return self._get_attr_value("weight")

    def set_decoration(self, decoration) -> _Self:
        """改文字修饰线（下划线/删除线）。 / Set the text decoration (underline / line-through).

        示例 / Example::
            t.set_decoration(TextDecoration.UNDERLINE)
        """
        return self.update(decoration=decoration)

    def get_decoration(self) -> object:
        """读取文字修饰线的当前属性值。 / Read the current raw text-decoration attribute."""
        return self._get_attr_value("decoration")

    def set_letter_spacing(self, spacing) -> _Self:
        """改字间距。 / Set the letter spacing.

        示例 / Example::
            t.set_letter_spacing(4)
        """
        return self.update(letter_spacing=spacing)

    def get_letter_spacing(self) -> object:
        """读取字间距的当前属性值。 / Read the current raw letter-spacing attribute."""
        return self._get_attr_value("letter_spacing")

    def set_word_spacing(self, spacing) -> _Self:
        """改词间距（西文排版用）。 / Set the word spacing (mostly for Latin text).

        示例 / Example::
            t.set_word_spacing(6)
        """
        return self.update(word_spacing=spacing)

    def get_word_spacing(self) -> object:
        """读取词间距的当前属性值。 / Read the current raw word-spacing attribute."""
        return self._get_attr_value("word_spacing")

    def set_h_align(self, align) -> _Self:
        """改水平对齐（TextHAlign 或 "middle"）。 / Set the horizontal alignment (TextHAlign or a string).

        示例 / Example::
            t.set_h_align(TextHAlign.MIDDLE)
        """
        return self.update(h_align=align)

    def get_h_align(self) -> object:
        """读取水平对齐的当前属性值（text-anchor）。 / Read the current raw text-anchor attribute."""
        return self._get_attr_value("h_align")

    def set_v_align(self, align) -> _Self:
        """改垂直对齐（TextVAlign 或 "middle"）。 / Set the vertical alignment (TextVAlign or a string).

        示例 / Example::
            t.set_v_align(TextVAlign.MIDDLE)
        """
        return self.update(v_align=align)

    def get_v_align(self) -> object:
        """读取垂直对齐的当前属性值。 / Read the current raw alignment-baseline attribute."""
        return self._get_attr_value("v_align")

    def set_char_rotate(self, angles) -> _Self:
        """改逐字旋转角度（角度列表）。 / Set the per-character rotation angles (a list).

        示例 / Example::
            t.set_char_rotate([-90, -90])
        """
        return self.update(char_rotate=angles)

    def get_char_rotate(self) -> object:
        """读取逐字旋转的当前属性值。 / Read the current raw rotate attribute."""
        return self._get_attr_value("char_rotate")

    def set_text_length(self, length, adjust=None) -> _Self:
        """改文字总宽压缩；给了 adjust 就一并设置调整方式。 / Set the text length; pass adjust to set lengthAdjust at the same time.

        示例 / Example::
            t.set_text_length(460, LengthAdjust.SPACING_AND_GLYPHS)
        """
        if adjust is None:
            return self.update(text_length=length)
        return self.update(text_length=length, length_adjust=adjust)

    def get_text_length(self) -> object:
        """读取文字总宽的当前属性值（textLength）。 / Read the current raw textLength attribute."""
        return self._get_attr_value("text_length")

    def set_length_adjust(self, adjust) -> _Self:
        """改宽度调整方式（配合 text_length）。 / Set lengthAdjust (pairs with text_length).

        示例 / Example::
            t.set_length_adjust(LengthAdjust.SPACING)
        """
        return self.update(length_adjust=adjust)

    def get_length_adjust(self) -> object:
        """读取宽度调整方式的当前属性值。 / Read the current raw lengthAdjust attribute."""
        return self._get_attr_value("length_adjust")

    def bbox(self) -> tuple:
        """估算包围盒（按字号 x 字数近似，精确宽度需渲染后测量）。 / Estimate the bounding box from font size times character count; exact width needs rendering. """
        x = float(self.node.attribs.get("x", 0))
        y = float(self.node.attribs.get("y", 0))
        size = float(self.node.attribs.get("font-size", 16))
        n = len(self.node.text or "")
        return (x, y - size, x + size * n, y + size * 0.3)

# ===========================================================================
# 使用示例
# ===========================================================================
# 在 PyCharm 里点绿色三角直接运行本文件即可；也可命令行：
#     python -m malight.elements.text
# ===========================================================================
if __name__ == "__main__":
    import os

    from malight import (Malight, ColorName, Font, FontWeight, TextDecoration,
                         TextHAlign, TextVAlign, LengthAdjust, PaintOrder)

    _out = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        "..", "..", "output"))
    pen = Malight(os.path.join(_out, "demo_text"), width=680, height=420)
    pen.set_background_color(ColorName.WHITESMOKE)

    # -----------------------------------------------------------------
    # 字体有三种写法，可以混用 / Three ways to name a font; mix them freely
    # -----------------------------------------------------------------
    # 1) 字体枚举（推荐：有补全、拼错立刻报错，不会静默变默认字体） / 1) Font enum: completion while typing and a loud failure on a typo
    pen.text(340, 55, "① 字体枚举 Font.SIMHEI / (1) font enum Font.SIMHEI", font=Font.SIMHEI, font_size=26,
             h_align=TextHAlign.MIDDLE, fill_color=ColorName.NAVY)

    # 2) 字体名字符串（任何已安装字体都行） / 2) Family name as a string: any installed font works
    pen.text(340, 100, "② 字体名字符串 Microsoft YaHei / (2) family name string Microsoft YaHei",
             font="Microsoft YaHei", font_size=22, h_align="middle",
             fill_color=ColorName.STEELBLUE)

    # 3) 字体文件路径（自动 base64 内嵌，换电脑也不掉字体） / 3) Font file path, base64-embedded so it survives a move
    from malight.fonts import find_font_file
    kai = find_font_file(Font.KAITI)
    if kai:
        pen.text(340, 145, "③ 字体文件内嵌（楷体） / (3) embedded font file KaiTi", font=kai, font_size=22,
                 h_align="middle", fill_color=ColorName.CHOCOLATE)
    else:
        pen.text(340, 145, "③ 未找到楷体文件，跳过 / (3) KaiTi file not found, skipping", font_size=18,
                 h_align="middle", fill_color=ColorName.DIMGRAY)

    # -----------------------------------------------------------------
    # 字重 / 斜体 / 修饰线（全部有枚举） / Weight, italic and decoration all have enums
    # -----------------------------------------------------------------
    pen.text(340, 195, "字重 W900 + 斜体 / weight W900 and italic", font=Font.ARIAL,
             weight=FontWeight.W900, italic=True, font_size=24,
             h_align="middle")
    pen.text(340, 235, "下划线 underline / underline", font_size=20, h_align="middle",
             decoration=TextDecoration.UNDERLINE, fill_color=ColorName.TEAL)
    pen.text(340, 270, "删除线 line-through / line-through", font_size=20, h_align="middle",
             decoration=TextDecoration.LINE_THROUGH,
             fill_color=ColorName.CRIMSON)

    # -----------------------------------------------------------------
    # 描边空心字 / 字间距 / 词间距 / Outlined text, letter spacing and word spacing
    # -----------------------------------------------------------------
    pen.text(190, 340, "描边空心字 / outlined text", font=Font.MS_YAHEI, font_size=42,
             fill_color="none", stroke_color=ColorName.ORANGERED,
             stroke_width=1.5, letter_spacing=8, h_align="middle")

    # word_spacing：词间距（英文排版常用） / word_spacing, usually relevant for Latin text
    pen.text(520, 340, "word spacing", font=Font.ARIAL, font_size=22,
             word_spacing=10, h_align="middle", fill_color=ColorName.INDIGO)

    # -----------------------------------------------------------------
    # 文字按指定宽度铺满（textLength）+ 垂直对齐 / Stretch text to a width with textLength, plus vertical alignment
    # -----------------------------------------------------------------
    # -----------------------------------------------------------------
    # 先描边后填充 + 创建后逐项再设置（set_* 与参数名两种写法都支持） / Stroke-first paint-order, then post-creation tweaks in both set_* and bare-name styles
    # -----------------------------------------------------------------
    word = pen.text(340, 385, "111111", font_size=20,
                    h_align="middle", v_align=TextVAlign.MIDDLE,
                    fill_color=ColorName.CHOCOLATE)
    word.set_paint_order(PaintOrder.STROKE)   # set_ 风格：链式逐项改 / set_ style
    word.set_stroke_color(ColorName.ORANGERED).set_stroke_width(3)
    # 参数名风格：无参读值、带参改值（可链式） / bare-name style: no-arg reads, one-arg sets
    word.text_length(460).length_adjust(
        LengthAdjust.SPACING_AND_GLYPHS).font_size(24)
    print("font-size =", word.font_size(),
          "| stroke =", word.stroke_color())

    # -----------------------------------------------------------------
    # 逐字旋转（做弧形/波浪标题的简易替代） / Rotate character by character: a simple stand-in for arc or wave titles
    # -----------------------------------------------------------------
    pen.text(340, 415, "逐字旋转 / per-character rotation", font_size=24, h_align="middle",
             char_rotate=[-14, -7, 0, 7, 14], fill_color=ColorName.SEAGREEN)

    # -----------------------------------------------------------------
    # 局部更新：只改字号与颜色，文字内容与位置不变 / Partial update: only size and colour change; the text and position stay
    # -----------------------------------------------------------------
    t = pen.text(40, 55, "局部更新演示 / partial update demo", font_size=16)
    t.update(font_size=20, fill_color=ColorName.CRIMSON, bold=True)
    print("文字包围盒(估算): / text bbox (estimated):", tuple(round(v, 1) for v in t.bbox()))
    print("当前 font-size: / current font-size:", t.node.attribs.get("font-size"),
          "| text:", t.node.text)

    pen.finish()
