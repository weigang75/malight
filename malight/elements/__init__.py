# -*- coding: utf-8 -*-
"""元素库：每个 SVG 元素类一个文件（中文注释 + 示例）。"""

from .base import Element, _paint, _fmt_points, _fmt_transform
from .circle import CircleElement
from .ellipse import EllipseElement
from .rect import RectElement
from .line import LineElement
from .polyline import PolylineElement
from .polygon import PolygonElement
from .text import TextElement
from .textpath import TextPathElement
from .image import ImageElement
from .svgimage import SVGImageElement
from .group import GroupElement
from .svggroup import SvgGroupElement
from .symbol import TemplateElement
from .use import UseElement
from .marker import MarkerElement
from .clippath import ClipPathElement
from .mask import MaskElement
from .link import LinkElement
from .pattern import PatternElement
from .path import PathElement

__all__ = ["Element", "PathElement", "CircleElement", "EllipseElement", "RectElement", "LineElement", "PolylineElement", "PolygonElement", "TextElement", "TextPathElement", "ImageElement", "SVGImageElement", "GroupElement", "SvgGroupElement", "TemplateElement", "UseElement", "MarkerElement", "ClipPathElement", "MaskElement", "LinkElement", "PatternElement"]