# -*- coding: utf-8 -*-
"""
英文正文译文表（body_en）
========================

模块文档字符串的**正文**（摘要之后的设计说明）只有中文。英文页要「全英文」，
但又不想让源码 docstring 变成中英各一半（体积翻倍），于是把英文正文集中放在
这里：``tools/gen_docs.py`` 生成 ``xxx.en.md`` 时按模块取用。

English bodies for module docstrings. The Chinese body stays the single source of
truth in the source file; this table carries the English rendering that
``tools/gen_docs.py`` puts on the ``xxx.en.md`` pages, so the source does not have
to grow a second copy of every paragraph.

维护约定 / How to maintain:
    1. 只有「正文含中文」的模块才需要在这里登记；正文是空或纯英文的模块不用写。
    2. 正文里用**纯 Markdown**（单反引号、围栏代码块、管道表格），不要再写 RST 记号。
    3. 改完中文正文后跑 ``python tools/body_en.py --stamp`` 更新指纹；
       中文改了而这里没跟上时，``gen_docs.py --check`` 会报「译文可能已过期」。

    Run ``python tools/body_en.py --stamp`` after touching the Chinese body, and
    ``--check`` to see which entries went stale (the fingerprint mismatch check).
"""

from __future__ import print_function

import hashlib
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def _mixin(cls):
    """board 包里 Mixin 模块反复出现的那句说明，避免抄 12 遍。"""
    return ("This file contains a single class, `{0}`, a mixin that "
            "`board/__init__.py` composes into `MagicPen`.".format(cls))


