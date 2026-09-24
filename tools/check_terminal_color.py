# -*- coding: utf-8 -*-
"""
终端上色判定闸门（check_terminal_color）
========================================

Gate for terminal color auto-detection.

这条是用户报出来的：在 **PyCharm 里跑脚本，彩色消息全都没有颜色**。
根因是判定只看 ``sys.stdout.isatty()`` —— PyCharm（以及 VS Code、IDEA 等）
的运行窗口把标准输出接成**管道**，``isatty()`` 恒为 False，可窗口本身是会
渲染 ANSI 的。于是 ``print_red(...)`` 里那个加色分支压根不执行。

The user reported that colored messages showed no color inside PyCharm. The
sole gate used to be ``sys.stdout.isatty()``; IDE run windows pipe stdout, so
``isatty()`` is always False even though the window renders ANSI fine.

现在的判定顺序（见 ``malight/tools.py`` 的 ``_auto_color``）::

    NO_COLOR                      -> 关（最高优先）
    MALIGHT_COLOR                 -> 按值
    FORCE_COLOR / CLICOLOR_FORCE  -> 开
    stream.isatty()               -> 开
    宿主渲染 ANSI 且输出是真 fd、又没重定向到文件 -> 开（IDE 运行窗口）
    否则                           -> 关

内存缓冲（``io.StringIO``、pytest 的输出捕获）**永远不上色** —— 它不会渲染
任何东西，染色只会污染断言里的字符串。

本工具把每个分支都跑一遍：**真的起子进程**、真的看输出里有没有转义码，
而不是只读环境变量。判据是「输出里出现了 ``\\x1b[``」，这是用户眼睛能看到
的唯一事实。

用法::

    python tools/check_terminal_color.py            # 逐场景明细
    python tools/check_terminal_color.py --quiet    # 只打一行结论
"""

from __future__ import print_function

import io
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

#: 影响判定的环境变量：跑场景前一律从父进程环境里摘掉，保证结果可复现
_CONTROL_ENV = ("NO_COLOR", "MALIGHT_COLOR", "FORCE_COLOR", "CLICOLOR_FORCE",
                "PYCHARM_HOSTED", "TERM_PROGRAM", "VSCODE_PID",
                "JETBRAINS_IDE", "TERMINAL_EMULATOR")

#: 子进程脚本：打一行红字（另打一行到内存缓冲），父进程看有没有转义码
_CHILD = (
    "import io\n"
    "from malight import print_red, color_enabled\n"
    "print_red('X')\n"
    "print('enabled=%s' % color_enabled())\n"
    "buf = io.StringIO()\n"
    "print_red('Y', file=buf)\n"
    "print('buffer=%s' % ('\\x1b[' in buf.getvalue()))\n"
)

#: (场景说明, 追加的环境变量, 是否重定向到磁盘文件, 期望上色)
CASES = (
    ("管道且无宿主标记（后台任务 / 日志采集）", {}, False, False),
    ("管道 + PYCHARM_HOSTED=1（PyCharm 运行窗口）", {"PYCHARM_HOSTED": "1"}, False, True),
    ("管道 + TERM_PROGRAM=vscode（VS Code 终端）", {"TERM_PROGRAM": "vscode"}, False, True),
    ("重定向到磁盘文件 + PYCHARM_HOSTED=1", {"PYCHARM_HOSTED": "1"}, True, False),
    ("NO_COLOR=1（事实标准，最高优先）", {"NO_COLOR": "1", "PYCHARM_HOSTED": "1"}, False, False),
    ("MALIGHT_COLOR=0", {"MALIGHT_COLOR": "0", "PYCHARM_HOSTED": "1"}, False, False),
    ("MALIGHT_COLOR=1（强制开）", {"MALIGHT_COLOR": "1"}, False, True),
    ("FORCE_COLOR=1（强制开）", {"FORCE_COLOR": "1"}, False, True),
)


def _base_env():
    """父进程环境去掉全部控制变量。"""
    return {k: v for k, v in os.environ.items() if k not in _CONTROL_ENV}


def _forced(extra):
    """这组环境变量是否属于「用户显式要求上色」。"""
    for name in ("MALIGHT_COLOR", "FORCE_COLOR", "CLICOLOR_FORCE"):
        value = extra.get(name)
        if value is not None and value.strip().lower() not in ("", "0", "false", "no", "off"):
            return True
    return False


def _run_case(py, tmp, script, extra, redirect_to):
    """跑一个场景，返回 ``(标准输出是否上色, 内存缓冲是否上色, 输出)``。"""
    env = _base_env()
    env.update(extra)
    env["PYTHONPATH"] = ROOT + os.pathsep + env.get("PYTHONPATH", "")
    env["PYTHONIOENCODING"] = "utf-8"
    if redirect_to:
        with io.open(redirect_to, "w", encoding="utf-8") as handle:
            subprocess.call([py, script], env=env, stdout=handle,
                            stderr=subprocess.DEVNULL)
        text = io.open(redirect_to, encoding="utf-8", errors="replace").read()
    else:
        proc = subprocess.Popen([py, script], env=env, stdout=subprocess.PIPE,
                                stderr=subprocess.DEVNULL)
        text = proc.stdout.read().decode("utf-8", "replace")
    colored = "\x1b[" in text.split("enabled=")[0]
    buffered = "buffer=True" in text
    return colored, buffered, text


def main(argv):
    """跑完整场景矩阵；任何一条不符期望就返回 1。"""
    quiet = "--quiet" in argv
    py = sys.executable or "python"
    tmp = tempfile.mkdtemp(prefix="malight_color_")
    script = os.path.join(tmp, "child.py")
    io.open(script, "w", encoding="utf-8", newline="\n").write(_CHILD)
    out_txt = os.path.join(tmp, "redirect.txt")

    problems = []
    try:
        for label, extra, redirect, want in CASES:
            got, buffered, _text = _run_case(py, tmp, script, extra,
                                             out_txt if redirect else None)
            if got != want:
                problems.append("%s：上色=%s，期望=%s" % (label, got, want))
            # 自动判断出来的上色，绝不能落到内存缓冲上（io.StringIO / 测试捕获
            # 不会渲染任何东西，染色只会污染断言里的字符串）。
            # 用户显式「强制开」时例外 —— 那时要的就是转义码，写到哪都带。
            if buffered and not _forced(extra):
                problems.append("%s：内存缓冲被染上了转义码" % label)
            if not quiet:
                print("  %s %-46s 上色=%-5s 期望=%-5s"
                      % ("OK  " if got == want else "FAIL", label, got, want))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    if problems:
        print("终端上色判定与预期不符：")
        for line in problems:
            print("  - " + line)
        return 1
    if not quiet:
        print("\n")
    print("终端上色判定 %d 个场景全部符合预期" % len(CASES))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
