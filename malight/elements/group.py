# -*- coding: utf-8 -*-
"""
GroupElement 元素（每类一文件，含中文注释与示例）。 / GroupElement: bundle elements so they transform and animate together.
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


class GroupElement(Element["GroupElement"]):
    """
    组元素（对应中文版 `元素组`）：把多个元素打包，便于整体变换/动画。 / Group element: bundle elements so they can be transformed or animated together.

    示例::
        g = pen.g()
        c1 = pen.circle(100, 100, 40, fill_color="red")
        c2 = pen.circle(200, 100, 40, fill_color="blue")
        c1.change_group(g)
        c2.change_group(g)
        g.translate(50, 0)          # 整组平移
        g.animate_rotate(360, center=(175, 100))  # 整组旋转
    """

    def __init__(self, board, parent=None, class_name=None, style_str=None, **kw):
        super().__init__(board, parent, tag="g")
        self._update_attrs(class_name=class_name, style_str=style_str, **kw)

    def _update_attrs(self, class_name=None, style_str=None, **kw):
        """写入组属性（内部方法）。"""
        self._apply_common({"class_name": class_name, "style_str": style_str,
                            "id_": kw.pop("id_", None)})
        self._apply_common(kw)
        self._apply_paint(kw)

    def add_element(self, el) -> "GroupElement":
        """
        把元素加入本组（对应中文版 `添加元素`）。 / Add an element to this group.

        示例::
            g.add_element(pen.circle(0, 0, 10))
        """
        el.change_group(self)
        return self

    def append(self, el) -> "GroupElement":
        """add_element 的别名（对应中文版 `append`）。 / Alias of add_element. """
        return self.add_element(el)

    def remove_element(self, el) -> "GroupElement":
        """从组中移除元素（对应中文版 `移除元素`）。 / Remove an element from the group. """
        if el.parent_node is self.node:
            el.remove()
        return self

    def elements(self) -> list:
        """
        取本组内的直接子元素对象（不含孙辈），对应中文版 `元素列表`。 / Return this group's immediate children, excluding grandchildren.

        :return: [Element, ...]

        示例::
            for el in g.elements():
                print(el)
        """
        return self._child_elements()

    def all_elements(self) -> list:
        """
        取本组内**所有**后代元素对象（递归展开嵌套组）。 / Return every descendant element, recursing into nested groups.

        :return: [Element, ...]

        示例::
            for el in g.all_elements():
                print(el)
        """
        result = []
        for el in self._child_elements():
            result.append(el)
            if isinstance(el, GroupElement):
                result.extend(el.all_elements())
        return result

    def bbox(self) -> tuple:
        """
        组内所有子元素包围盒的并集 (min_x, min_y, max_x, max_y)。 / Union of the bounding boxes of all children, as (min_x, min_y, max_x, max_y).

        遍历组内所有元素（含嵌套组），各自算 bbox 后取并集；
        组内没有任何可算 bbox 的元素时返回 None。

        示例::
            x0, y0, x1, y1 = g.bbox()
        """
        boxes = []
        for el in self.all_elements():
            b = el.bbox()
            if b:
                boxes.append(b)
        if not boxes:
            return None
        return (min(b[0] for b in boxes), min(b[1] for b in boxes),
                max(b[2] for b in boxes), max(b[3] for b in boxes))

    def _child_elements(self) -> list:
        """
        收集直接挂在本组节点下的元素对象（内部方法）。

        实现要点：元素的 ``node.element`` 反向引用由 ``Element.__init__`` 写入，
        所以这里直接扫节点树即可，**无需元素有 id**，匿名元素同样能取到
        （早期版本靠 `_registry` 反查，匿名元素全部丢失，导致 bbox 恒为 None）。
        """
        result = []
        for child in self.node.children:
            el = getattr(child, "element", None)
            if el is not None:
                result.append(el)
        return result

# ===========================================================================
# 使用示例
# ===========================================================================
# 在 PyCharm 里点绿色三角直接运行本文件即可；也可命令行：
#     python -m malight.elements.group
# ===========================================================================
if __name__ == "__main__":
    import os

    from malight import Malight, ColorName

    _out = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        "..", "..", "output"))
    pen = Malight(os.path.join(_out, "demo_group"), width=620, height=380)
    pen.set_background_color(ColorName.WHITESMOKE)

    # -----------------------------------------------------------------
    # 1) 建组：把多个元素装进一个 <g>，统一变换 / 统一加特效 / 1) Put elements in one <g> for a shared transform or effect
    # -----------------------------------------------------------------
    g = pen.g(id_="row")
    for i, c in enumerate([ColorName.TOMATO, ColorName.TEAL, ColorName.GOLD,
                           ColorName.STEELBLUE]):
        el = pen.circle(110 + i * 70, 100, 26, fill_color=c)
        el.change_group(g)                      # 方式一：创建后移入组 / option A: create it, then move it into the group
    g.set_filter(pen.fx.shadow(5, 6, 6))        # 整组一起投影 / shadow applied to the whole group
    print("组内元素数: / children in group:", len(g.node.children))

    # -----------------------------------------------------------------
    # 2) 组支持嵌套组；append 与 add_element 等价 / 2) Groups nest; append and add_element are equivalent
    # -----------------------------------------------------------------
    card = pen.g(id_="card")
    card.append(pen.rect(70, 180, 190, 110, corner_radius=14,
                         fill_color=ColorName.WHITESMOKE,
                         stroke_color=ColorName.LIGHTGRAY))
    inner = pen.g()
    inner.append(pen.text(165, 225, "嵌套组 / nested group", font_size=20,
                          fill_color=ColorName.NAVY, h_align="middle"))
    inner.append(pen.text(165, 258, "统一旋转 / 统一透明 / shared rotation and opacity", font_size=13,
                          fill_color=ColorName.DIMGRAY, h_align="middle"))
    card.append(inner)                          # 组里再放组 / a group inside a group

    # -----------------------------------------------------------------
    # 3) 整组变换 + 整组透明度 / 3) Transform and opacity for the whole group
    # -----------------------------------------------------------------
    card.rotate(-8, cx=165, cy=235)
    card.update(opacity=0.95)

    # -----------------------------------------------------------------
    # 4) 组的包围盒（会遍历子元素计算） / 4) Group bounding box, computed by walking the children
    # -----------------------------------------------------------------
    print("组的 bbox: / group bbox:", tuple(round(v, 1) for v in card.bbox()))
    print("组中心: / group centre:", round(card.center_x, 1), round(card.center_y, 1))

    # -----------------------------------------------------------------
    # 5) 组内元素可以「取出」：换到画布根（传 pen.canvas_node） / 5) Take a child out by reparenting it to the canvas root (pen.canvas_node)
    # -----------------------------------------------------------------
    box = pen.rect(360, 60, 90, 90, fill_color=ColorName.KHAKI)
    tmp = pen.g()
    box.change_group(tmp)
    box.change_group(pen.canvas_node)           # 放回画布根 / back to the canvas root
    print("取出后组内元素数: / children left in the group:", len(tmp.node.children))

    # -----------------------------------------------------------------
    # 6) 从组里移除元素 / 克隆整个组 / 6) Remove a child, or clone the whole group
    # -----------------------------------------------------------------
    g2 = pen.g()
    extra = pen.circle(430, 250, 30, fill_color=ColorName.PLUM)
    g2.append(extra)
    g2.remove_element(extra)
    clone = g.clone(dx=0, dy=170, id_="row_copy")
    print("克隆组的 id: / cloned group id:", clone.node.attribs.get("id"))

    pen.finish()
