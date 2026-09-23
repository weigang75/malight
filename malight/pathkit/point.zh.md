<!-- 本文件由 tools/gen_docs.py 从源码自动生成，请勿手改。
     要改内容请改同目录的 point.py 里的文档字符串，然后重跑生成器。 -->

# point.py

**简体中文** ｜ [English](point.en.md) ｜ [← 返回 README](../../README.md)

路径可调点（pathkit.point）—— PathPoint 类

`PathPoint` 表示路径上**一个可以拖动调整的点**，分两种：

- **锚点（anchor）**：曲线的起点 / 终点 / 拐点 —— 钢笔工具里的实心方点
- **控制点（control）**：贝塞尔曲线的「调整杆」端点 —— 拖它就改变曲线弧度

它就是中文版「路径元素」里那个「能看到曲线起始点、终点、调整点位置」的能力，
英文版把它做成了可读可改的普通对象。

使用示例

```python
from malight.pathkit import PathEditor

ed = PathEditor(path)

# 看：打印出每个点的类型和坐标
for pt in ed.anchors:
    print(pt)                  # <锚点#0 (50, 50)>

# 改：直接拖点（改完自动写回路径，无需手动 apply）
ed.anchors[1].move_to(220, 80)
ed.controls[0].move_by(10, -20)
```


---

## 类与方法

### `PathPoint`

路径上的一个可调点（锚点或控制点）。

| 方法 | 说明 |
|---|---|
| `move_to(x, y)` | 把点移动到指定坐标（立即写回路径元素）。 |
| `move_by(dx, dy)` | 相对移动（立即写回路径元素）。 |
| `pos`（属性） | 当前坐标 (x, y)。 |
| `x`（属性） | 当前 x 坐标。 |
| `y`（属性） | 当前 y 坐标。 |
| `role`（属性） | 角色说明，跟随语言设置（英文 "anchor#2" / 中文 "锚点#2"）。 |

---

## 完整示例

在 PyCharm 里点绿色三角直接运行，或命令行：`python malight/pathkit/point.py`

```python
if __name__ == "__main__":
    import os

    from malight import Malight, ColorName
    from malight.pathkit import PathEditor

    _out = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        "..", "..", "output"))
    os.makedirs(_out, exist_ok=True)
    pen = Malight(os.path.join(_out, "demo_path_point"), width=640, height=400)
    pen.set_background_color(ColorName.WHITESMOKE)

    # -----------------------------------------------------------------
    # 0) 准备一条路径（每段都给足锚点与调整点）
    # -----------------------------------------------------------------
    p = pen.path(fill_color="none", stroke_color=ColorName.CRIMSON,
                 stroke_width=3)
    p.move_to(60, 300)
    p.cubic_to((140, 90), (280, 90), (360, 300))
    p.quad_to((440, 180), (560, 280))
    ed = PathEditor(p)

    # -----------------------------------------------------------------
    # 1) 锚点对象：常用属性一览
    #    pos=(x,y)  x/y=单轴  kind=类型  index=序号  role=中文角色
    #    repr 是中文短描述，print 列表时很直观
    # -----------------------------------------------------------------
    print("=== 锚点 ===")
    for a in ed.anchors:
        print("  repr:", repr(a),
              "| kind:", a.kind,
              "| index:", a.index,
              "| role:", a.role,
              "| pos:", a.pos,
              "| x/y:", a.x, a.y)

    # -----------------------------------------------------------------
    # 2) 控制点对象：额外带 seg_index / ctrl_index（属于第几段的第几个柄） / 2) Control points also carry seg_index
    # -----------------------------------------------------------------
    print("=== 调整点 ===")
    for c in ed.controls:
        print("  repr:", repr(c),
              "| kind:", c.kind,
              "| index:", c.index,
              "| seg_index:", c.seg_index,
              "| ctrl_index:", c.ctrl_index,
              "| pos:", c.pos)

    # -----------------------------------------------------------------
    # 3) 解包：点对象可以直接 x, y = pt（省去 .pos）
    # -----------------------------------------------------------------
    x, y = ed.anchors[0]
    print("解包第 1 个锚点:", x, y)

    # -----------------------------------------------------------------
    # 4) 拖点：move_to 绝对移动、move_by 相对移动，都会立即写回路径
    #    返回 self，所以可以链式连续拖
    # -----------------------------------------------------------------
    ed.anchors[1].move_to(180, 70)
    ed.anchors[1].move_by(0, 15)                 # 再下移 15
    ed.controls[0].move_by(-20, -10)             # 调整点：改变曲线弧度
    print("拖动后 d:", ed.to_d())

    # -----------------------------------------------------------------
    # 5) 控制点也可以按「第几段第几个」精确定位（与编辑器 move_control 等价）
    # -----------------------------------------------------------------
    for c in ed.controls:
        if c.seg_index == ed.curve_indices()[0] and c.ctrl_index == 1:
            c.move_to(320, 110)
            print("第 {} 段第 {} 个调整点拖到 (320,110)".format(
                c.seg_index, c.ctrl_index, c.seg_index, c.ctrl_index))

    # -----------------------------------------------------------------
    # 6) 相等与哈希：同坐标同类型的点视为相等；点对象可放进 set
    # -----------------------------------------------------------------
    print("anchors[0] == anchors[0]:", ed.anchors[0] == ed.anchors[0])
    print("anchors[0] == anchors[1]:", ed.anchors[0] == ed.anchors[1])
    print("去重后的点数 {}/{}".format(
        len(set(ed.anchors + ed.controls)),
        len(ed.anchors) + len(ed.controls),
        len(set(ed.anchors + ed.controls)),
        len(ed.anchors) + len(ed.controls)))

    # -----------------------------------------------------------------
    # 7) 可视化：把这些点画出来，序号与坐标一一对应，方便照着手动微调
    # -----------------------------------------------------------------
    ed.show(labels=True)

    pen.finish()
```

---

## 同级模块

[editor](editor.zh.md) ｜ [htmleditor](htmleditor.zh.md) ｜ [parser](parser.zh.md) ｜ [segment](segment.zh.md)
