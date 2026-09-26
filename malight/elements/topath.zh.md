<!-- 本文件由 tools/gen_docs.py 从源码自动生成，请勿手改。
     要改内容请改同目录的 topath.py 里的文档字符串，然后重跑生成器。 -->

# topath.py

**简体中文** ｜ [English](topath.en.md) ｜ [← 返回 README](../../README.md)

元素转 PathElement（topath）—— `Element.to_path_element()` 的实现层

unsupported kinds raise `NotImplementedError`. / `convert_to_path()` 把几何元素
（矩形 / 圆 / 椭圆 / 直线 / 多边形 / 折线）转换成等价的 `PathElement`，原元素
保留；`PathElement` 自身直接原样返回。图片 / 文字等需要轮廓提取的类型抛
`NotImplementedError`（i18n 词条 `err.to_path_todo`，提示暂未实现）。

样式（填充 / 描边等）会带到新路径上；`kw` 可覆盖。 / Styles (fill / stroke
and so on) carry over to the new path; `kw` overrides them.

---

## 类与方法

### 函数

| 函数 | 说明 |
|---|---|
| `convert_to_path` | 把几何元素转换为等价 PathElement（原元素保留）。 |

---

## 完整示例

在 PyCharm 里点绿色三角直接运行，或命令行：`python malight/elements/topath.py`

```python
if __name__ == "__main__":
    import os

    from malight import Malight, ColorName

    _out = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        "..", "..", "output"))
    pen = Malight(os.path.join(_out, "demo_topath"), width=420, height=300)
    pen.set_background_color(ColorName.WHITESMOKE)

    rect = pen.rect(40, 40, 120, 80, fill_color=ColorName.TEAL,
                    stroke_color="gray")
    rp = rect.to_path_element()
    print("rect ->", type(rp).__name__, "| d:", rp.get_d())   # 圆角

    circle = pen.circle(240, 80, 40, fill_color="none",
                        stroke_color=ColorName.CRIMSON, stroke_width=3)
    cp = circle.to_path_element()
    print("circle -> d:", cp.get_d()[:60], "...")

    poly = pen.polygon([(60, 180), (150, 180), (105, 260)],
                       fill_color=ColorName.GOLD)
    pp = poly.to_path_element()
    print("polygon -> d:", pp.get_d())

    try:
        pen.text(240, 220, "hi").to_path_element()
    except NotImplementedError as exc:
        print("text -> NotImplementedError（符合预期", exc)

    pen.finish()
```

---

## 同级模块

[base](base.zh.md) ｜ [circle](circle.zh.md) ｜ [clippath](clippath.zh.md) ｜ [ellipse](ellipse.zh.md) ｜ [group](group.zh.md) ｜ [image](image.zh.md) ｜ [line](line.zh.md) ｜ [link](link.zh.md) ｜ [marker](marker.zh.md) ｜ [mask](mask.zh.md) ｜ [path](path.zh.md) ｜ [pattern](pattern.zh.md) ｜ [polygon](polygon.zh.md) ｜ [polyline](polyline.zh.md) ｜ [rect](rect.zh.md) ｜ [svggroup](svggroup.zh.md) ｜ [svgimage](svgimage.zh.md) ｜ [symbol](symbol.zh.md) ｜ [text](text.zh.md) ｜ [textpath](textpath.zh.md) ｜ [use](use.zh.md)
