# -*- coding: utf-8 -*-
"""
路径 HTML 编辑器的跨语言一致性校验（check_htmleditor_js）
=========================================================

`PathHTMLEditor` 生成的页面里带着一套 JS 点位模型（`buildGroups` / `toD` /
`moveAnchor` / `splitSegment`），与 Python 侧的 `PathSegment` / `PathEditor`
是**两份实现**。两份实现一旦漂移，用户在浏览器里拖出来的 d 串就跟他复制走的
代码对不上 —— 而且这种错**不会报错**，只会安静地给出错误坐标。

本脚本把页面里的 JS **原样抽出来**（`<script>` 里 DOM 之前的那段纯函数），
用 Node 跑一遍，逐项与 Python 的结果比对：

    1. ``toD()``                    == ``segments_to_d(segs)``
    2. 锚点 / 调整点个数              == ``PathEditor.anchor_count`` / ``control_count``
    3. 首个锚点坐标                   == ``PathEditor.anchor_positions()[0]``
    4. **逐个锚点**拖到同一个目标坐标，两种模式各比一次：
         - 「锚点连动调整杆」关 == ``PathEditor.move_anchor(i, x, y)``
         - 「锚点连动调整杆」开 == ``PathEditor.move_anchor(i, x, y, link_handles=True)``
       （第 4 条最容易错：M 段在 d 串里用的是 end，JS 侧必须 start/end 一起写；
         而连动模式漏了某侧调整杆，也只会安静地给出错的弧度）
    5. 逐段 ``splitSegment(i, .5)``  == ``PathSegment.split(0.5)``，L / C / Q 各测一遍
    6. 圆弧段拒绝拆分                == ``NotImplementedError``

M / Z 段不在拆分比对范围内：UI 里双击只会命中可绘制的 L / C / Q 段，
而 Python 的 ``split()`` 对 M / Z 会返回一个奇怪的 Z 段（历史行为），
拿它当标准反而会把 JS 带偏。

用例里特意留了一条「脏小数」（曲线中点是 1/8 的倍数，会落到 3~4 位小数）：
Python 的 ``to_d()`` 用 ``"%.4f"`` 去尾零、JS 用 ``Math.round(v*10000)/10000``，
只有这种坐标才能把两者的数字格式化差异逼出来。全是整数坐标的用例是测不到的。

Cross-language consistency check: the generated page carries its own JS point model
next to the Python one, and the two silently drift apart if nobody compares them.
This script lifts the JS out of the generated HTML and runs it under Node.

**没装 Node 的机器会自动跳过**（打印 SKIP 并返回 0），所以它不会挡住回归。

用法 / Usage::

    python tools/check_htmleditor_js.py
    python tools/check_htmleditor_js.py --self-test    # 注入错误，自检检查器本身
    MALIGHT_NODE=/path/to/node python tools/check_htmleditor_js.py   # 指定解释器
"""

from __future__ import print_function

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from malight import Malight                                        # noqa: E402
from malight.pathkit import (PathEditor, PathHTMLEditor,          # noqa: E402
                             parse_path_d, segments_to_d)

#: 用例字段：
#:   name  说明
#:   d     d 串
#:   drag  要拖动比对的锚点序号（挑「带调整杆」的锚点，才能覆盖连动分支）
#:   split 要比对拆分的段号
#:   arc   圆弧段号（可选，None 表示无）
CASES = (
    {"name": "直线 + 三次 + 二次 + 闭合",
     "d": "M40,200 L120,120 C160,60 260,60 300,120 Q340,180 400,140 Z",
     "drag": [0, 1, 2], "split": [1, 2, 3], "arc": None},
    {"name": "脏小数（曲线中点是 1/8 倍数）",
     "d": "M0,0 C10,33 70,77 90,11",
     "drag": [0, 1], "split": [1], "arc": None},
    {"name": "圆弧（不可拆）",
     "d": "M20,120 A60,60 0 0,1 140,120 L140,180",
     "drag": [1], "split": [2], "arc": 1},
    {"name": "多子路径",
     "d": "M20,20 L80,20 M140,20 L200,20",
     "drag": [0, 2], "split": [1, 3], "arc": None},
)

#: 拖锚点时统一拖到这个坐标
DRAG_TO = (50, 60)

#: DOM 与纯逻辑的分界线：这行之前没有任何 document / window 引用
SPLIT_MARK = "var stage = document.getElementById"


