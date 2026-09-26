# -*- coding: utf-8 -*-
"""
路径 UI 编辑器（pathkit.htmleditor）—— PathHTMLEditor 类
=========================================================

PathHTMLEditor: export a path as one self-contained HTML file you drag points in.

`PathEditor` 只能在 Python 里改坐标：改一次、出一张图、看一眼，再改。
本类补上「手」——把同一条路径导出成**一个自我包含的 .html**，
用鼠标拖锚点与调整杆，右侧实时给出 d 串和可直接粘贴的 malight 代码。

导出的页面**零依赖、纯离线**（没有任何 CDN、框架或构建步骤），
双击就能用，也可以直接发给别人；页面里自带 中文 / English 切换。

三种用法:

1. **改一条已有路径**
   ``p = pen.path(...)`` 画好 → ``PathHTMLEditor(p).save("edit.html")``。
2. **从 d 串开始**
   ``PathHTMLEditor(d="M20,200 C80,40 180,40 240,200").save("edit.html")``。
3. **接着 Python 的进度改**（配合 `PathEditor`）
   ``ed.save_json("points.json")`` 存档 → 页面里拖 → 下载回 points.json
   → ``ed.load_json("points.json")`` 读回。
   页面下载的 JSON 与 `PathEditor.to_dict()` **同一套结构**，可以直接读回。

页面能做什么 / 不能做什么:

* 能：拖锚点、拖调整点、「锚点连动调整杆」开关、双击某段在中点插入锚点、
  **双击锚点删除该点**（浏览器原生确认框提醒，相邻两段合并为一段；复位可撤销）、
  选中锚点后**切换段线类型**（直线 L / 三次 C / 二次 Q，Q→C 精确升阶、C→Q 取
  切线交点近似）、**平滑 / 尖角锚点**（平滑锚点拖一侧调整杆时另一侧自动镜像）、
  **背景图层**（``background_svg=`` 内嵌已保存的 SVG 垫底，「背景」按钮控制
  显隐、透明度滑条可调，路径叠在原图上改，所见即所得）、
  **取点模式**（「取点」开启后点画布即记录坐标，显示 x/y 与相邻两点 dx/dy/d，
  自动生成链式代码：同 y → ``h_line_to``、同 x → ``v_line_to``——
  对应中文版 `获取坐标点.html`）、
  右侧代码面板 **set_d / 链式 / 取点三种写法**（与 `chain_code` 同一套生成
  逻辑、回归里逐字符比对）、方向键微调（Shift 走 10 像素）、复位、
  下载点位 JSON、复制 d 串与代码。
* 不能：拖完之后**回写**正在运行的 Python 进程（浏览器里改的只是页面自己的数据）。
  要闭环就走上面第 3 种用法，用 JSON 往返。
  下载的 JSON 会带上平滑标记（``sms`` / ``sme`` 两个附加键），
  `PathEditor.to_dict()` 读回时自动忽略，双向兼容。
* 圆弧段（A）不支持拆分锚点、也不能改类型 —— 与 `PathSegment.split()` 的限制一致。

配套便捷方法 `Malight.svg_editor(path)`：一条命令生成上面这一切——
先 ``finish()`` 保存 SVG，再调它，HTML 自动内嵌背景图层（对应中文版
`获取坐标点.html` 的加强版，定位 + 调路径二合一）。

「锚点连动调整杆」勾上时，锚点位移多少、挂在它这一侧的调整杆就位移多少
（曲线不会突然拐个弯）—— 这正是 `PathEditor.move_anchor(..., link_handles=True)`；
取消勾选则只动锚点本身，与默认的 `move_anchor()` 一致。

页面里的 JS 与 Python 是**两份实现**：``tools/check_htmleditor_js.py`` 会把页面
那段 JS 抽出来用 Node 跑一遍，逐锚点确认两边拖出来的 d 串一模一样
（连动 / 不连动两种模式都比，「链式」「取点」代码也逐字符比对），并且脚本自带
``--self-test`` —— 注入 10 处真实错法，确认比对项不是「永远为空所以永远通过」。

主页面的 UI 文案取自 `malight.i18n` 的 ``html.*`` 词条，
导出时按 `use_language()` 取 en / zh 两套内嵌进页面，所以一份文件两种语言都能看。
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
import re

from ..i18n import is_chinese, t, use_language
from ..tools import paint_path
from .parser import parse_path_d, segments_to_d


#: 页面里要用的全部标签词条（`i18n` 里 en / zh 两套都要配齐，否则页面会露出键名）
UI_KEYS = (
    "html.title", "html.subtitle", "html.hint",
    "html.segments", "html.anchors", "html.controls",
    "html.d_label", "html.code_label", "html.code_setd", "html.code_chain",
    "html.code_pick", "html.bg", "html.pick", "html.clear_pick",
    "html.select_path",
    "html.copy", "html.copied",
    "html.copy_fail", "html.reset", "html.handles", "html.link_handles",
    "html.json", "html.json_hint", "html.arc_no_split",
    "html.del_confirm", "html.no_delete", "html.anchor_type",
    "html.to_line", "html.to_cubic", "html.to_quad",
    "html.smooth", "html.corner",
    "html.fit", "html.zoom_hint", "html.sel_pos",
)


def _ui_messages() -> dict:
    """
    把 ``html.*`` 词条按语言取出来，供页面内切换。

    取词时用 ``use_language()`` 临时切语言，**不会污染全局设置**
    （这正是 `use_language` 存在的意义：文档生成与这里取两套文案都用它）。
    """
    out = {}
    for code in ("en", "zh"):
        with use_language(code):
            out[code] = {k.split(".", 1)[1]: t(k) for k in UI_KEYS}
    return out


# ---------------------------------------------------------------------------
# 数字格式化：与页面 JS 的 num() 严格一致（4 位小数、去尾零、-0 归 0），
# 这是 chain_code 与页面 JS chainCode() 逐字符比对能成立的前提。
# / Number formatting must stay in lockstep with the page's num() (4 decimals,
# trailing zeros stripped, -0 normalised) — chain_code and the page's JS
# chainCode() are compared character by character in the Node gate.
# ---------------------------------------------------------------------------
def _fmt_num(v) -> str:
    """按页面 JS 的 num() 规则格式化数字（内部函数）。"""
    s = "%.4f" % float(v)
    s = s.rstrip("0").rstrip(".")
    return "0" if s in ("", "-0") else s


def _fmt_pt(p) -> str:
    """坐标点 → "x,y"（与 JS 的 pt() 一致，内部函数）。"""
    return _fmt_num(p[0]) + "," + _fmt_num(p[1])


def chain_code(segments, width, height, fill_color="none",
               stroke_color="#e63946", stroke_width=3) -> str:
    """
    把段列表转成 malight **链式** Python 代码。 / Render segments as chained malight Python code.

    页面右侧代码面板的「链式」页签用的就是这套格式（页面 JS 里还有一份
    同逻辑的 ``chainCode()``，`tools/check_htmleditor_js.py` 会让两者逐字符
    比对，防止漂移）。每个方法都返回 ``PathElement``，所以可以一路 ``.`` 下去；
    圆弧段用 `PathElement.ellipse_arc_to`（能表达 rx ≠ ry 与旋转角，
    比 `arc_to` 更通用）。::

        from malight.pathkit.htmleditor import chain_code
        print(chain_code(parse_path_d("M0,0 L80,0"), 200, 120))

    :param segments: ``parse_path_d`` 出的段列表（或页面 JSON 的 segments）
    :param width: 画布宽
    :param height: 画布高
    :param fill_color: 填充色
    :param stroke_color: 描边色
    :param stroke_width: 线宽
    :return: 可直接粘贴运行的 Python 源码文本
    """
    calls = []
    for s in segments:
        cmd = getattr(s, "cmd", None) or (s.get("cmd") if isinstance(s, dict) else None)
        if not cmd:
            continue
        end = getattr(s, "end", None) or (s.get("end") if isinstance(s, dict) else None)
        ctrls = getattr(s, "ctrls", None)
        if ctrls is None and isinstance(s, dict):
            ctrls = s.get("ctrls") or ()
        if cmd == "M":
            calls.append(".move_to(%s, %s)" % (_fmt_num(end[0]), _fmt_num(end[1])))
        elif cmd == "L":
            calls.append(".line_to(%s, %s)" % (_fmt_num(end[0]), _fmt_num(end[1])))
        elif cmd == "C":
            calls.append(".cubic_to((%s), (%s), (%s))"
                         % (_fmt_pt(ctrls[0]), _fmt_pt(ctrls[1]), _fmt_pt(end)))
        elif cmd == "Q":
            calls.append(".quad_to((%s), (%s))" % (_fmt_pt(ctrls[0]), _fmt_pt(end)))
        elif cmd == "A":
            params = getattr(s, "params", None)
            if params is None and isinstance(s, dict):
                params = s.get("params") or (0, 0, 0, 0, 0)
            params = list(params or (0, 0, 0, 0, 0))
            calls.append(".ellipse_arc_to(%s, %s, (%s), sweep=%d, large_arc=%d,"
                         " x_axis_rotation=%s)"
                         % (_fmt_num(params[0]), _fmt_num(params[1]), _fmt_pt(end),
                            1 if params[4] else 0, 1 if params[3] else 0,
                            _fmt_num(params[2])))
        elif cmd == "Z":
            calls.append(".close()")
    if not calls:
        calls.append(".move_to(0, 0)")
    return ("from malight import Malight\n\n"
            "pen = Malight(\"curve\", width=%d, height=%d)\n"
            "p = (pen.path(fill_color=\"%s\", stroke_color=\"%s\", stroke_width=%s)\n"
            "     %s)\n"
            "pen.finish()\n"
            % (width, height, fill_color, stroke_color, stroke_width,
               "\n     ".join(calls)))


# ===========================================================================
# 页面模板 / Page template
# ===========================================================================
# 用 @@TOKEN@@ 占位 + str.replace 注入，**不走 str.format** ——
# 页面里的 JS / CSS 到处是花括号，用 format 得把每一处都写成 {{ }}，改一处漏一处。
_PAGE = r"""<!DOCTYPE html>
<html lang="@@LANG@@">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>@@TITLE@@</title>
<!-- Generated by malight.pathkit.PathHTMLEditor — do not edit by hand. -->
<style>
:root{--bg:#f4f4f6;--card:#fff;--ink:#1c1c1e;--muted:#6b6b70;--line:#dcdce1;
      --accent:#e63946;--anchor:#1f6feb;--ctrl:#d9822b}
*{box-sizing:border-box}
body{margin:0;padding:24px;background:var(--bg);color:var(--ink);
     font:14px/1.6 -apple-system,"Segoe UI","Microsoft YaHei",sans-serif}
h1{margin:0 0 4px;font-size:18px;font-weight:600}
.sub{color:var(--muted);margin:0 0 18px}
.wrap{display:flex;gap:20px;flex-wrap:wrap;align-items:flex-start}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px}
.stage{position:relative;flex:0 0 auto}
.side{flex:1 1 320px;min-width:300px;display:flex;flex-direction:column;gap:12px}
.stats{display:flex;gap:10px}
.stat{flex:1;background:var(--card);border:1px solid var(--line);
      border-radius:10px;padding:10px 12px}
