<!-- 本文件由 tools/gen_docs.py 从源码自动生成，请勿手改。
     要改内容请改同目录的 tools.py 里的文档字符串，然后重跑生成器。 -->

# tools.py

**简体中文** ｜ [English](tools.en.md) ｜ [← 返回 README](../README.md)

工具集（tools）—— 图像/导出/几何/滤镜/字体辅助

对应中文版《神笔码靓》的 通用工具集/图像处理工具/cairosvg工具集/
路径工具集/滤镜工具集 等模块的公共部分。

示例

```python
from malight.tools import image_to_data_uri, wave_line_points
uri = image_to_data_uri("photo.jpg")            # 图片转 base64 内嵌
pts = wave_line_points((0, 0), (200, 0), 20, 4) # 波浪线顶点
```


---

## 类与方法

### 函数

| 函数 | 说明 |
|---|---|
| `set_color` | 打开/关闭终端颜色；`None` 表示回到自动判断。 |
| `color_enabled` | 当前是否给终端输出上色（按 stdout 判断）。 |
| `paint` | 给一段文字加 ANSI 样式（未启用颜色时原样返回）。 |
| `paint_path` | 让一行「文件已保存」提示更醒目：整行加粗、其中的路径绿色。 |
| `print_color` | 打印一行彩色消息（未启用颜色时原样打印）。 |
| `print_red` | 用红色打印一行消息。 |
| `print_green` | 用绿色打印一行消息。 |
| `print_yellow` | 用黄色打印一行消息。 |
| `print_blue` | 用蓝色打印一行消息。 |
| `print_magenta` | 用紫红色打印一行消息（`purple` 与之同色）。 |
| `print_cyan` | 用青色打印一行消息。 |
| `print_white` | 用白色打印一行消息。 |
| `print_grey` | 用灰色打印一行消息（`gray` 同义）。 |
| `asset_path` | 找一个包内/项目资源文件，返回绝对路径；找不到返回 None。 |
| `asset_dir` | 找一个资源**目录**（查找顺序同 :func:`asset_path`）；不存在返回 None。 |
| `human_size` | 把文件大小格式化为易读字符串（如 "88.3 KB"）。 |
| `report` | 统一打印「导出成功 + 全路径 + 大小」，方便复制路径直接用；全路径既是返回值， 也是各导出函数的返回值。 |
| `image_to_data_uri` | 本地图片转 base64 data URI（内嵌进 SVG，离线可用）。 |
| `image_size` | 获取图片真实宽高（需要 Pillow，读取失败返回 (0, 0)）。 |
| `linked_path` | 把本地资源路径转成「SVG 里引用的路径」（不内嵌时用）。 |
| `get_svg_size` | 读取 SVG 文件的宽高（解析 width/height 或 viewBox）。 |
| `scale_svg_file` | 等比缩放 SVG 文件并另存（对应中文版 `缩放SVG图片`）。 |
| `import_svg_as_nodes` | 把 SVG 文件解析为节点组（供绘图板 import_svg_as_group 使用）。 |
| `read_svg_text` | 读 SVG 文件的源文本（UTF-8 优先，退回 GBK，去 BOM）。 |
| `svg_text_to_data_uri` | SVG 文本转 `data:image/svg+xml;base64,...`（内嵌用）。 |
| `svg_intrinsic_size` | 从 SVG 文本读内在尺寸 (宽, 高)，读不到返回 (0, 0)。 |
| `svg_colors` | 列出 SVG 文本里用到的颜色（归一成小写 `#rrggbb`，按首次出现顺序去重）。 |
| `replace_svg_color` | 按「颜色」替换 SVG 文本里的颜色（同一个 SVG 文件换色复用）。 |
| `walk_svg_nodes` | 深度优先遍历节点树（含自身）。 |
| `svg_node_colors` | 列出节点树里用到的颜色（归一成小写 `#rrggbb`，按首次出现顺序去重）。 |
| `replace_svg_node_color` | 在**节点树**里按颜色替换（`import_svg_as_group` / `import_svg_as_symbol` 拿到的节点）。 |
| `replace_svg_node_text` | 在**节点树**里做纯字符串替换：标签名 + 节点文本 + 所有属性值。 |
| `svg_transform_points` | 把一组点按 SVG 的 transform 映射一遍。 |
| `has_cairosvg` | 本机是否装了 cairosvg（英文版新增：用于自动挑选导出引擎）。 |
| `export_png_cairo` | 用 cairosvg 把 SVG 渲染为 PNG（对应中文版 `生成PNG` 的 cairosvg 方式）。 |
| `export_pdf_cairo` | 用 cairosvg 把 SVG 转为 PDF（对应中文版 `生成PDF`）。 |
| `find_chrome` | 查找本机 Chrome 可执行文件（英文版新增）。 |
| `export_pdf_chrome` | 用 Chrome 无头模式把 SVG 打印为 PDF（英文版新增）。 |
| `export_png_chrome` | 用 Chrome 无头模式把 SVG 截图为 PNG（英文版新增，支持 SVG filter）。 |
| `export_docx_from_pdf` | 把 PDF 转为 DOCX（需要 pdf2docx 库，对应中文版 `生成DOCX`）。 |
| `arrow_path_points` | 计算箭头三角形的三个顶点（对应中文版 `获取箭头路径` 的核心）。 |
| `wave_line_points` | 计算正弦波浪线的采样顶点（对应中文版 `画波浪线` 的核心）。 |
| `regular_polygon_points` | 正 N 边形顶点（对应中文版 `N边形路径`）。 |
| `star_points` | N 角星顶点（外角 + 内角交替，对应中文版 `N角星路径`）。 |
| `heart_points` | 爱心曲线顶点（对应中文版 `爱心路径`）。 |
| `point_list_bbox` | 顶点列表包围盒。 |
| `create_blur_filter` | 创建高斯模糊滤镜定义（对应中文版 `滤镜工具集.模糊滤镜`）。 |
| `create_drop_shadow_filter` | 创建投影滤镜（英文版新增能力，对应中文版未提供的 drop-shadow）。 |
| `create_glow_filter` | 创建发光滤镜（英文版新增能力）。 |
| `text_width` | 估算文字宽度（需要 Pillow 加载系统字体；失败时按 1.0x 字号估算）。 |
| `find_font_file` | 在 Windows 字体目录中查找字体文件（对应中文版 `字体查找器` 的简化版）。 |
| `text_to_path_d` | 文字转路径（对应中文版 `文字转路径`，需要 fontTools 库）。 |

