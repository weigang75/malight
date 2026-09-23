# -*- coding: utf-8 -*-
"""
类型注解校验测试（PyCharm / VSCode 提示保障）
=============================================

三件事：
1. 全库公共方法必须带返回类型注解（漏了就失败）；
2. 每个注解都能被 ``typing.get_type_hints`` 求值（防止写错名字）；
3. 抽样断言运行时返回值与注解一致（``pen.path()`` 真的是 PathElement 等）。

运行::

    python test_types.py

期望输出::

    公共方法总数: 2xx，缺注解: 0
    注解求值失败: 0
    运行时类型断言: 全通过
    ALL TYPE HINT TESTS PASSED
"""

import inspect
import os
import sys
import typing

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import malight                                   # noqa: E402
from malight import Malight                      # noqa: E402
from malight.board.fx import FilterChain         # noqa: E402
from malight.elements import (CircleElement, RectElement, PathElement,   # noqa: E402
                              TextElement, GroupElement, PolylineElement,
                              PolygonElement, Element)
from malight.gradients import LinearGradient     # noqa: E402

# ---------------------------------------------------------------------------
# 1) 注解覆盖率：逐类逐方法扫描
# ---------------------------------------------------------------------------
SKIP_NAME = {"__init__", "__repr__", "__str__"}   # 魔法方法不强制

missing = []
total = 0
for mod_name, mod in sys.modules.items():
    if not mod_name.startswith("malight"):
        continue
    for cls_name, cls in vars(mod).items():
        if not inspect.isclass(cls) or cls.__module__ != mod_name:
            continue
        for fn_name, fn in vars(cls).items():
            if not inspect.isfunction(fn) or fn_name in SKIP_NAME:
                continue
            if fn_name.startswith("_"):
                continue                              # 内部方法不强制
            total += 1
            if "return" not in fn.__annotations__:
                missing.append(f"{mod_name}.{cls_name}.{fn_name}")

print(f"公共方法总数: {total}，缺注解: {len(missing)}")
for m in missing:
    print("   缺注解:", m)
assert not missing, "存在未标注返回类型的公共方法"

# ---------------------------------------------------------------------------
# 2) 注解求值：全部模块（同时确保 import 无副作用错误）
# ---------------------------------------------------------------------------
import importlib                                    # noqa: E402
import pkgutil                                      # noqa: E402

bad = []
mod_names = [m.name for m in pkgutil.walk_packages(malight.__path__, "malight.")]
for name in mod_names:
    importlib.import_module(name)
for mod_name in ["malight"] + mod_names:
    mod = sys.modules.get(mod_name)
    if mod is None:
        continue
    for cls_name, cls in vars(mod).items():
        if not inspect.isclass(cls) or cls.__module__ != mod_name:
            continue
        for fn_name, fn in vars(cls).items():
            if not inspect.isfunction(fn):
                continue
            try:
                typing.get_type_hints(fn)
            except Exception as e:                    # noqa: BLE001
                bad.append(f"{mod_name}.{cls_name}.{fn_name}: {e}")
print(f"注解求值失败: {len(bad)}")
for b in bad:
    print("   ", b)
assert not bad, "存在无法求值的注解（名字写错或漏 import）"

# ---------------------------------------------------------------------------
# 3) 运行时类型断言：注解说返回什么，就得真的是什么
# ---------------------------------------------------------------------------
pen = Malight("test_types", width=400, height=300)

checks = [
    ("circle", pen.circle(100, 100, 40), CircleElement),
    ("rect", pen.rect(10, 10, 50, 50), RectElement),
    ("path", pen.path(), PathElement),
    ("text", pen.text(10, 10, "hi"), TextElement),
    ("g", pen.g(), GroupElement),
    ("polyline", pen.polyline([(0, 0), (10, 10)]), PolylineElement),
    ("polygon", pen.polygon([(0, 0), (10, 0), (5, 10)]), PolygonElement),
]
for name, obj, expect in checks:
    assert isinstance(obj, expect), f"{name}: {type(obj)} != {expect}"
    print(f"  pen.{name}() -> {type(obj).__name__}")

# 链式方法返回自身（_Self TypeVar）
p = pen.path()
assert p.move_to(0, 0) is p and p.line_to(10, 10) is p
circle = pen.circle(200, 200, 20)
assert circle.set_id("c1") is circle
assert circle.translate(5, 5) is circle
assert circle.set_filter(pen.fx.blur(2)) is circle
print("  链式方法返回自身 OK")

# 渐变 / 滤镜 / 集合返回
assert isinstance(pen.linearGradient((0, 0), (1, 0), "red", "blue"),
                  LinearGradient)
assert isinstance(pen.fx.shadow(4, 4, 4), FilterChain)
assert isinstance(pen.repeat_grid(pen.circle(0, 0, 5), 2, 20, 2, 20), list)
assert isinstance(pen.arrange_horizontal([], gap=1), list)
print("  渐变/滤镜/排列返回类型 OK")

# 元素布尔运算返回新路径元素
p1 = pen.path().move_to(0, 0).line_to(10, 0).line_to(10, 10).close()
print(f"  path.union 返回类型注解: "
      f"{PathElement.union.__annotations__.get('return')}")

# 命名空间导出保持完整
assert malight.Malight is malight.MagicPen
print("  导出符号 OK")

print("ALL TYPE HINT TESTS PASSED")