# ===========================================================================
# 英文正文 / English bodies
# ===========================================================================
BODY_EN = {
    # ------------------------------------------------------------------
    # page 模块（打印与 PDF 的页面设置）
    # ------------------------------------------------------------------
    "malight/page.py": """\
`PageSetup` carries the paper, margin and scaling that `export_pdf_chrome`
(and the board's `export_pdf`) use when printing a canvas to a real sheet of
paper. By default a PDF page is exactly the canvas size with zero margins, so
nothing is ever cut off; give it a `size` and the content is scaled to fit the
sheet, centered inside the margins.

**Chrome engine only**: `@page` paper sizes and the `zoom` property are browser
layout features, so the cairosvg engine cannot honour them. Passing page setup
to `export_pdf_cairo` raises instead of silently ignoring it. PNG export is a
screen screenshot and has no notion of paper at all — its size is always
canvas x scale.
""",
    # ------------------------------------------------------------------
    # board 包
    # ------------------------------------------------------------------
    "malight/board/containers.py": _mixin("ContainerMixin"),
    "malight/board/core.py": """\
Canvas setup, element registration, page configuration, background and lifecycle hooks,
plus `finish()` saving and PNG / PDF / DOCX export. The drawing methods live in the
sibling mixin files.

This file contains a single class, `BoardCore`, a mixin that `board/__init__.py`
composes into `MagicPen`.""",
    "malight/board/debug.py": _mixin("DebugMixin"),
    "malight/board/effects.py": _mixin("ClipMaskMixin"),
    "malight/board/filters.py": """\
Every way to use filters (8 styles; they stack and can be shared). See
`assets/images/filters_preview.png` for the illustrated version - 8 cards,
code on the left, rendered result on the right.

**1. Element method chain (recommended - `fx_*` returns the element, so it chains forever)**

```python
el.fx_inner_shadow(1, 1, 2, "#ffffff", 0.6).fx_emboss().fx_blur(1.5)
```

**2. Stack an effect by name (same as `el.fx_blur(3)`)**

```python
el.fx("blur", 3)
```

**3. Append any raw SVG filter primitive**

```python
el.fx("custom", "feBlend", mode="screen", in2="SourceGraphic")
```

**4. Continue the chain already bound to the element**

```python
el.fx_chain().blur(2).saturate(1.4)
```

**5. Factory, one call (most common - pass `filter=` straight in)**

```python
pen.circle(500, 300, 120, fill_color="#4e79a7",
           filter=pen.fx.shadow(6, 8, 6))
```

**6. Factory chain, then bind it (one chain can be shared by many elements)**

```python
f = pen.fx.chain().blur(1).shadow(5, 5, 4)
a.set_filter(f)                 # or the equivalent f.apply(a)
```

**7. Stack / replace / clear (`set_filter` stacks by default instead of overwriting)**

```python
el.set_filter(pen.fx.shadow(6, 8, 6))
el.set_filter(pen.fx.saturate(0.4))         # stacks, the shadow stays
el.set_filter(pen.fx.glow(8), merge=False)  # replaces the whole chain
el.set_filter(None)                         # clears it
```

**8. Low-level helpers (grab an id from `tools.create_*_filter`, attach via `extra`)**

```python
fid = create_glow_filter(pen, 6)
pen.text(60, 150, "NEON", extra={"filter": "url(#%s)" % fid})
```

The factory methods map one-to-one onto the element shortcuts
(`pen.fx.blur(x)` is the same as `el.fx_blur(x)`); `pen.filter` is an alias of
`pen.fx`.

Every method returns a `FilterChain` (carrying a `<filter>` node and its id) that you can
pass straight to an element's `filter` argument, or bind with `el.set_filter(f)` /
`f.apply(el)`.

This file contains a single class, `FilterAPI`.""",
    "malight/board/fx.py": """\
One `FilterChain` maps to one SVG `<filter>` definition. Each effect method appends an SVG
filter primitive in call order (feGaussianBlur / feOffset / feFlood / feComposite /
feMerge / feColorMatrix / feComponentTransfer / feConvolveMatrix / feTurbulence /
feDisplacementMap / feMorphology / feSpecularLighting), and the output of the previous step
becomes the input of the next one - what you see is what you get.

Only effects that render identically and predictably in mainstream browsers (Chrome /
Firefox / Safari / Edge) are included; filters with unstable results are left out.

The elements carry shortcuts that mirror the factory one-to-one (`fx_*` returns the
element itself, so it chains forever):

```python
el.fx_inner_shadow(1, 1, 2, "#ffffff", 0.6).fx_emboss().fx_blur(1.5)
el.fx("blur", 3)                            # by name, same as el.fx_blur(3)
el.fx("custom", "feBlend", mode="screen")   # append a raw SVG primitive
el.fx_chain().blur(2).saturate(1.4)         # continue the element's own chain
```

All 8 ways to use filters are listed in the module docstring of
`malight/board/filters.py`, illustrated in `assets/images/filters_preview.png`.

This file contains a single class, `FilterChain`.""",
    "malight/board/gradients_mixin.py": _mixin("GradientMixin"),
    "malight/board/images.py": _mixin("ImageMixin"),
    "malight/board/layout.py": _mixin("LayoutMixin"),
    "malight/board/paths.py": _mixin("PathMixin"),
    "malight/board/repeat.py": _mixin("RepeatMixin"),
    "malight/board/shapes.py": _mixin("ShapeMixin"),
    "malight/board/style.py": "This file contains a single class, `StyleAPI`.",
    "malight/board/text_board.py": _mixin("TextMixin"),

    # ------------------------------------------------------------------
    # 顶层模块
    # ------------------------------------------------------------------
    "malight/compat.py": """\
Helps long-time users move scripts written for the original Chinese edition (Shenbi
Maliang) over to the English `malight` API.

Two ways to use it.

**1. Online compatibility layer** - a lookup table you can query at runtime:

```python
import malight.compat as compat

compat.METHOD_MAP        # Chinese method name -> English method name
compat.CLASS_MAP         # Chinese class name  -> English class name
compat.print_mapping(name)   # prints "name -> draw_circle" for one entry
```

**2. Offline migration script**

```bash
python -m malight.compat old_drawing.py new_drawing.py
# Rewrites Chinese API names into the English ones. Regex based and best
# effort: review the result before running the new script.
```""",
    "malight/definitions.py": """\
This module is the constant registry of the English edition, the counterpart of the
definition module in the original Chinese edition.

**Design rule (enum or string, both work)**: wherever a parameter takes only a handful of
values you get an enum, and plain strings are always accepted as well. The point is to be
convenient without being error-prone:

| Parameter | Recommended (enum) | Also accepted (string) |
|---|---|---|
| Color | `ColorName.RED` | `"red"`, `"#ff0000"`, or the Chinese colour word |
| Font | `Font.SIMHEI` | `"SimHei"` / `"simhei.ttf"` |
| Fill rule | `FillRule.EVENODD` | `"evenodd"` |
| Dash style | `DashStyle.DASHED` | `"8 4"` |
| Cap / join | `StrokeCap.ROUND` | `"round"` |
| Line join | `StrokeJoin.ROUND` | `"round"` |
| Text alignment | `TextHAlign.MIDDLE` | `"middle"` |
| Font weight | `FontWeight.BOLD` | `"bold"` / `700` |
| Text decoration | `TextDecoration.UNDERLINE` | `"underline"` |
| Blend mode | `BlendMode.MULTIPLY` | `"multiply"` |
| Arrow style | `ArrowStyle.SOLID` | `"solid"` |
| Point style | `PointStyle.CROSS` | `"cross"` |
| Gradient units | `CoordUnits.USER_SPACE` | `"userSpaceOnUse"` |
| Export engine | `PDFMode.CHROME` | `1` |

Every public entry point normalises its arguments through `value_of()`, so the two
spellings can be mixed freely.

Example:

```python
from malight import Color, ColorName, Font, FillRule, DashStyle

pen.text(100, 100, "Heading", font=Font.SIMHEI, weight=FontWeight.BOLD)
pen.polygon(pts, fill_color=ColorName.TEAL, fill_rule=FillRule.EVENODD)
pen.line((0, 0), (100, 0), stroke_style=DashStyle.DASHED)

print(Color.RED)                 # "#ff0000" (138 named colours plus the 2 no-colour constants)
print(ColorName.RED)             # "red" (the common subset, as an enum)
print(Color.RGB(30, 144, 255))   # "#1e90ff"
print(Color.darken("#D75D72"))   # darken a colour
w, h = PaperSize.A4_portrait()   # A4 pixel size
```""",
    "malight/ext.py": """\
Design goal: adding capabilities later on (a chart pack, an icon pack, an effects pack and
so on) must never require editing malight's own source. Any package that registers itself
with `@toolkit` is pulled in by a single `pen.use_toolkit("name")` line, which attaches all
of its methods to the drawing board.

Three roles:

1. Toolkit author - write a class whose methods take the pen as their first argument, and
   decorate it with `@toolkit("registered-name")` to register it automatically.
2. User - import the toolkit module, then `pen.use_toolkit("registered-name")`.
3. Discovery - `malight.ext.list_toolkits()` lists every registered toolkit.

This file contains function-level API only (registry, decorator and binding).""",
    "malight/fonts.py": """\
The single entry point for fonts in the English edition of malight, the counterpart of the
font module in the original Chinese edition, extended with embedded font files.

**Three ways to name a font, mix them freely**

```python
from malight import Malight, Font

pen = Malight("demo", width=600, height=400)

# 1) Enum (recommended: IDE completion, a typo fails fast, no font names to memorise)
pen.text(300, 60,  "SimHei heading", font=Font.SIMHEI, font_size=32)

# 2) Family name as a string - works for any installed font
pen.text(300, 120, "Microsoft YaHei", font="Microsoft YaHei", font_size=28)

# 3) A font file (.ttf/.otf/.ttc/.woff - base64-embedded into the SVG, so it
#    survives moving machines and sharing; PDF/PNG export looks the same)
pen.text(300, 180, "KaiTi", font=r"C:\\Windows\\Fonts\\simkai.ttf", font_size=28)
```

Why enums are recommended: when a family name is wrong the browser silently falls back to
its default font - no error, and hard to trace. An enum gives you completion while you type
and fails loudly when the name is misspelled.

Handy helpers:

```python
Font.SIMHEI.value             # "SimHei"     the family name
Font.of("SimHei")             # Font.SIMHEI  string -> enum
Font.list_names()             # every enum member name
Font.is_font_file("a.ttf")    # True         is this a font file?
Font.family_of("c:/a.ttf")    # "a"          guess the family name from a file
find_font_file("KaiTi")       # full path to a font file (None when not found)
```

**Font-file directory convention: `assets/fonts`**. Drop `.ttf` / `.otf` / `.ttc`
files into the in-package `malight/assets/fonts/` folder (ships with the package)
or into your own `<project>/assets/fonts/`; `find_font_file` looks there **first**,
before the system font folders, so fonts travel with the project and nothing goes
missing on another machine. The `MALIGHT_FONTS` environment variable (entries
separated by `;`) adds more folders. Lookups go through `malight.asset_path` /
`malight.asset_dir`.""",
    "malight/gradients.py": """\
The counterpart of the gradient module in the original Chinese edition.
Gradient definitions go into `<defs>`, and the returned value can be used directly as a fill
or stroke colour.

Example:

```python
from malight import MagicPen
pen = MagicPen("demo_gradient", width=500, height=300)

# Linear gradient: from top-left to bottom-right, red to blue
grad = pen.linearGradient((0, 0), (1, 1), "red", "blue")

# Radial gradient: a golden sun
sun = pen.radialGradient((250, 120), 90, "white", "orange")

pen.rect(50, 180, 400, 80, fill_color=grad)
pen.circle(250, 120, 90, fill_color=sun)
pen.finish()
```""",
    "malight/i18n.py": """\
malight's errors, notices and export messages are **English by default**; one line switches
them to Chinese:

```python
import malight
malight.set_language("zh")      # switch to Chinese
malight.set_language("en")      # back to English, the default
```

If you would rather not touch the code, use the environment variable - handy for CI and
command-line scripts:

```bash
set MALIGHT_LANG=zh             # Windows
export MALIGHT_LANG=zh          # macOS / Linux
set MALIGHT_LANG=auto           # follow the system language
```

Precedence: `set_language()` > `MALIGHT_LANG` > the default `"en"`.

Only **runtime messages** are affected, never API names or returned data: machine-readable
values such as `kind` and `cmd` are always English ASCII so programs can rely on them.

Adding your own language (Traditional Chinese, Japanese, ...):

```python
from malight import i18n

i18n.add_messages("fr", {"export.ok": "[malight] {kind} export OK{tail} -> {path} [{size}]"})
malight.set_language("fr")      # untranslated keys fall back to English
```

Temporary switch, with no global side effect (useful in tests or doc generation):

```python
with malight.use_language("zh"):
    pen.export_png()            # these lines print Chinese
```""",
    "malight/tools.py": """\
The shared part of the utility modules in the original Chinese edition: general helpers,
image processing, cairosvg helpers, path helpers and filter helpers.

Example:

```python
from malight.tools import image_to_data_uri, wave_line_points
uri = image_to_data_uri("photo.jpg")             # embed an image as a base64 data URI
pts = wave_line_points((0, 0), (200, 0), 20, 4)  # vertices of a wave line
```""",
    "malight/svg_backend.py": """\
A minimal SVG element tree and serialiser, replacing the original dependency on svgwrite.
The in-house backend exists because it supports every attribute in the SVG spec losslessly
(fill-rule, transform, filter, marker, SMIL animation and so on) and avoids svgwrite's
validation and rewriting of some attributes.

You normally never import this module; the element classes use it internally.

Example (internal debugging only):

```python
from malight.svg_backend import SvgNode
node = SvgNode("circle", {"cx": 10, "cy": 20, "r": 5, "fill": "red"})
print(node.to_xml())     # <circle cx="10" cy="20" r="5" fill="red"/>
```""",

    # ------------------------------------------------------------------
    # elements 包
    # ------------------------------------------------------------------
    "malight/elements/base.py": """\
- `_paint`          normalises colour arguments
- `_fmt_points`     formats a point list
- `_fmt_transform`  formats a transform list
- `_num`            converts an attribute value to float (tolerates forms like `"120px"`)
- `Element`         base class of every element: style / transform / animation / z-order /
                    clone / bounding box""",
    "malight/elements/path.py": """\
Path commands map one-to-one onto SVG path `d` syntax: move / line / horizontal and
vertical lines / quadratic and cubic Beziers / arc / close. It also supports boolean
operations, transforms, smoothing and turtle-style turning (forward, turn, rounded
corners).""",

    # ------------------------------------------------------------------
    # pathkit 包
    # ------------------------------------------------------------------
    "malight/pathkit/editor.py": """\
A helper for `PathElement`: it turns "a string of d commands" into **points you can see and
edit**.

The problem it solves: paths are hard to work with - you cannot tell how many points a curve
has, where they are, or what dragging one does. This class does four things:

1. **Look**: `describe()` prints every segment's start point, end point and control points;
   `anchors` / `controls` hand you all anchor and control-point objects.
2. **Edit**: `move_anchor()` / `move_control()` drag any point and write the change back
   into the path automatically. Pass `link_handles=True` to `move_anchor()` and the
   control points attached to that side of the anchor travel with it, so the tangent
   direction is preserved instead of the curve suddenly kinking.
3. **Add / remove**: `insert_anchor()` adds a point on the curve without changing its
   shape, `remove_anchor()` merges points.
4. **Visualise / persist**: `show()` draws the anchors and handles on the canvas, the way a
   pen tool does; `save_json()` / `load_json()` export the points, let you edit them and
   read them back.

Example:

```python
from malight import Malight
from malight.pathkit import PathEditor

pen = Malight("demo", width=600, height=400)
p = pen.path(fill_color="none", stroke_color="#e63946", stroke_width=3)
p.move_to(60, 300)
p.cubic_to((120, 80), (260, 80), (320, 300))
p.quad_to((420, 120), (520, 300))

ed = PathEditor(p)          # or p.editor()
print(ed.describe())        # 1) inspect the structure
ed.anchors[1].move_to(200, 60)         # 2) drag an anchor
ed.controls[0].move_by(0, -30)         #    drag a control point
ed.insert_anchor(1, 0.5)               # 3) add an anchor at the middle of a curve
ed.show()                              # 4) mark every point on the canvas

pen.finish()
```""",
    "malight/pathkit/htmleditor.py": """\
`PathEditor` can only change coordinates from inside Python: edit, render, look, edit again.
This class adds the missing **hand** - it exports the same path as **one self-contained
.html file** where you drag anchors and handles with the mouse while the d string and a
ready-to-paste malight snippet update live on the right.

The exported page is **dependency-free and fully offline** (no CDN, no framework, no build
step). Double-click it and it works; you can also just send it to someone. The page carries
its own English / Chinese switch.

Three ways to use it:

1. **Edit a path you already drew**
   Build it with `p = pen.path(...)`, then `PathHTMLEditor(p).save("edit.html")`.
2. **Start from a d string**
   `PathHTMLEditor(d="M20,200 C80,40 180,40 240,200").save("edit.html")`.
3. **Continue from Python** (together with `PathEditor`)
   `ed.save_json("points.json")` -> drag in the page -> download points.json ->
   `ed.load_json("points.json")`. The downloaded JSON uses exactly the same structure as
   `PathEditor.to_dict()`, so it loads straight back.

What the page can and cannot do:

* Can: drag anchors, drag handles, an "anchor moves its handles" toggle, double-click a
  segment to insert an anchor at its midpoint, arrow-key nudging (Shift moves 10 px),
  reset, download the point JSON, copy the d string and the code.
* Cannot: write back into a running Python process - what you change in the browser lives
  only in the page's own data. For a closed loop use option 3 above and round-trip the JSON.
* Arcs (`A`) cannot have an anchor inserted - the same limitation as `PathSegment.split()`.

With "anchor moves its handles" ticked, the anchor and the handle on that side shift by the
same amount, so the curve does not suddenly kink - this is exactly
`PathEditor.move_anchor(..., link_handles=True)`. Unticked, only the anchor itself moves,
matching the default `move_anchor()`.

The page's JS and the Python code are **two separate implementations**, so
`tools/check_htmleditor_js.py` lifts the page's JS out, runs it under Node and checks
anchor by anchor that both produce an identical d string (in both linking modes). That
script also has a `--self-test` which injects 8 genuine mistakes to prove the comparisons
are not vacuously passing.

The page's UI strings come from the `html.*` entries in `malight.i18n`, pulled in for both
en and zh via `use_language()`, so a single file reads correctly in either language.""",
    "malight/pathkit/parser.py": """\
Used internally by malight. It parses a `d` string into one `PathSegment` per path command,
normalises every coordinate to **absolute** values and expands the shortcut commands so that
inspecting and editing them later is straightforward:

- `H` / `V` (horizontal and vertical lines) -> expanded to `L`
- `S` (smooth cubic Bezier)                 -> expanded to `C`, first control point computed
- `T` (smooth quadratic Bezier)             -> expanded to `Q`, control point computed
- relative commands (lowercase m / l / c ...) -> converted to absolute coordinates

That way every curve has an explicit start point, end point and control points - the same
points you see with the pen tool in Illustrator or Figma.

Example:

```python
from malight.pathkit import parse_path_d
segs = parse_path_d("M0,0 C10,20 30,20 40,0 L80,0 Z")
for s in segs:
    print(s)
```""",
    "malight/pathkit/point.py": """\
`PathPoint` is **one draggable point** on a path. There are two kinds:

- **anchor**: a curve's start, end or corner - the solid square in a pen tool
- **control point**: the tip of a Bezier handle - dragging it changes the curvature

This is the "see where a curve starts, ends and bends" capability of the original Chinese
edition's path element, exposed here as an ordinary object you can read and modify.

Example:

```python
from malight.pathkit import PathEditor

ed = PathEditor(path)

# Look: print each point's type and coordinates
for pt in ed.anchors:
    print(pt)                  # <anchor#0 (50, 50)>

# Edit: drag points directly - written back into the path, no manual apply
ed.anchors[1].move_to(220, 80)
ed.controls[0].move_by(10, -20)
```""",
    "malight/pathkit/segment.py": """\
`PathSegment` is **one segment** of an SVG path (one path command). Coordinates are
normalised to absolute values, and every curve states its start point, end point and control
points explicitly.

It is the smallest unit through which `PathEditor` looks inside a path:

- `M` move (start point, draws nothing)
- `L` line
- `C` cubic Bezier (two control points)
- `Q` quadratic Bezier (one control point)
- `A` arc (rx / ry / rotation / large-arc / sweep)
- `Z` close

Example:

```python
from malight.pathkit import parse_path_d

seg = parse_path_d("M0,0 C0,80 100,80 100,0")[1]
print(seg.kind)          # "cubic"
print(seg.start)         # (0.0, 0.0)   start point
print(seg.ctrls)         # ((0.0, 80.0), (100.0, 80.0))  the two control points
print(seg.end)           # (100.0, 0.0) end point
print(seg.length())      # curve length
print(seg.point_at(0.5)) # coordinates at 50% along the curve
```""",
}


