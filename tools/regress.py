# -*- coding: utf-8 -*-
"""
全量回归（regress）
===================

一条命令跑完发布前的所有检查，替代散落的手工命令：

    1. 全部 .py 语法编译（malight / examples / tools）；
    2. 双语字符串的占位符与实参个数匹配（``"中文 %.2f / English %.2f" % v`` 这类
       漏参**只在跑到那一行才炸**，静态扫一遍才不会漏）；
    3. examples/ 下全部示例逐个运行（含子目录，如 board_games/ 棋类样例；
       在临时目录里跑，不污染 output/）；
    4. malight 下所有带 ``if __name__ == "__main__":`` 的模块逐个运行；
    5. examples/test_types.py（类型注解审计）、test_fx_smoke.py（滤镜冒烟）；
    6. 文档链路：gen_docs.py --check（模块双语文档与源码同步）、
       bilingualize_code.py --check（示例注释/文案是否都配了英文）、
       body_en.py（英文正文译文表指纹）、pypi_readme.py --check（PyPI 说明页）、
       gen_color_constants.py --check（Color 常量与 _COLOR_TABLE 同步）、
       英文页无中文、相对链接全部有效；
    7. i18n 自检：默认英文、切中文、环境变量、缺词兜底；
    8. SMIL 动画参数合法性（``check_smil.py``）：``calcMode="spline"`` 的
       ``keySplines`` 段数必须 == 关键帧数 - 1，否则浏览器**静默丢弃**整段动画。

用法 / Usage::

    python tools/regress.py             # 全量
    python tools/regress.py --fast      # 跳过耗时的导出类示例（无 Chrome 时用）
    python tools/regress.py --list      # 只列出将要运行的项目
"""

from __future__ import print_function

import ast
import io
import os
import re
import subprocess
import sys
import tempfile
import time
import warnings

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PY = sys.executable

#: 需要真实浏览器/外部程序的示例，--fast 时跳过
SLOW = {"demo_export.py"}

SKIP_MODULE_PARTS = ("__pycache__",)


# ---------------------------------------------------------------------------
# 执行器
# ---------------------------------------------------------------------------
class Report(object):
    def __init__(self):
        self.rows = []
        self.failed = []

    def add(self, kind, name, ok, detail="", seconds=0.0):
        self.rows.append((kind, name, ok, detail, seconds))
        if not ok:
            self.failed.append((name, detail))
        print("  %s %-42s %6.2fs %s" % ("PASS" if ok else "FAIL", name,
                                        seconds, detail if not ok else ""))
        sys.stdout.flush()

    def summary(self):
        kinds = {}
        for kind, _n, ok, _d, _s in self.rows:
            total, okc = kinds.get(kind, (0, 0))
            kinds[kind] = (total + 1, okc + (1 if ok else 0))
        print("\n" + "=" * 68)
        for kind in sorted(kinds):
            total, okc = kinds[kind]
            print("  %-14s %3d/%3d 通过" % (kind, okc, total))
        print("  %-14s %3d/%3d 通过" % ("合计", len(self.rows) - len(self.failed),
                                        len(self.rows)))
        if self.failed:
            print("\n失败项：")
            for name, detail in self.failed:
                print("  -", name)
                if detail:
                    for line in detail.strip().splitlines()[-6:]:
                        print("      ", line)
            return 1
        print("\n全部通过。")
        return 0


def run_py(args, cwd, env=None):
    """跑一个 Python 命令，返回 ``(ok, 输出尾部, 秒数)``。"""
    start = time.time()
    env2 = dict(os.environ)
    env2["PYTHONPATH"] = ROOT + os.pathsep + env2.get("PYTHONPATH", "")
    env2["PYTHONIOENCODING"] = "utf-8"
    if env:
        env2.update(env)
    r = subprocess.run([PY] + args, cwd=cwd, env=env2,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                       encoding="utf-8", errors="replace")
    tail = (r.stdout or "").strip()
    if len(tail) > 1600:
        tail = "…\n" + tail[-1600:]
    return r.returncode == 0, tail, time.time() - start


def rel(p):
    return os.path.relpath(p, ROOT).replace(os.sep, "/")


# ---------------------------------------------------------------------------
# 各项检查
# ---------------------------------------------------------------------------
def collect(targets):
    """收集要运行的脚本：examples/*.py（含子目录，如 board_games/）、tests、带 __main__ 的模块。"""
    demos, tests, modules = [], [], []
    ex_dir = os.path.join(ROOT, "examples")
    for root, dirs, names in os.walk(ex_dir):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for n in sorted(names):
            if not n.endswith(".py"):
                continue
            p = os.path.join(root, n)
            (tests if n.startswith("test_") else demos).append(p)
    for root, dirs, names in os.walk(os.path.join(ROOT, "malight")):
        dirs[:] = [d for d in dirs if d not in SKIP_MODULE_PARTS]
        for n in sorted(names):
            if not n.endswith(".py"):
                continue
            p = os.path.join(root, n)
            if 'if __name__ == "__main__":' in io.open(p, encoding="utf-8").read():
                modules.append(p)
    return demos, tests, modules


def check_compile(rep):
    """
    全部 .py 编译通过，且**不产生 SyntaxWarning**。

    SyntaxWarning 单独算失败：``re.compile(u"\\[")`` 这类非 raw 字符串里的无效转义
    只会警告、不会中断，编译得过、跑起来也对，但它是真的写错了 —— 我已经因为这个
    栽过一次（正则少了个 raw 前缀，行为飘了还看不出来）。
    """
    bad = []
    for sub in ("malight", "examples", "tools"):
        for root, dirs, names in os.walk(os.path.join(ROOT, sub)):
            dirs[:] = [d for d in dirs if d not in SKIP_MODULE_PARTS]
            for n in names:
                if n.endswith(".py"):
                    p = os.path.join(root, n)
                    try:
                        with warnings.catch_warnings():
                            warnings.simplefilter("error", SyntaxWarning)
                            compile(io.open(p, encoding="utf-8").read(), p, "exec")
                    except SyntaxWarning as e:
                        bad.append("%s: SyntaxWarning: %s" % (rel(p), e))
                    except SyntaxError as e:
                        bad.append("%s: %s" % (rel(p), e))
    rep.add("语法", "全部 .py 可编译（无 SyntaxWarning）", not bad, "\n".join(bad))


