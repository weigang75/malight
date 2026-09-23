# -*- coding: utf-8 -*-
"""
SMIL 动画合法性检查（check_smil）
=================================

背景：``animate_rotate(..., accelerate=True)`` 曾生成了**非法**的
``calcMode="spline"`` 组合 —— ``keySplines`` 写死两段，而两帧动画只允许一段。
浏览器遇到这种组合会把整段 ``<animateTransform>`` **直接丢弃**，
于是「地球不绕太阳公转」、旋转/缩放毫无反应，且**不报任何错**。

本工具把这些「静默失效」的写法钉在回归里：

    1. 用真实 API 生成覆盖全部动画方法的 SVG；
    2. 逐个数 ``<animateTransform>`` / ``<animateMotion>`` / ``<animate>``
       的属性，检查 SMIL 文档规定的硬约束：
        - ``calcMode="spline"`` ⇒ 必须有 ``keyTimes`` 与 ``keySplines``；
        - ``keySplines`` 段数 == 关键帧数 - 1；
        - ``keyTimes`` 个数 == 关键帧数，首 0 末 1；
        - ``values`` 不能有空段，``dur`` 必须为正；
    3. ``--self-test``：往合法 SVG 里注入若干典型错误，检测器**必须**全部报出
       —— 一个永远比不出来的检查器比没有更危险。

用法 / Usage::

    python tools/check_smil.py                 # 静态检查（快，CI 用）
    python tools/check_smil.py --render        # 追加 Chrome 真实渲染验证
    python tools/check_smil.py --self-test     # 注入错误，自检上面那项有效
"""

from __future__ import print_function

import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from malight import MagicPen                                    # noqa: E402

TMP = tempfile.gettempdir()

#: 所有走 _animate_transform 的公开方法，一条不落
CASES = (
    ("translate", lambda e: e.animate_translate(offset=(50, 0), dur=2, repeat_count="indefinite")),
    ("rotate", lambda e: e.animate_rotate(360, center=(200, 150), dur=3)),
    ("rotate-accel", lambda e: e.animate_rotate(360, center=(200, 150), dur=3, accelerate=True)),
    ("scale", lambda e: e.animate_scale(factor=(1.5, 1.5), dur=2, repeat_count=3)),
    ("skewX", lambda e: e.animate_skew_x(20, dur=2)),
    ("skewY", lambda e: e.animate_skew_y(20, dur=2)),
    ("motion", lambda e: e.animate_motion("M 40 40 L 300 200", dur=4)),
    ("opacity", lambda e: e.animate_opacity(1, 0, dur=2)),
)

_ATTR = re.compile(r'([\w:-]+)="([^"]*)"')
_ANIM_TAG = re.compile(r"<(animateTransform|animateMotion|animate)\b[^>]*>")


def _attrs(tag_text):
    return dict(_ATTR.findall(tag_text))


def scrape(svg_text):
    """取出所有动画节点：[(标签名, 属性 dict), ...]。"""
    return [(m.group(1), _attrs(m.group(0))) for m in _ANIM_TAG.finditer(svg_text)]


def check_nodes(nodes, where, bad):
    """对动画节点做 SMIL 合法性检查，问题追加到 bad。"""
    for tag, a in nodes:
        if tag == "animateTransform":
            if a.get("attributeName") != "transform":
                bad.append("%s: animateTransform 的 attributeName 必须是 transform" % where)
            if "type" not in a:
                bad.append("%s: animateTransform 缺少 type" % where)
            frames = [x for x in a.get("values", "").split(";") if x.strip()]
            if not frames:
                bad.append("%s: animateTransform 缺少 values" % where)
        elif tag == "animateMotion":
            if not a.get("path"):
                bad.append("%s: animateMotion 缺少 path" % where)
            frames = [x for x in a.get("values", "").split(";") if x.strip()] if a.get("values") else []
        else:                                            # <animate>
            if "attributeName" not in a:
                bad.append("%s: <animate> 缺少 attributeName" % where)
            frames = [x for x in a.get("values", "").split(";") if x.strip()]

        dur = a.get("dur", "")
        m = re.match(r"^([\d.]+)s?$", dur)
        if not m or float(m.group(1)) <= 0:
            bad.append("%s: dur 非法 %r" % (where, dur))

        cm = a.get("calcMode")
        ks, kt = a.get("keySplines"), a.get("keyTimes")
        n = len(frames)
        if cm == "spline":
            if not ks:
                bad.append("%s: calcMode=spline 但没有 keySplines（会被浏览器丢弃）" % where)
            if not kt:
                bad.append("%s: calcMode=spline 但没有 keyTimes（会被浏览器丢弃）" % where)
        if ks:
            segs = [x.strip() for x in ks.split(";") if x.strip()]
            if n and len(segs) != n - 1:
                bad.append("%s: keySplines %d 段 != 关键帧数-1(%d) —— 浏览器会丢弃整段动画"
                           % (where, len(segs), n - 1))
            for s in segs:
                nums = s.split()
                if len(nums) != 4:
                    bad.append("%s: keySplines 每段要 4 个数字，实际 %r" % (where, s))
                elif any(not (0.0 <= float(x) <= 1.0) for x in nums):
                    bad.append("%s: keySplines 数值须在 0~1，实际 %r" % (where, s))
        if kt:
            ts = [x.strip() for x in kt.split(";") if x.strip()]
            if n and len(ts) != n:
                bad.append("%s: keyTimes %d 个 != 关键帧数 %d（会被浏览器丢弃）" % (where, len(ts), n))
            if ts and (ts[0] != "0" or ts[-1] != "1"):
                bad.append("%s: keyTimes 首尾应为 0 与 1，实际 %r" % (where, kt))