.stat b{display:block;font-size:20px;font-weight:600;margin-top:2px}
.stat span{color:var(--muted);font-size:12px}
.row{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px}
button{font:inherit;padding:6px 12px;border:1px solid var(--line);background:var(--card);
       color:var(--ink);border-radius:8px;cursor:pointer}
button:hover{border-color:var(--muted)}
button.on{background:var(--ink);color:var(--card);border-color:var(--ink)}
label.chk{display:flex;align-items:center;gap:6px;cursor:pointer;color:var(--muted)}
pre{background:var(--card);border:1px solid var(--line);border-radius:10px;
    padding:12px;margin:0;overflow:auto;font-size:12.5px;line-height:1.55;
    font-family:ui-monospace,Consolas,"Courier New",monospace;white-space:pre-wrap;
    word-break:break-all;max-height:270px}
.lbl{display:flex;justify-content:space-between;align-items:center;
     margin-bottom:6px;color:var(--muted);font-size:12px}
.hint{color:var(--muted);font-size:12.5px}
.lang{margin-left:auto}
.toast{position:fixed;left:50%;bottom:28px;transform:translateX(-50%);
       background:var(--ink);color:var(--card);padding:8px 16px;border-radius:8px;
       font-size:13px;opacity:0;pointer-events:none;transition:opacity .2s}
#bgwrap{position:absolute;top:0;left:0;pointer-events:none;display:none}
#bgwrap svg{width:100%;height:100%}
#pick-tip{position:absolute;display:none;background:rgba(28,28,30,.85);color:#fff;
          padding:4px 8px;border-radius:6px;font-size:11px;line-height:1.5;
          pointer-events:none;white-space:pre;z-index:5}
input[type=range]{vertical-align:middle;width:90px}
</style>
</head>
<body>
<div class="lbl"><span></span>
  <span class="lang"><button id="l-en">English</button> <button id="l-zh">简体中文</button></span>
</div>
<h1 id="t-title"></h1>
<p class="sub" id="t-sub"></p>
<div class="wrap">
  <div class="stage card"><div id="bgwrap" style="width:@@W@@px;height:@@H@@px">@@BGSVG@@</div>
    <svg id="stage" width="@@W@@" height="@@H@@"></svg>
    <div id="pick-tip"></div>
    <div class="row" id="row-btns">
      <button id="b-reset"></button>
      <button id="b-fit"></button>
      <button id="b-handles"></button>
      <button id="b-bg"></button>
      <input type="range" id="bg-op" min="10" max="100" value="50" style="display:none">
      <label class="chk" id="path-sel-wrap" style="display:none"><span id="t-paths"></span>
        <select id="path-sel" style="font:inherit;padding:4px 6px;border:1px solid var(--line);
                border-radius:6px;background:var(--card);color:var(--ink)"></select></label>
      <button id="b-pick"></button>
      <button id="b-clearpick"></button>
      <button id="b-json"></button>
      <label class="chk"><input type="checkbox" id="c-link" checked><span id="t-link"></span></label>
    </div>
    <p class="hint" id="t-hint" style="margin:10px 0 0"></p>
  </div>
  <div class="side">
    <div class="row" id="a-tools" style="display:none;margin-top:0">
      <span class="hint" id="t-atype"></span>
      <button id="b-l"></button><button id="b-c"></button><button id="b-q"></button>
      <button id="b-smooth"></button>
    </div>
    <p class="hint" id="sel-pos" style="display:none;margin:6px 0 0;font-weight:600"></p>
    <div class="stats">
      <div class="stat"><span id="t-seg"></span><b id="n-seg">0</b></div>
      <div class="stat"><span id="t-anc"></span><b id="n-anc">0</b></div>
      <div class="stat"><span id="t-ctl"></span><b id="n-ctl">0</b></div>
    </div>
    <div><div class="lbl"><span id="t-d"></span></div><pre id="out-d"></pre></div>
    <div>
      <div class="lbl"><span id="t-code"></span>
        <span><button id="b-setd"></button> <button id="b-chain"></button>
              <button id="b-picktab"></button> <button id="b-copy"></button></span></div>
      <pre id="out-code"></pre>
    </div>
    <p class="hint" id="t-json"></p>
  </div>
</div>
<div class="toast" id="toast"></div>
<script>
var DATA = @@DATA@@;
var UI = @@UI@@;
var LANG = "@@LANG@@";

var segs = JSON.parse(JSON.stringify(DATA.segments));   // DATA 必须保持原样，"复位"才有东西可回 / keep DATA pristine so Reset has something to restore
var grid = DATA.grid || 0;
var W = DATA.w, H = DATA.h;
var showHandles = true, linkHandles = true, sel = null;
var drag = null;
// 取点模式状态：picks=[{x,y},...] 纯数据，Node 闸门直接测 pickCalls(picks)。
// / Pick-mode state: picks=[{x,y},...] pure data, pickCalls(picks) is gate-tested.
var pickMode = false, picks = [];
// 视图缩放/平移：viewBox 驱动（x/y/w/h 为用户坐标系可见窗口），滚轮缩放、
// 中键拖拽平移。「适应」按钮回到整幅画布。操作 stage 的函数在 DOM 段。
// / View zoom & pan driven by the viewBox (x/y/w/h = visible window in user
// coordinates): wheel zooms around the cursor, middle-drag pans, Fit resets.
// The stage-touching helpers live in the DOM section below.
var view = { x: 0, y: 0, w: W, h: H };
// 多路径：pathsData=[{id,name,d,segments,fill,stroke,strokeWidth},...]，
// curPath 是当前编辑的路径下标；背景里对应节点会被隐藏，避免与编辑层重影。
// / Multi-path: pathsData carries every path on the board; curPath is the one
// being edited. Its copy in the background is hidden so the editable overlay
// is the only visible instance.
var pathsData = DATA.paths || [];
var curPath = 0;
function curStyle(){
  var p = pathsData[curPath];
  return p || {fill: DATA.fill, stroke: DATA.stroke, strokeWidth: DATA.strokeWidth};
}
// 手动识别双击要用的上次按下记录 / last-press record for manual double-click detection
var lastDownTime = 0, lastDownX = 0, lastDownY = 0;

// "var stage" 之前是**纯逻辑段**：不碰 document / window，可被 Node 直接跑来做跨语言校验。
// 提示默认丢弃，DOM 段再把它接到页面上的 toast / no-op here, wired to the toast further down
var notify = function(msg){};

function ui(key, vars){
  var txt = (UI[LANG] && UI[LANG][key]) || (UI.en && UI.en[key]) || key;
  return txt.replace(/\{(\w+)\}/g, function(m, k){ return vars && (k in vars) ? vars[k] : m; });
}
function num(v){
  v = parseFloat(v);
  if (!isFinite(v)) v = 0;
  return String(Math.round(v * 10000) / 10000);
}
function pt(p){ return num(p[0]) + "," + num(p[1]); }

function toD(){
  var out = [];
  for (var i = 0; i < segs.length; i++){
    var s = segs[i];
    if (!s.cmd) continue;
    if (s.cmd === "M" || s.cmd === "L") out.push(s.cmd + pt(s.end));
    else if (s.cmd === "C") out.push("C" + pt(s.ctrls[0]) + " " + pt(s.ctrls[1]) + " " + pt(s.end));
    else if (s.cmd === "Q") out.push("Q" + pt(s.ctrls[0]) + " " + pt(s.end));
    else if (s.cmd === "A"){
      var q = s.params || [0, 0, 0, 0, 0];
      out.push("A" + num(q[0]) + "," + num(q[1]) + " " + num(q[2]) + " " +
               (q[3] ? 1 : 0) + "," + (q[4] ? 1 : 0) + " " + pt(s.end));
    }
    else if (s.cmd === "Z") out.push("Z");
  }
  return out.join(" ");
}

function buildGroups(){
  var groups = [], ctrls = [], last = null;
  for (var si = 0; si < segs.length; si++){
    var s = segs[si];
    if (s.cmd === "M"){
      last = [["start", si], ["end", si]];
      groups.push(last);
      continue;
    }
    if (last !== null) last.push(["start", si]);
    else { last = [["start", si]]; groups.push(last); }
    for (var k = 0; k < (s.ctrls || []).length; k++) ctrls.push([si, k]);
    if (s.cmd === "Z") last = null;
    else { last = [["end", si]]; groups.push(last); }
  }
  return { anchors: groups, ctrls: ctrls };
}

