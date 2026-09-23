# -*- coding: utf-8 -*-
"""
FilterAPI —— 滤镜工厂（pen.fx / pen.filter）。 / The filter factory behind pen.fx and pen.filter.

滤镜的全部用法（8 种，可叠加、可复用；图解见 assets/images/filters_preview.png，
8 张卡片 = 左边代码右边结果）：

1. 元素方法链式（推荐，fx_* 返回自身可无限接）::
       el.fx_inner_shadow(1, 1, 2, "#ffffff", 0.6).fx_emboss().fx_blur(1.5)
2. 按名字叠加（等价 el.fx_blur(3)）::
       el.fx("blur", 3)
3. 追加任意 SVG 滤镜原语（保留扩展能力）::
       el.fx("custom", "feBlend", mode="screen", in2="SourceGraphic")
4. 取元素已有的链继续加效果::
       el.fx_chain().blur(2).saturate(1.4)
5. 工厂一步到位（filter= 直接传，最常用）::
       pen.circle(500, 300, 120, fill_color="#4e79a7",
                  filter=pen.fx.shadow(6, 8, 6))
6. 工厂建链再绑定（一条链可复用给多个元素）::
       f = pen.fx.chain().blur(1).shadow(5, 5, 4)
       a.set_filter(f)                 # 或等价的 f.apply(a)
7. 叠加 / 替换 / 清除（set_filter 默认是叠加，不是覆盖）::
       el.set_filter(pen.fx.shadow(6, 8, 6))
       el.set_filter(pen.fx.saturate(0.4))         # 叠上去，投影还在
       el.set_filter(pen.fx.glow(8), merge=False)  # 整条替换
       el.set_filter(None)                         # 清除
8. 底层工具（tools.create_*_filter 拿 id，extra 挂引用）::
       fid = create_glow_filter(pen, 6)
       pen.text(60, 150, "NEON", extra={"filter": "url(#%s)" % fid})

工厂方法与元素快捷方法一一对应（pen.fx.blur(x) 等价 el.fx_blur(x)）；
``pen.filter`` 是 ``pen.fx`` 的别名。

每个方法返回一个 FilterChain（含 <filter> 节点与 id），
可直接作为元素的 filter 参数，或用 el.set_filter(f) / f.apply(el) 绑定。

本文件只包含 FilterAPI 一个类。
"""

from .fx import FilterChain


