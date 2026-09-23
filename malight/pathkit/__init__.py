# -*- coding: utf-8 -*-
"""
pathkit —— 路径辅助工具包（英文版新增）
=========================================

pathkit: inspect and edit the anchors and control points of a path.

解决「PathElement 太复杂、不好用」的问题：把路径变成**看得见、拖得动**的点。

包含四个类 + 两个函数：

- `PathEditor`     路径编辑器：看结构、拖锚点、拖控制点、加点、删点、可视化、存档
- `PathHTMLEditor` 路径 **UI** 编辑器：导出单文件 HTML，用鼠标拖点并实时出代码
- `PathPoint`      一个可调点（锚点 / 控制点）
- `PathSegment`    路径中的一段（M / L / C / Q / A / Z，绝对坐标）
- `parse_path_d(d)`        d 字符串 -> 线段列表（展开 H/V/S/T，绝对坐标）
- `segments_to_d(segs)`    线段列表 -> d 字符串

最快上手（在已有路径上查看并调整）::

    from malight import Malight

    pen = Malight("demo", width=600, height=400)
    p = pen.path(fill_color="none", stroke_color="#e63946", stroke_width=3)
    p.move_to(60, 300)
    p.cubic_to((120, 80), (260, 80), (320, 300))

    print(p.describe())           # 直接看结构（PathElement 上的便捷方法）
    p.anchors()[1].move_to(200, 60)      # 拖第 2 个锚点
    p.controls()[1].move_by(0, -40)      # 拖第 2 个调整点
    p.show_points()                      # 把点画在画布上
    pen.finish()

用鼠标拖（拿不准坐标时最快）::

    from malight.pathkit import PathEditor

    ed = PathEditor(p)
    ed.save_html("output/edit.html")     # 浏览器打开，拖完复制代码 / 下载 points.json

单独使用编辑器类::

    from malight.pathkit import PathEditor

    ed = PathEditor(p)
    ed.insert_anchor(1, 0.5)      # 曲线中点加锚点（形状不变）
    ed.save_json("points.json")   # 点位存档，外部改完再 load_json 读回
"""

from .segment import PathSegment
from .point import PathPoint
from .editor import PathEditor
from .htmleditor import PathHTMLEditor
from .parser import parse_path_d, segments_to_d, reverse_segments, tokenize

__all__ = [
    "PathEditor", "PathHTMLEditor", "PathPoint", "PathSegment",
    "parse_path_d", "segments_to_d", "reverse_segments", "tokenize",
]
