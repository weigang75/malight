# -*- coding: utf-8 -*-
"""
路径坐标解析（pathkit.parser）—— SVG path d 串 <-> 结构化线段列表
====================================================================

Parse an SVG path d string into structured segments, and render segments back to d.

英文版 malight 内部使用。把 `d` 字符串解析为「每段一个 PathSegment」，
坐标全部归一化为**绝对坐标**，并把这些快捷命令展开，方便后续查看与调整：

- ``H``/``V``（水平/垂直线）  → 展开为 ``L``
- ``S``（平滑三次贝塞尔）     → 展开为 ``C``（自动算出第一个控制点）
- ``T``（平滑二次贝塞尔）     → 展开为 ``Q``（自动算出控制点）
- 相对命令（小写 m/l/c/...）  → 转成绝对坐标

这样每条曲线都有明确的「起点 / 终点 / 控制点」，就是你在 Illustrator、
Figma 里用钢笔工具看到的那些点。

使用示例::

    from malight.pathkit import parse_path_d
    segs = parse_path_d("M0,0 C10,20 30,20 40,0 L80,0 Z")
    for s in segs:
        print(s)
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

from .segment import PathSegment


# 每个命令的参数个数
ARG_COUNT = {"M": 2, "L": 2, "H": 1, "V": 1, "C": 6, "S": 4,
             "Q": 4, "T": 2, "A": 7, "Z": 0}

# 记号：命令字母 或 数字（含小数、指数、负号）
_TOKEN_RE = None


def tokenize(d) -> list:
    """
    把 d 字符串切成「命令字母 / 数字」记号列表。 / Split a d string into a token list of command letters and numbers.

    :param d: SVG path 的 d 串
    :return: ["M", "0", "0", "C", "10", "20", ...]

    示例::
        tokenize("M0,0L10,10")     # ['M', '0', '0', 'L', '10', '10']
    """
    import re
    global _TOKEN_RE
    if _TOKEN_RE is None:
        _TOKEN_RE = re.compile(r"[MmLlHhVvCcSsQqTtAaZz]|-?\d*\.?\d+(?:[eE][-+]?\d+)?")
    return _TOKEN_RE.findall(str(d))


def parse_path_d(d) -> list:
    """
    解析 SVG path 的 d 字符串为线段列表（绝对坐标，已展开快捷命令）。 / Parse an SVG path d string into segments with absolute coordinates and shortcut commands expanded.

    :param d: 如 "M10,10 L50,50 C60,60 70,70 80,80 Z"
    :return: [PathSegment, ...]；无法解析的片段会被跳过

    示例::
        segs = parse_path_d("M0,0 h100 v50 z")
        print(segs[0].cmd, segs[0].end)      # M (0.0, 0.0)
        print(segs[1].cmd, segs[1].end)      # L (100.0, 0.0)
        print(segs[2].cmd, segs[2].end)      # L (100.0, 50.0)
        print(segs[3].cmd)                   # Z
    """
    tokens = tokenize(d)
    segs = []
    i = 0
    cmd = None
    cur = (0.0, 0.0)          # 当前点
    sub_start = (0.0, 0.0)    # 当前子路径起点（Z 用）
    prev_cmd = None           # 上一个命令（S/T 反射控制点用）
    prev_cubic_ctrl = None    # 上一段三次贝塞尔的第二控制点
    prev_quad_ctrl = None     # 上一段二次贝塞尔的控制点

    while i < len(tokens):
        tok = tokens[i]
        if tok.isalpha():
            cmd = tok
            i += 1
            if cmd.upper() == "Z":
                segs.append(PathSegment("Z", start=cur, end=sub_start, ctrls=()))
                cur = sub_start
                prev_cmd, prev_cubic_ctrl, prev_quad_ctrl = "Z", None, None
                continue
        elif cmd is None:
            i += 1               # 忽略开头非法记号
            continue
        else:
            # 隐式重复上一命令：M 后面连续的数字按 L 处理（SVG 规范）
            if cmd == "M":
                cmd = "L"
            elif cmd == "m":
                cmd = "l"

        up = cmd.upper()
        n = ARG_COUNT.get(up)
        if n is None or i + n > len(tokens):
            break
        try:
            vals = [float(v) for v in tokens[i:i + n]]
        except ValueError:
            i += 1
            continue
        i += n
        rel = cmd.islower()

        def _abs(x, y):
            """相对坐标转绝对坐标（内部函数）。"""
            return (cur[0] + x, cur[1] + y) if rel else (x, y)

        if up == "M":
            cur = _abs(*vals)
            sub_start = cur
            segs.append(PathSegment("M", start=cur, end=cur, ctrls=()))
            prev_cubic_ctrl = prev_quad_ctrl = None

        elif up == "L":
            p = _abs(*vals)
            segs.append(PathSegment("L", start=cur, end=p, ctrls=()))
            cur = p
            prev_cubic_ctrl = prev_quad_ctrl = None

        elif up == "H":
            p = (cur[0] + vals[0], cur[1]) if rel else (vals[0], cur[1])
            segs.append(PathSegment("L", start=cur, end=p, ctrls=()))
            cur = p
            prev_cubic_ctrl = prev_quad_ctrl = None

        elif up == "V":
            p = (cur[0], cur[1] + vals[0]) if rel else (cur[0], vals[0])
            segs.append(PathSegment("L", start=cur, end=p, ctrls=()))
            cur = p
            prev_cubic_ctrl = prev_quad_ctrl = None

        elif up == "C":
            c1 = _abs(vals[0], vals[1])
            c2 = _abs(vals[2], vals[3])
            p = _abs(vals[4], vals[5])
            segs.append(PathSegment("C", start=cur, end=p, ctrls=(c1, c2)))
            cur = p
            prev_cubic_ctrl, prev_quad_ctrl = c2, None

        elif up == "S":
            # 第一控制点 = 上一段第二控制点关于当前点的反射
            if prev_cmd in ("C", "S") and prev_cubic_ctrl is not None:
                c1 = (2 * cur[0] - prev_cubic_ctrl[0], 2 * cur[1] - prev_cubic_ctrl[1])
            else:
                c1 = cur
            c2 = _abs(vals[0], vals[1])
            p = _abs(vals[2], vals[3])
            segs.append(PathSegment("C", start=cur, end=p, ctrls=(c1, c2)))
            cur = p
            prev_cubic_ctrl, prev_quad_ctrl = c2, None

        elif up == "Q":
            c1 = _abs(vals[0], vals[1])
            p = _abs(vals[2], vals[3])
            segs.append(PathSegment("Q", start=cur, end=p, ctrls=(c1,)))
            cur = p
            prev_quad_ctrl, prev_cubic_ctrl = c1, None

        elif up == "T":
            if prev_cmd in ("Q", "T") and prev_quad_ctrl is not None:
                c1 = (2 * cur[0] - prev_quad_ctrl[0], 2 * cur[1] - prev_quad_ctrl[1])
            else:
                c1 = cur
            p = _abs(vals[0], vals[1])
            segs.append(PathSegment("Q", start=cur, end=p, ctrls=(c1,)))
            cur = p
            prev_quad_ctrl, prev_cubic_ctrl = c1, None

        elif up == "A":
            rx, ry, rot, large, sweep = vals[0], vals[1], vals[2], vals[3], vals[4]
            p = _abs(vals[5], vals[6])
            segs.append(PathSegment("A", start=cur, end=p, ctrls=(),
                                    params=(rx, ry, rot, bool(large), bool(sweep))))
            cur = p
            prev_cubic_ctrl = prev_quad_ctrl = None

        prev_cmd = up

    return segs


def segments_to_d(segs) -> str:
    """
    把线段列表还原为 SVG path 的 d 字符串。 / Render a segment list back into an SVG path d string.

    :param segs: [PathSegment, ...]
    :return: d 串

    示例::
        segs = parse_path_d("M0,0 h100")
        segments_to_d(segs)     # "M0,0 L100,0"
    """
    return " ".join(s.to_d() for s in segs if s.cmd)


def reverse_segments(segs) -> list:
    """
    反转线段列表（起终点互换、控制点顺序颠倒、圆弧方向取反）。 / Reverse a segment list: endpoints swap, control-point order flips and arcs take the opposite sweep.

    用于 `PathElement.reverse()`（原版依赖 svgpathtools，本版自带实现）。

    :param segs: [PathSegment, ...]
    :return: 反转后的新列表

    示例::
        segs = reverse_segments(parse_path_d("M0,0 L100,0"))
        segments_to_d(segs)     # "M100,0 L0,0"
    """
    drawable = [s for s in segs if s.cmd != "M"]
    drawable.reverse()
    out = []
    start = (segs[-1].end if segs else (0.0, 0.0))
    out.append(PathSegment("M", start=start, end=start, ctrls=()))
    cur = start
    for s in drawable:
        if s.cmd == "Z":
            continue                      # 闭合在两段之间没有意义，跳过
        if s.cmd == "L":
            out.append(PathSegment("L", start=cur, end=s.start, ctrls=()))
        elif s.cmd == "C":
            out.append(PathSegment("C", start=cur, end=s.start,
                                   ctrls=(s.ctrls[1], s.ctrls[0])))
        elif s.cmd == "Q":
            out.append(PathSegment("Q", start=cur, end=s.start, ctrls=(s.ctrls[0],)))
        elif s.cmd == "A":
            p = s.params
            out.append(PathSegment("A", start=cur, end=s.start, ctrls=(),
                                   params=(p[0], p[1], p[2], p[3], not p[4])))
        cur = s.start
    return out


# ===========================================================================
# 使用示例（直接在 PyCharm 里点绿色三角运行本文件即可）
# ===========================================================================
if __name__ == "__main__":
    import os
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

    print("=== 1) 解析（含相对命令 / 快捷命令展开）=== / === 1) parse, with relative commands and shortcuts expanded ===")
    d = "M10,10 h100 v50 s20,20 40,0 t40,0 a20,20 0 0,1 40,0 Z"
    for s in parse_path_d(d):
        print("  ", s.describe())

    print("\n=== 2) 还原为 d 串（H/V/S/T 已展开为 L/C/Q，坐标等价）=== / \n=== 2) back to a d string, H/V/S/T expanded to L/C/Q with equal coordinates ===")
    print("  ", segments_to_d(parse_path_d(d)))

    print("\n=== 3) 反转路径方向 === / \n=== 3) reverse the path direction ===")
    segs = parse_path_d("M0,0 L100,0 C110,20 130,20 140,0")
    print("   原: /    before:", segments_to_d(segs))
    print("   后: /    after:", segments_to_d(reverse_segments(segs)))

    print("\n=== 4) 曲线取点（弧长参数化，用于定位/测长）=== / \n=== 4) points on a curve, arc-length parameterised ===")
    seg = parse_path_d("M0,0 C0,100 100,100 100,0")[1]
    _len = seg.length()
    # 双语字符串里同一个占位符出现两次（中英各一次），参数要给两遍 / a bilingual string repeats each placeholder, so pass it twice
    print("   曲线长度 ≈ %.2f /    curve length ≈ %.2f" % (_len, _len))
    print("   1/4 处坐标: /    point at 1/4:", tuple(round(v, 2) for v in seg.point_at(0.25)))