def check_eol(rep):
    """文本文件必须统一 LF —— 混合行尾会把 CRLF 混进生成的文档，也污染 diff。"""
    text_ext = (".py", ".pyi", ".md", ".txt", ".in", ".toml", ".cfg", ".json",
                ".csv", ".svg", ".html", ".yml", ".yaml")
    skip_dirs = {"__pycache__", "build", "dist", ".idea", "malight.egg-info",
                 "output"}
    bad = []
    for root, dirs, names in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for n in names:
            if not (n.endswith(text_ext) or n in ("LICENSE", ".gitignore",
                                                  ".gitattributes")):
                continue
            p = os.path.join(root, n)
            b = io.open(p, "rb").read()
            if b"\r" in b:
                bad.append("%s (CRLF x%d)" % (rel(p), b.count(b"\r")))
    rep.add("行尾", "文本文件统一 LF", not bad, "\n".join(bad[:12]))


def check_script(rep, kind, path, tmp, env=None):
    ok, out, sec = run_py([path], tmp, env)
    rep.add(kind, rel(path), ok, out, sec)


#: ``%s`` / ``%.2f`` / ``%d`` …（``%%`` 是转义，单独排除）
FMT = re.compile(r"%[-#0-9. +]*[sdfrxeg]")


def check_placeholders(rep):
    """
    双语字符串的占位符必须和参数个数对得上。

    这条是踩出来的：把中文文案配成 ``"中文 %.2f / English %.2f"`` 之后，同一个
    占位符在字符串里出现了**两次**（中英各一次），而调用处往往还是原来的
    ``% value`` —— 语法能编译、`--check` 也看不出来，只有真跑到那一行才
    ``TypeError: not enough arguments for format string``。

    而 ``regress.py`` 里"模块示例"那一项**只在 `elif` 分支才会执行到**这类
    print，所以光靠跑示例会漏。用 AST 静态扫一遍，把这一整类问题一次锁死：
    凡左操作数是**字符串字面量**、且含 `` / ``（双语）的 ``%`` / ``.format``，
    逐个核对占位符数量与实参数量。f-string 天然安全，跳过。

    另外核对**左右两半的占位符是否一样多**：``"{:,} 字节 / bytes".format(n)``
    切开之后英文半边是 ``"bytes".format(n)`` —— 语法合法、不报错，只是把数字
    静默吞了；中文半边却完全正常，所以光跑示例发现不了。这条只对 ``malight/``
    生效：只有 ``malight/`` 的源码会进文档（见 ``gen_docs.gather_modules``），
    ``tools/`` 里带 `` / `` 的字符串是打印消息与 ``%`` 模板，不是双语示例。
    """
    import ast

    if HERE not in sys.path:
        sys.path.insert(0, HERE)
    import bipair

    def asymmetry(path, node, s):
        """双语字面量左右占位符数量不一致时返回说明，否则 None。"""
        pair = bipair.split_pair(s.value)
        if pair is None:
            return None
        n_zh = len(FMT.findall(pair[0].replace("%%", ""))) \
            + len(re.findall(r"\{[^{}]*\}", pair[0]))
        n_en = len(FMT.findall(pair[1].replace("%%", ""))) \
            + len(re.findall(r"\{[^{}]*\}", pair[1]))
        if n_zh == n_en:
            return None
        return ("%s:%d  双语占位符左右不对称（zh=%d / en=%d）| %s"
                % (rel(p), node.lineno, n_zh, n_en, s.value.strip()[:60]))

    bad = []
    for sub in ("malight", "examples", "tools"):
        for root, dirs, names in os.walk(os.path.join(ROOT, sub)):
            dirs[:] = [d for d in dirs if d not in SKIP_MODULE_PARTS]
            for n in sorted(names):
                if not n.endswith(".py"):
                    continue
                p = os.path.join(root, n)
                try:
                    tree = ast.parse(io.open(p, encoding="utf-8").read(), p)
                except SyntaxError:
                    continue                     # 交给「语法」那一项去报
                doc_src = sub == "malight"       # 只有它会进文档
                for node in ast.walk(tree):
                    # --- % 格式化 ---
                    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod):
                        s = node.left
                        if not (isinstance(s, ast.Constant)
                                and isinstance(s.value, str)
                                and " / " in s.value):
                            continue
                        want = len(FMT.findall(s.value.replace("%%", "")))
                        got = (len(node.right.elts)
                               if isinstance(node.right, ast.Tuple) else 1)
                        if want != got:
                            bad.append("%s:%d  %% 占位符 %d 个 / 实参 %d 个  | %s"
                                       % (rel(p), node.lineno, want, got,
                                          s.value.strip()[:66]))
                        if doc_src:
                            msg = asymmetry(p, node, s)
                            if msg:
                                bad.append(msg)
                    # --- str.format() 自动编号 ---
                    if (isinstance(node, ast.Call)
                            and isinstance(node.func, ast.Attribute)
                            and node.func.attr == "format"):
                        s = node.func.value
                        if not (isinstance(s, ast.Constant)
                                and isinstance(s.value, str)
                                and " / " in s.value):
                            continue
                        slots = re.findall(r"\{(\d*)[^}]*\}", s.value)
                        explicit = any(sl for sl in slots)
                        if not explicit and slots and len(slots) != len(node.args) \
                                and not any(k.arg is None for k in node.keywords):
                            bad.append("%s:%d  {} 占位符 %d 个 / format 实参 %d 个  | %s"
                                       % (rel(p), node.lineno, len(slots),
                                          len(node.args), s.value.strip()[:66]))
                        if doc_src:
                            msg = asymmetry(p, node, s)
                            if msg:
                                bad.append(msg)
    rep.add("占位符", "双语字符串占位符与实参匹配、左右对称", not bad,
            "\n".join(bad[:10]))


