# -*- coding: utf-8 -*-
"""
SvgGroupElement 元素（每类一文件，含中文注释与示例）。 / SvgGroupElement: an SVG file imported as an editable group.
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

from typing import Iterator

from ..svg_backend import SvgNode, fmt_num
from .base import _fmt_transform
from .group import GroupElement


class SvgGroupElement(GroupElement):
    """
    导入的 SVG 组元素（对应中文版 `导入SVG为组`）：整个 SVG 文件被解析成节点树装进一个 ``<g>``，所以它就是一只普通组 —— 变换 / 滤镜 / 动画 / 克隆 / 包围盒照常。 / An imported SVG group: the whole file is parsed into a node tree inside a <g>, so it behaves exactly like a normal group.

    与 `pen.g()` 造的普通组是同一家族（``isinstance(g, GroupElement)`` 为真）：
    平移 / 旋转 / 缩放 / 滤镜 / 克隆 / 动画 / `bbox()` 一应俱全，标准用法与普通
    组完全一致。 / It is the same family as a group from pen.g(): transforms,
    filters, cloning, animation and bbox all behave the same way.

    **本类不带换色方法** —— 换色是「自带一份文本」的元素才有的能力（目前只有
    `pen.svg_image()` 返回的 SVG 图元素）。这里的内容是一棵节点树，颜色写在
    节点属性上，要换色就用 tools 里的函数就地改::

        from malight.tools import replace_svg_node_color, svg_node_colors
        g = pen.import_svg_as_group("icon.svg", x=40, y=60)
        print(svg_node_colors(g.node))                  # ['#ffffff', '#4dabf7']
        replace_svg_node_color(g.node, "white", "#ff0000")

    要「同一个文件贴很多份、每份不同配色」，用 `pen.svg_image()`（每份一份独立
    文本）。 / For several differently coloured copies of one file, use
    pen.svg_image(), where every copy carries its own text.

    注意：``<style>`` 块里的 class 规则在**整个文档**里生效 —— 同一份靠 class
    上色的文件导入多份、各改各色时，后导入的规则会覆盖先导入的（CSS 的固有
    行为）；属性上色（``fill="#..."``）没有这个问题，多份导入各改各的互不影响。
    / A caution: class rules inside <style> blocks are document-global, so
    several imported copies of a class-coloured file override each other;
    attribute colours (fill="#...") do not have this problem.

    示例::
        g = pen.import_svg_as_group("icon.svg", x=40, y=60, scale=0.5)
        g.translate(10, 0)     # 组该有的能力照常 / a group behaves like a group
        print(g.bbox())        # 内容占的位置 / where the content sits
    """

    def __init__(self, board, parent=None, svg_file="", x=0, y=0, scale=None,
                 **kw):
        """
        :param board: 所属绘图板
        :param parent: 父容器（缺省挂画布根）
        :param svg_file: SVG 文件路径
        :param x: 放置位置 x
        :param y: 放置位置 y
        :param scale: 缩放倍数（缺省 1.0）
        :param kw: 其它公共样式参数（opacity / class_name / filter 等）

        内部状态要在 ``super().__init__`` 之前备好：父类构造里就会调用
        ``_update_attrs`` 去解析文件。 / The internal state must exist before
        super().__init__, because the base constructor calls _update_attrs.
        """
        self._svg_src_file = None      # 当前内容的来源文件（用来判断「换了文件」）
        self._svg_size = (0.0, 0.0)    # SVG 原始画布尺寸（bbox 用）
        self._svg_base_items = []      # 位置 + 缩放（排在变换链最后，见 _sync_transform）
        self._svg_place = (0, 0, 1.0)  # 记下 x / y / scale，供 get_x / get_y / get_scale 读回
        super().__init__(board, parent, svg_file=svg_file, x=x, y=y,
                         scale=scale, **kw)

    def _update_attrs(self, svg_file="", x=0, y=0, scale=None, **kw):
        """
        解析 SVG 文件、把节点树接管进本组的 ``<g>``（内部方法）。 / Parse the file and adopt its node tree into this group's <g> (internal).

        只在「首次」与「换了文件」时重新解析：``update(x=...)`` 这类局部更新
        只改位置变换，不会把已经改过颜色的节点树冲掉。 / Re-parsing happens
        only on first load or when the file changes, so a partial update keeps
        the recoloured tree.
        """
        self._apply_common({"class_name": kw.pop("class_name", None),
                            "style_str": kw.pop("style_str", None),
                            "id_": kw.pop("id_", None)})
        self._apply_common(kw)
        self._apply_paint(kw)

        from ..i18n import t
        src = str(svg_file or "") or (self._svg_src_file or "")
        if not src:
            raise ValueError(t("err.svg_group_no_file"))
        if src != self._svg_src_file:
            self._adopt(src)
            self._svg_src_file = src

        # 位置与缩放单独存着，由 _sync_transform 拼在变换链最后（见那里的说明）
        sx = sy = float(scale) if scale else 1.0
        self._svg_place = (x, y, sx)
        self._svg_base_items = [f"translate({fmt_num(x)},{fmt_num(y)})",
                                f"scale({fmt_num(sx)},{fmt_num(sy)})"]
        self._sync_transform()

    def _adopt(self, svg_file):
        """
        解析文件、把内容搬进本组的 ``<g>``（内部方法）。 / Parse the file and move its content into this group's <g> (internal).

        `tools.import_svg_as_nodes` 解析出的外层 ``<g>`` 只负责
        「translate + scale」定位，这里要的是内容本身：把 ``<g xmlns=...>``
        那层的命名空间属性与子树接过来，定位改由元素自己的变换机制管
        （这样之后的 ``translate()`` 还能继续叠加）。 / The wrapper <g> from
        import_svg_as_nodes only carries placement; we take the namespaced
        content and let the element's own transform handle placement.
        """
        from ..tools import import_svg_as_nodes
        node, w, h = import_svg_as_nodes(svg_file)
        inner = node.children[0] if node.children else None
        if inner is not None:
            self.node.attribs.update(inner.attribs)
            self.node.children = list(inner.children)
        self._svg_size = (float(w), float(h))

    def _sync_transform(self):
        """
        同步变换到节点（覆写基类：本组的「位置 + 缩放」排在变换链最后）。 / Sync the transform; this group appends its own placement last (override).

        SVG 的变换链从左到右累乘、**写在后面的先作用到点上**，所以把「位置 +
        缩放」放末尾，才能保证 ``x`` / ``y`` 就是画布坐标、``scale`` 就是倍率，
        而且之后调用 `translate()` 的位移不会被这个 scale 再缩一次。 / The
        list multiplies left to right with the last item acting first, so
        keeping placement last leaves x / y in canvas units and stops a later
        translate from being scaled again.
        """
        items = self._transform_items + self._svg_base_items
        self.node.set("transform", _fmt_transform(items) or None)

    # ------------------------------------------------------------------
    # 内容遍历（导入的是裸节点，没有元素对象，所以另走一条路）
    # ------------------------------------------------------------------
    def walk(self) -> "Iterator[SvgNode]":
        """
        深度优先遍历本组内含的全部 SVG 节点。 / Walk every SVG node inside this group, depth first.

        :return: 生成器，逐个产出 SvgNode

        导入的内容是「裸节点」，没有各自的元素对象，所以 `elements()` 恒为空；
        想逐个查看或改属性就用本方法。 / The imported nodes have no element
        objects, hence an empty elements(); use this to inspect them.

        示例::
            for n in g.walk():
                print(n.tag, n.attribs.get("fill"))
        """
        return self.node.walk()

    def elements(self) -> list:
        """
        本组内含的子元素对象 —— 导入的 SVG 内容是裸节点，没有元素对象，因此恒为空列表。 / Always empty: imported SVG content is bare nodes, which have no element objects.

        遍历内容请用 `walk()`（拿节点、看属性）；要动本组则直接用组的能力
        （`translate` / `set_filter` / `animate_*` 等）。 / Use walk() to
        iterate the content; use the group's own methods to transform it.

        示例::
            print(len(g.elements()))     # 0
        """
        return []

    # ------------------------------------------------------------------
    # 几何信息
    # ------------------------------------------------------------------
    def bbox(self) -> tuple:
        """
        本组内容的包围盒 (min_x, min_y, max_x, max_y)。 / Bounding box of the imported content.

        按 SVG 文件的原始画布尺寸取矩形，再过一遍本组的变换链
        （``translate`` / ``scale`` / ``rotate`` / ``skew`` / ``matrix``）。导入的
        节点没有元素对象，所以这里给的是「整份 SVG 的外框」，而不是逐个子图形
        的并集。 / The file's original canvas rectangle mapped through this
        group's transform list: imported nodes have no element objects, so this
        is the whole canvas box rather than a union of individual shapes.

        :return: (min_x, min_y, max_x, max_y)；文件没给出尺寸信息时返回 None

        示例::
            x0, y0, x1, y1 = g.bbox()
        """
        w, h = self._svg_size
        if not w or not h:
            return None
        from ..tools import svg_transform_points
        pts = svg_transform_points([(0.0, 0.0), (w, 0.0), (w, h), (0.0, h)],
                                   self._transform_items + self._svg_base_items)
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        return (min(xs), min(ys), max(xs), max(ys))

    # ------------------------------------------------------------------
    # 放置参数 / 来源文件的读取（手写，不交给生成器）
    # ------------------------------------------------------------------
    # 生成器写的 get_* 走 _get_attr_value（读节点属性），但 x / y / scale 在本类里
    # 是写进 transform 的、svg_file 也不是节点属性 —— 那样读只会得到 None。这几个
    # 值本元素自己记着，直接读回来；set_* 仍用生成器那版（走 update）。
    # 写在生成区块之外，生成器会因此不再生成这 4 个 get_*。
    # ------------------------------------------------------------------
    def get_x(self) -> object:
        """读取放置位置 x。 / Read the x this group was placed at."""
        return self._svg_place[0]

    def get_y(self) -> object:
        """读取放置位置 y。 / Read the y this group was placed at."""
        return self._svg_place[1]

    def get_scale(self) -> object:
        """读取缩放倍数。 / Read the scale factor."""
        return self._svg_place[2]

    def get_svg_file(self) -> object:
        """读取当前内容的来源文件路径。 / Read the SVG file this group was built from."""
        return self._svg_src_file

    # ------------------------------------------------------------------
    # 参数访问器（显式方法，与动态合成的 set_/get_ 等价）。 / Parameter accessors, written out explicitly; identical to the
    # 展开成真实方法是为了让 IDE 能补全、拼错能报错。 / dynamically synthesized set_/get_. Real methods so the IDE completes them and flags typos.
    # 本区块由 tools/gen_attr_accessors.py 依 _update_attrs 生成。 / Generated from the _update_attrs signature by tools/gen_attr_accessors.py.
    # 手改会被 `python tools/gen_attr_accessors.py --check` 判为不同步。 / Hand edits make that check report it as out of sync.
    # ------------------------------------------------------------------
    # >>> gen_attr_accessors: begin (generated, do not edit by hand)
    def set_svg_file(self, value) -> "SvgGroupElement":
        """设置 svg_file（等价 ``update(svg_file=value)``）。 / Set svg_file; the same as ``update(svg_file=value)``."""
        return self.update(svg_file=value)

    def set_x(self, value) -> "SvgGroupElement":
        """设置 x（等价 ``update(x=value)``）。 / Set x; the same as ``update(x=value)``."""
        return self.update(x=value)

    def set_y(self, value) -> "SvgGroupElement":
        """设置 y（等价 ``update(y=value)``）。 / Set y; the same as ``update(y=value)``."""
        return self.update(y=value)

    def set_scale(self, value) -> "SvgGroupElement":
        """设置 scale（等价 ``update(scale=value)``）。 / Set scale; the same as ``update(scale=value)``."""
        return self.update(scale=value)
    # <<< gen_attr_accessors: end


# ===========================================================================
# 使用示例
# ===========================================================================
# 在 PyCharm 里点绿色三角直接运行本文件即可；也可命令行：
#     python -m malight.elements.svggroup
# ===========================================================================
if __name__ == "__main__":
    import os

    from malight import Malight, ColorName

    _out = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        "..", "..", "output"))
    os.makedirs(_out, exist_ok=True)

    # 造一个外部 SVG 当素材（示例用；实际项目里放你自己的图） / Build an external SVG to work with: demo only, use your own file in a project
    # 用属性上色：多份导入各改各的互不影响（class 规则是文档级全局的，会互相覆盖） / attribute colours: several copies stay independent (class rules are document-global and override each other)
    badge_path = os.path.join(_out, "sample_badge.svg")
    with open(badge_path, "w", encoding="utf-8") as f:
        f.write('''<svg xmlns="http://www.w3.org/2000/svg" width="120" height="100">
  <rect x="6" y="6" width="108" height="88" rx="14" fill="#4dabf7"/>
  <circle cx="44" cy="50" r="20" fill="#ffd43b"/>
  <text x="72" y="58" font-size="18" fill="#ffffff">SVG</text>
</svg>''')

    pen = Malight(os.path.join(_out, "demo_svggroup"), width=620, height=360)
    pen.set_background_color(ColorName.WHITESMOKE)

    # -----------------------------------------------------------------
    # 1) 导入为组：拿到的是元素，用法与普通组一致 / 1) Import as a group: an element, used like any group
    #    换色走 tools 里的函数（元素上不带换色方法） / recolouring goes through the tools functions
    # -----------------------------------------------------------------
    from malight.tools import replace_svg_node_color, svg_node_colors

    g = pen.import_svg_as_group(badge_path, x=40, y=50, scale=1.2)
    print("用到的颜色: / colours used:", svg_node_colors(g.node))
    replace_svg_node_color(g.node, "white", "#ff0000")     # 属性上的白色 / a colour in an attribute
    replace_svg_node_color(g.node, "#4dabf7", "#2a9d8f")   # <style> 块里的 class 颜色 / a colour inside a <style> block
    print("换色后: / after recolouring:", svg_node_colors(g.node))

    # -----------------------------------------------------------------
    # 2) 它同时是普通组：变换 / 滤镜 / 克隆都照常 / 2) It is a normal group too: transforms, filters and clone all work
    # -----------------------------------------------------------------
    g.rotate(-8, cx=100, cy=100)
    print("组内容的包围盒: / bounding box:", tuple(round(v, 1) for v in g.bbox()))

    # -----------------------------------------------------------------
    # 3) 遍历内容节点：导入的节点没有元素对象，用 walk() / 3) Walk the nodes: imported nodes have no element objects
    # -----------------------------------------------------------------
    shapes = [n.tag for n in g.walk() if n.tag in ("rect", "circle", "text")]
    print("内容节点: / content nodes:", shapes)

    # -----------------------------------------------------------------
    # 4) 同一个文件导入两份、各自配色，互不影响 / 4) Import the same file twice, recolour each independently
    # -----------------------------------------------------------------
    g2 = pen.import_svg_as_group(badge_path, x=320, y=50, scale=1.2)
    replace_svg_node_color(g2.node, "#4dabf7", "#e76f51")
    replace_svg_node_color(g2.node, "#ffd43b", "#f4a261")
    g2.set_filter(pen.fx.shadow(4, 5, 5))

    # -----------------------------------------------------------------
    # 5) 局部更新只改位置，不会把改过的颜色冲掉 / 5) A partial update moves it without losing the recolouring
    # -----------------------------------------------------------------
    g2.update(y=200)
    print("移动后包围盒: / bbox after moving:", tuple(round(v, 1) for v in g2.bbox()))

    pen.finish()