---

## 完整示例

在 PyCharm 里点绿色三角直接运行，或命令行：`python malight/tools.py`

```python
if __name__ == "__main__":
    import malight

    # --- 1) 彩色消息：八种颜色各有一个同名函数 ---
    malight.print_red("错误：导出失败")
    malight.print_green("成功：已导出 3 个文件")
    malight.print_yellow("警告：字体缺失，已回退默认字体")
    malight.print_blue("信息：正在用 Chrome 引擎")
    malight.print_magenta("紫红色，与 purple 同色")
    malight.print_cyan("青色，适合打印调试信息")
    malight.print_white("白色，普通提示")
    malight.print_grey("灰色，可以忽略")

    # --- 2) 通用写法：颜色与样式随你组合 ---
    malight.print_color("加粗的普通红色",
                        color="red", bold=True, bright=False)
    malight.print_color("写进 stderr，并按 stderr 判断上色",
                        color="yellow", file=sys.stderr)

    # --- 3) paint 只返回带色字符串，不打印 ---
    print("paint ->", malight.paint("styled text", color="green", bold=True))

    # --- 4) 重定向到磁盘文件时自动不上色（运行窗口仍上色），也可手动关闭 ---
    malight.set_color(False)
    malight.print_red("这行没有转义码")
    malight.set_color(None)                    # None 交回自动判断

    # --- 5) 中文别名（与中文版《神笔码靓》同名）与英文名指向同一函数 ---
    print("color_enabled() ->", malight.color_enabled())
```

---

## 同级模块

[compat](compat.zh.md) ｜ [definitions](definitions.zh.md) ｜ [ext](ext.zh.md) ｜ [fonts](fonts.zh.md) ｜ [gradients](gradients.zh.md) ｜ [i18n](i18n.zh.md) ｜ [page](page.zh.md) ｜ [svg_backend](svg_backend.zh.md)
