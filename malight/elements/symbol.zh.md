<!-- 本文件由 tools/gen_docs.py 从源码自动生成，请勿手改。
     要改内容请改同目录的 symbol.py 里的文档字符串，然后重跑生成器。 -->

# symbol.py

**简体中文** ｜ [English](symbol.en.md) ｜ [← 返回 README](../../README.md)

TemplateElement 元素（每类一文件，含中文注释与示例）。

---

## 类与方法

### `TemplateElement`

模板元素（`<symbol>`，对应中文版 `元素模板`）：定义可复用的图形。

| 方法 | 说明 |
|---|---|
| `add_element(el)` | 把元素加入模板内容。 |
| `append(el)` | add_element 的别名。 |
| `add(el)` | add_element 的别名（对应中文版 `模板.add(图形)` 的习惯写法）。 |
| `clone(x=None, y=None, width=None, height=None, **kw)` | 盖章：用 `<use>` 实例化本模板并返回实例元素（英文版新增）。 |
| `set_view_box(value)` | 设置 view_box（等价 `update(view_box=value)`）。 |
| `get_view_box()` | 读取 view_box 的当前属性值。 |
| `set_id_(value)` | 设置 id_（等价 `update(id_=value)`）。 |
| `get_id_()` | 读取 id_ 的当前属性值。 |

---

## 完整示例

在 PyCharm 里点绿色三角直接运行，或命令行：`python malight/elements/symbol.py`

```python
if __name__ == "__main__":
    import os

    from malight import Malight, ColorName

    _out = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        "..", "..", "output"))
    pen = Malight(os.path.join(_out, "demo_symbol"), width=620, height=380)
    pen.set_background_color(ColorName.WHITESMOKE)

    # -----------------------------------------------------------------
    # 1) 定义模板 <symbol>：只定义不显示（放在 <defs> 里）
    #    view_box 是模板自己的坐标系，用 <use> 复用时再缩放
    # -----------------------------------------------------------------
    star = pen.symbol(id_="star_tpl", view_box="0 0 100 100")
    star.append(pen.polygon(
        [(50, 5), (61, 38), (96, 38), (68, 59), (79, 92),
         (50, 71), (21, 92), (32, 59), (4, 38), (39, 38)],
        fill_color=ColorName.GOLD, stroke_color=ColorName.GOLDENROD))
    print("模板 id:", star.node.attribs.get("id"),
          "| viewBox:", star.node.attribs.get("viewBox"))

    # -----------------------------------------------------------------
    # 2) 用 <use> 反复复用：改模板一处，全部实例一起变，体积也小
    # -----------------------------------------------------------------
    for i in range(4):
        pen.use("star_tpl", x=50 + i * 70, y=50, width=60, height=60)
    for i in range(4):
        pen.use("star_tpl", x=80 + i * 70, y=130, width=40, height=40,
                opacity=0.7)

    # -----------------------------------------------------------------
    # 3) 实例可以各自加滤镜 / 动画 / 变换，互不影响
    # -----------------------------------------------------------------
    big = pen.use("star_tpl", x=230, y=200, width=150, height=150,
                  filter=pen.fx.glow(6, ColorName.GOLD))
    big.animate_rotate(360, center=(305, 275), dur=6)

    # -----------------------------------------------------------------
    # 4) 也可以把「外部 SVG 文件」直接注册成模板复用
    #    改模板内容的颜色走 tools 函数（模板本身不挂换色方法），改一处所有 <use> 一起变
    # -----------------------------------------------------------------
    icon = os.path.join(_out, "sample_icon.svg")
    if os.path.exists(icon):
        from malight.tools import replace_svg_node_color, svg_node_colors

        tpl_icon = pen.import_svg_as_symbol(icon, id_="icon_tpl")
        print("模板里的颜色:",
              svg_node_colors(tpl_icon.node))
        replace_svg_node_color(tpl_icon.node, "white", "#ff0000")
        pen.use("icon_tpl", x=430, y=210, width=150, height=100)
        pen.use("icon_tpl", x=430, y=300, width=100, height=67)

    # -----------------------------------------------------------------
    # 5) 局部更新：改模板的 viewBox（应谨慎，会改变所有实例的比例基准）
    # -----------------------------------------------------------------
    pen.symbol(id_="dot_tpl", view_box="0 0 10 10").append(
        pen.circle(5, 5, 4, fill_color=ColorName.CRIMSON))
    pen.use("dot_tpl", x=60, y=300, width=40, height=40)
    pen.use("dot_tpl", x=120, y=300, width=40, height=40, opacity=0.5)

    # -----------------------------------------------------------------
    # 6) 已有元素直接转模板（to_template + clone，英文版新增）
    # -----------------------------------------------------------------
    dot = pen.circle(400, 320, 26, fill_color=ColorName.STEELBLUE)
    tpl = dot.to_template()              # 元素进 defs，画布上暂不显示
    tpl.clone()                          # 原位原尺寸盖一个实例
    tpl.clone(x=480, width=42).fx_shadow(2, 2, 3)   # 移动缩放 + 实例自己的滤镜

    pen.finish()
```

---

## 同级模块

[base](base.zh.md) ｜ [circle](circle.zh.md) ｜ [clippath](clippath.zh.md) ｜ [ellipse](ellipse.zh.md) ｜ [group](group.zh.md) ｜ [image](image.zh.md) ｜ [line](line.zh.md) ｜ [link](link.zh.md) ｜ [marker](marker.zh.md) ｜ [mask](mask.zh.md) ｜ [path](path.zh.md) ｜ [pattern](pattern.zh.md) ｜ [polygon](polygon.zh.md) ｜ [polyline](polyline.zh.md) ｜ [rect](rect.zh.md) ｜ [svggroup](svggroup.zh.md) ｜ [svgimage](svgimage.zh.md) ｜ [text](text.zh.md) ｜ [textpath](textpath.zh.md) ｜ [topath](topath.zh.md) ｜ [use](use.zh.md)
