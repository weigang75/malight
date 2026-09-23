# -*- coding: utf-8 -*-
"""
棋类样例 1：中国象棋（Xiangqi / Chinese Chess）—— 继承绘图板的写法
====================================================================

按「Python超人/三月三」神笔码靓原版《中国象棋制作》的布局 1:1 移植：
A4 纵向页面，棋盘居中（8 列 x 9 行，楚河汉界断开），黑子两行在上、
红子两行在下交错陈列。棋子文字保留 malight 的 `fx_engrave()` 雕刻
凹陷滤镜（上/左内缘压深、下/右内缘提亮，像刻进木头里）。

Ported 1:1 from the original MagicPen-CN class `中国象棋制作`: an A4
portrait sheet with the board (8 x 9, split by the river) centred, black
pieces staggered in two rows on top and red pieces in two rows below.
The piece glyphs keep malight's `fx_engrave()` carved-in filter.

布局公式与原版一致 / Layout formulas match the original::

    单元格宽 = (宽 - 左边距 - 右边距) // 8
    棋盘起点 Y = (高 - 单元格宽 * 9) / 2 + 位移Y
    棋子行距 = 字号 * 1.13，上排错开 0.25 格、下排错开 0.75 格

运行 / Run::

    python examples/board_games/chinese_chess.py
    # 生成 output/chinese_chess.svg 与 output/chinese_chess.png
"""

import os as _os, sys as _sys

_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))))

from malight import Malight, Color, Font, PaperSize, TextHAlign, TextVAlign, PNGMode


