# -*- coding: utf-8 -*-
"""
magicpen —— 旧包名兼容 shim（源码目录专用）
==========================================

malight v2.0 由原 `magicpen` 更名而来。为了让按旧名写的脚本
（``import magicpen`` / ``from magicpen import MagicPen``）继续可用，
本 shim 把名字全部转发到 ``malight``。

注意：
- 本目录**不进 wheel**（发布包只含 malight），只在源码仓库内提供迁移缓冲；
- 新代码请直接 ``import malight``；
- 旧脚本也可用内置迁移工具一次性改写：
  ``python -m malight.compat 旧脚本.py 新脚本.py``

示例::

    import magicpen                     # 等价于 import malight
    pen = magicpen.MagicPen("demo")     # MagicPen 仍可用（等价 malight.Malight）
    pen.circle(100, 100, 50, fill_color="red")
    pen.finish()
"""

import os as _os
import sys as _sys

# 允许从仓库根目录直接 import（把仓库根加入搜索路径）
_REPO_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
if _REPO_ROOT not in _sys.path:
    _sys.path.insert(0, _REPO_ROOT)

from malight import *                                    # noqa: F401,F403
from malight import (MagicPen, Malight, Color,            # noqa: F401
                     SystemFont, TextHAlign, TextVAlign, StrokeCap,
                     StrokeJoin, ArrowStyle, PointStyle, GridRepeatType,
                     CoordUnits, PaperSize, PaperSettings, PNGMode, PDFMode,
                     DOCXMode, PaperOrientation, ColorScheme, PointStyle as _PS)
from malight import __version__                           # noqa: F401
import malight as _malight

# 子模块透传：magicpen.board / magicpen.elements / magicpen.tools ...
from malight import board, elements, tools, ext   # noqa: F401
try:
    from malight import compat                    # noqa: F401
except ImportError:                               # pragma: no cover
    compat = None

# 兼容旧的项目根目录结构：magicpen/magicpen/...
__all__ = list(getattr(_malight, "__all__", []))
