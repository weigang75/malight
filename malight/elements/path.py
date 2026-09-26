# -*- coding: utf-8 -*-
"""
PathElement 路径元素（对应中文版 路径元素）。 / PathElement: move / line / curve / arc commands, turtle drawing and boolean operations.

路径命令与 SVG path d 语法一一对应：移动/直线/水平垂直线/
二次与三次贝塞尔/圆弧/闭合；另支持布尔运算、变换、平滑、
乌龟式转向（前进/转角/圆角）等高级能力。
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
    __package__ = "malight.elements"

import math
import re
from ..svg_backend import SvgNode, fmt_num
from .base import Element, _paint
from ..i18n import t

# 路径辅助工具（查看/拖动锚点与控制点）。
# 用 try/except 兜底：正常导入顺序下拿到真实 PathEditor（PyCharm 有提示），
# 极端导入顺序下退化为占位类型，绝不会因为循环导入而报错。
try:
    from ..pathkit import PathEditor, PathSegment   # PathSegment 供 slice 切段用 / used by slice()
except ImportError:                      # pragma: no cover - 极端导入顺序兜底
    PathEditor = object
    PathSegment = object


def _norm_deg(a):
    """角度归一化到 0~360。"""
    return a % 360.0


class PathElement(Element["PathElement"]):
    """
    路径元素（对应中文版 `路径元素`）。 / Path element.

    内部维护命令列表与"画笔状态"（当前点 + 朝向角）。
    由 ``pen.path(...)`` 创建。

    示例::
        p = pen.path(fill_color="none", stroke_color="red", stroke_width=2)
        p.move_to(50, 50)
        p.cubic_to((100, 20), (150, 120), (200, 50))   # 三次贝塞尔
        p.quad_to((250, 10), (300, 50))                # 二次贝塞尔
        p.arc_to(40, (350, 90))                        # 圆弧
        p.close()
    """

    def __init__(self, board, parent=None, **kw):
        super().__init__(board, parent, tag="path")
        self._cmds = []           # 命令片段列表，如 ["M10,10", "L50,50", "Z"]
        self._cur = (0.0, 0.0)    # 当前点
        self._start = (0.0, 0.0)  # 当前子路径起点（close 用）
        self._heading = 0.0       # 海龟朝向（度，0=向右，顺时针为正）
        self._last_quad_ctrl = (0.0, 0.0)  # 上一条 Q/T 的控制点（平滑 T 反射用）
        self._update_attrs(**kw)

    def _update_attrs(self, d=None, **kw):
        """
        写入路径样式（内部方法）。 / Write the path style attributes (internal).

        :param d: 直接给 SVG 路径串（等价 ``set_d``）；不传则保留命令式绘制的结果
        :param kw: 填充/描边（``_apply_paint``）与公共样式（``_apply_common``）参数

        与其它元素走同一条属性管线，因此
        ``pen.path(..., opacity=0.5, blend_mode=..., class_name=...)``
        在创建时同样生效 —— 英文版修正：以前这里只应用 fill/stroke 系列，
        ``opacity`` / ``fill_opacity`` / ``stroke_opacity`` / ``blend_mode`` /
        ``vector_effect`` / ``class_name`` / ``style_str`` / ``extra``
        会被静默丢弃，``update()`` 的动态参数表也是空的。
        """
        self._apply_common({"id_": kw.pop("id_", None)})
        self._apply_common(kw)
        self._apply_paint(kw)
        if d is not None:
            self.set_d(d)
        elif self._cmds:
            self._sync()

    # ---------------------------------------------------------------
    # d 字符串
    # ---------------------------------------------------------------
    def get_d(self) -> str:
        """
        获取路径的 d 字符串（对应中文版 `获取路径d`）。 / Return the path's d string.

        示例::
            print(p.get_d())   # "M50,50 C100,20 150,120 200,50 Z"
        """
        return " ".join(self._cmds)

    def set_d(self, d) -> "PathElement":
        """
        直接设置 SVG path 的 d 字符串（英文版新增，对应原版 `原生path`）。 / Set the SVG path d string directly.

        :param d: 合法的 SVG path d 串

        示例::
            p = pen.path(fill_color="teal")
            p.set_d("M20,20 L80,20 L80,80 Z")   # 直接写原始路径
        """
        self._cmds = [d]
        self.node.set("d", d)
        return self

    def _sync(self):
        """把命令列表同步到节点属性（内部方法）。"""
        self.node.set("d", self.get_d())

    def _cmd(self, piece):
        """追加命令片段并同步（内部方法）。"""
        self._cmds.append(piece)
        self._sync()

    @staticmethod
    def _pt(x, y) -> str:
        """坐标格式化（内部方法）。"""
        return f"{fmt_num(x)},{fmt_num(y)}"

    # ---------------------------------------------------------------
    # 命令式绘制
    # ---------------------------------------------------------------
    def move_to(self, x, y=None) -> "PathElement":
        """
        抬笔移动到指定点（不画线），并开启新子路径（对应中文版 `移动到`/`落笔`）。 / Lift the pen, move to a point without drawing, and start a new subpath.

        :param x: 目标 x，或 (x, y) 元组
        :param y: 目标 y

        示例::
            p.move_to(50, 50)
            p.move_to((120, 80))    # 也支持元组
        """
        if y is None:
            x, y = x
        self._cur = (float(x), float(y))
        self._start = self._cur
        self._cmd(f"M{self._pt(x, y)}")
        return self

    # 落笔与移动到等价（保留中文版双名语义）
    pen_down = move_to

    def line_to(self, end_x, end_y=None) -> "PathElement":
        """
        从当前点画直线到目标点（对应中文版 `画直线`）。 / Draw a straight line from the current point to the target point.

        :param end_x: 终点 x，或 (x, y) 元组
        :param end_y: 终点 y

        示例::
            p.move_to(0, 0)
            p.line_to(100, 0)      # 画 100 长的水平线
            p.line_to(100, 100)    # 竖直线
        """
        if end_y is None:
            end_x, end_y = end_x
        # 海龟语义下同时更新朝向
        self._heading = math.degrees(math.atan2(end_y - self._cur[1],
                                                end_x - self._cur[0]))
        self._cur = (float(end_x), float(end_y))
        self._cmd(f"L{self._pt(end_x, end_y)}")
        return self

    def h_line_to(self, end_x) -> "PathElement":
        """水平线到 end_x（对应中文版 `画水平线`）。 / Draw a horizontal line to end_x. 示例:: p.h_line_to(200)"""
        self.line_to(end_x, self._cur[1])
        return self

    def v_line_to(self, end_y) -> "PathElement":
        """垂直线到 end_y（对应中文版 `画垂直线`）。 / Draw a vertical line to end_y. 示例:: p.v_line_to(200)"""
        self.line_to(self._cur[0], end_y)
        return self

    def cubic_to(self, ctrl1, ctrl2, end) -> "PathElement":
        """
        三次贝塞尔曲线（对应中文版 `三次贝塞尔曲线`/`画曲线`）。 / Cubic Bézier curve.

        :param ctrl1: 第一控制点 (x, y)
        :param ctrl2: 第二控制点 (x, y)
        :param end: 终点 (x, y)

        示例::
            p.move_to(50, 200)
            p.cubic_to((120, 80), (220, 280), (300, 150))
        """
        self._cur = (float(end[0]), float(end[1]))
        self._cmd(f"C{self._pt(*ctrl1)} {self._pt(*ctrl2)} {self._pt(*end)}")
        self._heading_from_tangent(end, ctrl2)   # 朝向 = 末端切线 / heading = end tangent
        return self

    def smooth_cubic_to(self, ctrl2, end) -> "PathElement":
        """
        平滑三次贝塞尔（自动反射前一控制点，对应中文版 `平滑曲线`）。 / Smooth cubic Bézier continuation.

        示例::
            p.cubic_to((80, 20), (150, 120), (200, 60))
            p.smooth_cubic_to((280, 10), (330, 90))   # 光滑衔接
        """
        self._cur = (float(end[0]), float(end[1]))
        self._cmd(f"S{self._pt(*ctrl2)} {self._pt(*end)}")
        self._heading_from_tangent(end, ctrl2)   # 朝向 = 末端切线 / heading = end tangent
        return self

    def quad_to(self, ctrl, end) -> "PathElement":
        """
        二次贝塞尔曲线（对应中文版 `二次贝塞尔曲线`）。 / Quadratic Bézier curve.

        示例::
            p.move_to(50, 100)
            p.quad_to((175, 0), (300, 100))   # 抛物线拱形
        """
        self._cur = (float(end[0]), float(end[1]))
        self._cmd(f"Q{self._pt(*ctrl)} {self._pt(*end)}")
        self._last_quad_ctrl = (float(ctrl[0]), float(ctrl[1]))
        self._heading_from_tangent(end, ctrl)    # 朝向 = 末端切线 / heading = end tangent
        return self

    def smooth_quad_to(self, end) -> "PathElement":
        """平滑二次贝塞尔（对应中文版 `平滑的二次贝塞尔曲线`）。 / Smooth quadratic Bézier continuation. """
        # 反射上一控制点（无历史时控制点=当前点，与 SVG 规范一致）
        # / reflect the previous control point (falls back to the current point per spec)
        refl = (2 * self._cur[0] - self._last_quad_ctrl[0],
                2 * self._cur[1] - self._last_quad_ctrl[1])
        self._last_quad_ctrl = refl
        self._cur = (float(end[0]), float(end[1]))
        self._cmd(f"T{self._pt(*end)}")
        self._heading_from_tangent(end, refl)    # 朝向 = 末端切线 / heading = end tangent
        return self

    def _heading_from_tangent(self, end, ctrl) -> None:
        """曲线末端切线 = 终点 - 末控制点；零长切线不动朝向（内部方法）。"""
        dx = float(end[0]) - float(ctrl[0])
        dy = float(end[1]) - float(ctrl[1])
        if math.hypot(dx, dy) > 1e-12:
            self._heading = _norm_deg(math.degrees(math.atan2(dy, dx)))

    def ellipse_arc_to(self, rx, ry, end, sweep=0, large_arc=False,
                       x_axis_rotation=0) -> "PathElement":
        """
        椭圆弧（对应中文版 `画椭圆弧`）。 / Elliptical arc.

        画完后海龟朝向更新为弧末端切线方向（后续 `forward` /
        `turn_right_line` 以弧末端切线为参考）。 / Afterwards the turtle
        heading equals the arc's end tangent, so forward / turn commands
        continue from the curve naturally.

        :param rx: X 轴半径
        :param ry: Y 轴半径
        :param end: 终点 (x, y)
        :param sweep: 0=逆时针, 1=顺时针
        :param large_arc: 是否取大弧
        :param x_axis_rotation: 椭圆 X 轴旋转角

        示例::
            p.move_to(50, 100)
            p.ellipse_arc_to(80, 40, (210, 100), sweep=1)   # 半个横椭圆
        """
        x1, y1 = self._cur
        self._cur = (float(end[0]), float(end[1]))
        self._cmd(f"A{fmt_num(rx)},{fmt_num(ry)} {fmt_num(x_axis_rotation)} "
                  f"{1 if large_arc else 0},{1 if sweep else 0} {self._pt(*end)}")
        h = self._arc_end_heading((x1, y1), self._cur, rx, ry, x_axis_rotation,
                                  bool(large_arc), bool(sweep))
        if h is not None:
            self._heading = _norm_deg(h)
        return self

    @staticmethod
    def _arc_end_heading(p1, p2, rx, ry, phi_deg, large_arc, sweep):
        """
        求椭圆弧末端切线的朝向角（度，屏幕坐标系，内部方法）。

        用 SVG 端点参数化（W3C F.6.5）反推圆心与末端参数角，
        再对椭圆参数式求导得切线。失败（退化弧）返回 None。
        / End-tangent heading of an elliptical arc in degrees (screen coords),
        via the SVG endpoint-to-center conversion (W3C F.6.5) plus the
        parametric derivative; None for degenerate arcs.
        """
        rx, ry = abs(float(rx)), abs(float(ry))
        if rx < 1e-12 or ry < 1e-12:
            return None
        phi = math.radians(float(phi_deg))
        cos_p, sin_p = math.cos(phi), math.sin(phi)
        # F.6.5.1: 端点转到以弦中点为原点、椭圆轴对齐的坐标系 / step 1
        dx, dy = (p1[0] - p2[0]) / 2, (p1[1] - p2[1]) / 2
        x1p = cos_p * dx + sin_p * dy
        y1p = -sin_p * dx + cos_p * dy
        # F.6.6: 半径过小则放大保证弧存在 / step 2: scale radii if needed
        lam = x1p * x1p / (rx * rx) + y1p * y1p / (ry * ry)
        if lam > 1:
            s = math.sqrt(lam)
            rx, ry = rx * s, ry * s
        # F.6.5.2: 求圆心 / step 3: center
        num = rx * rx * ry * ry - rx * rx * y1p * y1p - ry * ry * x1p * x1p
        den = rx * rx * y1p * y1p + ry * ry * x1p * x1p
        if den < 1e-18:
            return None
        if num < 0:
            num = 0.0   # 半径缩放后的浮点误差兜底 / float guard after scaling
        co = math.sqrt(num / den) * (1 if sweep != large_arc else -1)
        cxp, cyp = co * rx * y1p / ry, -co * ry * x1p / rx
        # 末端点在轴对齐系里的坐标：终点与起点关于弦中点对称（x1p,y1p 是起点）
        # / end point in the axis-aligned frame mirrors the start about the chord midpoint
        mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
        ux = (-x1p - cxp) / rx          # cos t2
        uy = (-y1p - cyp) / ry          # sin t2
        # 参数式导数：(-rx sin t, ry cos t)，sweep=1 时 t 递增 / parametric derivative
        vx_f = -rx * uy
        vy_f = ry * ux
        sign = 1 if sweep else -1
        # 转回屏幕坐标（旋转 phi）并归一 / rotate back by phi, normalize
        vx = sign * (cos_p * vx_f - sin_p * vy_f)
        vy = sign * (sin_p * vx_f + cos_p * vy_f)
        norm = math.hypot(vx, vy)
        if norm < 1e-12:
            return None
        return math.degrees(math.atan2(vy, vx))

    def arc_to(self, radius, end, sweep=0, large_arc=False) -> "PathElement":
        """
        圆弧（对应中文版 `画圆弧`）。 / Circular arc.

        :param radius: 圆弧半径
        :param end: 终点 (x, y)
        :param sweep: 0=逆时针, 1=顺时针
        :param large_arc: 是否取大弧

        示例::
            p.move_to(50, 100)
            p.arc_to(75, (200, 100), sweep=1)   # 上拱半圆
        """
        return self.ellipse_arc_to(radius, radius, end, sweep, large_arc)

    def circle_to(self, center, sweep=0) -> "PathElement":
        """
        在路径中以圆弧画完整圆（对应中文版 `画圆`）。 / Draw a full circle in the path using arc commands.

        :param center: 圆心 (x, y)
        :param sweep: 方向（0 逆时针 / 1 顺时针）

        示例::
            p = pen.path(fill_color="gold")
            p.move_to(100, 50)
            p.circle_to((100, 100))       # 以 (100,100) 为圆心的圆
        """
        cx, cy = center
        r = math.hypot(self._cur[0] - cx, self._cur[1] - cy)
        if r < 1e-6:
            return self
        s = 1 if sweep else 0
        # 两个半圆弧拼成整圆
        self._cmd(f"A{fmt_num(r)},{fmt_num(r)} 0 0,{s} "
                  f"{self._pt(cx + (cx - self._cur[0]), cy + (cy - self._cur[1]))}")
        self._cmd(f"A{fmt_num(r)},{fmt_num(r)} 0 0,{s} {self._pt(*self._start)}")
        self._cur = self._start
        return self

    def close(self) -> "PathElement":
        """
        闭合当前子路径（回到子路径起点，对应中文版 `闭合`）。 / Close the current subpath.

        示例::
            p.move_to(10, 10); p.line_to(100, 10); p.close()
        """
        self._cur = self._start
        self._cmd("Z")
        return self

    def new_subpath(self, x=None, y=None, **kw) -> "PathElement":
        """
        开启新子路径（对应中文版 `新路径`）：同一元素里画不相连的多段。 / Start a new subpath so one element can hold several disconnected pieces.

        :param kw: 可覆盖描边/填充样式（作用于新子路径所在的整个 path 节点）

        示例::
            p.move_to(10, 10); p.line_to(50, 10)
            p.new_subpath(10, 50); p.line_to(50, 50)   # 两条平行线
        """
        if x is not None:
            self.move_to(x, y if y is not None else (x if isinstance(x, tuple) else (x, y)))
        return self

    # ---------------------------------------------------------------
    # 海龟式绘制（朝向角状态机）
    # ---------------------------------------------------------------
    def _heading_rad(self) -> float:
        """当前朝向的弧度值（内部方法）。"""
        return math.radians(self._heading)

    def forward(self, length) -> "PathElement":
        """
        沿当前朝向前进并画线（对应中文版 `前进直线`）。 / Move forward along the current heading, drawing a line.

        :param length: 前进距离

        示例::
            p.move_to(50, 200)
            p.forward(100)           # 向右画 100
            p.turn_right_line(90, 100)  # 右转画 100
            p.forward(100)
        """
        dx = length * math.cos(self._heading_rad())
        dy = length * math.sin(self._heading_rad())
        return self.line_to(self._cur[0] + dx, self._cur[1] + dy)

    def backward(self, length) -> "PathElement":
        """沿当前朝向后退并画线（对应中文版 `后退直线`）。 / Move backwards along the current heading, drawing a line. 示例:: p.backward(50)"""
        return self.forward(-length)

    def turn_right_move(self, angle, distance=0) -> "PathElement":
        """
        右转 angle 度后移动（不画线）（对应中文版 `右转移动`）。 / Turn right by angle degrees and move without drawing.

        示例::
            p.turn_right_move(90, 50)   # 右转 90°，抬笔走 50
        """
        self._heading = _norm_deg(self._heading + angle)
        if distance:
            dx = distance * math.cos(self._heading_rad())
            dy = distance * math.sin(self._heading_rad())
            self._cur = (self._cur[0] + dx, self._cur[1] + dy)
            self._start = self._cur
            self._cmd(f"M{self._pt(*self._cur)}")
        return self

    def turn_left_move(self, angle, distance=0) -> "PathElement":
        """左转 angle 度后移动（对应中文版 `左转移动`）。 / Turn left by angle degrees and move without drawing. 示例:: p.turn_left_move(90)"""
        return self.turn_right_move(-angle, distance)

    def turn_right_line(self, angle, length) -> "PathElement":
        """
        右转 angle 度后画线（对应中文版 `右转直线`）。 / Turn right by angle degrees and draw a line.

        示例::
            for _ in range(5):           # 画五角星轮廓
                p.forward(150)
                p.turn_right_line(144, 0.01)
        """
        self.turn_right_move(angle, 0)
        if length:
            self.forward(length)
        return self

    def turn_left_line(self, angle, length) -> "PathElement":
        """左转 angle 度后画线（对应中文版 `左转直线`）。 / Turn left by angle degrees and draw a line. """
        return self.turn_right_line(-angle, length)

    def turn_right_arc(self, angle, radius) -> "PathElement":
        """
        右转圆弧：画一段向右弯的弧线（对应中文版 `右转弧线`）。 / Turn-right arc: draw an arc curving to the right.

        弦沿转向角平分线方向，画完后朝向 = 弧末端切线方向，
        后续 `forward` / `turn_right_line` 等自动以新切线为参考。
        / The chord points along the turn's bisector; afterwards the heading
        equals the arc's end tangent, so forward / turn_right_line continue
        from it naturally.

        :param angle: 弧对应的转向角（度）
        :param radius: 弧半径

        示例::
            p.move_to(50, 200)
            p.forward(80)
            p.turn_right_arc(90, 40)    # 右弯 90° 的圆角
            p.forward(80)
        """
        self._heading = _norm_deg(self._heading + angle)
        # 弦方向 = 起止朝向的平分角（新朝向回退半个转向角）
        # / chord direction = bisector of the turn (new heading minus half the turn)
        mid = math.radians(self._heading - angle / 2)
        chord = 2 * radius * math.sin(math.radians(abs(angle)) / 2)
        end = (self._cur[0] + chord * math.cos(mid),
               self._cur[1] + chord * math.sin(mid))
        return self.arc_to(radius, end, sweep=1, large_arc=abs(angle) > 180)

    def turn_left_arc(self, angle, radius) -> "PathElement":
        """左转圆弧（对应中文版 `左转弧线`）。 / Turn-left arc. 示例:: p.turn_left_arc(90, 40)"""
        self._heading = _norm_deg(self._heading - angle)
        # 弦方向 = 起止朝向的平分角（新朝向回退半个转向角）
        # / chord direction = bisector of the turn (new heading plus half the turn)
        mid = math.radians(self._heading + angle / 2)
        chord = 2 * radius * math.sin(math.radians(abs(angle)) / 2)
        end = (self._cur[0] + chord * math.cos(mid),
               self._cur[1] + chord * math.sin(mid))
        return self.arc_to(radius, end, sweep=0, large_arc=abs(angle) > 180)

    def fillet(self, p1, p2, radius) -> "PathElement":
        """
        两线段之间倒圆角（对应中文版 `倒圆角直线`）：
        从当前点经 p1 拐向 p2，拐角处以 radius 圆弧过渡。 / Round the corner between two segments: go from the current point through p1 towards p2 with an arc of radius.

        示例::
            p.move_to(50, 250)
            p.fillet((50, 100), (200, 100), 30)   # 直角变圆角
            p.line_to(300, 100)
        """
        x0, y0 = self._cur
        x1, y1 = p1
        x2, y2 = p2
        v1 = (x1 - x0, y1 - y0)
        v2 = (x2 - x1, y2 - y1)
        l1 = math.hypot(*v1)
        l2 = math.hypot(*v2)
        if l1 < 1e-6 or l2 < 1e-6:
            return self
        ang = math.acos(max(-1, min(1, (v1[0] * v2[0] + v1[1] * v2[1]) / (l1 * l2))))
        half = (math.pi - ang) / 2
        t1 = radius / math.tan(half)
        t1 = min(t1, l1 * 0.99)
        t2 = radius / math.tan(half)
        t2 = min(t2, l2 * 0.99)
        # 直线到切点
        self.line_to(x1 - v1[0] / l1 * t1, y1 - v1[1] / l1 * t1)
        # 圆弧到第二切点
        tangent2 = (x1 + v2[0] / l2 * t2, y1 + v2[1] / l2 * t2)
        sweep = 1 if (v1[0] * v2[1] - v1[1] * v2[0]) > 0 else 0
        self.arc_to(radius, tangent2, sweep=sweep)
        return self

    # ---------------------------------------------------------------
    # 变换 / 结构操作
    # ---------------------------------------------------------------
    def _parse_own_d(self) -> list:
        """把自身命令串解析为绝对命令点列表（简易解析，内部方法）。"""
        tokens = re.findall(r"[MmLlHhVvCcSsQqTtAaZz]|-?\d*\.?\d+(?:e[-+]?\d+)?",
                            self.get_d())
        return tokens

    def translate_cmds(self, dx, dy) -> "PathElement":
        """
        平移路径的所有坐标点（对应中文版 `坐标平移`，直接改坐标而非 transform）。 / Translate every coordinate of the path.

        示例::
            p.translate_cmds(100, 0)   # 路径整体右移 100
        """
        d = self.get_d()
        nums = re.findall(r"-?\d+\.?\d*(?:e[-+]?\d+)?", d)
        # 逐段替换 M/L/C/Q/S/T/A 后面的坐标对（A 的中间参数除外）——
        # 简化实现：对常见 M/L/C/Q/S/T/Z 命令处理
        out = []
        i = 0
        tokens = d.replace(",", " ").split()
        cmd = None
        expect = {"M": 2, "L": 2, "C": 6, "Q": 4, "S": 4, "T": 2, "A": 7, "Z": 0, "H": 1, "V": 1}
        k = 0
        while k < len(tokens):
            t = tokens[k]
            if t.upper() in expect and not any(c.isdigit() for c in t.replace(".", "").replace("-", "")) or t.upper() in "MLCQSTZAHV":
                cmd = t
                out.append(t)
                k += 1
                if cmd in ("Z", "z"):
                    continue
                params = []
                n = expect[cmd.upper()]
                for j in range(n):
                    params.append(float(tokens[k + j]))
                if cmd.upper() in ("M", "L", "T"):
                    for j in range(0, n, 2):
                        params[j] += dx
                        params[j + 1] += dy
                elif cmd.upper() == "C":
                    for j in range(0, n, 2):
                        params[j] += dx
                        params[j + 1] += dy
                elif cmd.upper() in ("Q", "S"):
                    for j in range(0, n, 2):
                        params[j] += dx
                        params[j + 1] += dy
                elif cmd.upper() == "A":
                    params[5] += dx
                    params[6] += dy
                elif cmd.upper() == "H":
                    params[0] += dx
                elif cmd.upper() == "V":
                    params[0] += dy
                out.extend(fmt_num(v) for v in params)
                k += n
            else:
                out.append(t)
                k += 1
        self.set_d(" ".join(out))
        return self

    def reverse(self) -> "PathElement":
        """
        反转路径方向（对应中文版 `反向路径`）：起终点互换，形状不变。 / Reverse the path direction, swapping start and end while keeping the shape.

        英文版改为自带实现，不再依赖 svgpathtools。

        示例::
            p.reverse()   # 起终点互换
        """
        self.editor(refresh=True).reverse()
        return self

    def merge(self, other) -> "PathElement":
        """
        合并另一条路径到本路径（对应中文版 `合并路径`）。 / Merge another path into this one.

        :param other: 另一个 PathElement（其命令串被追加）

        示例::
            main.merge(p2)   # p2 的形状并入 main，统一一个元素
        """
        self._cmds.extend(other._cmds)
        self._sync()
        other.remove()
        return self

    # ---------------------------------------------------------------
    # 布尔运算（需要 shapely；英文版增强：不依赖时给出清晰报错）
    # ---------------------------------------------------------------
    def _boolean(self, op, other) -> "PathElement":
        """布尔运算内部实现（内部方法）。"""
        try:
            from shapely.geometry import Polygon as _ShapelyPoly
            from shapely.ops import unary_union
        except ImportError:
            raise NotImplementedError(t("err.need_shapely"))
        a = _ShapelyPoly(self.to_point_list())
        b = _ShapelyPoly(other.to_point_list())
        if op == "union":
            r = a.union(b)
        elif op == "intersect":
            r = a.intersection(b)
        else:
            r = a.difference(b)
        coords = list(r.exterior.coords)
        new = PathElement(self.board, self.parent_node)
        new.move_to(*coords[0])
        for x, y in coords[1:]:
            new.line_to(x, y)
        new.close()
        new._copy_paint_from(self)
        return new

    def union(self, other) -> "PathElement":
        """
        并集（对应中文版 `并集`）：返回新路径元素。 / Union: return a new path element.

        示例::
            merged = pa.union(pb)
        """
        return self._boolean("union", other)

    def intersect(self, other) -> "PathElement":
        """交集（对应中文版 `交集`）。 / Intersection. 示例:: common = pa.intersect(pb)"""
        return self._boolean("intersect", other)

    def subtract(self, other) -> "PathElement":
        """差集（对应中文版 `差集`）。 / Difference. 示例:: hole = pa.subtract(pb)"""
        return self._boolean("difference", other)

    # ---------------------------------------------------------------
    # 几何信息
    # ---------------------------------------------------------------
    def to_point_list(self, samples=200) -> list:
        """
        采样路径为顶点列表（对应中文版 `路径点列表`），供布尔/测距等使用。 / Sample the path into a vertex list for boolean ops and measurements.

        英文版改为自带解析（不依赖 svgpathtools），曲线也采样准确。

        :param samples: 总采样点数（按段数分摊给每段）

        示例::
            pts = p.to_point_list()
        """
        from ..pathkit import parse_path_d
        segs = [s for s in parse_path_d(self.get_d()) if s.cmd != "M"]
        if not segs:
            return []
        pts = [segs[0].start]
        per = max(2, int(samples / len(segs)))
        for s in segs:
            for i in range(1, per + 1):
                pts.append(s.point_at(i / float(per)))
        return pts

    def length(self, samples=48) -> float:
        """
        路径总长度（按段精确/近似求和，对应中文版 `路径长度`）。 / Total path length.

        闭合边（Z）按直线计入。 / The closing edge (Z) counts as a straight line.

        :param samples: 曲线段的采样精度

        示例::
            print(p.length())
        """
        return self._walk(samples)[2]

    def point_at(self, ratio) -> tuple:
        """
        取路径上指定比例位置的坐标（按**弧长**定位，对应中文版 `位置坐标`）。 / Return the coordinates at a given fraction along the path.

        :param ratio: 0.0（起点）~ 1.0（终点）
        :return: (x, y)

        示例::
            x, y = p.point_at(0.5)   # 路径正中点
        """
        segs, lens, total = self._walk()
        if total <= 0:
            return segs[0].start if segs else (0.0, 0.0)
        return self._point_at_len(max(0.0, min(1.0, float(ratio))) * total,
                                  segs, lens, total)

    # ---------------------------------------------------------------
    # 几何查询：切线 / 法线 / 弧长取点 / 两路径距离（英文版新增）
    # ---------------------------------------------------------------
    def _walk(self, samples=48):
        """
        把 d 串解析为「可计量段」列表并累计弧长（内部方法）。

        Z 闭合段换成等效直线段参与采样（闭合边也是粘贴线 / 法线的目标），
        M 段跳过；每段同时构建采样累积弧长表，段内取点按真弧长插值
        （参数 t 与弧长在曲线上非线性）。 :return: (segs, lens, total)
        """
        from ..pathkit import parse_path_d, PathSegment
        segs = []
        for s in parse_path_d(self.get_d()):
            if s.cmd == "M":
                continue
            if s.cmd == "Z":
                segs.append(PathSegment("L", s.start, s.end))
            else:
                segs.append(s)
        lens = []
        for s in segs:
            s._build_arc_table(samples)
            lens.append(s.length(samples))
        return segs, lens, sum(lens)

    @staticmethod
    def _point_at_len(target, segs, lens, total) -> tuple:
        """按弧长 target 在已解析的段列表上取点（内部方法）。"""
        acc = 0.0
        for s, l in zip(segs, lens):
            if acc + l >= target or s is segs[-1]:
                return s.point_at_arc(target - acc)
            acc += l
        return segs[-1].end

    def point_at_distance(self, dist, samples=48) -> tuple:
        """
        沿路径从起点走 dist 长度处的坐标（英文版新增）。 / Return the point at an absolute arc length dist from the start.

        :param dist: 弧长距离（负数或超出总长会夹到起/终点）
        :param samples: 曲线段采样精度
        :return: (x, y)

        示例::
            p.point_at_distance(50)     # 沿路径 50 个单位处
        """
        segs, lens, total = self._walk(samples)
        if total <= 0:
            return segs[0].start if segs else (0.0, 0.0)
        return self._point_at_len(max(0.0, min(total, float(dist))), segs, lens, total)

    def tangent_at(self, ratio, samples=48) -> tuple:
        """
        路径上 ratio 位置的**单位切线向量**（沿行进方向，英文版新增）。 / Unit tangent vector at a given fraction, pointing along the travel direction.

        :param ratio: 0.0 ~ 1.0（按弧长定位，同 `point_at`）
        :return: (tx, ty) 单位向量

        示例::
            tx, ty = p.tangent_at(0.3)
        """
        segs, lens, total = self._walk(samples)
        if total <= 0:
            return (1.0, 0.0)
        d = max(0.0, min(1.0, float(ratio))) * total
        eps = max(total * 1e-4, 1e-6)
        a = self._point_at_len(max(0.0, d - eps), segs, lens, total)
        b = self._point_at_len(min(total, d + eps), segs, lens, total)
        dx, dy = b[0] - a[0], b[1] - a[1]
        n = math.hypot(dx, dy)
        if n < 1e-12:
            return (1.0, 0.0)
        return (dx / n, dy / n)

    def tangent_angle_at(self, ratio, samples=48) -> float:
        """
        路径上 ratio 位置的切线角（度，0=向右、顺时针为正，与海龟朝向同义，
        英文版新增）。 / Tangent angle in degrees at a given fraction
        (0 = pointing right, clockwise positive, same convention as the turtle heading).

        示例::
            ang = p.tangent_angle_at(0.5)   # 例如 90.0 表示竖直向下
        """
        tx, ty = self.tangent_at(ratio, samples)
        return math.degrees(math.atan2(ty, tx))

    def normal_at(self, ratio, side="left", samples=48) -> tuple:
        """
        路径上 ratio 位置的**单位法线向量**（英文版新增）。

        :param ratio: 0.0 ~ 1.0（按弧长定位）
        :param side: "left" 行进方向左侧 / "right" 右侧
            （SVG 的 y 轴向下，「左」指沿行进方向逆时针旋转 90°）
        :return: (nx, ny) 单位向量

        示例::
            nx, ny = p.normal_at(0.5)             # 左法线
            rx, ry = p.normal_at(0.5, "right")    # 右法线
        """
        tx, ty = self.tangent_at(ratio, samples)
        if str(side).lower().startswith("r"):
            return (-ty, tx)
        return (ty, -tx)

    def distance_to(self, other, samples=200) -> float:
        """
        本路径与另一条路径的**最短距离**（双方按弧长均匀采样后求最近点对，
        近似值，英文版新增）。 / Shortest distance between this path and another,
        approximated by nearest pair over uniform arc-length samples.

        :param other: 另一个 PathElement（或能 ``to_point_list()`` 的元素）
        :param samples: 每条路径的采样点数
        :return: 最短距离（浮点）

        示例::
            print(pa.distance_to(pb))     # 两条曲线离得多近
        """
        mine = self.to_point_list(samples)
        get = getattr(other, "to_point_list", None)
        theirs = get(samples) if callable(get) else [other.point_at(i / samples)
                                                     for i in range(samples + 1)]
        if not mine or not theirs:
            return float("inf")
        best = float("inf")
        for a in mine:
            for b in theirs:
                d = math.hypot(a[0] - b[0], a[1] - b[1])
                if d < best:
                    best = d
        return best

    def paste_line(self, distance, step=None, taper_angle=90.0,
                   start=0.0, end=1.0, **kw) -> "PathElement":
        """
        沿路径生成**梯形单元组成的粘贴线**（英文版新增，贴纸花边效果）：
        路径按弧长分成若干等长单元，每个单元是一条贴着路径的梯形
        （底边在路径上、顶边偏移 ``distance``），全部单元并入一条新路径。 /
        Build a pasted trim line along the path: arc-length equal units, each a
        trapezoid sitting on the path with its top edge offset by ``distance``.

        :param distance: 偏移距离，正值贴在行进方向**左侧**、负值贴**右侧**
        :param step: 每个单元的底边长度；缺省按「单元长约 = |distance|」自动取
        :param taper_angle: 梯形**腰与底边的夹角**（度，默认 90 = 矩形）；
                            小于 90 顶边收拢变梯形（如 60），90~180 外扩
        :param start: 起始比例（按弧长，0.0~1.0），如 0.3
        :param end: 结束比例（按弧长），如 0.7——只贴 0.3~0.7 这一段
        :param kw: 新路径的样式覆盖（fill_color / stroke_color 等，缺省继承本路径样式）
        :return: 新的 PathElement（原路径不变）

        示例（矩形外圈 30%~70% 段贴一圈宽 12 的梯形花边）::
            frame = pen.rect(40, 40, 200, 140).to_path_element()
            trim = frame.paste_line(12, step=10, taper_angle=60,
                                    start=0.3, end=0.7,
                                    fill_color="white", stroke_color="gray")
        """
        segs, lens, total = self._walk()
        if total <= 0 or abs(distance) < 1e-9:
            raise ValueError(t("err.paste_line_no_length"))
        a = max(0.0, min(1.0, float(start))) * total
        b = max(0.0, min(1.0, float(end))) * total
        if b < a:
            a, b = b, a
        span = b - a
        if span <= 1e-9:
            raise ValueError(t("err.paste_line_no_length"))
        step = abs(float(step)) if step else max(4.0, abs(float(distance)))
        n = max(1, int(math.ceil(span / step)))
        du = span / n
        # 内缩量：腰与底边夹角 θ，高 |distance| → 内底两端各缩 |distance|/tan θ
        # / inset per end: leg-to-base angle θ and height |distance|
        tan_a = math.tan(math.radians(float(taper_angle)))
        inset = abs(float(distance)) / tan_a if abs(tan_a) > 1e-9 else du
        inset = max(0.0, min(inset, du / 2.0))   # 夹住防止内底交叉 / clamp against bowties
        trim = PathElement(self.board, self.parent_node)
        for i in range(n):
            d0, d1 = a + i * du, min(a + (i + 1) * du, b)
            p0 = self._point_at_len(d0, segs, lens, total)
            p1 = self._point_at_len(d1, segs, lens, total)
            t0 = self.tangent_at(d0 / total)
            t1 = self.tangent_at(min(1.0, d1 / total))
            q0 = (p0[0] + t0[1] * distance, p0[1] - t0[0] * distance)
            q1 = (p1[0] + t1[1] * distance, p1[1] - t1[0] * distance)
            # 顶边沿切线方向收拢成梯形 / pull the top edge in along the tangents
            q0 = (q0[0] + t0[0] * inset, q0[1] + t0[1] * inset)
            q1 = (q1[0] - t1[0] * inset, q1[1] - t1[1] * inset)
            trim.move_to(p0[0], p0[1])
            trim.line_to(p1[0], p1[1])
            trim.line_to(q1[0], q1[1])
            trim.line_to(q0[0], q0[1])
            trim.close()
        trim._copy_paint_from(self)
        if kw:
            trim.update(**kw)
        return trim

    # ---------------------------------------------------------------
    # 弧长区间切片（英文版新增）：复制指定范围的一段路径
    # ---------------------------------------------------------------
    @staticmethod
    def _param_at_arc(seg, target) -> float:
        """
        本段上弧长 target 处对应的命令参数 t（0~1，内部方法）。

        与 `_param_at_arc` 反向的换算：累积弧长表按参数均匀采样，
        二分找到所在采样区间后线性插值回参数值。
        """
        pts, cum = seg._arc_table
        n = len(cum) - 1
        if target <= 0.0:
            return 0.0
        if target >= cum[-1]:
            return 1.0
        lo, hi = 0, n
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if cum[mid] <= target:
                lo = mid
            else:
                hi = mid
        span = cum[lo + 1] - cum[lo]
        u = 0.0 if span <= 1e-12 else (target - cum[lo]) / span
        return (lo + u) / float(n)

    @staticmethod
    def _split_arc(seg, t) -> tuple:
        """
        在参数 t 处把圆弧段一分为二（内部方法）。

        走 SVG 规范 F.6.5 端点参数化：由 arc_center() 拿到圆心与起止角，
        中点参数角一分为二，两个子弧沿用同一椭圆（rx/ry/旋转角），
        大弧/方向标记按子弧扫过角重新判定——只要子弧端点仍在同一椭圆上
        且标记正确，F.6.5 反推出来的圆心与原弧完全一致。

        :return: (前半段, 后半段)；退化弧（无圆心）按直线近似拆分
        """
        info = seg.arc_center()
        if info is None:
            mid = seg.point_at(t)
            return (PathSegment("L", seg.start, mid),
                    PathSegment("L", mid, seg.end))
        _cx, _cy, rx, ry, _phi, theta1, dtheta = info
        rot = seg.params[2]
        pmid = seg.point_at(t)

        def _sub(p_from, p_to, dt):
            """按扫过角 dt 造一条子弧（内部函数）；接近零退化为直线。"""
            if abs(dt) < 1e-9:
                return PathSegment("L", p_from, p_to)
            return PathSegment("A", p_from, p_to, params=(
                rx, ry, rot, abs(dt) > math.pi + 1e-9, dt > 0))

        return (_sub(seg.start, pmid, dtheta * t),
                _sub(pmid, seg.end, dtheta * (1.0 - t)))

    @classmethod
    def _cut_segment(cls, seg, t0, t1):
        """
        取线段参数区间 [t0, t1] 的那一小段（内部方法），形状精确不变。

        C/Q 用 de Casteljau 两次分割（不经过编辑器 split 的 0.02 钳位，
        边界处不变形）；A 走 `_split_arc`；L/Z 闭边按线性插值。
        :return: 新的 PathSegment（原段不动）
        """
        if t0 <= 1e-9 and t1 >= 1.0 - 1e-9:
            return seg
        if seg.cmd == "A":
            front, _ = cls._split_arc(seg, t1)
            if t0 > 1e-9:
                _, front = cls._split_arc(front, t0 / t1)
            return front

        lerp = lambda a, b, u: (a[0] + (b[0] - a[0]) * u,
                                a[1] + (b[1] - a[1]) * u)

        def _dec(pts, u):
            """de Casteljau 一次分割：返回（前半控制点组, 后半控制点组）。"""
            if len(pts) == 4:            # C 三次 / cubic
                q0, q1, q2 = lerp(*pts[0:2], u), lerp(pts[1], pts[2], u), lerp(pts[2], pts[3], u)
                r0, r1 = lerp(q0, q1, u), lerp(q1, q2, u)
                s = lerp(r0, r1, u)
                return ((pts[0], q0, r0, s), (s, r1, q2, pts[3]))
            q0, q1 = lerp(*pts, u)       # Q 二次 / quadratic
            s = lerp(q0, q1, u)
            return ((pts[0], q0, s), (s, q1, pts[2]))

        if seg.cmd == "L":
            return PathSegment("L", lerp(seg.start, seg.end, t0),
                               lerp(seg.start, seg.end, t1))
        if seg.cmd == "C":
            pts = (seg.start,) + tuple(seg.ctrls) + (seg.end,)
        elif seg.cmd == "Q":
            pts = (seg.start,) + tuple(seg.ctrls) + (seg.end,)
        else:
            return seg
        left, _ = _dec(pts, t1)          # 前半段覆盖 [0, t1] / left half covers [0, t1]
        if t0 > 1e-9:
            _, left = _dec(left, t0 / t1)  # 再取 [t0, t1] / then keep [t0, t1]
        ctrls = left[1:-1]
        cmd = "C" if len(left) == 4 else "Q"
        return PathSegment(cmd, left[0], left[-1], ctrls=ctrls)

    def slice(self, start=0.0, end=1.0, samples=48, **kw) -> "PathElement":
        """
        复制路径上指定**弧长区间**的一段，返回新路径（原路径不变，
        英文版新增）。 / Copy the portion of the path inside the given
        arc-length range into a new PathElement (the original stays).

        :param start: 起始比例（按真弧长，0.0~1.0），如 0.3
        :param end: 结束比例（按真弧长），如 0.7
        :param samples: 曲线采样精度（定位切分点用）
        :param kw: 新路径的样式覆盖（fill_color / stroke_color 等，
            缺省继承本路径样式）
        :return: 新的 PathElement

        区间边界落在某一段中间时该段被精确切分：直线/闭合边按线性插值，
        贝塞尔曲线走 de Casteljau 分割，圆弧经 SVG 规范 F.6.5 端点参数化
        拆成两条同椭圆子弧——切出来的新路径与原路径逐点重合。
        支持多子路径（M 断开的路径）：不连续处自动抬笔（move_to）。

        示例（复制钢琴路径 30%~70% 那一段）::
            piano2 = piano.slice(0.3, 0.7)
            piano2.translate(0, 40)      # 拿到手的就是普通路径 / it is a normal path
        """
        segs, lens, total = self._walk(samples)
        if total <= 0:
            raise ValueError(t("err.slice_no_length"))
        a = max(0.0, min(1.0, float(start))) * total
        b = max(0.0, min(1.0, float(end))) * total
        if b < a:
            a, b = b, a
        if b - a <= 1e-9:
            raise ValueError(t("err.slice_no_length"))
        new = PathElement(self.board, self.parent_node)
        acc = 0.0
        last = None          # 新路径当前点（判断要不要抬笔 / current point of the new path）
        for s, l in zip(segs, lens):
            s0, s1 = acc, acc + l
            acc = s1
            lo, hi = max(a, s0), min(b, s1)
            if hi - lo <= total * 1e-9:      # 与区间无交集 / no overlap with the range
                continue
            t0 = 0.0 if lo <= s0 + 1e-9 else self._param_at_arc(s, lo - s0)
            t1 = 1.0 if hi >= s1 - 1e-9 else self._param_at_arc(s, hi - s0)
            piece = self._cut_segment(s, t0, t1)
            if last is None or math.hypot(piece.start[0] - last[0],
                                          piece.start[1] - last[1]) > 1e-6:
                new.move_to(*piece.start)    # 子路径断开处抬笔 / lift the pen at subpath gaps
            new._cmds.append(piece.to_d())
            new._cur = piece.end
            last = piece.end
        new._sync()
        new._copy_paint_from(self)
        if kw:
            new.update(**kw)
        return new

    def bbox(self) -> tuple:
        """路径包围盒（按顶点采样近似）。 / Path bounding box, approximated from sampled vertices. """
        pts = self.to_point_list(120)
        if not pts:
            return (0, 0, 0, 0)
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        return (min(xs), min(ys), max(xs), max(ys))

    # ---------------------------------------------------------------
    # 路径查看与调整辅助（英文版新增，见 malight.pathkit）
    # ---------------------------------------------------------------
    def editor(self, refresh=False) -> "PathEditor":
        """
        取得本路径的编辑器（可查看 / 拖动锚点与控制点）。 / Get a PathEditor for this path so you can inspect and drag its anchors and control points.

        :param refresh: 是否强制重新解析当前 d 串（外部改过 d 后传 True）
        :return: PathEditor

        示例::
            ed = p.editor()
            ed.anchors[1].move_to(200, 80)      # 拖动第 2 个锚点
            ed.controls[0].move_by(0, -30)      # 拖动第 1 个调整点
        """
        from ..pathkit import PathEditor
        ed = getattr(self, "_editor", None)
        if ed is None or ed.path is not self:
            ed = PathEditor(self)
            self._editor = ed
        elif refresh or ed.to_d() != self.get_d():
            ed.reload()
        return ed

    def segments(self) -> list:
        """
        取路径的全部线段对象（每段含起点/终点/控制点）。 / Return every PathSegment, each carrying its start, end and control points.

        :return: [PathSegment, ...]

        示例::
            for s in p.segments():
                print(s.cmd, s.start, s.end)
        """
        return self.editor().segments

    def anchors(self) -> list:
        """
        取全部锚点对象（曲线的起点、终点、拐点）。 / Return every anchor point: the curve start, end and corner points.

        :return: [PathPoint, ...]

        示例::
            for a in p.anchors():
                print(a.role, a.pos)
            p.anchors()[1].move_to(220, 90)     # 直接拖
        """
        return self.editor().anchors

    def controls(self) -> list:
        """
        取全部控制点对象（贝塞尔曲线的调整点）。 / Return every control point, i.e. the Bézier handles.

        :return: [PathPoint, ...]

        示例::
            for c in p.controls():
                print(c.role, c.pos)
        """
        return self.editor().controls

    def anchor_points(self) -> list:
        """
        取全部锚点坐标（纯坐标版，便于打印 / 传参）。 / Return every anchor coordinate as plain tuples, handy for printing or passing around.

        :return: [(x, y), ...]

        示例::
            p.anchor_points()     # [(50.0, 50.0), (200.0, 50.0)]
        """
        return [a.pos for a in self.anchors()]

    def control_points(self) -> list:
        """
        取全部控制点坐标（纯坐标版）。 / Return all control-point coordinates as plain tuples.

        :return: [(x, y), ...]

        示例::
            p.control_points()    # [(100.0, 20.0), (150.0, 120.0)]
        """
        return [c.pos for c in self.controls()]

    def move_anchor(self, index, x, y) -> "PathElement":
        """
        移动第 index 个锚点（改完立即生效）。 / Move the anchor at index and apply it immediately.

        :param index: 锚点序号（从 0 开始，支持负数）
        :return: self（可链式）

        示例::
            p.move_anchor(0, 60, 60)      # 把起点挪到 (60,60)
            p.move_anchor(-1, 300, 200)   # 把终点挪到 (300,200)
        """
        self.editor().move_anchor(index, x, y)
        return self

    def move_control(self, seg_index, ctrl_index, x, y) -> "PathElement":
        """
        移动「第 seg_index 段」的第 ctrl_index 个调整点（改完立即生效）。 / Move control point ctrl_index of segment seg_index and apply it immediately.

        :return: self（可链式）

        示例::
            p.move_control(0, 0, 120, 40)   # 改变第 0 段的弧度
        """
        self.editor().move_control(seg_index, ctrl_index, x, y)
        return self

    def describe(self) -> str:
        """
        生成路径结构说明（每段的起点/调整点/终点 + 全部锚点坐标）。 / Build a readable path report: start / controls / end per segment, plus every anchor.

        :return: 多行文本（不打印）

        示例::
            print(p.describe())
        """
        return self.editor().describe()

    def print_points(self) -> str:
        """
        打印路径结构说明（看曲线有几个点、点在哪）。 / Print the path report so you can see how many points a curve has and where they sit.

        :return: 同样内容的字符串

        示例::
            p.print_points()
        """
        return self.editor().print_report()

    def show_points(self, board=None, **kw) -> "GroupElement":
        """
        在画布上画出锚点（方块）与调整杆（线 + 圆点），像钢笔工具一样。 / Draw anchors as squares and handles as lines with round dots, just like a pen tool.

        :param board: 绘图板（默认取所属绘图板）
        :param kw: 透传给 PathEditor.show（颜色 / 大小 / 是否标序号）
        :return: 承载标记的 GroupElement

        示例::
            p.show_points()               # 标出所有点
            p.show_points(labels=True)    # 带锚点序号
        """
        return self.editor().show(board=board, **kw)

    def smooth(self, tightness=1.0) -> "PathElement":
        """
        把路径中的折线顶点平滑为贝塞尔曲线（Catmull-Rom 转样条，
        对应中文版 `平滑路径`）。 / Smooth the polyline vertices into a Bézier curve.

        :param tightness: 张力系数，1.0 为标准

        示例::
            p.move_to(50, 200)
            for pt in [(120, 100), (200, 220), (280, 90), (360, 180)]:
                p.line_to(*pt)
            p.smooth()   # 折线变光滑曲线
        """
        # 提取顶点（仅支持 M/L/Z 组成的路径）
        verts = []
        for tok in self._cmds:
            if tok.startswith("M") or tok.startswith("L"):
                x, y = tok[1:].split(",")
                verts.append((float(x), float(y)))
            elif tok.startswith("Z") and verts:
                verts.append(verts[0])
        if len(verts) < 3:
            return self
        closed = verts[0] == verts[-1]
        n = len(verts) - (1 if closed else 0)
        self._cmds = []
        self._cur = verts[0]
        self._start = verts[0]
        self._cmd(f"M{self._pt(*verts[0])}")
        for i in range(n - (0 if closed else 1)):
            p0 = verts[(i - 1) % n]
            p1 = verts[i % n]
            p2 = verts[(i + 1) % n]
            p3 = verts[(i + 2) % n]
            c1 = (p1[0] + (p2[0] - p0[0]) / 6.0 * tightness,
                  p1[1] + (p2[1] - p0[1]) / 6.0 * tightness)
            c2 = (p2[0] - (p3[0] - p1[0]) / 6.0 * tightness,
                  p2[1] - (p3[1] - p1[1]) / 6.0 * tightness)
            self.cubic_to(c1, c2, p2)
        if closed:
            self.close()
        return self

    # ---------------------------------------------------------------
    # 内部辅助
    # ---------------------------------------------------------------
    def _copy_mutable_state(self, other):
        """
        克隆时各复制一份命令列表（内部方法）。

        ``clone`` 是浅拷贝，不这么做的话克隆体和原路径会**共用** ``_cmds``：
        之后往任一条上继续画，另一条的 ``d`` 也会跟着变。

        示例（内部）::

            twin = p.clone(); twin.line_to(300, 200)   # 原路径 p 不受影响
        """
        other._cmds = list(self._cmds)
        other._cur = self._cur
        other._start = self._start
        other._heading = self._heading
        other._last_quad_ctrl = self._last_quad_ctrl
        other._editor = None      # 编辑器绑定在原元素上，克隆体按需重建

    def _copy_paint_from(self, other) -> "PathElement":
        """
        复制另一元素的填充/描边样式到本路径（内部方法）。

        示例（一般内部使用）::
            new_path._copy_paint_from(old_circle)
        """
        for k in ("fill", "stroke", "stroke-width", "stroke-dasharray",
                  "stroke-linecap", "stroke-linejoin", "fill-rule", "opacity"):
            if k in other.node.attribs:
                self.node.set(k, other.node.attribs[k])
        return self

# ===========================================================================
# 使用示例
# ===========================================================================
# 在 PyCharm 里点绿色三角直接运行本文件即可；也可命令行：
#     python -m malight.elements.path
# ===========================================================================
if __name__ == "__main__":
    import os

    from malight import Malight, ColorName, FillRule
    from malight.pathkit import PathEditor

    _out = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        "..", "..", "output"))
    pen = Malight(os.path.join(_out, "demo_path"), width=660, height=420)
    pen.set_background_color(ColorName.WHITESMOKE)

    # -----------------------------------------------------------------
    # 1) 命令式绘制：移动 / 直线 / 贝塞尔 / 圆弧 / 闭合 / 1) Command-style drawing: move, line, Bezier, arc, close
    # -----------------------------------------------------------------
    p = pen.path(fill_color="none", stroke_color=ColorName.TOMATO,
                 stroke_width=3)
    p.move_to(60, 320)                                  # 起笔 / start
    p.line_to(140, 180)                                 # 直线 / line
    p.cubic_to((200, 80), (300, 80), (360, 180))        # 三次贝塞尔（2 个控制点） / cubic Bezier, two control points
    p.quad_to((420, 240), (480, 180))                   # 二次贝塞尔（1 个控制点） / quadratic Bezier, one control point
    p.arc_to(40, (560, 240), sweep=1)                   # 圆弧 / arc

    # -----------------------------------------------------------------
    # 2) 看结构：每一段的起点 / 调整点 / 终点都能打印出来 / 2) Inspect the structure: every segment's start, control and end point prints
    # -----------------------------------------------------------------
    print(p.describe())          # 对应中文版「路径元素」的看点能力 / The point inspection the original edition's path element offered

    # -----------------------------------------------------------------
    # 3) 调整：拖动锚点与控制点（改完立刻写回路径，无需手动 apply） / 3) Edit: drag anchors and control points, written back to the path at once
    # -----------------------------------------------------------------
    print("锚点: / anchors:", p.anchor_points())        # 所有锚点坐标 / every anchor coordinate
    print("调整点: / control points:", p.control_points())     # 所有贝塞尔控制柄坐标 / every Bezier handle coordinate
    print("带调整点的段号: / segments with control points:", p.editor().curve_indices())   # 直线段没有调整点 / line segments have no control points
    p.anchors()[2].move_to(200, 90)          # 拖第 3 个锚点 / drag the third anchor
    p.controls()[0].move_by(0, -20)          # 拖第 1 个调整点 / drag the first control point
    p.move_anchor(1, 150, 200)               # 也可以按索引直接改 / or address it by index
    p.move_control(2, 0, 210, 100)           # 第 2 段（三次贝塞尔）的第 1 个调整点 / the first handle of segment 2, a cubic

    # -----------------------------------------------------------------
    # 4) 结构编辑：加点（形状不变）/ 反转方向 / 点位存档 / 4) Structure edits: insert a point without changing the shape, reverse, save points
    # -----------------------------------------------------------------
    ed = p.editor()                          # 等价于 PathEditor(p) / the same as PathEditor(p)
    ed.insert_anchor(1, 0.5)                 # 在第 1 段中点插入锚点（形状不变） / insert an anchor at the middle of segment 1, shape unchanged
    ed.reverse()                             # 起终点互换 / swap start and end
    ed.save_json(os.path.join(_out, "path_points.json"))   # 点位存档 / save the points

    # 5) 可视化：把锚点（方块）与调整杆（线 + 圆点）画出来看 / 5) Visualise: anchors as squares, handles as lines with dots
    p.show_points(labels=True)

    # -----------------------------------------------------------------
    # 6) 几何信息：长度 / 弧长取点 / 切线法线 / 包围盒 / 平移所有命令 / 6) Geometry: length, arc-length point, tangent & normal, bbox, translate
    # -----------------------------------------------------------------
    _len = p.length()
    print("路径长度 ≈ %.2f / path length ≈ %.2f" % (_len, _len))
    print("弧长 30%% 处坐标: / point at 30%% of arc length:", tuple(round(v, 2) for v in p.point_at(0.3)))
    print("切线向量 / tangent:", tuple(round(v, 3) for v in p.tangent_at(0.3)),
          "| 切线角 / angle:", round(p.tangent_angle_at(0.3), 2))
    print("左法线 / left normal:", tuple(round(v, 3) for v in p.normal_at(0.3)))
    print("绝对弧长 50 处: / at distance 50:", tuple(round(v, 2) for v in p.point_at_distance(50)))
    print("包围盒: / bounding box:", tuple(round(v, 1) for v in p.bbox()))

    # -----------------------------------------------------------------
    # 6b) 沿路径贴一圈梯形粘贴线 / 6b) paste a trim line of trapezoid units along the path
    # -----------------------------------------------------------------
    trim = p.paste_line(14, step=16, fill_color=ColorName.LAVENDER,
                        stroke_color=ColorName.DIMGRAY, stroke_width=0.6)
    print("粘贴线段数: / trim units:", trim.get_d().count("Z"))

    # -----------------------------------------------------------------
    # 7) 更多绘制命令：水平/垂直直线、整圆、平滑连接、圆角 / 7) More commands: horizontal and vertical lines, full circle, smooth joins
    # -----------------------------------------------------------------
    q = pen.path(fill_color="none", stroke_color=ColorName.STEELBLUE,
                 stroke_width=3)
    q.move_to(60, 380)
    q.h_line_to(200)                 # 水平线 / horizontal line
    q.v_line_to(350)                 # 垂直线 / vertical line
    pen.text(280, 400, "h_line_to / v_line_to", font_size=13,
             fill_color=ColorName.DIMGRAY, h_align="middle")

    ring = pen.path(fill_color="none", stroke_color=ColorName.SEAGREEN,
                    stroke_width=3)
    ring.move_to(560, 340)           # 先定一个点（半径 = 它与圆心的距离） / fix one point first: the radius is its distance to the centre
    ring.circle_to((560, 385))       # 画整圆 / draw the full circle

    # -----------------------------------------------------------------
    # 8) 填充规则：即使是一条 path 也能用 EVENODD 挖洞（多子路径） / 8) Fill rule: EVENODD punches holes using several subpaths in one path
    # -----------------------------------------------------------------
    ring2 = pen.path(fill_color=ColorName.TEAL, fill_rule=FillRule.EVENODD,
                     stroke_color="none")
    ring2.move_to(490, 60)
    ring2.circle_to((490, 105))      # 外圈（半径 45） / outer ring, radius 45
    ring2.new_subpath(490, 75)       # 起一条新子路径 = 内圈起点 / a new subpath starts the inner ring
    ring2.circle_to((490, 105))      # 内圈（半径 30）→ 与 EVENODD 配合挖出孔洞 / inner ring, radius 30: EVENODD turns it into a hole

    # -----------------------------------------------------------------
    # 9) 布尔运算（两个路径求并/交/差，返回新 PathElement） / 9) Boolean ops (union, intersection, difference) return a new PathElement
    # -----------------------------------------------------------------
    a = pen.path(fill_color="none", stroke_color=ColorName.NAVY)
    a.move_to(100, 60)
    a.circle_to((130, 90))
    b = pen.path(fill_color="none", stroke_color=ColorName.CRIMSON)
    b.move_to(150, 60)
    b.circle_to((130, 90))
    try:
        merged = a.union(b)
        print("布尔并集结果 d 长度: / union result d length:", len(merged.get_d()))
    except Exception as exc:                 # 需要 shapely 等可选依赖 / requires optional dependencies such as shapely
        print("布尔运算需要可选依赖，跳过: / boolean ops need an optional dependency, skipping:", type(exc).__name__)

    pen.finish()
    pen.svg_editor()
# ---------------------------------------------------------------------------
# 底部导入：show_points() 的返回注解引用 GroupElement，而 group.py 又继承本模块 / Bottom import: show_points()'s return annotation names GroupElement, which subclasses
# 的 Element —— 顶部互相导入会循环；放到文件末尾两个问题都解决。 / the Element defined here - a top-level import would cycle; the bottom solves both.
# ---------------------------------------------------------------------------
from .group import GroupElement  # noqa: E402