def check_i18n_shadow(rep):
    """
    不许用名为 ``t`` 的形参 / 局部变量遮蔽 ``from ..i18n import t``。

    这条是踩出来的：``PathSegment.split(self, t=0.5)`` 里 ``t`` 既是拆分位置
    （浮点）又是 i18n 的取词函数，函数体里那句
    ``raise NotImplementedError(t("err.arc_split"))`` 于是拿浮点当函数调 ——
    本该抛 ``NotImplementedError``（圆弧不支持拆分），实际抛的是
    ``TypeError: 'float' object is not callable``，调用方写着
    ``except NotImplementedError`` 就永远接不住。

    形参名叫 ``t`` 本身没错（``split(t=0.5)`` 是公开签名），错的是**在同一个
    函数体里还要调 ``t(...)``**。所以这里只查这一种组合：本函数作用域里绑定了
    ``t``，且本函数自己的代码里出现了 ``t(...)`` 调用。要发消息就绕一层
    模块级小函数（见 ``segment._arc_split_msg``）。

    只扫 ``malight/``：``tools/`` 里不引用 i18n，扫了纯属噪声。
    """
    import ast

    def collect(fn):
        """返回 (被绑定为 t 的行号列表, 调用 t(...) 的行号列表)。

        两级都用**剪枝遍历**：不进嵌套函数 / lambda / 推导式的作用域，
        否则子作用域里自己的 ``t`` 会造成误报。
        """
        bound, called = [], []

        def targets(node):
            if isinstance(node, ast.Name):
                if node.id == "t":
                    bound.append(getattr(node, "lineno", 0))
            elif isinstance(node, (ast.Tuple, ast.List)):
                for e in node.elts:
                    targets(e)

        def walk(node):
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef,
                                      ast.Lambda, ast.ListComp, ast.SetComp,
                                      ast.DictComp, ast.GeneratorExp)):
                    continue                      # 子作用域，另算
                if isinstance(child, ast.Call):
                    f = child.func
                    if isinstance(f, ast.Name) and f.id == "t":
                        called.append(child.lineno)
                if isinstance(child, (ast.Assign, ast.AnnAssign, ast.AugAssign,
                                      ast.NamedExpr)):
                    for tg in (getattr(child, "targets", None)
                               or [getattr(child, "target", None)]):
                        if tg is not None:
                            targets(tg)
                elif isinstance(child, (ast.For, ast.AsyncFor)):
                    targets(child.target)
                elif isinstance(child, ast.comprehension):
                    targets(child.target)
                elif isinstance(child, ast.withitem) and child.optional_vars:
                    targets(child.optional_vars)
                walk(child)

        a = fn.args
        for arg in (list(getattr(a, "posonlyargs", [])) + list(a.args)
                    + list(a.kwonlyargs)):
            if arg.arg == "t":
                bound.append(arg.lineno)
        if a.vararg and a.vararg.arg == "t":
            bound.append(a.vararg.lineno)
        if a.kwarg and a.kwarg.arg == "t":
            bound.append(a.kwarg.lineno)
        walk(fn)
        return bound, called

    bad = []
    for root, dirs, names in os.walk(os.path.join(ROOT, "malight")):
        dirs[:] = [d for d in dirs if d not in SKIP_MODULE_PARTS]
        for n in sorted(names):
            if not n.endswith(".py"):
                continue
            p = os.path.join(root, n)
            try:
                tree = ast.parse(io.open(p, encoding="utf-8").read(), p)
            except SyntaxError:
                continue                          # 交给「语法」那一项去报
            for node in ast.walk(tree):
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                bound, called = collect(node)
                if bound and called:
                    bad.append("%s:%d  %s() 里 %s 绑定了 t，又调了 t(...)（第 %s 行）"
                               % (rel(p), node.lineno, node.name,
                                  "形参" if bound else "局部变量",
                                  ", ".join(str(c) for c in called)))
    rep.add("遮蔽", "没有用 t 遮蔽 i18n 取词函数的函数", not bad, "\n".join(bad[:10]))


def check_htmleditor(rep):
    """
    页面里的 JS 点位模型必须与 Python 侧算出一样的 d 串。

    页面自带一套 JS 实现（拖锚点 / 拆段 / 输出 d），Python 侧是另一套。
    两份实现漂移时**不会报错**，只会安静地给出错的坐标，所以必须逐项比对。
    检查脚本自己也有 ``--self-test``：注入 8 处真实错法，确认比对项仍然有效
    （写这些用例时踩过两次"以为在测、其实没走到那条分支"的坑）。

    没装 Node 的机器上检查脚本会打印 SKIP 并返回 0，回归照过。
    """
    tool = os.path.join(HERE, "check_htmleditor_js.py")
    ok, tail, sec = run_py([tool], ROOT)
    if not ok:
        rep.add("网页编辑器", "页面 JS 与 Python 点位模型一致", False, tail, sec)
        return
    # 顺带跑一次自检：确认比对项不是"永远为空所以永远通过"
    ok2, tail2, sec2 = run_py([tool, "--self-test"], ROOT)
    rep.add("网页编辑器", "页面 JS 与 Python 点位模型一致", ok2,
            tail2 if not ok2 else "", sec + sec2)


def check_smil_anim(rep):
    """
    SMIL 动画的关键帧/缓动参数必须合法，否则浏览器**静默丢弃整段动画**。

    这条是真 bug 换来的：``animate_rotate(..., accelerate=True)`` 早先给两帧动画
    写了**两段** ``keySplines``（spline 要求段数 = 关键帧数 - 1），于是整段
    ``<animateTransform>`` 被判非法丢弃 —— 用户看到的现象是"地球不绕太阳公转"，
    控制台一句报错都没有。检查器自己带 ``--self-test``（注入 5 处错法）。

    默认只做静态检查（快）；``--render`` 会用 Chrome 负 ``begin`` 定相位截图，
    验证动画真的在转（含"非法写法确实被丢弃"的反证），供人工深查。
    """
    tool = os.path.join(HERE, "check_smil.py")
    ok, tail, sec = run_py([tool], ROOT)
    if not ok:
        rep.add("动画", "SMIL 关键帧/缓动参数合法", False, tail, sec)
        return
    ok2, tail2, sec2 = run_py([tool, "--self-test"], ROOT)
    rep.add("动画", "SMIL 关键帧/缓动参数合法（含自证）", ok2,
            tail2 if not ok2 else "", sec + sec2)


