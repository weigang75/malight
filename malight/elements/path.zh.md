<!-- 本文件由 tools/gen_docs.py 从源码自动生成，请勿手改。
     要改内容请改同目录的 path.py 里的文档字符串，然后重跑生成器。 -->

# path.py

**简体中文** ｜ [English](path.en.md) ｜ [← 返回 README](../../README.md)

PathElement 路径元素（对应中文版 路径元素）。

路径命令与 SVG path d 语法一一对应：移动/直线/水平垂直线/
二次与三次贝塞尔/圆弧/闭合；另支持布尔运算、变换、平滑、
乌龟式转向（前进/转角/圆角）等高级能力。

---

## 类与方法

### `PathElement`

路径元素（对应中文版 `路径元素`）。

| 方法 | 说明 |
|---|---|
| `get_d()` | 获取路径的 d 字符串（对应中文版 `获取路径d`）。 |
| `set_d(d)` | 直接设置 SVG path 的 d 字符串（英文版新增，对应原版 `原生path`）。 |
| `move_to(x, y=None)` | 抬笔移动到指定点（不画线），并开启新子路径（对应中文版 `移动到`/`落笔`）。 |
| `line_to(end_x, end_y=None)` | 从当前点画直线到目标点（对应中文版 `画直线`）。 |
| `h_line_to(end_x)` | 水平线到 end_x（对应中文版 `画水平线`）。 |
| `v_line_to(end_y)` | 垂直线到 end_y（对应中文版 `画垂直线`）。 |
| `cubic_to(ctrl1, ctrl2, end)` | 三次贝塞尔曲线（对应中文版 `三次贝塞尔曲线`/`画曲线`）。 |
| `smooth_cubic_to(ctrl2, end)` | 平滑三次贝塞尔（自动反射前一控制点，对应中文版 `平滑曲线`）。 |
| `quad_to(ctrl, end)` | 二次贝塞尔曲线（对应中文版 `二次贝塞尔曲线`）。 |
| `smooth_quad_to(end)` | 平滑二次贝塞尔（对应中文版 `平滑的二次贝塞尔曲线`）。 |
| `ellipse_arc_to(rx, ry, end, sweep=0, large_arc=False, x_axis_rotation=0)` | 椭圆弧（对应中文版 `画椭圆弧`）。 |
| `arc_to(radius, end, sweep=0, large_arc=False)` | 圆弧（对应中文版 `画圆弧`）。 |
| `circle_to(center, sweep=0)` | 在路径中以圆弧画完整圆（对应中文版 `画圆`）。 |
| `close()` | 闭合当前子路径（回到子路径起点，对应中文版 `闭合`）。 |
| `new_subpath(x=None, y=None, **kw)` | 开启新子路径（对应中文版 `新路径`）：同一元素里画不相连的多段。 |
| `forward(length)` | 沿当前朝向前进并画线（对应中文版 `前进直线`）。 |
| `backward(length)` | 沿当前朝向后退并画线（对应中文版 `后退直线`）。 |
| `turn_right_move(angle, distance=0)` | 右转 angle 度后移动（不画线）（对应中文版 `右转移动`）。 |
| `turn_left_move(angle, distance=0)` | 左转 angle 度后移动（对应中文版 `左转移动`）。 |
| `turn_right_line(angle, length)` | 右转 angle 度后画线（对应中文版 `右转直线`）。 |
| `turn_left_line(angle, length)` | 左转 angle 度后画线（对应中文版 `左转直线`）。 |
| `turn_right_arc(angle, radius)` | 右转圆弧：画一段向右弯的弧线（对应中文版 `右转弧线`）。 |
| `turn_left_arc(angle, radius)` | 左转圆弧（对应中文版 `左转弧线`）。 |
| `fillet(p1, p2, radius)` | 两线段之间倒圆角（对应中文版 `倒圆角直线`）： 从当前点经 p1 拐向 p2，拐角处以 radius 圆弧过渡。 |
| `translate_cmds(dx, dy)` | 平移路径的所有坐标点（对应中文版 `坐标平移`，直接改坐标而非 transform）。 |
| `reverse()` | 反转路径方向（对应中文版 `反向路径`）：起终点互换，形状不变。 |
| `merge(other)` | 合并另一条路径到本路径（对应中文版 `合并路径`）。 |
| `union(other)` | 并集（对应中文版 `并集`）：返回新路径元素。 |
| `intersect(other)` | 交集（对应中文版 `交集`）。 |
| `subtract(other)` | 差集（对应中文版 `差集`）。 |
| `to_point_list(samples=200)` | 采样路径为顶点列表（对应中文版 `路径点列表`），供布尔/测距等使用。 |
| `length(samples=48)` | 路径总长度（按段精确/近似求和，对应中文版 `路径长度`）。 |
| `point_at(ratio)` | 取路径上指定比例位置的坐标（按**弧长**定位，对应中文版 `位置坐标`）。 |
| `point_at_distance(dist, samples=48)` | 沿路径从起点走 dist 长度处的坐标（英文版新增）。 |
| `tangent_at(ratio, samples=48)` | 路径上 ratio 位置的**单位切线向量**（沿行进方向，英文版新增）。 |
| `tangent_angle_at(ratio, samples=48)` | 路径上 ratio 位置的切线角（度，0=向右、顺时针为正，与海龟朝向同义， 英文版新增）。 |
| `normal_at(ratio, side='left', samples=48)` | 路径上 ratio 位置的**单位法线向量**（英文版新增）。 |
| `distance_to(other, samples=200)` | 本路径与另一条路径的**最短距离**（双方按弧长均匀采样后求最近点对， 近似值，英文版新增）。 |
| `paste_line(distance, step=None, taper_angle=90.0, start=0.0, end=1.0, **kw)` | 沿路径生成**梯形单元组成的粘贴线**（英文版新增，贴纸花边效果）： 路径按弧长分成若干等长单元，每个单元是一条贴着路径的梯形 （底边在路径上、顶边偏移 `distance`），全部单元并入一条新路径。 |
| `slice(start=0.0, end=1.0, samples=48, **kw)` | 复制路径上指定**弧长区间**的一段，返回新路径（原路径不变， 英文版新增）。 |
| `bbox()` | 路径包围盒（按顶点采样近似）。 |
| `editor(refresh=False)` | 取得本路径的编辑器（可查看 / 拖动锚点与控制点）。 |
| `segments()` | 取路径的全部线段对象（每段含起点/终点/控制点）。 |
| `anchors()` | 取全部锚点对象（曲线的起点、终点、拐点）。 |
| `controls()` | 取全部控制点对象（贝塞尔曲线的调整点）。 |
| `anchor_points()` | 取全部锚点坐标（纯坐标版，便于打印 / 传参）。 |
| `control_points()` | 取全部控制点坐标（纯坐标版）。 |
| `move_anchor(index, x, y)` | 移动第 index 个锚点（改完立即生效）。 |
| `move_control(seg_index, ctrl_index, x, y)` | 移动「第 seg_index 段」的第 ctrl_index 个调整点（改完立即生效）。 |
| `describe()` | 生成路径结构说明（每段的起点/调整点/终点 + 全部锚点坐标）。 |
| `print_points()` | 打印路径结构说明（看曲线有几个点、点在哪）。 |
| `show_points(board=None, **kw)` | 在画布上画出锚点（方块）与调整杆（线 + 圆点），像钢笔工具一样。 |
| `smooth(tightness=1.0)` | 把路径中的折线顶点平滑为贝塞尔曲线（Catmull-Rom 转样条， 对应中文版 `平滑路径`）。 |

