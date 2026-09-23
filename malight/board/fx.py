# -*- coding: utf-8 -*-
"""
FilterChain —— 链式滤镜构建器（参考 Photoshop / Illustrator 常用滤镜）。 / FilterChain, a chainable builder for Photoshop-style filter stacks.

一个 FilterChain 对应 SVG 的一个 ``<filter>`` 定义，效果方法按调用顺序
串接 SVG 滤镜原语（feGaussianBlur / feOffset / feFlood / feComposite /
feMerge / feColorMatrix / feComponentTransfer / feConvolveMatrix /
feTurbulence / feDisplacementMap / feMorphology / feSpecularLighting），
前一步的输出自动作为下一步的输入，所见即所得。

只收录在主流浏览器（Chrome / Firefox / Safari / Edge）中渲染结果
稳定、可预期的效果；不收录渲染结果不可控的滤镜。

元素侧还有与工厂一一对应的快捷方法（fx_* 返回自身，可无限链式）::

    el.fx_inner_shadow(1, 1, 2, "#ffffff", 0.6).fx_emboss().fx_blur(1.5)
    el.fx("blur", 3)                            # 按名字，等价 el.fx_blur(3)
    el.fx("custom", "feBlend", mode="screen")   # 追加自定义 SVG 原语
    el.fx_chain().blur(2).saturate(1.4)         # 取元素已有的链继续加

滤镜的全部用法（8 种）集中在 malight/board/filters.py 的模块说明里，
配图见 assets/images/filters_preview.png。

本文件只包含 FilterChain 一个类。
"""

import copy
import math

from ..svg_backend import SvgNode
from ..elements.base import Element, _paint


def count_refs(board, chain) -> int:
    """
    统计画布上有多少个元素引用了该滤镜链（内部辅助，用于判断能否回收 <filter> 节点）。 / Count how many drawn nodes reference this filter chain; used to decide whether the <filter> node can be recycled.

    :param board: 绘图板 :param chain: FilterChain
    :return: 引用该链的节点数量

    示例（内部）::
        count_refs(pen, chain)     # 0 表示没有元素在用它了
    """
    if board is None:
        return 0
    want = chain.url()
    n = 0
    stack = [board.canvas_node]
    while stack:
        node = stack.pop()
        if node.attribs.get("filter") == want:
            n += 1
        stack.extend(c for c in node.children if isinstance(c, SvgNode))
    return n


# 常用颜色矩阵（feColorMatrix values，5x4：R G B A + 偏移行）
_GRAY_MATRIX = ("0.2126 0.7152 0.0722 0 0 "
                "0.2126 0.7152 0.0722 0 0 "
                "0.2126 0.7152 0.0722 0 0 "
                "0 0 0 1 0")
_SEPIA_MATRIX = ("0.393 0.769 0.189 0 0 "
                 "0.349 0.686 0.168 0 0 "
                 "0.272 0.534 0.131 0 0 "
                 "0 0 0 1 0")

# 无输入端的滤镜原语（不应写 "in" 属性）
_NO_INPUT = {"feFlood", "feTurbulence", "feImage",
             "feDistantLight", "fePointLight", "feSpotLight"}


