# -*- coding: utf-8 -*-
"""
元素基类与共享辅助函数（所有元素的公共能力）。 / The Element base class and the helpers shared by every element.

- `_paint`     颜色参数归一化
- `_fmt_points` 顶点列表格式化
- `_fmt_transform` 变换列表格式化
- `_num`       属性值转 float（容忍 "120px" 这类写法）
- `Element`    所有元素的基类：样式/变换/动画/层级/克隆/包围盒
"""


# ---------------------------------------------------------------------------
# 直接运行引导：在 PyCharm 里点绿色三角运行本文件（或命令行 python 本文件路径）时，
# 相对导入需要包上下文，这里自动补上项目根路径与包名。
# 正常 `import malight.xxx` 时这段不会执行，对包本身零影响。
# ---------------------------------------------------------------------------
if __name__ == "__main__" and not __package__:
    import os as _os
    import sys as _sys
    _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.dirname(
        _os.path.abspath(__file__)))))
    __package__ = "malight.elements"

import inspect
import re
from typing import Generic, Optional, Tuple, TypeVar
from ..svg_backend import SvgNode, fmt_num
from ..definitions import (Color, StrokeCap, StrokeJoin, TextHAlign, TextVAlign,
                           value_of)
from ..i18n import t


def _num(value, default=None):
    """
    把属性值转成 float（内部辅助）。

    :param value: 属性原值（可能是 str / int / float / None）
    :param default: 无法解析时返回的默认值
    :return: float 或 default

    容忍带单位的写法：``"120px"`` -> 120.0、``" 0.5 "`` -> 0.5；
    空串、None、``"auto"`` 这类无法解析的值返回 default。

    示例::
        _num("120px")      # 120.0
        _num(None, 0.0)    # 0.0
        _num("auto")       # None
    """
    if value is None or value == "":
        return default
    if isinstance(value, (int, float)):
        return float(value)
    m = re.match(r"\s*(-?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?)", str(value))
    return float(m.group(1)) if m else default


def _paint(value):
    """
    颜色参数归一化：具名颜色转十六进制；url(#id)/none/#hex 原样保留。

    :param value: 颜色串（中/英文名、#hex、url(#id)、none）
    :return: SVG 可用的 paint 值

    示例::
        _paint("红色")            # "#ff0000"
        _paint("url(#grad1)")    # "url(#grad1)"
    """
    if value is None:
        return None
    if isinstance(value, (tuple, list)):
        return Color.RGB(*value)
    s = str(value)
    if s.startswith("url(") or s.startswith("#") or s == "none" or s == "":
        return s
    return Color.hex_of(s)


def _fmt_points(points):
    """
    顶点列表 -> "x,y x,y ..." 字符串（polyline/polygon 用）。

    示例::
        _fmt_points([(10, 20), (30, 40)])   # "10,20 30,40"
    """
    return " ".join(f"{fmt_num(x)},{fmt_num(y)}" for x, y in points)


def _fmt_transform(items):
    """
    变换列表 -> transform 属性字符串。

    示例::
        _fmt_transform(["translate(10,20)", "rotate(45,100,100)"])
        # "translate(10,20) rotate(45,100,100)"
    """
    return " ".join(items)


# 方法链的 self 类型变量（PEP 484 的 self-type 写法）。
#
# 返回 self 的方法标注 `-> _Self`，并给首个参数补 `self: _Self`。
# Element 本身写成 `Generic[_Self]`，每个子类声明成
# `class PathElement(Element["PathElement"])` —— 于是
# `pen.path(...).move_to(...).set_opacity(...)` 在 IDE 里一路都是
# PathElement，点号后面补出来的是子类自己的方法，而不是全在 Element 上。
# （英文版修正：只写 `-> _Self` 而没有泛型实参时，PyCharm 只按上界
# Element 推导，链式补全拿不到子类方法。子类自己的方法另有更直接的
# 写法：直接标 `-> "PathElement"`，不依赖任何推导。）
_Self = TypeVar("_Self", bound="Element")


# 绘图板方法把「签名之外的参数」统一收进 extra 字典传下来。
# 其中下面这些键有对应的标准参数名，必须先并回 kwargs 按规范处理，
# 否则会被当成裸属性写成 stroke-cap / fill-rule 之类的非法名。
_EXTRA_AS_PARAM = {
    "opacity", "fill_opacity", "stroke_opacity", "class_name", "style_str",
    "vector_effect", "blend_mode", "filter", "paint_order",
    "fill_color", "stroke_color", "stroke_width", "stroke_style",
    "dash_offset", "stroke_cap", "stroke_join", "fill_rule",
}

# 裸属性键 -> 规范 SVG 属性名（写 `extra={"stroke_cap": ...}` 时也能正确落位）
_ATTR_ALIAS = {
    "stroke_cap": "stroke-linecap",
    "stroke_join": "stroke-linejoin",
    "stroke_style": "stroke-dasharray",
    "dash_offset": "stroke-dashoffset",
    "fill_rule": "fill-rule",
    "fill_opacity": "fill-opacity",
    "stroke_opacity": "stroke-opacity",
    "class_name": "class",
    "style_str": "style",
    "vector_effect": "vector-effect",
    "text_length": "textLength",
    "length_adjust": "lengthAdjust",
}


