<!-- 本文件由 tools/gen_docs.py 从源码自动生成，请勿手改。
     要改内容请改同目录的 base.py 里的文档字符串，然后重跑生成器。 -->

# base.py

**简体中文** ｜ [English](base.en.md) ｜ [← 返回 README](../../README.md)

元素基类与共享辅助函数（所有元素的公共能力）。

- `_paint`     颜色参数归一化
- `_fmt_points` 顶点列表格式化
- `_fmt_transform` 变换列表格式化
- `_num`       属性值转 float（容忍 "120px" 这类写法）
- `Element`    所有元素的基类：样式/变换/动画/层级/克隆/包围盒

---

## 类与方法

### `Element`

所有元素的基类（对应中文版 `元素`）。

| 方法 | 说明 |
|---|---|
| `set_opacity(value)` | 设置整体不透明度（0-1）。 |
| `get_opacity()` | 读取不透明度的当前属性值（没设置过返回 None）。 |
| `set_fill_opacity(value)` | 设置填充不透明度。 |
| `get_fill_opacity()` | 读取填充不透明度的当前属性值。 |
| `set_stroke_opacity(value)` | 设置描边不透明度。 |
| `get_stroke_opacity()` | 读取描边不透明度的当前属性值。 |
| `set_fill_color(color)` | 设置填充色（支持 ColorName、#RRGGBB、渐变引用）；传 None 去掉填充。 |
| `get_fill_color()` | 读取填充色的当前属性值。 |
| `set_stroke_color(color)` | 设置描边色；传 None 去掉描边。 |
| `get_stroke_color()` | 读取描边色的当前属性值。 |
| `set_stroke_width(width)` | 设置描边宽度；传 None 去掉描边宽度。 |
| `get_stroke_width()` | 读取描边宽度的当前属性值。 |
| `set_stroke_style(dash)` | 设置描边虚线样式（如 "6,3"）。 |
| `get_stroke_style()` | 读取虚线样式的当前属性值。 |
| `set_dash_offset(offset)` | 设置虚线起始偏移（配合虚线做流动效果）。 |
| `get_dash_offset()` | 读取虚线偏移的当前属性值。 |
| `set_stroke_cap(cap)` | 设置线端样式（butt / round / square）。 |
| `get_stroke_cap()` | 读取线端样式的当前属性值。 |
| `set_stroke_join(join)` | 设置转折样式（miter / round / bevel）。 |
| `get_stroke_join()` | 读取转折样式的当前属性值。 |
| `set_fill_rule(rule)` | 设置填充规则（evenodd 可给重叠路径挖洞）。 |
| `get_fill_rule()` | 读取填充规则的当前属性值。 |
| `set_blend_mode(mode)` | 设置混合模式（写进 CSS style）。 |
| `set_paint_order(order)` | 设置绘制顺序，`PaintOrder.STROKE` 表示先描边后填充（空心字必备）。 |
| `get_paint_order()` | 读取绘制顺序的当前属性值。 |
| `set_vector_effect(effect)` | 设置矢量效果（non-scaling-stroke = 缩放时线宽不变）。 |
| `get_vector_effect()` | 读取矢量效果的当前属性值。 |
| `set_class_name(name)` | 设置 CSS 类名（配合样式表做分类样式）。 |
| `get_class_name()` | 读取 CSS 类名的当前属性值。 |
| `set_style_str(style)` | 直接设置内联 CSS。 |
| `get_style_str()` | 读取内联 CSS 的当前属性值。 |
| `set_id(id_)` | 设置元素 id（可用于 get_element(id) 反查）。 |
| `set_filter(f, merge=True)` | 给元素绑定滤镜，**多次调用会叠加而不是覆盖**（英文版新增，配合 pen.fx 滤镜工厂）。 |
| `fx_chain(pad=0.4)` | 取出本元素绑定的滤镜链，没有就新建一条并绑定（返回 FilterChain）。 |
| `fx(name, *args, **kwargs)` | 按名字叠加任意滤镜效果（通用入口）。 |
| `fx_blur(std_deviation=3)` | 叠加高斯模糊（等价 pen.fx.blur）。 |
| `fx_sharpen(amount=0.5)` | 叠加锐化（等价 pen.fx.sharpen）。 |
| `fx_motion_blur(distance=10, angle=0)` | 叠加动感模糊（等价 pen.fx.motion_blur）。 |
| `fx_shadow(dx=4, dy=4, blur=4, color='black', opacity=0.5)` | 叠加投影（等价 pen.fx.shadow）。 |
| `fx_drop_shadow(dx=3, dy=3, std_deviation=3, opacity=0.5)` | 叠加投影（旧参数名版本，等价 pen.fx.drop_shadow）。 |
| `fx_inner_shadow(dx=3, dy=3, blur=3, color='black', opacity=0.6)` | 叠加内阴影（等价 pen.fx.inner_shadow）。 |
| `fx_glow(std_deviation=4, color='#ffb703', opacity=0.9)` | 叠加外发光（等价 pen.fx.glow）。 |
| `fx_inner_glow(blur=5, color='#ffd166', opacity=0.9)` | 叠加内发光（等价 pen.fx.inner_glow）。 |
| `fx_bevel(strength=1.0, blur=2, azimuth=225, elevation=55)` | 叠加斜面浮雕高光（等价 pen.fx.bevel）。 |
| `fx_engrave(depth=1.2, blur=1, dark='#3E2410', light='#FFFDF5')` | 叠加雕刻凹陷（与凸起的 fx_bevel 相反，等价 pen.fx.engrave）。 |
| `fx_outline(width=3, color='gold')` | 叠加外描边（等价 pen.fx.outline）。 |
| `fx_roughen(scale=4, frequency=0.05)` | 叠加粗糙化手绘感（等价 pen.fx.roughen）。 |
| `fx_noise(opacity=0.15)` | 叠加噪点颗粒（等价 pen.fx.noise）。 |
| `fx_emboss(azimuth=45)` | 叠加浮雕灰度（等价 pen.fx.emboss）。 |
| `fx_edge_detect()` | 叠加边缘检测线稿感（等价 pen.fx.edge_detect）。 |
| `fx_saturate(factor=1.2)` | 叠加饱和度调整（等价 pen.fx.saturate）。 |
| `fx_hue_rotate(degrees=90)` | 叠加色相旋转（等价 pen.fx.hue_rotate）。 |
| `fx_grayscale()` | 叠加去色（等价 pen.fx.grayscale）。 |
| `fx_sepia()` | 叠加怀旧褐色调（等价 pen.fx.sepia）。 |
| `fx_brightness(factor=1.2)` | 叠加亮度调整（等价 pen.fx.brightness）。 |
| `fx_contrast(factor=1.3)` | 叠加对比度调整（等价 pen.fx.contrast）。 |
| `fx_gamma(r=1.0, g=1.0, b=1.0)` | 叠加伽马校正（等价 pen.fx.gamma）。 |
| `fx_invert()` | 叠加反相（等价 pen.fx.invert）。 |
| `fx_posterize(levels=4)` | 叠加色调分离（等价 pen.fx.posterize）。 |
| `fx_color_overlay(color='red', opacity=0.8)` | 叠加颜色叠加（等价 pen.fx.color_overlay）。 |
| `translate(dx, dy=0)` | 平移元素。 |
| `rotate(angle, cx=None, cy=None)` | 旋转元素。 |
| `scale(sx, sy=None)` | 缩放元素（sy 缺省时等比）。 |
| `skew_x(angle)` | 沿 X 轴倾斜（度）。 |
| `skew_y(angle)` | 沿 Y 轴倾斜（度）。 |
| `animate_opacity(start=1.0, end=0.0, dur=3, repeat_count='indefinite', begin=0)` | 透明度渐变动画（对应中文版 `透明动画`）。 |
| `animate_translate(offset=(0, 0), dur=3, repeat_count=1, begin=0)` | 平移动画（对应中文版 `平移动画`）。 |
| `animate_rotate(angle=360, center=(0, 0), dur=3, repeat_count='indefinite', begin=0, accelerate=False)` | 旋转动画（对应中文版 `旋转动画` / `加速旋转动画`）。 |
| `animate_scale(factor=(2, 2), dur=3, repeat_count=1, begin=0)` | 缩放动画（对应中文版 `缩放动画`）。 |
| `animate_skew_x(angle=30, dur=3, repeat_count=1, begin=0)` | X 轴倾斜动画（对应中文版 `倾斜X动画`）。 |
| `animate_skew_y(angle=30, dur=3, repeat_count=1, begin=0)` | Y 轴倾斜动画（对应中文版 `倾斜Y动画`）。 |
| `animate_motion(path, dur=5, rotate=False, repeat_count='indefinite', begin=0)` | 沿轨迹移动动画（对应中文版 `轨迹移动动画`）。 |
| `animate_dash_flow(dur=2, repeat_count='indefinite', dash='8 4', speed=64)` | 虚线流动画（对应中文版 `虚线流动画`）：蚂蚁线效果。 |
| `remove()` | 从画布上删除本元素（对应中文版 `删除`）。 |
| `bring_to_front()` | 置顶（对应中文版 `置前`）：移到父容器的最后一个。 |
| `send_to_back()` | 置底（英文版新增）：移到父容器的第一个。 |
| `change_group(new_parent)` | 把元素移动到另一个组（对应中文版 `更换组`）。 |
| `to_group(id_=None)` | 把本元素原地包进一个新组并返回该组（英文版新增）。 |
| `clone(dx=0, dy=0, id_=None)` | 克隆元素（对应中文版 `克隆`），可指定偏移与新 id。 |
| `update(**kw)` | 按需更新元素属性（英文版新增：只改传入的项，其余保持原值）。 |
| `bbox()` | 元素包围盒 (min_x, min_y, max_x, max_y)；无法确定时返回 None。 |
| `center_x`（属性） | 中心点 x（对应中文版 `中心x`）。 |
| `center_y`（属性） | 中心点 y（对应中文版 `中心y`）。 |
| `width`（属性） | 宽度（对应中文版 `宽`）。 |
| `height`（属性） | 高度（对应中文版 `高`）。 |

