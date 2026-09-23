# -*- coding: utf-8 -*-
"""
路径可调点（pathkit.point）—— PathPoint 类
============================================

PathPoint: a single draggable anchor or control point.

`PathPoint` 表示路径上**一个可以拖动调整的点**，分两种：

- **锚点（anchor）**：曲线的起点 / 终点 / 拐点 —— 钢笔工具里的实心方点
- **控制点（control）**：贝塞尔曲线的「调整杆」端点 —— 拖它就改变曲线弧度

它就是中文版「路径元素」里那个「能看到曲线起始点、终点、调整点位置」的能力，
英文版把它做成了可读可改的普通对象。

使用示例::

    from malight.pathkit import PathEditor

    ed = PathEditor(path)

    # 看：打印出每个点的类型和坐标
    for pt in ed.anchors:
        print(pt)                  # <锚点#0 (50, 50)>

    # 改：直接拖点（改完自动写回路径，无需手动 apply）
    ed.anchors[1].move_to(220, 80)
    ed.controls[0].move_by(10, -20)
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
    __package__ = "malight.pathkit"


from ..i18n import t
class PathPoint:
    """
    路径上的一个可调点（锚点或控制点）。 / A draggable point on a path: an anchor or a control point.

    通常由 `PathEditor.anchors` / `PathEditor.controls` 得到，不用自己创建。

    常用属性与方法::

        pt.pos          # (x, y) 当前坐标
        pt.x, pt.y      # 单轴坐标
        pt.kind         # "anchor"（锚点）/ "control"（控制点）
        pt.role         # 中文角色，如 "锚点#2" / "第3段·调整点1"
        pt.move_to(x, y)    # 移到指定位置（立即写回路径）
        pt.move_by(dx, dy)  # 相对移动
    """

    __slots__ = ("_refs", "kind", "index", "editor", "seg_index", "ctrl_index")

    def __init__(self, refs, kind, index, editor,
                 seg_index=None, ctrl_index=None):
        """
        :param refs: 内部引用列表 [(segment, "start"/"end"/"ctrl", ctrl下标), ...]
        :param kind: "anchor" 或 "control"
        :param index: 在 anchors/controls 列表中的序号
        :param editor: 所属 PathEditor（用于写回）
        """
        self._refs = list(refs)
        self.kind = kind
        self.index = index
        self.editor = editor
        self.seg_index = seg_index
        self.ctrl_index = ctrl_index

    # ---------------------------------------------------------------
    # 坐标读取
    # ---------------------------------------------------------------
    def _read(self):
        """读当前坐标（内部方法）。"""
        seg, field, *_ = self._refs[0]
        if field == "start":
            return seg.start
        if field == "end":
            return seg.end
        return seg.ctrls[self._refs[0][2]]

    @property
    def pos(self):
        """当前坐标 (x, y)。 / Current position as an (x, y) pair. 示例:: pt.pos   # (120.0, 80.0)"""
        return self._read()

    @property
    def x(self):
        """当前 x 坐标。 / Current x coordinate. 示例:: pt.x"""
        return self._read()[0]

    @property
    def y(self):
        """当前 y 坐标。 / Current y coordinate. 示例:: pt.y"""
        return self._read()[1]

    @property
    def role(self):
        """
        角色说明，跟随语言设置（英文 "anchor#2" / 中文 "锚点#2"）。 / Human-readable role; follows the current language.

        示例:: pt.role -> "anchor#2"
        """
        if self.kind == "anchor":
            return t("pt.anchor", index=self.index)
        return t("pt.control", seg=self.seg_index, ctrl=self.ctrl_index)

    # ---------------------------------------------------------------
    # 调整
    # ---------------------------------------------------------------
    def move_to(self, x, y) -> "PathPoint":
        """
        把点移动到指定坐标（立即写回路径元素）。 / Move the point to a coordinate and write it back to the path immediately.

        :return: self（可链式）

        示例::
            ed.anchors[0].move_to(100, 100)
            ed.anchors[2].move_to(300, 150).move_by(0, 10)
        """
        x, y = float(x), float(y)
        for ref in self._refs:
            seg, field = ref[0], ref[1]
            if field == "start":
                seg.start = (x, y)
            elif field == "end":
                seg.end = (x, y)
            else:
                items = list(seg.ctrls)
                items[ref[2]] = (x, y)
                seg.ctrls = tuple(items)
        if self.editor is not None:
            self.editor.apply()
        return self

    def move_by(self, dx, dy) -> "PathPoint":
        """
        相对移动（立即写回路径元素）。 / Move the point by a relative offset and write it back immediately.

        :param dx: x 方向位移
        :param dy: y 方向位移

        示例::
            ed.anchors[1].move_by(0, -20)   # 上移 20
        """
        x, y = self._read()
        return self.move_to(x + dx, y + dy)

    # ---------------------------------------------------------------
    # 便捷协议
    # ---------------------------------------------------------------
    def __iter__(self):
        """支持 `x, y = point` 解包。"""
        return iter(self._read())

    def __eq__(self, other):
        return (isinstance(other, PathPoint)
                and tuple(round(v, 6) for v in self.pos)
                == tuple(round(v, 6) for v in other.pos)
                and self.kind == other.kind)

    # 定义了 __eq__ 之后默认不可哈希，这里显式恢复（点对象可用于 set/dict）
    __hash__ = object.__hash__

    def __repr__(self):
        # 走 i18n，不写死中文：默认英文输出时 repr 就是 <anchor#0 (50, 50)>
        p = self._read()
        return "<{} ({}, {})>".format(self.role, round(p[0], 2), round(p[1], 2))



