<!-- 本文件由 tools/gen_docs.py 从源码自动生成，请勿手改。
     要改内容请改同目录的 svgimage.py 里的文档字符串，然后重跑生成器。 -->

# svgimage.py

**简体中文** ｜ [English](svgimage.en.md) ｜ [← 返回 README](../../README.md)

SVGImageElement 元素（每类一文件，含中文注释与示例）。

---

## 类与方法

### `SVGImageElement`

SVG 图片元素（对应中文版 `SVG图元素`）：把另一个 SVG 文件作为图像嵌入，并且**能改它的源文本** —— 同一个文件换上不同颜色反复复用。

| 方法 | 说明 |
|---|---|
| `get_svg_text()` | 读取当前 SVG 源文本（换色改的就是这一份）。 |
| `set_svg_text(text)` | 整段替换 SVG 源文本并重新内嵌。 |
| `replace_text(old, new, *, count=…, warn=…)` | 把 SVG 文本里的 old 原样替换成 new。 |
| `replace_color(old, new, *, count=…, warn=…)` | 把 SVG 文本里的某一种颜色换成另一种（对应中文版 `颜色替换`）。 |
| `replace_colors(mapping, *, count=…, warn=…)` | 批量换色：一次改完 {旧色: 新色} 里列的所有颜色（相当于中文版 `颜色替换` 连调多次）。 |
| `svg_colors()` | 列出这个 SVG 用到的颜色（归一成小写 `#rrggbb`，按首次出现顺序）。 |
| `set_svg_file(value)` | 设置 svg_file（等价 `update(svg_file=value)`）。 |
| `get_svg_file()` | 读取 svg_file 的当前属性值。 |
| `set_x(value)` | 设置 x（等价 `update(x=value)`）。 |
| `get_x()` | 读取 x 的当前属性值。 |
| `set_y(value)` | 设置 y（等价 `update(y=value)`）。 |
| `get_y()` | 读取 y 的当前属性值。 |
| `set_width(value)` | 设置 width（等价 `update(width=value)`）。 |
| `get_width()` | 读取 width 的当前属性值。 |
| `set_height(value)` | 设置 height（等价 `update(height=value)`）。 |
| `get_height()` | 读取 height 的当前属性值。 |

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
    pen.svg_image(icon_path, x=50, y=60, width=180, height=120)

    # 2) 只给宽：高按 SVG 自身比例自动算
    pen.svg_image(icon_path, x=300, y=60, width=180)

    # 3) 缩放 + 透明度 + 滤镜
    img = pen.svg_image(icon_path, x=60, y=210, width=140, height=90,
                        opacity=0.85, filter=pen.fx.shadow(5, 6, 6))
    print("SVG 图元素 bbox:", tuple(round(v, 1) for v in img.bbox()))

    # 4) 局部更新：只改尺寸，位置与内嵌数据都不动
    img.update(width=200, height=120)
    print("更新后 bbox:", tuple(round(v, 1) for v in img.bbox()))

    # 5) 同一个 SVG 文件换色复用：改的是该元素自己那份文本，各改各的互不影响
    badge = pen.svg_image(icon_path, x=300, y=210, width=80)
    print("文件里用到的颜色:", badge.svg_colors())
    badge.replace_color("white", "#ff6b6b")               # white -> red
    pen.svg_image(icon_path, x=400, y=210, width=80).replace_color("white", "#51cf66")
    pen.svg_image(icon_path, x=500, y=210, width=80).replace_colors({"white": "#cc5de8", "#4dabf7": "#845ef7"})
    print("换色后:", badge.svg_colors())

    # 6) 想「拆开二次编辑」而不是当图片用 → import_svg_as_group
    #    拿到的是组元素（能变换）；换色走 tools 函数，因为换色只属于上面那条自带文本的通道
    grp = pen.import_svg_as_group(icon_path, x=400, y=120, scale=0.7)
    print("导入为组后的节点数:", len(list(grp.walk())))
    from malight.tools import replace_svg_node_color
    replace_svg_node_color(grp.node, "#4dabf7", "#845ef7")
    print("导入为组后 bbox:",
          tuple(round(v, 1) for v in grp.bbox()))

    pen.finish()
```

---

## 同级模块

[base](base.zh.md) ｜ [circle](circle.zh.md) ｜ [clippath](clippath.zh.md) ｜ [ellipse](ellipse.zh.md) ｜ [group](group.zh.md) ｜ [image](image.zh.md) ｜ [line](line.zh.md) ｜ [link](link.zh.md) ｜ [marker](marker.zh.md) ｜ [mask](mask.zh.md) ｜ [path](path.zh.md) ｜ [pattern](pattern.zh.md) ｜ [polygon](polygon.zh.md) ｜ [polyline](polyline.zh.md) ｜ [rect](rect.zh.md) ｜ [svggroup](svggroup.zh.md) ｜ [symbol](symbol.zh.md) ｜ [text](text.zh.md) ｜ [textpath](textpath.zh.md) ｜ [use](use.zh.md)
