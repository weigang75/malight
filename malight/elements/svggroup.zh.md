<!-- 本文件由 tools/gen_docs.py 从源码自动生成，请勿手改。
     要改内容请改同目录的 svggroup.py 里的文档字符串，然后重跑生成器。 -->

# svggroup.py

**简体中文** ｜ [English](svggroup.en.md) ｜ [← 返回 README](../../README.md)

SvgGroupElement 元素（每类一文件，含中文注释与示例）。

---

## 类与方法

### `SvgGroupElement`

导入的 SVG 组元素（对应中文版 `导入SVG为组`）：整个 SVG 文件被解析成节点树装进一个 `<g>`，所以它就是一只普通组 —— 变换 / 滤镜 / 动画 / 克隆 / 包围盒照常。

| 方法 | 说明 |
|---|---|
| `walk()` | 深度优先遍历本组内含的全部 SVG 节点。 |
| `elements()` | 本组内含的子元素对象 —— 导入的 SVG 内容是裸节点，没有元素对象，因此恒为空列表。 |
| `bbox()` | 本组内容的包围盒 (min_x, min_y, max_x, max_y)。 |
| `get_x()` | 读取放置位置 x。 |
| `get_y()` | 读取放置位置 y。 |
| `get_scale()` | 读取缩放倍数。 |
| `get_svg_file()` | 读取当前内容的来源文件路径。 |
| `set_svg_file(value)` | 设置 svg_file（等价 `update(svg_file=value)`）。 |
| `set_x(value)` | 设置 x（等价 `update(x=value)`）。 |
| `set_y(value)` | 设置 y（等价 `update(y=value)`）。 |
| `set_scale(value)` | 设置 scale（等价 `update(scale=value)`）。 |

---

## 完整示例

在 PyCharm 里点绿色三角直接运行，或命令行：`python malight/elements/svggroup.py`

```python
if __name__ == "__main__":
    import os

    from malight import Malight, ColorName

    _out = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        "..", "..", "output"))
    os.makedirs(_out, exist_ok=True)

    # 造一个外部 SVG 当素材（示例用；实际项目里放你自己的图）
    # 用属性上色：多份导入各改各的互不影响（class 规则是文档级全局的，会互相覆盖）
    badge_path = os.path.join(_out, "sample_badge.svg")
    with open(badge_path, "w", encoding="utf-8") as f:
        f.write('''<svg xmlns="http://www.w3.org/2000/svg" width="120" height="100">
  <rect x="6" y="6" width="108" height="88" rx="14" fill="#4dabf7"/>
  <circle cx="44" cy="50" r="20" fill="#ffd43b"/>
  <text x="72" y="58" font-size="18" fill="#ffffff">SVG</text>
</svg>''')

    pen = Malight(os.path.join(_out, "demo_svggroup"), width=620, height=360)
    pen.set_background_color(ColorName.WHITESMOKE)

    # -----------------------------------------------------------------
    # 1) 导入为组：拿到的是元素，用法与普通组一致
    #    换色走 tools 里的函数（元素上不带换色方法）
    # -----------------------------------------------------------------
    from malight.tools import replace_svg_node_color, svg_node_colors

    g = pen.import_svg_as_group(badge_path, x=40, y=50, scale=1.2)
    print("用到的颜色:", svg_node_colors(g.node))
    replace_svg_node_color(g.node, "white", "#ff0000")     # 属性上的白色
    replace_svg_node_color(g.node, "#4dabf7", "#2a9d8f")   # <style> 块里的 class 颜色
    print("换色后:", svg_node_colors(g.node))

    # -----------------------------------------------------------------
    # 2) 它同时是普通组：变换 / 滤镜 / 克隆都照常
    # -----------------------------------------------------------------
    g.rotate(-8, cx=100, cy=100)
    print("组内容的包围盒:", tuple(round(v, 1) for v in g.bbox()))

    # -----------------------------------------------------------------
    # 3) 遍历内容节点：导入的节点没有元素对象，用 walk()
    # -----------------------------------------------------------------
    shapes = [n.tag for n in g.walk() if n.tag in ("rect", "circle", "text")]
    print("内容节点:", shapes)

    # -----------------------------------------------------------------
    # 4) 同一个文件导入两份、各自配色，互不影响
    # -----------------------------------------------------------------
    g2 = pen.import_svg_as_group(badge_path, x=320, y=50, scale=1.2)
    replace_svg_node_color(g2.node, "#4dabf7", "#e76f51")
    replace_svg_node_color(g2.node, "#ffd43b", "#f4a261")
    g2.set_filter(pen.fx.shadow(4, 5, 5))

    # -----------------------------------------------------------------
    # 5) 局部更新只改位置，不会把改过的颜色冲掉
    # -----------------------------------------------------------------
    g2.update(y=200)
    print("移动后包围盒:", tuple(round(v, 1) for v in g2.bbox()))

    pen.finish()
```

---

## 同级模块

[base](base.zh.md) ｜ [circle](circle.zh.md) ｜ [clippath](clippath.zh.md) ｜ [ellipse](ellipse.zh.md) ｜ [group](group.zh.md) ｜ [image](image.zh.md) ｜ [line](line.zh.md) ｜ [link](link.zh.md) ｜ [marker](marker.zh.md) ｜ [mask](mask.zh.md) ｜ [path](path.zh.md) ｜ [pattern](pattern.zh.md) ｜ [polygon](polygon.zh.md) ｜ [polyline](polyline.zh.md) ｜ [rect](rect.zh.md) ｜ [svgimage](svgimage.zh.md) ｜ [symbol](symbol.zh.md) ｜ [text](text.zh.md) ｜ [textpath](textpath.zh.md) ｜ [use](use.zh.md)