# ===========================================================================
# 指纹：中文正文一变，就该重新审一遍英文
# ===========================================================================
#: 生成方（gen_docs.py）用同一函数算中文正文的指纹；与下表不一致 = 可能过期。
SOURCE_HASH = {
    "malight/board/containers.py": "4afbf5101136",
    "malight/board/core.py": "1598797ae086",
    "malight/board/debug.py": "86b1c6315e13",
    "malight/board/effects.py": "46c77bff3e7c",
    "malight/board/filters.py": "5e95f9faef26",
    "malight/board/fx.py": "51463a8875b7",
    "malight/board/gradients_mixin.py": "ae97117a3a20",
    "malight/board/images.py": "f1a5ca2518dd",
    "malight/board/layout.py": "5ef6c1869239",
    "malight/board/paths.py": "c663a2da41e6",
    "malight/board/repeat.py": "9cc80c70ed20",
    "malight/board/shapes.py": "c02ee9513b9e",
    "malight/board/style.py": "c1e62374609a",
    "malight/board/text_board.py": "38a278e1093c",
    "malight/compat.py": "e786d0d08cb9",
    "malight/definitions.py": "8c7b9d91bdab",
    "malight/elements/base.py": "2bd99dcb7486",
    "malight/elements/path.py": "365412591266",
    "malight/ext.py": "1d453d9ce210",
    "malight/fonts.py": "3f9b09fe4ae9",
    "malight/gradients.py": "c4d43bb4f27d",
    "malight/i18n.py": "c3db36a0bce5",
    "malight/page.py": "b72609b798f0",
    "malight/pathkit/editor.py": "ccd83faea77f",
    "malight/pathkit/htmleditor.py": "eed953017fe1",
    "malight/pathkit/parser.py": "609d2521aca4",
    "malight/pathkit/point.py": "8ec8aaa5e193",
    "malight/pathkit/segment.py": "2cf7001e1ec5",
    "malight/svg_backend.py": "af78196ced11",
    "malight/tools.py": "aa065dd96daa",
}