---

## 完整示例

在 PyCharm 里点绿色三角直接运行，或命令行：`python malight/elements/base.py`

```python
if __name__ == "__main__":
    import os

    from malight import Malight, ColorName, Font

    # 输出统一放到项目根的 output/ 目录（从哪运行结果都在同一处）
    _out = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        "..", "..", "output"))
    pen = Malight(os.path.join(_out, "demo_element_base"), width=560, height=340)
    pen.set_background_color(ColorName.WHITESMOKE)

    pen.text(280, 40, "Element 基类：所有元素的共同能力", font=Font.SIMHEI,
             font_size=20, h_align="middle", fill_color=ColorName.NAVY)

    # 1) 元素由绘图板创建，返回的是「具体类型」，PyCharm 能提示
    ball = pen.circle(140, 170, 60, fill_color=ColorName.TOMATO,
                      stroke_color=ColorName.NAVY, stroke_width=3)
    print("元素类型:", type(ball).__name__)          # CircleElement

    # 2) 设置 id 后可以反查
    ball.set_id("ball")
    print("按 id 反查同一个对象:", pen.get_element("ball") is ball)

    # 3) 几何信息（基类提供，所有元素都有）
    print("包围盒 bbox:", tuple(round(v, 1) for v in ball.bbox()))
    print("中心点:", round(ball.center_x, 1), round(ball.center_y, 1))
    print("宽高:", round(ball.width, 1), round(ball.height, 1))

    # 4) 变换：可链式，返回的仍是 CircleElement
    ball.translate(20, -10)                  # 平移
    ball.rotate(15, cx=140, cy=170)          # 绕指定点旋转
    ball.scale(1.05)                         # 缩放

    # 5) 局部更新：只改传入的项，几何不受影响
    ball.update(opacity=0.85)

    # 6) 滤镜：一行加特效（pen.fx 是滤镜工厂）
    #    滤镜效果请用浏览器打开输出 SVG 查看，转 PNG 时 cairosvg 不渲染 filters
    ball.set_filter(pen.fx.shadow(6, 8, 6))

    # 7) 克隆（同类型；可带偏移与新 id）
    twin = ball.clone(dx=190, id_="ball2")
    print("克隆体类型:", type(twin).__name__,
          "| id:", twin.node.attribs.get("id"))

    # 8) 层级调整：后画的元素在上层，可用它们改遮挡关系
    twin.bring_to_front()

    # 9) 动画（SMIL，用浏览器打开 SVG 才能看到动）
    twin.animate_translate(offset=(0, -30), dur=2, repeat_count="indefinite")
    twin.animate_opacity(1.0, 0.4, dur=2, repeat_count="indefinite")

    # 10) 透传自定义 SVG 属性（extra 里的键会原样落成属性）
    pen.rect(370, 130, 150, 90, corner_radius=10,
             fill_color=ColorName.STEELBLUE,
             extra={"data-name": "panel"})

    # 11) 删除元素（从画布移除）
    pen.circle(500, 300, 20, fill_color=ColorName.CRIMSON).remove()

    pen.finish()      # 保存 SVG，并打印文件全路径（方便直接复制）


# ---------------------------------------------------------------------------
# 底部导入：to_group() 的返回注解引用 GroupElement，而 group.py 又继承本模块的
# Element —— 顶部互相导入会循环；放到文件末尾（Element 已定义完毕）两个问题都解决，
# elements.__init__ 保证 base 先于 group 导入，运行时不会触发循环。
# ---------------------------------------------------------------------------
from .group import GroupElement  # noqa: E402
```

---

## 同级模块

[circle](circle.zh.md) ｜ [clippath](clippath.zh.md) ｜ [ellipse](ellipse.zh.md) ｜ [group](group.zh.md) ｜ [image](image.zh.md) ｜ [line](line.zh.md) ｜ [link](link.zh.md) ｜ [marker](marker.zh.md) ｜ [mask](mask.zh.md) ｜ [path](path.zh.md) ｜ [pattern](pattern.zh.md) ｜ [polygon](polygon.zh.md) ｜ [polyline](polyline.zh.md) ｜ [rect](rect.zh.md) ｜ [svgimage](svgimage.zh.md) ｜ [symbol](symbol.zh.md) ｜ [text](text.zh.md) ｜ [textpath](textpath.zh.md) ｜ [use](use.zh.md)
