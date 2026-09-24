# -*- coding: utf-8 -*-
"""
ClipPathElement 元素（每类一文件，含中文注释与示例）。 / ClipPathElement: clip-path definitions.
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


class ClipPathElement(Element["ClipPathElement"]):
    """
    裁剪元素（<clipPath>，对应中文版 `裁剪元素`）。 / Clip-path element.

    示例::
        photo = pen.image("photo.jpg", 0, 0, width=400, height=300)
        pen.clip_circle(200, 150, 120, target=photo)   # 圆形裁剪照片
    """

    def __init__(self, board, clip_shape=None, targets=None, units=None, id_=None,
                 **kw):
        super().__init__(board, board.defs_node, tag="clipPath")
        self._update_attrs(clip_shape=clip_shape, units=units, id_=id_, **kw)
        self.apply_to(targets)

    def _update_attrs(self, clip_shape=None, units=None, id_=None, **kw):
        """写入 clipPath 属性并挂载裁剪形状（内部方法）。"""
        self._apply_common({"id_": id_ or Element._next_id("clip")})
        self._apply_common(kw)      # 公共样式照常落地（英文版修正：以前直接 TypeError）
        self._apply_paint(kw)       # 填充/描边会被裁剪形状继承
        self.node.set("clipPathUnits", units or "userSpaceOnUse")
        if clip_shape is not None:
            if hasattr(clip_shape, "remove"):
                # 裁剪形状从画布移入 defs（不在画面上显示）
                node = clip_shape.node
                clip_shape.remove()
                clip_shape.parent_node = self.node
                self.node.add(node)
            else:
                self.node.add(clip_shape)

    def apply_to(self, targets) -> "ClipPathElement":
        """
        把裁剪应用到目标元素（可为单个或列表）。 / Apply the clip to one target element or a list of them.

        示例::
            clip.apply_to([img1, img2])
        """
        if targets is None:
            return self
        if not isinstance(targets, (list, tuple)):
            targets = [targets]
        for t in targets:
            t.node.set("clip-path", f"url(#{self.node.attribs['id']})")
        return self

    # ------------------------------------------------------------------
    # 参数访问器（显式方法，与动态合成的 set_/get_ 等价）。 / Parameter accessors, written out explicitly; identical to the
    # 展开成真实方法是为了让 IDE 能补全、拼错能报错。 / dynamically synthesized set_/get_. Real methods so the IDE completes them and flags typos.
    # 本区块由 tools/gen_attr_accessors.py 依 _update_attrs 生成。 / Generated from the _update_attrs signature by tools/gen_attr_accessors.py.
    # 手改会被 `python tools/gen_attr_accessors.py --check` 判为不同步。 / Hand edits make that check report it as out of sync.
    # ------------------------------------------------------------------
    # >>> gen_attr_accessors: begin (generated, do not edit by hand)
    def set_clip_shape(self, value) -> "ClipPathElement":
        """设置 clip_shape（等价 ``update(clip_shape=value)``）。 / Set clip_shape; the same as ``update(clip_shape=value)``."""
        return self.update(clip_shape=value)

    def get_clip_shape(self) -> object:
        """读取 clip_shape 的当前属性值。 / Read the current raw clip_shape attribute."""
        return self._get_attr_value("clip_shape")

    def set_units(self, value) -> "ClipPathElement":
        """设置 units（等价 ``update(units=value)``）。 / Set units; the same as ``update(units=value)``."""
        return self.update(units=value)

    def get_units(self) -> object:
        """读取 units 的当前属性值。 / Read the current raw units attribute."""
        return self._get_attr_value("units")

    def set_id_(self, value) -> "ClipPathElement":
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
#     python -m malight.elements.clippath
# ===========================================================================
if __name__ == "__main__":
    import os

    from malight import Malight, ColorName, CoordUnits

    _out = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        "..", "..", "output"))
    pen = Malight(os.path.join(_out, "demo_clippath"), width=660, height=380)
    pen.set_background_color(ColorName.WHITESMOKE)

    pen.text(330, 40, "裁剪（clipPath）：只显示裁剪形状内部的内容 / Clipping: only what is inside the clip shape shows",
             font_size=16, h_align="middle", fill_color=ColorName.DIMGRAY)

    # -----------------------------------------------------------------
    # 1) 圆形裁剪（一步到位） / 1) A circular clip in one call
    # -----------------------------------------------------------------
    big = pen.rect(40, 70, 190, 190, fill_color=ColorName.TOMATO)
    pen.clip_circle(135, 165, 90, targets=[big])
    pen.text(135, 285, "圆形裁剪 / circle clip", font_size=15, h_align="middle",
             fill_color=ColorName.MAROON)

    # -----------------------------------------------------------------
    # 2) 矩形裁剪 / 2) A rectangular clip
    # -----------------------------------------------------------------
    box = pen.rect(270, 70, 190, 190, fill_color=ColorName.STEELBLUE)
    pen.clip_rect(310, 115, 110, 100, targets=[box])
    pen.text(365, 285, "矩形裁剪 / rect clip", font_size=15, h_align="middle",
             fill_color=ColorName.NAVY)

    # -----------------------------------------------------------------
    # 3) 任意形状裁剪：用 PathElement 当裁剪路径（异形头像 / 波浪边） / 3) Any shape: use a PathElement as the clip path, for avatars or wavy edges
    # -----------------------------------------------------------------
    wave = pen.path(fill_color="none")
    wave.move_to(500, 115)
    wave.cubic_to((520, 60), (560, 60), (580, 115))
    wave.line_to(580, 250)
    wave.line_to(500, 250)
    wave.close()
    target = pen.rect(480, 70, 130, 190, fill_color=ColorName.GOLD)
    cp = pen.clipPath(wave, targets=[target],
                      units=CoordUnits.USER_SPACE)
    print("裁剪元素 id: / clip element id:", cp.node.attribs.get("id"))
    pen.text(545, 285, "异形裁剪 / custom clip", font_size=15, h_align="middle",
             fill_color=ColorName.CHOCOLATE)

    # -----------------------------------------------------------------
    # 4) 一个裁剪区域可以作用到多个目标（做成「统一取景框」） / 4) One clip region can drive several targets, like a shared viewfinder
    # -----------------------------------------------------------------
    tile_a = pen.rect(60, 315, 120, 55, fill_color=ColorName.TEAL)
    tile_b = pen.rect(200, 315, 120, 55, fill_color=ColorName.PLUM)
    pen.clip_circle(100, 342, 30, targets=[tile_a])
    pen.clip_circle(240, 342, 30, targets=[tile_b])
    print("提示：裁剪形状本身会被移入 <defs>，不会显示在画布上 / Note: the clip shape itself moves into <defs> and is not drawn")

    pen.finish()
