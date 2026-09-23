<!-- 本文件由 tools/gen_docs.py 从源码自动生成，请勿手改。
     要改内容请改同目录的 svg_backend.py 里的文档字符串，然后重跑生成器。 -->

# svg_backend.py

**简体中文** ｜ [English](svg_backend.en.md) ｜ [← 返回 README](../README.md)

SVG 轻量后端（svg_backend）—— 内部模块

提供最小化的 SVG 元素树与序列化能力，替代原版对 svgwrite 的依赖。
使用自研后端的原因：可以无损支持 SVG 规范的所有属性
（fill-rule、transform、filter、marker、SMIL 动画等），
避免 svgwrite 对部分属性的校验/改写限制。

一般无需直接导入本模块；元素类会自动使用它。

示例（仅供内部调试）

```python
from malight.svg_backend import SvgNode
node = SvgNode("circle", {"cx": 10, "cy": 20, "r": 5, "fill": "red"})
print(node.to_xml())     # <circle cx="10" cy="20" r="5" fill="red"/>
```


---

## 类与方法

### 函数

| 函数 | 说明 |
|---|---|
| `fmt_num` | 数值格式化：保留小数、去掉多余的 0。 |

### `SvgNode`

SVG 节点：标签 + 属性字典 + 子节点列表。

| 方法 | 说明 |
|---|---|
| `add(child)` | 添加子节点（SvgNode 或原始 XML 字符串）。 |
| `set(key, value)` | 设置属性值。值为 None 时删除该属性（便于条件属性）。 |
| `find(node_id)` | 按 id 递归查找子节点；找不到返回 None。 |
| `remove_child(child)` | 移除指定子节点（不抛错）。 |
| `to_xml(indent=0, pretty=True)` | 序列化为 XML 字符串。 |

---

## 同级模块

[compat](compat.zh.md) ｜ [definitions](definitions.zh.md) ｜ [ext](ext.zh.md) ｜ [fonts](fonts.zh.md) ｜ [gradients](gradients.zh.md) ｜ [i18n](i18n.zh.md) ｜ [page](page.zh.md) ｜ [tools](tools.zh.md)
