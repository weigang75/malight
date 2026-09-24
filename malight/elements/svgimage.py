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

from .base import Element, _paint, _fmt_points, _fmt_transform


class SVGImageElement(Element["SVGImageElement"]):
    """
    SVG 图片元素（对应中文版 `SVG图元素`）：把另一个 SVG 文件作为图像嵌入，并且**能改它的源文本** —— 同一个文件换上不同颜色反复复用。 / SVG image element: embed another SVG file as an image whose source text can be rewritten, so one file can be recoloured and reused.

    文本读进元素后就缓存在元素上：`replace_text` / `replace_color` 改的都是
    这一份，改完自动重新内嵌，`update(width=...)` 这类局部更新不会把它冲掉。

    示例::
        icon = pen.svg_image("logo.svg", x=10, y=10, width=200)
        icon.replace_color("#ffffff", "#ff0000")   # white -> red
        print(icon.svg_colors())                   # ['#4dabf7', '#ffffff', ...]
    """

    def __init__(self, board, parent=None, svg_file="", x=0, y=0, width=None,
                 height=None, svg_text=None, **kw):
        super().__init__(board, parent, tag="image")
        self._svg_text = None        # 当前 SVG 源文本（改色改的就是这一份）
        self._svg_src_file = None    # 上次读过的文件，用来判断「换了文件」
        self._svg_uri_text = None    # 上次写进 href 的文本，避免重复编码
        self._update_attrs(svg_file=svg_file, x=x, y=y, width=width,
                           height=height, svg_text=svg_text, **kw)

    def _update_attrs(self, svg_file="", x=0, y=0, width=None, height=None,
                      svg_text=None, **kw):
        """
        写入 SVG 图属性（内部方法）。 / Write the SVG-image attributes (internal).

        文本来源二选一：``svg_file``（读文件）或 ``svg_text``（直接给源文本）。
        读到的文本会缓存到 ``self._svg_text``；之后 `replace_text` /
        `replace_color` 在这份文本上改并重新内嵌，所以 ``update(width=...)``
        这类局部更新不会把改动冲掉。 / The text is cached on the element, so
        partial updates keep whatever the recolor methods produced.
        """
        self._apply_common({"id_": kw.pop("id_", None)})
        self._apply_common(kw)
        from ..i18n import t
        from ..tools import read_svg_text, svg_intrinsic_size
        svg_file = str(svg_file or "")
        if svg_file and svg_file != self._svg_src_file:
            # 换了文件（含首次）：以文件内容为准，重读一份
            self._svg_text = read_svg_text(svg_file)
            self._svg_src_file = svg_file
        elif svg_text is not None:
            self._svg_text = str(svg_text)
        elif self._svg_text is None:
            if not svg_file:
                raise ValueError(t("err.svg_no_source"))
            self._svg_text = read_svg_text(svg_file)
            self._svg_src_file = svg_file
        self._embed_svg()
        self.node.set("x", x)
        self.node.set("y", y)
        if width is not None and height is None:
            # 只给宽：按 SVG 自身比例算高（矢量图不用 Pillow） / width only: keep the SVG's own ratio
            iw, ih = svg_intrinsic_size(self._svg_text)
            if iw and ih:
                height = float(width) * ih / iw
        self.node.set("width", width)
        self.node.set("height", height)

    # ------------------------------------------------------------------
    # SVG 源文本：读、改、换色
    # ------------------------------------------------------------------
    def _embed_svg(self):
        """把当前文本编码成 base64 data URI 写进 href（文本没变就跳过，内部方法）。"""
        if self._svg_uri_text == self._svg_text:
            return
        from ..tools import svg_text_to_data_uri
        url = svg_text_to_data_uri(self._svg_text)
        self.node.set("href", url)
        self.node.set("{http://www.w3.org/1999/xlink}href", url)
        self._svg_uri_text = self._svg_text

    def _warn_no_replace(self, old, warn=True):
        """
        一处都没替换到时给出提示（内部方法，静默无效最难查）。 / Warn when nothing matched; a silent no-op is the hardest bug to find.
        """
        if not warn:
            return
        from ..i18n import t
        from ..tools import paint
        print(paint(t("info.svg_replace_none", old=old,
                      colors=", ".join(self.svg_colors()) or "-"), "yellow"))

    def get_svg_text(self) -> str:
        """
        读取当前 SVG 源文本（换色改的就是这一份）。 / Read the current SVG source text, i.e. the text the recolor methods edit.

        示例::
            text = icon.get_svg_text()
            print(text[:40])    # <svg xmlns="http://www.w3.org/2000/svg" ...
        """
        return self._svg_text or ""

    def set_svg_text(self, text) -> "SVGImageElement":
        """
        整段替换 SVG 源文本并重新内嵌。 / Replace the whole SVG source text and re-embed it.

        :param text: 新的 SVG 源文本
        :return: self（可链式）

        示例::
            icon.set_svg_text(open("other.svg", encoding="utf-8").read())
        """
        return self.update(svg_text=str(text))

    def replace_text(self, old, new, *, count=-1,
                     warn=True) -> "SVGImageElement":
        """
        把 SVG 文本里的 old 原样替换成 new。 / Replace a raw substring inside the SVG text.

        纯字符串替换：``old`` 写什么就找什么。换颜色更推荐 `replace_color`
        —— 它认得 ``#fff`` / ``white`` / ``白色`` 这些不同写法。

        :param old: 要被替换的字符串
        :param new: 新字符串
        :param count: 最多替换几处（-1 = 全部）
        :param warn: 一处都没换到时是否打印提示（默认打印，免得改了却没生效）
        :return: self（可链式）

        示例::
            icon.replace_text("#ffffff", "#ff0000")
            icon.replace_text("<circle", "<rect", count=1)
        """
        old = str(old)
        text = self.get_svg_text()
        hits = text.count(old)
        if hits == 0:
            self._warn_no_replace(old, warn)
            return self
        return self.update(svg_text=text.replace(old, str(new), count))

    def replace_color(self, old, new, *, count=-1,
                      warn=True) -> "SVGImageElement":
        """
        把 SVG 文本里的某一种颜色换成另一种（对应中文版 `颜色替换`）。 / Swap one colour for another inside the SVG text.

        ``old`` / ``new`` 都能写颜色名（``white``、``青色``）、十六进制
        （``#fff`` / ``#ffffff``）或 ``rgb(...)``：文件里写成哪种都会被认出来，
        而 ``id="orange"`` 这类同名标识不会被误伤。

        :param old: 要换掉的颜色
        :param new: 新颜色
        :param count: 最多替换几处（-1 = 全部）
        :param warn: 一处都没换到时是否打印提示（默认打印）
        :return: self（可链式）

        示例::
            icon = pen.svg_image("icon.svg", width=120)
            icon.replace_color("#ffffff", "#ff0000")    # white -> red
            icon.replace_color("white", "#333333")      # same colour, another spelling
        """
        return self.replace_colors({old: new}, count=count, warn=warn)

    def replace_colors(self, mapping, *, count=-1,
                       warn=True) -> "SVGImageElement":
        """
        批量换色：一次改完 {旧色: 新色} 里列的所有颜色（相当于中文版 `颜色替换` 连调多次）。 / Recolour in bulk: swap every pair in the {old: new} mapping in one go.

        :param mapping: 形如 ``{"#ffffff": "#ff0000", "white": "#333333"}``
        :param count: 每对颜色最多替换几处（-1 = 全部）
        :param warn: 某个旧色一处都没换到时是否打印提示
        :return: self（可链式）

        示例::
            icon.replace_colors({"white": "#ff0000", "black": "#f5f5f5"})
        """
        from ..tools import replace_svg_color
        text = self.get_svg_text()
        for old, new in dict(mapping).items():
            text, hits = replace_svg_color(text, old, new, count)
            if hits == 0:
                self._warn_no_replace(old, warn)
        if text == self.get_svg_text():
            return self                 # 一处都没改到：别白写一遍 base64
        return self.update(svg_text=text)

    def svg_colors(self) -> list:
        """
        列出这个 SVG 用到的颜色（归一成小写 ``#rrggbb``，按首次出现顺序）。 / List the colours the SVG uses, normalised to lowercase #rrggbb in order of first appearance.

        :return: 颜色列表，如 ``['#4dabf7', '#ffd43b', '#ffffff']``

        换色前先跑一次，就知道文件里到底写的是哪种写法。 / Run it before
        recolouring to see which spellings the file actually uses.

        示例::
            print(icon.svg_colors())
        """
        from ..tools import svg_colors
        return svg_colors(self.get_svg_text())

    # ------------------------------------------------------------------
    # 参数访问器（显式方法，与动态合成的 set_/get_ 等价）。 / Parameter accessors, written out explicitly; identical to the
    # 展开成真实方法是为了让 IDE 能补全、拼错能报错。 / dynamically synthesized set_/get_. Real methods so the IDE completes them and flags typos.
    # 本区块由 tools/gen_attr_accessors.py 依 _update_attrs 生成。 / Generated from the _update_attrs signature by tools/gen_attr_accessors.py.
    # 手改会被 `python tools/gen_attr_accessors.py --check` 判为不同步。 / Hand edits make that check report it as out of sync.
    # ------------------------------------------------------------------
    # >>> gen_attr_accessors: begin (generated, do not edit by hand)
    def set_svg_file(self, value) -> "SVGImageElement":
        """设置 svg_file（等价 ``update(svg_file=value)``）。 / Set svg_file; the same as ``update(svg_file=value)``."""
        return self.update(svg_file=value)

    def get_svg_file(self) -> object:
        """读取 svg_file 的当前属性值。 / Read the current raw svg_file attribute."""
        return self._get_attr_value("svg_file")

    def set_x(self, value) -> "SVGImageElement":
        """设置 x（等价 ``update(x=value)``）。 / Set x; the same as ``update(x=value)``."""
        return self.update(x=value)

    def get_x(self) -> object:
        """读取 x 的当前属性值。 / Read the current raw x attribute."""
        return self._get_attr_value("x")

    def set_y(self, value) -> "SVGImageElement":
        """设置 y（等价 ``update(y=value)``）。 / Set y; the same as ``update(y=value)``."""
        return self.update(y=value)

    def get_y(self) -> object:
        """读取 y 的当前属性值。 / Read the current raw y attribute."""
        return self._get_attr_value("y")

    def set_width(self, value) -> "SVGImageElement":
        """设置 width（等价 ``update(width=value)``）。 / Set width; the same as ``update(width=value)``."""
        return self.update(width=value)

    def get_width(self) -> object:
        """读取 width 的当前属性值。 / Read the current raw width attribute."""
        return self._get_attr_value("width")

    def set_height(self, value) -> "SVGImageElement":
        """设置 height（等价 ``update(height=value)``）。 / Set height; the same as ``update(height=value)``."""
        return self.update(height=value)

    def get_height(self) -> object:
        """读取 height 的当前属性值。 / Read the current raw height attribute."""
        return self._get_attr_value("height")
    # <<< gen_attr_accessors: end


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
    pen.svg_image(icon_path, x=50, y=60, width=180, height=120)

    # 2) 只给宽：高按 SVG 自身比例自动算 / 2) Width only: the height follows the SVG's own ratio
    pen.svg_image(icon_path, x=300, y=60, width=180)

    # 3) 缩放 + 透明度 + 滤镜 / 3) Scale, opacity and a filter
    img = pen.svg_image(icon_path, x=60, y=210, width=140, height=90,
                        opacity=0.85, filter=pen.fx.shadow(5, 6, 6))
    print("SVG 图元素 bbox: / SVG image bbox:", tuple(round(v, 1) for v in img.bbox()))

    # 4) 局部更新：只改尺寸，位置与内嵌数据都不动 / 4) Partial update: only the size changes; position and data stay
    img.update(width=200, height=120)
    print("更新后 bbox: / bbox after update:", tuple(round(v, 1) for v in img.bbox()))

    # 5) 同一个 SVG 文件换色复用：改的是该元素自己那份文本，各改各的互不影响 / 5) Recolour one file: each element edits its own copy of the text
    badge = pen.svg_image(icon_path, x=300, y=210, width=80)
    print("文件里用到的颜色: / colours used in the file:", badge.svg_colors())
    badge.replace_color("white", "#ff6b6b")               # white -> red
    pen.svg_image(icon_path, x=400, y=210, width=80).replace_color("white", "#51cf66")
    pen.svg_image(icon_path, x=500, y=210, width=80).replace_colors({"white": "#cc5de8", "#4dabf7": "#845ef7"})
    print("换色后: / after recolouring:", badge.svg_colors())

    # 6) 想「拆开二次编辑」而不是当图片用 → import_svg_as_group / 6) To edit the contents instead, use import_svg_as_group
    #    拿到的是组元素（能变换）；换色走 tools 函数，因为换色只属于上面那条自带文本的通道 / a group element that transforms; recolour through the tools functions
    grp = pen.import_svg_as_group(icon_path, x=400, y=120, scale=0.7)
    print("导入为组后的节点数: / nodes after importing as a group:", len(list(grp.walk())))
    from malight.tools import replace_svg_node_color
    replace_svg_node_color(grp.node, "#4dabf7", "#845ef7")
    print("导入为组后 bbox: / bbox after importing as a group:",
          tuple(round(v, 1) for v in grp.bbox()))

    pen.finish()
