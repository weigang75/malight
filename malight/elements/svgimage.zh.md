<!-- 本文件由 tools/gen_docs.py 从源码自动生成，请勿手改。
     要改内容请改同目录的 svgimage.py 里的文档字符串，然后重跑生成器。 -->

# svgimage.py

**简体中文** ｜ [English](svgimage.en.md) ｜ [← 返回 README](../../README.md)

SVGImageElement 元素（每类一文件，含中文注释与示例）。

---

## 类与方法

### `SVGImageElement`

SVG 图片元素（对应中文版 `SVG图元素`）：把另一个 SVG 文件作为图像嵌入。

---

## 完整示例

在 PyCharm 里点绿色三角直接运行，或命令行：`python malight/elements/svgimage.py`

```python
if __name__ == "__main__":
    import os

    from malight import Malight, ColorName

    _out = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        "..", "..", "output"))
    os.makedirs(_out, exist_ok=True)

    # 先造一个外部 SVG 当素材（示例用；实际项目里放你自己的图）
    icon_path = os.path.join(_out, "sample_icon.svg")
    with open(icon_path, "w", encoding="utf-8") as f:
        f.write('''<svg xmlns="http://www.w3.org/2000/svg" width="120" height="80">
  <rect x="0" y="0" width="120" height="80" rx="14" fill="#4dabf7"/>
  <circle cx="42" cy="40" r="22" fill="#ffd43b"/>
  <text x="74" y="48" font-size="18" fill="#ffffff">SVG</text>
</svg>''')

    pen = Malight(os.path.join(_out, "demo_svgimage"), width=600, height=340)
    pen.set_background_color(ColorName.WHITESMOKE)

    # 1) 把 SVG 文件当图片贴上去：保持矢量，放大不糊
    #    （内部转成 data:image/svg+xml;base64 内嵌，离线可用）
    pen.paste_svg(icon_path, x=50, y=60, width=180, height=120)

    # 2) 只给位置 = 用 SVG 原始尺寸
    pen.paste_svg(icon_path, x=300, y=60)

    # 3) 缩放 + 透明度 + 滤镜
    img = pen.paste_svg(icon_path, x=80, y=220, width=140, height=90,
                        opacity=0.85, filter=pen.fx.shadow(5, 6, 6))
    print("SVG 图元素 bbox:", tuple(round(v, 1) for v in img.bbox()))

    # 4) 局部更新：只改尺寸，位置与内嵌数据不动
    img.update(width=200, height=130)
    print("更新后 bbox:", tuple(round(v, 1) for v in img.bbox()))

    # 5) 想「拆开二次编辑」而不是当图片用 → import_svg_as_group
    grp = pen.import_svg_as_group(icon_path, x=380, y=230, scale=1.2)
    print("导入为组后的子节点数:", len(grp.children))

    pen.finish()
```

---

## 同级模块

[base](base.zh.md) ｜ [circle](circle.zh.md) ｜ [clippath](clippath.zh.md) ｜ [ellipse](ellipse.zh.md) ｜ [group](group.zh.md) ｜ [image](image.zh.md) ｜ [line](line.zh.md) ｜ [link](link.zh.md) ｜ [marker](marker.zh.md) ｜ [mask](mask.zh.md) ｜ [path](path.zh.md) ｜ [pattern](pattern.zh.md) ｜ [polygon](polygon.zh.md) ｜ [polyline](polyline.zh.md) ｜ [rect](rect.zh.md) ｜ [symbol](symbol.zh.md) ｜ [text](text.zh.md) ｜ [textpath](textpath.zh.md) ｜ [use](use.zh.md)
