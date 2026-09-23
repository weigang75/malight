# -*- coding: utf-8 -*-
"""
双语对解析（bipair）
====================

``tools/bilingualize_code.py`` 把示例代码里的中文注释与中文文案写成
「中文 / English」形式；``tools/gen_docs.py`` 生成文档时再按语言各取一半。
两个工具共用本模块的解析逻辑，保证「写进去」和「读出来」用的是同一套规则。

Splitter for the ``"Chinese / English"`` pairs used inside example code. The
injector (bilingualize_code.py) and the docs generator (gen_docs.py) share this
module so that what gets written is exactly what gets read back.

拆分规则 / Splitting rule:
    从右往左找第一个满足下面四条的 ``" / "``：

    * 左半边含中文；
    * 右半边**不含**中文；
    * 右半边含至少两个拉丁字母（挡住 ``0(M) / 1(L) / 2(C)`` 这类
      「用斜杠分隔的编号」被误判成双语对）；
    * 右半边不以 ``2(C)`` 这种编号片段开头（挡住三项以上的编号链，
      只有前一条时它们会被误判 —— 见 ``_CODE_CHAIN``）。

    Finds the right-most ``" / "`` whose left side has CJK, whose right side has
    none, and whose right side contains a real word (two or more letters) without
    starting with a ``2(C)``-style numbering fragment.
"""

from __future__ import print_function

import re

SEP = " / "
_CJK = re.compile(r"[\u4e00-\u9fff]")
_LETTER = re.compile(r"[A-Za-z]")

#: 「中文」在这个项目里有两套写法，**两套都必须认**：
#: ``gen_docs.py`` 内部按 ``"cn"`` / ``"en"`` 分派页面，
#: 而语言码（``malight.i18n``、``MALIGHT_LANG``、``xxx.zh.md`` 后缀）是 ``zh``。
#: 只认一种的后果是静默的：``pick("…", "cn")`` 掉进 else 分支取了英文半边，
#: 于是每一页 ``.zh.md`` 的示例代码都变成英文 —— 而正文还是中文，
#: 扫 CJK 的检查完全看不出来。统一在这里判，别再各写各的。
CN_CODES = ("cn", "zh")


def is_cn(lang):
    """``lang`` 是不是中文（``cn`` / ``zh`` / ``zh-TW`` 都算）。"""
    return str(lang).lower().startswith(CN_CODES)


def _looks_english(text):
    """
    右半边像不像英文：至少要有两个拉丁字母。

    用「字母个数」而不是「{2,} 连续字母」，是为了同时接受 ``e.g. [2, 3]``
    这类缩写，又能挡住 ``3(Q)`` 这种「斜杠分隔的编号」（那只有一个字母）。
    """
    return len(_LETTER.findall(text)) >= 2


#: 「0(M)」「2(C)」这类编号片段。单项靠 ``_looks_english`` 就挡住了，
#: 但**三项以上的链**挡不住：``段号 0(M) / 1(L) / 2(C)`` 里从右往左找，
#: ``2(C)`` 被挡掉之后，下一个候选 ``1(L) / 2(C)`` 里有两个字母、
#: 又没中文，于是被误判成双语对 —— 英文页会取到 ``1(L) / 2(C)``，
#: 把前面的中文连同 ``0(M)`` 一起吞掉。所以再补一道：右半边不能以编号片段开头。
_CODE_CHAIN = re.compile(r"^\s*\d+\s*\(\s*[A-Za-z]\s*\)")

#: 引号（按长度优先匹配）
QUOTES = ('"""', "'''", '"', "'")


def has_cjk(text):
    """文本里有没有汉字。"""
    return bool(_CJK.search(text or ""))


def split_pair(text):
    """
    把 ``"中文 / English"`` 拆成两半。

    :return: ``(中文, 英文)``；不是双语对时返回 ``None``
    """
    idx = text.rfind(SEP)
    while idx >= 0:
        left, right = text[:idx], text[idx + len(SEP):]
        if (_CJK.search(left) and not _CJK.search(right)
                and _looks_english(right) and not _CODE_CHAIN.match(right)):
            return left, right
        idx = text.rfind(SEP, 0, idx)
    return None


