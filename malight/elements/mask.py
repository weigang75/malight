# -*- coding: utf-8 -*-
"""
MaskElement 元素（每类一文件，含中文注释与示例）。 / MaskElement: control visibility by luminance.
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


class MaskElement(Element["MaskElement"]):
    """
    遮罩元素（<mask>，对应中文版 `遮罩元素`）：按亮度控制可见度。 / Mask element controlling visibility by luminance.

    示例::
        grad = pen.linearGradient((0, 0), (0, 1), "white", "black")
        shade = pen.rect(0, 0, 400, 300, fill_color=grad)
        m = pen.mask(shade)                 # 遮罩形状自动从画布移入 mask
        pen.rect(0, 0, 400, 300, fill_color="gold", extra={"mask": f"url(#{m.node.attribs['id']})"})
    """

    def __init__(self, board, mask_shape=None, targets=None, units=None,
                 content_units=None, id_=None, **kw):
        super().__init__(board, board.defs_node, tag="mask")
        self._update_attrs(mask_shape=mask_shape, units=units,
                           content_units=content_units, id_=id_, **kw)
        self.apply_to(targets)

    def _update_attrs(self, mask_shape=None, units=None, content_units=None, id_=None,
                      **kw):
        """写入 mask 属性并挂载遮罩形状（内部方法）。"""
        self._apply_common({"id_": id_ or Element._next_id("mask")})
        self._apply_common(kw)      # 公共样式照常落地（英文版修正：以前直接 TypeError）
        self._apply_paint(kw)       # 填充/描边会被遮罩形状继承
        self.node.set("maskUnits", units or "objectBoundingBox")
        self.node.set("maskContentUnits", content_units or "userSpaceOnUse")
        if mask_shape is not None and hasattr(mask_shape, "remove"):
            node = mask_shape.node
            mask_shape.remove()
            mask_shape.parent_node = self.node
            self.node.add(node)

    def apply_to(self, targets) -> "MaskElement":
        """把遮罩应用到目标元素。 / Apply the mask to a target element. 示例:: m.apply_to(img)"""
        if targets is None:
            return self
        if not isinstance(targets, (list, tuple)):
            targets = [targets]
        for t in targets:
            t.node.set("mask", f"url(#{self.node.attribs['id']})")
        return self

    # ------------------------------------------------------------------
    # 参数访问器（显式方法，与动态合成的 set_/get_ 等价）。 / Parameter accessors, written out explicitly; identical to the
    # 展开成真实方法是为了让 IDE 能补全、拼错能报错。 / dynamically synthesized set_/get_. Real methods so the IDE completes them and flags typos.
    # 本区块由 tools/gen_attr_accessors.py 依 _update_attrs 生成。 / Generated from the _update_attrs signature by tools/gen_attr_accessors.py.
    # 手改会被 `python tools/gen_attr_accessors.py --check` 判为不同步。 / Hand edits make that check report it as out of sync.
    # ------------------------------------------------------------------
    # >>> gen_attr_accessors: begin (generated, do not edit by hand)
    def set_mask_shape(self, value) -> "MaskElement":
        """设置 mask_shape（等价 ``update(mask_shape=value)``）。 / Set mask_shape; the same as ``update(mask_shape=value)``."""
        return self.update(mask_shape=value)

    def get_mask_shape(self) -> object:
        """读取 mask_shape 的当前属性值。 / Read the current raw mask_shape attribute."""
        return self._get_attr_value("mask_shape")

    def set_units(self, value) -> "MaskElement":
        """设置 units（等价 ``update(units=value)``）。 / Set units; the same as ``update(units=value)``."""
        return self.update(units=value)

    def get_units(self) -> object:
        """读取 units 的当前属性值。 / Read the current raw units attribute."""
        return self._get_attr_value("units")

    def set_content_units(self, value) -> "MaskElement":
        """设置 content_units（等价 ``update(content_units=value)``）。 / Set content_units; the same as ``update(content_units=value)``."""
        return self.update(content_units=value)

    def get_content_units(self) -> object:
        """读取 content_units 的当前属性值。 / Read the current raw content_units attribute."""
        return self._get_attr_value("content_units")

    def set_id_(self, value) -> "MaskElement":
        """设置 id_（等价 ``update(id_=value)``）。 / Set id_; the same as ``update(id_=value)``."""
        return self.update(id_=value)

    def get_id_(self) -> object:
        """读取 id_ 的当前属性值。 / Read the current raw id_ attribute."""
        return self._get_attr_value("id_")
    # <<< gen_attr_accessors: end

# ===========================================================================
# 使用示例
# ===========================================================================
# 在 PyCharm 里点绿色三角直接运行本文件即可；也可命令行：
#     python -m malight.elements.mask
# ===========================================================================
if __name__ == "__main__":
    import os

    from malight import Malight, ColorName

    _out = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        "..", "..", "output"))
    pen = Malight(os.path.join(_out, "demo_mask"), width=660, height=380)
    pen.set_background_color(ColorName.WHITESMOKE)

    pen.text(330, 40, "遮罩（mask）：白色显示、黑色隐藏、灰色半透明 / Masking: white shows, black hides, grey is translucent",
             font_size=16, h_align="middle", fill_color=ColorName.DIMGRAY)

    # -----------------------------------------------------------------
    # 1) 黑白渐变当遮罩 → 图片「淡出」效果（做长图渐隐最常用） / 1) A black-and-white gradient as a mask fades an image out
    # -----------------------------------------------------------------
    photo = pen.rect(40, 80, 220, 170, fill_color=ColorName.STEELBLUE)
    fade = pen.linearGradient((0, 0), (1, 0), "white", "black")
    shade = pen.rect(40, 80, 220, 170, fill_color=fade.paint())
    m = pen.mask(shade, targets=[photo])
    print("遮罩元素 id: / mask element id:", m.node.attribs.get("id"))
    pen.text(150, 270, "渐变遮罩（右淡出） / gradient mask, fading right", font_size=15, h_align="middle",
             fill_color=ColorName.NAVY)

    # -----------------------------------------------------------------
    # 2) 圆形遮罩 → 「聚光灯 / 圆形取景」效果 / 2) A circular mask gives a spotlight or round viewfinder
    # -----------------------------------------------------------------
    bg = pen.rect(300, 80, 240, 170, fill_color=ColorName.CHOCOLATE)
    spot = pen.circle(420, 165, 70, fill_color="white")
    pen.mask(spot, targets=[bg])
    pen.text(420, 270, "圆形遮罩（聚光灯） / circle mask, spotlight", font_size=15, h_align="middle",
             fill_color=ColorName.MAROON)

    # -----------------------------------------------------------------
    # 3) 遮罩自己也可以是一个组（多块形状叠加成遮罩） / 3) The mask itself can be a group of overlapping shapes
    #    白底 + 黑条纹 → 目标被「切成条纹」显示 / White plus black stripes shows the target as stripes
    # -----------------------------------------------------------------
    strip = pen.rect(60, 300, 240, 50, fill_color=ColorName.TEAL)
    bars = pen.g()
    bars.append(pen.rect(60, 300, 240, 50, fill_color="white"))
    for i in range(6):
        bars.append(pen.line((70 + i * 40, 300), (70 + i * 40, 350),
                             stroke_color="black", stroke_width=6))
    pen.mask(bars, targets=[strip])
    pen.text(180, 370, "条纹遮罩（条纹显示） / stripe mask", font_size=14, h_align="middle",
             fill_color=ColorName.CHOCOLATE)

    # -----------------------------------------------------------------
    # 4) 遮罩也能作用于组（整组一起被遮） / 4) A mask can cover a whole group
    # -----------------------------------------------------------------
    g = pen.g()
    g.append(pen.circle(450, 325, 26, fill_color=ColorName.GOLD))
    g.append(pen.circle(500, 325, 26, fill_color=ColorName.PLUM))
    curtain = pen.rect(420, 295, 110, 60, fill_color="white")
    pen.mask(curtain, targets=[g])

    pen.finish()
