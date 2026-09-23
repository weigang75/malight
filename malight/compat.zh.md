<!-- 本文件由 tools/gen_docs.py 从源码自动生成，请勿手改。
     要改内容请改同目录的 compat.py 里的文档字符串，然后重跑生成器。 -->

# compat.py

**简体中文** ｜ [English](compat.en.md) ｜ [← 返回 README](../README.md)

兼容迁移（compat）—— 中文 API → 英文 API 对照与迁移工具

帮助老用户把「神笔码靓」中文脚本迁移到 magicpen 英文版。

提供两种用法：

1. 在线兼容层（零改动运行旧代码思路的参考）

```text
    import malight.compat as compat
    compat.print_mapping("画圆")     # 查询单个映射

2. 离线迁移脚本::

    python -m malight.compat 旧脚本.py 新脚本.py
    # 自动把中文名称替换为英文版名称（正则批量替换，改动处人工复核）
```


---

## 类与方法

### 函数

| 函数 | 说明 |
|---|---|
| `print_mapping` | 查询中文名称对应的英文版名称。 |
| `migrate` | 迁移中文脚本到英文版（正则批量替换，尽力而为，结果需人工复核）。 |

---

## 完整示例

在 PyCharm 里点绿色三角直接运行，或命令行：`python malight/compat.py`

```python
if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 3:
        migrate(sys.argv[1], sys.argv[2])
    else:
        print("用法: python -m malight.compat <旧脚本.py> [新脚本.py]")
```

---

## 同级模块

[definitions](definitions.zh.md) ｜ [ext](ext.zh.md) ｜ [fonts](fonts.zh.md) ｜ [gradients](gradients.zh.md) ｜ [i18n](i18n.zh.md) ｜ [page](page.zh.md) ｜ [svg_backend](svg_backend.zh.md) ｜ [tools](tools.zh.md)