function applyAnchor(refs, x, y){
  for (var i = 0; i < refs.length; i++){
    var s = segs[refs[i][1]];
    if (refs[i][0] === "start") s.start = [x, y]; else s.end = [x, y];
  }
}
function anchorPos(refs){ var s = segs[refs[0][1]]; return refs[0][0] === "start" ? s.start : s.end; }
function moveAnchor(refs, x, y){
  var old = anchorPos(refs), dx = x - old[0], dy = y - old[1];
  applyAnchor(refs, x, y);
  if (!linkHandles) return;
  for (var j = 0; j < segs.length; j++){
    var g = segs[j];
    if (!g.ctrls || !g.ctrls.length) continue;
    for (var r = 0; r < refs.length; r++){
      if (refs[r][1] !== j) continue;
      if (g.cmd === "Q"){
        if (refs[r][0] === "start") g.ctrls[0] = [g.ctrls[0][0] + dx, g.ctrls[0][1] + dy];
      } else if (g.cmd === "C"){
        var which = refs[r][0] === "start" ? 0 : 1;
        g.ctrls[which] = [g.ctrls[which][0] + dx, g.ctrls[which][1] + dy];
      }
    }
  }
}

function splitSegment(si, t){
  var s = segs[si];
  if (s.cmd === "A"){ notify(ui("arc_no_split")); return false; }
  if (s.cmd !== "L" && s.cmd !== "C" && s.cmd !== "Q") return false;
  t = Math.max(0.02, Math.min(0.98, t));
  var lerp = function(a, b){ return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t]; };
  if (s.cmd === "L"){
    var mid = lerp(s.start, s.end);
    segs[si] = { cmd: "L", start: s.start, end: mid, ctrls: [], params: null };
    segs.splice(si + 1, 0, { cmd: "L", start: mid, end: s.end, ctrls: [], params: null });
  } else if (s.cmd === "C"){
    var q0 = lerp(s.start, s.ctrls[0]), q1 = lerp(s.ctrls[0], s.ctrls[1]),
        q2 = lerp(s.ctrls[1], s.end);
    var r0 = lerp(q0, q1), r1 = lerp(q1, q2), sp = lerp(r0, r1);
    segs[si] = { cmd: "C", start: s.start, end: sp, ctrls: [q0, r0], params: null };
    segs.splice(si + 1, 0, { cmd: "C", start: sp, end: s.end, ctrls: [r1, q2], params: null });
  } else {
    var u0 = lerp(s.start, s.ctrls[0]), u1 = lerp(s.ctrls[0], s.end), sp2 = lerp(u0, u1);
    segs[si] = { cmd: "Q", start: s.start, end: sp2, ctrls: [u0], params: null };
    segs.splice(si + 1, 0, { cmd: "Q", start: sp2, end: s.end, ctrls: [u1], params: null });
  }
  return true;
}

// 右侧代码面板当前页签："setd" | "chain" | "pick" / which code flavour the panel shows
var codeMode = "setd";

// set_d 写法 / the set_d flavour
function setdCode(){
  var c = curStyle();
  return 'from malight import Malight\n\n' +
    'pen = Malight("curve", width=' + W + ', height=' + H + ')\n' +
    'p = pen.path(fill_color="' + c.fill + '", stroke_color="' + c.stroke +
    '", stroke_width=' + c.strokeWidth + ')\n' +
    'p.set_d("' + toD() + '")\n' +
    'pen.finish()\n';
}
// 链式写法：与 Python 侧 chain_code() 是两份实现，Node 闸门逐字符比对。
// / The chained flavour — Python's chain_code() is its twin and the Node gate
// compares the two character by character.
function chainCode(){
  var calls = [];
  for (var i = 0; i < segs.length; i++){
    var s = segs[i];
    if (!s.cmd) continue;
    if (s.cmd === "M") calls.push(".move_to(" + num(s.end[0]) + ", " + num(s.end[1]) + ")");
    else if (s.cmd === "L") calls.push(".line_to(" + num(s.end[0]) + ", " + num(s.end[1]) + ")");
    else if (s.cmd === "C") calls.push(".cubic_to((" + pt(s.ctrls[0]) + "), (" +
                                       pt(s.ctrls[1]) + "), (" + pt(s.end) + "))");
    else if (s.cmd === "Q") calls.push(".quad_to((" + pt(s.ctrls[0]) + "), (" +
                                       pt(s.end) + "))");
    else if (s.cmd === "A"){
      // 弧段用 ellipse_arc_to：能表达 rx != ry 与旋转角 / ellipse_arc_to covers rx!=ry and rotation
      var q = s.params || [0, 0, 0, 0, 0];
      calls.push(".ellipse_arc_to(" + num(q[0]) + ", " + num(q[1]) + ", (" + pt(s.end) +
                 "), sweep=" + (q[4] ? 1 : 0) + ", large_arc=" + (q[3] ? 1 : 0) +
                 ", x_axis_rotation=" + num(q[2]) + ")");
    }
    else if (s.cmd === "Z") calls.push(".close()");
  }
  if (!calls.length) calls.push(".move_to(0, 0)");
  var c = curStyle();
  return 'from malight import Malight\n\n' +
    'pen = Malight("curve", width=' + W + ', height=' + H + ')\n' +
    'p = (pen.path(fill_color="' + c.fill + '", stroke_color="' + c.stroke +
    '", stroke_width=' + c.strokeWidth + ')\n' +
    '     ' + calls.join('\n     ') + ')\n' +
    'pen.finish()\n';
}

// ---- 取点模式 / pick mode ------------------------------------------------
// 取点序列 -> 链式调用串。与上一个点同 y 用 h_line_to、同 x 用 v_line_to
// （对应中文版 获取坐标点.html 的 水平线/垂直线），重复点跳过。
// / Pick sequence -> chained calls. Same y as the previous point -> h_line_to,
// same x -> v_line_to (mirrors the Chinese picker's 水平线/垂直线), duplicates skipped.
function pickCalls(list){
  var out = [];
  for (var i = 0; i < list.length; i++){
    var x = num(list[i].x), y = num(list[i].y);
    if (i === 0){ out.push(".move_to(" + x + ", " + y + ")"); continue; }
    var px = num(list[i - 1].x), py = num(list[i - 1].y);
    if (x === px && y === py) continue;               // 重复点 / duplicate pick
    if (y === py) out.push(".h_line_to(" + x + ")");
    else if (x === px) out.push(".v_line_to(" + y + ")");
    else out.push(".line_to(" + x + ", " + y + ")");
  }
  return out;
}
function pickSnippet(list){
  if (!list.length) return "";
  var c = curStyle();
  return 'from malight import Malight\n\n' +
    'pen = Malight("curve", width=' + W + ', height=' + H + ')\n' +
    'p = pen.path(fill_color="' + c.fill + '", stroke_color="' + c.stroke +
    '", stroke_width=' + c.strokeWidth + ')\n' +
    'p = (p\n     ' + pickCalls(list).join('\n     ') + ')\n' +
    'pen.finish()\n';
}

