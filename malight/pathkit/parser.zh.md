<!-- 本文件由 tools/gen_docs.py 从源码自动生成，请勿手改。
     要改内容请改同目录的 parser.py 里的文档字符串，然后重跑生成器。 -->

# parser.py

**简体中文** ｜ [English](parser.en.md) ｜ [← 返回 README](../../README.md)

路径坐标解析（pathkit.parser）—— SVG path d 串 <-> 结构化线段列表

英文版 malight 内部使用。把 `d` 字符串解析为「每段一个 PathSegment」，
坐标全部归一化为**绝对坐标**，并把这些快捷命令展开，方便后续查看与调整：

- `H`/`V`（水平/垂直线）  → 展开为 `L`
- `S`（平滑三次贝塞尔）     → 展开为 `C`（自动算出第一个控制点）
- `T`（平滑二次贝塞尔）     → 展开为 `Q`（自动算出控制点）
- 相对命令（小写 m/l/c/...）  → 转成绝对坐标

这样每条曲线都有明确的「起点 / 终点 / 控制点」，就是你在 Illustrator、
Figma 里用钢笔工具看到的那些点。

使用示例

```python
from malight.pathkit import parse_path_d
segs = parse_path_d("M0,0 C10,20 30,20 40,0 L80,0 Z")
for s in segs:
    print(s)
```


---

## 类与方法

### 函数

| 函数 | 说明 |
|---|---|
| `tokenize` | 把 d 字符串切成「命令字母 / 数字」记号列表。 |
| `parse_path_d` | 解析 SVG path 的 d 字符串为线段列表（绝对坐标，已展开快捷命令）。 |
| `segments_to_d` | 把线段列表还原为 SVG path 的 d 字符串。 |
| `reverse_segments` | 反转线段列表（起终点互换、控制点顺序颠倒、圆弧方向取反）。 |

---

## 完整示例

在 PyCharm 里点绿色三角直接运行，或命令行：`python malight/pathkit/parser.py`

```python
if __name__ == "__main__":
    import os
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

    print("=== 1) 解析（含相对命令 / 快捷命令展开）===")
    d = "M10,10 h100 v50 s20,20 40,0 t40,0 a20,20 0 0,1 40,0 Z"
    for s in parse_path_d(d):
        print("  ", s.describe())

    print("\n=== 2) 还原为 d 串（H/V/S/T 已展开为 L/C/Q，坐标等价）===")
    print("  ", segments_to_d(parse_path_d(d)))

    print("\n=== 3) 反转路径方向 ===")
    segs = parse_path_d("M0,0 L100,0 C110,20 130,20 140,0")
    print("   原:", segments_to_d(segs))
    print("   后:", segments_to_d(reverse_segments(segs)))

    print("\n=== 4) 曲线取点（弧长参数化，用于定位/测长）===")
    seg = parse_path_d("M0,0 C0,100 100,100 100,0")[1]
    _len = seg.length()
    # 双语字符串里同一个占位符出现两次（中英各一次），参数要给两遍
    print("   曲线长度 ≈ %.2f" % (_len, _len))
    print("   1/4 处坐标:", tuple(round(v, 2) for v in seg.point_at(0.25)))
```

---

## 同级模块

[editor](editor.zh.md) ｜ [htmleditor](htmleditor.zh.md) ｜ [point](point.zh.md) ｜ [segment](segment.zh.md)