# ===========================================================================
# 使用示例
# ===========================================================================
# 在 PyCharm 里点绿色三角直接运行本文件即可；也可命令行：
#     python -m malight.pathkit.point
# 本示例覆盖 PathPoint 的全部能力：
#     pos / x / y / kind / index / role / seg_index / ctrl_index
#     move_to / move_by
#     __iter__（解包）/ __eq__ / __hash__ / __repr__
# 注意：PathPoint 通常不自己 new，而是从 PathEditor.anchors / .controls 取。
# ===========================================================================
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
    # 0) 准备一条路径（每段都给足锚点与调整点） / 0) Prepare a path whose segments have anchors and control points
    # -----------------------------------------------------------------
    p = pen.path(fill_color="none", stroke_color=ColorName.CRIMSON,
                 stroke_width=3)
    p.move_to(60, 300)
    p.cubic_to((140, 90), (280, 90), (360, 300))
    p.quad_to((440, 180), (560, 280))
    ed = PathEditor(p)

    # -----------------------------------------------------------------
    # 1) 锚点对象：常用属性一览 / 1) Anchor objects: the everyday attributes
    #    pos=(x,y)  x/y=单轴  kind=类型  index=序号  role=中文角色 / pos=(x,y), x/y single axis, kind, index and role
    #    repr 是中文短描述，print 列表时很直观 / repr is a short readable description, handy when printing lists
    # -----------------------------------------------------------------
    print("=== 锚点 === / === anchors ===")
    for a in ed.anchors:
        print("  repr:", repr(a),
              "| kind:", a.kind,
              "| index:", a.index,
              "| role:", a.role,
              "| pos:", a.pos,
              "| x/y:", a.x, a.y)

    # -----------------------------------------------------------------
    # 2) 控制点对象：额外带 seg_index / ctrl_index（属于第几段的第几个柄） / 2) Control points also carry seg_index / ctrl_index
    # -----------------------------------------------------------------
    print("=== 调整点 === / === control points ===")
    for c in ed.controls:
        print("  repr:", repr(c),
              "| kind:", c.kind,
              "| index:", c.index,
              "| seg_index:", c.seg_index,
              "| ctrl_index:", c.ctrl_index,
              "| pos:", c.pos)

    # -----------------------------------------------------------------
    # 3) 解包：点对象可以直接 x, y = pt（省去 .pos） / 3) Unpack a point: x, y = pt, no .pos needed
    # -----------------------------------------------------------------
    x, y = ed.anchors[0]
    print("解包第 1 个锚点: / first anchor unpacked:", x, y)

    # -----------------------------------------------------------------
    # 4) 拖点：move_to 绝对移动、move_by 相对移动，都会立即写回路径 / 4) move_to and move_by both write straight back to the path
    #    返回 self，所以可以链式连续拖 / they return self, so drags chain
    # -----------------------------------------------------------------
    ed.anchors[1].move_to(180, 70)
    ed.anchors[1].move_by(0, 15)                 # 再下移 15 / then move down another 15
    ed.controls[0].move_by(-20, -10)             # 调整点：改变曲线弧度 / a control point changes the curvature
    print("拖动后 d: / d after dragging:", ed.to_d())

    # -----------------------------------------------------------------
    # 5) 控制点也可以按「第几段第几个」精确定位（与编辑器 move_control 等价） / 5) Address a control point by segment and index, like editor move_control
    # -----------------------------------------------------------------
    for c in ed.controls:
        if c.seg_index == ed.curve_indices()[0] and c.ctrl_index == 1:
            c.move_to(320, 110)
            print("第 {} 段第 {} 个调整点拖到 (320,110) / segment {} control point {} moved to (320,110)".format(
                c.seg_index, c.ctrl_index, c.seg_index, c.ctrl_index))

    # -----------------------------------------------------------------
    # 6) 相等与哈希：同坐标同类型的点视为相等；点对象可放进 set / dict
    # -----------------------------------------------------------------
    print("anchors[0] == anchors[0]:", ed.anchors[0] == ed.anchors[0])
    print("anchors[0] == anchors[1]:", ed.anchors[0] == ed.anchors[1])
    print("去重后的点数 {}/{} / unique {}/{}".format(
        len(set(ed.anchors + ed.controls)),
        len(ed.anchors) + len(ed.controls),
        len(set(ed.anchors + ed.controls)),
        len(ed.anchors) + len(ed.controls)))

    # -----------------------------------------------------------------
    # 7) 可视化：把这些点画出来，序号与坐标一一对应，方便照着手动微调 / 7) Draw the points, numbered to match, for manual fine-tuning
    # -----------------------------------------------------------------
    ed.show(labels=True)

    pen.finish()