def build_all(indir):
    """用真实 API 生成每个动画的 SVG，返回 [(名字, 路径, 文本)]。"""
    made = []
    for name, fn in CASES:
        path = os.path.join(indir, "smil_%s.svg" % name.replace("-", "_"))
        pen = MagicPen(path, width=400, height=300)
        el = pen.circle(200, 150, 40, fill_color="#3b82f6")
        fn(el)
        pen.finish()
        text = open(path, encoding="utf-8").read()
        made.append((name, path, text))
    return made


def scan(made):
    """扫描已生成的 SVG，返回问题列表。"""
    bad = []
    for name, _path, text in made:
        nodes = scrape(text)
        if not nodes:
            bad.append("%s: 没有生成任何动画节点" % name)
            continue
        check_nodes(nodes, name, bad)
        # 注：svg 里除了动画节点，base.py 还会写 <animate> 之类的其它节点，一并扫了
    return bad


# ---------------------------------------------------------------------------
# 真实渲染验证（--render）
# ---------------------------------------------------------------------------
_PNG_BLUE = (0x3b, 0x82, 0xf6)


def _centroid(png):
    import struct
    import zlib
    data = open(png, "rb").read()
    pos, idat, w, h, ct = 8, b"", None, None, None
    while pos < len(data):
        ln = struct.unpack(">I", data[pos:pos + 4])[0]
        typ = data[pos + 4:pos + 8]
        chunk = data[pos + 8:pos + 8 + ln]
        if typ == b"IHDR":
            w, h, _bd, ct = struct.unpack(">IIBB", chunk[:10])
        elif typ == b"IDAT":
            idat += chunk
        elif typ == b"IEND":
            break
        pos += 12 + ln
    raw = zlib.decompress(idat)
    bpp = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[ct]
    stride = w * bpp
    out, prev, i = bytearray(), bytearray(stride), 0
    for _y in range(h):
        f = raw[i]; i += 1
        line = bytearray(raw[i:i + stride]); i += stride
        if f == 1:
            for x in range(bpp, stride):
                line[x] = (line[x] + line[x - bpp]) & 255
        elif f == 2:
            for x in range(stride):
                line[x] = (line[x] + prev[x]) & 255
        elif f == 3:
            for x in range(stride):
                a = line[x - bpp] if x >= bpp else 0
                line[x] = (line[x] + ((a + prev[x]) >> 1)) & 255
        elif f == 4:
            for x in range(stride):
                a = line[x - bpp] if x >= bpp else 0
                b = prev[x]
                c = prev[x - bpp] if x >= bpp else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[x] = (line[x] + pr) & 255
        out += line
        prev = line
    sx = sy = n = 0
    for y in range(h):
        base = y * stride
        for x in range(w):
            o = base + x * bpp
            if (abs(out[o] - _PNG_BLUE[0]) < 40 and abs(out[o + 1] - _PNG_BLUE[1]) < 40
                    and abs(out[o + 2] - _PNG_BLUE[2]) < 40):
                sx += x; sy += y; n += 1
    return (sx / n, sy / n) if n else (None, None)


def _shoot(svg, png, chrome):
    subprocess.run([chrome, "--headless", "--disable-gpu", "--hide-scrollbars",
                    "--force-device-scale-factor=1", "--virtual-time-budget=1200",
                    "--screenshot=" + png, "file:///" + svg.replace("\\", "/")],
                   capture_output=True, timeout=120)
    return os.path.exists(png)