class ChineseChess(Malight):
    """中国象棋棋谱页（继承 Malight 绘图板，对应原版 `中国象棋制作` 类）。

    A xiangqi sheet subclassing the Malight board (the CN original
    subclasses its drawing board the same way).

    :param file_path: 输出文件名（相对路径自动存到 output/ 目录）
    :param piece_fill: 棋子底色（原版默认 #E3CA92 木色）
    :param piece_outline: 棋子圆片描边色（原版默认 #905B18）
    :param board_bg: 棋盘底色（None = 透明，只留裁剪虚线框）
    :param grid_color: 棋盘线色（None = 黑色）
    :param two_sides: 棋子布局两侧（True = 上下陈列；False = 单侧布局，
                       棋盘整体下移、黑子收拢到棋盘正下方）

    示例 / Example::

        chess = ChineseChess("chinese_chess", board_bg="#F5D7A1",
                             grid_color="#916D3A")
        chess.finish()
    """

    def __init__(self, file_path, piece_fill=None, piece_outline=None,
                 board_bg=None, grid_color=None, two_sides=True):
        w, h = PaperSize.A4_portrait(1)  # 与原版同一张 A4 纵向纸 / same A4 portrait sheet
        super().__init__(file_path, width=w, height=h)
        self.set_background_color(Color.WHITE)

        self.margin_l, self.margin_r = 60, 60
        self.margin_t, self.margin_b = 20, 20

        self.board_bg = Color.TRANSPARENT if board_bg is None else board_bg
        self.piece_fill = "#E3CA92" if piece_fill is None else piece_fill
        self.piece_outline = "#905B18" if piece_outline is None else piece_outline
        self.grid_color = Color.BLACK if grid_color is None else grid_color
        self.two_sides = two_sides
        self.piece_colors = ["#FB3B10", Color.BLACK]  # [红方, 黑方] / [red, black]

        self.red_pieces = "車馬相仕帅仕相馬車兵兵兵兵兵炮炮"
        self.black_pieces = "車馬象士将士象馬車卒卒卒卒卒砲砲"

        # 棋盘几何（与原版公式逐项对应） / board geometry, formula by formula
        self.shift_y = 0 if two_sides else 115
        self.cell = (w - self.margin_l - self.margin_r) // 8
        self.board_x = self.margin_l
        self.board_y = (h - self.cell * 9) / 2 + self.shift_y

    # ------------------------------------------------------------------
    # 画表格：cols x rows 的网格线（对应原版 `画表格`）
    # ------------------------------------------------------------------
    def _table(self, x, y, cols, rows):
        for i in range(rows + 1):
            self.line((x, y + i * self.cell), (x + cols * self.cell, y + i * self.cell),
                      stroke_color=self.grid_color)
        for j in range(cols + 1):
            self.line((x + j * self.cell, y), (x + j * self.cell, y + rows * self.cell),
                      stroke_color=self.grid_color)

    # ------------------------------------------------------------------
    # 兵/炮位四角标记：贴边的点只画朝棋盘内侧的两角
    # ------------------------------------------------------------------
    def _cross_mark(self, px, py, col):
        gap = 0.08 * self.cell  # 线段贴近 / inset from the point
        arm = 0.15 * self.cell  # 线段长 / arm length
        for sx in (-1, 1):
            if sx < 0 and col == 0 or sx > 0 and col == 8:
                continue  # 左右贴边不留外侧刻度 / no arms outside the edge
            for sy in (-1, 1):
                cx, cy = px + sx * gap, py + sy * gap
                self.line((cx, cy), (cx + sx * arm, cy), stroke_color=self.grid_color)
                self.line((cx, cy), (cx, cy + sy * arm), stroke_color=self.grid_color)

    def build_board(self):
        """造棋盘：裁剪虚线框 + 上下两块 4 行表格 + 内外框 + 九宫与标记。"""
        cell, bx, by = self.cell, self.board_x, self.board_y
        frame = 5  # 棋盘外框边距 / outer frame inset
        crop = 33  # 裁剪余量 / crop margin (原版 33)

        # 1) 裁剪线：木色底板 + 虚线裁切框（有背景图的原版变体才省略这一步）
        self.rect(bx - crop, by - crop, cell * 8 + crop * 2, cell * 9 + crop * 2,
                  fill_color=self.board_bg, stroke_color=self.grid_color,
                  stroke_style="2,2", stroke_width=0.5)

        # 2) 棋盘表格：上下各 4 行 —— 中间天然留出楚河汉界，
        #    左右两条边线由内框矩形贯通（与原版完全同一套画法）
        self._table(bx, by, 8, 4)
        self._table(bx, by + cell * 5, 8, 4)

        # 3) 棋盘内框与外框粗线
        self.rect(bx, by, cell * 8, cell * 9, stroke_color=self.grid_color)
        self.rect(bx - frame, by - frame, cell * 8 + frame * 2,
                  cell * 9 + frame * 2, stroke_width=3, stroke_color=self.grid_color)

        # 4) 九宫斜线（上下各一座 X）
        for top in (by, by + cell * 7):
            self.line((bx + cell * 3, top), (bx + cell * 5, top + cell * 2),
                      stroke_color=self.grid_color)
            self.line((bx + cell * 5, top), (bx + cell * 3, top + cell * 2),
                      stroke_color=self.grid_color)

        # 5) 兵卒位（第 3/6 行的 0/2/4/6/8 路）与炮位（第 2/7 行的 1/7 路）
        for row in (3, 6):
            for col in (0, 2, 4, 6, 8):
                self._cross_mark(bx + col * cell, by + row * cell, col)
        for row in (2, 7):
            for col in (1, 7):
                self._cross_mark(bx + col * cell, by + row * cell, col)

        # 6) 楚河汉界：两组字各自逐字旋转（对应原版 字旋转(-90)/字旋转(90)）
        river_y = self.height / 2 + self.shift_y
        font_size = 55
        self.text(self.width * 0.25, river_y, "楚　河", font=Font.LISU,
                  font_size=font_size, fill_color=self.grid_color,
                  h_align=TextHAlign.MIDDLE, v_align=TextVAlign.MIDDLE,
                  char_rotate=-90).translate(48, 15)
        self.text(self.width * 0.75, river_y, "界　汉", font=Font.LISU,
                  font_size=font_size, fill_color=self.grid_color,
                  h_align=TextHAlign.MIDDLE, v_align=TextVAlign.MIDDLE,
                  char_rotate=90).translate(0, -40)

        # 7) 页面签名（原版 写软件信息：河界正中，半透明）
        self.text(self.width / 2, river_y, "MaLight",
                  font_size=font_size / 1.5, fill_color=self.grid_color,
                  h_align=TextHAlign.MIDDLE, v_align=TextVAlign.MIDDLE,
                  opacity=0.5)

    def build_piece(self, x, y, char, font_size, char_color):
        """构建棋子：木色圆片 + 模糊暗环 + 色圈 + 雕刻字（滤镜保留）。"""
        radius = font_size / 1.55
        self.circle(x, y, radius, fill_color=self.piece_fill,
                    stroke_color=self.piece_outline)
        self.circle(x, y, radius * 1.5 / 1.55).fx_blur(1)  # 立体感暗环 / soft dark ring
        self.circle(x, y, font_size / 1.93, stroke_color=char_color,
                    stroke_width=2)
        # 字：雕刻凹陷 —— 上/左内缘压深、下/右内缘受光提亮（fx_bevel/fx_emboss 是凸起，方向反了）
        self.text(x, y + 5, char, font=Font.LISU, font_size=font_size,
                  fill_color=char_color, h_align=TextHAlign.MIDDLE,
                  v_align=TextVAlign.MIDDLE).fx_engrave(1.5, 0.5, "#3E2410", "#FFFFFF")

    def _stagger_rows(self, chars, font_size, row_gap, color, y_base, y_shift=0.0):
        """两行交错陈列：首行错开 0.25 格、次行 0.75 格（原版 错开偏移）。"""
        half = len(chars) // 2
        xi = yi = 0
        offset = 0.25
        for char in chars:
            if xi >= half:
                xi = 0
                yi += 1
                offset = 0.75
            x = self.margin_l + self.cell * (xi + offset)
            self.build_piece(x, yi * row_gap + y_base + y_shift, char,
                             font_size, color)
            xi += 1

    def build_pieces(self):
        """造棋子：黑子两行在上、红子两行在下（单侧布局时黑子收到棋盘下）。"""
        font_size = 50
        row_gap = font_size * 1.13  # 棋子行距 / piece row pitch
        self._stagger_rows(self.black_pieces, font_size, row_gap,
                           self.piece_colors[1], self.margin_t + 24)
        shift = 0.0 if self.two_sides else -830.0
        self._stagger_rows(self.red_pieces, font_size, row_gap,
                           self.piece_colors[0],
                           self.height - self.margin_b - font_size - 31, shift)

    def on_create(self):
        """创作主钩子（finish() 时自动调用）。 / Main draw hook, called by finish()."""
        self.build_board()
        self.build_pieces()


if __name__ == "__main__":
    chess = ChineseChess("chinese_chess", board_bg="#F5D7A1",
                         grid_color="#916D3A")
    chess.finish()
    chess.export_png(scale=2, mode=PNGMode.CHROME)
    print("棋类样例完成 / done: output/chinese_chess.svg / .png")