// ---- 锚点类型 / anchor type ---------------------------------------------
// 平滑标记存在段上：sms=起点侧锚点平滑，sme=终点侧。共享锚点两侧同步写，
// 读时任一侧为真即平滑。Python 侧没有这个概念，JSON 往返时多出的键会被忽略。
// / Smoothness lives on segments: sms = smooth at its start anchor, sme = at its
// end. Shared anchors write both sides; either side being set means smooth.
// Python ignores these extra keys on round-trip.
function anchorSmooth(refs){
  for (var i = 0; i < refs.length; i++){
    var s = segs[refs[i][1]];
    if (refs[i][0] === "start" ? s.sms : s.sme) return true;
  }
  return false;
}
function setAnchorSmooth(refs, on){
  for (var i = 0; i < refs.length; i++){
    var s = segs[refs[i][1]];
    if (refs[i][0] === "start") s.sms = on; else s.sme = on;
  }
}
// 锚点引出的可编辑段：优先「起点是它」的段，否则取「终点是它」的段。
// / The anchor's outgoing segment: prefer one starting here, else one ending here.
function segAt(refs){
  var i, r, s;
  for (i = 0; i < refs.length; i++){
    r = refs[i]; s = segs[r[1]];
    if (r[0] === "start" && s.cmd && "LCQA".indexOf(s.cmd) >= 0) return r[1];
  }
  for (i = 0; i < refs.length; i++){
    r = refs[i]; s = segs[r[1]];
    if (r[0] === "end" && s.cmd && "LCQA".indexOf(s.cmd) >= 0) return r[1];
  }
  return -1;
}
// 两条直线的交点（C→Q 用切线交点近似；平行/共线返回 null）/ Line-line intersection (null if parallel)
function lineIntersect(p1, p2, p3, p4){
  var d = (p2[0] - p1[0]) * (p4[1] - p3[1]) - (p2[1] - p1[1]) * (p4[0] - p3[0]);
  if (Math.abs(d) < 1e-9) return null;
  var t = ((p3[0] - p1[0]) * (p4[1] - p3[1]) - (p3[1] - p1[1]) * (p4[0] - p3[0])) / d;
  return [p1[0] + (p2[0] - p1[0]) * t, p1[1] + (p2[1] - p1[1]) * t];
}
// 段类型转换：L↔C↔Q。Q→C 精确升阶；C→Q 取两端切线交点（退化时取中点）；
// 任意→L 直接拉直。A / M / Z 不允许。/ Convert L<->C<->Q. Q->C elevates exactly;
// C->Q intersects the end tangents (midpoint fallback); anything ->L straightens.
function convertSegment(si, type){
  var s = segs[si];
  if (!s.cmd || "LCQ".indexOf(s.cmd) < 0 || "LCQ".indexOf(type) < 0) return false;
  if (s.cmd === type) return true;
  var a = s.start, b = s.end, keep = {sms: s.sms, sme: s.sme};
  if (type === "L"){
    segs[si] = {cmd: "L", start: a, end: b, ctrls: [], params: null,
                sms: keep.sms, sme: keep.sme};
  } else if (type === "C"){
    var c1 = [a[0] + (b[0] - a[0]) / 3, a[1] + (b[1] - a[1]) / 3];
    var c2 = [a[0] + 2 * (b[0] - a[0]) / 3, a[1] + 2 * (b[1] - a[1]) / 3];
    if (s.cmd === "Q"){
      // 二次升三次的精确控制点 / exact degree elevation from quad
      var q = s.ctrls[0];
      c1 = [a[0] + 2 * (q[0] - a[0]) / 3, a[1] + 2 * (q[1] - a[1]) / 3];
      c2 = [b[0] + 2 * (q[0] - b[0]) / 3, b[1] + 2 * (q[1] - b[1]) / 3];
    }
    segs[si] = {cmd: "C", start: a, end: b, ctrls: [c1, c2], params: null,
                sms: keep.sms, sme: keep.sme};
  } else {
    var cp;
    if (s.cmd === "C"){
      cp = lineIntersect(a, s.ctrls[0], b, s.ctrls[1]) ||
           [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2];
    } else {
      cp = [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2];
    }
    segs[si] = {cmd: "Q", start: a, end: b, ctrls: [cp], params: null,
                sms: keep.sms, sme: keep.sme};
  }
  return true;
}
// 删除锚点 i。三种情形：闭合角（组里有 Z）→ 删 Z 开口；子路径起点（M）→
// 删它引出的第一段、M 挪到该段终点；中间锚点 → 入段终点接出段终点、出段删除。
// / Delete anchor i. Three cases: closing corner (a Z in the group) -> drop the Z;
// subpath start (M) -> drop its first drawn segment and move M to that end;
// middle anchor -> the incoming segment ends at the outgoing's end, outgoing removed.
function deleteAnchor(i){
  var refs = groups().anchors[i];
  if (!refs || !refs.length) return false;
  var k, r, s;
  for (k = 0; k < refs.length; k++){
    r = refs[k];
    if (r[0] === "start" && segs[r[1]].cmd === "Z"){
      segs.splice(r[1], 1);
      return true;
    }
  }
  for (k = 0; k < refs.length; k++){
    r = refs[k]; s = segs[r[1]];
    if (s.cmd === "M"){
      var nxt = segs[r[1] + 1];
      if (!nxt || nxt.cmd === "Z") return false;
      segs[r[1]].start = nxt.end;
      segs[r[1]].end = nxt.end;
      segs.splice(r[1] + 1, 1);
      return true;
    }
  }
  var inc = -1, out = -1;
  for (k = 0; k < refs.length; k++){
    r = refs[k]; s = segs[r[1]];
    if (!s.cmd) continue;
    if (r[0] === "end" && inc < 0) inc = r[1];
    if (r[0] === "start" && out < 0) out = r[1];
  }
  if (inc < 0 || out < 0) return false;
  segs[inc].end = segs[out].end;
  segs.splice(out, 1);
  return true;
}

var stage = document.getElementById("stage");
var toast = document.getElementById("toast"), toastTimer = null;
notify = function(msg){
  toast.textContent = msg;
  toast.style.opacity = "1";
  if (toastTimer) clearTimeout(toastTimer);
  toastTimer = setTimeout(function(){ toast.style.opacity = "0"; }, 1800);
};
// 背景图层（若模板注入了背景 SVG）：默认隐藏、透明度默认 50%，滚轮缩放同层联动
// / bg layer, hidden by default, opacity 50% out of the box, zooms with the view
var bgwrap = document.getElementById("bgwrap");
// 背景层必须与 stage 逐像素对齐：bgwrap 是 absolute 定位在卡片 padding 盒
// 原点上，而 stage 在内容盒里（差一个卡片内边距）。stage 是 <svg>，没有
// offsetLeft/offsetTop，只能用 getBoundingClientRect 相对卡片算（扣掉边框）。
// / The bg layer must overlay the stage pixel-for-pixel: bgwrap is absolutely
// positioned at the card's padding-box origin while the stage sits in the
// content box. The stage is an <svg> with no offsetLeft/offsetTop, so measure
// with getBoundingClientRect relative to the card (minus its border).
(function(){
  // bgwrap 此刻 display:none，offsetParent 恒为 null，不能用；
  // 定位容器就是父级 .stage.card（position:relative），它始终可见。
  // / bgwrap is display:none here so offsetParent is always null; the
  // positioned ancestor is the parent .stage.card, which is always visible.
  var card = bgwrap.parentElement;
  if (!card) return;
  var sr = stage.getBoundingClientRect(), cr = card.getBoundingClientRect();
  var cs = getComputedStyle(card);
  var bl = parseFloat(cs.borderLeftWidth) || 0;
  var bt = parseFloat(cs.borderTopWidth) || 0;
  bgwrap.style.left = (sr.left - cr.left - bl) + "px";
  bgwrap.style.top = (sr.top - cr.top - bt) + "px";
})();
bgwrap.style.opacity = "0.5";
// 路径选择器：多条路径时出现，切换即加载对应段并隐藏背景里的原路径
// / Path selector: shown when the board has several paths. Switching loads that
// path's segments and hides its copy in the background (no double image).
function loadPath(i){
  var prev = pathsData[curPath];
  curPath = i;
  var p = pathsData[i];
  if (prev){ var n0 = bgwrap.querySelector('[id="' + prev.id + '"]'); if (n0) n0.style.display = ""; }
  if (p){ var n1 = bgwrap.querySelector('[id="' + p.id + '"]'); if (n1) n1.style.display = "none"; }
  segs = JSON.parse(JSON.stringify(p ? p.segments : DATA.segments));
  sel = null; picks = [];
  document.getElementById("pick-tip").style.display = "none";
  draw();
}
(function initPathSelector(){
  var selEl = document.getElementById("path-sel");
  if (pathsData.length > 1){
    for (var i = 0; i < pathsData.length; i++){
      var op = document.createElement("option");
      op.value = i;
      op.textContent = pathsData[i].name || pathsData[i].id;
      selEl.appendChild(op);
    }
    document.getElementById("path-sel-wrap").style.display = "inline-flex";
    selEl.onchange = function(){ loadPath(+this.value); };
  }
  if (pathsData.length) loadPath(0);
})();
function draw(){
  var g = buildGroups();
  var d = toD(), s = "";
  var vz = zoomFactor();   // 手柄等 UI 元素尺寸除以它，缩放后屏幕大小不变 / UI chrome stays the same on screen
  if (grid){
    for (var gx = 0; gx <= W; gx += grid)
      s += '<line x1="' + gx + '" y1="0" x2="' + gx + '" y2="' + H + '" stroke="#e6e6ea" stroke-width="' + (1 / vz) + '"/>';
    for (var gy = 0; gy <= H; gy += grid)
      s += '<line x1="0" y1="' + gy + '" x2="' + W + '" y2="' + gy + '" stroke="#e6e6ea" stroke-width="' + (1 / vz) + '"/>';
  }
  var cur = curStyle();   // 编辑层用当前路径自己的样式 / overlay wears the edited path's style
  s += '<path class="ps" d="' + d + '" fill="' + cur.fill +
       '" stroke="' + cur.stroke + '" stroke-width="' + cur.strokeWidth +
       '" stroke-linecap="round" stroke-linejoin="round"/>';
  if (showHandles){
    for (var i = 0; i < segs.length; i++){
      var seg = segs[i];
      if (!seg.ctrls || !seg.ctrls.length) continue;
      var pts = [seg.start].concat(seg.ctrls).concat([seg.end]);
      for (var k = 0; k + 1 < pts.length; k++)
        s += '<line x1="' + pts[k][0] + '" y1="' + pts[k][1] + '" x2="' + pts[k + 1][0] +
             '" y2="' + pts[k + 1][1] + '" stroke="#b9c2cf" stroke-width="' + (1 / vz) + '"/>';
    }
    for (var ci = 0; ci < g.ctrls.length; ci++){
      var ref = g.ctrls[ci], sg = segs[ref[0]], cp = sg.ctrls[ref[1]];
      var on = sel && sel.kind === "c" && sel.si === ref[0] && sel.ci === ref[1];
      s += '<circle class="ph" data-si="' + ref[0] + '" data-ci="' + ref[1] +
           '" cx="' + cp[0] + '" cy="' + cp[1] + '" r="' + ((on ? 6.5 : 5) / vz) +
           '" fill="' + (on ? "#f43f5e" : DATA.ctrl) + '" stroke="#fff" stroke-width="' +
           (1.5 / vz) + '" style="cursor:grab"/>';
      if (on)   // 选中记号：玫红外圈（屏幕尺寸恒定）/ selection ring, constant on screen
        s += '<circle cx="' + cp[0] + '" cy="' + cp[1] + '" r="' + (10 / vz) +
             '" fill="none" stroke="#f43f5e" stroke-width="' + (2 / vz) +
             '" pointer-events="none"/>';
    }
  }
  for (var ai = 0; ai < g.anchors.length; ai++){
    var ap = anchorPos(g.anchors[ai]);
    var on2 = sel && sel.kind === "a" && sel.i === ai;
    s += '<rect class="pa" data-i="' + ai + '" x="' + (ap[0] - 5.5 / vz) + '" y="' + (ap[1] - 5.5 / vz) +
         '" width="' + (11 / vz) + '" height="' + (11 / vz) + '" rx="' + (2 / vz) +
         '" fill="' + (on2 ? "#f43f5e" : DATA.anchor) +
         '" stroke="#fff" stroke-width="' + (1.5 / vz) + '" style="cursor:grab"/>';
    if (on2)  // 选中记号：玫红外圈 + 十字准星 / selection ring + crosshair
      s += '<circle cx="' + ap[0] + '" cy="' + ap[1] + '" r="' + (10 / vz) +
           '" fill="none" stroke="#f43f5e" stroke-width="' + (2 / vz) +
           '" pointer-events="none"/>' +
           '<line x1="' + (ap[0] - 14 / vz) + '" y1="' + ap[1] + '" x2="' + (ap[0] - 11 / vz) +
           '" y2="' + ap[1] + '" stroke="#f43f5e" stroke-width="' + (1.5 / vz) + '" pointer-events="none"/>' +
           '<line x1="' + (ap[0] + 11 / vz) + '" y1="' + ap[1] + '" x2="' + (ap[0] + 14 / vz) +
           '" y2="' + ap[1] + '" stroke="#f43f5e" stroke-width="' + (1.5 / vz) + '" pointer-events="none"/>' +
           '<line x1="' + ap[0] + '" y1="' + (ap[1] - 14 / vz) + '" x2="' + ap[0] +
           '" y2="' + (ap[1] - 11 / vz) + '" stroke="#f43f5e" stroke-width="' + (1.5 / vz) + '" pointer-events="none"/>' +
           '<line x1="' + ap[0] + '" y1="' + (ap[1] + 11 / vz) + '" x2="' + ap[0] +
           '" y2="' + (ap[1] + 14 / vz) + '" stroke="#f43f5e" stroke-width="' + (1.5 / vz) + '" pointer-events="none"/>';
  }
  // 取点叠加层：虚线折线 + 十字（最上层，不参与拖拽）/ pick overlay on top, non-interactive
  if (picks.length){
    var pts = "";
    for (var q = 0; q < picks.length; q++) pts += picks[q].x + "," + picks[q].y + " ";
    s += '<polyline points="' + pts.trim() + '" fill="none" stroke="#8b5cf6" ' +
         'stroke-width="' + (1.5 / vz) + '" stroke-dasharray="5 4" pointer-events="none"/>';
    for (q = 0; q < picks.length; q++){
      s += '<line x1="' + (picks[q].x - 7 / vz) + '" y1="' + picks[q].y + '" x2="' +
           (picks[q].x + 7 / vz) + '" y2="' + picks[q].y + '" stroke="#8b5cf6" ' +
           'stroke-width="' + (1.5 / vz) + '" pointer-events="none"/>';
      s += '<line x1="' + picks[q].x + '" y1="' + (picks[q].y - 7 / vz) + '" x2="' +
           picks[q].x + '" y2="' + (picks[q].y + 7 / vz) + '" stroke="#8b5cf6" ' +
           'stroke-width="' + (1.5 / vz) + '" pointer-events="none"/>';
    }
  }
  stage.innerHTML = s;
  document.getElementById("n-seg").textContent = segs.filter(function(x){ return x.cmd; }).length;
  document.getElementById("n-anc").textContent = g.anchors.length;
  document.getElementById("n-ctl").textContent = g.ctrls.length;
  document.getElementById("out-d").textContent = d;
  document.getElementById("out-code").textContent =
    codeMode === "chain" ? chainCode() :
    codeMode === "pick" ? pickSnippet(picks) : setdCode();
  // 代码页签高亮必须跟着 codeMode 走（只在 setLang 里设置的话，点击后不刷新）
  // / Tab highlight must follow codeMode - setLang alone never refreshes on click.
  document.getElementById("b-setd").className = codeMode === "setd" ? "on" : "";
  document.getElementById("b-chain").className = codeMode === "chain" ? "on" : "";
  document.getElementById("b-picktab").className = codeMode === "pick" ? "on" : "";
  // 锚点工具行：只在选中锚点时出现 / anchor tools row: only while an anchor is selected
  var at = document.getElementById("a-tools");
  if (sel && sel.kind === "a" && g.anchors[sel.i]){
    at.style.display = "flex";
    var refs = g.anchors[sel.i];
    var sm = anchorSmooth(refs);
    var bs = document.getElementById("b-smooth");
    bs.textContent = ui(sm ? "smooth" : "corner");
    bs.className = sm ? "on" : "";
    var si2 = segAt(refs);
    var cmd2 = si2 >= 0 ? segs[si2].cmd : "";
    document.getElementById("b-l").className = cmd2 === "L" ? "on" : "";
    document.getElementById("b-c").className = cmd2 === "C" ? "on" : "";
    document.getElementById("b-q").className = cmd2 === "Q" ? "on" : "";
  } else {
    at.style.display = "none";
  }
  // 选中点坐标（锚点与调整杆都显示，拖拽中实时刷新）/ selected point coords, live while dragging
  var sp = document.getElementById("sel-pos");
  if (sel){
    var pos = sel.kind === "a"
      ? (g.anchors[sel.i] ? anchorPos(g.anchors[sel.i]) : null)
      : (segs[sel.si] && segs[sel.si].ctrls ? segs[sel.si].ctrls[sel.ci] : null);
    if (pos){
      var fx = function(v){ return Math.round(v * 100) / 100; };
      sp.textContent = ui("sel_pos") + ": (" + fx(pos[0]) + ", " + fx(pos[1]) + ")";
      sp.style.display = "block";
    } else {
      sp.style.display = "none";
    }
  } else {
    sp.style.display = "none";
  }
}