_STAMP_START = "SOURCE_HASH = {"
_STAMP_END = "}\n"


def normalize(text):
    """指纹用文本：折叠空白、去掉行尾，避免因为换行格式变化误报。"""
    return "\n".join(l.rstrip() for l in (text or "").strip().splitlines())


def body_hash(text):
    """中文正文的 sha1（取前 12 位）—— 用来判断英文译文是否可能过期。"""
    return hashlib.sha1(normalize(text).encode("utf-8")).hexdigest()[:12]


def stamp(dry_run=False):
    """按当前源码重算指纹，写回本文件的 SOURCE_HASH。"""
    sys.path.insert(0, HERE)
    import gen_docs                                     # 延迟导入，避免循环

    by_key = {}
    for path in gen_docs.gather_modules():
        key = os.path.relpath(path, ROOT).replace(os.sep, "/")
        if key not in BODY_EN:
            continue
        doc = gen_docs.ast.get_docstring(gen_docs.ast.parse(gen_docs.read_src(path)))
        _title, _en, body = gen_docs.module_doc_parts(doc)
        by_key[key] = body_hash(body)

    missing = sorted(k for k in BODY_EN if k not in by_key)
    stale = sorted(k for k, v in by_key.items() if SOURCE_HASH.get(k) != v)

    lines = ["SOURCE_HASH = {"]
    for key in sorted(by_key):
        lines.append('    "%s": "%s",' % (key, by_key[key]))
    lines.append("}")
    block = "\n".join(lines) + "\n"

    if not dry_run:
        src = io.open(__file__, encoding="utf-8", newline="").read()
        start = src.index(_STAMP_START)
        end = src.index("\n}\n", start) + len("\n}\n")
        io.open(__file__, "w", encoding="utf-8", newline="").write(
            src[:start] + block + src[end:])
    return stale, missing


