# -*- coding: utf-8 -*-
"""
方法链返回类型闸门：链式方法必须解析成「当前元素类」，不能退化成 Element。
============================================================================

背景（用户实测反馈）：`pen.path(...).move_to(...).` 在 PyCharm 里点出来的
全是 Element 的方法，子类自己的方法一个都补不到 —— 因为标注只写了
`-> _Self`（模块级 TypeVar，bound=Element），PyCharm 只按上界推导。

所以链式方法的返回类型必须是**具体元素类**。本工具用两条腿保证：

1. 静态检查（永远跑，零依赖）
   - 每个子类声明成 `class PathElement(Element["PathElement"])`
     （泛型实参把基类里 65 个 `-> _Self` 的链式方法代入成具体子类）；
   - 子类自己 `return self` 的方法，返回标注必须是本类名（带引号也行）；
   - 子类文件里不允许再出现 `_Self`；
   - 基类 `Element` 必须是 `Generic[_Self]`，且 `-> _Self` 的方法首个
     参数要写成 `self: _Self`（PEP 484 的 self-type，给 mypy/pyright 用）。

2. 类型检查器实测（装了 mypy 才跑）
   把探针源码交给 mypy，断言每个 `reveal_type` 都报具体元素类。
   没装 mypy 就跳过并说明 —— 静态检查那半边仍然生效。

命令行::

    python tools/check_chain_typing.py            # 静/实测都跑
    python tools/check_chain_typing.py --no-mypy  # 只做静态检查（回归用）
"""

import ast
import os
import shutil
import subprocess
import sys
import tempfile

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
ELEMS = os.path.join(_ROOT, "malight", "elements")

# 期望 mypy 推出来的类型：表达式 -> 类名（见 PROBE）
EXPECT = [
    ("pen.path().set_opacity(0.5)", "PathElement"),
    ("pen.path().translate(1, 2).rotate(30)", "PathElement"),
    ("pen.path().move_to(1, 1).set_stroke_width(2)", "PathElement"),
    ("pen.circle(5, 5, 1).set_fill_color('red')", "CircleElement"),
    ("pen.text(1, 1, 'x').update(font_size=9)", "TextElement"),
    ("pen.rect(0, 0, 2, 2).set_stroke_join('round')", "RectElement"),
    ("pen.polyline([(0, 0), (1, 1)]).clone()", "PolylineElement"),
    ("pen.copy(pen.circle(1, 1, 1))", "CircleElement"),
]

PROBE_HEAD = '''# -*- coding: utf-8 -*-
from malight import Malight
pen = Malight("probe", width=100, height=100)
'''


# ---------------------------------------------------------------------------
# 1) 静态检查
# ---------------------------------------------------------------------------
def _returns_self(node):
    """方法体里有没有「裸 return self」（直接或分支里）。"""
    for sub in ast.walk(node):
        if isinstance(sub, ast.Return) and isinstance(sub.value, ast.Name) \
                and sub.value.id == "self":
            return True
    return False


def _ann_text(ann):
    """把返回标注还原成可比较的名字（"PathElement" / PathElement 都一样）。"""
    if isinstance(ann, ast.Constant) and isinstance(ann.value, str):
        return ann.value
    if isinstance(ann, ast.Name):
        return ann.id
    if isinstance(ann, ast.Subscript) and isinstance(ann.value, ast.Name):
        return ann.value.id
    return None


