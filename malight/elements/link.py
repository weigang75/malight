# -*- coding: utf-8 -*-
"""
LinkElement 元素（每类一文件，含中文注释与示例）。 / LinkElement: click the element to open a URL.
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

from ..svg_backend import SvgNode
from .base import Element, _paint, _fmt_points, _fmt_transform, _Self


class LinkElement(Element):
    """
    链接元素（<a>，对应中文版 `链接元素`）：点击元素打开网页。 / Link element: clicking the element opens a URL.

    悬停提示与说明用 SVG 原生的 ``<title>`` / ``<desc>`` 子元素实现
    （浏览器打开时鼠标悬停会显示 title 文本）。

    示例::
        btn = pen.rect(50, 50, 120, 40, fill_color="steelblue")
        pen.a(btn, "https://example.com", tooltip="访问官网")
    """

    def __init__(self, board, parent=None, href="", tooltip=None, description=None, **kw):
        super().__init__(board, parent, tag="a")
        self._update_attrs(href=href, tooltip=tooltip, description=description, **kw)

    def _update_attrs(self, href="", tooltip=None, description=None, **kw):
        """写入链接属性（内部方法）。"""
        self._apply_common(kw)
        self.node.set("href", href)
        self.node.set("{http://www.w3.org/1999/xlink}href", href)
        if tooltip is not None:
            self._set_child_text("title", tooltip)
        if description is not None:
            self._set_child_text("desc", description)

    def _set_child_text(self, tag, text):
        """
        设置或更新 ``<title>`` / ``<desc>`` 子元素（内部方法）。

        SVG 的悬停提示必须是子元素，写成属性浏览器不认，所以这里单独处理。
        """
        for child in list(self.node.children):
            if child.tag == tag:
                child.text = text
                return self
        node = SvgNode(tag)
        node.text = text
        # title / desc 应排在最前面
        self.node.children.insert(0, node)
        return self

    def wrap(self, el) -> _Self:
        """
        把元素包进链接（对应中文版 `创建链接` 的主体逻辑）。 / Wrap an element in a link.

        :param el: 要包进链接的元素

        示例::
            link.wrap(shape)
        """
        if el is not None:
            el.change_group(self)
        return self

# ===========================================================================
# 使用示例
# ===========================================================================
# 在 PyCharm 里点绿色三角直接运行本文件即可；也可命令行：
#     python -m malight.elements.link
# ===========================================================================
if __name__ == "__main__":
    import os

    from malight import Malight, ColorName

    _out = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        "..", "..", "output"))
    pen = Malight(os.path.join(_out, "demo_link"), width=660, height=340)
    pen.set_background_color(ColorName.WHITESMOKE)

    pen.text(330, 40, "链接元素 <a>：点元素即可跳转（用浏览器打开 SVG 时生效） / Link element <a>: clicking it navigates, in a browser",
             font_size=16, h_align="middle", fill_color=ColorName.DIMGRAY)

    # -----------------------------------------------------------------
    # 1) 把任意元素包成链接：圆角按钮 / 1) Wrap any element in a link: a rounded button
    # -----------------------------------------------------------------
    btn = pen.rect(60, 100, 180, 70, corner_radius=14,
                   fill_color=ColorName.STEELBLUE)
    pen.text(150, 143, "点我 / Click me", font_size=22, fill_color="white",
             h_align="middle")
    link = pen.a(btn, "https://www.python.org", tooltip="打开 Python 官网 / Open the Python website",
                 description="外部链接示例 / external link demo")
    print("链接 href: / link href:", link.node.attribs.get("href"))

    # -----------------------------------------------------------------
    # 2) 文字链接（加下划线更像链接） / 2) A text link, underlined to look clickable
    # -----------------------------------------------------------------
    t = pen.text(300, 143, "点这里访问文档 / Read the docs here", font_size=20,
                 fill_color=ColorName.NAVY, underline=True)
    pen.a(t, "https://docs.python.org", tooltip="Python 文档 / Python docs")

    # -----------------------------------------------------------------
    # 3) 图片 / 图形链接；也可以跳内部锚点（如 "#top"） / 3) Image or shape links, and in-page anchors such as "#top"
    # -----------------------------------------------------------------
    icon = pen.circle(520, 135, 36, fill_color=ColorName.GOLD)
    pen.a(icon, "#top", tooltip="回到顶部 / Back to top")

    # -----------------------------------------------------------------
    # 4) 链接元素本身也能加滤镜、改透明度 / 4) A link element takes filters and opacity too
    # -----------------------------------------------------------------
    link.set_filter(pen.fx.glow(4, ColorName.SKYBLUE))

    # 5) wrap：先建链接再往里塞元素（与 pen.a(el, url) 等价） / 5) wrap: create the link, then nest elements (the same as pen.a(el, url))
    holder = pen.a(None, "https://www.example.com", tooltip="示例 / demo")
    holder.wrap(pen.text(150, 240, "另一个链接 / another link", font_size=20,
                         fill_color=ColorName.TEAL))
    print("第二个链接 href: / second link href:", holder.node.attribs.get("href"))

    # 6) 局部更新：换地址 / 换提示 / 6) Partial update: change the address or the tooltip
    holder.update(href="https://www.python.org", tooltip="换成 Python 官网 / back to the Python website")
    print("更新后 href: / href after update:", holder.node.attribs.get("href"))

    pen.finish()
