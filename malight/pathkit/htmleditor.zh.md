<!-- 本文件由 tools/gen_docs.py 从源码自动生成，请勿手改。
     要改内容请改同目录的 htmleditor.py 里的文档字符串，然后重跑生成器。 -->

# htmleditor.py

**简体中文** ｜ [English](htmleditor.en.md) ｜ [← 返回 README](../../README.md)

路径 UI 编辑器（pathkit.htmleditor）—— PathHTMLEditor 类

`PathEditor` 只能在 Python 里改坐标：改一次、出一张图、看一眼，再改。
本类补上「手」——把同一条路径导出成**一个自我包含的 .html**，
用鼠标拖锚点与调整杆，右侧实时给出 d 串和可直接粘贴的 malight 代码。

导出的页面**零依赖、纯离线**（没有任何 CDN、框架或构建步骤），
双击就能用，也可以直接发给别人；页面里自带 中文 / English 切换。

三种用法:

1. **改一条已有路径**
   `p = pen.path(...)` 画好 → `PathHTMLEditor(p).save("edit.html")`。
2. **从 d 串开始**
   `PathHTMLEditor(d="M20,200 C80,40 180,40 240,200").save("edit.html")`。
3. **接着 Python 的进度改**（配合 `PathEditor`）
   `ed.save_json("points.json")` 存档 → 页面里拖 → 下载回 points.json
   → `ed.load_json("points.json")` 读回。
   页面下载的 JSON 与 `PathEditor.to_dict()` **同一套结构**，可以直接读回。

页面能做什么 / 不能做什么:

* 能：拖锚点、拖调整点、「锚点连动调整杆」开关、双击某段在中点插入锚点、
  **双击锚点删除该点**（浏览器原生确认框提醒，相邻两段合并为一段；复位可撤销）、
  选中锚点后**切换段线类型**（直线 L / 三次 C / 二次 Q，Q→C 精确升阶、C→Q 取
  切线交点近似）、**平滑 / 尖角锚点**（平滑锚点拖一侧调整杆时另一侧自动镜像）、
  **背景图层**（`background_svg=` 内嵌已保存的 SVG 垫底，「背景」按钮控制
  显隐、透明度滑条可调，路径叠在原图上改，所见即所得）、
  **取点模式**（「取点」开启后点画布即记录坐标，显示 x/y 与相邻两点 dx/dy/d，
  自动生成链式代码：同 y → `h_line_to`、同 x → `v_line_to`——
  对应中文版 `获取坐标点.html`）、
  右侧代码面板 **set_d / 链式 / 取点三种写法**（与 `chain_code` 同一套生成
  逻辑、回归里逐字符比对）、方向键微调（Shift 走 10 像素）、复位、
  下载点位 JSON、复制 d 串与代码。
* 不能：拖完之后**回写**正在运行的 Python 进程（浏览器里改的只是页面自己的数据）。
  要闭环就走上面第 3 种用法，用 JSON 往返。
  下载的 JSON 会带上平滑标记（`sms` / `sme` 两个附加键），
  `PathEditor.to_dict()` 读回时自动忽略，双向兼容。
* 圆弧段（A）不支持拆分锚点、也不能改类型 —— 与 `PathSegment.split()` 的限制一致。

配套便捷方法 `Malight.svg_editor(path)`：一条命令生成上面这一切——
先 `finish()` 保存 SVG，再调它，HTML 自动内嵌背景图层（对应中文版
`获取坐标点.html` 的加强版，定位 + 调路径二合一）。

「锚点连动调整杆」勾上时，锚点位移多少、挂在它这一侧的调整杆就位移多少
（曲线不会突然拐个弯）—— 这正是 `PathEditor.move_anchor(..., link_handles=True)`；
取消勾选则只动锚点本身，与默认的 `move_anchor()` 一致。

页面里的 JS 与 Python 是**两份实现**：`tools/check_htmleditor_js.py` 会把页面
那段 JS 抽出来用 Node 跑一遍，逐锚点确认两边拖出来的 d 串一模一样
（连动 / 不连动两种模式都比，「链式」「取点」代码也逐字符比对），并且脚本自带
`--self-test` —— 注入 10 处真实错法，确认比对项不是「永远为空所以永远通过」。

主页面的 UI 文案取自 `malight.i18n` 的 `html.*` 词条，
导出时按 `use_language()` 取 en / zh 两套内嵌进页面，所以一份文件两种语言都能看。

---

## 类与方法

### 函数

| 函数 | 说明 |
|---|---|
| `chain_code` | 把段列表转成 malight **链式** Python 代码。 |

### `PathHTMLEditor`

把一条路径导出成可拖拽的单文件 HTML 编辑器。

