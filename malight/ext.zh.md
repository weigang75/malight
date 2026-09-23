<!-- 本文件由 tools/gen_docs.py 从源码自动生成，请勿手改。
     要改内容请改同目录的 ext.py 里的文档字符串，然后重跑生成器。 -->

# ext.py

**简体中文** ｜ [English](ext.en.md) ｜ [← 返回 README](../README.md)

ext —— malight 扩展机制（让第三方工具包无缝挂进绘图板）。

设计目标：以后给「神笔码靓」增加能力（如图表包、图标包、特效包）
不需要改 malight 源码 —— 任何包只要用 `@toolkit` 注册，
用户一行 `pen.use_toolkit("名字")` 即可把全部方法挂到绘图板上。

三个角色：
1. 工具包作者：写一个类，方法第一个参数是 pen（self），
   用 `@toolkit("注册名")` 装饰即可自动注册；
2. 用户：import 该工具包模块 → `pen.use_toolkit("注册名")`；
3. 查询：`malight.ext.list_toolkits()` 查看所有已注册工具包。

本文件只包含函数级 API（注册表 + 装饰器 + 绑定）。

---

## 类与方法

### 函数

| 函数 | 说明 |
|---|---|
| `register` | 注册一个工具包类（内部函数，一般用 @toolkit 装饰器代替）。 |
| `inspect_class` | 校验参数是否为类（内部函数）。 |
| `toolkit` | 工具包注册装饰器（推荐用法）。 |
| `list_toolkits` | 列出所有已注册工具包名。 |

---

## 同级模块

[compat](compat.zh.md) ｜ [definitions](definitions.zh.md) ｜ [fonts](fonts.zh.md) ｜ [gradients](gradients.zh.md) ｜ [i18n](i18n.zh.md) ｜ [page](page.zh.md) ｜ [svg_backend](svg_backend.zh.md) ｜ [tools](tools.zh.md)