class FilterAPI:
    """
    FilterAPI —— 滤镜工厂（对应中文版 `滤镜工具集`，参考 PS/AI 常用滤镜）。 / FilterAPI - the filter factory.

    通过 ``pen.fx``（或别名 ``pen.filter``）访问。每个方法返回 FilterChain，
    可继续 .blur() / .saturate() ... 链式叠加。

    示例::
        pen = MagicPen("fx", width=800, height=600)
        pen.circle(400, 300, 120, fill_color="#e63946",
                   filter=pen.fx.glow(8, "#ffd60a"))
        pen.finish()
    """

    def __init__(self, board):
        self.board = board

    # ------------------------------------------------------------------
    # 链式入口
    # ------------------------------------------------------------------
    def chain(self, id_=None, pad=0.4) -> FilterChain:
        """
        新建一个空滤镜链，然后自由叠加效果。 / Start an empty filter chain and stack effects on it freely.

        示例::
            f = pen.fx.chain().shadow(4, 4, 3).outline(2, "white")
            pen.circle(100, 100, 50, fill_color="#2a9d8f").set_filter(f)
        """
        return FilterChain(self.board, id_=id_, pad=pad)

    # ------------------------------------------------------------------
    # 模糊与锐化
    # ------------------------------------------------------------------
    def blur(self, std_deviation=3, **kw) -> FilterChain:
        """高斯模糊。 / Gaussian blur. 示例:: pen.image("p.jpg", filter=pen.fx.blur(4))"""
        return self.chain(**kw).blur(std_deviation)

    def sharpen(self, amount=0.5, **kw) -> FilterChain:
        """锐化（0~1）。 / Sharpen, amount 0-1. 示例:: pen.star(500, 300, 120, filter=pen.fx.sharpen(0.8))"""
        return self.chain(**kw).sharpen(amount)

    def motion_blur(self, distance=10, angle=0, **kw) -> FilterChain:
        """动感模糊。 / Motion blur. 示例:: pen.circle(200, 500, 40, filter=pen.fx.motion_blur(12, 0))"""
        return self.chain(**kw).motion_blur(distance, angle)

    # ------------------------------------------------------------------
    # 图层样式（阴影/发光/描边/浮雕）
    # ------------------------------------------------------------------
    def shadow(self, dx=4, dy=4, blur=4, color="black", opacity=0.5, **kw) -> FilterChain:
        """投影（= drop_shadow 的短名）。 / Drop shadow; a short alias of drop_shadow. 示例:: pen.rect(100, 100, 200, 150, filter=pen.fx.shadow(6, 6, 5))"""
        return self.chain(**kw).shadow(dx, dy, blur, color, opacity)

    def drop_shadow(self, dx=3, dy=3, std_deviation=3, opacity=0.5, **kw) -> FilterChain:
        """投影（旧参数名兼容版）。 / Drop shadow, kept for the older parameter names. 示例:: fx = pen.fx.drop_shadow(5, 5, 4)"""
        return self.chain(**kw).shadow(dx, dy, std_deviation, "black", opacity)

    def inner_shadow(self, dx=3, dy=3, blur=3, color="black", opacity=0.6, **kw) -> FilterChain:
        """内阴影。 / Inner shadow. 示例:: pen.rect(350, 200, 300, 200, filter=pen.fx.inner_shadow())"""
        return self.chain(**kw).inner_shadow(dx, dy, blur, color, opacity)

    def glow(self, std_deviation=4, color="#ffb703", opacity=0.9, **kw) -> FilterChain:
        """外发光。 / Outer glow. 示例:: pen.text(500, 150, "GLOW", filter=pen.fx.glow(8, "#00b4d8"))"""
        return self.chain(**kw).glow(std_deviation, color, opacity)

    def inner_glow(self, blur=5, color="#ffd166", opacity=0.9, **kw) -> FilterChain:
        """内发光。 / Inner glow. 示例:: pen.circle(700, 400, 100, filter=pen.fx.inner_glow())"""
        return self.chain(**kw).inner_glow(blur, color, opacity)

    def bevel(self, strength=1.0, blur=2, azimuth=225, elevation=55, **kw) -> FilterChain:
        """浮雕斜面（PS 斜面和浮雕）。 / Bevel and emboss, like the Photoshop layer style. 示例:: pen.text(500, 300, "3D", filter=pen.fx.bevel())"""
        return self.chain(**kw).bevel(strength, blur, azimuth, elevation)

    def engrave(self, depth=1.2, blur=1, dark="#3E2410", light="#FFFDF5", **kw) -> FilterChain:
        """雕刻凹陷（与 bevel 的凸起相反）。 / Engrave, the opposite of a raised bevel. 示例:: pen.text(60, 200, "帅", filter=pen.fx.engrave())"""
        return self.chain(**kw).engrave(depth, blur, dark, light)

    def outline(self, width=3, color="gold", **kw) -> FilterChain:
        """外描边。 / Outer stroke growing outwards along the outline. 示例:: pen.text(500, 200, "HALO", filter=pen.fx.outline(4, "#d62828"))"""
        return self.chain(**kw).outline(width, color)

    # ------------------------------------------------------------------
    # 风格化
    # ------------------------------------------------------------------
    def roughen(self, scale=4, frequency=0.05, **kw) -> FilterChain:
        """粗糙化（手绘感）。 / Roughen for a hand-drawn feel. 示例:: pen.heart(500, 300, 160, filter=pen.fx.roughen())"""
        return self.chain(**kw).roughen(scale, frequency)

    def noise(self, opacity=0.15, **kw) -> FilterChain:
        """噪点颗粒。 / Grainy noise overlay. 示例:: pen.rect(300, 200, 400, 250, filter=pen.fx.noise(0.2))"""
        return self.chain(**kw).noise(opacity)

    def emboss(self, azimuth=45, **kw) -> FilterChain:
        """浮雕灰度。 / Grayscale emboss. 示例:: pen.text(500, 300, "EM", filter=pen.fx.emboss())"""
        return self.chain(**kw).emboss(azimuth)

    def edge_detect(self, width=1, **kw) -> FilterChain:
        """边缘检测（线稿感），width>1 加粗边缘线。 / Edge detection for a line-art look; width above 1 thickens the strokes. 示例:: pen.star(500, 300, 140, filter=pen.fx.edge_detect(2))"""
        return self.chain(**kw).edge_detect(width)

    # ------------------------------------------------------------------
    # 颜色调整
    # ------------------------------------------------------------------
    def saturate(self, factor=1.2, **kw) -> FilterChain:
        """饱和度。 / Saturation. 示例:: pen.circle(300, 300, 100, filter=pen.fx.saturate(1.6))"""
        return self.chain(**kw).saturate(factor)

    def hue_rotate(self, degrees=90, **kw) -> FilterChain:
        """色相旋转。 / Hue rotation. 示例:: pen.circle(500, 300, 100, filter=pen.fx.hue_rotate(140))"""
        return self.chain(**kw).hue_rotate(degrees)

    def grayscale(self, **kw) -> FilterChain:
        """去色。 / Desaturate to grayscale. 示例:: pen.image("p.jpg", filter=pen.fx.grayscale())"""
        return self.chain(**kw).grayscale()

    def sepia(self, **kw) -> FilterChain:
        """褐色怀旧调。 / Sepia tone. 示例:: pen.image("old.jpg", filter=pen.fx.sepia())"""
        return self.chain(**kw).sepia()

    def brightness(self, factor=1.2, **kw) -> FilterChain:
        """亮度。 / Brightness. 示例:: pen.rect(0, 0, 500, 300, filter=pen.fx.brightness(1.4))"""
        return self.chain(**kw).brightness(factor)

    def contrast(self, factor=1.3, **kw) -> FilterChain:
        """对比度。 / Contrast. 示例:: pen.image("p.jpg", filter=pen.fx.contrast(1.5))"""
        return self.chain(**kw).contrast(factor)

    def gamma(self, r=1.0, g=1.0, b=1.0, **kw) -> FilterChain:
        """伽马校正。 / Gamma correction. 示例:: pen.image("p.jpg", filter=pen.fx.gamma(0.8, 0.9, 1.1))"""
        return self.chain(**kw).gamma(r, g, b)

    def invert(self, **kw) -> FilterChain:
        """反相。 / Invert colors. 示例:: pen.image("p.jpg", filter=pen.fx.invert())"""
        return self.chain(**kw).invert()

    def posterize(self, levels=4, **kw) -> FilterChain:
        """色调分离。 / Posterize; fewer levels means flatter color blocks. 示例:: pen.image("p.jpg", filter=pen.fx.posterize(3))"""
        return self.chain(**kw).posterize(levels)

    def color_overlay(self, color="red", opacity=0.8, **kw) -> FilterChain:
        """颜色叠加。 / Color overlay. 示例:: pen.polygon(pts, filter=pen.fx.color_overlay("#073b4c", 0.7))"""
        return self.chain(**kw).color_overlay(color, opacity)
