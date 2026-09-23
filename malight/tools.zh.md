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
| `color_enabled` | 当前是否给终端输出上色。 |
| `paint` | 给一段文字加 ANSI 样式（未启用颜色时原样返回）。 |
| `paint_path` | 让一行「文件已保存」提示更醒目：整行加粗、其中的路径绿色。 |
| `asset_path` | 找一个包内/项目资源文件，返回绝对路径；找不到返回 None。 |
| `asset_dir` | 找一个资源**目录**（查找顺序同 :func:`asset_path`）；不存在返回 None。 |
| `human_size` | 把文件大小格式化为易读字符串（如 "88.3 KB"）。 |
| `report` | 统一打印「导出成功 + 全路径 + 大小」，方便复制路径直接用；全路径既是返回值， 也是各导出函数的返回值。 |
| `image_to_data_uri` | 本地图片转 base64 data URI（内嵌进 SVG，离线可用）。 |
| `image_size` | 获取图片真实宽高（需要 Pillow，读取失败返回 (0, 0)）。 |
| `get_svg_size` | 读取 SVG 文件的宽高（解析 width/height 或 viewBox）。 |
| `scale_svg_file` | 等比缩放 SVG 文件并另存（对应中文版 `缩放SVG图片`）。 |
| `import_svg_as_nodes` | 把 SVG 文件解析为节点组（供绘图板 import_svg_as_group 使用）。 |
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

## 同级模块

[compat](compat.zh.md) ｜ [definitions](definitions.zh.md) ｜ [ext](ext.zh.md) ｜ [fonts](fonts.zh.md) ｜ [gradients](gradients.zh.md) ｜ [i18n](i18n.zh.md) ｜ [page](page.zh.md) ｜ [svg_backend](svg_backend.zh.md)