| 方法 | 说明 |
|---|---|
| `segments()` | 当前的线段列表（每次调用重新解析，改过 path 的 d 之后能拿到新的）。 |
| `to_dict()` | 转成可 JSON 序列化的数据（结构与 `PathEditor.to_dict()` 一致）。 |
| `render()` | 生成完整的 HTML 文本（自我包含，可直接写盘或塞进任何地方）。 |
| `save(file)` | 把页面写到磁盘，返回绝对路径。 |

---

## 完整示例

在 PyCharm 里点绿色三角直接运行，或命令行：`python malight/pathkit/htmleditor.py`

```python
if __name__ == "__main__":
    import os

    from malight import Malight, ColorName
    from malight.pathkit import PathEditor, PathHTMLEditor

    _out = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        "..", "..", "output"))
    os.makedirs(_out, exist_ok=True)

    # -----------------------------------------------------------------
    # 1) 造一条路径：起笔 + 直线 + 三次贝塞尔 + 二次贝塞尔
    # -----------------------------------------------------------------
    pen = Malight(os.path.join(_out, "demo_path_htmleditor"), width=660, height=430)
    pen.set_background_color(ColorName.WHITESMOKE)
    p = pen.path(fill_color="none", stroke_color=ColorName.DARKSLATEGRAY,
                 stroke_width=3)
    p.move_to(60, 320)
    p.line_to(150, 190)
    p.cubic_to((210, 80), (320, 80), (380, 190))
    p.quad_to((450, 280), (560, 210))

    # -----------------------------------------------------------------
    # 2) 从 PathElement 导出：画布尺寸默认跟随绘图板（660x430）
    # -----------------------------------------------------------------
    ed = PathHTMLEditor(p)
    print("画布尺寸 :", ed.width, "x", ed.height)
    print("段数     :", len(ed.segments()))
    print("d 串     :", ed.to_dict()["d"][:56], "...")

    # 3) 落盘：双击 output/path_editor.html 就能打开拖点
    ed.save(os.path.join(_out, "path_editor.html"))

    # -----------------------------------------------------------------
    # 4) 只给 d 串也能用（不需要绘图板，适合处理别处拿来的路径）
    # -----------------------------------------------------------------
    bare = PathHTMLEditor(d="M40,160 C40,40 200,40 200,160 Z", width=260, height=220)
    bare.save(os.path.join(_out, "path_editor_from_d.html"))
    print("从 d 导出 :", bare)

    # -----------------------------------------------------------------
    # 5) 接着 PathEditor 的进度来：存档 -> 页面里拖 -> 下载 points.json 读回
    #    页面下载的 JSON 与 PathEditor.to_dict() 同一套结构，可直接 load_json
    # -----------------------------------------------------------------
    pe = PathEditor(p)
    pe.move_anchor(1, 160, 170)                    # 先在 Python 里挪一个锚点
    from_points = PathHTMLEditor(points=pe.to_dict())
    print("点位来源  :", len(from_points.segments()), "段")
    print("两条来源  :", from_points.to_dict()["d"] == pe.to_d())
    from_points.save(os.path.join(_out, "path_editor_from_points.html"))

    # -----------------------------------------------------------------
    # 6) 链式代码：页面「链式」页签展示的就是这套格式
    #    与 JS 侧 chainCode() 互为镜像，Node 闸门逐字符比对
    #    chainCode(); compared character by character in the Node gate
    # -----------------------------------------------------------------
    from malight.pathkit.htmleditor import chain_code

    print("链式代码  :")
    print(chain_code(ed.segments(), ed.width, ed.height, ed.fill_color,
                     ed.stroke_color, ed.stroke_width))

    # -----------------------------------------------------------------
    # 7) 页面是自我包含的：没有 CDN、没有框架，离线双击即用
    # -----------------------------------------------------------------
    html = ed.render()
    # 占位符左右各写一份
    # 只写中文半边的话，英文页会取到 "bytes".format(n)，数字被静默吞掉
    _size = len(html.encode("utf-8"))
    print("页面体积  :", "{:,} 字节".format(_size, _size))
    print("离线可用  :", "http://" not in html and "https://" not in html)

    # 第二条路径：页面下拉里就有两条可选
    p2 = pen.path(fill_color="none", stroke_color=ColorName.STEELBLUE,
                  stroke_width=2)
    p2.move_to((80, 80)).line_to((220, 80)).line_to((150, 170)).close()

    pen.finish()

    # -----------------------------------------------------------------
    # 8) 一条命令生成编辑器专用 HTML
    #    内嵌刚保存的 SVG 作背景，调路径 + 取点二合一
    #    background; path editing + point picking in one page
    #    不传 path 会收集画面上全部路径，页面下拉逐条编辑
    #    board's paths are collected and the page offers a selector
    # -----------------------------------------------------------------
    print("编辑器页面 :", pen.svg_editor())
```

---

## 同级模块

[editor](editor.zh.md) ｜ [parser](parser.zh.md) ｜ [point](point.zh.md) ｜ [segment](segment.zh.md)
