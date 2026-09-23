# -*- coding: utf-8 -*-
"""
扩展机制演示 —— 用 @toolkit 把自定义工具包挂进绘图板。

运行: python demo_ext.py   输出到 ../output/ext_demo.svg
以后给「神笔码靓」增加图表包/图标包/特效包，都可以这样扩展，
不需要修改 malight 源码。
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from malight import Malight
from malight.ext import toolkit, list_toolkits


# ------------------------------------------------------------------
# 第 1 步：工具包作者写一个类，用 @toolkit("注册名") 注册
# （第一个参数 self 就是绘图板 pen）
# ------------------------------------------------------------------
@toolkit("charts")
class ChartToolkit:
    """简易图表工具包（演示扩展机制用）。"""

    def bar_chart(self, data, x, y, w, h, color="#4e79a7",
                  labels=None, title=None):
        """柱状图：data 为数值列表，(x, y) 为左上角，w/h 为宽高。"""
        vmax = max(data) or 1
        bw = w / len(data)
        for i, v in enumerate(data):
            bh = h * v / vmax
            self.rect(x + i * bw + bw * 0.15, y + h - bh,
                      bw * 0.7, bh, fill_color=color)
            if labels:
                self.text(x + i * bw + bw / 2, y + h + 22, str(labels[i]),
                          font_size=14, h_align="middle")
        if title:
            self.text(x + w / 2, y - 18, title, font_size=18,
                      h_align="middle")


@toolkit("badges")
class BadgeToolkit:
    """徽章工具包（演示多工具包共存）。"""

    def badge(self, cx, cy, r, text, bg="#d62828", fg="#ffffff"):
        """圆形徽章。"""
        self.circle(cx, cy, r, fill_color=bg,
                    filter=self.fx.shadow(3, 4, 3, opacity=0.35))
        self.text(cx, cy + 8, text, font_size=r * 0.9, fill_color=fg,
                  h_align="middle")


# ------------------------------------------------------------------
# 第 2 步：用户 import 后一行挂载
# ------------------------------------------------------------------
print("已注册工具包:", list_toolkits())

pen = Malight("ext_demo", width=800, height=600)
pen.set_background_color("#f8f9fa")
pen.text(400, 50, "malight 扩展机制：@toolkit + pen.use_toolkit()",
         font_size=24, fill_color="#343a40", h_align="middle")

pen.use_toolkit("charts", "badges")     # 挂载（可一次多个）

# ------------------------------------------------------------------
# 第 3 步：像原生方法一样调用
# ------------------------------------------------------------------
pen.bar_chart([3, 7, 5, 9, 6], 80, 120, 420, 300,
              labels=["一", "二", "三", "四", "五"], title="季度销量")
pen.badge(650, 200, 55, "NEW")
pen.badge(650, 380, 55, "HOT", bg="#2a9d8f")

pen.finish()
print("已生成:", pen.file_path)
