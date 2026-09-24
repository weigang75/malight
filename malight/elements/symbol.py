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

from .base import Element, _paint, _fmt_points, _fmt_transform


class TemplateElement(Element["TemplateElement"]):
    """
    模板元素（<symbol>，对应中文版 `元素模板`）：定义可复用的图形。 / Symbol element defining a reusable graphic.

    三种用法（推荐第 3 种，最省事）::

        # 1) 先建模板再塞图形
        t = pen.symbol(id="star_icon", view_box="0 0 40 40")
        t.add_element(pen.polygon(...))
        # 2) 实例化（<use> 复用，改模板一处全部实例一起变）
        pen.template("star_icon", x=50, y=50, width=40, height=40)
        # 3) 已有元素直接转模板（英文版新增），clone() 盖章
        tpl = pen.circle(50, 50, 20, fill_color="gold").to_template()
        tpl.clone(x=120)                       # 盖一个变形实例
    """

    def __init__(self, board, parent=None, view_box=None, id_=None, **kw):
        # symbol 放入 defs
        super().__init__(board, board.defs_node, tag="symbol")
        self._update_attrs(view_box=view_box, id_=id_, **kw)

    def _update_attrs(self, view_box=None, id_=None, **kw):
        """写入 symbol 属性（内部方法）。"""
        self._apply_common({"id_": id_})
        self._apply_common(kw)
        self._apply_paint(kw)   # 填充/描边会被模板内容继承（英文版修正）
        self.node.set("viewBox", view_box)

    def add_element(self, el) -> "TemplateElement":
        """把元素加入模板内容。 / Add a shape to the symbol content. 示例:: t.add_element(shape)"""
        el.change_group(self)
        return self

    def append(self, el) -> "TemplateElement":
        """add_element 的别名。 / Alias of add_element. """
        return self.add_element(el)

    def add(self, el) -> "TemplateElement":
        """add_element 的别名（对应中文版 `模板.add(图形)` 的习惯写法）。 / Alias of add_element."""
        return self.add_element(el)

    def clone(self, x=None, y=None, width=None, height=None, **kw) -> "UseElement":
        """
        盖章：用 <use> 实例化本模板并返回实例元素（英文版新增）。 / Stamp an instance of this template with <use> and return the UseElement.

        缺省位置/尺寸取 to_template() 记录的原元素包围盒 —— ``tpl.clone()``
        一个参数都不给，就在原位按原尺寸复现一个实例；也可以任意移动缩放。
        实例是普通元素，还能继续链式加滤镜/动画。 / Defaults come from the
        bounding box recorded by to_template(), so ``tpl.clone()`` reproduces
        the element exactly where it was; pass x/y/width/height to move or
        resize. The instance is a normal element and chains further.

        :param x, y: 实例左上角位置；None = 原元素位置
        :param width, height: 实例尺寸；None = 原元素尺寸
        :return: UseElement 实例（可链式 .fx_shadow() / .animate_*() 等）

        示例::
            tpl.clone()                    # 原位原尺寸一个实例
            tpl.clone(x=300, width=120)    # 移动并缩放
            tpl.clone(x=60, y=60).fx_shadow(2, 2, 3)
        """
        box = getattr(self, "_origin_bbox", None)   # to_template() 时记录 / recorded by to_template()
        if x is None:
            x = box[0] if box else 0
        if y is None:
            y = box[1] if box else 0
        if width is None and box:
            width = box[2] - box[0]
        if height is None and box:
            height = box[3] - box[1]
        tid = self.node.attribs.get("id")
        return self.board.use(tid, x=x, y=y, width=width, height=height, **kw)

    # ------------------------------------------------------------------
    # 模板内容不带换色方法
    # ------------------------------------------------------------------
    # 换色是「自带一份文本」的元素才有的本事 —— 目前只有 pen.svg_image() 返回的
    # SVG 图元素（它内嵌着自己那份 SVG 文本）。模板与组只是「节点树」，没有自己的
    # 文本，所以不挂换色方法。要给模板内容换色，用 tools 里的函数就地改属性
    # （改的是 <symbol> 内容，所有 <use> 实例会一起变）:
    #
    #     from malight.tools import replace_svg_node_color
    #     tpl = pen.import_svg_as_symbol("icon.svg", id_="icon_tpl")
    #     replace_svg_node_color(tpl.node, "white", "#ff0000")
    #     pen.use("icon_tpl", x=60, y=60, width=80)      # 实例已经是红色
    #
    # Recolouring is a capability of elements that carry their own text, i.e.
    # the SVG image element from pen.svg_image(); a template or a group is just
    # a node tree, so it has no recolour methods. Use the tools functions on
    # its node instead (every <use> instance changes with the symbol).
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # 参数访问器（显式方法，与动态合成的 set_/get_ 等价）。 / Parameter accessors, written out explicitly; identical to the
    # 展开成真实方法是为了让 IDE 能补全、拼错能报错。 / dynamically synthesized set_/get_. Real methods so the IDE completes them and flags typos.
    # 本区块由 tools/gen_attr_accessors.py 依 _update_attrs 生成。 / Generated from the _update_attrs signature by tools/gen_attr_accessors.py.
    # 手改会被 `python tools/gen_attr_accessors.py --check` 判为不同步。 / Hand edits make that check report it as out of sync.
    # ------------------------------------------------------------------
    # >>> gen_attr_accessors: begin (generated, do not edit by hand)
    def set_view_box(self, value) -> "TemplateElement":
        """设置 view_box（等价 ``update(view_box=value)``）。 / Set view_box; the same as ``update(view_box=value)``."""
        return self.update(view_box=value)

    def get_view_box(self) -> object:
        """读取 view_box 的当前属性值。 / Read the current raw view_box attribute."""
        return self._get_attr_value("view_box")

    def set_id_(self, value) -> "TemplateElement":
        """设置 id_（等价 ``update(id_=value)``）。 / Set id_; the same as ``update(id_=value)``."""
        return self.update(id_=value)

    def get_id_(self) -> object:
        """读取 id_ 的当前属性值。 / Read the current raw id_ attribute."""
        return self._get_attr_value("id_")
    # <<< gen_attr_accessors: end

