<!-- 本文件由 tools/gen_docs.py 从源码自动生成，请勿手改。
     要改内容请改同目录的 editor.py 里的文档字符串，然后重跑生成器。 -->

# editor.py

**简体中文** ｜ [English](editor.en.md) ｜ [← 返回 README](../../README.md)

路径编辑器（pathkit.editor）—— PathEditor 类

`PathElement` 的辅助类：把「一串 d 命令」变成**可看、可改的点**。

解决的问题：路径难用 —— 你看不到曲线有几个点、点在哪、拖了变成什么样。
本类提供四件事：

1. **看**：`describe()` 打印每段的起点 / 终点 / 调整点；
   `anchors` / `controls` 拿到全部锚点与控制点对象。
2. **改**：`move_anchor()` `move_control()` 拖任意一个点，改完自动写回路径。
3. **加/减**：`insert_anchor()` 在曲线上加点（形状不变）、`remove_anchor()` 合并点。
4. **可视化 / 存档**：`show()` 在画布上把锚点与调整杆画出来（像钢笔工具那样）；
   `save_json()` / `load_json()` 把点位导出改完再读回来。

使用示例

```python
from malight import Malight
from malight.pathkit import PathEditor

pen = Malight("demo", width=600, height=400)
p = pen.path(fill_color="none", stroke_color="#e63946", stroke_width=3)
p.move_to(60, 300)
p.cubic_to((120, 80), (260, 80), (320, 300))
p.quad_to((420, 120), (520, 300))

ed = PathEditor(p)          # 也可以用 p.editor()
print(ed.describe())        # 1) 看结构
ed.anchors[1].move_to(200, 60)         # 2) 拖锚点
ed.controls[0].move_by(0, -30)         #    拖调整点
ed.insert_anchor(1, 0.5)               # 3) 曲线中点加一个锚点
ed.show()                              # 4) 在画布上标出所有点

pen.finish()
```


---

## 类与方法

### `PathEditor`

路径编辑器：查看 / 调整 PathElement 的锚点与控制点。

| 方法 | 说明 |
|---|---|
| `reload()` | 重新从路径元素解析出线段 / 锚点 / 控制点（外部改过 d 后调用）。 |
| `to_d()` | 把当前（可能已被拖过的）点序列还原为 d 字符串（不写回路径）。 |
| `apply()` | 把当前点序列写回路径元素（拖点后自动调用，一般不用手动调）。 |
| `apply_structure()` | 结构发生变化（加点 / 删点 / 反转）后写回并重建点列表。 |
| `describe()` | 生成可读的路径结构说明（字符串，不打印）。 |
| `print_report()` | 打印路径结构说明（并返回同样内容）。 |
| `move_anchor(index, x, y, link_handles=False)` | 移动第 index 个锚点到 (x, y)。 |
| `move_control(seg_index, ctrl_index, x, y)` | 移动「第 seg_index 段」的第 ctrl_index 个调整点到 (x, y)。 |
| `curve_indices()` | 返回**带调整点**的线段序号列表（只有贝塞尔 / 圆弧段才有控制点）。 |
| `move_anchor_by(index, dx, dy)` | 相对移动锚点。 |
| `set_anchors(positions)` | 批量设置锚点坐标（适合外部算法算好一串新坐标后一次性回填）。 |
| `anchor_positions()` | 取出全部锚点坐标（便于打印 / 传给外部算法）。 |
| `control_positions()` | 取出全部控制点坐标。 |
| `insert_anchor(seg_index, t=0.5)` | 在第 seg_index 段上插入一个锚点（曲线形状保持不变）。 |
| `remove_anchor(index)` | 删除一个锚点（把它两侧的直线段合并为一条；曲线段暂不支持）。 |
| `reverse()` | 反转路径方向（起终点互换，形状不变）。 |
| `scale_all(sx, sy=None, cx=0, cy=0)` | 以 (cx, cy) 为中心整体缩放所有点（直接改坐标，不是 transform）。 |
| `to_dict()` | 导出为可 JSON 序列化的字典（点位存档）。 |
| `save_json(file)` | 把路径点位存成 JSON（方便外部工具/脚本批量调点再读回）。 |
| `load_json(file, apply=True)` | 读取 JSON 点位并回填到路径（配合 save_json 使用）。 |
| `to_html(**kwargs)` | 导出「可拖拽的单文件 HTML 编辑器」的源码（字符串）。 |
| `save_html(file, **kwargs)` | 把「可拖拽的单文件 HTML 编辑器」写到磁盘，返回绝对路径。 |
| `show(board=None, anchor_color='#e63946', control_color='#1d3557', handle_color='#457b9d', size=4, labels=False, id_=None)` | 在画布上把锚点与调整杆画出来（像钢笔工具那样），方便对照调整。 |
| `closed`（属性） | 路径是否闭合（最后一段是 Z）。 |
| `anchor_count`（属性） | 锚点个数。 |
| `control_count`（属性） | 控制点（调整点）个数。 |

---

## 完整示例

在 PyCharm 里点绿色三角直接运行，或命令行：`python malight/pathkit/editor.py`

