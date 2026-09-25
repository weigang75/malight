# -*- coding: utf-8 -*-
"""
棋类样例 2：国际象棋（Chess / International Chess）—— 继承绘图板的写法
========================================================================

按「Python超人/三月三」神笔码靓原版《国际象棋制作》的布局 1:1 移植：
A4 纵向页面，8x8 绿白棋盘居中（格子里叠 0.3 透明度的开局水印字），
白子两行在上、黑子两行在下交错陈列，每枚棋子由多层圆环 + 字符组成。

Ported 1:1 from the original MagicPen-CN class `国际象棋制作`: an A4
portrait sheet with a green/cream 8x8 board (faint 0.3-opacity starting
position watermarks on the squares), white pieces staggered in two rows
on top and black pieces below, each disc built from layered rings.

布局公式与原版一致 / Layout formulas match the original::

    单元格宽 = (宽 - 左边距 - 右边距) // 8
    棋盘起点 Y = (高 - 单元格宽 * 9) / 2 + 位移Y + 30
    棋子行距 = 字号 * 1.35，上排错开 0.25 格、下排错开 0.75 格

运行 / Run::

    python examples/board_games/international_chess.py
    # 生成 output/international_chess.svg 与 output/international_chess.png
"""

import os as _os, sys as _sys

_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))))

from malight import Malight, Color, Font, PaperSize, TextHAlign, TextVAlign

#: 棋子字形字体栈：U+2654..265F 棋子符号很多字体都没有（Times New Roman /
#: 常见中文字体里就没有），不指定字体或指定了没有这些字形的字体时，浏览器
#: 兜底失败就会渲染成「方块豆腐」。给一串候选：Windows 用 Segoe UI Symbol，
#: Linux 用 DejaVu Sans，macOS 用 Apple Symbols，兜底 sans-serif。
PIECE_FONT = '"Segoe UI Symbol", "DejaVu Sans", "Apple Symbols", ' \
             '"Noto Sans Symbols 2", sans-serif'