class FilterChain:
    """
    FilterChain —— 链式滤镜（对应 Photoshop 的「图层样式 + 滤镜」）。 / FilterChain - chainable filters, modelled on Photoshop layer styles plus filters.

    通过 ``pen.fx`` 工厂创建；效果方法全部链式调用，返回自身::

        f = pen.fx.chain()
        f.blur(2).shadow(dx=5, dy=5, blur=5).saturate(1.3)
        pen.circle(120, 120, 80, fill_color="#4e79a7").set_filter(f)

        # 或一步到位：工厂方法直接返回已含单个效果的链
        pen.rect(300, 80, 200, 120, fill_color="#e15759",
                 filter=pen.fx.glow(6, color="#ffb703"))

    多个效果**按调用顺序叠加**（后者作用于前者的输出），
    例如内阴影之后再浮雕，两个效果都会保留::

        pen.text(60, 200, "帅", font_size=44, fill_color="#c23b22") \\
           .set_filter(pen.fx.inner_shadow(1, 1, 2, "#ffffff", 0.6)) \\
           .set_filter(pen.fx.emboss())

    元素上绑定的链如果被多个元素共用（如 ``clone()`` 出来的副本），
    再叠加时会自动**复制一份专属于该元素**的链，不会串改其他元素。

    :param board: 所属绘图板（滤镜 <filter> 节点挂到其 <defs>）
    :param id_: 滤镜 id（缺省自动生成 fx_1 / fx_2 ...）
    :param pad: 滤镜作用区域外扩比例（默认 0.4，防止大模糊/投影被裁切）
    """

    def __init__(self, board, id_=None, pad=0.4):
        self.board = board
        self.id = id_ or board._gen_id("fx")
        self.pad = pad
        p = int(round(pad * 100))
        self.node = SvgNode("filter", {
            "id": self.id,
            "x": f"-{p}%", "y": f"-{p}%",
            "width": f"{100 + 2 * p}%", "height": f"{100 + 2 * p}%",
        })
        board.defs_node.add(self.node)
        # 登记到画板：元素可以由 filter 属性反查回链（克隆、手工赋值后仍能续接）
        chains = getattr(board, "_filter_chains", None)
        if chains is None:
            chains = board._filter_chains = {}
        chains[self.id] = self
        self._src = "SourceGraphic"   # 当前效果链的输入源
        self._merge_seq = 0           # 跨链合并计数（用于给合并进来的 result 起唯一名）

    # ------------------------------------------------------------------
    # 应用与引用
    # ------------------------------------------------------------------
    def url(self) -> str:
        """返回 filter 引用串 "url(#id)"。 / Return the filter reference string "url(#id)". 示例:: el.node.set("filter", f.url())"""
        return f"url(#{self.id})"

    def apply(self, el) -> "Element":
        """把滤镜应用到元素（等价于 el.set_filter(f)）。 / Apply the filter to an element; equivalent to el.set_filter(f). 示例:: f.apply(circle)"""
        el.set_filter(self)
        return el

    def clone(self, id_=None) -> "FilterChain":
        """
        复制一条独立的新链（含已有效果），供另一个元素单独续接使用。 / Copy this chain, effects included, into an independent new one so another element can extend it on its own.

        内部用于「同一条链被多个元素共用」时避免互相影响；
        也可以直接拿来微调出一个变体。

        示例::

            base = pen.fx.shadow(5, 6, 5)
            soft = base.clone().blur(2)     # 变体，不影响 base
        """
        new = FilterChain(self.board, id_=id_, pad=self.pad)
        rename = {}
        for ch in self.node.children:
            if isinstance(ch, SvgNode):
                r = ch.attribs.get("result")
                if r:
                    rename[r] = f"{r}_c{new.id.split('_')[-1]}"
        for ch in self.node.children:
            new.node.add(self._retarget(ch, rename, "SourceGraphic"))
        if self._src in rename:
            new._src = rename[self._src]
        return new

    def merge_from(self, other) -> "FilterChain":
        """
        把另一个滤镜链的效果**叠加**到本链末尾（内部方法）。 / Stack another chain's effects onto the end of this one (internal).

        合并规则：``other`` 里的 result 名统一改名避免与本链冲突；
        ``other`` 中指向 ``SourceGraphic`` 的输入改指本链当前的输出，
        所以第二个效果是作用在第一个效果的结果上的（真正的叠加，
        而不是被覆盖）。``SourceAlpha`` 保持不动 —— 那是原始图形的轮廓。

        :param other: 要被吸收的链（吸收后其 <filter> 节点可回收）
        :return: self
        """
        if other is self or other.node is self.node:
            return self                      # 同一条链重复绑定，忽略
        self._merge_seq += 1
        seq = self._merge_seq
        rename = {}
        for ch in other.node.children:
            if isinstance(ch, SvgNode):
                r = ch.attribs.get("result")
                if r:
                    rename[r] = f"{r}_x{seq}"
        base_src = self._src
        for ch in other.node.children:
            self.node.add(self._retarget(ch, rename, base_src))
        if other._src in rename:
            self._src = rename[other._src]
        return self

    def _retarget(self, node, rename, base_src) -> SvgNode:
        """
        深拷贝一个原语节点，并把它的 result / in / in2 引用改到本链的命名空间（内部方法）。 / Deep-copy one primitive and rewrite its result/in/in2 references into this chain's namespace (internal).
        """
        new = copy.deepcopy(node)
        self._retarget_inplace(new, rename, base_src)
        return new

    def _retarget_inplace(self, node, rename, base_src) -> None:
        """
        就地改写一个原语（含子节点）的引用名（内部方法）。 / Rewrite the references of one primitive in place, children included (internal).

        **必须递归到子节点**：feMergeNode 的 ``in``、feFuncA 等挂在原语
        下面，只在原语自身的属性上改名的话，``feMerge`` 引用的还是旧名 ——
        合并后旧名已不存在，整段效果会被静默丢掉（合并两条都用 ``feMerge``
        的链时，前一条会消失）。
        """
        r = node.attribs.get("result")
        if r in rename:
            node.attribs["result"] = rename[r]
        for key in ("in", "in2", "in3"):
            v = node.attribs.get(key)
            if v is None:
                continue
            if v in rename:
                node.attribs[key] = rename[v]
            elif v == "SourceGraphic" and base_src != "SourceGraphic":
                node.attribs[key] = base_src      # 接上本链已有的输出
        for ch in node.children:
            if isinstance(ch, SvgNode):
                self._retarget_inplace(ch, rename, base_src)

    def dispose(self) -> None:
        """
        从画板 defs 移除本链的 <filter> 节点并注销（内部方法）。 / Remove this chain's <filter> from the board defs and unregister it (internal).

        只在确认没有元素引用它时调用（见 ``count_refs()``），
        否则元素上的 ``filter="url(#...)"`` 会指向不存在的滤镜。
        """
        self.board.defs_node.remove_child(self.node)
        chains = getattr(self.board, "_filter_chains", None)
        if chains is not None:
            chains.pop(self.id, None)

    def __str__(self) -> str:
        return f"url(#{self.id})"

    # ------------------------------------------------------------------
    # 内部原语
    # ------------------------------------------------------------------
    def _fe(self, tag, attribs=None, result=True) -> SvgNode:
        """
        追加一个滤镜原语节点（内部方法）。

        - 原语无输入端（如 feFlood）时不写 ``in``；
          未显式给 ``in`` 时自动接上一步 result（效果链）；
        - result=True 时生成 result 名并更新链输入。
        """
        attribs = dict(attribs or {})
        if tag not in _NO_INPUT and "in" not in attribs:
            attribs["in"] = self._src
        if result:
            r = f"{tag.replace('fe', '').lower()}_{len(self.node.children)}"
            attribs["result"] = r
            self._src = r
        n = SvgNode(tag, attribs)
        self.node.add(n)
        return n

    def _r(self, node) -> str:
        """取节点的 result 名（内部方法）。"""
        return node.attribs.get("result")

    def _merge_over_source(self, under_src=True, base="SourceGraphic") -> None:
        """
        把当前结果与底图合并（内部方法）。under_src=True 时效果垫底。

        :param base: 合成的底图 —— 默认 ``SourceGraphic``（本效果是链上第一个
            效果时）；本效果前面还有别的效果时，调用方必须把本效果的输入
            （进入本效果时的 ``self._src``）传进来，否则合成结果里只剩
            SourceGraphic，**前面的效果会被整段丢掉**（两个都带合成的效果
            叠加时，就是「后面的把前面的顶掉」）。

        合并后的结果会**成为链的新输入**，所以后面继续追加的效果是叠在
        「底图 + 本效果」之上的（这是多个效果能叠加的关键；早期版本这里把
        输入重置回 SourceGraphic，导致同一链里后面的效果把前面的顶掉）。
        """
        cur = self._src
        m = SvgNode("feMerge")
        if under_src:
            m.add(SvgNode("feMergeNode", {"in": cur}))
            m.add(SvgNode("feMergeNode", {"in": base}))
        else:
            m.add(SvgNode("feMergeNode", {"in": base}))
            m.add(SvgNode("feMergeNode", {"in": cur}))
        r = f"merge_{len(self.node.children)}"
        m.set("result", r)
        self.node.add(m)
        self._src = r

    def _flood_color(self, color, opacity, alpha_result) -> str:
        """flood + 按 alpha 区域着色（内部方法），返回彩色层 result 名。"""
        fl = self._fe("feFlood", {"flood-color": _paint(color) or "#000000",
                                  "flood-opacity": opacity})
        return self._fe("feComposite", {"in": self._r(fl),
                                        "in2": alpha_result,
                                        "operator": "in"})

    # ------------------------------------------------------------------
    # 模糊与锐化（Blur / Sharpen）
    # ------------------------------------------------------------------
    def blur(self, std_deviation=3) -> "FilterChain":
        """
        高斯模糊（对应 PS「高斯模糊」）。 / Gaussian blur, matching Photoshop's Gaussian Blur.

        :param std_deviation: 模糊强度（标准差，越大越模糊）

        示例::
            pen.text(500, 100, "背景文字", font_size=40,
                     filter=pen.fx.blur(3))
        """
        self._fe("feGaussianBlur", {"stdDeviation": std_deviation})
        return self

    def sharpen(self, amount=0.5) -> "FilterChain":
        """
        锐化（对应 PS「USM 锐化」的简化版，amount 0~1）。 / Sharpen, a simplified Photoshop USM Sharpen, amount 0-1.

        示例::
            pen.star(500, 300, 120, fill_color="#f4a261",
                     filter=pen.fx.sharpen(0.8))
        """
        a = max(0.0, float(amount))
        kernel = f"0 {-a} 0 {-a} {1 + 4 * a} {-a} 0 {-a} 0"
        self._fe("feConvolveMatrix", {
            "order": "3", "kernelMatrix": kernel,
            "preserveAlpha": "true"})
        return self

    def motion_blur(self, distance=10, angle=0) -> "FilterChain":
        """
        方向模糊（对应 PS「动感模糊」，distance ≤ 15 效果最佳）。 / Directional blur, like Photoshop's Motion Blur; distance up to about 15 works best.

        :param distance: 模糊拖尾长度（像素）
        :param angle: 拖尾方向（度，0 = 水平向右，90 = 垂直向下）

        示例::
            pen.circle(200, 500, 40, fill_color="#2a9d8f",
                       filter=pen.fx.motion_blur(14, 0))   # 横向拖尾
        """
        distance = max(1, min(15, int(distance)))
        n = 2 * distance + 1
        rad = math.radians(angle)
        # 在 n×n 网格中沿角度方向取一条线，核值均分
        pts = set()
        for i in range(-distance, distance + 1):
            x = int(round(i * math.cos(rad))) + distance
            y = int(round(i * math.sin(rad))) + distance
            pts.add((x, y))
        v = 1.0 / len(pts)
        kernel = " ".join(
            str(v) if (c, r) in pts else "0"
            for r in range(n) for c in range(n))
        self._fe("feConvolveMatrix", {
            "order": str(n), "kernelMatrix": kernel,
            "edgeMode": "duplicate", "preserveAlpha": "false"})
        return self

    # ------------------------------------------------------------------
    # 阴影与发光（Photoshop 图层样式）
    # ------------------------------------------------------------------
    def shadow(self, dx=4, dy=4, blur=4, color="black", opacity=0.5) -> "FilterChain":
        """
        投影（对应 PS「投影 Drop Shadow」）。 / Drop shadow.

        :param dx: 水平偏移 :param dy: 垂直偏移
        :param blur: 模糊半径 :param color: 阴影颜色 :param opacity: 不透明度 0~1

        示例::
            pen.circle(500, 300, 120, fill_color="#4e79a7",
                       filter=pen.fx.shadow(6, 8, 6, "#1d3557", 0.45))
        """
        base = self._src                       # 本效果的输入，作为合成底图
        self._fe("feGaussianBlur", {"in": "SourceAlpha",
                                    "stdDeviation": blur})
        self._fe("feOffset", {"dx": dx, "dy": dy})
        self._flood_color(color, opacity, self._src)
        self._merge_over_source(under_src=True, base=base)
        return self

    def inner_shadow(self, dx=3, dy=3, blur=3, color="black", opacity=0.6) -> "FilterChain":
        """
        内阴影（对应 PS「内阴影 Inner Shadow」）。 / Inner shadow.

        示例::
            pen.rect(350, 200, 300, 200, corner_radius=16, fill_color="#f1faee",
                     filter=pen.fx.inner_shadow(5, 5, 5, "#1d3557", 0.5))
        """
        base = self._src                       # 本效果的输入，作为合成底图
        self._fe("feGaussianBlur", {"in": "SourceAlpha",
                                    "stdDeviation": blur})
        off = self._fe("feOffset", {"dx": dx, "dy": dy})
        # 内阴影 alpha = SourceAlpha - 偏移后的模糊 alpha
        self._fe("feComposite", {
            "in": "SourceAlpha", "in2": self._r(off),
            "operator": "arithmetic", "k1": 0, "k2": 1, "k3": -1, "k4": 0})
        self._flood_color(color, opacity, self._src)
        self._merge_over_source(under_src=False, base=base)
        return self

    def glow(self, blur=5, color="#ffb703", opacity=0.9) -> "FilterChain":
        """
        外发光（对应 PS「外发光 Outer Glow」）。 / Outer glow.

        示例::
            pen.text(500, 150, "GLOW", font_size=64, fill_color="#ffffff",
                     filter=pen.fx.glow(8, "#00b4d8"))
        """
        base = self._src                       # 本效果的输入，作为合成底图
        self._fe("feGaussianBlur", {"in": "SourceAlpha",
                                    "stdDeviation": blur})
        self._flood_color(color, opacity, self._src)
        self._merge_over_source(under_src=True, base=base)
        return self

    def inner_glow(self, blur=5, color="#ffd166", opacity=0.9) -> "FilterChain":
        """
        内发光（对应 PS「内发光 Inner Glow」）。 / Inner glow.

        示例::
            pen.circle(700, 400, 100, fill_color="#003049",
                       filter=pen.fx.inner_glow(8, "#ffd60a", 0.9))
        """
        base = self._src                       # 本效果的输入，作为合成底图
        self._fe("feGaussianBlur", {"in": "SourceAlpha",
                                    "stdDeviation": blur})
        edge = self._fe("feComposite", {
            "in": "SourceAlpha", "in2": self._src,
            "operator": "arithmetic", "k1": 0, "k2": 1, "k3": -1, "k4": 0})
        self._flood_color(color, opacity, self._r(edge))
        self._merge_over_source(under_src=False, base=base)
        return self

    # ------------------------------------------------------------------
    # 立体与描边（Bevel / Outline）
    # ------------------------------------------------------------------
    def bevel(self, strength=1.0, blur=2, azimuth=225, elevation=55,
              light_color="white", surface=2.5) -> "FilterChain":
        """
        浮雕斜面（对应 PS「斜面和浮雕 Bevel & Emboss」的高光部分）。 / Bevel and emboss, covering the highlight half of the Photoshop effect.

        :param strength: 高光强度（0~2） :param blur: 斜面宽度（模糊量）
        :param azimuth: 光源方位角（度，225 = 左上打光）
        :param elevation: 光源仰角（度） :param light_color: 高光颜色

        示例::
            pen.text(500, 300, "3D", font_size=96, fill_color="#e76f51",
                     filter=pen.fx.bevel(1.2, 2, 225, 55))
        """
        base = self._src                      # 先记住链当前的图，后面加高光要用
        b = self._fe("feGaussianBlur", {"in": "SourceAlpha",
                                        "stdDeviation": blur})
        spec = self._fe("feSpecularLighting", {
            "in": self._r(b),
            "surfaceScale": surface,
            "specularConstant": max(0.0, float(strength)),
            "specularExponent": 20,
            "lighting-color": _paint(light_color) or "#ffffff",
        })
        spec.add(SvgNode("feDistantLight",
                         {"azimuth": azimuth, "elevation": elevation}))
        clipped = self._fe("feComposite", {
            "in": self._r(spec), "in2": "SourceAlpha", "operator": "in"})
        # 高光加到**当前链的图上**（不是 SourceGraphic），前面叠加的效果才不会被丢掉
        self._fe("feComposite", {
            "in": base, "in2": self._r(clipped),
            "operator": "arithmetic", "k1": 0, "k2": 1, "k3": 1, "k4": 0})
        return self

    def engrave(self, depth=1.2, blur=1, dark="#3E2410", light="#FFFDF5",
                dark_opacity=0.85, light_opacity=0.9) -> "FilterChain":
        """
        雕刻凹陷（对应 PS「斜面和浮雕 Bevel & Emboss」的凹陷方向，与 bevel 相反）。 / Engrave - the opposite of bevel: the top/left inner edge goes dark and the bottom/right inner edge catches the light, so the shape reads as carved into the surface.

        光源仍按惯例来自左上，但凹槽的受光面与凸起正好相反：上/左内缘背光
        压深、下/右内缘受光提亮，眼睛就把图形读成「刻进去」的。
        想刻得深一点就加大 depth，想更锐利就减小 blur。

        :param depth: 刻痕深度（内缘偏移像素，越大刻得越深）
        :param blur: 刻痕柔和度（模糊量）
        :param dark: 上/左内缘的暗边颜色
        :param light: 下/右内缘的亮边颜色
        :param dark_opacity: 暗边不透明度 0~1
        :param light_opacity: 亮边不透明度 0~1

        示例::

            # 元素侧：直接叠一层雕刻效果
            pen.text(500, 300, "帅", font_size=48,
                     fill_color="#C23B22").fx_engrave()
            # 一步到位
            pen.text(500, 300, "帅", font_size=48,
                     filter=pen.fx.engrave())
        """
        d = max(0.1, float(depth))
        self.inner_shadow(d, d, blur, dark, dark_opacity)        # 上/左内缘压深
        self.inner_shadow(-d * 0.8, -d * 0.8, max(0.2, blur * 0.9),
                          light, light_opacity)                  # 下/右内缘提亮
        return self

    def outline(self, width=3, color="gold") -> "FilterChain":
        """
        外描边（对应 PS「描边 Stroke」图层样式，沿轮廓向外扩）。 / Outer stroke that expands outwards along the outline.

        示例::
            pen.text(500, 200, "HALO", font_size=72, fill_color="#ffffff",
                     filter=pen.fx.outline(4, "#d62828"))
        """
        base = self._src                       # 本效果的输入，作为合成底图
        self._fe("feMorphology", {
            "in": "SourceAlpha", "operator": "dilate",
            "radius": max(0.5, width / 2.0)})
        self._flood_color(color, 1.0, self._src)
        self._merge_over_source(under_src=True, base=base)
        return self

    # ------------------------------------------------------------------
    # 风格化（Stylize）
    # ------------------------------------------------------------------
    def roughen(self, scale=4, frequency=0.05, seed=None) -> "FilterChain":
        """
        粗糙化（对应 PS「扩散/粗糙化」手绘感，用湍流置换实现）。 / Roughen for a hand-drawn look, implemented with turbulence displacement.

        :param scale: 置换强度（像素） :param frequency: 噪声频率（越小纹理越大）

        示例::
            pen.heart(500, 300, 160, fill_color="#e63946",
                      filter=pen.fx.roughen(6, 0.04))
        """
        base = self._src                      # 先记住链当前的图（湍流会改 self._src）
        t = self._fe("feTurbulence", {
            "type": "fractalNoise",
            "baseFrequency": frequency, "numOctaves": 2,
            **({"seed": seed} if seed is not None else {})})
        self._fe("feDisplacementMap", {
            "in": base, "in2": self._r(t),
            "scale": scale, "xChannelSelector": "R", "yChannelSelector": "G"})
        return self

    def noise(self, opacity=0.15, mono=True, seed=None) -> "FilterChain":
        """
        噪点颗粒（对应 PS「添加杂色」，叠加在图形上）。 / Grainy noise overlaid on the shape.

        示例::
            pen.rect(300, 200, 400, 250, fill_color="#e9c46a",
                     filter=pen.fx.noise(0.2))
        """
        base = self._src                       # 本效果的输入，作为合成底图
        t = self._fe("feTurbulence", {
            "type": "fractalNoise", "baseFrequency": 0.9, "numOctaves": 2,
            **({"seed": seed} if seed is not None else {})})
        r_t = self._r(t)
        if mono:
            g = self._fe("feColorMatrix",
                         {"in": r_t, "type": "matrix", "values": _GRAY_MATRIX})
            r_t = self._r(g)
        # 压低噪声 alpha，再限制到图形内部
        a = self._fe("feComponentTransfer", {"in": r_t})
        a.add(SvgNode("feFuncA", {"type": "linear",
                                  "slope": max(0.0, min(1.0, opacity)),
                                  "intercept": 0}))
        self._fe("feComposite", {"in": self._r(a), "in2": "SourceAlpha",
                                 "operator": "in"})
        self._merge_over_source(under_src=False, base=base)
        return self

    def emboss(self, azimuth=45) -> "FilterChain":
        """
        浮雕灰度（对应 PS「风格化→浮雕效果」，输出灰度浮雕）。 / Grayscale emboss, like Photoshop's Stylize - Emboss.

        示例::
            pen.text(500, 300, "EMBOSS", font_size=80, fill_color="#adb5bd",
                     filter=pen.fx.emboss(45))
        """
        self._fe("feConvolveMatrix", {
            "order": "3",
            "kernelMatrix": "-2 -1 0 -1 1 1 0 1 2",
            "divisor": 1, "edgeMode": "duplicate", "preserveAlpha": "false"})
        self._fe("feColorMatrix", {"type": "saturate", "values": 0})
        return self

    def edge_detect(self, width=1) -> "FilterChain":
        """
        边缘检测（对应 PS「风格化→查找边缘」，输出线稿感灰度）。 / Edge detection producing line-art grayscale, like Photoshop's Find Edges.

        :param width: 线条粗细；width>1 时用 feMorphology dilate 把边缘线
                      加粗到约 width 像素（1 = 默认细线，适合细密线稿）。 /
                      Line thickness: width above 1 dilates the edge strokes to
                      roughly that many pixels; 1 keeps the default thin lines.

        示例::
            pen.star(500, 300, 140, fill_color="#fca311",
                     filter=pen.fx.edge_detect())
            pen.star(700, 300, 140, fill_color="#fca311",
                     filter=pen.fx.edge_detect(2))   # 线更粗 / thicker strokes
        """
        self._fe("feConvolveMatrix", {
            "order": "3",
            "kernelMatrix": "0 1 0 1 -4 1 0 1 0",
            "divisor": 1, "edgeMode": "duplicate", "preserveAlpha": "false"})
        if width and width > 1:
            self._fe("feMorphology", {"operator": "dilate", "radius": width})
        return self

    # ------------------------------------------------------------------
    # 颜色调整（Image → Adjustments）
    # ------------------------------------------------------------------
    def saturate(self, factor=1.2) -> "FilterChain":
        """
        饱和度（对应 PS「色相/饱和度」）：factor<1 降低，>1 提高。 / Saturation: factor below 1 reduces it, above 1 increases it.

        示例::
            pen.circle(300, 300, 100, fill_color="#e63946",
                       filter=pen.fx.saturate(1.6))
        """
        self._fe("feColorMatrix", {"type": "saturate", "values": factor})
        return self

    def hue_rotate(self, degrees=90) -> "FilterChain":
        """
        色相旋转（对应 PS「色相」滑块，整图换色系）。 / Hue rotation, shifting the whole palette like Photoshop's hue slider.

        示例::
            pen.circle(500, 300, 100, fill_color="#e63946",
                       filter=pen.fx.hue_rotate(140))   # 红变青
        """
        self._fe("feColorMatrix", {"type": "hueRotate", "values": degrees})
        return self

    def grayscale(self) -> "FilterChain":
        """去色（对应 PS「去色/黑白」）。 / Desaturate, like Photoshop's Desaturate / Black and White. 示例:: pen.image("p.jpg").set_filter(pen.fx.grayscale())"""
        self._fe("feColorMatrix", {"type": "matrix", "values": _GRAY_MATRIX})
        return self

    def sepia(self) -> "FilterChain":
        """怀旧褐色调（对应 PS「照片滤镜→褐」）。 / Warm sepia tone, like Photoshop's Photo Filter. """
        self._fe("feColorMatrix", {"type": "matrix", "values": _SEPIA_MATRIX})
        return self

    def brightness(self, factor=1.2) -> "FilterChain":
        """
        亮度（对应 PS「亮度」）：factor<1 变暗，>1 变亮。 / Brightness: factor below 1 darkens, above 1 brightens.

        示例::
            pen.rect(0, 0, 500, 300, fill_color="#457b9d",
                     filter=pen.fx.brightness(1.4))
        """
        p = self._fe("feComponentTransfer")
        for ch in ("feFuncR", "feFuncG", "feFuncB"):
            p.add(SvgNode(ch, {"type": "linear",
                               "slope": max(0.0, factor), "intercept": 0}))
        return self

    def contrast(self, factor=1.3) -> "FilterChain":
        """
        对比度（对应 PS「对比度」）：factor<1 降低，>1 提高。 / Contrast: factor below 1 reduces it, above 1 increases it.

        示例::
            pen.image("photo.jpg").set_filter(pen.fx.contrast(1.5))
        """
        p = self._fe("feComponentTransfer")
        k = max(0.0, float(factor))
        for ch in ("feFuncR", "feFuncG", "feFuncB"):
            p.add(SvgNode(ch, {"type": "linear", "slope": k,
                               "intercept": 0.5 * (1 - k)}))
        return self

    def gamma(self, r=1.0, g=1.0, b=1.0) -> "FilterChain":
        """
        伽马校正（对应 PS「曝光度/曲线」的幂次调整）：>1 提亮中间调，<1 压暗。 / Gamma correction: above 1 lifts midtones, below 1 darkens them.

        示例::
            pen.image("photo.jpg").set_filter(pen.fx.gamma(0.8, 0.9, 1.1))
        """
        p = self._fe("feComponentTransfer")
        for ch, e in zip(("feFuncR", "feFuncG", "feFuncB"), (r, g, b)):
            p.add(SvgNode(ch, {"type": "gamma", "amplitude": 1,
                               "exponent": max(0.01, e), "offset": 0}))
        return self

    def invert(self) -> "FilterChain":
        """反相（对应 PS「反相 Ctrl+I」）。 / Invert colors. """
        p = self._fe("feComponentTransfer")
        for ch in ("feFuncR", "feFuncG", "feFuncB"):
            p.add(SvgNode(ch, {"type": "table", "tableValues": "1 0"}))
        return self

    def posterize(self, levels=4) -> "FilterChain":
        """
        色调分离（对应 PS「色调分离 Posterize」）：levels 越小色块感越强。 / Posterize: fewer levels produce flatter color blocks.

        示例::
            pen.image("photo.jpg").set_filter(pen.fx.posterize(3))
        """
        vals = " ".join(
            str(round(i / max(1, levels - 1), 3)) for i in range(levels))
        p = self._fe("feComponentTransfer")
        for ch in ("feFuncR", "feFuncG", "feFuncB"):
            p.add(SvgNode(ch, {"type": "discrete", "tableValues": vals}))
        return self

    def color_overlay(self, color="red", opacity=0.8) -> "FilterChain":
        """
        颜色叠加（对应 PS「颜色叠加 Color Overlay」）。 / Color overlay.

        示例::
            pen.polygon([(400, 200), (600, 200), (500, 380)],
                        fill_color="#118ab2",
                        filter=pen.fx.color_overlay("#073b4c", 0.7))
        """
        base = self._src                       # 本效果的输入，作为合成底图
        self._flood_color(color, opacity, "SourceAlpha")
        self._merge_over_source(under_src=False, base=base)
        return self

    # ------------------------------------------------------------------
    # 自定义原语（扩展口）
    # ------------------------------------------------------------------
    def custom(self, tag, **attribs) -> "FilterChain":
        """
        追加任意 SVG 滤镜原语（保留扩展能力，如 feBlend / feTile 等）。 / Append any raw SVG filter primitive, such as feBlend or feTile, so the chain stays extensible.

        :param tag: 原语标签名（如 "feBlend"） :param attribs: 原语属性

        示例::
            f = pen.fx.chain().blur(2)
            f.custom("feBlend", mode="screen", in2="SourceGraphic")
        """
        self._fe(tag, attribs)
        return self