def is_paired(text):
    """
    这段文本是否已经是双语对（或是被折行拆开的一半）。

    ``"中文…… / "`` 结尾的多行拼接，后半行是纯英文，也算已处理。
    """
    if split_pair(text) is not None:
        return True
    return has_cjk(text) and text.rstrip().endswith("/")


def pick(text, lang):
    """
    从双语对里取 ``lang`` 那一半；不是双语对时原样返回。

    ``lang`` 收 ``cn`` / ``zh``（都当中文）与 ``en``，见 ``CN_CODES``。

    保留原文本的前导空白（注释与示例输出常靠它对齐），只裁掉分隔符两侧的空格。
    """
    pair = split_pair(text)
    if pair is None:
        return text
    left, right = pair
    indent = left[:len(left) - len(left.lstrip())]
    if is_cn(lang):
        return left.rstrip()
    return indent + right.strip()


# ===========================================================================
# 一行代码的结构扫描
# ===========================================================================
def scan_line(line):
    """
    扫一行代码，找出注释起点与所有单行字符串字面量。

    :return: ``(注释起点, [(内容起点, 内容终点, 引号), ...])``；
             注释起点为 ``-1`` 表示没有注释
    """
    strings, i, n = [], 0, len(line)
    while i < n:
        ch = line[i]
        if ch == "#":
            return i, strings
        if ch in "\"'":
            quote = ch
            if line[i:i + 3] in ('"""', "'''"):
                quote = line[i:i + 3]
            j, buf = i + len(quote), []
            while j < n:
                if line[j] == "\\":
                    buf.append(line[j:j + 2])
                    j += 2
                    continue
                if line[j:j + len(quote)] == quote:
                    break
                buf.append(line[j])
                j += 1
            if j >= n:                       # 没有收尾引号：三引号开头，放弃这一行
                return -1, strings
            strings.append((i + len(quote), j, quote))
            i = j + len(quote)
            continue
        i += 1
    return -1, strings


def trim_line(line, lang):
    """
    按 ``lang`` 裁剪一行代码：注释与字符串里的双语对只保留对应的一半。

    不是双语对的地方原样保留，所以对没写过英文的代码是安全的空操作。

    顺序很关键：**先改注释、再改字符串**。字符串在注释左边，改完注释不会
    影响字符串的下标；反过来（先改字符串）会让注释的起点偏移，把注释切错。
    """
    comment_at, strings = scan_line(line)
    out = line
    if comment_at >= 0:
        head, comment = out[:comment_at], out[comment_at + 1:]
        if has_cjk(comment) and split_pair(comment) is not None:
            out = head + "#" + pick(comment, lang)
    for start, end, _quote in reversed(strings):
        inner = out[start:end]
        if has_cjk(inner) and split_pair(inner) is not None:
            out = out[:start] + pick(inner, lang) + out[end:]
    return out


def trim_block(code, lang):
    """把一段示例代码按 ``lang`` 整块裁剪。"""
    return "\n".join(trim_line(l, lang) for l in code.split("\n"))


if __name__ == "__main__":
    samples = [
        'ball.translate(20, -10)                  # 平移 / translate',
        'print("元素类型: / element type:", type(ball).__name__)',
        'print("段号依次是 0(M) / 1(L) / 2(C) / 3(Q)")',
        'pen.fx.shadow(6, 8, 6)  # 一行加投影滤镜 / one-line drop shadow',
        'd = "M0 0 L10 10"       # 不含中文',
    ]
    for s in samples:
        print("原文:", s)
        print("  中文:", trim_line(s, "zh"))
        print("  英文:", trim_line(s, "en"))
        at, frags = scan_line(s)

        def _frag(at, frags, s):
            if at >= 0:
                return s[at + 1:]
            return s[frags[0][0]:frags[0][1]] if frags else ""

        print("  片段已双语:", is_paired(_frag(at, frags, s)))
        print()
