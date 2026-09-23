# -*- coding: utf-8 -*-
"""
SVG 轻量后端（svg_backend）—— 内部模块
========================================

A tiny SVG element and serialisation backend (internal).

提供最小化的 SVG 元素树与序列化能力，替代原版对 svgwrite 的依赖。
使用自研后端的原因：可以无损支持 SVG 规范的所有属性
（fill-rule、transform、filter、marker、SMIL 动画等），
避免 svgwrite 对部分属性的校验/改写限制。

一般无需直接导入本模块；元素类会自动使用它。

示例（仅供内部调试）::

    from malight.svg_backend import SvgNode
    node = SvgNode("circle", {"cx": 10, "cy": 20, "r": 5, "fill": "red"})
    print(node.to_xml())     # <circle cx="10" cy="20" r="5" fill="red"/>
"""

from typing import Optional
from xml.sax.saxutils import escape


def fmt_num(value, keep=2):
    """
    数值格式化：保留小数、去掉多余的 0。 / Format a number, keeping its decimals and trimming redundant zeros.

    :param value: 数值或数值字符串
    :param keep: 保留小数位数（默认 2）
    :return: 简洁的数字字符串，如 "12.5"、"100"

    示例::
        fmt_num(12.500)   # "12.5"
        fmt_num(100.00)   # "100"
    """
    if isinstance(value, str):
        # 已经是字符串的（如 "50%"、"url(#id)"）原样返回
        return value
    if isinstance(value, (int,)) or (isinstance(value, float) and value.is_integer()):
        return str(int(value))
    s = f"{float(value):.{keep}f}".rstrip("0").rstrip(".")
    return s if s else "0"


class SvgNode:
    """
    SVG 节点：标签 + 属性字典 + 子节点列表。 / An SVG node: tag, attribute dict and child list.

    属性键可包含命名空间前缀（如 "xlink:href"、"xmlns:xlink"）。
    子节点可以是 SvgNode，也可以是原始 XML 字符串。

    示例::
        g = SvgNode("g", {"id": "root"})
        g.add(SvgNode("circle", {"r": 10}))
        print(g.to_xml())
    """

    def __init__(self, tag, attributes=None, text=None):
        """
        :param tag: 标签名，如 "path"、"circle"、"g"
        :param attributes: 属性字典 {名: 值}
        :param text: 节点文本内容（如 <text> 的文字），默认无

        说明：``element`` 是元素对象反向引用（由 ``Element.__init__`` 写入），
        用于「已知节点、找回它的元素对象」，例如统计一个组里有哪些元素。
        直接创建的裸节点该属性为 None。
        """
        self.tag = tag
        self.attribs = dict(attributes or {})
        self.children = []      # 子节点：SvgNode 或原始字符串
        self.text = text        # 文本内容（escape 后输出）
        self.element = None     # 反向引用：该节点所属的元素对象（可为 None）

    def __deepcopy__(self, memo):
        """
        深拷贝：只复制「标签 / 属性 / 子节点 / 文本」，**不复制** element 反向引用。

        这样 `Element.clone()` 深拷贝节点树时不会把整个元素对象图（甚至画板）
        一并复制过去，克隆出来的节点保持 element 为 None，由克隆方自行绑定。
        """
        import copy
        new = SvgNode(self.tag, dict(self.attribs), self.text)
        memo[id(self)] = new
        for child in self.children:
            if isinstance(child, SvgNode):
                new.children.append(child.__deepcopy__(memo))
            else:
                new.children.append(copy.deepcopy(child, memo))
        return new

    # ---------------------------------------------------------------
    # 树操作
    # ---------------------------------------------------------------
    def add(self, child) -> "SvgNode":
        """
        添加子节点（SvgNode 或原始 XML 字符串）。 / Append a child node - either an SvgNode or a raw XML string.

        示例::
            g.add(SvgNode("rect", {"width": 10}))
        """
        self.children.append(child)
        return child

    def set(self, key, value) -> None:
        """
        设置属性值。值为 None 时删除该属性（便于条件属性）。 / Set an attribute; passing None removes it, which makes conditional attributes easy.

        命名空间规范化：键中的 Clark 写法 {ns}href 自动转为 xlink:href，
        保证序列化出的 XML 合法。

        示例::
            node.set("opacity", 0.5)
        """
        if key.startswith("{"):
            key = key.replace("{http://www.w3.org/1999/xlink}", "xlink:")
            key = key.replace("{http://www.w3.org/2000/svg}", "")
        if value is None:
            self.attribs.pop(key, None)
        else:
            self.attribs[key] = value

    def find(self, node_id) -> "Optional[SvgNode]":
        """
        按 id 递归查找子节点；找不到返回 None。 / Find a descendant by id recursively; returns None when absent.

        示例::
            node.find("layer_1")
        """
        if self.attribs.get("id") == node_id:
            return self
        for c in self.children:
            if isinstance(c, SvgNode):
                found = c.find(node_id)
                if found is not None:
                    return found
        return None

    def remove_child(self, child) -> None:
        """移除指定子节点（不抛错）。 / Remove a child node, silently ignoring a missing one. """
        try:
            self.children.remove(child)
        except ValueError:
            pass

    # ---------------------------------------------------------------
    # 序列化
    # ---------------------------------------------------------------
    def to_xml(self, indent=0, pretty=True) -> str:
        """
        序列化为 XML 字符串。 / Serialise the node to an XML string.

        :param indent: 缩进层级（pretty=True 时有效）
        :param pretty: 是否格式化缩进与换行
        :return: XML 字符串

        示例::
            SvgNode("rect", {"width": 5}).to_xml()   # '<rect width="5"/>'
        """
        pad = ("  " * indent) if pretty else ""
        nl = "\n" if pretty else ""
        attrs = []
        for k, v in self.attribs.items():
            if v is None:
                continue
            if isinstance(v, float):
                v = fmt_num(v)
            attrs.append(f' {k}="{escape(str(v), {chr(34): "&quot;"})}"')
        attr_str = "".join(attrs)

        # 无子节点：自闭合
        if not self.children and self.text is None:
            return f"{pad}<{self.tag}{attr_str}/>{nl}"

        # 有文本无子节点：单行
        if not self.children and self.text is not None:
            return f"{pad}<{self.tag}{attr_str}>{escape(str(self.text))}</{self.tag}>{nl}"

        # 有子节点：展开
        parts = [f"{pad}<{self.tag}{attr_str}>{nl}"]
        if self.text is not None:
            parts.append(f"{pad}  {escape(str(self.text))}{nl}")
        for c in self.children:
            if isinstance(c, SvgNode):
                parts.append(c.to_xml(indent + 1, pretty))
            else:  # 原始字符串
                if pretty:
                    for line in str(c).splitlines():
                        parts.append(f"{pad}  {line}\n")
                else:
                    parts.append(str(c))
        parts.append(f"{pad}</{self.tag}>{nl}")
        return "".join(parts)