class InternationalChess(Malight):
    """国际象棋棋谱页（继承 Malight 绘图板，对应原版 `国际象棋制作` 类）。

    A chess sheet subclassing the Malight board (the CN original
    subclasses its drawing board the same way).

    :param file_path: 输出文件名（相对路径自动存到 output/ 目录）
    :param piece_fill: 棋子底色（原版默认 #E3CA92 木色）
    :param piece_outline: 棋子圆片描边色（原版默认 #905B18）
    :param board_bg: 棋盘浅格底色（None = 透明；示例用经典 #EEEED2）
    :param grid_color: 深格与线条色（None = 黑色；示例用经典 #779557）
    :param two_sides: 棋子布局两侧（True = 上下陈列；False = 单侧布局）

    示例 / Example::

        chess = InternationalChess("international_chess",
                                   board_bg="#EEEED2", grid_color="#779557")
        chess.finish()
    """

    def __init__(self, file_path, piece_fill=None, piece_outline=None,
                 board_bg=None, grid_color=None, two_sides=True):
        w, h = PaperSize.A4_portrait(1)  # 与原版同一张 A4 纵向纸 / same A4 portrait sheet
        super().__init__(file_path, width=w, height=h)
        self.set_background_color(Color.WHITE)

        self.margin_l, self.margin_r = 60, 60
        self.margin_t, self.margin_b = 30, 20

        self.board_bg = Color.TRANSPARENT if board_bg is None else board_bg
        self.piece_fill = "#E3CA92" if piece_fill is None else piece_fill
        self.piece_outline = "#905B18" if piece_outline is None else piece_outline
        self.grid_color = Color.BLACK if grid_color is None else grid_color
        self.two_sides = two_sides

        # 原版字串：前 16 枚白子、后 16 枚黑子（底线 8 枚 + 兵 8 枚）
        self.white_pieces = "♖♘♗♕♔♗♘♖♙♙♙♙♙♙♙♙"
        self.black_pieces = "♟♟♟♟♟♟♟♟♜♞♝♛♚♝♞♜"

        # 棋盘几何（与原版公式逐项对应；棋盘高按 9 格算，整体比 8 格棋盘多留一格）
        self.shift_y = 0 if two_sides else 130
        self.cell = (w - self.margin_l - self.margin_r) // 8
        self.board_x = self.margin_l
        self.board_y = (h - self.cell * 9) / 2 + self.shift_y + 30

    def build_board(self):
        """造棋盘：裁剪虚线框 + 明暗格 + 水印字 + 内外框 + 页面签名。"""
        cell, bx, by = self.cell, self.board_x, self.board_y
        frame = 5  # 棋盘外框边距 / outer frame inset
        crop = 38  # 裁剪余量 / crop margin (原版 38)

        # 1) 裁剪线：浅色底板 + 虚线裁切框（浅格透明感来自它）
        self.rect(bx - crop, by - crop, cell * 8 + crop * 2, cell * 8 + crop * 2,
                  fill_color=self.board_bg, stroke_color=self.grid_color,
                  stroke_style="2,2", stroke_width=0.5)

        # 2) 棋盘内框
        self.rect(bx, by, cell * 8, cell * 8, stroke_color=self.grid_color)

        # 3) 明暗格 + 开局水印字：(xi+yi) 为偶数画深格；
        #    深格上水印用浅色、浅格上用深色，始终与底色对比
        pieces = self.white_pieces + self.black_pieces
        font_size = 60
        index = 0
        for yi in range(8):
            for xi in range(8):
                if (xi + yi) % 2 != 0:
                    self.rect(bx + xi * cell, by + yi * cell, cell, cell,
                              fill_color=self.grid_color, stroke_width=0)
                    char_color = self.board_bg
                else:
                    char_color = self.grid_color
                if yi in (0, 1, 6, 7):
                    glyph = self.text(bx + (xi + 0.5) * cell,
                                      by + (yi + 0.5) * cell + 3, pieces[index],
                                      font=PIECE_FONT, font_size=font_size,
                                      fill_color=char_color,
                                      h_align=TextHAlign.MIDDLE,
                                      v_align=TextVAlign.MIDDLE, opacity=0.3)
                    if yi in (0, 1):
                        # 上方两行字旋转 180，让白方面向黑方（原版 字旋转(180)）
                        glyph.update(char_rotate=180)
                        glyph.translate(font_size, -font_size * 0.7)
                    index += 1

        # 4) 棋盘外框粗线
        self.rect(bx - frame, by - frame, cell * 8 + frame * 2,
                  cell * 8 + frame * 2, stroke_width=3, stroke_color=self.grid_color)

        # 5) 页面签名与网址（原版 写软件信息/写网址信息 的位置）
        #    签名右对齐到右边距，避免长英文串居中时溢出页面被裁掉
        font_size = 55
        self.text(self.width - self.margin_l,
                  self.height / 2 + self.shift_y + cell * 4.18,
                  "Created with MaLight", font=Font.VERDANA,
                  font_size=font_size / 2,
                  fill_color=self.grid_color, h_align=TextHAlign.END,
                  v_align=TextVAlign.MIDDLE, opacity=0.5)
        url_y = (self.height - self.margin_b - 160 if self.two_sides
                 else self.height - self.margin_b - font_size / 4 - 21)
        url_text = self.text(self.width - self.margin_l, url_y, "https://github.com/weigang75",
                             font=Font.VERDANA, font_size=font_size / 4,
                             fill_color=Color.BLACK, h_align=TextHAlign.END, opacity=0.7)
        self.create_link(url_text, "https://github.com/weigang75/malight")

    def build_piece(self, x, y, char, font_size, char_color):
        """构建棋子：多层圆环 + 投影字 + 模糊暗环（原版五层画法）。"""
        disc = self.grid_color if char_color == Color.WHITE else self.board_bg
        self.circle(x, y, font_size / 1.54, fill_color=disc,
                    stroke_color=self.grid_color)
        self.circle(x, y, font_size / 1.6, stroke_color=char_color,
                    stroke_width=1.5)
        self.text(x, y + 6.5, char, font=PIECE_FONT, font_size=font_size,
                  fill_color=char_color,
                  h_align=TextHAlign.MIDDLE, v_align=TextVAlign.MIDDLE
                  ).fx_shadow(1, 1, 0.8)
        self.circle(x, y, font_size / 1.92, stroke_color=Color.BLACK,
                    stroke_width=2).fx_blur(0.8)  # 立体感 / 3-D feel
        self.circle(x, y, font_size / 1.85, stroke_color=char_color,
                    stroke_width=3)

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
        """造棋子：白子两行在上、黑子两行在下（单侧布局时收到棋盘下）。"""
        font_size = 50
        row_gap = font_size * 1.35  # 棋子行距 / piece row pitch
        self._stagger_rows(self.white_pieces, font_size, row_gap,
                           Color.WHITE, self.margin_t + 24)
        shift = -30.0 if self.two_sides else -800.0
        self._stagger_rows(self.black_pieces, font_size, row_gap,
                           "#303030",
                           self.height - self.margin_b - font_size - 31, shift)

    def on_create(self):
        """创作主钩子（finish() 时自动调用）。 / Main draw hook, called by finish()."""
        self.build_board()
        self.build_pieces()


if __name__ == "__main__":
    chess = InternationalChess("international_chess",
                               board_bg="#EEEED2", grid_color="#779557")
    chess.finish()
    chess.export_png(scale=2)
    print("棋类样例完成 / done: output/international_chess.svg / .png")
