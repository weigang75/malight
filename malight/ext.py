# -*- coding: utf-8 -*-
"""
ext —— malight 扩展机制（让第三方工具包无缝挂进绘图板）。 / The extension mechanism: register a third-party toolkit with @toolkit and mount it on a board.

设计目标：以后给「神笔码靓」增加能力（如图表包、图标包、特效包）
不需要改 malight 源码 —— 任何包只要用 ``@toolkit`` 注册，
用户一行 ``pen.use_toolkit("名字")`` 即可把全部方法挂到绘图板上。

三个角色：
1. 工具包作者：写一个类，方法第一个参数是 pen（self），
   用 ``@toolkit("注册名")`` 装饰即可自动注册；
2. 用户：import 该工具包模块 → ``pen.use_toolkit("注册名")``；
3. 查询：``malight.ext.list_toolkits()`` 查看所有已注册工具包。

本文件只包含函数级 API（注册表 + 装饰器 + 绑定）。
"""

import types
from .i18n import t

# 注册表：注册名 -> 工具包类
_registry = {}


def register(name, cls):
    """
    注册一个工具包类（内部函数，一般用 @toolkit 装饰器代替）。 / Register a toolkit class; internal helper, normally reached through the @toolkit decorator.

    :param name: 注册名（挂载时使用，如 "charts"）
    :param cls: 工具包类，其公开方法（非下划线开头）将成为绘图板方法

    示例::
        class BadgeKit:
            def badge(self, x, y, text): ...
        malight.ext.register("badge", BadgeKit)
    """
    if not isinstance(name, str) or not name:
        raise ValueError(t("err.toolkit_name_empty"))
    if not inspect_class(cls):
        raise TypeError(t("err.toolkit_not_class", name=name,
                          type=type(cls).__name__))
    _registry[name] = cls
    return cls


def inspect_class(cls):
    """校验参数是否为类（内部函数）。 / Check that the argument is a class; internal helper. """
    return isinstance(cls, type)


def toolkit(name):
    """
    工具包注册装饰器（推荐用法）。 / Toolkit registration decorator; the recommended way to register one.

    :param name: 注册名（pen.use_toolkit(name) 时使用）

    示例（工具包作者）::
        # my_charts.py
        from malight.ext import toolkit

        @toolkit("charts")
        class ChartToolkit:
            def bar_chart(self, data, x, y, w, h, color="#4e79a7"):
                # self 就是绘图板 pen
                total = max(data)
                bw = w / len(data)
                for i, v in enumerate(data):
                    self.rect(x + i * bw, y + h - h * v / total,
                              bw * 0.7, h * v / total, fill_color=color)

    示例（用户）::
        import my_charts                       # 触发注册
        pen = Malight("report")
        pen.use_toolkit("charts")              # 挂载
        pen.bar_chart([3, 7, 5], 100, 100, 400, 300)   # 直接调用
    """
    def deco(cls):
        return register(name, cls)
    return deco


def list_toolkits():
    """
    列出所有已注册工具包名。 / List the names of every registered toolkit.

    示例::
        print(malight.ext.list_toolkits())   # ['charts', 'badge', ...]
    """
    return sorted(_registry.keys())


def _bind(pen, name):
    """
    把工具包的公开方法挂到绘图板实例上（内部函数，pen.use_toolkit 调用）。

    已挂载的同名方法会被覆盖（后挂载优先）；以 "_" 开头的方法不挂载。
    """
    cls = _registry.get(name)
    if cls is None:
        raise KeyError(t("err.toolkit_not_found", name=name,
                         names=list_toolkits()))
    count = 0
    # 工具包方法的 self 就是绘图板 pen（用起来和原生方法一致，
    # 方法内可直接调用 self.circle / self.rect / self.fx ...）
    for attr in dir(cls):
        if attr.startswith("_"):
            continue
        func = getattr(cls, attr, None)
        if callable(func) and isinstance(func, types.FunctionType):
            setattr(pen, attr, func.__get__(pen, type(pen)))
            count += 1
    return count
