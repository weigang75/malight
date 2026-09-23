# -*- coding: utf-8 -*-
"""
SVGImageElement 元素（每类一文件，含中文注释与示例）。 / SVGImageElement: embed another SVG file as an image.
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


class SVGImageElement(Element):
    """
    SVG 图片元素（对应中文版 `SVG图元素`）：把另一个 SVG 文件作为图像嵌入。 / SVG image element: embed another SVG file as an image.

    示例::
        pen.paste_svg("logo.svg", x=10, y=10, width=200)
    """

    def __init__(self, board, parent=None, svg_file="", x=0, y=0, width=None, height=None, **kw):
        super().__init__(board, parent, tag="image")
        self._update_attrs(svg_file=svg_file, x=x, y=y, width=width, height=height, **kw)

    def _update_attrs(self, svg_file="", x=0, y=0, width=None, height=None, **kw):
        """SVG 文件转 base64 内嵌（内部方法）。"""
        self._apply_common({"id_": kw.pop("id_", None)})
        self._apply_common(kw)
        import base64
        with open(svg_file, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        url = f"data:image/svg+xml;base64,{data}"
        self.node.set("href", url)
        self.node.set("{http://www.w3.org/1999/xlink}href", url)
        self.node.set("x", x)
        self.node.set("y", y)
        self.node.set("width", width)
        self.node.set("height", height)


# ===========================================================================
# 容器类元素
# ===========================================================================

# ===========================================================================
# 使用示例
# ===========================================================================
# 在 PyCharm 里点绿色三角直接运行本文件即可；也可命令行：
#     python -m malight.elements.svgimage
# ===========================================================================
if __name__ == "__main__":
    import os

    from malight import Malight, ColorName

    _out = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        "..", "..", "output"))
    os.makedirs(_out, exist_ok=True)

    # 先造一个外部 SVG 当素材（示例用；实际项目里放你自己的图） / Build an external SVG to work with: demo only, use your own file in a project
    icon_path = os.path.join(_out, "sample_icon.svg")
    with open(icon_path, "w", encoding="utf-8") as f:
        f.write('''<svg xmlns="http://www.w3.org/2000/svg" width="120" height="80">
  <rect x="0" y="0" width="120" height="80" rx="14" fill="#4dabf7"/>
  <circle cx="42" cy="40" r="22" fill="#ffd43b"/>
  <text x="74" y="48" font-size="18" fill="#ffffff">SVG</text>
</svg>''')

    pen = Malight(os.path.join(_out, "demo_svgimage"), width=600, height=340)
    pen.set_background_color(ColorName.WHITESMOKE)

    # 1) 把 SVG 文件当图片贴上去：保持矢量，放大不糊 / 1) Place an SVG file as an image: still vector, sharp at any size
    #    （内部转成 data:image/svg+xml;base64 内嵌，离线可用） / embedded as data:image/svg+xml;base64, so it works offline
    pen.paste_svg(icon_path, x=50, y=60, width=180, height=120)

    # 2) 只给位置 = 用 SVG 原始尺寸 / 2) Position only: the SVG keeps its original size
    pen.paste_svg(icon_path, x=300, y=60)

    # 3) 缩放 + 透明度 + 滤镜 / 3) Scale, opacity and a filter
    img = pen.paste_svg(icon_path, x=80, y=220, width=140, height=90,
                        opacity=0.85, filter=pen.fx.shadow(5, 6, 6))
    print("SVG 图元素 bbox: / SVG image bbox:", tuple(round(v, 1) for v in img.bbox()))

    # 4) 局部更新：只改尺寸，位置与内嵌数据不动 / 4) Partial update: only the size changes; position and data stay
    img.update(width=200, height=130)
    print("更新后 bbox: / bbox after update:", tuple(round(v, 1) for v in img.bbox()))

    # 5) 想「拆开二次编辑」而不是当图片用 → import_svg_as_group / 5) To edit the contents instead, use import_svg_as_group
    grp = pen.import_svg_as_group(icon_path, x=380, y=230, scale=1.2)
    print("导入为组后的子节点数: / children after importing as a group:", len(grp.children))

    pen.finish()