def render_check(indir):
    """用负 begin 把动画 reset 到指定相位，截图读地球质心，验证真的在转。

    负 ``begin`` 是关键技巧：页面在 t=0 就处于 3 秒相位，
    截图（t≈0）即可看到旋转结果，无需等待真实时间推进 ——
    ``--virtual-time-budget`` 与 ``setCurrentTime()`` 都不推进会 SMIL 时钟。
    """
    from malight.tools import find_chrome
    chrome = find_chrome()
    if not chrome:
        print("未找到 Chrome，跳过渲染验证（可设 MALIGHT_CHROME 指定路径）")
        return True

    head = ('<svg xmlns="http://www.w3.org/2000/svg" width="800" height="500" viewBox="0 0 800 500">'
            '<rect width="800" height="500" fill="#fff"/>'
            '<circle cx="400" cy="250" r="70" fill="#ffb300"/>'
            '<circle cx="400" cy="250" r="220" fill="none" stroke="#334455"/>')
    earth = '<circle cx="620" cy="250" r="22" fill="#3b82f6"/>'
    spline = ('calcMode="spline" keyTimes="0;1" keySplines="0.4 0 0.6 1"')

    def anim(extra):
        return ('<animateTransform attributeName="transform" type="rotate" '
                'values="0 400 250;360 400 250" dur="6s" begin="-3s" fill="freeze" %s/>' % extra)

    trials = (
        ("无动画基线(应停在起点)", earth, (620, 250)),
        ("普通旋转 begin=-3s(应转 180°)",
         '<circle cx="620" cy="250" r="22" fill="#3b82f6">' + anim("") + "</circle>", (180, 250)),
        ("加速旋转 begin=-3s(修复后应转 180°)",
         '<circle cx="620" cy="250" r="22" fill="#3b82f6">' + anim(spline) + "</circle>", (180, 250)),
        ("非法 keySplines(修复前的写法，应被丢弃=停在起点)",
         '<circle cx="620" cy="250" r="22" fill="#3b82f6">'
         + anim('calcMode="spline" keyTimes="0;1" keySplines="0.4 0 0.6 1; 0.4 0 0.6 1"')
         + "</circle>", (620, 250)),
    )
    ok_all = True
    for i, (label, body, expect) in enumerate(trials):
        svg = os.path.join(indir, "render_%d.svg" % i)
        png = os.path.join(indir, "render_%d.png" % i)
        open(svg, "w", encoding="utf-8").write(head + body + "</svg>")
        if not _shoot(svg, png, chrome):
            print("  [渲染] %-46s 截图失败" % label)
            ok_all = False
            continue
        cx, cy = _centroid(png)
        dist = None if cx is None else ((cx - expect[0]) ** 2 + (cy - expect[1]) ** 2) ** 0.5
        good = dist is not None and dist < 30
        ok_all = ok_all and good
        print("  [渲染] %-46s 质心=(%.1f, %.1f) 期望%s 距离 %s  %s"
              % (label, cx if cx else -1, cy if cy else -1, expect,
                 "%.1f" % dist if dist is not None else "-", "OK" if good else "FAIL"))
    return ok_all


# ---------------------------------------------------------------------------
# 自检：注入错误，检测器必须报出来
# ---------------------------------------------------------------------------
INJECTIONS = (
    ("keySplines 多一段（修复前的真 bug）",
     'keySplines="0.4 0 0.6 1"', 'keySplines="0.4 0 0.6 1; 0.4 0 0.6 1"'),
    ("keySplines 少一段",
     'keySplines="0.4 0 0.6 1"', 'keySplines=""'),
    ("keyTimes 个数不匹配",
     'keyTimes="0;1"', 'keyTimes="0;0.5;1"'),
    ("dur 为 0",
     'dur="3s"', 'dur="0s"'),
    ("keySplines 数值越界",
     'keySplines="0.4 0 0.6 1"', 'keySplines="1.4 0 0.6 1"'),
)


def self_test(indir):
    made = build_all(indir)
    base_bad = scan(made)
    if base_bad:
        print("自检前提不成立：合法 SVG 本身就被判为有问题：")
        for b in base_bad[:5]:
            print("   ", b)
        return False

    accel = [t for n, _p, t in made if n.endswith("accel")]
    ref = accel[0]
    missed = []
    for label, old, new in INJECTIONS:
        if old not in ref:
            missed.append("%s：注入锚点 %r 没找到" % (label, old))
            continue
        bad = scan([("injected", "", ref.replace(old, new, 1))])
        if not bad:
            missed.append("%s：注入后没被检出（检测器失效）" % label)
    if missed:
        print("自检失败：")
        for m in missed:
            print("   ", m)
        return False
    print("自检通过：%d 处注入错误全部被检出" % len(INJECTIONS))
    return True


# ---------------------------------------------------------------------------
def main(argv):
    with_render = "--render" in argv
    do_self = "--self-test" in argv
    indir = tempfile.mkdtemp(prefix="malight_smil_")
    try:
        made = build_all(indir)
        bad = scan(made)
        nodes = sum(len(scrape(t)) for _n, _p, t in made)
        print("SMIL 动画检查：%d 个动画方法，%d 个动画节点" % (len(made), nodes))

        if do_self:
            ok = self_test(indir)
            if not ok:
                return 1

        if bad:
            print("发现 %d 处问题（浏览器会静默丢弃这些动画）：" % len(bad))
            for b in bad[:20]:
                print("   ", b)
            return 1
        print("静态检查通过：calcMode / keyTimes / keySplines / dur 全部合法")

        if with_render:
            print("真实渲染验证（Chrome，负 begin 定相位）：")
            if not render_check(indir):
                return 1
        return 0
    finally:
        import shutil
        shutil.rmtree(indir, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
