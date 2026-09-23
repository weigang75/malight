# -*- coding: utf-8 -*-
"""
路径线段（pathkit.segment）—— PathSegment 类
==============================================

PathSegment: one SVG path command in absolute coordinates, with geometry helpers.

`PathSegment` 表示 SVG 路径中的**一段**（对应一个 path 命令），
坐标已归一化为绝对坐标，每条曲线都明确给出「起点 / 终点 / 控制点」。

它是 `PathEditor` 看到路径内部结构的最基本单位：

- ``M`` 移动（起点，不画）
- ``L`` 直线段
- ``C`` 三次贝塞尔（2 个控制点）
- ``Q`` 二次贝塞尔（1 个控制点）
- ``A`` 圆弧（rx/ry/旋转角/大弧/方向）
- ``Z`` 闭合

使用示例::

    from malight.pathkit import parse_path_d

    seg = parse_path_d("M0,0 C0,80 100,80 100,0")[1]
    print(seg.kind)          # "cubic"（三次贝塞尔）
    print(seg.start)         # (0.0, 0.0)   起点
    print(seg.ctrls)         # ((0.0, 80.0), (100.0, 80.0))  两个调整点
    print(seg.end)           # (100.0, 0.0) 终点
    print(seg.length())      # 曲线长度
    print(seg.point_at(0.5)) # 曲线上 50% 处的坐标
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

import math
from typing import Optional
from ..i18n import t


# 命令 -> 英文类型名（结构化数据，恒为 ASCII，便于程序判断）
KIND_NAME = {
    "M": "move", "L": "line", "C": "cubic", "Q": "quad", "A": "arc", "Z": "close",
}


def kind_text(cmd):
    """
    段类型说明，跟随语言设置（中文「三次贝塞尔」/ 英文 "cubic"）。 / Localised
    segment-kind name, following the current output language.

    :param cmd: 命令字母，如 "C"
    :return: 类型说明；未知命令原样返回

    示例::
        kind_text("C")     # 中文 -> "三次贝塞尔"   英文 -> "cubic"
    """
    key = "seg.kind." + str(cmd).upper()
    text = t(key)
    return cmd if text == key else text


def _arc_split_msg():
    """
    圆弧不支持拆分时的提示文案（内部函数）。 / Message shown when a split is attempted on an arc (internal).

    单独抽成一个函数，是因为 `PathSegment.split()` 的形参也叫 ``t``：
    在它体内直接写 ``t("err.arc_split")`` 会被浮点形参遮蔽，变成
    ``TypeError: 'float' object is not callable``（而不是该抛的 NotImplementedError）。
    """
    return t("err.arc_split")


class PathSegment:
    """
    路径中的一段（一个 SVG path 命令，绝对坐标）。 / One segment of a path: a single SVG path command in absolute coordinates.

    一般不用自己 new，由 `parse_path_d()` 或 `PathEditor` 生成。

    属性说明（就是你在钢笔工具里能看到、能拖的那几个点）::

        seg.cmd       命令字母 M / L / C / Q / A / Z
        seg.kind      英文语义 move / line / cubic / quad / arc / close
        seg.start     本段起点 (x, y)
        seg.end       本段终点 (x, y)
        seg.ctrls     控制点（调整点）元组：C 两个、Q 一个、其余空
        seg.params    圆弧参数 (rx, ry, 旋转角, 大弧, 顺时针)
    """

    __slots__ = ("cmd", "start", "end", "ctrls", "params")

    def __init__(self, cmd, start=(0.0, 0.0), end=(0.0, 0.0),
                 ctrls=(), params=None):
        """
        :param cmd: 命令字母（大写，绝对坐标语义）
        :param start: 起点 (x, y)
        :param end: 终点 (x, y)
        :param ctrls: 控制点元组
        :param params: 圆弧参数 (rx, ry, rot, large_arc, sweep)
        """
        self.cmd = cmd
        self.start = (float(start[0]), float(start[1]))
        self.end = (float(end[0]), float(end[1]))
        self.ctrls = tuple((float(c[0]), float(c[1])) for c in ctrls)
        self.params = params

    # ---------------------------------------------------------------
    # 基本信息
    # ---------------------------------------------------------------
    @property
    def kind(self):
        """本段的英文类型名：move / line / cubic / quad / arc / close。 / The English kind name of this segment: move / line / cubic / quad / arc / close. """
        return KIND_NAME.get(self.cmd, self.cmd)

    @property
    def is_curve(self):
        """是不是曲线段（三次/二次贝塞尔或圆弧）。 / Whether this is a curve segment: cubic, quadratic or arc. """
        return self.cmd in ("C", "Q", "A")

    @property
    def is_closed(self):
        """是不是闭合命令 Z。 / Whether this is the close command Z. """
        return self.cmd == "Z"

    @property
    def control_count(self):
        """本段控制点（调整点）个数。 / Number of control points in this segment. """
        return len(self.ctrls)

    def describe(self) -> str:
        """
        返回一行中文说明（打印路径结构时用）。 / Return a one-line human-readable description, used in the path report.

        示例::
            print(seg.describe())     # [1] 三次贝塞尔  起点(0,0) 调整点(0,80) (100,80) → 终点(100,0)
        """
        fmt = lambda p: "({:.2f}, {:.2f})".format(p[0], p[1]).replace(".00", "")
        txt = "{}  {}{}".format(kind_text(self.cmd),
                                t("seg.word.start"), fmt(self.start))
        if self.ctrls:
            txt += "  " + t("seg.word.ctrl") + " " + " ".join(
                fmt(c) for c in self.ctrls)
        if self.cmd == "A" and self.params:
            txt += "  " + t("seg.word.radius") + "({}, {})".format(
                *[round(v, 2) for v in self.params[:2]])
        txt += t("seg.arrow") + t("seg.word.end") + fmt(self.end)
        return txt

    def __repr__(self):
        return "<PathSegment {} {} -> {}>".format(
            self.cmd, tuple(round(v, 2) for v in self.start),
            tuple(round(v, 2) for v in self.end))

    # ---------------------------------------------------------------
    # 序列化
    # ---------------------------------------------------------------
    def to_d(self) -> str:
        """
        本段还原为 d 片段。 / Render this segment back to a d fragment.

        示例::
            PathSegment("L", (0, 0), (10, 10)).to_d()    # "L10,10"
        """
        f = lambda v: ("%.4f" % v).rstrip("0").rstrip(".") if isinstance(v, float) else str(v)
        pt = lambda p: "{},{}".format(f(p[0]), f(p[1]))
        if self.cmd in ("M", "L"):
            return "{}{}".format(self.cmd, pt(self.end))
        if self.cmd == "C":
            return "C{} {} {}".format(pt(self.ctrls[0]), pt(self.ctrls[1]), pt(self.end))
        if self.cmd == "Q":
            return "Q{} {}".format(pt(self.ctrls[0]), pt(self.end))
        if self.cmd == "A":
            rx, ry, rot, large, sweep = self.params
            return "A{},{} {} {},{} {}".format(f(rx), f(ry), f(rot),
                                              1 if large else 0, 1 if sweep else 0,
                                              pt(self.end))
        if self.cmd == "Z":
            return "Z"
        return ""

    # ---------------------------------------------------------------
    # 几何计算
    # ---------------------------------------------------------------
    def point_at(self, t) -> tuple:
        """
        取本段上参数 t 处（0~1，按线段长度近似）的坐标。 / Return the point at parameter t (0-1), approximated by arc length.

        :param t: 0.0=起点，1.0=终点
        :return: (x, y)

        示例::
            seg.point_at(0.5)     # 中点
        """
        t = max(0.0, min(1.0, float(t)))
        if self.cmd in ("M", "Z"):
            return self.end if self.cmd == "M" else self.start
        if self.cmd == "L":
            return (self.start[0] + (self.end[0] - self.start[0]) * t,
                    self.start[1] + (self.end[1] - self.start[1]) * t)
        if self.cmd == "C":
            p0, p1, p2, p3 = self.start, self.ctrls[0], self.ctrls[1], self.end
            mt = 1 - t
            a, b, c, d = mt ** 3, 3 * mt * mt * t, 3 * mt * t * t, t ** 3
            return (a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0],
                    a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1])
        if self.cmd == "Q":
            p0, p1, p2 = self.start, self.ctrls[0], self.end
            mt = 1 - t
            a, b, c = mt * mt, 2 * mt * t, t * t
            return (a * p0[0] + b * p1[0] + c * p2[0],
                    a * p0[1] + b * p1[1] + c * p2[1])
        if self.cmd == "A":
            info = self.arc_center()
            if info is None:
                return (self.start[0] + (self.end[0] - self.start[0]) * t,
                        self.start[1] + (self.end[1] - self.start[1]) * t)
            cx, cy, rx, ry, phi, theta1, dtheta = info
            theta = theta1 + dtheta * t
            cos_p, sin_p = math.cos(phi), math.sin(phi)
            return (cos_p * rx * math.cos(theta) - sin_p * ry * math.sin(theta) + cx,
                    sin_p * rx * math.cos(theta) + cos_p * ry * math.sin(theta) + cy)
        return self.end

    def arc_center(self) -> "Optional[tuple]":
        """
        圆弧的「端点参数 → 圆心参数」转换（SVG 规范 F.6.5）。 / Convert an arc from endpoint parameters to centre parameters, per SVG spec F.6.5.

        :return: (cx, cy, rx, ry, phi弧度, 起始角, 扫过角)；非圆弧返回 None
        """
        if self.cmd != "A" or not self.params:
            return None
        rx, ry, rot, large, sweep = self.params
        rx, ry = abs(rx), abs(ry)
        if rx < 1e-9 or ry < 1e-9:
            return None
        phi = math.radians(rot % 360)
        x1, y1 = self.start
        x2, y2 = self.end
        dx2, dy2 = (x1 - x2) / 2.0, (y1 - y2) / 2.0
        cosp, sinp = math.cos(phi), math.sin(phi)
        x1p = cosp * dx2 + sinp * dy2
        y1p = -sinp * dx2 + cosp * dy2
        lam = x1p ** 2 / rx ** 2 + y1p ** 2 / ry ** 2
        if lam > 1:                      # 半径太小，按规范等比放大
            s = math.sqrt(lam)
            rx, ry = rx * s, ry * s
        num = rx ** 2 * ry ** 2 - rx ** 2 * y1p ** 2 - ry ** 2 * x1p ** 2
        den = rx ** 2 * y1p ** 2 + ry ** 2 * x1p ** 2
        if den == 0:
            return None
        coef = math.sqrt(max(0.0, num / den))
        if large == sweep:
            coef = -coef
        cxp = coef * rx * y1p / ry
        cyp = -coef * ry * x1p / rx
        cx = cosp * cxp - sinp * cyp + (x1 + x2) / 2.0
        cy = sinp * cxp + cosp * cyp + (y1 + y2) / 2.0

        def _angle(ux, uy, vx, vy):
            """两向量夹角（带符号，内部函数）。"""
            dot = ux * vx + uy * vy
            n = math.hypot(ux, uy) * math.hypot(vx, vy)
            if n == 0:
                return 0.0
            a = math.acos(max(-1.0, min(1.0, dot / n)))
            return -a if (ux * vy - uy * vx) < 0 else a

        theta1 = _angle(1, 0, (x1p - cxp) / rx, (y1p - cyp) / ry)
        dtheta = _angle((x1p - cxp) / rx, (y1p - cyp) / ry,
                        (-x1p - cxp) / rx, (-y1p - cyp) / ry)
        if (not sweep) and dtheta > 0:
            dtheta -= 2 * math.pi
        elif sweep and dtheta < 0:
            dtheta += 2 * math.pi
        return (cx, cy, rx, ry, phi, theta1, dtheta)

    def length(self, samples=32) -> float:
        """
        本段长度（直线精确；曲线按 samples 段折线近似；M/Z 为 0）。 / Length of this segment: exact for lines, sampled for curves, zero for M and Z.

        :param samples: 曲线采样段数（越大越精确）
        :return: 长度（浮点）

        示例::
            seg.length()      # 例如 89.44
        """
        if self.cmd in ("M", "Z"):
            return 0.0
        if self.cmd == "L":
            return math.hypot(self.end[0] - self.start[0], self.end[1] - self.start[1])
        n = max(4, int(samples))
        pts = [self.point_at(i / n) for i in range(n + 1)]
        return sum(math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1])
                   for i in range(n))

    def bbox(self) -> tuple:
        """
        本段的包围盒 (min_x, min_y, max_x, max_y)（曲线按采样近似）。 / Segment bounding box as (min_x, min_y, max_x, max_y), sampled for curves.

        示例::
            seg.bbox()
        """
        if self.cmd == "Z":
            return (self.start[0], self.start[1], self.start[0], self.start[1])
        pts = [self.start, self.end] + list(self.ctrls)
        if self.is_curve:
            pts += [self.point_at(i / 16.0) for i in range(1, 16)]
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        return (min(xs), min(ys), max(xs), max(ys))

    # ---------------------------------------------------------------
    # 调整：移动锚点 / 移动控制点 / 拆分
    # ---------------------------------------------------------------
    def set_anchor(self, index, x, y) -> "PathSegment":
        """
        移动本段的一个锚点（起点 index=0，终点 index=1）。 / Move one of this segment's anchors: index 0 is the start, 1 the end.

        :return: self（可链式）

        示例::
            seg.set_anchor(1, 200, 100)     # 把终点移到 (200,100)
        """
        if int(index) == 0:
            self.start = (float(x), float(y))
        else:
            self.end = (float(x), float(y))
        return self

    def set_control(self, index, x, y) -> "PathSegment":
        """
        移动本段的一个控制点（调整点）。 / Move one of this segment's control points.

        :return: self（可链式）

        示例::
            seg.set_control(0, 60, 20)      # 拖第一个控制柄
        """
        if not self.ctrls:
            return self
        i = max(0, min(len(self.ctrls) - 1, int(index)))
        items = list(self.ctrls)
        items[i] = (float(x), float(y))
        self.ctrls = tuple(items)
        return self

    def split(self, t=0.5) -> tuple:
        """
        在参数 t 处把本段一分为二（新增一个锚点，形状完全不变）。 / Split this segment in two at parameter t, adding an anchor without changing the shape.

        :param t: 拆分位置 0~1
        :return: (前半段, 后半段)

        示例::
            a, b = seg.split(0.5)    # 曲线中点加一个可拖的锚点
        """
        t = max(0.02, min(0.98, float(t)))
        if self.cmd == "L":
            mid = self.point_at(t)
            return (PathSegment("L", self.start, mid),
                    PathSegment("L", mid, self.end))
        if self.cmd == "C":
            p0, p1, p2, p3 = self.start, self.ctrls[0], self.ctrls[1], self.end
            lerp = lambda a, b: (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
            q0, q1, q2 = lerp(p0, p1), lerp(p1, p2), lerp(p2, p3)
            r0, r1 = lerp(q0, q1), lerp(q1, q2)
            s = lerp(r0, r1)                      # 曲线上的新锚点
            return (PathSegment("C", p0, s, ctrls=(q0, r0)),
                    PathSegment("C", s, p3, ctrls=(r1, q2)))
        if self.cmd == "Q":
            p0, p1, p2 = self.start, self.ctrls[0], self.end
            lerp = lambda a, b: (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
            q0, q1 = lerp(p0, p1), lerp(p1, p2)
            s = lerp(q0, q1)
            return (PathSegment("Q", p0, s, ctrls=(q0,)),
                    PathSegment("Q", s, p2, ctrls=(q1,)))
        if self.cmd == "A":
            raise NotImplementedError(_arc_split_msg())
        return (self, PathSegment("Z", self.end, self.end))


# ===========================================================================
# 使用示例
# ===========================================================================
# 在 PyCharm 里点绿色三角直接运行本文件即可；也可命令行：
#     python -m malight.pathkit.segment
# 本示例覆盖 PathSegment 的全部能力：
#     cmd / kind / is_curve / is_closed / control_count
#     start / end / ctrls / params
#     describe / to_d / __repr__
#     point_at / length / bbox / arc_center
#     set_anchor / set_control / split
# 以及 parse_path_d / segments_to_d 两个配套函数。
# 本模块不依赖画板，纯几何计算，可以单独拿来算坐标。
# ===========================================================================
if __name__ == "__main__":
    from malight.pathkit import parse_path_d, segments_to_d
    from malight.pathkit import PathSegment

    def _pt(p):
        """把坐标打印成 (x, y) 两位小数的样子。 / Print coordinates as (x, y) with two decimals."""
        return "({:.2f}, {:.2f})".format(p[0], p[1])

    # -----------------------------------------------------------------
    # 1) 解析与段的基本信息 / 1) Parsing and basic segment information
    #    parse_path_d 会把 H/V/S/T 等快捷命令展开、相对命令转成绝对坐标， / parse_path_d expands shortcuts like H/V/S/T and makes relative commands absolute,
    #    所以下标 0 恒为起笔的 M 段，之后每段都带明确的起点/终点/调整点。 / so index 0 is always the starting M and every later segment has explicit points.
    # -----------------------------------------------------------------
    d = "M0,0 h100 v50 s20,20 40,0 t40,0 a20,20 0 0,1 40,0 Z"
    segs = parse_path_d(d)
    # 双语字符串里同一个占位符会出现两次（中英各一次），所以参数要给两遍。 / A bilingual string repeats each placeholder once per language, so pass it twice.
    print("=== 1) 解析结果（共 %d 段）=== / === 1) parsed (%d segments) ==="
          % (len(segs), len(segs)))
    for i, s in enumerate(segs):
        print("  #{} cmd={} kind={} curve={} ctrls={}  {} -> {}".format(
            i, s.cmd, s.kind, s.is_curve, s.control_count,
            _pt(s.start), _pt(s.end)))

    # -----------------------------------------------------------------
    # 2) describe() / to_d() / repr：一行中文说明、还原 d 片段、调试短描述 / 2) describe() / to_d() / repr: one-line description, d fragment, debug repr
    #    注意段号：0=M(h 之前) 1=L(h100) 2=L(v50) 3=C(s... 展开) 4=Q 5=A 6=Z / note the numbers: 0=M, 1=L(h100), 2=L(v50), 3=C(expanded), 4=Q, 5=A, 6=Z
    # -----------------------------------------------------------------
    print("\n=== 2) 单段说明 === / \n=== 2) one segment described ===")
    cubic = segs[3]                       # 由 s 展开来的三次贝塞尔 / the cubic expanded from s
    print("  describe:", cubic.describe())
    print("  to_d    :", cubic.to_d())
    print("  repr    :", repr(cubic))
    print("  起点/终点: /   start/end:", _pt(cubic.start), _pt(cubic.end))
    print("  调整点   : /   controls :", " ".join(_pt(c) for c in cubic.ctrls))
    print("  是否曲线: /   is curve:", cubic.is_curve, " 是否闭合段: /  is closed:", cubic.is_closed)

    # -----------------------------------------------------------------
    # 3) 几何计算：弧长取点 / 段长 / 包围盒（全部按弧长参数化，定位准） / 3) Geometry: point at arc length, length and bbox, all arc-length based
    # -----------------------------------------------------------------
    print("\n=== 3) 几何计算（三次贝塞尔 0,0 -> 100,0）=== / \n=== 3) geometry (cubic from 0,0 to 100,0) ===")
    demo = parse_path_d("M0,0 C0,100 100,100 100,0")[1]
    for t in (0.0, 0.25, 0.5, 0.75, 1.0):
        print("  t={:<4} -> {}".format(t, _pt(demo.point_at(t))))
    _len = demo.length()
    print("  曲线长度 ≈ %.2f /   curve length ≈ %.2f" % (_len, _len))
    print("  包围盒     : /   bbox     :", tuple(round(v, 2) for v in demo.bbox()))

    # -----------------------------------------------------------------
    # 4) 改点：set_anchor（起点 index=0 / 终点 index=1）、set_control / 4) set_anchor (index 0 start, 1 end) and set_control
    #    直接改本段坐标，返回 self，可链式 / they change this segment's coordinates and return self
    #    注意：段级 to_d() 只输出本段命令（不含起笔 M），要整条路径的 d 串 / note: a segment's to_d() emits only its own command, without the leading M;
    #    请用 segments_to_d([...]) 拼装。 / use segments_to_d([...]) for the whole path
    # -----------------------------------------------------------------
    print("\n=== 4) 改点 === / \n=== 4) edit points ===")
    moved = parse_path_d("M0,0 C0,100 100,100 100,0")[1]
    moved.set_anchor(0, 10, 20).set_anchor(1, 110, 20)
    moved.set_control(0, 20, 120)
    print("  改后 d: /   d after:", moved.to_d())
    print("  整条路径: /   whole path:", segments_to_d([PathSegment("M", moved.start, moved.start), moved]))

    # -----------------------------------------------------------------
    # 5) split()：在 t 处一分为二，新增一个锚点且**形状完全不变** / 5) split() cuts a segment at t, adding an anchor with the shape unchanged
    #    直线段、C、Q 都支持；圆弧暂不支持（会抛 NotImplementedError） / lines, C and Q are supported; arcs raise NotImplementedError
    # -----------------------------------------------------------------
    print("\n=== 5) 拆分 === / \n=== 5) split ===")
    a, b = demo.split(0.5)
    print("  前半段: /   first half:", a.to_d())
    print("  后半段: /   second half:", b.to_d())
    print("  拼回去: /   rejoined:", segments_to_d([a, b]))

    line = parse_path_d("M0,0 L100,0")[1]
    la, lb = line.split(0.5)
    print("  直线拆分: /   line split:", la.to_d(), "|", lb.to_d())

    # -----------------------------------------------------------------
    # 6) 圆弧：params 存 (rx, ry, rot, large_arc, sweep)，arc_center() 求圆心 / 6) Arcs keep (rx, ry, rot, large_arc, sweep); arc_center() gives the centre
    # -----------------------------------------------------------------
    print("\n=== 6) 圆弧 === / \n=== 6) arc ===")
    arc = parse_path_d("M0,0 A50,50 0 0,1 100,0")[1]
    print("  kind:", arc.kind, "| is_curve:", arc.is_curve)
    print("  params (rx,ry,rot,large_arc,sweep):", arc.params)
    print("  圆心: /   centre:", _pt(arc.arc_center()), "| 半径 50 → 圆心应在弧的垂直平分线上 / | radius 50 -> the centre sits on the perpendicular bisector")
    _arc_len = arc.length()
    print("  弧长 ≈ %.2f （半圆） /   arc length ≈ %.2f (half circle)"
          % (_arc_len, _arc_len))

    # -----------------------------------------------------------------
    # 7) 直接构造 PathSegment（自己算好坐标时用，不需要画板） / 7) Build a PathSegment directly when you already have the coordinates
    # -----------------------------------------------------------------
    print("\n=== 7) 直接构造 === / \n=== 7) constructed by hand ===")
    s1 = PathSegment("M", (0, 0), (0, 0))
    s2 = PathSegment("L", (0, 0), (60, 40))
    s3 = PathSegment("C", (60, 40), (200, 0), ctrls=((100, 90), (160, 90)))
    s4 = PathSegment("Z", (200, 0), (0, 0))
    print("  自建路径: /   hand-built path:", segments_to_d([s1, s2, s3, s4]))
    print("  第 3 段类型/调整点数: /   segment 3 kind / control count:", s3.kind, s3.control_count)
