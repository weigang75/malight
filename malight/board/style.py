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

        # 字体文件（一般不用手调，text(font="xxx.ttf") 会自动调用）
        family = pen.style.add_font_face(r"C:\\Windows\\Fonts\\simkai.ttf")

    嵌入方式由画板决定（``pen.set_embed(fonts=...)``）：默认 ``FontEmbed.SUBSET``
    —— 到 finish() 时按画面上真正用到的字自动子集化，字体只内嵌用到的字形；
    ``FontEmbed.EMBED`` 整份内嵌；``FontEmbed.LINK`` 只引用本地字体路径。
    / The mode comes from the board (``pen.set_embed(fonts=...)``): by default the
    font is subset to the characters actually drawn at finish() time.
    """

    def __init__(self, board):
        self.board = board
        self._classes = {}
        self._font_files = {}      # 字体文件绝对路径 -> 族名（同一文件只处理一次）
        self._font_notes = []      # finish 时的字体提示（子集化节省 / 回退内嵌）

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
        登记字体文件并返回可直接用于 font-family 的族名。 / Register a font file and return a family name usable for font-family.

        为什么要内嵌：SVG 只写字体名时，换一台没装该字体的电脑就会掉字
        （静默回退成默认字体）。内嵌后字体随 SVG 走，导出 PDF/PNG 也一致。

        真正写进 SVG 的时机是 **finish()** —— 那时才知道画面上到底用了哪些字，
        默认只内嵌这些字（``FontEmbed.SUBSET``），大字体能小几百倍。
        同一字体文件只处理一次（自动去重）。

        :param font_file: 字体文件路径（.ttf/.otf/.ttc/.woff/.woff2）
        :param family: 自定义族名（默认自动生成，形如 malight-simkai）
        :return: 族名（可直接写进 font-family）

        示例::
            pen.style.add_font_face(r"C:\\Windows\\Fonts\\simhei.ttf")
            # 返回 'malight-SimHei'，之后 text(font=...) 传路径即可自动用上
        """
        import os
        from ..fonts import Font
        if not os.path.isfile(str(font_file)):
            raise FileNotFoundError(t("err.font_file_missing",
                                      path=os.path.abspath(str(font_file))))
        key = os.path.abspath(str(font_file))
        if key in self._font_files:
            return self._font_files[key]
        family_name = family or Font.family_of(key)
        self._font_files[key] = family_name
        return family_name

    def _used_chars(self, family) -> str:
        """
        收集某个族名在画面上实际用到的字符（内部方法）。 / Collect the characters actually drawn with a font family; internal.

        遍历渲染树里带 ``font-family`` 的节点（含模板 / 克隆 / 组里的文字），
        把它们的内容拼起来 —— 这就是子集化要保留的字形集合。文字后来被
        ``set_text()`` 改过也没问题，因为这一步发生在 finish() 之前的最后一刻。
        """
        chars = set()
        stack = [self.board.root_node]
        while stack:
            node = stack.pop()
            if not isinstance(node, SvgNode):
                continue
            ff = node.attribs.get("font-family")
            if ff is None:
                style = str(node.attribs.get("style") or "")
                ff = style if "font-family" in style else None
            if ff and family in str(ff) and node.text:
                chars.update(str(node.text))
            stack.extend(node.children)
        return "".join(sorted(chars))

    def _font_css(self, font_file, family) -> str:
        """
        按当前嵌入方式生成一条 @font-face（内部方法，finish 时调用）。 / Build one @font-face rule according to the current embedding mode.

        * ``FontEmbed.LINK``  —— 只写本地路径，最小；
        * ``FontEmbed.EMBED`` —— 整份字体 base64 内嵌；
        * ``FontEmbed.SUBSET``（默认）—— 按实际用字子集化后内嵌；没有 fontTools
          或子集化失败时自动退回整份内嵌（宁可变大也不能掉字）。
        """
        import os
        from ..definitions import FontEmbed
        from ..fonts import font_face_css, font_link_css, subset_font_bytes
        mode = str(getattr(self.board, "font_embed", FontEmbed.SUBSET))
        name = os.path.basename(str(font_file))
        if mode == FontEmbed.LINK:
            _, css = font_link_css(font_file, family)
            self._font_notes.append(t("info.font_linked", name=name))
            return css
        before = os.path.getsize(font_file) / 1024.0
        chars = self._used_chars(family) if mode == FontEmbed.SUBSET else ""
        if chars:
            try:
                data = subset_font_bytes(font_file, chars)
            except Exception:
                # fontTools 没装（或子集化失败）：退回整份内嵌，绝不掉字
                self._font_notes.append(t("info.font_subset_fallback", name=name))
            else:
                self._font_notes.append(t(
                    "info.font_subset_auto", name=name,
                    before="%.1f MB" % (before / 1024.0) if before > 1024
                    else "%.1f KB" % before,
                    after="%.1f KB" % (len(data) / 1024.0),
                    n=len(chars)))
                return font_face_css(font_file, family, data=data)[1]
        else:
            # 没收到用字（字体登记了但没用上，或字体写在 CSS 类里）：整份内嵌最安全
            self._font_notes.append(t("info.font_embedded", name=name,
                                      mb=before / 1024.0))
        return font_face_css(font_file, family)[1]

    def _css_text(self) -> str:
        """
        生成 CSS 文本（内部方法）：@font-face 规则在前，类规则在后。

        字体规则在这里才落地 —— finish() 顺序是「画完 → 建样式表」，所以此刻
        画面上实际用到的字已经齐了，子集化才能做到「用几个字就嵌几个字形」。
        """
        lines = [self._font_css(path, family)
                 for path, family in self._font_files.items()]
        for name, styles in self._classes.items():
            body = "; ".join(f"{k}:{v}" for k, v in styles.items())
            lines.append(f"{name} {{ {body} }}")
        return "\n".join(lines)

    def build_style_node(self) -> "Optional[SvgNode]":
        """生成 <style> 节点（finish 时调用，内部方法）。 / Build the <style> node; called by finish() and considered internal. """
        if not self._classes and not self._font_files:
            return None
        node = SvgNode("style", {"type": "text/css"})
        node.text = self._css_text()
        for note in self._font_notes:
            print(note)
        return node
