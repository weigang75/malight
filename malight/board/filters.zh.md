<!-- 本文件由 tools/gen_docs.py 从源码自动生成，请勿手改。
     要改内容请改同目录的 filters.py 里的文档字符串，然后重跑生成器。 -->

# filters.py

**简体中文** ｜ [English](filters.en.md) ｜ [← 返回 README](../../README.md)

FilterAPI —— 滤镜工厂（pen.fx / pen.filter）。

滤镜的全部用法（8 种，可叠加、可复用；图解见 assets/images/filters_preview.png，
8 张卡片 = 左边代码右边结果）：

1. 元素方法链式（推荐，fx_* 返回自身可无限接）

```text
el.fx_inner_shadow(1, 1, 2, "#ffffff", 0.6).fx_emboss().fx_blur(1.5)
```

2. 按名字叠加（等价 el.fx_blur(3)）

```text
el.fx("blur", 3)
```

3. 追加任意 SVG 滤镜原语（保留扩展能力）

```text
el.fx("custom", "feBlend", mode="screen", in2="SourceGraphic")
```

4. 取元素已有的链继续加效果

```text
el.fx_chain().blur(2).saturate(1.4)
```

5. 工厂一步到位（filter= 直接传，最常用）

```text
pen.circle(500, 300, 120, fill_color="#4e79a7",
           filter=pen.fx.shadow(6, 8, 6))
```

6. 工厂建链再绑定（一条链可复用给多个元素）

```text
f = pen.fx.chain().blur(1).shadow(5, 5, 4)
a.set_filter(f)                 # 或等价的 f.apply(a)
```

7. 叠加 / 替换 / 清除（set_filter 默认是叠加，不是覆盖）

```text
el.set_filter(pen.fx.shadow(6, 8, 6))
el.set_filter(pen.fx.saturate(0.4))         # 叠上去，投影还在
el.set_filter(pen.fx.glow(8), merge=False)  # 整条替换
el.set_filter(None)                         # 清除
```

8. 底层工具（tools.create_*_filter 拿 id，extra 挂引用）

```text
fid = create_glow_filter(pen, 6)
pen.text(60, 150, "NEON", extra={"filter": "url(#%s)" % fid})
```

工厂方法与元素快捷方法一一对应（pen.fx.blur(x) 等价 el.fx_blur(x)）；
`pen.filter` 是 `pen.fx` 的别名。

每个方法返回一个 FilterChain（含 `<filter>` 节点与 id），
可直接作为元素的 filter 参数，或用 el.set_filter(f) / f.apply(el) 绑定。

本文件只包含 FilterAPI 一个类。

![滤镜的 8 种用法](../assets/images/filters_preview.png)

---

## 类与方法

### `FilterAPI`

FilterAPI —— 滤镜工厂（对应中文版 `滤镜工具集`，参考 PS/AI 常用滤镜）。

| 方法 | 说明 |
|---|---|
| `chain(id_=None, pad=0.4)` | 新建一个空滤镜链，然后自由叠加效果。 |
| `blur(std_deviation=3, **kw)` | 高斯模糊。 |
| `sharpen(amount=0.5, **kw)` | 锐化（0~1）。 |
| `motion_blur(distance=10, angle=0, **kw)` | 动感模糊。 |
| `shadow(dx=4, dy=4, blur=4, color='black', opacity=0.5, **kw)` | 投影（= drop_shadow 的短名）。 |
| `drop_shadow(dx=3, dy=3, std_deviation=3, opacity=0.5, **kw)` | 投影（旧参数名兼容版）。 |
| `inner_shadow(dx=3, dy=3, blur=3, color='black', opacity=0.6, **kw)` | 内阴影。 |
| `glow(std_deviation=4, color='#ffb703', opacity=0.9, **kw)` | 外发光。 |
| `inner_glow(blur=5, color='#ffd166', opacity=0.9, **kw)` | 内发光。 |
| `bevel(strength=1.0, blur=2, azimuth=225, elevation=55, **kw)` | 浮雕斜面（PS 斜面和浮雕）。 |
| `engrave(depth=1.2, blur=1, dark='#3E2410', light='#FFFDF5', **kw)` | 雕刻凹陷（与 bevel 的凸起相反）。 |
| `outline(width=3, color='gold', **kw)` | 外描边。 |
| `roughen(scale=4, frequency=0.05, **kw)` | 粗糙化（手绘感）。 |
| `noise(opacity=0.15, **kw)` | 噪点颗粒。 |
| `emboss(azimuth=45, **kw)` | 浮雕灰度。 |
| `edge_detect(width=1, **kw)` | 边缘检测（线稿感），width>1 加粗边缘线。 |
| `saturate(factor=1.2, **kw)` | 饱和度。 |
| `hue_rotate(degrees=90, **kw)` | 色相旋转。 |
| `grayscale(**kw)` | 去色。 |
| `sepia(**kw)` | 褐色怀旧调。 |
| `brightness(factor=1.2, **kw)` | 亮度。 |
| `contrast(factor=1.3, **kw)` | 对比度。 |
| `gamma(r=1.0, g=1.0, b=1.0, **kw)` | 伽马校正。 |
| `invert(**kw)` | 反相。 |
| `posterize(levels=4, **kw)` | 色调分离。 |
| `color_overlay(color='red', opacity=0.8, **kw)` | 颜色叠加。 |

---

## 同级模块

[containers](containers.zh.md) ｜ [core](core.zh.md) ｜ [debug](debug.zh.md) ｜ [effects](effects.zh.md) ｜ [fx](fx.zh.md) ｜ [gradients_mixin](gradients_mixin.zh.md) ｜ [images](images.zh.md) ｜ [layout](layout.zh.md) ｜ [paths](paths.zh.md) ｜ [repeat](repeat.zh.md) ｜ [shapes](shapes.zh.md) ｜ [style](style.zh.md) ｜ [text_board](text_board.zh.md)