class Element(Generic[_Self]):
    """
    所有元素的基类（对应中文版 `元素`）。 / Base class of every element.

    封装了样式、变换、动画、层级、克隆等公共能力。
    子类需实现 ``_update_attrs(**kwargs)`` 与可选的 ``bbox()``。

    示例（通常通过绘图板创建）::
        pen = MagicPen("e", width=400, height=300)
        el = pen.circle(200, 150, 80, fill_color="steelblue")
        el.set_opacity(0.6)            # 透明度
        el.translate(20, 0)            # 平移
        el.bring_to_front()            # 置顶
    """

    _id_counter = 0   # 全局自增 ID（用于未显式指定 id 的元素）
    _attr_params = frozenset()   # 本类 _update_attrs 的参数名（子类自动覆盖）

    # 所有元素都支持的「公共样式参数」：只要 _update_attrs 带 **kw，这些参数就能
    # 用 set_<参数> / get_<参数> 再设置/读取（与 _apply_common / _apply_paint
    # 实际处理的键保持一致）。它们的访问器就写在本类下方（显式方法，IDE 可见），
    # 唯一例外是混合模式：写进 style 里读不回来，只有 set_blend_mode。
    _COMMON_ATTR_PARAMS = frozenset(
        "opacity fill_opacity stroke_opacity class_name style_str "
        "vector_effect blend_mode filter paint_order "
        "fill_color stroke_color stroke_width stroke_style dash_offset "
        "stroke_cap stroke_join fill_rule".split())

    def __init_subclass__(cls, **kw):
        """
        自动包装子类的 ``_update_attrs``，记录每次写入时「完整生效的参数」。

        这样 ``update(**kw)`` 就能用「上次生效参数 + 本次改动」重放，
        实现真正的局部更新（未改的属性不变）。

        正常使用无需关心本方法，它是 update() 的实现基础。
        """
        super().__init_subclass__(**kw)
        fn = cls.__dict__.get("_update_attrs")
        if fn is None:
            return
        sig = inspect.signature(fn)
        # 记下本类可用的参数名，供动态 set_<参数> / get_<参数> 方法校验；
        # 带 **kw 的类再把公共样式参数并进来（update() 会照常落到公共处理）
        params = frozenset(sig.parameters) - {"self"}
        if "kw" in params:
            params = (params - {"kw"}) | Element._COMMON_ATTR_PARAMS
        cls._attr_params = params

        def _wrapped(self, **kwargs):
            try:
                bound = sig.bind(self, **kwargs)
                bound.apply_defaults()
            except TypeError:
                # 签名不匹配（例如缺必填参数）时照常抛错，只是不记录参数
                fn(self, **kwargs)
                return
            stored = {k: v for k, v in bound.arguments.items() if k != "self"}
            tail = stored.pop("kw", None)      # 签名里的 **kw 展开
            if tail:
                stored.update(tail)
            self._attrs_args = stored
            fn(self, **kwargs)

        _wrapped.__name__ = "_update_attrs"
        _wrapped.__doc__ = fn.__doc__
        _wrapped.__qualname__ = cls.__qualname__ + "._update_attrs"
        cls._update_attrs = _wrapped

    def __init__(self, board, parent=None, tag="g"):
        """
        :param board: 所属 MagicPen 绘图板
        :param parent: 父节点（SvgNode 或 GroupElement）；None 表示画布根
        :param tag: SVG 标签名
        """
        self.board = board
        self.tag = tag
        # 确定父容器：GroupElement 取其节点，SvgNode 直接用
        if parent is None:
            parent = board.canvas_node
        elif isinstance(parent, Element):
            parent = parent.node
        self.parent_node = parent
        self.node = SvgNode(tag)
        self.node.element = self    # 反向引用：便于由节点找回元素（如统计组内元素）
        parent.add(self.node)   # 关键：把元素节点挂到父容器（缺失会导致画布为空）
        self._transform_items = []
        self._dash_items = None

    # ---------------------------------------------------------------
    # ID 管理
    # ---------------------------------------------------------------
    @classmethod
    def _next_id(cls, prefix) -> str:
        """生成全局唯一自增 id，如 "circle_3"。"""
        cls._id_counter += 1
        return f"{prefix}_{cls._id_counter}"

    # ---------------------------------------------------------------
    # set_<参数> / get_<参数> 兜底（创建后逐项再设置/读取）
    # ---------------------------------------------------------------
    # 元素专属参数的访问器由 tools/gen_attr_accessors.py 写进各元素类体，
    # 公共样式参数的在下面手写 —— 都是真实方法，IDE 能补全、拼错会报错。
    # 本兜底只服务「直接以参数名调用」那一形式（t.font_size(36)）：它没法
    # 显式展开，因为像 EllipseElement.rotate 这种参数名与 Element.rotate()
    # 撞名。
    # 参数名 -> SVG 属性名的对照（get_* 读取节点属性时用；没列出的按
    # 「下划线转连字符」猜测，如 letter_spacing -> letter-spacing）
    _GET_ATTR_ALIASES = {
        "fill_color": "fill", "stroke_color": "stroke",
        "font": "font-family", "h_align": "text-anchor",
        "v_align": "alignment-baseline", "char_rotate": "rotate",
        "id_": "id", "text_length": "textLength",
        "length_adjust": "lengthAdjust", "stroke_style": "stroke-dasharray",
        "dash_offset": "stroke-dashoffset", "stroke_cap": "stroke-linecap",
        "stroke_join": "stroke-linejoin", "fill_rule": "fill-rule",
        "class_name": "class", "style_str": "style",
        "vector_effect": "vector-effect", "radius": "r",
        "paint_order": "paint-order", "corner_radius": "rx",
        # 文字类参数：读回的是它们真正落到的 SVG 属性
        "bold": "font-weight", "weight": "font-weight",
        "italic": "font-style",
        "underline": "text-decoration", "decoration": "text-decoration",
    }

    def __getattr__(self, name):
        """
        兜底合成元素级「再设置 / 读取」方法（三种写法都支持）：

        1. ``set_<参数>(值)``  —— 链式改值（``t.set_font_size(36)``）
        2. ``get_<参数>()``    —— 读当前属性原值（``t.get_font_size()``）
        3. 直接以参数名调用    —— 无参读值、带参改值（可链式）：
           ``t.font_size()`` 读、``t.font_size(36)`` 改并返回 self

        ``set_`` / ``get_`` 这两种**已经是真实方法**，不再靠这里：元素专属参数
        的访问器由 ``tools/gen_attr_accessors.py`` 写在各元素类体内，公共样式
        的在下面手写 —— 都是显式方法，PyCharm 能补全、拼错会报错。
        （用户报过「动态合成的成员 IDE 看不见」；动态写入的成员静态分析不认。）

        因此本方法现在只负责第 3 种写法：像 ``EllipseElement.rotate`` 这种
        参数名与 ``Element.rotate()`` 撞名的没法显式展开，只能留在这里兜底；
        拼错的参数名当场 AttributeError，不会被静默吞掉。

        Fallback synthesis for post-creation accessors. The ``set_`` / ``get_``
        forms are now real methods (element-specific ones generated into each
        class body, common style ones written out below); only the bare
        parameter-name form still goes through this hook.

        示例 / Example::

            t = pen.text(100, 100, "Hi", font_size=20)
            t.set_font_size(36).set_fill_color("teal")      # 真实方法 / real method
            t.font_size(36)                                 # 走本兜底 / via this hook
            t.get_font_size()      # -> 36
            t.font_size()          # -> 36（无参读值）
        """
        if name.startswith("set_") or name.startswith("get_"):
            param = name[4:]
            if param in type(self)._attr_params:
                if name.startswith("set_"):
                    def _setter(value):
                        """update(参数=值) 的链式包装 / chainable wrapper of update()."""
                        return self.update(**{param: value})
                    _setter.__name__ = name
                    _setter.__qualname__ = \
                        type(self).__qualname__ + "." + name
                    return _setter

                def _getter():
                    """读取当前属性原值 / read the current raw attribute value."""
                    return self._get_attr_value(param)
                _getter.__name__ = name
                _getter.__qualname__ = type(self).__qualname__ + "." + name
                return _getter
        if name in type(self)._attr_params:
            def _accessor(*args):
                """无参读值、带参改值（可链式）/ no-arg reads, one-arg sets (chainable)."""
                if not args:
                    return self._get_attr_value(name)
                if len(args) > 1:
                    raise TypeError(t("err.attr_one_arg", name=name))
                return self.update(**{name: args[0]})
            _accessor.__name__ = name
            _accessor.__qualname__ = type(self).__qualname__ + "." + name
            return _accessor
        raise AttributeError(t("err.attr_no_dynamic", name=name,
                               cls=type(self).__name__))

    def _get_attr_value(self, param):
        """
        读取参数对应的当前 SVG 属性值（内部方法）。 / Read the current raw SVG attribute for a parameter (internal).

        ``text`` 返回文字内容本身；其余按参数名查节点属性，查不到返回 None。
        写进 CSS style 的属性（如混合模式）不在这里，读不到属预期。
        """
        if param == "text":
            return self.node.text
        attr = self._GET_ATTR_ALIASES.get(param, param.replace("_", "-"))
        return self.node.attribs.get(attr)

    # ---------------------------------------------------------------
    # 公共样式参数的显式访问器
    # ---------------------------------------------------------------
    # 下面这些 set_<参数> / get_<参数> 与 __getattr__ 兜底合成的版本行为完全
    # 一致，写成显式方法是因为 IDE 只能补全源码里真实存在的方法（动态写入的
    # 成员静态分析看不见）。元素专属参数的同名访问器在各元素类体里，由
    # tools/gen_attr_accessors.py 生成。
    # These accessors behave exactly like the ones the __getattr__ fallback
    # synthesizes; they are spelled out so IDEs can autocomplete them.
    # Element-specific ones live in each element class, generated by
    # tools/gen_attr_accessors.py.

    def set_opacity(self: _Self, value) -> _Self:
        """设置整体不透明度（0-1）。 / Set the overall opacity (0-1).

        示例 / Example::
            el.set_opacity(0.6)
        """
        return self.update(opacity=value)

    def get_opacity(self) -> object:
        """读取不透明度的当前属性值（没设置过返回 None）。 / Read the current raw opacity attribute (None if never set)."""
        return self._get_attr_value("opacity")

    def set_fill_opacity(self: _Self, value) -> _Self:
        """设置填充不透明度。 / Set the fill opacity.

        示例 / Example::
            el.set_fill_opacity(0.3)
        """
        return self.update(fill_opacity=value)

    def get_fill_opacity(self) -> object:
        """读取填充不透明度的当前属性值。 / Read the current raw fill-opacity attribute."""
        return self._get_attr_value("fill_opacity")

    def set_stroke_opacity(self: _Self, value) -> _Self:
        """设置描边不透明度。 / Set the stroke opacity.

        示例 / Example::
            el.set_stroke_opacity(0.5)
        """
        return self.update(stroke_opacity=value)

    def get_stroke_opacity(self) -> object:
        """读取描边不透明度的当前属性值。 / Read the current raw stroke-opacity attribute."""
        return self._get_attr_value("stroke_opacity")

    def set_fill_color(self: _Self, color) -> _Self:
        """设置填充色（支持 ColorName、#RRGGBB、渐变引用）；传 None 去掉填充。 / Set the fill colour (ColorName, #RRGGBB or a gradient reference); None removes the fill.

        示例 / Example::
            el.set_fill_color(ColorName.CHOCOLATE)
        """
        if color is None:
            self.node.set("fill", None)
        return self.update(fill_color=color)

    def get_fill_color(self) -> object:
        """读取填充色的当前属性值。 / Read the current raw fill attribute."""
        return self._get_attr_value("fill_color")

    def set_stroke_color(self: _Self, color) -> _Self:
        """设置描边色；传 None 去掉描边。 / Set the stroke colour; None removes the stroke.

        示例 / Example::
            el.set_stroke_color(ColorName.ORANGERED)
        """
        if color is None:
            self.node.set("stroke", None)
        return self.update(stroke_color=color)

    def get_stroke_color(self) -> object:
        """读取描边色的当前属性值。 / Read the current raw stroke attribute."""
        return self._get_attr_value("stroke_color")

    def set_stroke_width(self: _Self, width) -> _Self:
        """设置描边宽度；传 None 去掉描边宽度。 / Set the stroke width; None removes it.

        示例 / Example::
            el.set_stroke_width(3)
        """
        if width is None:
            self.node.set("stroke-width", None)
        return self.update(stroke_width=width)

    def get_stroke_width(self) -> object:
        """读取描边宽度的当前属性值。 / Read the current raw stroke-width attribute."""
        return self._get_attr_value("stroke_width")

    def set_stroke_style(self: _Self, dash) -> _Self:
        """设置描边虚线样式（如 "6,3"）。 / Set the dash pattern, e.g. "6,3".

        示例 / Example::
            el.set_stroke_style("6,3")
        """
        return self.update(stroke_style=dash)

    def get_stroke_style(self) -> object:
        """读取虚线样式的当前属性值。 / Read the current raw stroke-dasharray attribute."""
        return self._get_attr_value("stroke_style")

    def set_dash_offset(self: _Self, offset) -> _Self:
        """设置虚线起始偏移（配合虚线做流动效果）。 / Set the dash offset (animate a dashed line by shifting it).

        示例 / Example::
            el.set_dash_offset(4)
        """
        return self.update(dash_offset=offset)

    def get_dash_offset(self) -> object:
        """读取虚线偏移的当前属性值。 / Read the current raw stroke-dashoffset attribute."""
        return self._get_attr_value("dash_offset")

    def set_stroke_cap(self: _Self, cap) -> _Self:
        """设置线端样式（butt / round / square）。 / Set the line cap (butt, round or square).

        示例 / Example::
            el.set_stroke_cap("round")
        """
        return self.update(stroke_cap=cap)

    def get_stroke_cap(self) -> object:
        """读取线端样式的当前属性值。 / Read the current raw stroke-linecap attribute."""
        return self._get_attr_value("stroke_cap")

    def set_stroke_join(self: _Self, join) -> _Self:
        """设置转折样式（miter / round / bevel）。 / Set the line join (miter, round or bevel).

        示例 / Example::
            el.set_stroke_join("round")
        """
        return self.update(stroke_join=join)

    def get_stroke_join(self) -> object:
        """读取转折样式的当前属性值。 / Read the current raw stroke-linejoin attribute."""
        return self._get_attr_value("stroke_join")

    def set_fill_rule(self: _Self, rule) -> _Self:
        """设置填充规则（evenodd 可给重叠路径挖洞）。 / Set the fill rule; evenodd punches holes in overlapping paths.

        示例 / Example::
            el.set_fill_rule(FillRule.EVENODD)
        """
        return self.update(fill_rule=rule)

    def get_fill_rule(self) -> object:
        """读取填充规则的当前属性值。 / Read the current raw fill-rule attribute."""
        return self._get_attr_value("fill_rule")

    def set_blend_mode(self: _Self, mode) -> _Self:
        """设置混合模式（写进 CSS style）。 / Set the blend mode (written into the CSS style).

        没有对应的 ``get_blend_mode``：混合模式落在 style 里，节点属性读不回来，
        要读回请用 ``get_style_str()`` 或看 ``node.attribs["style"]``。
        There is no ``get_blend_mode`` on purpose: the blend mode lives in the style
        attribute, so it cannot be read back as a node attribute.

        示例 / Example::
            el.set_blend_mode(BlendMode.MULTIPLY)
        """
        return self.update(blend_mode=mode)

    def set_paint_order(self: _Self, order) -> _Self:
        """设置绘制顺序，``PaintOrder.STROKE`` 表示先描边后填充（空心字必备）。 / Set the paint order; ``PaintOrder.STROKE`` draws the stroke first, which outlined/hollow text needs.

        示例 / Example::
            pen.text(60, 80, "标题", stroke_color="red", stroke_width=4,
                     paint_order=PaintOrder.STROKE)
        """
        return self.update(paint_order=order)

    def get_paint_order(self) -> object:
        """读取绘制顺序的当前属性值。 / Read the current raw paint-order attribute."""
        return self._get_attr_value("paint_order")

    def set_vector_effect(self: _Self, effect) -> _Self:
        """设置矢量效果（non-scaling-stroke = 缩放时线宽不变）。 / Set the vector effect; non-scaling-stroke keeps the stroke width when scaled.

        示例 / Example::
            el.set_vector_effect("non-scaling-stroke")
        """
        return self.update(vector_effect=effect)

    def get_vector_effect(self) -> object:
        """读取矢量效果的当前属性值。 / Read the current raw vector-effect attribute."""
        return self._get_attr_value("vector_effect")

    def set_class_name(self: _Self, name) -> _Self:
        """设置 CSS 类名（配合样式表做分类样式）。 / Set the CSS class name.

        示例 / Example::
            el.set_class_name("card-title")
        """
        return self.update(class_name=name)

    def get_class_name(self) -> object:
        """读取 CSS 类名的当前属性值。 / Read the current raw class attribute."""
        return self._get_attr_value("class_name")

    def set_style_str(self: _Self, style) -> _Self:
        """直接设置内联 CSS。 / Set the inline CSS style string.

        示例 / Example::
            el.set_style_str("mix-blend-mode:multiply")
        """
        return self.update(style_str=style)

    def get_style_str(self) -> object:
        """读取内联 CSS 的当前属性值。 / Read the current raw style attribute."""
        return self._get_attr_value("style_str")

    def set_id(self: _Self, id_) -> _Self:
        """
        设置元素 id（可用于 get_element(id) 反查）。 / Set the element id, which get_element(id) can look up later.

        示例::
            el = pen.circle(10, 10, 5, id_="sun")
            pen.get_element("sun") is el   # True
        """
        if id_:
            self.node.set("id", id_)
            if self.board is not None:
                self.board._registry[id_] = self
        return self

    # ---------------------------------------------------------------
    # 样式设置（公共属性，所有元素通用）
    # ---------------------------------------------------------------
    def _apply_common(self, kw):
        """
        应用公共样式属性（从 kwargs 中取出并写入节点）。

        支持的键（全部可选）:
            id_, opacity, fill_opacity, stroke_opacity, class_name, style_str,
            transform, vector_effect, blend_mode(混合模式), filter(滤镜),
            extra(任意 SVG 属性字典)

        子类在 ``_update_attrs`` 中先调用本方法。

        关于 extra（重要）:
            绘图板方法会把「签名里没有的参数」塞进 extra 传下来，例如
            ``pen.circle(..., stroke_cap=StrokeCap.ROUND)``。本方法会把
            extra 中属于已知参数的键并回 kwargs，按标准属性名处理；
            剩下的才作为裸 SVG 属性写入（并做下划线转连字符）。
        """
        # 1) 拆开 extra：已知参数并回 kwargs，其余留作裸属性
        raw_extra = kw.pop("extra", None) or {}
        plain_extra = {}
        for key, val in raw_extra.items():
            if key in _EXTRA_AS_PARAM:
                # 显式传参优先：只有对应参数为空时才用 extra 里的值
                if kw.get(key) is None:
                    kw[key] = val
            else:
                plain_extra[key] = val

        # 2) 常规公共属性
        if kw.get("id_"):
            self.set_id(kw.pop("id_"))
        else:
            kw.pop("id_", None)
        if kw.get("opacity") is not None:
            self.node.set("opacity", kw.pop("opacity"))
        else:
            kw.pop("opacity", None)
        if kw.get("fill_opacity") is not None:      # 英文版新增：填充透明度
            self.node.set("fill-opacity", kw.pop("fill_opacity"))
        else:
            kw.pop("fill_opacity", None)
        if kw.get("stroke_opacity") is not None:    # 英文版新增：描边透明度
            self.node.set("stroke-opacity", kw.pop("stroke_opacity"))
        else:
            kw.pop("stroke_opacity", None)
        if kw.get("class_name") is not None:
            self.node.set("class", kw.pop("class_name"))
        else:
            kw.pop("class_name", None)
        if kw.get("style_str") is not None:
            self.node.set("style", kw.pop("style_str"))
        else:
            kw.pop("style_str", None)
        if kw.get("vector_effect") is not None:
            self.node.set("vector-effect", value_of(kw.pop("vector_effect")))
        else:
            kw.pop("vector_effect", None)
        # 混合模式（英文版新增）：blend_mode=BlendMode.MULTIPLY 或 "multiply"
        bm = kw.pop("blend_mode", None)
        if bm is not None:
            self._add_style("mix-blend-mode", value_of(bm))
        # 滤镜（英文版新增）：filter=pen.fx.shadow(...) 或 "url(#id)"
        if kw.get("filter") is not None:
            self.set_filter(kw.pop("filter"))
        else:
            kw.pop("filter", None)
        # 任意属性透传（英文版新增）：extra={"data-name": "x"}
        # 注意：blend_mode / mix-blend-mode 是纯 CSS 属性，必须写进 style 才生效
        for key, val in plain_extra.items():
            name = _ATTR_ALIAS.get(key, key.replace("_", "-"))
            if name in ("blend-mode", "mix-blend-mode"):
                self._add_style("mix-blend-mode", value_of(val))
                continue
            self.node.set(name, value_of(val))

    def _add_style(self, prop, value):
        """
        往元素的 style 属性里追加一条 CSS 声明（内部方法）。

        示例（内部）::
            el._add_style("mix-blend-mode", "multiply")
        """
        if value is None:
            return self
        old = self.node.attribs.get("style") or ""
        pair = f"{prop}:{value}"
        if pair not in old:
            self.node.set("style", (old + ";" + pair).strip(";"))
        return self

    def _font_family(self, font):
        """
        字体参数归一化（内部方法，配合 malight.fonts）。

        支持三种写法（可混用）：

        1. 字体枚举 ``Font.SIMHEI``
        2. 字体名字符串 ``"Microsoft YaHei"``
        3. 字体文件路径 ``r"C:\\Windows\\Fonts\\simkai.ttf"``
           —— 自动内嵌为 @font-face，换电脑不掉字体。默认只内嵌画面上
           **实际用到的字**（自动子集化，几 KB 级别）；想整份内嵌或只引用
           本地路径，用 ``pen.set_embed(fonts=FontEmbed.EMBED / LINK)``。

        :return: 可写入 font-family 的字体名；未指定时返回 None
        """
        from ..fonts import Font
        if font is None:
            return None
        v = value_of(font)
        if not v:
            return None
        v = str(v)
        if Font.is_font_file(v):
            board = self.board
            if board is not None and hasattr(board, "style"):
                return board.style.add_font_face(v)
            return None
        return v

    def set_filter(self: _Self, f, merge=True) -> _Self:
        """
        给元素绑定滤镜，**多次调用会叠加而不是覆盖**（英文版新增，配合 pen.fx 滤镜工厂）。 / Attach a filter; calling it again stacks the new effects instead of overwriting the old ones.

        :param f: FilterChain 对象 / 滤镜 id 字符串 / "url(#id)" / None（清除）
        :param merge: True（默认）把新链的效果并进元素已有的链；False 表示整条替换

        SVG 一个元素只能带一个 ``filter`` 属性，所以「叠加」的做法是把新效果
        合并进原有那条 ``<filter>`` 里：先前的效果仍然是链的前半段，
        新效果接在后面作用于它的输出。

        示例::

            el = pen.circle(500, 300, 120, fill_color="#e63946")
            el.set_filter(pen.fx.shadow(6, 8, 6))       # 投影
            el.set_filter(pen.fx.saturate(0.4))         # 再叠一层去色（投影还在）
            el.set_filter(pen.fx.glow(8), merge=False)  # 只留发光
            el.set_filter(None)                         # 清除滤镜（整条）

        说明：同一条链被多个元素共用时（例如 ``clone()`` 出来的副本），
        叠加前会先自动复制一份专属于本元素的链，不会串改到其他元素。
        """
        if f is None:
            self.node.set("filter", None)
            return self
        # 字符串 / "url(#id)" 形式：维持「直接替换」的老行为
        url = getattr(f, "url", None)
        if not callable(url) or not merge:
            val = url() if callable(url) else str(f)
            if not val.startswith("url(") and val != "none":
                val = f"url(#{val})"
            self.node.set("filter", val)
            return self
        # FilterChain：与元素已有的链合并
        from ..board.fx import count_refs          # 延迟导入，避免与 board 循环依赖
        if getattr(f, "board", None) is not None and f.board is not self.board:
            raise ValueError(t("err.fx_other_board"))
        cur = self._current_filter_chain()
        if cur is not None and cur is not f:
            if count_refs(self.board, cur) > 1:
                cur = cur.clone()                  # 被多个元素共用 → 先私有化
            cur.merge_from(f)
            self.node.set("filter", cur.url())
            if count_refs(self.board, f) == 0:     # 临时链没人引用 → 回收其 <filter>
                f.dispose()
            return self
        self.node.set("filter", f.url())
        return self

    def get_filter(self) -> object:
        """读取滤镜属性的当前值（如 ``"url(#fx_1)"``；没滤镜返回 None）。 / Read the current raw filter attribute, such as ``"url(#fx_1)"``; None when there is no filter."""
        return self._get_attr_value("filter")

    def _current_filter_chain(self):
        """
        由元素当前的 ``filter`` 属性反查回它所属的滤镜链（内部方法）。 / Resolve the chain that the element's current filter attribute points at (internal).

        :return: FilterChain 或 None（没有滤镜 / 不是本画板登记的链）

        之所以要反查而不是记在实例上：``clone()`` 出来的副本、以及手工写
        ``filter="url(#fx_3)"`` 的元素，仍然能正确地往上续接效果。
        """
        board = self.board
        if board is None:
            return None
        chains = getattr(board, "_filter_chains", None)
        if not chains:
            return None
        val = str(self.node.attribs.get("filter") or "")
        m = re.fullmatch(r"url\(#(.+)\)", val)
        return chains.get(m.group(1)) if m else None

    # ---------------------------------------------------------------
    # 滤镜叠加：fx_* 快捷方法（等价 pen.fx.xxx(...)，并自动叠加到已有滤镜之后）
    # ---------------------------------------------------------------
    def _fx(self: _Self, name, *args, **kwargs) -> _Self:
        """
        调用 pen.fx 上的某个效果并叠加到本元素已有滤镜之后（内部方法）。 / Call one effect from pen.fx and stack it after the element's existing filter (internal).

        :param name: 效果名（见 malight/board/filters.py，如 "blur" / "emboss"）
        :param args: 透传给该效果的位置参数
        :param kwargs: 透传给该效果的关键字参数
        :return: self
        """
        if name == "custom":                     # 自定义原语：直接往链上追加
            self.fx_chain().custom(*args, **kwargs)
            return self
        factory = getattr(getattr(self.board, "fx", None), name, None)
        if name == "chain" or not callable(factory):
            raise AttributeError(t("err.fx_unknown", name=name))
        self.set_filter(factory(*args, **kwargs))
        return self

    def fx_chain(self, pad=0.4) -> "object":
        """
        取出本元素绑定的滤镜链，没有就新建一条并绑定（返回 FilterChain）。 / Return the chain bound to this element, creating and binding a new one when there is none.

        :param pad: 新建链时滤镜作用区域的外扩比例
        :return: FilterChain（可继续 .blur().shadow() 链式调用）

        注：返回类型只能标成 object —— FilterChain 在 malight/board/fx.py，
        与元素基类相互引用，标注真实类名会让 ``typing.get_type_hints`` 求值失败。

        示例::

            el.fx_chain().blur(2).saturate(1.4)
        """
        chain = self._current_filter_chain()
        if chain is None:
            from ..board.fx import FilterChain
            chain = FilterChain(self.board, pad=pad)
            self.set_filter(chain)
        return chain

    def fx(self: _Self, name, *args, **kwargs) -> _Self:
        """
        按名字叠加任意滤镜效果（通用入口）。 / Stack any filter effect by name; the generic entry point.

        :param name: 效果名（"blur" / "shadow" / "emboss" ...）
        :param args: 效果参数 :param kwargs: 效果参数

        示例::

            el.fx("blur", 3)                            # 等价 el.fx_blur(3)
            el.fx("custom", "feBlend", mode="screen")   # 追加自定义 SVG 原语
        """
        return self._fx(name, *args, **kwargs)

    def fx_blur(self: _Self, std_deviation=3) -> _Self:
        """叠加高斯模糊（等价 pen.fx.blur）。 / Stack a Gaussian blur; same as pen.fx.blur. """
        return self._fx("blur", std_deviation=std_deviation)

    def fx_sharpen(self: _Self, amount=0.5) -> _Self:
        """叠加锐化（等价 pen.fx.sharpen）。 / Stack a sharpen pass; same as pen.fx.sharpen. """
        return self._fx("sharpen", amount=amount)

    def fx_motion_blur(self: _Self, distance=10, angle=0) -> _Self:
        """叠加动感模糊（等价 pen.fx.motion_blur）。 / Stack a motion blur; same as pen.fx.motion_blur. """
        return self._fx("motion_blur", distance=distance, angle=angle)

    def fx_shadow(self: _Self, dx=4, dy=4, blur=4, color="black", opacity=0.5) -> _Self:
        """叠加投影（等价 pen.fx.shadow）。 / Stack a drop shadow; same as pen.fx.shadow. """
        return self._fx("shadow", dx=dx, dy=dy, blur=blur,
                        color=color, opacity=opacity)

    def fx_drop_shadow(self: _Self, dx=3, dy=3, std_deviation=3, opacity=0.5) -> _Self:
        """叠加投影（旧参数名版本，等价 pen.fx.drop_shadow）。 / Stack a drop shadow with the older parameter names; same as pen.fx.drop_shadow. """
        return self._fx("drop_shadow", dx=dx, dy=dy,
                        std_deviation=std_deviation, opacity=opacity)

    def fx_inner_shadow(self: _Self, dx=3, dy=3, blur=3, color="black", opacity=0.6) -> _Self:
        """叠加内阴影（等价 pen.fx.inner_shadow）。 / Stack an inner shadow; same as pen.fx.inner_shadow. """
        return self._fx("inner_shadow", dx=dx, dy=dy, blur=blur,
                        color=color, opacity=opacity)

    def fx_glow(self: _Self, std_deviation=4, color="#ffb703", opacity=0.9) -> _Self:
        """叠加外发光（等价 pen.fx.glow）。 / Stack an outer glow; same as pen.fx.glow. """
        return self._fx("glow", std_deviation=std_deviation,
                        color=color, opacity=opacity)

    def fx_inner_glow(self: _Self, blur=5, color="#ffd166", opacity=0.9) -> _Self:
        """叠加内发光（等价 pen.fx.inner_glow）。 / Stack an inner glow; same as pen.fx.inner_glow. """
        return self._fx("inner_glow", blur=blur, color=color, opacity=opacity)

    def fx_bevel(self: _Self, strength=1.0, blur=2, azimuth=225, elevation=55) -> _Self:
        """叠加斜面浮雕高光（等价 pen.fx.bevel）。 / Stack a bevel highlight; same as pen.fx.bevel. """
        return self._fx("bevel", strength=strength, blur=blur,
                        azimuth=azimuth, elevation=elevation)

    def fx_engrave(self: _Self, depth=1.2, blur=1, dark="#3E2410",
                   light="#FFFDF5") -> _Self:
        """叠加雕刻凹陷（与凸起的 fx_bevel 相反，等价 pen.fx.engrave）。 / Stack an engraved, carved-in look; the opposite of the raised fx_bevel, and the same as pen.fx.engrave. """
        return self._fx("engrave", depth=depth, blur=blur,
                        dark=dark, light=light)

    def fx_outline(self: _Self, width=3, color="gold") -> _Self:
        """叠加外描边（等价 pen.fx.outline）。 / Stack an outer stroke; same as pen.fx.outline. """
        return self._fx("outline", width=width, color=color)

    def fx_roughen(self: _Self, scale=4, frequency=0.05) -> _Self:
        """叠加粗糙化手绘感（等价 pen.fx.roughen）。 / Stack a roughen pass for a hand-drawn look; same as pen.fx.roughen. """
        return self._fx("roughen", scale=scale, frequency=frequency)

    def fx_noise(self: _Self, opacity=0.15) -> _Self:
        """叠加噪点颗粒（等价 pen.fx.noise）。 / Stack grain noise; same as pen.fx.noise. """
        return self._fx("noise", opacity=opacity)

    def fx_emboss(self: _Self, azimuth=45) -> _Self:
        """叠加浮雕灰度（等价 pen.fx.emboss）。 / Stack a grayscale emboss; same as pen.fx.emboss. """
        return self._fx("emboss", azimuth=azimuth)

    def fx_edge_detect(self: _Self) -> _Self:
        """叠加边缘检测线稿感（等价 pen.fx.edge_detect）。 / Stack edge detection for a line-art look; same as pen.fx.edge_detect. """
        return self._fx("edge_detect")

    def fx_saturate(self: _Self, factor=1.2) -> _Self:
        """叠加饱和度调整（等价 pen.fx.saturate）。 / Stack a saturation change; same as pen.fx.saturate. """
        return self._fx("saturate", factor=factor)

    def fx_hue_rotate(self: _Self, degrees=90) -> _Self:
        """叠加色相旋转（等价 pen.fx.hue_rotate）。 / Stack a hue rotation; same as pen.fx.hue_rotate. """
        return self._fx("hue_rotate", degrees=degrees)

    def fx_grayscale(self: _Self) -> _Self:
        """叠加去色（等价 pen.fx.grayscale）。 / Stack a desaturate; same as pen.fx.grayscale. """
        return self._fx("grayscale")

    def fx_sepia(self: _Self) -> _Self:
        """叠加怀旧褐色调（等价 pen.fx.sepia）。 / Stack a sepia tone; same as pen.fx.sepia. """
        return self._fx("sepia")

    def fx_brightness(self: _Self, factor=1.2) -> _Self:
        """叠加亮度调整（等价 pen.fx.brightness）。 / Stack a brightness change; same as pen.fx.brightness. """
        return self._fx("brightness", factor=factor)

    def fx_contrast(self: _Self, factor=1.3) -> _Self:
        """叠加对比度调整（等价 pen.fx.contrast）。 / Stack a contrast change; same as pen.fx.contrast. """
        return self._fx("contrast", factor=factor)

    def fx_gamma(self: _Self, r=1.0, g=1.0, b=1.0) -> _Self:
        """叠加伽马校正（等价 pen.fx.gamma）。 / Stack a gamma correction; same as pen.fx.gamma. """
        return self._fx("gamma", r=r, g=g, b=b)

    def fx_invert(self: _Self) -> _Self:
        """叠加反相（等价 pen.fx.invert）。 / Stack an invert; same as pen.fx.invert. """
        return self._fx("invert")

    def fx_posterize(self: _Self, levels=4) -> _Self:
        """叠加色调分离（等价 pen.fx.posterize）。 / Stack a posterize; same as pen.fx.posterize. """
        return self._fx("posterize", levels=levels)

    def fx_color_overlay(self: _Self, color="red", opacity=0.8) -> _Self:
        """叠加颜色叠加（等价 pen.fx.color_overlay）。 / Stack a color overlay; same as pen.fx.color_overlay. """
        return self._fx("color_overlay", color=color, opacity=opacity)

    def _apply_paint(self, kw):
        """
        应用填充/描边类属性（从 kwargs 中取出）。

        支持的键（枚举 / 字符串两种写法都行）:
            fill_color, stroke_color, stroke_width, stroke_style（DashStyle 或 "8 4"）,
            stroke_cap（StrokeCap）, stroke_join（StrokeJoin）,
            fill_rule（FillRule.EVENODD 或 "evenodd"）, dash_offset
        """
        fc = kw.pop("fill_color", None)
        if fc is not None:
            self.node.set("fill", _paint(fc))
        sc = kw.pop("stroke_color", None)
        if sc is not None:
            self.node.set("stroke", _paint(sc))
        sw = kw.pop("stroke_width", None)
        if sw is not None:
            self.node.set("stroke-width", sw)
        ss = kw.pop("stroke_style", None)     # 虚线样式：DashStyle 枚举 / "8 4" / [8, 4]
        if ss is not None:
            ss = value_of(ss)
            if ss == "" or ss is None:
                self.node.set("stroke-dasharray", None)
            else:
                self.node.set("stroke-dasharray",
                              " ".join(str(v) for v in ss) if isinstance(ss, (list, tuple)) else ss)
        so = kw.pop("dash_offset", None)      # 英文版新增：虚线偏移
        if so is not None:
            self.node.set("stroke-dashoffset", so)
        cap = kw.pop("stroke_cap", None)
        if cap is not None:
            self.node.set("stroke-linecap", value_of(cap))
        join = kw.pop("stroke_join", None)
        if join is not None:
            self.node.set("stroke-linejoin", value_of(join))
        fr = kw.pop("fill_rule", None)        # 英文版新增：evenodd 挖洞
        if fr is not None:
            self.node.set("fill-rule", value_of(fr))
        po = kw.pop("paint_order", None)      # 英文版新增：先描边 / paint order
        if po is not None:
            self.node.set("paint-order", value_of(po))

    # ---------------------------------------------------------------
    # 几何变换
    # ---------------------------------------------------------------
    def _sync_transform(self):
        """把 _transform_items 同步到节点的 transform 属性。"""
        self.node.set("transform", _fmt_transform(self._transform_items) or None)

    def translate(self: _Self, dx, dy=0) -> _Self:
        """
        平移元素。 / Translate the element.

        :param dx: X 方向位移
        :param dy: Y 方向位移

        示例::
            el.translate(50, 30)   # 右移 50、下移 30
        """
        self._transform_items.append(f"translate({fmt_num(dx)},{fmt_num(dy)})")
        self._sync_transform()
        return self

    def rotate(self: _Self, angle, cx=None, cy=None) -> _Self:
        """
        旋转元素。 / Rotate the element.

        :param angle: 角度（度，顺时针为正）
        :param cx: 旋转中心 x（默认原点）
        :param cy: 旋转中心 y

        示例::
            el.rotate(45, cx=200, cy=150)
        """
        if cx is None:
            self._transform_items.append(f"rotate({fmt_num(angle)})")
        else:
            self._transform_items.append(
                f"rotate({fmt_num(angle)},{fmt_num(cx)},{fmt_num(cy)})")
        self._sync_transform()
        return self

    def scale(self: _Self, sx, sy=None) -> _Self:
        """
        缩放元素（sy 缺省时等比）。 / Scale the element; omitting sy keeps it proportional.

        示例::
            el.scale(1.5)        # 放大 1.5 倍
            el.scale(2, 0.5)     # 横向放大、纵向压缩
        """
        if sy is None:
            sy = sx
        self._transform_items.append(f"scale({fmt_num(sx)},{fmt_num(sy)})")
        self._sync_transform()
        return self

    def skew_x(self: _Self, angle) -> _Self:
        """沿 X 轴倾斜（度）。 / Shear along the X axis, in degrees. 示例:: el.skew_x(15)"""
        self._transform_items.append(f"skewX({fmt_num(angle)})")
        self._sync_transform()
        return self

    def skew_y(self: _Self, angle) -> _Self:
        """沿 Y 轴倾斜（度）。 / Shear along the Y axis, in degrees. 示例:: el.skew_y(15)"""
        self._transform_items.append(f"skewY({fmt_num(angle)})")
        self._sync_transform()
        return self

    # ---------------------------------------------------------------
    # SMIL 动画（对应中文版动画工具集）
    # ---------------------------------------------------------------
    def _animate_transform(self: _Self, attr_type, values, dur, repeat_count, begin, accelerate=False) -> _Self:
        """写入 <animateTransform> 子节点（内部方法）。"""
        an = SvgNode("animateTransform", {
            "attributeName": "transform",
            "type": attr_type,
            "values": values,
            "dur": f"{dur}s",
            "begin": f"{begin}s" if begin else "0s",
        })
        if repeat_count:
            an.set("repeatCount", repeat_count if isinstance(repeat_count, str) else int(repeat_count))
        if accelerate:
            # 缓入缓出：calcMode=spline 要求 keySplines 的个数 = 关键帧数 - 1。
            # 之前写死两段样条，两帧动画时个数对不上，整个 <animateTransform>
            # 会被浏览器判为非法并**直接丢弃** —— 旋转/公转一动不动
            # （地球不绕太阳转的真 bug，2026-09-23 修复）。keyTimes 一并补上。
            frames = values.split(";")
            n = len(frames)
            an.set("calcMode", "spline")
            an.set("keyTimes", ";".join(fmt_num(i / (n - 1)) for i in range(n)))
            an.set("keySplines", "; ".join(["0.4 0 0.6 1"] * (n - 1)))
        self.node.add(an)
        return self

    def animate_opacity(self: _Self, start=1.0, end=0.0, dur=3, repeat_count="indefinite", begin=0) -> _Self:
        """
        透明度渐变动画（对应中文版 `透明动画`）。 / Animate opacity.

        :param start: 起始透明度
        :param end: 结束透明度
        :param dur: 时长（秒）
        :param repeat_count: 重复次数或 "indefinite"
        :param begin: 延迟秒数

        示例::
            el.animate_opacity(1, 0, dur=2)   # 2 秒内淡出，循环
        """
        an = SvgNode("animate", {
            "attributeName": "opacity",
            "values": f"{start};{end}",
            "dur": f"{dur}s",
            "begin": f"{begin}s" if begin else "0s",
        })
        if repeat_count:
            an.set("repeatCount", repeat_count if isinstance(repeat_count, str) else int(repeat_count))
        self.node.add(an)
        return self

    def animate_translate(self: _Self, offset=(0, 0), dur=3, repeat_count=1, begin=0) -> _Self:
        """
        平移动画（对应中文版 `平移动画`）。 / Animate translation.

        :param offset: (dx, dy) 位移向量
        :param dur: 时长秒
        :param repeat_count: 重复次数（"indefinite" 表示循环）

        示例::
            el.animate_translate(offset=(100, 0), dur=2, repeat_count="indefinite")
        """
        dx, dy = offset
        return self._animate_transform("translate", f"0 0;{fmt_num(dx)} {fmt_num(dy)}",
                                       dur, repeat_count, begin)

    def animate_rotate(self: _Self, angle=360, center=(0, 0), dur=3, repeat_count="indefinite",
                       begin=0, accelerate=False) -> _Self:
        """
        旋转动画（对应中文版 `旋转动画` / `加速旋转动画`）。 / Animate rotation.

        :param angle: 总旋转角度（度）
        :param center: 旋转中心 (cx, cy)
        :param dur: 时长秒
        :param accelerate: True 时使用缓入缓出（加速旋转效果）

        示例::
            el.animate_rotate(360, center=(200, 150), dur=5, accelerate=True)
        """
        cx, cy = center
        return self._animate_transform(
            "rotate", f"0 {fmt_num(cx)} {fmt_num(cy)};{fmt_num(angle)} {fmt_num(cx)} {fmt_num(cy)}",
            dur, repeat_count, begin, accelerate)

    def animate_scale(self: _Self, factor=(2, 2), dur=3, repeat_count=1, begin=0) -> _Self:
        """
        缩放动画（对应中文版 `缩放动画`）。 / Animate scaling.

        示例::
            el.animate_scale(factor=(1.5, 1.5), dur=2, repeat_count="indefinite")
        """
        fx, fy = factor
        return self._animate_transform("scale", f"1 1;{fmt_num(fx)} {fmt_num(fy)}",
                                       dur, repeat_count, begin)

    def animate_skew_x(self: _Self, angle=30, dur=3, repeat_count=1, begin=0) -> _Self:
        """X 轴倾斜动画（对应中文版 `倾斜X动画`）。 / Animate a shear along the X axis. 示例:: el.animate_skew_x(20)"""
        return self._animate_transform("skewX", f"0;{fmt_num(angle)}", dur, repeat_count, begin)

    def animate_skew_y(self: _Self, angle=30, dur=3, repeat_count=1, begin=0) -> _Self:
        """Y 轴倾斜动画（对应中文版 `倾斜Y动画`）。 / Animate a shear along the Y axis. 示例:: el.animate_skew_y(20)"""
        return self._animate_transform("skewY", f"0;{fmt_num(angle)}", dur, repeat_count, begin)

    def animate_motion(self: _Self, path, dur=5, rotate=False, repeat_count="indefinite", begin=0) -> _Self:
        """
        沿轨迹移动动画（对应中文版 `轨迹移动动画`）。 / Animate movement along a motion path.

        :param path: 轨迹，可为 PathElement、路径 d 字符串或顶点列表
        :param rotate: 是否跟随轨迹方向转向

        示例::
            el.animate_motion("M100,100 C200,50 300,150 400,100", dur=4, rotate=True)
        """
        from .path import PathElement
        if isinstance(path, PathElement):
            d = path.get_d()
        elif isinstance(path, (list, tuple)):
            d = "M " + " L ".join(f"{fmt_num(x)},{fmt_num(y)}" for x, y in path)
        else:
            d = path
        an = SvgNode("animateMotion", {
            "path": d, "dur": f"{dur}s",
            "begin": f"{begin}s" if begin else "0s",
        })
        if rotate:
            an.set("rotate", "auto")
        if repeat_count:
            an.set("repeatCount", repeat_count if isinstance(repeat_count, str) else int(repeat_count))
        self.node.add(an)
        return self

    def animate_dash_flow(self: _Self, dur=2, repeat_count="indefinite", dash="8 4", speed=64) -> _Self:
        """
        虚线流动画（对应中文版 `虚线流动画`）：蚂蚁线效果。 / Animate marching-ants dashes flowing along the stroke.

        :param dash: 虚线样式，如 "8 4"
        :param speed: 每秒流动的虚线单位数（决定 dashoffset 动画幅度）

        示例::
            line = pen.line((50, 50), (350, 50), stroke_width=4)
            line.animate_dash_flow(dur=2, dash="10 6")
        """
        self.node.set("stroke-dasharray", dash)
        total = sum(float(x) for x in re.findall(r"[\d.]+", dash)) or 12
        an = SvgNode("animate", {
            "attributeName": "stroke-dashoffset",
            "values": f"0;{-total * speed / total if False else -total}",
            "dur": f"{dur}s",
            "repeatCount": repeat_count if isinstance(repeat_count, str) else int(repeat_count),
        })
        self.node.add(an)
        return self

    # ---------------------------------------------------------------
    # 层级与生命周期
    # ---------------------------------------------------------------
    def remove(self: _Self) -> _Self:
        """
        从画布上删除本元素（对应中文版 `删除`）。 / Remove this element from the canvas.

        示例::
            el.remove()
        """
        if self.parent_node is not None:
            self.parent_node.remove_child(self.node)
            self.parent_node = None
        return self

    def bring_to_front(self: _Self) -> _Self:
        """
        置顶（对应中文版 `置前`）：移到父容器的最后一个。 / Bring to front by moving last among siblings.

        示例::
            el.bring_to_front()
        """
        if self.parent_node is not None:
            self.parent_node.remove_child(self.node)
            self.parent_node.add(self.node)
        return self

    def send_to_back(self: _Self) -> _Self:
        """
        置底（英文版新增）：移到父容器的第一个。 / Send to back by moving first among siblings.

        示例::
            el.send_to_back()
        """
        if self.parent_node is not None:
            self.parent_node.remove_child(self.node)
            self.parent_node.children.insert(0, self.node)
        return self

    def change_group(self: _Self, new_parent) -> _Self:
        """
        把元素移动到另一个组（对应中文版 `更换组`）。 / Move the element into another group.

        :param new_parent: GroupElement 或 SvgNode

        示例::
            g = pen.g()
            el.change_group(g)
        """
        if isinstance(new_parent, Element):
            new_parent = new_parent.node
        if self.parent_node is not None:
            self.parent_node.remove_child(self.node)
        new_parent.add(self.node)
        self.parent_node = new_parent
        return self

    def to_group(self, id_=None) -> "GroupElement":
        """
        把本元素原地包进一个新组并返回该组（英文版新增）。 / Wrap this element in a new group in place and return the group.

        元素在画布上的位置与层叠顺序都不变，只是外层多了一个 <g>；之后组级
        样式/滤镜/动画作用于整组，可与元素自身的滤镜叠加（两层滤镜各算各的，
        不会挤进同一条滤镜链）。 / The element keeps its place and stacking order;
        a <g> wraps it so group-level styles, filters and animations stack on top of
        the element's own filter (two separate filter chains, not merged).

        :param id_: 新组的 id（可选）
        :return: 包住本元素的 GroupElement

        示例（水印字：元素级边缘检测 + 组级投影）::
            pen.text(500, 250, "MaLight", font_size=28, opacity=0.1) \
                .fx_edge_detect().to_group().fx_shadow(1, 1, 0.5, "#000000", 0.6)
        """
        from .group import GroupElement      # 延迟导入，避免循环依赖
        orig = self.parent_node
        g = GroupElement(self.board, parent=orig)
        if id_:
            g.set_id(id_)
        if orig is not None and self.node in orig.children:
            # 组顶替元素原来的层叠位置（原来是第几个就还在第几个）
            idx = orig.children.index(self.node)
            self.change_group(g)
            orig.remove_child(g.node)
            orig.children.insert(idx, g.node)
        else:
            self.change_group(g)
        return g

    def to_template(self, id_=None, view_box=None) -> "TemplateElement":
        """
        把本元素原地转成 <symbol> 模板并返回该模板（英文版新增）。 / Turn this element into a <symbol> template in place and return the template.

        元素从画布移入 <defs> 的 <symbol>（画布上不再直接显示），view_box
        缺省按元素包围盒推算；返回的模板用 ``clone()`` 盖章出任意多个实例
        —— 改模板一处，所有实例一起变，画布体积也更小。 / The element moves
        from the canvas into a <symbol> in <defs> (no longer drawn directly);
        view_box defaults to the element's bounding box. Stamp any number of
        instances with ``clone()`` - edit the template once, every instance
        updates, and the file stays small.

        :param id_: 模板 id（缺省自动生成 template-1、template-2 …）
        :param view_box: 模板自己的坐标系；None = 元素包围盒（或画布尺寸）
        :return: TemplateElement（用 ``tpl.clone(x, y, width, height)`` 盖章）

        示例（背景图转模板再盖章复用）::
            tpl = pen.image(image_file="bg.jpg", x=0, y=0,
                            width=pen.width, height=pen.height).to_template()
            tpl.clone()                    # 原位一个实例（位置尺寸同原图）
            tpl.clone(x=60, width=200)     # 任意变形复用
        """
        from .symbol import TemplateElement      # 延迟导入，避免循环依赖
        box = self.bbox()
        tpl = TemplateElement(self.board, id_=id_, view_box=view_box)
        if view_box is None:
            if box:
                tpl.node.set("viewBox", "{} {} {} {}".format(
                    fmt_num(box[0]), fmt_num(box[1]),
                    fmt_num(box[2] - box[0]), fmt_num(box[3] - box[1])))
            elif self.board is not None:
                tpl.node.set("viewBox", "0 0 {} {}".format(
                    fmt_num(self.board.width), fmt_num(self.board.height)))
        if self.board is not None and not tpl.node.attribs.get("id"):
            n = 1
            while ("template-%d" % n) in self.board._registry:
                n += 1
            tpl.set_id("template-%d" % n)
        self.change_group(tpl)
        tpl._origin_bbox = box                   # clone() 缺省位置/尺寸用 / default stamp geometry
        return tpl

    def clone(self: _Self, dx=0, dy=0, id_=None) -> _Self:
        """
        克隆元素（对应中文版 `克隆`），可指定偏移与新 id。 / Clone the element, optionally with an offset and a new id.

        :param dx: 克隆体 X 偏移
        :param dy: 克隆体 Y 偏移
        :param id_: 克隆体 id
        :return: 新元素（同类型）

        示例::
            twin = el.clone(dx=120, id_="sun2")
        """
        import copy
        new_node = copy.deepcopy(self.node)
        if (dx or dy) and new_node.attribs.get("transform"):
            new_node.attribs["transform"] += f" translate({fmt_num(dx)},{fmt_num(dy)})"
        elif dx or dy:
            new_node.attribs["transform"] = f"translate({fmt_num(dx)},{fmt_num(dy)})"
        if id_:
            new_node.set("id", id_)
        same = copy.copy(self)
        same.node = new_node
        same.node.element = same        # 新节点绑定到克隆体自身
        same.parent_node = self.parent_node
        self._copy_mutable_state(same)  # 各复制一份可变内部状态（见该方法说明）
        self.parent_node.add(new_node)
        if id_ and self.board is not None:
            self.board._registry[id_] = same
        return same

    def _copy_mutable_state(self, other):
        """
        把「每个元素各自独立」的可变内部状态复制给克隆体（内部方法）。

        ``clone`` 走的是浅拷贝，形如 ``self._cmds``（路径的命令列表）这样的
        列表会被**两条路径共用**：之后往任一条上继续画，另一条的 ``d`` 也会
        跟着变。子类覆盖本方法，把这类状态各复制一份。

        默认无状态，什么都不做。

        示例（内部）::

            twin = path.clone(); twin.line_to(300, 200)   # 不影响原路径
        """

    def update(self: _Self, **kw) -> _Self:
        """
        按需更新元素属性（英文版新增：只改传入的项，其余保持原值）。 / Update only the attributes you pass in; everything else keeps its current value.

        这是所有元素通用的「局部更新」入口。原理：元素每次写入属性时都会
        记下当时完整生效的参数；``update`` 用「上次的参数 + 本次传入」重放一遍，
        所以没写的属性不会被默认值冲掉。

        :param kw: 要更新的属性，键名与创建时一致（枚举 / 字符串都行）
        :return: self（可链式）

        示例::
            c = pen.circle(100, 100, 50, fill_color="red")
            c.update(radius=80)          # 只改半径，圆心仍在 (100, 100)
            c.update(opacity=0.5)        # 只改透明度
            c.update(fill_color=ColorName.TEAL, stroke_width=4)

            t = pen.text(100, 80, "标题", font_size=24)
            t.update(font_size=36, bold=True)   # 只改这两项

            img = pen.svg_image("icon.svg", 10, 10, 120, 80)
            img.update(width=200)        # 只改宽度
        """
        if hasattr(self, "_update_attrs"):
            args = dict(getattr(self, "_attrs_args", None) or {})
            args.update(kw)
            self._update_attrs(**args)
            return self
        # 兜底：极少数没有 _update_attrs 的元素，按属性名直接写
        self._apply_common(kw)
        self._apply_paint(kw)
        for key, val in kw.items():
            name = _ATTR_ALIAS.get(key, key.replace("_", "-"))
            self.node.set(name, value_of(val))
        return self

    # ---------------------------------------------------------------
    # 几何信息
    # ---------------------------------------------------------------
    def bbox(self) -> "Optional[tuple]":
        """
        元素包围盒 (min_x, min_y, max_x, max_y)；无法确定时返回 None。 / Element bounding box as (min_x, min_y, max_x, max_y); None when it cannot be determined.

        基类默认按节点的 ``x / y / width / height`` 属性推算，因此
        `<use>`、`<image>`、`<svg>`（嵌套）、`<pattern>` 这类「矩形占位」
        元素可以直接拿到包围盒；宽高是通过 ``<use>`` 复用的模板时，还会回退到
        被引用对象的 ``viewBox`` 尺寸。

        圆形 / 矩形 / 文本 / 路径等有几何算法的元素会各自覆盖本方法，
        给出更精确的结果（例如圆按 cx±r、路径按采样点）。

        示例::
            print(el.bbox())        # (50.0, 60.0, 230.0, 180.0)
        """
        return self._wh_bbox()

    def _wh_bbox(self) -> "Optional[tuple]":
        """
        按 ``x / y / width / height`` 属性推算包围盒（内部方法）。

        width / height 缺失时，若本元素通过 href 引用了 symbol / svg，
        则回退使用被引用对象的 viewBox 宽高（`<use>` 不写宽高时的真实表现）。
        依旧拿不到就返回 None。

        示例（内部）::
            b = self._wh_bbox()
        """
        x = _num(self.node.attribs.get("x"), 0.0)
        y = _num(self.node.attribs.get("y"), 0.0)
        w = _num(self.node.attribs.get("width"))
        h = _num(self.node.attribs.get("height"))
        if w is None or h is None:
            rw, rh = self._ref_view_box_size()
            w = w if w is not None else rw
            h = h if h is not None else rh
        if w is None or h is None or w <= 0 or h <= 0:
            return None
        return (x, y, x + w, y + h)

    def _ref_view_box_size(self) -> tuple:
        """
        被引用对象（symbol / svg）viewBox 的宽高；取不到返回 (None, None)。

        仅对 ``href="#某id"`` 这种内部引用有效（外部文件引用无法读取）。

        示例（内部）::
            w, h = self._ref_view_box_size()
        """
        href = (self.node.attribs.get("href") or
                self.node.attribs.get("xlink:href") or "")
        href = str(href)
        if not href.startswith("#") or self.board is None:
            return (None, None)
        target = self.board.get_element(href[1:])
        if target is None:
            return (None, None)
        parts = re.split(r"[,\s]+", str(target.node.attribs.get("viewBox") or "").strip())
        if len(parts) == 4:
            return (_num(parts[2]), _num(parts[3]))
        return (_num(target.node.attribs.get("width")),
                _num(target.node.attribs.get("height")))

    @property
    def center_x(self) -> "Optional[float]":
        """中心点 x（对应中文版 `中心x`）。 / Center x coordinate. 示例:: print(el.center_x)"""
        b = self.bbox()
        return (b[0] + b[2]) / 2 if b else None

    @property
    def center_y(self) -> "Optional[float]":
        """中心点 y（对应中文版 `中心y`）。 / Center y coordinate. """
        b = self.bbox()
        return (b[1] + b[3]) / 2 if b else None

    @property
    def width(self) -> "Optional[float]":
        """宽度（对应中文版 `宽`）。 / Width. """
        b = self.bbox()
        return b[2] - b[0] if b else None

    @property
    def height(self) -> "Optional[float]":
        """高度（对应中文版 `高`）。 / Height. """
        b = self.bbox()
        return b[3] - b[1] if b else None

    def __repr__(self) -> str:
        return f"<{type(self).__name__} id={self.node.attribs.get('id')}>"


