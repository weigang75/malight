# -*- coding: utf-8 -*-
"""
样式表 API（pen.style.add_class(...)），SVG <style>。 / The style helper (pen.style) for CSS classes, the global stylesheet and font embedding.
本文件只包含 StyleAPI 一个类。
"""
from typing import Optional
from ..svg_backend import SvgNode, fmt_num
from .. import tools
from ..i18n import t


class StyleAPI:
    """
    样式子工具（pen.style），对应中文版 `样式工具集`：
    管理 CSS 类、全局样式表与**字体文件内嵌**。 / Style helper (pen.style) managing CSS classes, the global stylesheet and font-file embedding.

    示例::
        pen.style.add_class(".title", {"font-size": "36px", "fill": "navy"})
        pen.text(100, 100, "标题", class_name="title")

        # 字体文件内嵌（一般不用手调，text(font="xxx.ttf") 会自动调用）
        family = pen.style.add_font_face(r"C:\\Windows\\Fonts\\simkai.ttf")
    """

    def __init__(self, board):
        self.board = board
        self._classes = {}
        self._font_rules = []      # @font-face 规则（英文版新增）
        self._font_faces = {}      # 字体文件 -> 族名（同一文件只内嵌一次）

    def add_class(self, class_name, styles) -> "StyleAPI":
        """
        定义 CSS 类。 / Define a CSS class.

        :param class_name: 类名（带点），如 ".title"
        :param styles: 样式字典 {"fill": "navy", ...}

        示例::
            pen.style.add_class(".red-box", {"fill": "red", "stroke": "black"})
        """
        self._classes[class_name] = styles
        return self

    def add_font_face(self, font_file, family=None) -> str:
        """
        把字体文件内嵌为 @font-face，返回可直接用于 font-family 的族名。 / Embed a font file as @font-face and return a family name usable for font-family.

        为什么要内嵌：SVG 只写字体名时，换一台没装该字体的电脑就会掉字
        （静默回退成默认字体）。内嵌后字体随 SVG 走，导出 PDF/PNG 也一致。

        同一字体文件只内嵌一次（自动去重）。

        :param font_file: 字体文件路径（.ttf/.otf/.ttc/.woff/.woff2）
        :param family: 自定义族名（默认自动生成，形如 malight-simkai）
        :return: 族名（可直接写进 font-family）

        示例::
            pen.style.add_font_face(r"C:\\Windows\\Fonts\\simhei.ttf")
            # 返回 'malight-SimHei'，之后 text(font=...) 传路径即可自动用上
        """
        import os
        from ..fonts import font_face_css
        key = os.path.abspath(font_file)
        if key in self._font_faces:
            return self._font_faces[key]
        family, css = font_face_css(font_file, family)
        self._font_rules.append(css)
        self._font_faces[key] = family
        # 提示体积：完整中文字体 base64 内嵌后约 +33%，文件会明显变大
        try:
            mb = os.path.getsize(key) / 1024.0 / 1024.0
            if mb > 2:
                print(t("info.font_embedded", name=os.path.basename(key), mb=mb))
        except OSError:
            pass
        return family

    def _css_text(self) -> str:
        """生成 CSS 文本（内部方法）：@font-face 规则在前，类规则在后。"""
        lines = list(self._font_rules)
        for name, styles in self._classes.items():
            body = "; ".join(f"{k}:{v}" for k, v in styles.items())
            lines.append(f"{name} {{ {body} }}")
        return "\n".join(lines)

    def build_style_node(self) -> "Optional[SvgNode]":
        """生成 <style> 节点（finish 时调用，内部方法）。 / Build the <style> node; called by finish() and considered internal. """
        if not self._classes and not self._font_rules:
            return None
        node = SvgNode("style", {"type": "text/css"})
        node.text = self._css_text()
        return node