def check():
    """返回 ``(过期列表, 缺译文列表)``。"""
    sys.path.insert(0, HERE)
    import gen_docs

    stale, need = [], []
    for path in gen_docs.gather_modules():
        key = os.path.relpath(path, ROOT).replace(os.sep, "/")
        doc = gen_docs.ast.get_docstring(gen_docs.ast.parse(gen_docs.read_src(path)))
        _title, _en, body = gen_docs.module_doc_parts(doc)
        has_cn = bool(re.search(r"[\u4e00-\u9fff]", body))
        if key not in BODY_EN:
            if has_cn:
                need.append(key)
            continue
        if not has_cn:
            stale.append(key + "（中文正文已改为纯英文，可删掉本条目）")
        elif SOURCE_HASH.get(key) != body_hash(body):
            stale.append(key + "（中文正文变了，英文译文可能过期）")
    return stale, need


def main(argv):
    if "--stamp" in argv:
        stale, missing = stamp(dry_run=False)
        print("已更新 %d 条指纹；过期 %d 条，缺译文 %d 条"
              % (len(BODY_EN), len(stale), len(missing)))
        for s in stale:
            print("   过期:", s)
        for m in missing:
            print("   缺译文:", m)
        return 0
    stale, need = check()
    if not stale and not need:
        print("英文正文译文表正常：%d 条，指纹全部匹配" % len(BODY_EN))
        return 0
    for s in stale:
        print("过期 / STALE:", s)
    for n in need:
        print("缺译文 / MISSING:", n, "（正文含中文但未登记英文）")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
