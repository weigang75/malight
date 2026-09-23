<!-- 本文件由 tools/gen_docs.py 从源码自动生成，请勿手改。
     要改内容请改同目录的 image.py 里的文档字符串，然后重跑生成器。 -->

# image.py

**简体中文** ｜ [English](image.en.md) ｜ [← 返回 README](../../README.md)

ImageElement 元素（每类一文件，含中文注释与示例）。

---

## 类与方法

### `ImageElement`

位图图像元素（对应中文版 `图元素`）。

| 方法 | 说明 |
|---|---|
| `bbox()` | 包围盒。 |

---

## 完整示例

在 PyCharm 里点绿色三角直接运行，或命令行：`python malight/elements/image.py`

```python
if __name__ == "__main__":
    import os
    import struct
    import zlib

    from malight import Malight, ColorName, AspectRatio, ImageRendering

    _out = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        "..", "..", "output"))
    os.makedirs(_out, exist_ok=True)

    def make_png(path, w=64, h=48, rgb=(230, 57, 70)):
        """用标准库生成一张纯色 PNG（示例自备素材，避免依赖 Pillow）。"""
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

    # 准备一张小图（本地图片会自动 base64 内嵌，SVG 离线也能看）
    img = make_png(os.path.join(_out, "sample.png"), 64, 48, (230, 57, 70))

    # 1) 只给宽度：高度按原图比例自动算（保持比例最省心）
    i1 = pen.image(img, x=40, y=50, width=140)
    print("只给宽，自动算出的高:", i1.node.attribs.get("height"))

    # 2) 宽高都给：默认 AspectRatio.MEET（完整显示，可能留白）
    pen.image(img, x=220, y=50, width=140, height=140)
    pen.text(290, 215, "MEET 完整显示", font_size=14, fill_color=ColorName.DIMGRAY,
             h_align="middle")

    # 3) AspectRatio.SLICE：铺满裁切（不变形，会裁掉超出部分）
    pen.image(img, x=400, y=50, width=140, height=140,
              aspect=AspectRatio.SLICE)
    pen.text(470, 215, "SLICE 铺满裁切", font_size=14,
             fill_color=ColorName.DIMGRAY, h_align="middle")

    # 4) 拉伸 + 像素化放大（做像素风 / 放大镜效果）
    pen.image(img, x=40, y=260, width=200, height=60,
              aspect=AspectRatio.STRETCH,
              rendering=ImageRendering.PIXELATED, opacity=0.9)

    # 5) 外链引用：不内嵌，SVG 体积小（但看图需联网）
    pen.image("https://www.python.org/static/img/python-logo.png",
              x=280, y=250, width=250, height=80, external=True)

    # 6) 局部更新：只改宽高与透明度，位置和内嵌数据都不动
    i2 = pen.image(img, x=560, y=260, width=60, height=60)
    i2.update(width=90, height=90, opacity=0.5)
    print("图片包围盒:", tuple(round(v, 1) for v in i2.bbox()))

    pen.finish()
```

---

## 同级模块

[base](base.zh.md) ｜ [circle](circle.zh.md) ｜ [clippath](clippath.zh.md) ｜ [ellipse](ellipse.zh.md) ｜ [group](group.zh.md) ｜ [line](line.zh.md) ｜ [link](link.zh.md) ｜ [marker](marker.zh.md) ｜ [mask](mask.zh.md) ｜ [path](path.zh.md) ｜ [pattern](pattern.zh.md) ｜ [polygon](polygon.zh.md) ｜ [polyline](polyline.zh.md) ｜ [rect](rect.zh.md) ｜ [svgimage](svgimage.zh.md) ｜ [symbol](symbol.zh.md) ｜ [text](text.zh.md) ｜ [textpath](textpath.zh.md) ｜ [use](use.zh.md)