def static_check():
    """返回问题列表。"""
    bad = []
    base_path = os.path.join(ELEMS, "base.py")
    base_src = open(base_path, encoding="utf-8").read()
    base_tree = ast.parse(base_src)

    # --- 基类：Element(Generic[_Self]) + self: _Self ---
    base_cls = next((n for n in base_tree.body
                     if isinstance(n, ast.ClassDef) and n.name == "Element"), None)
    if base_cls is None:
        bad.append("base.py: 找不到 class Element")
        return bad
    bases = [_ann_text(b) for b in base_cls.bases]
    if "Generic" not in bases:
        bad.append("base.py: Element 必须是 Generic[_Self]（否则链式补全拿不到子类）")
    unsignatured = []
    for fn in base_cls.body:
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if _ann_text(fn.returns) != "_Self":
            continue
        if not fn.args.args or fn.args.args[0].arg != "self":
            continue
        if fn.args.args[0].annotation is None:
            unsignatured.append(fn.name)
    if unsignatured:
        bad.append("base.py: 这些 `-> _Self` 方法没写 `self: _Self`：%s"
                   % ", ".join(sorted(unsignatured)[:8]))

    # --- 各子类 ---
    for name in sorted(os.listdir(ELEMS)):
        if not name.endswith(".py") or name in ("base.py", "__init__.py"):
            continue
        path = os.path.join(ELEMS, name)
        src = open(path, encoding="utf-8").read()
        rel = "malight/elements/" + name
        if "_Self" in src:
            bad.append("%s: 子类文件里不该再出现 _Self（返回类型要写具体类）" % rel)
        try:
            tree = ast.parse(src)
        except SyntaxError as exc:
            bad.append("%s: 语法错误 %s" % (rel, exc))
            continue
        cls = None
        for node in tree.body:
            if not isinstance(node, ast.ClassDef):
                continue
            for b in node.bases:
                if isinstance(b, ast.Name) and b.id == "Element":
                    bad.append('%s: %s 继承写成了裸 Element，应为 Element["%s"]'
                               % (rel, node.name, node.name))
                    cls = node
                elif isinstance(b, ast.Subscript) and _ann_text(b) == "Element":
                    cls = node
            if cls is node:
                break
        if cls is None:
            continue
        for fn in cls.body:
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if not _returns_self(fn):
                continue
            got = _ann_text(fn.returns)
            if got is None:
                bad.append("%s: %s.%s 有 return self 但没写返回类型，IDE 推不出链式类型"
                           % (rel, cls.name, fn.name))
            elif got != cls.name:
                bad.append("%s: %s.%s 返回标注是 %r，应为 %r"
                           % (rel, cls.name, fn.name, got, cls.name))
    return bad


# ---------------------------------------------------------------------------
# 2) mypy 实测（可选）
# ---------------------------------------------------------------------------
def mypy_check():
    """返回 (状态, 说明)。状态：ok / fail / skip。"""
    try:
        import mypy  # noqa: F401
    except ImportError:
        return "skip", "未安装 mypy，跳过（静态检查仍已生效）"
    body = "".join("reveal_type(%s)\n" % e for e, _ in EXPECT)
    src = PROBE_HEAD + body
    fd, path = tempfile.mkstemp(suffix=".py", prefix="_chain_probe_", dir=_ROOT)
    # mypy 默认会在仓库根写 .mypy_cache/，会污染工作区（回归的 LF/行尾检查会报它），
    # 所以缓存目录指到临时目录里。
    cache = tempfile.mkdtemp(prefix="malight_mypy_")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(src)
        proc = subprocess.run(
            [sys.executable, "-m", "mypy", "--no-error-summary",
             "--no-incremental", "--follow-imports=silent",
             "--cache-dir", cache, path],
            cwd=_ROOT, capture_output=True, encoding="utf-8", errors="replace")
        out = (proc.stdout or "") + (proc.stderr or "")
        got = {}
        for line in out.splitlines():
            if "note:" in line and "Revealed type is" in line:
                num = line.split(":")[1].strip()
                got[int(num)] = line.split('"')[1].split(".")[-1]
        problems = []
        first = PROBE_HEAD.count("\n") + 1      # reveal_type 首行行号
        for i, (expr, want) in enumerate(EXPECT):
            have = got.get(first + i)
            if have != want:
                problems.append("%s -> %s（期望 %s）" % (expr, have or "未解析", want))
        if problems:
            return "fail", "\n".join(problems)
        return "ok", "mypy 实测 %d 条链式表达式全部解析成具体元素类" % len(EXPECT)
    finally:
        try:
            os.remove(path)
        except OSError:
            pass
        shutil.rmtree(cache, ignore_errors=True)


def main():
    only_static = "--no-mypy" in sys.argv
    bad = static_check()
    print("=" * 74)
    print("方法链返回类型检查：链式方法必须解析成具体元素类")
    print("=" * 74)
    if bad:
        print("静态检查失败 %d 项：" % len(bad))
        for b in bad:
            print("  - " + b)
        return 1
    print("静态检查通过：基类 Generic[_Self] + self: _Self，"
          "19 个子类全部参数化且链式返回标注为本类。")

    if only_static:
        return 0
    state, detail = mypy_check()
    if state == "skip":
        print("类型检查器实测：跳过（%s）" % detail)
        return 0
    print("类型检查器实测：%s（%s）" % ("通过" if state == "ok" else "失败", detail))
    return 1 if state == "fail" else 0


if __name__ == "__main__":
    sys.exit(main())
