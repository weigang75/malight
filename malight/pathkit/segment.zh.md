<!-- 本文件由 tools/gen_docs.py 从源码自动生成，请勿手改。
     要改内容请改同目录的 segment.py 里的文档字符串，然后重跑生成器。 -->

# segment.py

**简体中文** ｜ [English](segment.en.md) ｜ [← 返回 README](../../README.md)

路径线段（pathkit.segment）—— PathSegment 类

`PathSegment` 表示 SVG 路径中的**一段**（对应一个 path 命令），
坐标已归一化为绝对坐标，每条曲线都明确给出「起点 / 终点 / 控制点」。

它是 `PathEditor` 看到路径内部结构的最基本单位：

- `M` 移动（起点，不画）
- `L` 直线段
- `C` 三次贝塞尔（2 个控制点）
- `Q` 二次贝塞尔（1 个控制点）
- `A` 圆弧（rx/ry/旋转角/大弧/方向）
- `Z` 闭合

使用示例

```python
from malight.pathkit import parse_path_d

seg = parse_path_d("M0,0 C0,80 100,80 100,0")[1]
print(seg.kind)          # "cubic"（三次贝塞尔）
print(seg.start)         # (0.0, 0.0)   起点
print(seg.ctrls)         # ((0.0, 80.0), (100.0, 80.0))  两个调整点
print(seg.end)           # (100.0, 0.0) 终点
print(seg.length())      # 曲线长度
print(seg.point_at(0.5)) # 曲线上 50% 处的坐标
```


---

## 类与方法

### 函数

| 函数 | 说明 |
|---|---|
| `kind_text` | 段类型说明，跟随语言设置（中文「三次贝塞尔」/ 英文 "cubic"）。 |

### `PathSegment`

路径中的一段（一个 SVG path 命令，绝对坐标）。

| 方法 | 说明 |
|---|---|
| `describe()` | 返回一行中文说明（打印路径结构时用）。 |
| `to_d()` | 本段还原为 d 片段。 |
| `point_at(t)` | 取本段上参数 t 处（0~1，按线段长度近似）的坐标。 |
| `arc_center()` | 圆弧的「端点参数 → 圆心参数」转换（SVG 规范 F.6.5）。 |
| `length(samples=32)` | 本段长度（直线精确；曲线按 samples 段折线近似；M/Z 为 0）。 |
| `bbox()` | 本段的包围盒 (min_x, min_y, max_x, max_y)（曲线按采样近似）。 |
| `set_anchor(index, x, y)` | 移动本段的一个锚点（起点 index=0，终点 index=1）。 |
| `set_control(index, x, y)` | 移动本段的一个控制点（调整点）。 |
| `split(t=0.5)` | 在参数 t 处把本段一分为二（新增一个锚点，形状完全不变）。 |
| `kind`（属性） | 本段的英文类型名：move / line / cubic / quad / arc / close。 |
| `is_curve`（属性） | 是不是曲线段（三次/二次贝塞尔或圆弧）。 |
| `is_closed`（属性） | 是不是闭合命令 Z。 |
| `control_count`（属性） | 本段控制点（调整点）个数。 |

---

## 完整示例

在 PyCharm 里点绿色三角直接运行，或命令行：`python malight/pathkit/segment.py`