def check_bilingual_split(rep):
    """
    双语对拆分必须 ``cn`` / ``zh`` / ``en`` 三种语言码都取对半边。

    这条是踩出来的：``gen_docs.py`` 内部按 ``"cn"`` / ``"en"`` 分派页面，
    而 ``bipair.pick()`` 原来只认 ``"zh"`` —— 传 ``"cn"`` 直接掉进 else 分支，
    于是**每一页 ``.zh.md`` 的示例代码都渲染成了英文**：注释被换成英文半边，
    ``print("画布尺寸 : / canvas :", ...)`` 也只剩 ``canvas``。而正文仍是中文，
    所以扫 CJK 的英文纯净度检查一点都看不出来，中文页就这样安静地烂了很久。

    这里直接拿 ``bipair`` 试三种语言码，比去比对生成结果更早、更准。
    """
    if HERE not in sys.path:
        sys.path.insert(0, HERE)
    import bipair

    sample = 'print("画布尺寸 : / canvas :")   # 造一条路径 / build a path'
    bad = []
    for lang in ("cn", "zh", "zh-TW"):
        out = bipair.trim_line(sample, lang)
        if "画布尺寸" not in out or "造一条路径" not in out:
            bad.append("lang=%r 没取到中文半边 -> %s" % (lang, out))
    out_en = bipair.trim_line(sample, "en")
    if "canvas" not in out_en or "build a path" not in out_en:
        bad.append("lang='en' 没取到英文半边 -> %s" % out_en)
    # 不是双语对的代码必须原样通过，别把普通斜杠当分隔符
    plain = 'print("段号 0(M) / 1(L) / 2(C)")'
    if bipair.trim_block(plain, "en") != plain:
        bad.append("非双语对被误切 -> %s" % bipair.trim_block(plain, "en"))
    rep.add("双语对", "cn / zh / en 三种语言码都取对半边", not bad,
            "\n".join(bad))


