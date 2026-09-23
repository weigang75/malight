<!-- 本文件由 tools/gen_docs.py 从源码自动生成，请勿手改。
     要改内容请改同目录的 fx.py 里的文档字符串，然后重跑生成器。 -->

# fx.py

**简体中文** ｜ [English](fx.en.md) ｜ [← 返回 README](../../README.md)

FilterChain —— 链式滤镜构建器（参考 Photoshop / Illustrator 常用滤镜）。

一个 FilterChain 对应 SVG 的一个 `<filter>` 定义，效果方法按调用顺序
串接 SVG 滤镜原语（feGaussianBlur / feOffset / feFlood / feComposite /
feMerge / feColorMatrix / feComponentTransfer / feConvolveMatrix /
feTurbulence / feDisplacementMap / feMorphology / feSpecularLighting），
前一步的输出自动作为下一步的输入，所见即所得。

只收录在主流浏览器（Chrome / Firefox / Safari / Edge）中渲染结果
稳定、可预期的效果；不收录渲染结果不可控的滤镜。

元素侧还有与工厂一一对应的快捷方法（fx_* 返回自身，可无限链式）

```text
el.fx_inner_shadow(1, 1, 2, "#ffffff", 0.6).fx_emboss().fx_blur(1.5)
el.fx("blur", 3)                            # 按名字，等价 el.fx_blur(3)
el.fx("custom", "feBlend", mode="screen")   # 追加自定义 SVG 原语
el.fx_chain().blur(2).saturate(1.4)         # 取元素已有的链继续加
```

滤镜的全部用法（8 种）集中在 malight/board/filters.py 的模块说明里，
配图见 assets/images/filters_preview.png。

本文件只包含 FilterChain 一个类。

![滤镜效果一览](../assets/images/fx_preview.png)

---

## 类与方法

### 函数

| 函数 | 说明 |
|---|---|
| `count_refs` | 统计画布上有多少个元素引用了该滤镜链（内部辅助，用于判断能否回收 `<filter>` 节点）。 |

### `FilterChain`

FilterChain —— 链式滤镜（对应 Photoshop 的「图层样式 + 滤镜」）。

| 方法 | 说明 |
|---|---|
| `url()` | 返回 filter 引用串 "url(#id)"。 |
| `apply(el)` | 把滤镜应用到元素（等价于 el.set_filter(f)）。 |
| `clone(id_=None)` | 复制一条独立的新链（含已有效果），供另一个元素单独续接使用。 |
| `merge_from(other)` | 把另一个滤镜链的效果**叠加**到本链末尾（内部方法）。 |
| `dispose()` | 从画板 defs 移除本链的 `<filter>` 节点并注销（内部方法）。 |
| `blur(std_deviation=3)` | 高斯模糊（对应 PS「高斯模糊」）。 |
| `sharpen(amount=0.5)` | 锐化（对应 PS「USM 锐化」的简化版，amount 0~1）。 |
| `motion_blur(distance=10, angle=0)` | 方向模糊（对应 PS「动感模糊」，distance ≤ 15 效果最佳）。 |
| `shadow(dx=4, dy=4, blur=4, color='black', opacity=0.5)` | 投影（对应 PS「投影 Drop Shadow」）。 |
| `inner_shadow(dx=3, dy=3, blur=3, color='black', opacity=0.6)` | 内阴影（对应 PS「内阴影 Inner Shadow」）。 |
| `glow(blur=5, color='#ffb703', opacity=0.9)` | 外发光（对应 PS「外发光 Outer Glow」）。 |
| `inner_glow(blur=5, color='#ffd166', opacity=0.9)` | 内发光（对应 PS「内发光 Inner Glow」）。 |
| `bevel(strength=1.0, blur=2, azimuth=225, elevation=55, light_color='white', surface=2.5)` | 浮雕斜面（对应 PS「斜面和浮雕 Bevel & Emboss」的高光部分）。 |
| `engrave(depth=1.2, blur=1, dark='#3E2410', light='#FFFDF5', dark_opacity=0.85, light_opacity=0.9)` | 雕刻凹陷（对应 PS「斜面和浮雕 Bevel & Emboss」的凹陷方向，与 bevel 相反）。 |
| `outline(width=3, color='gold')` | 外描边（对应 PS「描边 Stroke」图层样式，沿轮廓向外扩）。 |
| `roughen(scale=4, frequency=0.05, seed=None)` | 粗糙化（对应 PS「扩散/粗糙化」手绘感，用湍流置换实现）。 |
| `noise(opacity=0.15, mono=True, seed=None)` | 噪点颗粒（对应 PS「添加杂色」，叠加在图形上）。 |
| `emboss(azimuth=45)` | 浮雕灰度（对应 PS「风格化→浮雕效果」，输出灰度浮雕）。 |
| `edge_detect(width=1)` | 边缘检测（对应 PS「风格化→查找边缘」，输出线稿感灰度）。 |
| `saturate(factor=1.2)` | 饱和度（对应 PS「色相/饱和度」）：factor<1 降低，>1 提高。 |
| `hue_rotate(degrees=90)` | 色相旋转（对应 PS「色相」滑块，整图换色系）。 |
| `grayscale()` | 去色（对应 PS「去色/黑白」）。 |
| `sepia()` | 怀旧褐色调（对应 PS「照片滤镜→褐」）。 |
| `brightness(factor=1.2)` | 亮度（对应 PS「亮度」）：factor<1 变暗，>1 变亮。 |
| `contrast(factor=1.3)` | 对比度（对应 PS「对比度」）：factor<1 降低，>1 提高。 |
| `gamma(r=1.0, g=1.0, b=1.0)` | 伽马校正（对应 PS「曝光度/曲线」的幂次调整）：>1 提亮中间调，<1 压暗。 |
| `invert()` | 反相（对应 PS「反相 Ctrl+I」）。 |
| `posterize(levels=4)` | 色调分离（对应 PS「色调分离 Posterize」）：levels 越小色块感越强。 |
| `color_overlay(color='red', opacity=0.8)` | 颜色叠加（对应 PS「颜色叠加 Color Overlay」）。 |
| `custom(tag, **attribs)` | 追加任意 SVG 滤镜原语（保留扩展能力，如 feBlend / feTile 等）。 |

---

## 同级模块

[containers](containers.zh.md) ｜ [core](core.zh.md) ｜ [debug](debug.zh.md) ｜ [effects](effects.zh.md) ｜ [filters](filters.zh.md) ｜ [gradients_mixin](gradients_mixin.zh.md) ｜ [images](images.zh.md) ｜ [layout](layout.zh.md) ｜ [paths](paths.zh.md) ｜ [repeat](repeat.zh.md) ｜ [shapes](shapes.zh.md) ｜ [style](style.zh.md) ｜ [text_board](text_board.zh.md)