function groups(){ return buildGroups(); }
// viewBox 应用与屏幕↔用户坐标换算 / viewBox apply + screen-to-user mapping
function applyView(){
  var vb = view.x + " " + view.y + " " + view.w + " " + view.h;
  stage.setAttribute("viewBox", vb);
  // 背景图层是独立的 <svg>，必须吃同一个 viewBox 才能跟编辑层同步缩放
  // / The background is a separate <svg>; give it the same viewBox so it zooms in lockstep
  if (bgwrap){
    var bg = bgwrap.querySelector("svg");
    if (bg) bg.setAttribute("viewBox", vb);
  }
}
function zoomFactor(){ return W / view.w; }   // 屏幕像素 / 用户单位（>1 为放大）/ screen px per user unit (>1 = zoomed in)
// 有 viewBox 后 getBoundingClientRect 的线性映射失效，必须走 CTM 矩阵
// （滚轮缩放 / 拖拽 / 取点全部经此换算，缩放状态下坐标自动正确）。
// / With a viewBox the linear getBoundingClientRect mapping breaks; the CTM
// matrix is the single source of truth, so zoomed-in picking stays exact.
function local(e){
  var m = stage.getScreenCTM().inverse();
  var pt = stage.createSVGPoint();
  pt.x = e.clientX; pt.y = e.clientY;
  var q = pt.matrixTransform(m);
  return [q.x, q.y];
}
// 滚轮缩放：以鼠标位置为不动点 / wheel zoom, cursor as the fixed point
stage.addEventListener("wheel", function(e){
  e.preventDefault();
  var p = local(e);
  var f = e.deltaY < 0 ? 1 / 1.2 : 1.2;
  var nw = Math.max(W / 40, Math.min(W * 2, view.w * f));   // 0.5x ~ 40x
  var k2 = nw / view.w;
  view.x = p[0] - (p[0] - view.x) * k2;
  view.y = p[1] - (p[1] - view.y) * k2;
  view.w = nw; view.h *= k2;
  applyView(); draw();
}, { passive: false });
// 中键平移 / middle-button pan
var pan = null;
stage.addEventListener("pointerdown", function(e){
  var t = e.target;
  // 中键按下 = 平移开始（优先于一切编辑交互）/ middle press starts panning
  if (e.button === 1){
    pan = { sx: e.clientX, sy: e.clientY, vx: view.x, vy: view.y };
    e.preventDefault();
    return;
  }
  // 取点模式：点画布记录坐标，拖拽/双击逻辑全部让位 / pick mode: record, everything else yields
  if (pickMode){
    var pp = local(e);
    var lastP = picks[picks.length - 1];
    if (!lastP || Math.abs(lastP.x - pp[0]) > 0.01 || Math.abs(lastP.y - pp[1]) > 0.01){
      picks.push({ x: pp[0], y: pp[1] });
      updatePickTip();
      draw();
    }
    e.preventDefault();
    return;
  }
  var now = Date.now();
  var onAnchor = !!(t.classList && t.classList.contains("pa"));
  var onPoint = !!(t.classList && (t.classList.contains("pa") ||
                                   t.classList.contains("ph")));
  // 手动识别双击：两次按下间隔 <400ms 且位移 <4px 就算。**不能依赖浏览器 dblclick**
  // —— 本处理器在按下时 draw() 重建 innerHTML，第一下按住的元素被摘出 DOM，
  // 按下/抬起落在不同节点上，浏览器不派发 click，dblclick 永远不触发。
  // / Detect double-click manually: two presses within 400ms and 4px. The browser
  // dblclick can NOT be used — draw() below rebuilds innerHTML on every press, the
  // pressed element leaves the DOM, so click/dblclick never fire at all.
  var isDbl = now - lastDownTime < 400 &&
      Math.abs(e.clientX - lastDownX) < 4 &&
      Math.abs(e.clientY - lastDownY) < 4;
  lastDownTime = now; lastDownX = e.clientX; lastDownY = e.clientY;
  // 双击锚点 = 删除（先确认）；双击空白/段线 = 中点加锚点 / dbl on anchor deletes, dbl elsewhere splits
  if (isDbl && onAnchor){ dblDelete(+t.dataset.i); return; }
  if (isDbl && !onPoint){ dblSplit(e); return; }
  if (t.classList.contains("pa")){ sel = { kind: "a", i: +t.dataset.i }; drag = sel; }
  else if (t.classList.contains("ph")){ sel = { kind: "c", si: +t.dataset.si, ci: +t.dataset.ci }; drag = sel; }
  else { sel = null; draw(); return; }
  var p = local(e), cur;
  if (drag.kind === "a") cur = anchorPos(groups().anchors[drag.i]);
  else cur = segs[drag.si].ctrls[drag.ci];
  drag.dx = p[0] - cur[0]; drag.dy = p[1] - cur[1];
  e.preventDefault(); draw();
});
function dblDelete(i){
  // 删除必须提醒使用者：confirm 是浏览器原生对话框，不参与 innerHTML 重建，
  // 不会被双击识别破坏。/ Deleting must warn the user: confirm() is a native
  // browser dialog, unaffected by the innerHTML rebuild.
  if (!confirm(ui("del_confirm"))) return;
  if (deleteAnchor(i)){ sel = null; draw(); }
  else notify(ui("no_delete"));
}
// 取点提示框：跟随最后一次点击，显示坐标与相邻两点差值 / pick tooltip follows the last click
function updatePickTip(){
  var tip = document.getElementById("pick-tip");
  if (!picks.length){ tip.style.display = "none"; return; }
  var q = picks[picks.length - 1];
  var txt = "x=" + num(q.x) + ", y=" + num(q.y);
  if (picks.length > 1){
    var pr = picks[picks.length - 2];
    var dx = q.x - pr.x, dy = q.y - pr.y;
    txt += "\ndx=" + num(dx) + ", dy=" + num(dy) +
           ", d=" + Math.round(Math.sqrt(dx * dx + dy * dy) * 100) / 100;
  }
  tip.textContent = txt;
  tip.style.display = "block";
  var r = stage.getBoundingClientRect(), box = stage.parentElement.getBoundingClientRect();
  var sc = r.width / view.w;
  var lx = (r.left - box.left) + q.x * sc, ty = (r.top - box.top) + q.y * sc;
  if (q.x > W - 90) lx -= 120; else lx += 12;   // 贴右往左弹 / flip near the right edge
  if (q.y > H - 50) ty -= 48; else ty += 12;    // 贴底往上弹 / flip near the bottom edge
  tip.style.left = lx + "px";
  tip.style.top = ty + "px";
}
// 拖平滑锚点一侧的调整杆时，另一侧的杆绕锚点镜像（各自保持原杆长）。
// / While dragging one handle of a smooth anchor, mirror the opposite handle
// around the anchor (each side keeps its own length).
function mirrorHandle(si, ci){
  var s = segs[si];
  var side = s.cmd === "C" ? (ci === 0 ? "start" : "end") : "start";
  var gs = groups().anchors;
  for (var gi = 0; gi < gs.length; gi++){
    var refs = gs[gi], hit = -1;
    for (var r = 0; r < refs.length; r++)
      if (refs[r][0] === side && refs[r][1] === si){ hit = r; break; }
    if (hit < 0) continue;
    if (!anchorSmooth(refs)) return;
    var A = anchorPos(refs), cur = segs[si].ctrls[ci];
    var vx = cur[0] - A[0], vy = cur[1] - A[1];
    var vl = Math.sqrt(vx * vx + vy * vy);
    if (vl < 1e-9) return;
    for (var r2 = 0; r2 < refs.length; r2++){
      if (r2 === hit) continue;
      var sj = segs[refs[r2][1]];
      if (!sj.ctrls || !sj.ctrls.length) continue;
      var ci2;
      if (sj.cmd === "C") ci2 = refs[r2][0] === "start" ? 0 : 1;
      else if (sj.cmd === "Q" && refs[r2][0] === "start") ci2 = 0;
      else continue;                       // Q 没有 end 侧调整杆 / quads have no end-side handle
      var oc = sj.ctrls[ci2];
      var od = Math.sqrt((oc[0] - A[0]) * (oc[0] - A[0]) +
                         (oc[1] - A[1]) * (oc[1] - A[1]));
      sj.ctrls[ci2] = [A[0] - vx / vl * od, A[1] - vy / vl * od];
    }
    return;
  }
}
function dblSplit(e){
  // 按点击坐标到各段采样点的最近距离找目标段（16px 容差），在中点拆分插入锚点。
  // 不能用 e.target 判定是否点中段线（见 pointerdown 里的注释）。
  // / Find the nearest segment by sampling its curve (16px tolerance) and split it
  // at the midpoint. Do NOT branch on e.target (see the pointerdown comment).
  var p = local(e), best = -1, bd = 1e9;
  for (var i = 0; i < segs.length; i++){
    var s = segs[i];
    if (!s.cmd || s.cmd === "M" || s.cmd === "Z" || s.cmd === "A") continue;
    var pts;
    if (s.cmd === "L"){
      // 直线段：把点击点投影到线段上取最近点 / Project the click onto the segment
      var ax = s.start[0], ay = s.start[1], bx = s.end[0], by = s.end[1];
      var vx = bx - ax, vy = by - ay;
      var tt = vx * (p[0] - ax) + vy * (p[1] - ay);
      tt = Math.max(0, Math.min(1, vx || vy ? tt / (vx * vx + vy * vy) : 0));
      pts = [[ax + vx * tt, ay + vy * tt]];
    } else {
      // 曲线段：按参数均匀采样（C 24 点 / Q 16 点）/ Sample the curve (C: 24, Q: 16)
      var n = s.cmd === "C" ? 24 : 16;
      pts = [];
      for (var k = 0; k <= n; k++){
        var t2 = k / n, u = 1 - t2, a = s.start, b = s.end, c = s.ctrls;
        if (s.cmd === "C"){
          pts.push([
            u*u*u*a[0] + 3*u*u*t2*c[0][0] + 3*u*t2*t2*c[1][0] + t2*t2*t2*b[0],
            u*u*u*a[1] + 3*u*u*t2*c[0][1] + 3*u*t2*t2*c[1][1] + t2*t2*t2*b[1]]);
        } else {
          pts.push([
            u*u*a[0] + 2*u*t2*c[0][0] + t2*t2*b[0],
            u*u*a[1] + 2*u*t2*c[0][1] + t2*t2*b[1]]);
        }
      }
    }
    for (var m = 0; m < pts.length; m++){
      var dx = pts[m][0] - p[0], dy = pts[m][1] - p[1];
      var dd = dx * dx + dy * dy;
      if (dd < bd){ bd = dd; best = i; }
    }
  }
  if (best < 0 || bd > 16 * 16) return;   // 离任何段都超过 16px：不算点中段线 / too far from every segment
  sel = null;
  if (splitSegment(best, 0.5)) draw();
}
window.addEventListener("pointermove", function(e){
  if (pan){
    var r = stage.getBoundingClientRect();
    var k = view.w / r.width;               // 用户单位 / 屏幕像素 / user units per screen px
    view.x = pan.vx - (e.clientX - pan.sx) * k;
    view.y = pan.vy - (e.clientY - pan.sy) * k;
    applyView(); draw();
    return;
  }
  if (!drag) return;
  var p = local(e), x = Math.max(-W, Math.min(W * 2, p[0] - drag.dx)),
      y = Math.max(-H, Math.min(H * 2, p[1] - drag.dy));
  if (drag.kind === "a") moveAnchor(groups().anchors[drag.i], x, y);
  else {
    segs[drag.si].ctrls[drag.ci] = [x, y];
    mirrorHandle(drag.si, drag.ci);   // 平滑锚点另一侧杆镜像 / mirror the twin handle
  }
  draw();
});
window.addEventListener("pointerup", function(){ drag = null; pan = null; });

