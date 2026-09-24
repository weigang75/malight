# assets/fonts —— 字体文件目录 / font files directory

把字体文件放这里，`find_font_file()` 会**优先**使用它们（其次才是系统字体目录）。
Put font files here; `find_font_file()` looks here **first**, before the system font folders.

## 放什么 / What goes here

```
assets/fonts/
├── my_brand.ttf        # .ttf / .otf / .ttc / .otc / .woff / .woff2 / .eot
└── ...
```

- **源码工程 / sdist** 里的这份 `malight/assets/fonts/` 随源码分发；**pip 安装的 wheel
  不带这个空目录**（wheel 只分发 `assets/images/` 下的预览图）—— 字体是使用者自己的
  资产，装完想放字体，请在**项目里**建 `<项目>/assets/fonts/`，或设 `MALIGHT_FONTS`。
  The copy in the source tree / sdist ships with the source; an installed **wheel does
  not include this empty folder** (only the preview PNGs under `assets/images/`). To add
  your own fonts, create `<project>/assets/fonts/` in your project or set `MALIGHT_FONTS`.
- **项目里**也可以建一个 `<项目>/assets/fonts/` 放项目自己的字体 ——
  查找顺序：包内 → 从当前目录逐级向上找 `<目录>/assets/fonts` → 系统字体目录。
  A project may also keep its own `<project>/assets/fonts/`. Lookup order: in-package →
  walk up from the current directory for `<dir>/assets/fonts` → system font folders.

## 自带字体 / Bundled fonts

仓库里已带几个可直接用的字体文件（用法见下方示例与 `examples/demo_fonts.py`）：

| 文件 / File | 字体族 / Family | 内容 / Content |
|---|---|---|
| `Android.ttf` | Droid Sans Fallback | 中英日韩等 fallback 文本字体（Apache 2.0）/ CJK fallback text font |
| `Digital-7Mono.TTF` | Digital-7 | 七段数码管风格数字 / seven-segment digit style |
| `MusicStaff.ttf` | akvo | 五线谱音符符号（映射在字母键位）/ music notation glyphs on letter keys |
| `mahjong.ttf` | Mahjong | 麻将牌面（映射在 A-Z）/ mahjong tiles mapped to A-Z |

```python
from malight import find_font_file, Malight

path = find_font_file("MusicStaff")     # 命中包内 assets/fonts/MusicStaff.ttf
pen = Malight("demo", width=600, height=400)
pen.text(300, 200, "ABCDEFG", font=path, font_size=32)   # 只内嵌用到的字
```

## 怎么用 / How to use

```python
from malight import find_font_file, Malight, FontEmbed

path = find_font_file("MyFont")          # 找到 assets/fonts/my_brand.ttf
pen = Malight("demo", width=600, height=400,
              fonts=FontEmbed.SUBSET)    # 默认就是它，写出来只为强调
pen.text(300, 200, "你好 Hello", font=path, font_size=32)
```

- 直接传**文件路径**给 `font=`，字体就会随 SVG 走 —— 换电脑、发给别人都不会掉
  字体。默认只内嵌画面上**实际用到的字**（自动子集化，5 MB 级中文字体通常降到
  几 KB），不用把文字再写第二遍。
  Passing the file path to `font=` makes the font travel with the SVG. By default
  only the **glyphs actually drawn** are embedded (automatic subsetting: a 5 MB CJK
  font usually drops to a few KB) - no need to repeat your text anywhere.
- 想要别的行为就用 `pen.set_embed(fonts=...)`：
  `FontEmbed.EMBED` 整份内嵌（最保险）/ `FontEmbed.LINK` 只写本地路径（文件最小，
  但字体必须留在原处）。
  Other behaviours: `pen.set_embed(fonts=...)` with `FontEmbed.EMBED` (whole file)
  or `FontEmbed.LINK` (path only - smallest, but the font must stay put).
- 环境变量 `MALIGHT_FONTS` 可追加更多字体目录（用 `;` 分隔）。
  Extra folders: the `MALIGHT_FONTS` environment variable (split with `;`).
- 查找入口：`malight.asset_dir("fonts")` / `malight.asset_path("fonts", "my.ttf")`。
  Entry points: `malight.asset_dir("fonts")` / `malight.asset_path("fonts", "my.ttf")`。

> 字体文件请确认授权允许再分发（很多商用字体不允许）。
> Make sure the font licence allows redistribution before committing it here.