# ===========================================================================
# 自检：故意把页面 JS 改坏，检查器必须每一条都报出来
# ===========================================================================
# 为什么要有这个：一个「啥都比不出来」的检查器会一直报绿，比没有还危险。
# 写这些用例时已经踩过两次坑 —— 替换字符串跟模板对不上、或者拖的锚点压根
# 没走到那条分支，于是「测试通过」其实什么都没测。所以把破坏固化下来，
# 每次跑 --self-test 都确认检查器仍然抓得住这些真实错法。
#: (说明, 原文, 改后, d 串, 拖的锚点, 拆分的段, 圆弧段)
MUTATIONS = (
    ("坐标精度（4 位退成 2 位）",
     "return String(Math.round(v * 10000) / 10000);",
     "return String(Math.round(v * 100) / 100);",
     "M0,0 C10,33 70,77 90,11", [0, 1], [1], None),
    ("M 段只挂 start 锚点",
     'last = [["start", si], ["end", si]];',
     'last = [["start", si]];',
     "M40,200 L120,120 C160,60 260,60 300,120", [0, 1], [1], None),
    ("顶层锚点只写 start 不写 end",
     'if (refs[i][0] === "start") s.start = [x, y]; else s.end = [x, y];',
     'if (refs[i][0] === "start") s.start = [x, y];',
     "M40,200 L120,120 C160,60 260,60 300,120", [0, 1], [1], None),
    ("圆弧被当成可拆分",
     'if (s.cmd === "A"){ notify(ui("arc_no_split")); return false; }\n'
     '  if (s.cmd !== "L" && s.cmd !== "C" && s.cmd !== "Q") return false;',
     'if (s.cmd !== "L" && s.cmd !== "C" && s.cmd !== "Q" '
     '&& s.cmd !== "A") return false;',
     "M20,120 A60,60 0 0,1 140,120 L140,180", [1], [2], 1),
    ("圆弧 large-arc / sweep 写反",
     '(q[3] ? 1 : 0) + "," + (q[4] ? 1 : 0)',
     '(q[3] ? 0 : 1) + "," + (q[4] ? 0 : 1)',
     "M20,120 A60,60 0 0,1 140,120 L140,180", [1], [2], 1),
    ("连动调整杆方向反了",
     'g.ctrls[which] = [g.ctrls[which][0] + dx, g.ctrls[which][1] + dy];',
     'g.ctrls[which] = [g.ctrls[which][0] - dx, g.ctrls[which][1] - dy];',
     "M40,200 L120,120 C160,60 260,60 300,120", [1, 2], [1], None),
    ("连动时把终点侧调整杆当起点侧",
     'var which = refs[r][0] === "start" ? 0 : 1;',
     'var which = 0;',
     "M40,200 L120,120 C160,60 260,60 300,120", [2], [1], None),
    ("直线拆分的中点算错",
     "var mid = lerp(s.start, s.end);",
     "var mid = lerp(s.start, lerp(s.start, s.end));",
     "M40,200 L120,120 C160,60 260,60 300,120", [0, 1], [1, 2], None),
)


def self_test(node):
    """逐个注入 MUTATIONS，确认检查器都能抓到（内部函数）。"""
    print("=== 自检：注入 %d 处错误，检查器必须全部报出 ===" % len(MUTATIONS))
    real = PathHTMLEditor.render
    missed = []
    for tag, old, new, d, drag, split, arc in MUTATIONS:
        if old not in real(_dummy_editor()):
            print("  [%s] 模板里找不到要替换的片段，用例已过期" % tag)
            missed.append(tag)
            continue

        def broken(self, _old=old, _new=new):
            return real(self).replace(_old, _new)

        PathHTMLEditor.render = broken
        try:
            bad = run_case(node, {"name": tag, "d": d, "drag": drag,
                                  "split": split, "arc": arc})
        finally:
            PathHTMLEditor.render = real
        print("  [%s] %s" % (tag, "抓到（%d 处不一致）" % len(bad) if bad
                             else "!! 漏了，检查器对此项无效"))
        if not bad:
            missed.append(tag)
    if missed:
        print("\n自检失败：%d 项漏网 -> %s" % (len(missed), "、".join(missed)))
        return 1
    print("\n自检通过：注入的错误全部被抓到。")
    return 0


def _dummy_editor():
    """自检用的最小编辑器，只为拿一份页面文本来验证替换片段是否存在。"""
    pen = Malight("self-test", width=120, height=120)
    p = pen.path(fill_color="none", stroke_color="#333")
    p.set_d("M0,0 L10,10")
    return PathHTMLEditor(p)


def find_node():
    """找 node 解释器：环境变量 MALIGHT_NODE > PATH；都没有返回 None。"""
    env = os.environ.get("MALIGHT_NODE")
    if env and os.path.exists(env):
        return env
    return shutil.which("node") or shutil.which("nodejs")