window.addEventListener("keydown", function(e){
  if (!sel) return;
  var step = e.shiftKey ? 10 : 1, dx = 0, dy = 0;
  if (e.key === "ArrowLeft") dx = -step;
  else if (e.key === "ArrowRight") dx = step;
  else if (e.key === "ArrowUp") dy = -step;
  else if (e.key === "ArrowDown") dy = step;
  else return;
  e.preventDefault();
  if (sel.kind === "a"){
    var gp = groups().anchors[sel.i];
    moveAnchor(gp, anchorPos(gp)[0] + dx, anchorPos(gp)[1] + dy);
  } else {
    var c = segs[sel.si].ctrls[sel.ci];
    segs[sel.si].ctrls[sel.ci] = [c[0] + dx, c[1] + dy];
  }
  draw();
});

function exportJSON(){
  var out = [];
  for (var i = 0; i < segs.length; i++){
    var s = segs[i];
    if (!s.cmd) continue;
    out.push({
      cmd: s.cmd,
      start: [parseFloat(s.start[0]), parseFloat(s.start[1])],
      end: [parseFloat(s.end[0]), parseFloat(s.end[1])],
      ctrls: (s.ctrls || []).map(function(c){ return [parseFloat(c[0]), parseFloat(c[1])]; }),
      params: s.params ? s.params.slice() : null,
      sms: !!s.sms, sme: !!s.sme   // 平滑标记；Python 读回时忽略 / smooth flags; ignored by Python
    });
  }
  return { d: toD(), segments: out };
}
document.getElementById("b-json").onclick = function(){
  var blob = new Blob([JSON.stringify(exportJSON(), null, 2)],
                      { type: "application/json" });
  var a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "points.json";
  a.click();
  setTimeout(function(){ URL.revokeObjectURL(a.href); }, 4000);
};
document.getElementById("b-copy").onclick = function(){
  var b = this, text = document.getElementById("out-code").textContent + "\n";
  var done = function(ok){ b.textContent = ui(ok ? "copied" : "copy_fail");
    setTimeout(function(){ b.textContent = ui("copy"); }, 1400); };
  if (navigator.clipboard && navigator.clipboard.writeText)
    navigator.clipboard.writeText(text).then(function(){ done(true); }, function(){ done(false); });
  else done(false);
};
document.getElementById("b-handles").onclick = function(){
  showHandles = !showHandles;
  this.className = showHandles ? "on" : "";
  draw();
};
document.getElementById("c-link").onchange = function(){ linkHandles = this.checked; };
// 锚点类型按钮：转换选中锚点引出的段 / anchor type buttons: convert the outgoing segment
document.getElementById("b-l").onclick = function(){ convertSel("L"); };
document.getElementById("b-c").onclick = function(){ convertSel("C"); };
document.getElementById("b-q").onclick = function(){ convertSel("Q"); };
function convertSel(type){
  if (!sel || sel.kind !== "a") return;
  var si = segAt(groups().anchors[sel.i]);
  if (si < 0) return;
  if (segs[si].cmd === "A"){ notify(ui("arc_no_split")); return; }
  if (convertSegment(si, type)) draw();
}
document.getElementById("b-smooth").onclick = function(){
  if (!sel || sel.kind !== "a") return;
  var refs = groups().anchors[sel.i];
  setAnchorSmooth(refs, !anchorSmooth(refs));
  draw();
};
// 代码页签 / code flavour tabs
document.getElementById("b-setd").onclick = function(){ codeMode = "setd"; draw(); };
document.getElementById("b-chain").onclick = function(){ codeMode = "chain"; draw(); };
document.getElementById("b-picktab").onclick = function(){ codeMode = "pick"; draw(); };
// 背景图层 / background image layer
document.getElementById("b-bg").onclick = function(){
  var show = bgwrap.style.display !== "block";
  bgwrap.style.display = show ? "block" : "none";
  document.getElementById("bg-op").style.display = show ? "inline" : "none";
  this.className = show ? "on" : "";
};
document.getElementById("bg-op").oninput = function(){
  bgwrap.style.opacity = this.value / 100;
};
// 取点 / pick mode
document.getElementById("b-pick").onclick = function(){
  pickMode = !pickMode;
  this.className = pickMode ? "on" : "";
  if (!pickMode) document.getElementById("pick-tip").style.display = "none";
};
document.getElementById("b-clearpick").onclick = function(){
  picks = [];
  document.getElementById("pick-tip").style.display = "none";
  draw();
};
document.getElementById("b-reset").onclick = function(){
  var src = pathsData[curPath] ? pathsData[curPath].segments : DATA.segments;
  segs = JSON.parse(JSON.stringify(src));
  sel = null; draw();
};
// 「适应」= 回到整幅画布 / Fit = back to the whole canvas
document.getElementById("b-fit").onclick = function(){
  view = { x: 0, y: 0, w: W, h: H };
  applyView(); draw();
};
function setLang(code){
  LANG = code;
  document.documentElement.lang = code;
  document.getElementById("t-title").textContent = ui("title");
  document.getElementById("t-sub").textContent = ui("subtitle");
  document.getElementById("t-hint").textContent = ui("hint") + " · " + ui("zoom_hint");
  document.getElementById("t-seg").textContent = ui("segments");
  document.getElementById("t-anc").textContent = ui("anchors");
  document.getElementById("t-ctl").textContent = ui("controls");
  document.getElementById("t-d").textContent = ui("d_label");
  document.getElementById("t-code").textContent = ui("code_label");
  document.getElementById("t-json").textContent = ui("json_hint");
  document.getElementById("t-link").textContent = ui("link_handles");
  document.getElementById("t-atype").textContent = ui("anchor_type");
  document.getElementById("b-l").textContent = ui("to_line");
  document.getElementById("b-c").textContent = ui("to_cubic");
  document.getElementById("b-q").textContent = ui("to_quad");
  document.getElementById("b-setd").textContent = ui("code_setd");
  document.getElementById("b-chain").textContent = ui("code_chain");
  document.getElementById("b-picktab").textContent = ui("code_pick");
  document.getElementById("b-bg").textContent = ui("bg");
  document.getElementById("b-pick").textContent = ui("pick");
  document.getElementById("b-clearpick").textContent = ui("clear_pick");
  document.getElementById("t-paths").textContent = ui("select_path");
  document.getElementById("b-copy").textContent = ui("copy");
  document.getElementById("b-reset").textContent = ui("reset");
  document.getElementById("b-fit").textContent = ui("fit");
  document.getElementById("b-handles").textContent = ui("handles");
  document.getElementById("b-json").textContent = ui("json");
  document.getElementById("l-en").className = code === "en" ? "on" : "";
  document.getElementById("l-zh").className = code === "zh" ? "on" : "";
  draw();
}
document.getElementById("l-en").onclick = function(){ setLang("en"); };
document.getElementById("l-zh").onclick = function(){ setLang("zh"); };
applyView();          // 统一背景与编辑层的初始 viewBox / sync both layers' initial viewBox
setLang(LANG);
</script>
</body>
</html>
"""


# ===========================================================================
# 路径 UI 编辑器 / Path HTML editor
# ===========================================================================
class PathHTMLEditor:
    """
    把一条路径导出成可拖拽的单文件 HTML 编辑器。 / Export a path as a self-contained, draggable HTML editor.

    示例::

        ed = PathHTMLEditor(p)            # p 是 PathElement
        ed.save("edit.html")              # 双击生成的 HTML 就能拖点了
        print(ed.render()[:60])           # 只想拿字符串也可以
    """

    def __init__(self, path=None, d=None, points=None, width=None, height=None,
                 background="#ffffff", stroke_color="#e63946", stroke_width=3,
                 fill_color="none", grid=20, title=None, background_svg=None,
                 paths=None):
        """
        :param path: 要编辑的 PathElement（也可用 d= / points= 二选一）
        :param d: 直接给 d 字符串（如 ``"M20,200 C80,40 180,40 240,200"``）
        :param points: ``PathEditor.to_dict()`` 那种 ``{"segments": [...]}`` 结构
        :param width: 画布宽；缺省时取 path 所属绘图板的宽，再退化为 640
        :param height: 画布同上
        :param background: 画布底色（仅影响页面，不影响你导出的 SVG）
        :param stroke_color: 路径描边色（页面预览用，也让生成的代码好看一点）
        :param stroke_width: 路径线宽
        :param fill_color: 填充色，默认 ``"none"``
        :param grid: 网格间距（像素）；``0`` 关闭网格
        :param title: 页面标题；缺省用 i18n 的 ``html.title``
        :param background_svg: 背景 SVG 文本**或文件路径**（页面「背景」按钮
            控制显隐，透明度滑条可调；路径就叠在原图上拖，所见即所得）。
            配套便捷方法：`Malight.svg_editor`（自动内嵌已保存的 SVG）。

        三个数据源**按 d > points > path 的优先级**取第一个给了的；
        一个都不给会抛 ``ValueError``。
        """
        self.path = path
        self._d_given = d
        self._points = points
        self.width = int(width) if width else self._guess_size()[0]
        self.height = int(height) if height else self._guess_size()[1]
        self.background = background
        self.stroke_color = stroke_color
        self.stroke_width = stroke_width
        self.fill_color = fill_color
        self.grid = int(grid or 0)
        self.title = title
        self.background_svg = background_svg
        #: 多路径模式：[{"id","name","d","fill","stroke","strokeWidth"}, ...]
        self._paths = paths
        if path is None and d is None and points is None and paths is None:
            raise ValueError(t("err.html_no_source"))

    # ---------------------------------------------------------------
    # 取点位模型
    # ---------------------------------------------------------------
    def _guess_size(self):
        """从路径所属绘图板猜画布尺寸；猜不到就用 640x420（内部函数）。"""
        board = getattr(self.path, "board", None) if self.path is not None else None
        w = getattr(board, "width", None)
        h = getattr(board, "height", None)
        return (int(w) if w else 640, int(h) if h else 420)

    def segments(self) -> list:
        """
        当前的线段列表（每次调用重新解析，改过 path 的 d 之后能拿到新的）。 / Segment list, re-parsed on each call so edits to the path show up.

        多路径模式下返回**第一条**路径的段（页面里逐条加载走 ``DATA.paths``）。
        / In multi-path mode this returns the *first* path's segments; the page
        loads each path from DATA.paths instead.

        :return: [PathSegment, ...]
        """
        if self._paths:
            return parse_path_d(self._paths[0]["d"])
        if self._d_given is not None:
            return parse_path_d(self._d_given)
        if self._points is not None:
            return self._segments_from_points()
        return parse_path_d(self.path.get_d())

    def _segments_from_points(self):
        """把 PathEditor.to_dict() 的 segments 还原成 PathSegment（内部函数）。"""
        from .segment import PathSegment

        out = []
        for item in (self._points or {}).get("segments", []):
            out.append(PathSegment(item["cmd"], item["start"], item["end"],
                                   ctrls=item.get("ctrls") or (),
                                   params=tuple(item["params"])
                                   if item.get("params") else None))
        return out

    def _background_svg_text(self) -> str:
        """背景 SVG -> **内联**标记（内部函数）；没给背景返回空串。

        内联而不是 <img>：页面 JS 要能隐藏「当前正在编辑的那条路径」，
        img 里的 SVG 是封闭文档，改不了里面的节点。
        / Inline markup instead of <img>: the page must hide the path currently
        being edited inside the background, which is impossible inside an img.
        """
        if not self.background_svg:
            return ""
        src = self.background_svg
        if "<" not in src:
            # 不是 SVG 文本就当文件路径 / treat non-markup input as a file path
            with open(src, encoding="utf-8") as f:
                src = f.read()
        m = re.search(r"<svg[\s\S]*</svg>", src)
        if m:
            src = m.group(0)
        # 背景里不该再执行脚本 / never carry scripts into the editor page
        return re.sub(r"<script[\s\S]*?</script>", "", src)

    def _paths_payload(self, body) -> list:
        """构建 DATA.paths（内部函数）；单路径来源包成一项。"""
        if not self._paths:
            # id/name 必须用元素的真实 id——页面靠它隐藏背景里正在编辑的
            # 那条副本，编造 path0 会让背景多出一条重影。/ Use the element's
            # real id: the page hides the bg copy by id, a made-up one leaks.
            pid = "path0"
            if self.path is not None:
                pid = str(self.path.node.attribs.get("id") or "path0")
            return [{"id": pid, "name": pid, "d": body["d"],
                     "segments": body["segments"],
                     "fill": self.fill_color, "stroke": self.stroke_color,
                     "strokeWidth": self.stroke_width}]
        out = []
        for i, item in enumerate(self._paths):
            segs = parse_path_d(item["d"])
            out.append({
                "id": str(item.get("id") or "path%d" % (i + 1)),
                "name": str(item.get("name") or item.get("id")
                            or ("path%d" % (i + 1))),
                "d": item["d"],
                "segments": [{"cmd": s.cmd, "start": list(s.start),
                              "end": list(s.end),
                              "ctrls": [list(c) for c in s.ctrls],
                              "params": list(s.params) if s.params else None}
                             for s in segs],
                "fill": item.get("fill", self.fill_color),
                "stroke": item.get("stroke", self.stroke_color),
                "strokeWidth": item.get("strokeWidth", self.stroke_width),
            })
        return out

    def to_dict(self) -> dict:
        """
        转成可 JSON 序列化的数据（结构与 `PathEditor.to_dict()` 一致）。 / The same JSON-ready structure that PathEditor.to_dict returns.

        示例::

            PathHTMLEditor(p).to_dict()["segments"][-1]["end"]
        """
        segs = self.segments()
        return {"d": segments_to_d(segs),
                "segments": [{"cmd": s.cmd,
                              "start": list(s.start),
                              "end": list(s.end),
                              "ctrls": [list(c) for c in s.ctrls],
                              "params": list(s.params) if s.params else None}
                             for s in segs]}

    # ---------------------------------------------------------------
    # 渲染 / 落盘
    # ---------------------------------------------------------------
    def render(self) -> str:
        """
        生成完整的 HTML 文本（自我包含，可直接写盘或塞进任何地方）。 / Build the whole self-contained HTML page as a string.

        :return: HTML 源码

        示例::

            html = PathHTMLEditor(d="M0,0 L100,0").render()
        """
        segs = self.segments()
        body = {"d": segments_to_d(segs),
                "segments": [{"cmd": s.cmd,
                              "start": list(s.start),
                              "end": list(s.end),
                              "ctrls": [list(c) for c in s.ctrls],
                              "params": list(s.params) if s.params else None}
                             for s in segs]}
        data = {
            "w": self.width, "h": self.height, "grid": self.grid,
            "stroke": self.stroke_color, "strokeWidth": self.stroke_width,
            "fill": self.fill_color,
            "d": body["d"],
            "segments": body["segments"],
            "paths": self._paths_payload(body),
        }
        title = self.title or t("html.title")
        lang = "zh" if is_chinese() else "en"
        return (_PAGE
                .replace("@@BGSVG@@", self._background_svg_text())
                .replace("@@LANG@@", lang)
                .replace("@@TITLE@@", title)
                .replace("@@W@@", str(self.width))
                .replace("@@H@@", str(self.height))
                .replace("@@DATA@@", json.dumps(data, ensure_ascii=False))
                .replace("@@UI@@", json.dumps(_ui_messages(), ensure_ascii=False)))

    def save(self, file) -> str:
        """
        把页面写到磁盘，返回绝对路径。 / Write the page to disk and return its absolute path.

        :param file: 输出文件路径（建议以 .html 结尾）
        :return: 绝对路径

        示例::

            PathHTMLEditor(p).save("output/path_editor.html")
        """
        file = os.path.abspath(file)
        parent = os.path.dirname(file)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(file, "w", encoding="utf-8", newline="\n") as f:
            f.write(self.render())
        print(paint_path(t("html.saved", file=file), file))
        return file

    def __repr__(self):
        """调试用短描述。 / Short debug description."""
        return "<PathHTMLEditor {}x{} {}>".format(
            self.width, self.height, segments_to_d(self.segments())[:40])


# ===========================================================================
# 使用示例
# ===========================================================================
# 在 PyCharm 里点绿色三角直接运行本文件即可；也可命令行：
#     python -m malight.pathkit.htmleditor
# 本示例覆盖 PathHTMLEditor 的全部公开能力：
#     构造（path / d / points 三种来源）/ segments / to_dict / render / save / repr
#     以及链式代码生成函数 chain_code
# 生成的文件在 output/ 下，双击用浏览器打开即可拖点。
# ===========================================================================
if __name__ == "__main__":
    import os

    from malight import Malight, ColorName
    from malight.pathkit import PathEditor, PathHTMLEditor

    _out = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        "..", "..", "output"))
    os.makedirs(_out, exist_ok=True)

    # -----------------------------------------------------------------
    # 1) 造一条路径：起笔 + 直线 + 三次贝塞尔 + 二次贝塞尔 / 1) Build a path: move, line, cubic and quad curves
    # -----------------------------------------------------------------
    pen = Malight(os.path.join(_out, "demo_path_htmleditor"), width=660, height=430)
    pen.set_background_color(ColorName.WHITESMOKE)
    p = pen.path(fill_color="none", stroke_color=ColorName.DARKSLATEGRAY,
                 stroke_width=3)
    p.move_to(60, 320)
    p.line_to(150, 190)
    p.cubic_to((210, 80), (320, 80), (380, 190))
    p.quad_to((450, 280), (560, 210))

    # -----------------------------------------------------------------
    # 2) 从 PathElement 导出：画布尺寸默认跟随绘图板（660x430） / 2) Export from a PathElement; the canvas follows the board size (660x430)
    # -----------------------------------------------------------------
    ed = PathHTMLEditor(p)
    print("画布尺寸 : / canvas :", ed.width, "x", ed.height)
    print("段数     : / segments :", len(ed.segments()))
    print("d 串     : / d string :", ed.to_dict()["d"][:56], "...")

    # 3) 落盘：双击 output/path_editor.html 就能打开拖点 / 3) Save it: open the file in a browser and start dragging
    ed.save(os.path.join(_out, "path_editor.html"))

    # -----------------------------------------------------------------
    # 4) 只给 d 串也能用（不需要绘图板，适合处理别处拿来的路径） / 4) A bare d string works too, no board needed
    # -----------------------------------------------------------------
    bare = PathHTMLEditor(d="M40,160 C40,40 200,40 200,160 Z", width=260, height=220)
    bare.save(os.path.join(_out, "path_editor_from_d.html"))
    print("从 d 导出 : / from d :", bare)

    # -----------------------------------------------------------------
    # 5) 接着 PathEditor 的进度来：存档 -> 页面里拖 -> 下载 points.json 读回 / 5) Round-trip through JSON: save, drag in the browser, load back
    #    页面下载的 JSON 与 PathEditor.to_dict() 同一套结构，可直接 load_json / the downloaded JSON matches PathEditor.to_dict, ready for load_json
    # -----------------------------------------------------------------
    pe = PathEditor(p)
    pe.move_anchor(1, 160, 170)                    # 先在 Python 里挪一个锚点 / nudge an anchor in Python first
    from_points = PathHTMLEditor(points=pe.to_dict())
    print("点位来源  : / from points :", len(from_points.segments()), "段 / segments")
    print("两条来源  : / same d :", from_points.to_dict()["d"] == pe.to_d())
    from_points.save(os.path.join(_out, "path_editor_from_points.html"))

    # -----------------------------------------------------------------
    # 6) 链式代码：页面「链式」页签展示的就是这套格式 / 6) Chained code: the page's "chained" tab shows exactly this flavour
    #    与 JS 侧 chainCode() 互为镜像，Node 闸门逐字符比对 / mirrors the JS
    #    chainCode(); compared character by character in the Node gate
    # -----------------------------------------------------------------
    from malight.pathkit.htmleditor import chain_code

    print("链式代码  : / chain code :")
    print(chain_code(ed.segments(), ed.width, ed.height, ed.fill_color,
                     ed.stroke_color, ed.stroke_width))

    # -----------------------------------------------------------------
    # 7) 页面是自我包含的：没有 CDN、没有框架，离线双击即用 / 7) The page is self-contained: no CDN, no framework, works offline
    # -----------------------------------------------------------------
    html = ed.render()
    # 占位符左右各写一份 / write the placeholder on both halves
    # 只写中文半边的话，英文页会取到 "bytes".format(n)，数字被静默吞掉 / otherwise the English page gets "bytes".format(n) and silently loses the number
    _size = len(html.encode("utf-8"))
    print("页面体积  : / page size :", "{:,} 字节 / {:,} bytes".format(_size, _size))
    print("离线可用  : / offline :", "http://" not in html and "https://" not in html)

    # 第二条路径：页面下拉里就有两条可选 / a second path: the page dropdown lists both
    p2 = pen.path(fill_color="none", stroke_color=ColorName.STEELBLUE,
                  stroke_width=2)
    p2.move_to((80, 80)).line_to((220, 80)).line_to((150, 170)).close()

    pen.finish()

    # -----------------------------------------------------------------
    # 8) 一条命令生成编辑器专用 HTML / 8) One call -> the dedicated editor HTML:
    #    内嵌刚保存的 SVG 作背景，调路径 + 取点二合一 / embeds the saved SVG as
    #    background; path editing + point picking in one page
    #    不传 path 会收集画面上全部路径，页面下拉逐条编辑 / with no path arg the
    #    board's paths are collected and the page offers a selector
    # -----------------------------------------------------------------
    print("编辑器页面 : / editor page :", pen.svg_editor())