# ---------------------------------------------------------------------------
# 底部导入：clone() 的返回注解引用 UseElement，而 use.py 又继承本模块的 / Bottom import: clone()'s return annotation names UseElement, which subclasses
# Element —— 顶部互相导入会循环；放到类定义之后即可。 / the Element defined in base; importing here (after the class) avoids the cycle.
# ---------------------------------------------------------------------------
from .use import UseElement  # noqa: E402

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
    #    改模板内容的颜色走 tools 函数（模板本身不挂换色方法），改一处所有 <use> 一起变 / recolour through the tools functions on its node: one edit updates every <use> instance
    # -----------------------------------------------------------------
    icon = os.path.join(_out, "sample_icon.svg")
    if os.path.exists(icon):
        from malight.tools import replace_svg_node_color, svg_node_colors

        tpl_icon = pen.import_svg_as_symbol(icon, id_="icon_tpl")
        print("模板里的颜色: / colours inside the template:",
              svg_node_colors(tpl_icon.node))
        replace_svg_node_color(tpl_icon.node, "white", "#ff0000")
        pen.use("icon_tpl", x=430, y=210, width=150, height=100)
        pen.use("icon_tpl", x=430, y=300, width=100, height=67)

    # -----------------------------------------------------------------
    # 5) 局部更新：改模板的 viewBox（应谨慎，会改变所有实例的比例基准） / 5) Partial update: the template viewBox resets every instance's scaling
    # -----------------------------------------------------------------
    pen.symbol(id_="dot_tpl", view_box="0 0 10 10").append(
        pen.circle(5, 5, 4, fill_color=ColorName.CRIMSON))
    pen.use("dot_tpl", x=60, y=300, width=40, height=40)
    pen.use("dot_tpl", x=120, y=300, width=40, height=40, opacity=0.5)

    # -----------------------------------------------------------------
    # 6) 已有元素直接转模板（to_template + clone，英文版新增） / 6) Turn an existing element into a template (to_template + clone)
    # -----------------------------------------------------------------
    dot = pen.circle(400, 320, 26, fill_color=ColorName.STEELBLUE)
    tpl = dot.to_template()              # 元素进 defs，画布上暂不显示 / into defs, not drawn yet
    tpl.clone()                          # 原位原尺寸盖一个实例 / one stamp, same place and size
    tpl.clone(x=480, width=42).fx_shadow(2, 2, 3)   # 移动缩放 + 实例自己的滤镜 / moved, scaled, own filter

    pen.finish()
