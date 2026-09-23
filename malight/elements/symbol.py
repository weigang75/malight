# -*- coding: utf-8 -*-
"""
TemplateElement 元素（每类一文件，含中文注释与示例）。 / TemplateElement: define a reusable symbol.
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


class TemplateElement(Element):
    """
    模板元素（<symbol>，对应中文版 `元素模板`）：定义可复用的图形。 / Symbol element defining a reusable graphic.

    配合 ``pen.template(id)`` / UseElement 复用。

    示例::
        t = pen.symbol(id="star_icon", view_box="0 0 40 40")
        t.add_element(pen.polygon([(20, 2), (38, 36), (2, 36)],
                                       fill_color="gold"))
        # 使用模板
        pen.template("star_icon", x=50, y=50, width=40, height=40)
    """

    def __init__(self, board, parent=None, view_box=None, id_=None, **kw):
        # symbol 放入 defs
        super().__init__(board, board.defs_node, tag="symbol")
        self._update_attrs(view_box=view_box, id_=id_, **kw)

    def _update_attrs(self, view_box=None, id_=None, **kw):
        """写入 symbol 属性（内部方法）。"""
        self._apply_common({"id_": id_})
        self._apply_common(kw)
        self.node.set("viewBox", view_box)

    def add_element(self, el) -> _Self:
        """把元素加入模板内容。 / Add a shape to the symbol content. 示例:: t.add_element(shape)"""
        el.change_group(self)
        return self

    def append(self, el) -> _Self:
        """add_element 的别名。 / Alias of add_element. """
        return self.add_element(el)

# ===========================================================================
# 使用示例
# ===========================================================================
# 在 PyCharm 里点绿色三角直接运行本文件即可；也可命令行：
#     python -m malight.elements.symbol
# ===========================================================================
if __name__ == "__main__":
    import os

    from malight import Malight, ColorName

    _out = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        "..", "..", "output"))
    pen = Malight(os.path.join(_out, "demo_symbol"), width=620, height=380)
    pen.set_background_color(ColorName.WHITESMOKE)

    # -----------------------------------------------------------------
    # 1) 定义模板 <symbol>：只定义不显示（放在 <defs> 里） / 1) Define a <symbol> template: definitions only, kept in <defs>
    #    view_box 是模板自己的坐标系，用 <use> 复用时再缩放 / view_box is the template's own coordinate system, scaled on each <use>
    # -----------------------------------------------------------------
    star = pen.symbol(id_="star_tpl", view_box="0 0 100 100")
    star.append(pen.polygon(
        [(50, 5), (61, 38), (96, 38), (68, 59), (79, 92),
         (50, 71), (21, 92), (32, 59), (4, 38), (39, 38)],
        fill_color=ColorName.GOLD, stroke_color=ColorName.GOLDENROD))
    print("模板 id: / template id:", star.node.attribs.get("id"),
          "| viewBox:", star.node.attribs.get("viewBox"))

    # -----------------------------------------------------------------
    # 2) 用 <use> 反复复用：改模板一处，全部实例一起变，体积也小 / 2) Reuse with <use>: one template edit updates every instance
    # -----------------------------------------------------------------
    for i in range(4):
        pen.use("star_tpl", x=50 + i * 70, y=50, width=60, height=60)
    for i in range(4):
        pen.use("star_tpl", x=80 + i * 70, y=130, width=40, height=40,
                opacity=0.7)

    # -----------------------------------------------------------------
    # 3) 实例可以各自加滤镜 / 动画 / 变换，互不影响 / 3) Instances take their own filters, animation and transforms
    # -----------------------------------------------------------------
    big = pen.use("star_tpl", x=230, y=200, width=150, height=150,
                  filter=pen.fx.glow(6, ColorName.GOLD))
    big.animate_rotate(360, center=(305, 275), dur=6)

    # -----------------------------------------------------------------
    # 4) 也可以把「外部 SVG 文件」直接注册成模板复用 / 4) An external SVG file can be registered as a template too
    # -----------------------------------------------------------------
    icon = os.path.join(_out, "sample_icon.svg")
    if os.path.exists(icon):
        pen.import_svg_as_symbol(icon, id_="icon_tpl")
        pen.use("icon_tpl", x=430, y=210, width=150, height=100)

    # -----------------------------------------------------------------
    # 5) 局部更新：改模板的 viewBox（应谨慎，会改变所有实例的比例基准） / 5) Partial update: the template viewBox resets every instance's scaling
    # -----------------------------------------------------------------
    pen.symbol(id_="dot_tpl", view_box="0 0 10 10").append(
        pen.circle(5, 5, 4, fill_color=ColorName.CRIMSON))
    pen.use("dot_tpl", x=60, y=300, width=40, height=40)
    pen.use("dot_tpl", x=120, y=300, width=40, height=40, opacity=0.5)

    pen.finish()
