# -*- coding: utf-8 -*-
"""
ImageElement 元素（每类一文件，含中文注释与示例）。 / ImageElement: a bitmap image.
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

from ..definitions import value_of
from .base import Element, _paint, _fmt_points, _fmt_transform


class ImageElement(Element["ImageElement"]):
    """
    位图图像元素（对应中文版 `图元素`）。 / Bitmap image element.

    本地图片自动转为 base64 内嵌（离线可用）；http(s) 地址直接外链。

    示例::
        pen.image("photo.jpg", x=50, y=50, width=300)
    """

    def __init__(self, board, parent=None, href="", x=0, y=0, width=None, height=None, **kw):
        super().__init__(board, parent, tag="image")
        self._update_attrs(href=href, x=x, y=y, width=width, height=height, **kw)

    def _update_attrs(self, href="", x=0, y=0, width=None, height=None,
                      aspect=None, rendering=None, external=False, embed=None, **kw):
        """
        写入图像属性（内部方法）。

        本地图片按画板的 ``images=`` 设置决定「内嵌成 base64」（默认
        ``ImageEmbed.EMBED``）还是「只引用路径」（``ImageEmbed.LINK``）；
        http(s) 地址与 ``data:`` 一律原样引用。 / Local files are embedded as
        base64 by default; ``ImageEmbed.LINK`` references the path instead.
        """
        import os
        self._apply_common({"id_": kw.pop("id_", None)})
        self._apply_common(kw)
        from ..definitions import ImageEmbed
        from ..tools import image_to_data_uri, linked_path
        from ..i18n import t
        src = str(href)
        mode = str(embed if embed is not None else
                   getattr(self.board, "image_embed", ImageEmbed.EMBED))
        if external or src.startswith(("http", "data:")):
            url = href
        elif mode == ImageEmbed.LINK:
            url = linked_path(src, getattr(self.board, "file_path", None))
            # 每种图片只提醒一次，避免一张图贴 N 次就刷 N 行
            seen = getattr(self.board, "_linked_notes", None)
            if seen is None:
                seen = self.board._linked_notes = set()
            key = os.path.abspath(src)
            if key not in seen:
                seen.add(key)
                print(t("info.image_linked", name=os.path.basename(key)))
        else:
            url = image_to_data_uri(href)
        self.node.set("href", url)
        self.node.set("{http://www.w3.org/1999/xlink}href", url)
        self.node.set("x", x)
        self.node.set("y", y)
        self.node.set("width", width)
        self.node.set("height", height)
        if aspect:
            # 支持 AspectRatio 枚举 / 自定义串，如 "xMinYMin meet"
            self.node.set("preserveAspectRatio", value_of(aspect))
        if rendering:
            self.node.set("image-rendering", value_of(rendering))
        if width is not None and height is None:
            # 只给宽时按原图比例推算高
            from ..tools import image_size
            try:
                iw, ih = image_size(href)
                self.node.set("height", float(height or 0) or float(width) * ih / iw)
            except Exception:
                pass

    def bbox(self) -> tuple:
        """包围盒。 / Bounding box. """
        x = float(self.node.attribs.get("x", 0))
        y = float(self.node.attribs.get("y", 0))
        w = float(self.node.attribs.get("width", 0))
        h = float(self.node.attribs.get("height", 0))
        return (x, y, x + w, y + h)

    # ------------------------------------------------------------------
    # 参数访问器（显式方法，与动态合成的 set_/get_ 等价）。 / Parameter accessors, written out explicitly; identical to the
    # 展开成真实方法是为了让 IDE 能补全、拼错能报错。 / dynamically synthesized set_/get_. Real methods so the IDE completes them and flags typos.
    # 本区块由 tools/gen_attr_accessors.py 依 _update_attrs 生成。 / Generated from the _update_attrs signature by tools/gen_attr_accessors.py.
    # 手改会被 `python tools/gen_attr_accessors.py --check` 判为不同步。 / Hand edits make that check report it as out of sync.
    # ------------------------------------------------------------------
    # >>> gen_attr_accessors: begin (generated, do not edit by hand)
    def set_href(self, value) -> "ImageElement":
        """设置 href（等价 ``update(href=value)``）。 / Set href; the same as ``update(href=value)``."""
        return self.update(href=value)

    def get_href(self) -> object:
        """读取 href 的当前属性值。 / Read the current raw href attribute."""
        return self._get_attr_value("href")

    def set_x(self, value) -> "ImageElement":
        """设置 x（等价 ``update(x=value)``）。 / Set x; the same as ``update(x=value)``."""
        return self.update(x=value)

    def get_x(self) -> object:
        """读取 x 的当前属性值。 / Read the current raw x attribute."""
        return self._get_attr_value("x")

    def set_y(self, value) -> "ImageElement":
        """设置 y（等价 ``update(y=value)``）。 / Set y; the same as ``update(y=value)``."""
        return self.update(y=value)

    def get_y(self) -> object:
        """读取 y 的当前属性值。 / Read the current raw y attribute."""
        return self._get_attr_value("y")

    def set_width(self, value) -> "ImageElement":
        """设置 width（等价 ``update(width=value)``）。 / Set width; the same as ``update(width=value)``."""
        return self.update(width=value)

    def get_width(self) -> object:
        """读取 width 的当前属性值。 / Read the current raw width attribute."""
        return self._get_attr_value("width")

    def set_height(self, value) -> "ImageElement":
        """设置 height（等价 ``update(height=value)``）。 / Set height; the same as ``update(height=value)``."""
        return self.update(height=value)

    def get_height(self) -> object:
        """读取 height 的当前属性值。 / Read the current raw height attribute."""
        return self._get_attr_value("height")

    def set_aspect(self, value) -> "ImageElement":
        """设置 aspect（等价 ``update(aspect=value)``）。 / Set aspect; the same as ``update(aspect=value)``."""
        return self.update(aspect=value)

    def get_aspect(self) -> object:
        """读取 aspect 的当前属性值。 / Read the current raw aspect attribute."""
        return self._get_attr_value("aspect")

    def set_rendering(self, value) -> "ImageElement":
        """设置 rendering（等价 ``update(rendering=value)``）。 / Set rendering; the same as ``update(rendering=value)``."""
        return self.update(rendering=value)

    def get_rendering(self) -> object:
        """读取 rendering 的当前属性值。 / Read the current raw rendering attribute."""
        return self._get_attr_value("rendering")

    def set_external(self, value) -> "ImageElement":
        """设置 external（等价 ``update(external=value)``）。 / Set external; the same as ``update(external=value)``."""
        return self.update(external=value)

    def get_external(self) -> object:
        """读取 external 的当前属性值。 / Read the current raw external attribute."""
        return self._get_attr_value("external")

    def set_embed(self, value) -> "ImageElement":
        """设置 embed（等价 ``update(embed=value)``）。 / Set embed; the same as ``update(embed=value)``."""
        return self.update(embed=value)

    def get_embed(self) -> object:
        """读取 embed 的当前属性值。 / Read the current raw embed attribute."""
        return self._get_attr_value("embed")
    # <<< gen_attr_accessors: end

# ===========================================================================
# 使用示例
# ===========================================================================
# 在 PyCharm 里点绿色三角直接运行本文件即可；也可命令行：
#     python -m malight.elements.image
# ===========================================================================
if __name__ == "__main__":
    import os
    import struct
    import zlib

    from malight import Malight, ColorName, AspectRatio, ImageRendering

    _out = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        "..", "..", "output"))
    os.makedirs(_out, exist_ok=True)

    def make_png(path, w=64, h=48, rgb=(230, 57, 70)):
        """用标准库生成一张纯色 PNG（示例自备素材，避免依赖 Pillow）。 / Build a solid-colour PNG with the standard library, so the demo needs no Pillow."""
        raw = b"".join(b"\x00" + bytes(rgb) * w for _ in range(h))

        def chunk(tag, data):
            body = tag + data
            return (struct.pack(">I", len(data)) + body
                    + struct.pack(">I", zlib.crc32(body) & 0xffffffff))

        png = (b"\x89PNG\r\n\x1a\n"
               + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
               + chunk(b"IDAT", zlib.compress(raw))
               + chunk(b"IEND", b""))
        with open(path, "wb") as f:
            f.write(png)
        return path

    pen = Malight(os.path.join(_out, "demo_image"), width=660, height=400)
    pen.set_background_color(ColorName.WHITESMOKE)

    # 准备一张小图（本地图片会自动 base64 内嵌，SVG 离线也能看） / Prepare a small image; local files are base64-embedded so the SVG works offline
    img = make_png(os.path.join(_out, "sample.png"), 64, 48, (230, 57, 70))

    # 1) 只给宽度：高度按原图比例自动算（保持比例最省心） / 1) Width only: the height follows the original ratio
    i1 = pen.image(img, x=40, y=50, width=140)
    print("只给宽，自动算出的高: / width only, computed height:", i1.node.attribs.get("height"))

    # 2) 宽高都给：默认 AspectRatio.MEET（完整显示，可能留白） / 2) Both given: AspectRatio.MEET fits the whole image, possibly with padding
    pen.image(img, x=220, y=50, width=140, height=140)
    pen.text(290, 215, "MEET 完整显示 / MEET, whole image", font_size=14, fill_color=ColorName.DIMGRAY,
             h_align="middle")

    # 3) AspectRatio.SLICE：铺满裁切（不变形，会裁掉超出部分） / 3) AspectRatio.SLICE fills and crops without distorting
    pen.image(img, x=400, y=50, width=140, height=140,
              aspect=AspectRatio.SLICE)
    pen.text(470, 215, "SLICE 铺满裁切 / SLICE, filled and cropped", font_size=14,
             fill_color=ColorName.DIMGRAY, h_align="middle")

    # 4) 拉伸 + 像素化放大（做像素风 / 放大镜效果） / 4) Stretch and pixelated zoom, for retro or magnifier looks
    pen.image(img, x=40, y=260, width=200, height=60,
              aspect=AspectRatio.STRETCH,
              rendering=ImageRendering.PIXELATED, opacity=0.9)

    # 5) 外链引用：不内嵌，SVG 体积小（但看图需联网） / 5) External reference: smaller SVG, but the image needs a network
    pen.image("https://www.python.org/static/img/python-logo.png",
              x=280, y=250, width=250, height=80, external=True)

    # 6) 局部更新：只改宽高与透明度，位置和内嵌数据都不动 / 6) Partial update: only size and opacity change; position and data stay
    i2 = pen.image(img, x=560, y=260, width=60, height=60)
    i2.update(width=90, height=90, opacity=0.5)
    print("图片包围盒: / image bbox:", tuple(round(v, 1) for v in i2.bbox()))

    pen.finish()