# ===========================================================================
# 基本图形元素
# ===========================================================================

# ===========================================================================
# 使用示例
# ===========================================================================
# 在 PyCharm 里点绿色三角直接运行本文件即可；也可命令行：
#     python -m malight.elements.base
# ===========================================================================
if __name__ == "__main__":
    import os

    from malight import Malight, ColorName, Font

    # 输出统一放到项目根的 output/ 目录（从哪运行结果都在同一处） / Output always goes to the project-root output/ directory, wherever you run from
    _out = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        "..", "..", "output"))
    pen = Malight(os.path.join(_out, "demo_element_base"), width=560, height=340)
    pen.set_background_color(ColorName.WHITESMOKE)

    pen.text(280, 40, "Element 基类：所有元素的共同能力 / Element base class: capabilities shared by every element", font=Font.SIMHEI,
             font_size=20, h_align="middle", fill_color=ColorName.NAVY)

    # 1) 元素由绘图板创建，返回的是「具体类型」，PyCharm 能提示 / 1) The board creates elements and returns concrete types, so PyCharm completes them
    ball = pen.circle(140, 170, 60, fill_color=ColorName.TOMATO,
                      stroke_color=ColorName.NAVY, stroke_width=3)
    print("元素类型: / element type:", type(ball).__name__)          # CircleElement

    # 2) 设置 id 后可以反查 / 2) Give it an id and you can look it up again
    ball.set_id("ball")
    print("按 id 反查同一个对象: / looked up by id, same object:", pen.get_element("ball") is ball)

    # 3) 几何信息（基类提供，所有元素都有） / 3) Geometry, provided by the base class for every element
    print("包围盒 bbox: / bounding box:", tuple(round(v, 1) for v in ball.bbox()))
    print("中心点: / centre:", round(ball.center_x, 1), round(ball.center_y, 1))
    print("宽高: / size:", round(ball.width, 1), round(ball.height, 1))

    # 4) 变换：可链式，返回的仍是 CircleElement / 4) Transforms chain and still return a CircleElement
    ball.translate(20, -10)                  # 平移 / translate
    ball.rotate(15, cx=140, cy=170)          # 绕指定点旋转 / rotate around a point
    ball.scale(1.05)                         # 缩放 / scale

    # 5) 局部更新：只改传入的项，几何不受影响 / 5) Partial update: only the keys you pass change, geometry is untouched
    ball.update(opacity=0.85)

    # 6) 滤镜：一行加特效（pen.fx 是滤镜工厂） / 6) Filters: one line per effect (pen.fx is the filter factory)
    #    滤镜效果请用浏览器打开输出 SVG 查看，转 PNG 时 cairosvg 不渲染 filters / Open the SVG in a browser for filter effects; cairosvg does not render them
    ball.set_filter(pen.fx.shadow(6, 8, 6))

    # 7) 克隆（同类型；可带偏移与新 id） / 7) Clone: same type, with an optional offset and a new id
    twin = ball.clone(dx=190, id_="ball2")
    print("克隆体类型: / clone type:", type(twin).__name__,
          "| id:", twin.node.attribs.get("id"))

    # 8) 层级调整：后画的元素在上层，可用它们改遮挡关系 / 8) Z-order: later elements sit on top; these change the overlap
    twin.bring_to_front()

    # 9) 动画（SMIL，用浏览器打开 SVG 才能看到动） / 9) Animation (SMIL; open the SVG in a browser to see it move)
    twin.animate_translate(offset=(0, -30), dur=2, repeat_count="indefinite")
    twin.animate_opacity(1.0, 0.4, dur=2, repeat_count="indefinite")

    # 10) 透传自定义 SVG 属性（extra 里的键会原样落成属性） / 10) Pass through custom SVG attributes: keys in extra become attributes
    pen.rect(370, 130, 150, 90, corner_radius=10,
             fill_color=ColorName.STEELBLUE,
             extra={"data-name": "panel"})

    # 11) 删除元素（从画布移除） / 11) Remove an element from the canvas
    pen.circle(500, 300, 20, fill_color=ColorName.CRIMSON).remove()

    pen.finish()      # 保存 SVG，并打印文件全路径（方便直接复制） / Save the SVG and print the full path, ready to copy


# ---------------------------------------------------------------------------
# 底部导入：to_group() 的返回注解引用 GroupElement，而 group.py 又继承本模块的 / Bottom import: to_group()'s return annotation names GroupElement, which subclasses
# Element —— 顶部互相导入会循环；放到文件末尾（Element 已定义完毕）两个问题都解决， / the Element defined in this module - importing both at the top would cycle; putting it
# elements.__init__ 保证 base 先于 group 导入，运行时不会触发循环。 / at the bottom solves both. elements.__init__ imports base before group, so no cycle.
# ---------------------------------------------------------------------------
from .group import GroupElement  # noqa: E402

# ---------------------------------------------------------------------------
# 底部导入（续）：to_template() 的返回注解同理引用 TemplateElement。 / Bottom import (cont.): same idea for to_template()'s TemplateElement annotation.
# ---------------------------------------------------------------------------
from .symbol import TemplateElement  # noqa: E402