def _class_methods(path, cls_name):
    """AST 提取某个文件里某个类的全部方法名（内部辅助）。"""
    tree = ast.parse(io.open(path, encoding="utf-8").read(), path)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == cls_name:
            return {n.name for n in node.body
                    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    return set()


def check_fx_api(rep):
    """
    ``pen.fx`` 的效果与 ``Element.fx_*`` 快捷方法必须一一对应。

    滤镜有三层 API：``FilterChain``（效果本体，fx.py）、``FilterAPI``
    （工厂转发，filters.py）、``Element.fx_<效果>``（元素侧快捷方式，
    elements/base.py）。三层都是手写清单，漏一处就是「效果存在却调不到」，
    而且不报错 —— 只能静态对齐。比对全部双向：

    1. FilterChain 的效果 ⇄ FilterAPI 的转发（``drop_shadow`` 是 ``shadow``
       的别名转发，单独登记）；
    2. FilterAPI 的效果 ⇄ ``Element.fx_*``（``fx_chain`` 不是效果快捷方式，
       是取回当前链的入口，不参与比对）；
    3. ``Element.fx_*`` 里不允许出现 pen.fx 上没有的效果。
    """
    fx_file = os.path.join(ROOT, "malight", "board", "fx.py")
    api_file = os.path.join(ROOT, "malight", "board", "filters.py")
    el_file = os.path.join(ROOT, "malight", "elements", "base.py")
    alias = {"drop_shadow": "shadow"}      # 别名转发：FilterAPI 名 -> FilterChain 名
    chain_fx = {n for n in _class_methods(fx_file, "FilterChain")
                if not n.startswith("_")} - {"url", "apply", "clone",
                                             "merge_from", "dispose", "custom"}
    api_fx = {n for n in _class_methods(api_file, "FilterAPI")
              if not n.startswith("_")} - {"chain"}
    el_fx = {n for n in _class_methods(el_file, "Element")
             if n.startswith("fx_")} - {"fx_chain"}
    el_names = {n[3:] for n in el_fx}
    chain_view = {alias.get(n, n) for n in api_fx}
    bad = []
    for n in sorted(chain_fx - chain_view):
        bad.append("FilterChain.%s() 没有转发到 FilterAPI（pen.fx 上调不到）" % n)
    for n in sorted(chain_view - chain_fx):
        bad.append("FilterAPI.%s() 在 FilterChain 上没有对应效果" % n)
    for n in sorted(api_fx - el_names):
        bad.append("缺 Element.fx_%s()：pen.fx.%s 没有元素侧快捷方式" % (n, n))
    for n in sorted(el_names - api_fx):
        bad.append("Element.fx_%s() 在 pen.fx 上没有对应效果" % n)
    rep.add("滤镜", "pen.fx 与 Element.fx_* 一一对应", not bad, "\n".join(bad[:10]))


def check_fx_chain(rep, tmp):
    """
    滤镜链不许出现「悬空 result」：算了却没人引用，等于这一层效果被静默丢掉。

    这是「滤镜后面覆盖了前面」的机器可判定症状，踩过两次：
    ``_merge_over_source()`` 的底图写死 ``SourceGraphic``（同一条链上叠两个
    带合成的效果，前一个整段消失）；``_retarget()`` 不递归到子节点
    （``feMergeNode`` 的 ``in`` 还指着旧名，跨链合并后 glow 连自己的合成层
    都找不着）。两处都不报错、XML 也合法，只是画面悄悄少了东西 —— 所以：

    1. 从 ``FilterChain`` 上取全部效果名，逐个跑三种叠加路径
       （单独用 / 接在 shadow 之后 / 接在 shadow 之前），再加上元素侧
       ``el.fx_shadow().fx_<效果>()`` 的跨链合并路径；
    2. 自检：人为把合成底图掰回 ``SourceGraphic``（老 bug 的写法），
       检测器必须报出来 —— 一个永远比不出来的检查器比没有更危险。
    """
    src = '''
import malight
from malight import Malight

BORROW = ("SourceGraphic", "SourceAlpha", "BackgroundImage",
          "FillPaint", "StrokePaint")
SKIP = ("url", "apply", "clone", "merge_from", "dispose", "custom")


def dangling(chain):
    """链上「算了却没人用」的 result 名（最后一个原语的 result 就是输出，不算）。"""
    ch = list(chain.node.children)
    names = [c.attribs.get("result") for c in ch if c.attribs.get("result")]
    used = set()
    for c in ch:
        for key in ("in", "in2", "in3"):
            v = c.attribs.get(key)
            if v:
                used.add(v)
        for sub in c.children:
            v = sub.attribs.get("in")
            if v:
                used.add(v)
    used -= set(BORROW)
    return [n for n in names[:-1] if n not in used]


pen = Malight("fx_chain_probe", width=600, height=400)
proto = pen.fx.chain()
names = sorted(n for n in dir(proto)
               if callable(getattr(proto, n)) and not n.startswith("_")
               and n not in SKIP)
bad = []
for n in names:
    c1 = pen.fx.chain()
    getattr(c1, n)()
    d = dangling(c1)
    if d:
        bad.append("%s() 单独用就断链：%s" % (n, d))
    c2 = pen.fx.chain()
    getattr(c2, n)()
    c2.shadow(4, 4, 3)
    d = dangling(c2)
    if d:
        bad.append("shadow() 叠在 %s() 之后被顶掉：%s" % (n, d))
    c3 = pen.fx.chain()
    c3.shadow(4, 4, 3)
    getattr(c3, n)()
    d = dangling(c3)
    if d:
        bad.append("%s() 叠在 shadow() 之后把前面的顶掉：%s" % (n, d))
    el = pen.rect(20, 20, 60, 40, fill_color="#4e79a7")
    el.fx_shadow(4, 4, 3)
    getattr(el, "fx_" + n)()
    d = dangling(el._current_filter_chain())
    if d:
        bad.append("el.fx_shadow().fx_%s() 跨链合并后断链：%s" % (n, d))

# 自检：把最后一次合成的底图掰回 SourceGraphic（老 bug 的写法，效果层全断）
probe = pen.fx.chain()
probe.inner_shadow(2, 2, 1, "#000000", 0.8)
probe.inner_shadow(-2, -2, 1, "#ffffff", 0.9)
last_merge = [c for c in probe.node.children if c.tag == "feMerge"][-1]
for sub in last_merge.children:
    sub.attribs["in"] = "SourceGraphic"
if not dangling(probe):
    bad.append("检测器失效：人为断开的链（老 bug 写法）没被检出")

if bad:
    print("\\n".join(bad[:10]))
    raise SystemExit(1)
print("滤镜链不断链：%d 个效果 x 4 条叠加路径全部通过" % len(names))
'''
    ok, out, sec = run_py(["-c", src], tmp)
    rep.add("滤镜", "效果叠加后链上无悬空 result", ok, out, sec)


def check_element_attrs(rep):
    """
    创建元素时传的样式参数必须真的写进 SVG（`tools/check_element_attrs.py`）。

    这条是用户报出来的：``pen.path(stroke_color=..., opacity=0.5,
    stroke_join=...)`` 里 ``opacity`` 没生效 —— ``PathElement`` 当时没走
    ``_update_attrs`` 属性管线，``opacity`` / ``fill_opacity`` /
    ``blend_mode`` / ``class_name`` 等一批公共样式参数被静默丢弃，
    ``pen.symbol(opacity=...)`` / ``pen.mask(opacity=...)`` 更是直接
    ``TypeError``。静默丢参在 IDE 里毫无提示，只能逐个入口实测。

    检查器遍历 33 个板级绘图入口，逐个传标准样式参数并核对节点属性。
    """
    tool = os.path.join(HERE, "check_element_attrs.py")
    ok, tail, sec = run_py([tool, "--quiet"], ROOT)
    rep.add("元素", "创建时的样式参数全部落到 SVG（33 个入口）", ok, tail, sec)


def check_clone_isolation(rep, tmp):
    """
    克隆出来的元素必须和原元素互不干扰（内部状态不能被共用）。

    这条也是「静默错效」家族的：``Element.clone`` 走的是浅拷贝，
    ``PathElement._cmds`` 这类列表会被两条路径共用 —— 克隆之后往任一条上
    继续画（``line_to`` 等），另一条的 ``d`` 会跟着改变，而界面上一点报错
    都没有。修法是 ``_copy_mutable_state``：子类把可变状态各复制一份。
    """
    src = '''
from malight import Malight

pen = Malight("_clone_iso", width=400, height=300)

# 路径：克隆后各自继续画，d 不能互相污染
a = pen.path(stroke_color="red", opacity=0.5)
a.move_to(0, 0); a.line_to(10, 10)
b = pen.copy(a)
b.line_to(50, 50)
a.line_to(90, 90)
assert a.node.attribs["d"] == "M0,0 L10,10 L90,90", a.node.attribs["d"]
assert b.node.attribs["d"] == "M0,0 L10,10 L50,50", b.node.attribs["d"]
assert a._cmds is not b._cmds, "克隆体与原路径共用命令列表"

# 克隆体的属性改动不能影响原元素（节点对象独立）
c = pen.circle(50, 50, 20, fill_color="navy", opacity=0.4)
navy = c.node.attribs["fill"]
d = c.clone()
d.update(fill_color="red", opacity=0.9)
assert c.node.attribs["fill"] == navy, c.node.attribs["fill"]
assert c.node.attribs["opacity"] == 0.4, c.node.attribs["opacity"]
assert d.node.attribs["opacity"] == 0.9, d.node.attribs["opacity"]
assert d.node is not c.node, "克隆体和原元素共用同一个节点"
print("克隆隔离通过：path 命令列表 / 元素属性均独立")
'''
    ok, out, sec = run_py(["-c", src], tmp)
    rep.add("元素", "克隆体与原元素内部状态互不共用", ok, out, sec)


def check_chain_typing(rep):
    """
    链式方法的返回类型必须是**具体元素类**（`tools/check_chain_typing.py`）。

    这条是用户报出来的：`pen.path(...).move_to(...).` 在 PyCharm 里点出来的
    全是 Element 的方法 —— 标注只写 `-> _Self`（模块级 TypeVar，bound=Element）
    时，PyCharm 只按上界推导，子类自己的方法一个都补不到。

    固化下来的三条硬规则：基类 `Element(Generic[_Self])` + `-> _Self` 的方法
    写 `self: _Self`；子类声明 `Element["XElement"]`；子类自己 `return self`
    的方法返回标注必须是本类名。用 ``--no-mypy`` 只做静态检查（依赖无关），
    人工可去掉该参数让 mypy 实测一遍 reveal_type。
    """
    tool = os.path.join(HERE, "check_chain_typing.py")
    ok, tail, sec = run_py([tool, "--no-mypy"], ROOT)
    rep.add("元素", "链式方法返回具体元素类（19 子类 + 基类泛型）", ok, tail, sec)


def check_attr_accessors(rep):
    """
    元素参数访问器必须**是真实方法**（`tools/gen_attr_accessors.py`）。

    用户报的「PyCharm 无法识别」有两处：`Color.BLACK` 那批常量是一处，元素参数
    访问器是第二处 —— `circle.set_radius(` / `t.set_font_size(` 原来是
    `Element.__getattr__` 按 `_attr_params` 动态合成的，IDE 补不出来，而文档
    恰恰在推荐这种链式写法（`t.set_font_size(36).set_fill_color("teal")`）。

    17 个元素类共 144 个访问器已展开成类体内的显式方法。这条检查做两件事：
    生成块与 `_update_attrs` 同步（静态），以及运行时**名字真的在某个类的
    ``__dict__`` 里** —— 后者防的是名字写错、缩进串了类，静态比对却放过。
    """
    tool = os.path.join(HERE, "gen_attr_accessors.py")
    ok, tail, sec = run_py([tool, "--check"], ROOT)
    rep.add("元素", "参数访问器是真实方法（144 个，IDE 可见）", ok, tail, sec)


def check_svg_text_edit(rep, tmp):
    """
    SVG 图元素能直接改**自己那份文本**（`pen.svg_image` + 换色方法）。

    这条是用户要的：``circle_pattern = pen.image("xx.svg", ...)`` 只是把 SVG
    当图片贴上去，文本锁在 base64 里改不了；同一个文件想要几种配色，就得复制
    几个文件。`svg_image()` 把源文本读进元素缓存，`replace_text` /
    `replace_color` 改的都是这一份，改完自动重新内嵌。

    端到端跑一遍：4 种白色写法（``#ffffff`` / ``white`` / ``rgba(...)`` /
    ``#FFF``）一次全换掉，而 ``id="orange"`` 这种同名标识与 ``<text>white</text>``
    正文不动；换色后再 ``update(width=...)``（局部更新）不能把文本冲回原样；
    同一个文件贴两次各改各的、互不影响；旧名 ``paste_svg`` 仍返回同一类。

    **换色只挂在这一条通道上**，因为它自带一份文本。导入成组 / 模板拿到的是
    节点树（`pen.import_svg_as_group` → `SvgGroupElement`），对象上**没有**
    换色方法，改色走 tools 函数 ``replace_svg_node_color(元素.node, ...)``；
    `SvgNode` 本身也只剩树操作（walk / to_xml / add / set / find），不再有
    replace_color —— 用户指出「Group 硬上换色方法」正是这个设计问题：颜色是
    图形的属性，不是「组」这个容器的性质。

    导入通道要验的是「它就是普通组」：类型是 SvgGroupElement、能 translate、
    bbox 跟着动，而换色要经 tools 函数（颜色属性 / ``style`` / ``<style>``
    块里 class 写的颜色一起换，模板改一处则所有 ``<use>`` 实例一起变）。
    """
    src = '''
from malight import GroupElement, ImageElement, Malight
from malight.elements.svgimage import SVGImageElement
from malight.elements.svggroup import SvgGroupElement
from malight.tools import (replace_svg_color, svg_colors, svg_intrinsic_size,
                           svg_text_to_data_uri, read_svg_text,
                           replace_svg_node_color, replace_svg_node_text,
                           svg_node_colors, walk_svg_nodes)
import base64, os, tempfile

SRC = """<svg xmlns="http://www.w3.org/2000/svg" width="120" height="80">
  <circle cx="60" cy="40" r="30" fill="#ffffff" stroke="white"/>
  <rect width="10" height="10" id="orange" fill="rgba(255,255,255,0.5)"/>
  <text x="10" y="70">white</text>
  <g style="fill:#FFF"><path d="M0 0h5"/></g>
</svg>"""
d = tempfile.mkdtemp()
p = os.path.join(d, "circle-pattern-01.svg")
open(p, "w", encoding="utf-8", newline="").write(SRC)
assert read_svg_text(p) == SRC
assert svg_text_to_data_uri("<svg/>").startswith("data:image/svg+xml;base64,")

# 1) 工具层：写法互认、不误伤、认不出就别乱换
assert svg_colors(SRC) == ["#ffffff"], svg_colors(SRC)
text, n = replace_svg_color(SRC, "白色", "#ff0000")
assert n == 4, n
assert text.replace(">white<", "").count("white") == 0, text
assert 'id="orange"' in text and ">white<" in text
assert replace_svg_color(SRC, "rgb(255,255,255)", "#00ff00")[1] == 4
assert replace_svg_color(SRC, "url(#fff)", "#000000")[1] == 0
assert replace_svg_color(SRC, "红", "#000000")[1] == 0
try:
    replace_svg_color(SRC, "#ffffff", "nonsense")
    raise AssertionError("新颜色认不出时应当报错")
except ValueError:
    pass
assert svg_intrinsic_size(SRC) == (120.0, 80.0)

# 2) 元素层：svg_image() -> 只给宽按比例算高 -> 换色 -> 局部更新不冲掉文本
pen = Malight("_svgtext", width=400, height=300)
icon = pen.svg_image(p, x=10, y=10, width=60)
assert isinstance(icon, SVGImageElement), type(icon)
assert icon.node.attribs["height"] == 40.0, icon.node.attribs["height"]
assert icon.svg_colors() == ["#ffffff"]
icon.replace_color("#ffffff", "#ff0000")
icon.update(width=120)                       # 局部更新不能把改过的文本冲回原样
raw = icon.node.attribs["href"].split("base64,", 1)[1]
cur = base64.b64decode(raw).decode("utf-8")
assert "#ff0000" in cur and "#ffffff" not in cur, cur
assert cur.replace(">white<", "").count("white") == 0
assert icon.node.attribs["width"] == 120
assert icon.get_svg_text() == cur
icon.replace_text("circle", "ellipse", warn=False)
assert "<ellipse" in icon.get_svg_text() and "<circle" not in icon.get_svg_text()
assert icon.set_svg_text(SRC) is icon and icon.svg_colors() == ["#ffffff"]

# 3) 同一个文件贴两次各改各的；旧名 paste_svg 仍是同一类
other = pen.svg_image(p, x=200, y=10, width=60)
assert other.svg_colors() == ["#ffffff"]          # 第二个实例没被第一个影响
other.replace_color("white", "#00a651")
assert other.svg_colors() == ["#00a651"]
assert icon.svg_colors() == ["#ffffff"]           # 各改各的
assert isinstance(pen.paste_svg(p, 0, 200, 40), SVGImageElement)
assert isinstance(pen.image(p, 0, 0, 40), ImageElement), "image() 仍是位图元素"

# 4) 导入成组：拿到的是「组元素」（有组的全套能力），但对象上没有换色方法
grp = pen.import_svg_as_group(p, x=10, y=200, scale=0.5)
assert isinstance(grp, SvgGroupElement), type(grp)
assert isinstance(grp, GroupElement), "导入的组与 pen.g() 同族"
assert not hasattr(grp, "replace_color"), "换色只属于 svg_image 那条通道"
assert not hasattr(grp, "svg_colors") and not hasattr(grp, "replace_text")
assert not hasattr(grp.node, "replace_color"), "SvgNode 只剩树操作"
assert not hasattr(grp.node, "svg_colors") and not hasattr(grp.node, "replace_text")
assert [n.tag for n in walk_svg_nodes(grp.node)][:2] == ["g", "svg"]
assert grp.elements() == [], "导入的节点没有元素对象"

# 组的能力：bbox 按原始画布 + 变换算，translate 之后跟着动
assert tuple(round(v, 1) for v in grp.bbox()) == (10.0, 200.0, 70.0, 240.0)
grp.translate(5, 0)
assert tuple(round(v, 1) for v in grp.bbox()) == (15.0, 200.0, 75.0, 240.0)

# 换色走 tools 函数改节点属性
assert svg_node_colors(grp.node) == ["#ffffff"], svg_node_colors(grp.node)
assert replace_svg_node_color(grp.node, "白色", "#ff0000") == 4, "命中 4 处"
assert svg_node_colors(grp.node) == ["#ff0000"]
grp.update(y=210)                            # 局部更新不重解析、不冲掉改色
assert svg_node_colors(grp.node) == ["#ff0000"]
assert tuple(round(v, 1) for v in grp.bbox()) == (15.0, 210.0, 75.0, 250.0)
xml = grp.node.to_xml(pretty=False)
assert 'id="orange"' in xml and ">white<" in xml, "同名标识与文字正文不动"

# 5) 模板：同样不带换色方法，改符号内容则所有 <use> 实例一起变
tpl = pen.import_svg_as_symbol(p, id_="icon_tpl")
assert not hasattr(tpl, "replace_color"), "模板也不挂换色方法"
assert svg_node_colors(tpl.node) == ["#ffffff"]
replace_svg_node_color(tpl.node, "white", "#1e90ff")
assert svg_node_colors(grp.node) == ["#ff0000"], "组与模板各持一份节点树"
pen.use("icon_tpl", x=200, y=200, width=80, height=54)
assert replace_svg_node_color(grp.node, "红", "#000000") == 0, "旧色认不出就不动"
try:
    replace_svg_node_color(grp.node, "#ff0000", "nonsense")
    raise AssertionError("新颜色认不出时应当报错")
except ValueError:
    pass
assert replace_svg_node_text(grp.node, "circle", "ellipse") == 1
assert "ellipse" in grp.node.to_xml(pretty=False)
out = pen.finish()
svg = open(out, encoding="utf-8").read()
assert "#1e90ff" in svg and "#ff0000" in svg, "两种改色都要落进导出文件"
print("SVG 文本换色通过：4 种写法一次全换、局部更新不冲文本、同文件多配色")
print("SVG 组通道通过：SvgGroupElement 可变换 / 无换色方法 / tools 函数改色")
'''
    ok, out, sec = run_py(["-c", src], tmp)
    rep.add("元素", "SVG 换色：图片通道（改文本）+ 导入节点通道", ok, out, sec)


def check_i18n(rep, tmp):
    """默认英文、切中文、环境变量、区域码兜底、use_language 作用域。"""
    src = (
        "import malight\n"
        "from malight import (t, set_language, get_language, reset_language,\n"
        "                     use_language, is_chinese, available_languages,\n"
        "                     Language, add_messages, i18n)\n"
        "assert get_language() == 'en', get_language()\n"
        "assert not is_chinese()\n"
        "assert 'en' in available_languages() and 'zh' in available_languages()\n"
        "assert set_language('zh') in ('zh',), set_language('zh')\n"
        "assert is_chinese() and get_language().startswith('zh')\n"
        "cn = t('export.ok', kind='SVG', tail='', path='a.svg', size='1 KB')\n"
        "reset_language()\n"
        "assert get_language() == 'en', get_language()\n"
        "en = t('export.ok', kind='SVG', tail='', path='a.svg', size='1 KB')\n"
        "assert cn != en, (cn, en)\n"
        "assert 'a.svg' in cn and 'a.svg' in en\n"
        "set_language('zh-TW')\n"
        "assert is_chinese(), '区域码 zh-TW 应回落到中文族'\n"
        "with use_language('en'):\n"
        "    assert not is_chinese()\n"
        "assert is_chinese(), '出块应还原'\n"
        "reset_language()\n"
        "assert t('__不存在的键__') == '__不存在的键__', '缺词应原样返回 key'\n"
        "add_messages('xx', {}); assert set_language('xx') in ('xx',)\n"
        "reset_language()\n"
        "set_language('auto'); get_language(); reset_language()\n"
        "print('i18n ok: en/zh/zh-TW/auto/use_language/缺词 全部符合预期')\n"
    )
    ok, out, sec = run_py(["-c", src], tmp)
    rep.add("多语言", "默认英文 + 切中文 + 兜底", ok, out, sec)

    ok, out, sec = run_py(["-c",
                           "import malight, os, sys\n"
                           "assert sys.stderr is not None\n"
                           "print(malight.get_language())"],
                          tmp, env={"MALIGHT_LANG": "zh"})
    ok = ok and out.strip().endswith("zh")
    rep.add("多语言", "环境变量 MALIGHT_LANG=zh", ok, out, sec)


CN = re.compile(r"[\u4e00-\u9fff]")
#: 英文页唯一允许出现中文的地方：语言开关的链接文字
SWITCH = re.compile(r"\[\u7b80\u4f53\u4e2d\u6587\]")
#: 必须通篇英文的页面（模块英文页 / 英文 README / PyPI 说明页）
ENGLISH_PAGES = ("README.en.md", "README.pypi.md", ".en.md")


def check_docs(rep, tmp):
    ok, out, sec = run_py([os.path.join(HERE, "gen_docs.py"), "--check"], tmp)
    rep.add("文档", "模块双语文档与源码同步", ok, out, sec)

    ok, out, sec = run_py([os.path.join(HERE, "bilingualize_code.py"), "--check"], tmp)
    rep.add("文档", "示例注释/文案双语完整", ok, out, sec)

    ok, out, sec = run_py([os.path.join(HERE, "body_en.py")], tmp)
    rep.add("文档", "英文正文译文表未过期", ok, out, sec)

    ok, out, sec = run_py([os.path.join(HERE, "pypi_readme.py"), "--check"], tmp)
    rep.add("文档", "PyPI 说明页与 README.en.md 同步", ok, out, sec)


def check_color_constants(rep):
    """
    `Color` 的 138 个颜色常量必须与 `_COLOR_TABLE` 同步（`tools/gen_color_constants.py`）。

    这条是用户报出来的：``Color.BLACK`` / ``Color.WHITE`` 运行时能用，但在
    PyCharm 里**无法识别** —— 常量原来是用一行 ``locals().update(...)``
    动态写进类命名空间的，静态分析看不见：点不出来、拼错也不报错。
    改成 138 行显式赋值后 IDE 立刻恢复，而颜色数据仍然只写在
    ``_COLOR_TABLE`` 一处；本检查保证两边不会漂移。
    """
    tool = os.path.join(HERE, "gen_color_constants.py")
    ok, tail, sec = run_py([tool, "--check"], ROOT)
    rep.add("文档", "颜色常量与 _COLOR_TABLE 同步（138 个）", ok, tail, sec)


def check_terminal_color(rep):
    """
    终端上色判定（`tools/check_terminal_color.py`）。

    这条是用户报出来的：**PyCharm 里彩色消息全都没有颜色**。根因是判定只看
    ``sys.stdout.isatty()``，而 IDE 的运行窗口把 stdout 接成管道、``isatty()``
    恒为 False（窗口本身却会渲染 ANSI），于是加色分支根本不执行。
    本检查真的起子进程、真的看输出里有没有 ``\\x1b[``，把 8 个场景逐一验证。
    """
    tool = os.path.join(HERE, "check_terminal_color.py")
    ok, tail, sec = run_py([tool, "--quiet"], ROOT)
    rep.add("文档", "终端上色判定（IDE 运行窗口 / 重定向 / 环境变量）", ok, tail, sec)


def check_docs_text(rep):
    """英文页不得混入中文；所有相对链接都要能点开。"""
    cjk, links = [], []
    files = [os.path.join(ROOT, "README.md"), os.path.join(ROOT, "README.en.md"),
             os.path.join(ROOT, "README.pypi.md")]
    for root, dirs, names in os.walk(os.path.join(ROOT, "malight")):
        dirs[:] = [d for d in dirs if d not in SKIP_MODULE_PARTS]
        for n in sorted(names):
            if n.endswith(".md"):
                files.append(os.path.join(root, n))
    for f in files:
        if not os.path.isfile(f):
            continue
        text = io.open(f, encoding="utf-8").read()
        if f.endswith(ENGLISH_PAGES):
            for no, line in enumerate(text.split("\n"), 1):
                if CN.search(line) and not SWITCH.search(line):
                    cjk.append("%s:%d %s" % (rel(f), no, line.strip()[:70]))
        for link in re.findall(r"\]\(([^)#]+)\)", text):
            if link.startswith(("http", "mailto")):
                continue
            target = os.path.normpath(os.path.join(os.path.dirname(f), link))
            if not os.path.exists(target):
                links.append("%s -> %s" % (rel(f), link))
    rep.add("文档", "英文页无中文（语言开关除外）", not cjk, "\n".join(cjk[:8]))
    rep.add("文档", "文档相对链接有效 (%d 个文件)" % len(files),
            not links, "\n".join(links[:8]))


# ---------------------------------------------------------------------------
def main(argv):
    fast = "--fast" in argv
    only_list = "--list" in argv
    demos, tests, modules = collect(argv)

    if fast:
        demos = [d for d in demos if os.path.basename(d) not in SLOW]

    if only_list:
        print("示例 (%d):" % len(demos))
        for d in demos:
            print("   ", rel(d))
        print("测试 (%d):" % len(tests))
        for d in tests:
            print("   ", rel(d))
        print("模块 __main__ 示例 (%d):" % len(modules))
        for d in modules:
            print("   ", rel(d))
        return 0

    print("=== malight 全量回归%s ===" % ("（--fast）" if fast else ""))
    print("解释器:", PY)
    print("示例 %d 个 ｜ 测试 %d 个 ｜ 模块示例 %d 个 ｜ 静态检查：语法/行尾/占位符/遮蔽/双语对/滤镜/元素属性/文档链路/多语言/网页编辑器/动画"
          % (len(demos), len(tests), len(modules)))
    print("-" * 68)

    rep = Report()
    tmp = tempfile.mkdtemp(prefix="malight_regress_")
    try:
        check_compile(rep)
        check_eol(rep)
        check_placeholders(rep)
        check_i18n_shadow(rep)
        check_bilingual_split(rep)
        check_fx_api(rep)
        check_fx_chain(rep, tmp)
        check_element_attrs(rep)
        check_clone_isolation(rep, tmp)
        check_chain_typing(rep)
        check_attr_accessors(rep)
        check_svg_text_edit(rep, tmp)
        check_docs(rep, tmp)
        check_color_constants(rep)
        check_terminal_color(rep)
        check_docs_text(rep)
        check_i18n(rep, tmp)
        check_htmleditor(rep)
        check_smil_anim(rep)
        for p in tests:
            check_script(rep, "测试", p, tmp)
        for p in demos:
            check_script(rep, "示例", p, tmp)
        for p in modules:
            check_script(rep, "模块示例", p, tmp)
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)

    return rep.summary()


if __name__ == "__main__":
    print("=== malight 全量回归 ===")
    sys.exit(main(sys.argv[1:]))