```python
if __name__ == "__main__":
    from malight.pathkit import parse_path_d, segments_to_d
    from malight.pathkit import PathSegment

    def _pt(p):
        """把坐标打印成 (x, y) 两位小数的样子。"""
        return "({:.2f}, {:.2f})".format(p[0], p[1])

    # -----------------------------------------------------------------
    # 1) 解析与段的基本信息
    #    parse_path_d 会把 H/V/S/T 等快捷命令展开、相对命令转成绝对坐标，
    #    所以下标 0 恒为起笔的 M 段，之后每段都带明确的起点/终点/调整点。
    # -----------------------------------------------------------------
    d = "M0,0 h100 v50 s20,20 40,0 t40,0 a20,20 0 0,1 40,0 Z"
    segs = parse_path_d(d)
    # 双语字符串里同一个占位符会出现两次（中英各一次），所以参数要给两遍。
    print("=== 1) 解析结果（共 %d 段）==="
          % (len(segs), len(segs)))
    for i, s in enumerate(segs):
        print("  #{} cmd={} kind={} curve={} ctrls={}  {} -> {}".format(
            i, s.cmd, s.kind, s.is_curve, s.control_count,
            _pt(s.start), _pt(s.end)))

    # -----------------------------------------------------------------
    # 2) describe() / to_d() / repr：一行中文说明、还原 d 片段、调试短描述 / 2) describe() / to_d()
    #    注意段号：0=M(h 之前) 1=L(h100) 2=L(v50) 3=C(s... 展开) 4=Q 5=A 6=Z
    # -----------------------------------------------------------------
    print("\n=== 2) 单段说明 ===")
    cubic = segs[3]                       # 由 s 展开来的三次贝塞尔
    print("  describe:", cubic.describe())
    print("  to_d    :", cubic.to_d())
    print("  repr    :", repr(cubic))
    print("  起点/终点:", _pt(cubic.start), _pt(cubic.end))
    print("  调整点   :", " ".join(_pt(c) for c in cubic.ctrls))
    print("  是否曲线:", cubic.is_curve, " 是否闭合段:", cubic.is_closed)

    # -----------------------------------------------------------------
    # 3) 几何计算：弧长取点 / 段长 / 包围盒（全部按弧长参数化，定位准）
    # -----------------------------------------------------------------
    print("\n=== 3) 几何计算（三次贝塞尔 0,0 -> 100,0）===")
    demo = parse_path_d("M0,0 C0,100 100,100 100,0")[1]
    for t in (0.0, 0.25, 0.5, 0.75, 1.0):
        print("  t={:<4} -> {}".format(t, _pt(demo.point_at(t))))
    _len = demo.length()
    print("  曲线长度 ≈ %.2f" % (_len, _len))
    print("  包围盒     :", tuple(round(v, 2) for v in demo.bbox()))

    # -----------------------------------------------------------------
    # 4) 改点：set_anchor（起点 index=0 / 终点 index=1）、set_control
    #    直接改本段坐标，返回 self，可链式
    #    注意：段级 to_d() 只输出本段命令（不含起笔 M），要整条路径的 d 串
    #    请用 segments_to_d([...]) 拼装。
    # -----------------------------------------------------------------
    print("\n=== 4) 改点 ===")
    moved = parse_path_d("M0,0 C0,100 100,100 100,0")[1]
    moved.set_anchor(0, 10, 20).set_anchor(1, 110, 20)
    moved.set_control(0, 20, 120)
    print("  改后 d:", moved.to_d())
    print("  整条路径:", segments_to_d([PathSegment("M", moved.start, moved.start), moved]))

    # -----------------------------------------------------------------
    # 5) split()：在 t 处一分为二，新增一个锚点且**形状完全不变**
    #    直线段、C、Q 都支持；圆弧暂不支持（会抛 NotImplementedError）
    # -----------------------------------------------------------------
    print("\n=== 5) 拆分 ===")
    a, b = demo.split(0.5)
    print("  前半段:", a.to_d())
    print("  后半段:", b.to_d())
    print("  拼回去:", segments_to_d([a, b]))

    line = parse_path_d("M0,0 L100,0")[1]
    la, lb = line.split(0.5)
    print("  直线拆分:", la.to_d(), "|", lb.to_d())

    # -----------------------------------------------------------------
    # 6) 圆弧：params 存 (rx, ry, rot, large_arc, sweep)，arc_center() 求圆心
    # -----------------------------------------------------------------
    print("\n=== 6) 圆弧 ===")
    arc = parse_path_d("M0,0 A50,50 0 0,1 100,0")[1]
    print("  kind:", arc.kind, "| is_curve:", arc.is_curve)
    print("  params (rx,ry,rot,large_arc,sweep):", arc.params)
    print("  圆心:", _pt(arc.arc_center()), "| 半径 50 → 圆心应在弧的垂直平分线上")
    _arc_len = arc.length()
    print("  弧长 ≈ %.2f （半圆）"
          % (_arc_len, _arc_len))

    # -----------------------------------------------------------------
    # 7) 直接构造 PathSegment（自己算好坐标时用，不需要画板）
    # -----------------------------------------------------------------
    print("\n=== 7) 直接构造 ===")
    s1 = PathSegment("M", (0, 0), (0, 0))
    s2 = PathSegment("L", (0, 0), (60, 40))
    s3 = PathSegment("C", (60, 40), (200, 0), ctrls=((100, 90), (160, 90)))
    s4 = PathSegment("Z", (200, 0), (0, 0))
    print("  自建路径:", segments_to_d([s1, s2, s3, s4]))
    print("  第 3 段类型/调整点数: /   segment 3 kind", s3.kind, s3.control_count)
```

---

## 同级模块

[editor](editor.zh.md) ｜ [htmleditor](htmleditor.zh.md) ｜ [parser](parser.zh.md) ｜ [point](point.zh.md)