```python
if __name__ == "__main__":
    import os

    from malight import Malight, ColorName
    from malight.pathkit import PathEditor

    _out = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        "..", "..", "output"))
    os.makedirs(_out, exist_ok=True)
    pen = Malight(os.path.join(_out, "demo_path_editor"), width=660, height=430)
    pen.set_background_color(ColorName.WHITESMOKE)

    # -----------------------------------------------------------------
    # 1) 先造一条路径：起笔 M -> 直线 L -> 三次贝塞尔 C -> 二次贝塞尔 Q
    #    段号依次是 0(M) / 1(L) / 2(C) / 3(Q)
    # -----------------------------------------------------------------
    p = pen.path(fill_color="none", stroke_color=ColorName.DARKSLATEGRAY,
                 stroke_width=3)
    p.move_to(60, 300)
    p.line_to(140, 180)
    p.cubic_to((200, 80), (300, 80), (360, 180))
    p.quad_to((430, 250), (520, 190))

    # -----------------------------------------------------------------
    # 2) 构造编辑器：PathEditor(p) 与 p.editor() 完全等价
    #    读统计信息：段数 / 锚点数 / 调整点数 / 是否闭合
    # -----------------------------------------------------------------
    ed = PathEditor(p)
    print("段数:", len(ed.segments),
          "| 锚点数:", ed.anchor_count,
          "| 调整点数:", ed.control_count,
          "| 是否闭合:", ed.closed)

    # -----------------------------------------------------------------
    # 3) 看结构：describe() 返回字符串，report 是它的别名，
    #    print_report() 打印并返回同样内容（三选一即可）
    # -----------------------------------------------------------------
    print(ed.describe())
    assert ed.report() == ed.describe()          # 别名，内容一致
    # 想直接打印时用 ed.print_report()

    # -----------------------------------------------------------------
    # 4) 看点位：锚点 / 调整点的纯坐标列表（便于打印或丢给外部算法）
    # -----------------------------------------------------------------
    print("锚点坐标:", ed.anchor_positions())
    print("调整点坐标:", ed.control_positions())

    # -----------------------------------------------------------------
    # 5) 拖点：锚点按序号拖（支持负数），调整点必须先知道哪几段是曲线
    #    直线段没有调整点，move_control 传错段号会给出明确提示
    # -----------------------------------------------------------------
    print("带调整点的段号:", ed.curve_indices())      # 例：[2, 3]
    ed.move_anchor(0, 70, 310)                       # 把起点拖到 (70,310)
    # 首个锚点在 d 串里就是 M 段；这一改必须真的落进 d 串 ——
    # 曾经只登记了 start 引用而 to_d() 用 end，导致拖首个锚点毫无反应
    assert ed.to_d().startswith("M70,310"), ed.to_d()
    ed.move_anchor(-1, 540, 200)                     # -1 = 最后一个锚点
    ed.move_anchor_by(1, 0, -15)                     # 相对移动：上移 15
    ed.move_control(ed.curve_indices()[0], 0, 210, 100)   # 第 1 条曲线的第 1 个调整点
    print("拖动后 d:", ed.to_d())

    # -----------------------------------------------------------------
    # 6) 批量设置锚点坐标（外部算法算好一串新坐标后一次性回填）
    # -----------------------------------------------------------------
    ed.set_anchors([(80, 300), (170, 170), (300, 90), (400, 190), (500, 230)])

    # -----------------------------------------------------------------
    # 7) 加点：在曲线上插入一个锚点，**形状保持不变**
    # -----------------------------------------------------------------
    ed.insert_anchor(ed.curve_indices()[0], 0.5)
    print("加点后锚点数:", ed.anchor_count)

    # -----------------------------------------------------------------
    # 8) 删点：只对「两侧都是直线段」的拐点有效（曲线请改调整点来简化）
    # -----------------------------------------------------------------
    q = pen.path(fill_color="none", stroke_color=ColorName.SEAGREEN,
                 stroke_width=3)
    q.move_to(60, 390)
    q.line_to(170, 390)
    q.line_to(270, 345)
    q.line_to(380, 390)
    qe = PathEditor(q)
    print("删点前:", qe.to_d())
    qe.remove_anchor(2)                     # 去掉中间那个拐点，两条直线合并
    print("删点后:", qe.to_d())

    # -----------------------------------------------------------------
    # 9) 反转方向（起终点互换，形状不变）+ 整体缩放（直接改坐标，不是 transform）
    # -----------------------------------------------------------------
    ed.reverse()
    ed.scale_all(0.95, 0.95, cx=300, cy=220)
    print("反转+缩放后:", ed.to_d())

    # -----------------------------------------------------------------
    # 10) 存档：to_dict() 拿可 JSON 化的数据 → save_json() 落盘 →
    #     外部随便改 → load_json() 读回并立即写回路径
    # -----------------------------------------------------------------
    data = ed.to_dict()
    data["segments"][-1]["end"] = [560, 210]        # 模拟外部算法改动
    print("存档字典键:", list(data.keys()))
    _json = os.path.join(_out, "path_editor_points.json")
    ed.save_json(_json)
    ed.load_json(_json)                             # 读回并应用到路径
    print("读回后 d:", ed.to_d())

    # -----------------------------------------------------------------
    # 11) 手动重解析：外部直接改过 d 串后，让编辑器重新读一遍
    # -----------------------------------------------------------------
    p.set_d("M80,120 C160,40 260,40 340,120 L520,120")
    ed.reload()
    print("reload 后段数:", len(ed.segments))

    # -----------------------------------------------------------------
    # 12) apply() / apply_structure()：拖点会**自动**写回，一般不用手动调；
    #     apply_structure() 用于结构变化后重建点列表（加点/删点/反转已自动调用）
    # -----------------------------------------------------------------
    ed.apply()
    ed.apply_structure()
    print("apply 后锚点数:", ed.anchor_count)

    # -----------------------------------------------------------------
    # 13) 可视化：把锚点（方块）+ 调整杆（线）+ 调整点（圆点）画在画布上
    #     labels=True 时还会标出锚点序号，方便对照微调
    # -----------------------------------------------------------------
    ed.show(labels=True)

    pen.finish()
```

---

## 同级模块

[htmleditor](htmleditor.zh.md) ｜ [parser](parser.zh.md) ｜ [point](point.zh.md) ｜ [segment](segment.zh.md)
