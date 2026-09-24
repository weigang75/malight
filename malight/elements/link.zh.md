<!-- 本文件由 tools/gen_docs.py 从源码自动生成，请勿手改。
     要改内容请改同目录的 link.py 里的文档字符串，然后重跑生成器。 -->

# link.py

**简体中文** ｜ [English](link.en.md) ｜ [← 返回 README](../../README.md)

LinkElement 元素（每类一文件，含中文注释与示例）。

---

## 类与方法

### `LinkElement`

链接元素（`<a>`，对应中文版 `链接元素`）：点击元素打开网页。

| 方法 | 说明 |
|---|---|
| `wrap(el)` | 把元素包进链接（对应中文版 `创建链接` 的主体逻辑）。 |
| `set_href(value)` | 设置 href（等价 `update(href=value)`）。 |
| `get_href()` | 读取 href 的当前属性值。 |
| `set_tooltip(value)` | 设置 tooltip（等价 `update(tooltip=value)`）。 |
| `get_tooltip()` | 读取 tooltip 的当前属性值。 |
| `set_description(value)` | 设置 description（等价 `update(description=value)`）。 |
| `get_description()` | 读取 description 的当前属性值。 |

---

## 完整示例

在 PyCharm 里点绿色三角直接运行，或命令行：`python malight/elements/link.py`

```python
if __name__ == "__main__":
    import os

    from malight import Malight, ColorName

    _out = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        "..", "..", "output"))
    pen = Malight(os.path.join(_out, "demo_link"), width=660, height=340)
    pen.set_background_color(ColorName.WHITESMOKE)

    pen.text(330, 40, "链接元素 <a>：点元素即可跳转（用浏览器打开 SVG 时生效）",
             font_size=16, h_align="middle", fill_color=ColorName.DIMGRAY)

    # -----------------------------------------------------------------
    # 1) 把任意元素包成链接：圆角按钮
    # -----------------------------------------------------------------
    btn = pen.rect(60, 100, 180, 70, corner_radius=14,
                   fill_color=ColorName.STEELBLUE)
    pen.text(150, 143, "点我", font_size=22, fill_color="white",
             h_align="middle")
    link = pen.a(btn, "https://www.python.org", tooltip="打开 Python 官网",
                 description="外部链接示例")
    print("链接 href:", link.node.attribs.get("href"))

    # -----------------------------------------------------------------
    # 2) 文字链接（加下划线更像链接）
    # -----------------------------------------------------------------
    t = pen.text(300, 143, "点这里访问文档", font_size=20,
                 fill_color=ColorName.NAVY, underline=True)
    pen.a(t, "https://docs.python.org", tooltip="Python 文档")

    # -----------------------------------------------------------------
    # 3) 图片 / 图形链接；也可以跳内部锚点（如 "#top"）
    # -----------------------------------------------------------------
    icon = pen.circle(520, 135, 36, fill_color=ColorName.GOLD)
    pen.a(icon, "#top", tooltip="回到顶部")

    # -----------------------------------------------------------------
    # 4) 链接元素本身也能加滤镜、改透明度
    # -----------------------------------------------------------------
    link.set_filter(pen.fx.glow(4, ColorName.SKYBLUE))

    # 5) wrap：先建链接再往里塞元素（与 pen.a(el, url) 等价）
    holder = pen.a(None, "https://www.example.com", tooltip="示例")
    holder.wrap(pen.text(150, 240, "另一个链接", font_size=20,
                         fill_color=ColorName.TEAL))
    print("第二个链接 href:", holder.node.attribs.get("href"))

    # 6) 局部更新：换地址 / 换提示
    holder.update(href="https://www.python.org", tooltip="换成 Python 官网")
    print("更新后 href:", holder.node.attribs.get("href"))

    pen.finish()
```

---

## 同级模块

[base](base.zh.md) ｜ [circle](circle.zh.md) ｜ [clippath](clippath.zh.md) ｜ [ellipse](ellipse.zh.md) ｜ [group](group.zh.md) ｜ [image](image.zh.md) ｜ [line](line.zh.md) ｜ [marker](marker.zh.md) ｜ [mask](mask.zh.md) ｜ [path](path.zh.md) ｜ [pattern](pattern.zh.md) ｜ [polygon](polygon.zh.md) ｜ [polyline](polyline.zh.md) ｜ [rect](rect.zh.md) ｜ [svggroup](svggroup.zh.md) ｜ [svgimage](svgimage.zh.md) ｜ [symbol](symbol.zh.md) ｜ [text](text.zh.md) ｜ [textpath](textpath.zh.md) ｜ [use](use.zh.md)
