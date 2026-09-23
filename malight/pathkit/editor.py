# -*- coding: utf-8 -*-
"""
路径编辑器（pathkit.editor）—— PathEditor 类
==============================================

PathEditor: read the structure, drag anchors and control points, insert or drop points, save point data.

`PathElement` 的辅助类：把「一串 d 命令」变成**可看、可改的点**。

解决的问题：路径难用 —— 你看不到曲线有几个点、点在哪、拖了变成什么样。
本类提供四件事：

1. **看**：``describe()`` 打印每段的起点 / 终点 / 调整点；
   ``anchors`` / ``controls`` 拿到全部锚点与控制点对象。
2. **改**：``move_anchor()`` ``move_control()`` 拖任意一个点，改完自动写回路径。
3. **加/减**：``insert_anchor()`` 在曲线上加点（形状不变）、``remove_anchor()`` 合并点。
4. **可视化 / 存档**：``show()`` 在画布上把锚点与调整杆画出来（像钢笔工具那样）；
   ``save_json()`` / ``load_json()`` 把点位导出改完再读回来。

使用示例::

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

import json
import os

# Element 只用于类型注解；用 try/except 兜底，保证任意导入顺序下都不会循环导入
try:

    from ..elements.base import Element
except ImportError:                      # pragma: no cover - 极端导入顺序兜底
    Element = object

from .parser import parse_path_d, segments_to_d, reverse_segments
from .point import PathPoint
from ..i18n import t
from ..tools import paint_path
from .segment import kind_text


class PathEditor:
    """
    路径编辑器：查看 / 调整 PathElement 的锚点与控制点。 / Path editor: inspect and adjust a PathElement's anchors and control points.

    构造方式::

        ed = PathEditor(path)      # 直接构造
        ed = path.editor()         # 或从路径元素拿（推荐，绘图板方法）
    """

    def __init__(self, path, auto_apply=True):
        """
        :param path: 要编辑的 PathElement
        :param auto_apply: 拖点后是否自动写回路径（默认 True，最省心）
        """
        self.path = path
        self.auto_apply = auto_apply
        self.segments = []
        self.anchors = []
        self.controls = []
        self._anchor_refs = []
        self.reload()

    # ---------------------------------------------------------------
    # 解析 / 写回
    # ---------------------------------------------------------------
    def reload(self) -> "PathEditor":
        """
        重新从路径元素解析出线段 / 锚点 / 控制点（外部改过 d 后调用）。 / Re-parse segments, anchors and control points from the path element, for use after d changed externally.

        :return: self

        示例::
            path.set_d("M0,0 L100,0")
            ed.reload()     # 让编辑器重新读一遍
        """
        self.segments = parse_path_d(self.path.get_d())
        anchor_refs = []
        control_refs = []
        last = None
        for si, seg in enumerate(self.segments):
            if seg.cmd == "M":
                # 新子路径：M 点自身就是一个锚点。
                # 起点与终点**都要登记**：to_d() 渲染 M 用的是 end，
                # 只挂 start 会让「拖动首个锚点」毫无反应（改动写不回 d 串里）。
                last = [(seg, "start", None), (seg, "end", None)]
                anchor_refs.append(last)
                continue
            # 可绘制段：起点与前一个锚点共享，没有则新建
            if last is not None:
                last.append((seg, "start", None))
            else:
                last = [(seg, "start", None)]
                anchor_refs.append(last)
            # 控制点（调整杆端点）
            for ci in range(len(seg.ctrls)):
                control_refs.append((si, ci))
            # 终点
            if seg.cmd == "Z":
                last = None            # 子路径结束
            else:
                last = [(seg, "end", None)]
                anchor_refs.append(last)

        self._anchor_refs = anchor_refs
        self.anchors = [PathPoint(refs, "anchor", i, self)
                        for i, refs in enumerate(anchor_refs)]
        self.controls = []
        for i, (si, ci) in enumerate(control_refs):
            seg = self.segments[si]
            self.controls.append(
                PathPoint([(seg, "ctrl", ci)], "control", i, self,
                          seg_index=si, ctrl_index=ci))
        return self

    def to_d(self) -> str:
        """
        把当前（可能已被拖过的）点序列还原为 d 字符串（不写回路径）。 / Rebuild a d string from the current point list without writing back to the path.

        示例::
            ed.to_d()      # "M50,50 C100,20 150,120 200,50 Z"
        """
        return segments_to_d(self.segments)

    def apply(self) -> "PathEditor":
        """
        把当前点序列写回路径元素（拖点后自动调用，一般不用手动调）。 / Write the current point list back to the path element; called automatically after dragging.

        :return: self

        示例::
            ed.anchors[0].move_to(10, 10)   # 已自动写回
            ed.apply()                      # 想手动确认也可以
        """
        self.path._cmds = [s.to_d() for s in self.segments if s.cmd]
        self.path._sync()
        self._sync_state()
        return self

    def apply_structure(self) -> "PathEditor":
        """
        结构发生变化（加点 / 删点 / 反转）后写回并重建点列表。 / Write back and rebuild the point list after a structural change such as inserting, removing or reversing.

        与 `apply()` 的区别：会重新生成 anchors / controls 列表，
        所以**改动前后拿到的点对象会换新**（普通拖动请用 move_* 系列）。

        :return: self
        """
        self.apply()
        self.reload()
        return self

    def _sync_state(self):
        """同步画笔内部状态（当前点 / 子路径起点），避免后续绘制命令接错位置。"""
        cur = (0.0, 0.0)
        start = (0.0, 0.0)
        for seg in self.segments:
            if seg.cmd == "M":
                start = seg.end
            cur = seg.end
        self.path._cur = cur
        self.path._start = start

    # ---------------------------------------------------------------
    # 统计信息
    # ---------------------------------------------------------------
    @property
    def closed(self):
        """路径是否闭合（最后一段是 Z）。 / Whether the path is closed, i.e. its last segment is Z. 示例:: ed.closed"""
        return bool(self.segments) and self.segments[-1].cmd == "Z"

    @property
    def anchor_count(self):
        """锚点个数。 / Number of anchors. 示例:: ed.anchor_count"""
        return len(self.anchors)

    @property
    def control_count(self):
        """控制点（调整点）个数。 / Number of control points. 示例:: ed.control_count"""
        return len(self.controls)

    def describe(self) -> str:
        """
        生成可读的路径结构说明（字符串，不打印）。 / Build a readable path report as a string, without printing it.

        :return: 多行文本

        示例::
            print(ed.describe())
        """
        lines = []
        lines.append(t("editor.title", segs=len(self.segments),
                        anchors=self.anchor_count,
                        ctrls=self.control_count,
                        closed=t("editor.closed") if self.closed
                        else t("editor.open")))
        lines.append("")
        lines.append(t("editor.table_head"))
        lines.append("  " + "-" * 76)
        for i, seg in enumerate(self.segments):
            fmt = lambda p: "({:.1f},{:.1f})".format(p[0], p[1])
            ctrls = " ".join(fmt(c) for c in seg.ctrls) or "-"
            lines.append("  {:<4}  {:<4}  {:<10}  {:<14}  {:<26}  {}".format(
                i, seg.cmd, kind_text(seg.cmd), fmt(seg.start), ctrls,
                fmt(seg.end)))
        lines.append("")
        lines.append(t("editor.anchors_head"))
        for a in self.anchors:
            lines.append("    {:<10} ({:.2f}, {:.2f})".format(a.role, a.x, a.y))
        if self.controls:
            lines.append(t("editor.controls_head"))
            for c in self.controls:
                lines.append("    {:<16} ({:.2f}, {:.2f})".format(c.role, c.x, c.y))
        return "\n".join(lines)

    # 别名：更符合直觉的名字
    report = describe

    def print_report(self) -> str:
        """
        打印路径结构说明（并返回同样内容）。 / Print the path report and return the same text.

        示例::
            ed.print_report()
        """
        txt = self.describe()
        print(txt)
        return txt

    # ---------------------------------------------------------------
    # 调整：移动点
    # ---------------------------------------------------------------
    def move_anchor(self, index, x, y, link_handles=False) -> "PathEditor":
        """
        移动第 index 个锚点到 (x, y)。 / Move the anchor at index to (x, y).

        :param link_handles: 是否让锚点两侧的贝塞尔调整杆跟着一起走（默认不跟）。
            为 True 时，锚点位移多少，挂在它这一侧的调整杆就位移多少 —— 切线方向
            随锚点一起平移，曲线不会突然拐个弯。网页版编辑器里的
            「锚点连动调整杆」勾选框就是它。
        :return: self（可链式）

        示例::
            ed.move_anchor(0, 60, 60)       # 把起点拖到 (60,60)
            ed.move_anchor(-1, 300, 200)    # 支持负数：-1 表示最后一个
            ed.move_anchor(1, 120, 90, link_handles=True)   # 连调整杆一起搬 / bring the handles along
        """
        anchor = self.anchors[int(index)]
        x, y = float(x), float(y)
        if link_handles:
            ox, oy = anchor.pos
            dx, dy = x - ox, y - oy
            for seg, field, _ in anchor._refs:
                # 只有「挂在本锚点这一侧的调整杆」才跟着走：C 的起点侧是
                # ctrls[0]、终点侧是 ctrls[1]；Q 只有一个调整杆且算在起点侧。
                if not seg.ctrls:
                    continue
                if field == "start":
                    k = 0
                elif field == "end" and seg.cmd == "C" and len(seg.ctrls) >= 2:
                    k = 1
                else:
                    continue
                items = list(seg.ctrls)
                items[k] = (items[k][0] + dx, items[k][1] + dy)
                seg.ctrls = tuple(items)
        anchor.move_to(x, y)
        return self

    def move_control(self, seg_index, ctrl_index, x, y) -> "PathEditor":
        """
        移动「第 seg_index 段」的第 ctrl_index 个调整点到 (x, y)。 / Move control point ctrl_index of segment seg_index to (x, y).

        只有贝塞尔曲线（C / Q）与圆弧（A）才有调整点；直线段（L / H / V）没有，
        传错段号会抛出 ``ValueError`` 并提示哪些段号可用（见 ``curve_indices()``）。

        :param seg_index: 线段序号（从 0 开始，0 是起笔的 M 段）
        :param ctrl_index: 该段第几个调整点（从 0 开始）
        :param x: 目标 x
        :param y: 目标 y
        :return: self（可链式）

        示例::
            ed.curve_indices()               # 先看哪几段有调整点，例如 [2, 3]
            ed.move_control(2, 0, 210, 100)  # 第 2 段的第 1 个调整点
        """
        seg = self.segments[int(seg_index)]
        items = list(seg.ctrls)
        if not items:
            raise ValueError(t("err.seg_no_ctrl", index=int(seg_index),
                                   cmd=seg.cmd, kind=seg.kind,
                                   avail=self.curve_indices()))
        if not 0 <= int(ctrl_index) < len(items):
            raise ValueError(t("err.ctrl_index_range", index=int(seg_index),
                                       count=len(items), given=ctrl_index,
                                       last=len(items) - 1))
        items[int(ctrl_index)] = (float(x), float(y))
        seg.ctrls = tuple(items)
        if self.auto_apply:
            self.apply()
        return self

    def curve_indices(self) -> list:
        """
        返回**带调整点**的线段序号列表（只有贝塞尔 / 圆弧段才有控制点）。 / Return the indices of segments that have control points; only Bezier and arc segments do.

        :return: [int, ...]，例如 [2, 3]

        示例::
            for i in ed.curve_indices():
                print(i, ed.segments[i].kind)
        """
        return [i for i, s in enumerate(self.segments) if s.ctrls]

    def move_anchor_by(self, index, dx, dy) -> "PathEditor":
        """相对移动锚点。 / Move an anchor by a relative offset. 示例:: ed.move_anchor_by(1, 0, -20)"""
        self.anchors[int(index)].move_by(dx, dy)
        return self

    def set_anchors(self, positions) -> "PathEditor":
        """
        批量设置锚点坐标（适合外部算法算好一串新坐标后一次性回填）。 / Set all anchor coordinates at once, handy for feeding back computed points.

        :param positions: [(x, y), ...]，长度不超过现有锚点数
        :return: self

        示例::
            ed.set_anchors([(50, 50), (200, 60), (300, 120), (420, 60)])
        """
        for i, p in enumerate(positions):
            if i >= len(self.anchors):
                break
            for ref in self._anchor_refs[i]:
                ref[0].set_anchor(0 if ref[1] == "start" else 1, p[0], p[1])
        if self.auto_apply:
            self.apply()
        return self

    def anchor_positions(self) -> list:
        """
        取出全部锚点坐标（便于打印 / 传给外部算法）。 / Return every anchor coordinate, handy for printing or feeding to external algorithms.

        :return: [(x, y), ...]

        示例::
            ed.anchor_positions()    # [(50.0, 50.0), (200.0, 50.0)]
        """
        return [a.pos for a in self.anchors]

    def control_positions(self) -> list:
        """
        取出全部控制点坐标。 / Return every control-point coordinate.

        :return: [("第1段·调整点0", (x, y)), ...]
        """
        return [(c.role, c.pos) for c in self.controls]

    # ---------------------------------------------------------------
    # 调整：增删锚点
    # ---------------------------------------------------------------
    def insert_anchor(self, seg_index, t=0.5) -> "PathEditor":
        """
        在第 seg_index 段上插入一个锚点（曲线形状保持不变）。 / Insert an anchor on segment seg_index while keeping the curve shape unchanged.

        :param seg_index: 段号
        :param t: 插入位置 0~1（0.5 = 中点）
        :return: self

        示例::
            ed.insert_anchor(1, 0.5)     # 第 1 段中点加一个锚点
        """
        i = int(seg_index)
        seg = self.segments[i]
        first, second = seg.split(t)
        self.segments[i:i + 1] = [first, second]
        if self.auto_apply:
            self.apply_structure()
        return self

    def remove_anchor(self, index) -> "PathEditor":
        """
        删除一个锚点（把它两侧的直线段合并为一条；曲线段暂不支持）。 / Drop an anchor by merging the straight segments on both sides; curved neighbours are not supported yet.

        :param index: 锚点序号
        :return: self

        示例::
            ed.remove_anchor(2)      # 去掉中间多余的拐点（两侧须是直线段）
        """
        i = int(index)
        if i < 0:
            i += len(self._anchor_refs)
        refs = self._anchor_refs[i]
        prev_seg = next((r[0] for r in refs if r[1] == "end"), None)
        next_seg = next((r[0] for r in refs if r[1] == "start"), None)
        if prev_seg is None or next_seg is None or prev_seg is next_seg:
            raise ValueError(t("err.anchor_is_endpoint"))
        if prev_seg.cmd != "L" or next_seg.cmd != "L":
            raise NotImplementedError(t("err.remove_anchor_curve"))
        k = self.segments.index(next_seg)
        merged = type(prev_seg)("L", start=prev_seg.start, end=next_seg.end)
        self.segments[self.segments.index(prev_seg):k + 1] = [merged]
        if self.auto_apply:
            self.apply_structure()
        return self

    def reverse(self) -> "PathEditor":
        """
        反转路径方向（起终点互换，形状不变）。 / Reverse the path direction, swapping start and end while keeping the shape.

        :return: self

        示例::
            ed.reverse()
        """
        self.segments = reverse_segments(self.segments)
        if self.auto_apply:
            self.apply_structure()
        return self

    def scale_all(self, sx, sy=None, cx=0, cy=0) -> "PathEditor":
        """
        以 (cx, cy) 为中心整体缩放所有点（直接改坐标，不是 transform）。 / Scale every point about (cx, cy) by rewriting coordinates rather than adding a transform.

        :return: self

        示例::
            ed.scale_all(1.5, 1.5, cx=100, cy=100)
        """
        if sy is None:
            sy = sx
        for seg in self.segments:
            seg.start = (cx + (seg.start[0] - cx) * sx, cy + (seg.start[1] - cy) * sy)
            seg.end = (cx + (seg.end[0] - cx) * sx, cy + (seg.end[1] - cy) * sy)
            seg.ctrls = tuple((cx + (c[0] - cx) * sx, cy + (c[1] - cy) * sy)
                              for c in seg.ctrls)
            if seg.params:
                rx, ry, rot, la, sw = seg.params
                seg.params = (rx * sx, ry * sy, rot, la, sw)
        if self.auto_apply:
            self.apply()
        return self

    # ---------------------------------------------------------------
    # 存档：导出点位 -> 外部改 -> 读回
    # ---------------------------------------------------------------
    def to_dict(self) -> dict:
        """
        导出为可 JSON 序列化的字典（点位存档）。 / Export a JSON-serialisable dict of all points.

        示例::
            data = ed.to_dict()
            data["segments"][1]["ctrls"][0] = [120, 40]    # 外部随便改
        """
        out = []
        for seg in self.segments:
            out.append({
                "cmd": seg.cmd,
                "start": list(seg.start),
                "end": list(seg.end),
                "ctrls": [list(c) for c in seg.ctrls],
                "params": list(seg.params) if seg.params else None,
            })
        return {"d": self.path.get_d(), "segments": out}

    def save_json(self, file) -> str:
        """
        把路径点位存成 JSON（方便外部工具/脚本批量调点再读回）。 / Save the path points as JSON so external tools can tweak and reload them.

        :param file: 输出文件路径
        :return: 绝对路径

        示例::
            ed.save_json("points.json")
        """
        file = os.path.abspath(file)
        os.makedirs(os.path.dirname(file), exist_ok=True)
        with open(file, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        print(paint_path(t("info.points_exported", file=file), file))
        return file

    def load_json(self, file, apply=True) -> "PathEditor":
        """
        读取 JSON 点位并回填到路径（配合 save_json 使用）。 / Read JSON points back into the path; pairs with save_json.

        :param file: JSON 文件
        :param apply: 是否立即写回路径元素
        :return: self

        示例::
            ed.load_json("points.json")
        """
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
        from .segment import PathSegment
        segs = []
        for item in data.get("segments", []):
            segs.append(PathSegment(item["cmd"], item["start"], item["end"],
                                    ctrls=item.get("ctrls") or (),
                                    params=tuple(item["params"]) if item.get("params") else None))
        if segs:
            self.segments = segs
            if apply:
                self.apply_structure()
        return self

    # ---------------------------------------------------------------
    # 导出：单文件 HTML 编辑器 / export a self-contained HTML editor
    # ---------------------------------------------------------------
    def to_html(self, **kwargs) -> str:
        """
        导出「可拖拽的单文件 HTML 编辑器」的源码（字符串）。 / Build a self-contained, draggable HTML editor page for this path.

        :param kwargs: 透传给 ``PathHTMLEditor``，如 ``width=`` / ``grid=0`` / ``title=``
        :return: HTML 源码

        走的是本编辑器**当前**的点位（``to_dict()``），所以 ``auto_apply=False``
        时还没写回路径的改动也会一起带出去。

        示例::

            html = ed.to_html(grid=0)
        """
        from .htmleditor import PathHTMLEditor
        kwargs.setdefault("points", self.to_dict())
        kwargs.setdefault("path", self.path)
        return PathHTMLEditor(**kwargs).render()

    def save_html(self, file, **kwargs) -> str:
        """
        把「可拖拽的单文件 HTML 编辑器」写到磁盘，返回绝对路径。 / Write the draggable HTML editor to disk and return its absolute path.

        :param file: 输出文件路径（建议以 .html 结尾）
        :param kwargs: 透传给 ``PathHTMLEditor``
        :return: 绝对路径

        页面是自我包含的：没有 CDN、没有框架，双击就能用，也可以直接发给别人；
        在里面拖完可以下载 ``points.json``，再用 :meth:`load_json` 读回来。

        示例::

            ed.save_html("output/edit.html")     # 浏览器打开这个文件开始拖点
        """
        from .htmleditor import PathHTMLEditor
        kwargs.setdefault("points", self.to_dict())
        kwargs.setdefault("path", self.path)
        return PathHTMLEditor(**kwargs).save(file)

    # ---------------------------------------------------------------
    # 可视化：在画布上把点画出来
    # ---------------------------------------------------------------
    def show(self, board=None, anchor_color="#e63946", control_color="#1d3557",
             handle_color="#457b9d", size=4, labels=False, id_=None) -> "Element":
        """
        在画布上把锚点与调整杆画出来（像钢笔工具那样），方便对照调整。 / Draw anchors and handles on the canvas, pen-tool style, so you can check and adjust them.

        - 锚点：实心方块
        - 调整点：实心圆点
        - 调整杆：细线（把控制点和它所属的锚点连起来）
        - labels=True 时标出锚点序号

        :param board: 绘图板（默认用路径所属的绘图板）
        :param anchor_color: 锚点颜色
        :param control_color: 调整点颜色
        :param handle_color: 调整杆颜色
        :param size: 点的大小（像素）
        :param labels: 是否标注锚点序号
        :return: 承载这些标记的 GroupElement（已置顶）

        示例::
            ed.show()                        # 直接在路径所在画布上标出来
            ed.show(labels=True)             # 带序号
        """
        pen = board or getattr(self.path, "board", None)
        if pen is None:
            raise ValueError(t("err.no_board"))
        g = pen.g(id_=id_, opacity=0.95)
        # 1) 调整杆连线
        for seg in self.segments:
            if not seg.ctrls:
                continue
            pts = [seg.start] + list(seg.ctrls) + [seg.end]
            for a, b in zip(pts, pts[1:]):
                ln = pen.line(a, b, stroke_color=handle_color, stroke_width=1)
                ln.node.set("opacity", 0.6)
                ln.change_group(g)
        # 2) 锚点（方块）
        for a in self.anchors:
            sq = pen.rect(a.x - size, a.y - size, size * 2, size * 2,
                          fill_color=anchor_color, stroke_color="white",
                          stroke_width=1)
            sq.change_group(g)
            if labels:
                pen.text(a.x + size + 2, a.y - size - 2, "{}".format(a.index),
                         font_size=11, fill_color=anchor_color).change_group(g)
        # 3) 调整点（圆点）
        for c in self.controls:
            ci = pen.circle(c.x, c.y, size * 0.8, fill_color=control_color,
                            stroke_color="white", stroke_width=1)
            ci.change_group(g)
        g.bring_to_front()
        return g


# ===========================================================================
# 使用示例
# ===========================================================================
# 在 PyCharm 里点绿色三角直接运行本文件即可；也可命令行：
#     python -m malight.pathkit.editor
# 本示例覆盖 PathEditor 的全部公开能力：
#     构造 / reload / to_d / apply / apply_structure
#     closed / anchor_count / control_count
#     describe / report / print_report
#     move_anchor / move_anchor_by / move_control / curve_indices / set_anchors
#     anchor_positions / control_positions
#     insert_anchor / remove_anchor / reverse / scale_all
#     to_dict / save_json / load_json
#     show
# ===========================================================================
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
    # 1) 先造一条路径：起笔 M -> 直线 L -> 三次贝塞尔 C -> 二次贝塞尔 Q / 1) Build a path: move M, line L, cubic C, quadratic Q
    #    段号依次是 0(M) / 1(L) / 2(C) / 3(Q) / the segment numbers are 0(M), 1(L), 2(C), 3(Q)
    # -----------------------------------------------------------------
    p = pen.path(fill_color="none", stroke_color=ColorName.DARKSLATEGRAY,
                 stroke_width=3)
    p.move_to(60, 300)
    p.line_to(140, 180)
    p.cubic_to((200, 80), (300, 80), (360, 180))
    p.quad_to((430, 250), (520, 190))

    # -----------------------------------------------------------------
    # 2) 构造编辑器：PathEditor(p) 与 p.editor() 完全等价 / 2) PathEditor(p) and p.editor() are the same thing
    #    读统计信息：段数 / 锚点数 / 调整点数 / 是否闭合 / read the counts: segments, anchors, control points, closed or not
    # -----------------------------------------------------------------
    ed = PathEditor(p)
    print("段数: / segments:", len(ed.segments),
          "| 锚点数: / | anchors:", ed.anchor_count,
          "| 调整点数: / | control points:", ed.control_count,
          "| 是否闭合: / | closed:", ed.closed)

    # -----------------------------------------------------------------
    # 3) 看结构：describe() 返回字符串，report 是它的别名， / 3) describe() returns a string and report is its alias,
    #    print_report() 打印并返回同样内容（三选一即可） / print_report() prints it and returns the same text; pick any one
    # -----------------------------------------------------------------
    print(ed.describe())
    assert ed.report() == ed.describe()          # 别名，内容一致 / an alias, same content
    # 想直接打印时用 ed.print_report() / use ed.print_report() to print it directly

    # -----------------------------------------------------------------
    # 4) 看点位：锚点 / 调整点的纯坐标列表（便于打印或丢给外部算法） / 4) Plain coordinate lists for anchors and control points
    # -----------------------------------------------------------------
    print("锚点坐标: / anchor coordinates:", ed.anchor_positions())
    print("调整点坐标: / control point coordinates:", ed.control_positions())

    # -----------------------------------------------------------------
    # 5) 拖点：锚点按序号拖（支持负数），调整点必须先知道哪几段是曲线 / 5) Drag anchors by index, negatives allowed; control points need curve indices
    #    直线段没有调整点，move_control 传错段号会给出明确提示 / line segments have no control points; a wrong index raises a clear error
    # -----------------------------------------------------------------
    print("带调整点的段号: / segments with control points:", ed.curve_indices())      # 例：[2, 3] / e.g. [2, 3]
    ed.move_anchor(0, 70, 310)                       # 把起点拖到 (70,310) / drag the start anchor to (70,310)
    # 首个锚点在 d 串里就是 M 段；这一改必须真的落进 d 串 —— / the first anchor is the M segment, and the edit must reach the d string:
    # 曾经只登记了 start 引用而 to_d() 用 end，导致拖首个锚点毫无反应 / it used to register only start while to_d reads end, so it silently did nothing
    assert ed.to_d().startswith("M70,310"), ed.to_d()
    ed.move_anchor(-1, 540, 200)                     # -1 = 最后一个锚点 / -1 means the last anchor
    ed.move_anchor_by(1, 0, -15)                     # 相对移动：上移 15 / move relatively: 15 upwards
    ed.move_control(ed.curve_indices()[0], 0, 210, 100)   # 第 1 条曲线的第 1 个调整点 / the first control point of the first curve
    print("拖动后 d: / d after dragging:", ed.to_d())

    # -----------------------------------------------------------------
    # 6) 批量设置锚点坐标（外部算法算好一串新坐标后一次性回填） / 6) Set several anchor coordinates at once, after an external algorithm computed them
    # -----------------------------------------------------------------
    ed.set_anchors([(80, 300), (170, 170), (300, 90), (400, 190), (500, 230)])

    # -----------------------------------------------------------------
    # 7) 加点：在曲线上插入一个锚点，**形状保持不变** / 7) Insert an anchor on a curve without changing its shape
    # -----------------------------------------------------------------
    ed.insert_anchor(ed.curve_indices()[0], 0.5)
    print("加点后锚点数: / anchors after inserting:", ed.anchor_count)

    # -----------------------------------------------------------------
    # 8) 删点：只对「两侧都是直线段」的拐点有效（曲线请改调整点来简化） / 8) Remove only corners between two line segments; simplify curves via handles
    # -----------------------------------------------------------------
    q = pen.path(fill_color="none", stroke_color=ColorName.SEAGREEN,
                 stroke_width=3)
    q.move_to(60, 390)
    q.line_to(170, 390)
    q.line_to(270, 345)
    q.line_to(380, 390)
    qe = PathEditor(q)
    print("删点前: / before removing:", qe.to_d())
    qe.remove_anchor(2)                     # 去掉中间那个拐点，两条直线合并 / drop the middle corner so the two lines merge
    print("删点后: / after removing:", qe.to_d())

    # -----------------------------------------------------------------
    # 9) 反转方向（起终点互换，形状不变）+ 整体缩放（直接改坐标，不是 transform） / 9) Reverse the direction, then scale by rewriting coordinates, not by a transform
    # -----------------------------------------------------------------
    ed.reverse()
    ed.scale_all(0.95, 0.95, cx=300, cy=220)
    print("反转+缩放后: / after reversing and scaling:", ed.to_d())

    # -----------------------------------------------------------------
    # 10) 存档：to_dict() 拿可 JSON 化的数据 → save_json() 落盘 → / 10) Persist: to_dict() gives JSON-ready data, save_json() writes it,
    #     外部随便改 → load_json() 读回并立即写回路径 / edit it anywhere, load_json() reads it back into the path
    # -----------------------------------------------------------------
    data = ed.to_dict()
    data["segments"][-1]["end"] = [560, 210]        # 模拟外部算法改动 / simulate an external edit
    print("存档字典键: / saved dict keys:", list(data.keys()))
    _json = os.path.join(_out, "path_editor_points.json")
    ed.save_json(_json)
    ed.load_json(_json)                             # 读回并应用到路径 / read it back and apply it
    print("读回后 d: / d after loading back:", ed.to_d())

    # -----------------------------------------------------------------
    # 11) 手动重解析：外部直接改过 d 串后，让编辑器重新读一遍 / 11) Re-parse manually after something else changed the d string
    # -----------------------------------------------------------------
    p.set_d("M80,120 C160,40 260,40 340,120 L520,120")
    ed.reload()
    print("reload 后段数: / segments after reload:", len(ed.segments))

    # -----------------------------------------------------------------
    # 12) apply() / apply_structure()：拖点会**自动**写回，一般不用手动调； / 12) Dragging writes back automatically; apply() is rarely called by hand;
    #     apply_structure() 用于结构变化后重建点列表（加点/删点/反转已自动调用） / apply_structure() rebuilds the point list after structural edits
    # -----------------------------------------------------------------
    ed.apply()
    ed.apply_structure()
    print("apply 后锚点数: / anchors after apply:", ed.anchor_count)

    # -----------------------------------------------------------------
    # 13) 可视化：把锚点（方块）+ 调整杆（线）+ 调整点（圆点）画在画布上 / 13) Draw anchors as squares, handles as lines and control points as dots
    #     labels=True 时还会标出锚点序号，方便对照微调 / labels=True also numbers the anchors for fine-tuning
    # -----------------------------------------------------------------
    ed.show(labels=True)

    pen.finish()