---

## 完整示例

在 PyCharm 里点绿色三角直接运行，或命令行：`python malight/elements/path.py`

```python
if __name__ == "__main__":
    import os

    from malight import Malight, ColorName, FillRule
    from malight.pathkit import PathEditor

    _out = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        "..", "..", "output"))
    pen = Malight(os.path.join(_out, "demo_path"), width=660, height=420)
    pen.set_background_color(ColorName.WHITESMOKE)

    # -----------------------------------------------------------------
    # 1) 命令式绘制：移动 / 直线 / 贝塞尔 / 圆弧 / 闭合
    # -----------------------------------------------------------------
    p = pen.path(fill_color="none", stroke_color=ColorName.TOMATO,
                 stroke_width=3)
    p.move_to(60, 320)                                  # 起笔
    p.line_to(140, 180)                                 # 直线
    p.cubic_to((200, 80), (300, 80), (360, 180))        # 三次贝塞尔（2 个控制点）
    p.quad_to((420, 240), (480, 180))                   # 二次贝塞尔（1 个控制点）
    p.arc_to(40, (560, 240), sweep=1)                   # 圆弧

    # -----------------------------------------------------------------
    # 2) 看结构：每一段的起点 / 调整点 / 终点都能打印出来
    # -----------------------------------------------------------------
    print(p.describe())          # 对应中文版「路径元素」的看点能力

    # -----------------------------------------------------------------
    # 3) 调整：拖动锚点与控制点（改完立刻写回路径，无需手动 apply）
    # -----------------------------------------------------------------
    print("锚点:", p.anchor_points())        # 所有锚点坐标
    print("调整点:", p.control_points())     # 所有贝塞尔控制柄坐标
    print("带调整点的段号:", p.editor().curve_indices())   # 直线段没有调整点
    p.anchors()[2].move_to(200, 90)          # 拖第 3 个锚点
    p.controls()[0].move_by(0, -20)          # 拖第 1 个调整点
    p.move_anchor(1, 150, 200)               # 也可以按索引直接改
    p.move_control(2, 0, 210, 100)           # 第 2 段（三次贝塞尔）的第 1 个调整点

    # -----------------------------------------------------------------
    # 4) 结构编辑：加点（形状不变）/ 反转方向 / 点位存档
    # -----------------------------------------------------------------
    ed = p.editor()                          # 等价于 PathEditor(p)
    ed.insert_anchor(1, 0.5)                 # 在第 1 段中点插入锚点（形状不变）
    ed.reverse()                             # 起终点互换
    ed.save_json(os.path.join(_out, "path_points.json"))   # 点位存档

    # 5) 可视化：把锚点（方块）与调整杆（线 + 圆点）画出来看
    p.show_points(labels=True)

    # -----------------------------------------------------------------
    # 6) 几何信息：长度 / 弧长取点 / 切线法线 / 包围盒 / 平移所有命令
    # -----------------------------------------------------------------
    _len = p.length()
    print("路径长度 ≈ %.2f" % (_len, _len))
    print("弧长 30%% 处坐标:", tuple(round(v, 2) for v in p.point_at(0.3)))
    print("切线向量", tuple(round(v, 3) for v in p.tangent_at(0.3)),
          "| 切线角", round(p.tangent_angle_at(0.3), 2))
    print("左法线", tuple(round(v, 3) for v in p.normal_at(0.3)))
    print("绝对弧长 50 处:", tuple(round(v, 2) for v in p.point_at_distance(50)))
    print("包围盒:", tuple(round(v, 1) for v in p.bbox()))

    # -----------------------------------------------------------------
    # 6b) 沿路径贴一圈梯形粘贴线
    # -----------------------------------------------------------------
    trim = p.paste_line(14, step=16, fill_color=ColorName.LAVENDER,
                        stroke_color=ColorName.DIMGRAY, stroke_width=0.6)
    print("粘贴线段数:", trim.get_d().count("Z"))

    # -----------------------------------------------------------------
    # 7) 更多绘制命令：水平/垂直直线、整圆、平滑连接、圆角
    # -----------------------------------------------------------------
    q = pen.path(fill_color="none", stroke_color=ColorName.STEELBLUE,
                 stroke_width=3)
    q.move_to(60, 380)
    q.h_line_to(200)                 # 水平线
    q.v_line_to(350)                 # 垂直线
    pen.text(280, 400, "h_line_to / v_line_to", font_size=13,
             fill_color=ColorName.DIMGRAY, h_align="middle")

    ring = pen.path(fill_color="none", stroke_color=ColorName.SEAGREEN,
                    stroke_width=3)
    ring.move_to(560, 340)           # 先定一个点（半径 = 它与圆心的距离）
    ring.circle_to((560, 385))       # 画整圆

    # -----------------------------------------------------------------
    # 8) 填充规则：即使是一条 path 也能用 EVENODD 挖洞（多子路径）
    # -----------------------------------------------------------------
    ring2 = pen.path(fill_color=ColorName.TEAL, fill_rule=FillRule.EVENODD,
                     stroke_color="none")
    ring2.move_to(490, 60)
    ring2.circle_to((490, 105))      # 外圈（半径 45）
    ring2.new_subpath(490, 75)       # 起一条新子路径 = 内圈起点
    ring2.circle_to((490, 105))      # 内圈（半径 30）→ 与 EVENODD 配合挖出孔洞

    # -----------------------------------------------------------------
    # 9) 布尔运算（两个路径求并/交/差，返回新 PathElement）
    # -----------------------------------------------------------------
    a = pen.path(fill_color="none", stroke_color=ColorName.NAVY)
    a.move_to(100, 60)
    a.circle_to((130, 90))
    b = pen.path(fill_color="none", stroke_color=ColorName.CRIMSON)
    b.move_to(150, 60)
    b.circle_to((130, 90))
    try:
        merged = a.union(b)
        print("布尔并集结果 d 长度:", len(merged.get_d()))
    except Exception as exc:                 # 需要 shapely 等可选依赖
        print("布尔运算需要可选依赖，跳过:", type(exc).__name__)

    pen.finish()
    pen.svg_editor()
# ---------------------------------------------------------------------------
# 底部导入：show_points() 的返回注解引用 GroupElement，而 group.py 又继承本模块
# 的 Element —— 顶部互相导入会循环；放到文件末尾两个问题都解决。
# ---------------------------------------------------------------------------
from .group import GroupElement  # noqa: E402
```

---

## 同级模块

[base](base.zh.md) ｜ [circle](circle.zh.md) ｜ [clippath](clippath.zh.md) ｜ [ellipse](ellipse.zh.md) ｜ [group](group.zh.md) ｜ [image](image.zh.md) ｜ [line](line.zh.md) ｜ [link](link.zh.md) ｜ [marker](marker.zh.md) ｜ [mask](mask.zh.md) ｜ [pattern](pattern.zh.md) ｜ [polygon](polygon.zh.md) ｜ [polyline](polyline.zh.md) ｜ [rect](rect.zh.md) ｜ [svggroup](svggroup.zh.md) ｜ [svgimage](svgimage.zh.md) ｜ [symbol](symbol.zh.md) ｜ [text](text.zh.md) ｜ [textpath](textpath.zh.md) ｜ [topath](topath.zh.md) ｜ [use](use.zh.md)
