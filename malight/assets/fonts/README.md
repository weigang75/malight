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
pen.text(300, 200, "ABCDEFG", font=path, font_size=32)   # 自动 base64 内嵌
```

## 怎么用 / How to use

```python
from malight import find_font_file, Malight

path = find_font_file("MyFont")          # 找到 assets/fonts/my_brand.ttf
pen = Malight("demo", width=600, height=400)
pen.text(300, 200, "你好 Hello", font=path, font_size=32)   # 自动 base64 内嵌
```

- 直接传**文件路径**给 `font=` 会把字体 base64 内嵌进 SVG —— 换电脑、发给别人
  都不会掉字体；大字体建议先用 `subset_font()` 子集化。
  Passing the file path to `font=` embeds the font (base64) into the SVG, so it
  survives on other machines; subset large fonts with `subset_font()` first.
- 更多目录：环境变量 `MALIGHT_FONTS`（用 `;` 分隔）。
  Extra folders: the `MALIGHT_FONTS` environment variable (split with `;`).
- 查找入口：`malight.asset_dir("fonts")` / `malight.asset_path("fonts", "my.ttf")`。
  Entry points: `malight.asset_dir("fonts")` / `malight.asset_path("fonts", "my.ttf")`.

> 字体文件请确认授权允许再分发（很多商用字体不允许）。
> Make sure the font licence allows redistribution before committing it here.
