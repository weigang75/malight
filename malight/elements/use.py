# -*- coding: utf-8 -*-
"""
UseElement 元素（每类一文件，含中文注释与示例）。 / UseElement: reference a symbol or an already defined shape.
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

from .base import Element, _paint, _fmt_points, _fmt_transform, _Self


class UseElement(Element):
    """
    复用元素（<use>，对应中文版 `复用元素`）：引用模板/已定义图形。 / Use element: reference a symbol or an already defined shape.

    示例::
        u = pen.template("star_icon", x=120, y=60, width=40, height=40)
        u.update(fill_color="red")   # 覆盖模板内未固定的填充色
    """

    def __init__(self, board, parent=None, href="", x=None, y=None,
                 width=None, height=None, **kw):
        super().__init__(board, parent, tag="use")
        self._update_attrs(href=href, x=x, y=y, width=width, height=height, **kw)

    def _update_attrs(self, href="", x=None, y=None, width=None, height=None, **kw):
        """写入 use 引用属性（内部方法）。"""
        self._apply_common(kw)
        self._apply_paint(kw)
        ref = href if str(href).startswith("#") else f"#{href}"
        self.node.set("href", ref)
        self.node.set("{http://www.w3.org/1999/xlink}href", ref)
        self.node.set("x", x)
        self.node.set("y", y)
        self.node.set("width", width)
        self.node.set("height", height)

# ===========================================================================
# 使用示例
# ===========================================================================
# 在 PyCharm 里点绿色三角直接运行本文件即可；也可命令行：
#     python -m malight.elements.use
# ===========================================================================
if __name__ == "__main__":
    import os

    from malight import Malight, ColorName

    _out = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        "..", "..", "output"))
    pen = Malight(os.path.join(_out, "demo_use"), width=620, height=380)
    pen.set_background_color(ColorName.WHITESMOKE)

    # 先准备一个模板（也可以来自外部 SVG，见 import_svg_as_symbol） / Prepare a template first (an external SVG works too, see import_svg_as_symbol)
    badge = pen.symbol(id_="badge", view_box="0 0 120 60")
    badge.append(pen.rect(0, 0, 120, 60, corner_radius=30,
                          fill_color=ColorName.STEELBLUE))
    badge.append(pen.text(60, 39, "NEW", font_size=26, fill_color="white",
                          h_align="middle"))

    # -----------------------------------------------------------------
    # 1) 最简复用：反复 <use> 同一个模板 / 1) Simplest reuse: <use> the same template over and over
    # -----------------------------------------------------------------
    pen.use("badge", x=40, y=40, width=150, height=75)
    pen.use("badge", x=220, y=40, width=150, height=75, opacity=0.85)
    pen.use("badge", x=400, y=40, width=150, height=75)

    # -----------------------------------------------------------------
    # 2) 只给 x / y：按模板原始尺寸放置 / 2) x / y only: drawn at the template's original size
    # -----------------------------------------------------------------
    pen.use("badge", x=60, y=150)

    # -----------------------------------------------------------------
    # 3) 每个实例可单独变换、加滤镜、改透明度 / 3) Each instance takes its own transform, filter and opacity
    # -----------------------------------------------------------------
    u = pen.use("badge", x=200, y=150, width=200, height=100,
                filter=pen.fx.shadow(6, 8, 6))
    u.update(opacity=0.95)
    u.rotate(-6, cx=300, cy=200)
    print("复用元素引用: / reused element reference:", u.node.attribs.get("href"))
    print("复用元素 bbox: / reused element bbox:", tuple(round(v, 1) for v in u.bbox()))

    # -----------------------------------------------------------------
    # 4) 多个实例可分别做动画（例如依次淡入上浮） / 4) Instances animate independently, for example fading in one after another
    # -----------------------------------------------------------------
    for i in range(3):
        item = pen.use("badge", x=70 + i * 165, y=290, width=140, height=70)
        item.animate_opacity(0, 1, dur=1.2, repeat_count=1, begin=i)
        item.animate_translate(offset=(0, -8), dur=1.2,
                               repeat_count="indefinite")

    # -----------------------------------------------------------------
    # 5) 局部更新：只改尺寸 / 透明度，引用关系不变 / 5) Partial update: only size and opacity change; the reference stays
    # -----------------------------------------------------------------
    small = pen.use("badge", x=480, y=290, width=90, height=45)
    small.update(width=120, height=60, opacity=0.6)
    print("更新后 bbox: / bbox after update:", tuple(round(v, 1) for v in small.bbox()))

    pen.finish()