def probe_js(html, case):
    """把页面里的 JS 纯函数段抽出来，拼上比对用的调用（内部函数）。"""
    script = re.search(r"<script>(.*?)</script>", html, re.S).group(1)
    body = script[:script.index(SPLIT_MARK)]
    dx, dy = DRAG_TO
    return body + """
var out = {};
// DATA 必须每次深拷贝，"复位"式的重来才干净 / deep-clone DATA every round
var fresh = function(){ segs = JSON.parse(JSON.stringify(DATA.segments)); };
var g = buildGroups();
out.d = toD();
out.anchors = g.anchors.length;
out.ctrls = g.ctrls.length;
out.a0 = anchorPos(g.anchors[0]);
var DRAGS = %s, DXC = %d, DYC = %d;
for (var n = 0; n < DRAGS.length; n++){
  var i = DRAGS[n];
  linkHandles = false;
  fresh();
  moveAnchor(buildGroups().anchors[i], DXC, DYC);
  out["drag" + i + "_plain"] = toD();
  linkHandles = true;
  fresh();
  moveAnchor(buildGroups().anchors[i], DXC, DYC);
  out["drag" + i + "_link"] = toD();
}
linkHandles = false;
var SPLITS = %s;
for (var m = 0; m < SPLITS.length; m++){
  var si = SPLITS[m];
  fresh();
  var blocked = splitSegment(si, 0.5) === false;
  out["split" + si + "blocked"] = blocked;
  out["split" + si] = blocked ? null : toD();
}
var arc = %s;
if (arc !== null){
  fresh();
  out.arcBlocked = splitSegment(arc, 0.5) === false;
}
console.log(JSON.stringify(out));
""" % (json.dumps(case["drag"]), dx, dy, json.dumps(case["split"]),
       "null" if case["arc"] is None else str(case["arc"]))


def expected(case, p):
    """Python 侧的期望值（内部函数）。

    `PathEditor.apply()` 会把改动写回路径元素，所以每次动用同一个 p 之前
    都要先把 d 串还原，否则第二轮的基准就已经是上一轮改过的形状了。
    """
    d = case["d"]
    segs = parse_path_d(d)
    p.set_d(d)
    ed = PathEditor(p)
    exp = {"d": segments_to_d(segs),
           "anchors": ed.anchor_count,
           "ctrls": ed.control_count,
           "a0": list(ed.anchor_positions()[0])}
    for i in case["drag"]:
        p.set_d(d)
        e1 = PathEditor(p)
        e1.move_anchor(i, DRAG_TO[0], DRAG_TO[1])
        exp["drag%d_plain" % i] = e1.to_d()
        p.set_d(d)
        e2 = PathEditor(p)
        e2.move_anchor(i, DRAG_TO[0], DRAG_TO[1], link_handles=True)
        exp["drag%d_link" % i] = e2.to_d()
    for si in case["split"]:
        first, second = segs[si].split(0.5)
        exp["split%d" % si] = segments_to_d(segs[:si] + [first, second] + segs[si + 1:])
        exp["split%dblocked" % si] = False
    if case["arc"] is not None:
        try:
            segs[case["arc"]].split(0.5)
            exp["arcBlocked"] = "Python 本应抛 NotImplementedError，却没抛"
        except NotImplementedError:
            exp["arcBlocked"] = True
    return exp


def run_case(node, case):
    """跑一个形状的全部比对项，返回不一致说明列表（空列表 = 全对）。"""
    pen = Malight("x", width=440, height=240)
    p = pen.path(fill_color="none", stroke_color="#333")
    p.set_d(case["d"])
    js = probe_js(PathHTMLEditor(p).render(), case)

    tmp = tempfile.mkdtemp(prefix="malight_jscheck_")
    path = os.path.join(tmp, "probe.js")
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(js)
        r = subprocess.run([node, path], stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT, text=True,
                           encoding="utf-8", errors="replace")
        text = (r.stdout or "").strip()
        if r.returncode != 0 or not text:
            return ["%s: node 执行失败（exit=%d）\n%s"
                    % (case["name"], r.returncode, text[-600:])]
        got = json.loads(text.splitlines()[-1])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    bad = []
    for key, want in sorted(expected(case, p).items()):
        have = got.get(key)
        if key == "a0":
            same = [round(float(v), 6) for v in have] == [round(float(v), 6)
                                                          for v in want]
        else:
            same = have == want
        if not same:
            bad.append("%s / %s\n     js = %r\n     py = %r"
                       % (case["name"], key, have, want))
    return bad


def main(argv):
    node = find_node()
    if not node:
        print("SKIP：未找到 node（可用 MALIGHT_NODE 指定路径），"
              "跳过页面 JS / Python 一致性校验")
        return 0
    if "--self-test" in argv:
        return self_test(node)
    print("=== 路径 HTML 编辑器：JS 与 Python 点位模型一致性校验 ===")
    print("node:", node)
    bad = []
    for case in CASES:
        print("  %-22s | %s" % (case["name"], case["d"][:52]))
        bad += run_case(node, case)
    if bad:
        print("\n不一致 %d 处（页面拖出来的结果和 Python 算的对不上）：" % len(bad))
        for item in bad:
            print("  -", item)
        return 1
    print("\n全部一致：页面上拖出来的 d 串与 Python 算的一模一样"
          "（含锚点连动调整杆的两种模式）。")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
