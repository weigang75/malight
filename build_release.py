# -*- coding: utf-8 -*-
"""
build_release —— malight 一键打包/发布脚本（生成 whl 与源码包）。

用法（在本项目根目录，即 pyproject.toml 所在目录）::

    python build_release.py              # 校验文档 + 打包 whl/sdist 到 dist/ + 自检
    python build_release.py --check      # 打包后追加 twine check 校验
    python build_release.py --upload     # 打包后上传到 PyPI（需已 pip install twine）
    python build_release.py --offline    # 不自动安装缺失的打包工具（build/twine）
    python build_release.py --full-clean # 连 build/ 中间缓存一起删掉再打包
    python build_release.py --no-clean   # 完全不清理（环境禁止删除时用）
    python build_release.py --no-docs    # 跳过文档链路校验（仅本地试打包时用）

发布到 PyPI 的完整流程::

    1) pip install -U twine
    2) python build_release.py --check      # 本地构建 + 元数据校验
    3) twine upload dist/*                  # 或直接 python build_release.py --upload
       # 测试环境: twine upload --repository testpypi dist/*
       # 账号密码建议用环境变量 TWINE_USERNAME / TWINE_PASSWORD，
       # 或在用户目录建 .pypirc（不要把 token 写进任何文件提交）

本脚本自动完成：文档链路校验（模块双语页 / 示例双语 / 译文表指纹 / PyPI 说明页）
→ 读取版本号 → 清理旧构建 → 打包 → 校验两个产物各装了该装的东西 →
临时安装 whl → 导入 malight 实测绘图/滤镜/扩展 → 报告产物清单。

产物分工是刻意的：wheel 只装可运行代码（含 py.typed，不含任何 .md）；
每个模块旁的 xxx.zh.md / xxx.en.md 双语页、以及 tools/ 下的生成器与译文表，
只随 sdist 分发 —— 拿到源码包的人不装额外东西就能离线重建全部文档。
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile
import venv

ROOT = os.path.dirname(os.path.abspath(__file__))
PKG_INIT = os.path.join(ROOT, "malight", "__init__.py")


def read_version():
    """从 malight/__init__.py 读取版本号（单一版本来源，与 pyproject 动态同步）。"""
    with open(PKG_INIT, encoding="utf-8") as f:
        m = re.search(r'__version__\s*=\s*"([^"]+)"', f.read())
    if not m:
        raise RuntimeError("无法在 malight/__init__.py 中找到 __version__")
    return m.group(1)


def run(cmd, cwd=ROOT):
    """执行命令，失败即中止。"""
    print("+", " ".join(cmd))
    r = subprocess.run(cmd, cwd=cwd)
    if r.returncode != 0:
        raise SystemExit(f"命令失败: {' '.join(cmd)}")


def python_module_ok(module):
    """
    检测解释器里是否有某模块。

    必须在项目根目录之外探测：仓库里构建产生的 ``build/`` 目录会被当成同名包
    导入成功，导致 ``python -m build`` 明明没装却探测为「已安装」。
    """
    return subprocess.run(
        [sys.executable, "-c", f"import {module}"],
        cwd=tempfile.gettempdir(),
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0


def ensure_tool(module, offline):
    """确保打包工具可用；缺失时尝试 pip 安装（--offline 跳过）。"""
    if python_module_ok(module):
        return True
    if offline:
        print(f"[跳过] 未安装 {module}（--offline 模式不自动安装）")
        return False
    print(f"[安装] pip install {module}")
    run([sys.executable, "-m", "pip", "install", "-q", module])
    return python_module_ok(module)


def clean(full=False):
    """
    清理旧构建产物。

    默认只精确删除 ``dist/`` 里的旧 ``*.whl`` / ``*.tar.gz``——它们是唯一会
    干扰产物清单的东西（不清掉就会把 2.1.0 的 whl 也当成本次产物）。

    ``build/`` 与 ``*.egg-info`` **故意保留**：前者只是 setuptools 的中间缓存，
    打包时会被重新填充；后者每次构建都会自动刷新。这两个目录动辄上百个文件，
    在带「批量删除护栏」的环境（不少企业终端安全软件都有）里，一次性删目录
    容易被拦下、直接打断整条发布流程。确需彻底重置时加 ``--full-clean``。
    """
    dist = os.path.join(ROOT, "dist")
    for f in sorted(os.listdir(dist)) if os.path.isdir(dist) else []:
        if f.endswith((".whl", ".tar.gz")):
            print("清理:", "dist" + os.sep + f)
            os.remove(os.path.join(dist, f))
    if full:
        for name in ("build", "dist", "malight.egg-info",
                     "src" + os.sep + "malight.egg-info"):
            p = os.path.join(ROOT, name)
            if os.path.isdir(p):
                print("清理:", name)
                shutil.rmtree(p, ignore_errors=True)
    else:
        print("（保留 build/ 与 *.egg-info 缓存；彻底重置请加 --full-clean）")


def build(with_sdist=True, offline=False):
    """打包。优先用官方 build 模块；不可用时回退 pip wheel。

    注意：**必须在项目根目录之外执行**。setuptools 构建后会在仓库里留下
    ``build/`` 目录，而 ``python -m build`` 会把当前目录下的 ``build/``
    当成同名包来解析，直接报 ``No module named build.__main__``。
    所以在临时目录里执行，并显式指定源码目录与输出目录。
    """
    has_build = ensure_tool("build", offline)
    if has_build:
        cmd = [sys.executable, "-m", "build",
               "--outdir", os.path.join(ROOT, "dist")]
        if not with_sdist:
            cmd += ["--wheel"]
        cmd += [ROOT]
        tmp = tempfile.mkdtemp(prefix="malight_build_")
        try:
            run(cmd, cwd=tmp)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        return
    # 回退方案：pip wheel（纯 Python 包足够；sdist 用 setup-less 方式缺失时提示）
    print("[回退] 使用 pip wheel --no-deps 构建纯 whl")
    run([sys.executable, "-m", "pip", "wheel", "--no-deps",
         "-w", os.path.join(ROOT, "dist"), ROOT])


def find_artifacts():
    """列出 dist/ 下的产物。"""
    dist = os.path.join(ROOT, "dist")
    if not os.path.isdir(dist):
        return []
    return sorted(os.path.join(dist, f) for f in os.listdir(dist)
                  if f.endswith((".whl", ".tar.gz")))


def refresh_docs():
    """
    打包前的「文档链路」闸门。

    文档不是随手写的附件，而是由 tools/ 下的生成器从**源码**推导出来的产物：

    * ``gen_docs.py``        —— 每个模块旁的 ``xxx.zh.md`` / ``xxx.en.md``；
    * ``gen_previews.py``    —— 模块文档里引用的效果预览图（滤镜/文字样式）在不在；
    * ``bilingualize_code.py`` —— 示例代码里的中文注释/文案是否都配了英文；
    * ``body_en.py``         —— 英文正文译文表是否还跟中文正文对得上（指纹）；
    * ``pypi_readme.py``     —— ``README.pypi.md`` 是否与 ``README.en.md`` 同步。

    任何一项落后就**中止打包**：宁可不发，也不发一个「README 说一套、模块页
    说另一套」的包。随后把所有生成物重跑一遍（幂等），确保 dist 里的内容与
    手头源码严格一致。
    """
    checks = [
        ([os.path.join(ROOT, "tools", "gen_docs.py"), "--check"],
         "模块双语文档与源码同步 —— 修复: python tools/gen_docs.py"),
        ([os.path.join(ROOT, "tools", "gen_previews.py"), "--check"],
         "效果预览图缺失 —— 修复: python tools/gen_previews.py"),
        ([os.path.join(ROOT, "tools", "bilingualize_code.py"), "--check"],
         "示例注释/文案双语完整 —— 修复: python tools/bilingualize_code.py"),
        ([os.path.join(ROOT, "tools", "body_en.py")],
         "英文正文译文表未过期 —— 修复: python tools/body_en.py --stamp"),
        ([os.path.join(ROOT, "tools", "pypi_readme.py"), "--check"],
         "PyPI 说明页与 README.en.md 同步 —— 修复: python tools/pypi_readme.py"),
    ]
    print("[文档] 校验生成物是否与源码一致")
    for cmd, tip in checks:
        r = subprocess.run([sys.executable] + cmd, cwd=ROOT,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                           text=True, encoding="utf-8", errors="replace")
        out = (r.stdout or "").strip()
        if r.returncode != 0:
            print(out)
            raise SystemExit("文档生成物已过期，先修复再打包：\n  " + tip)
        lines = [l.strip() for l in out.splitlines() if l.strip()]
        print("  OK  %s" % (lines[-1][:110] if lines else "已同步"))

    # 重跑生成器（幂等），保证打包时手头文件就是最新产物
    for tool in ("gen_docs.py", "bilingualize_code.py", "pypi_readme.py"):
        r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", tool)],
                           cwd=ROOT, stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT, text=True,
                           encoding="utf-8", errors="replace")
        if r.returncode != 0:
            print(r.stdout)
            raise SystemExit("重跑 %s 失败" % tool)
    print("  （已重跑生成器：文档 / 示例双语 / PyPI 说明页）")


#: sdist 里必须带上、用来「离线重建文档」的东西
SDIST_DOCS = ("README.md", "README.en.md", "README.pypi.md", "pyproject.toml",
              "tools/gen_docs.py", "tools/gen_previews.py",
              "tools/bilingualize_code.py", "tools/body_en.py",
              "tools/code_en.py", "tools/bipair.py", "tools/pypi_readme.py",
              "malight/assets/images/fx_preview.png",
              "malight/assets/images/filters_preview.png",
              "malight/assets/images/text_preview.png",
              "malight/assets/images/fonts_preview.png",
              "malight/assets/fonts/README.md")


def verify_artifacts():
    """
    校验两个产物各自的「该有的有、不该有的没有」：

    * sdist —— 每个模块旁的双语文档（.zh.md/.en.md）+ 全套生成器 + 译文表；
               拿到源码包的人不装任何额外东西就能重建文档。
    * wheel —— 可运行代码（py.typed + 各子包）+ 包内资源
               （malight/assets/images/ 的效果预览图）；一个 .md 都不许混进来；
               METADATA（就是 PyPI 页面）通篇英文，只放行语言开关那一行的
               ``[简体中文]``。
    """
    import tarfile
    import zipfile

    whl = [p for p in find_artifacts() if p.endswith(".whl")][-1]
    sd = [p for p in find_artifacts() if p.endswith(".tar.gz")][-1]

    with zipfile.ZipFile(whl) as z:
        names = z.namelist()
        meta_name = [n for n in names if n.endswith("METADATA")][0]
        # METADATA 就是 PyPI 页面的正文，必须在 with 里读出来（archive 一关就没了）
        meta = z.read(meta_name).decode("utf-8")
    stray = [n for n in names if n.lower().endswith((".md", ".rst", ".txt"))
             and n.split("/")[-1] not in ("METADATA", "WHEEL", "RECORD",
                                          "entry_points.txt", "top_level.txt",
                                          "LICENSE")]
    # 图片只允许出现在包内资源目录 malight/assets/images/（效果预览图，
    # 随包分发，malight.asset_path() 在 pip 安装后也能找到）。出现在别处
    # 说明 package-data 白名单被放宽了。
    allowed_img = "malight/assets/images/"
    stray_img = [n for n in names
                 if n.lower().endswith((".png", ".svg", ".jpg", ".jpeg", ".gif"))
                 and not n.startswith(allowed_img)]
    missing_img = [n for n in ("malight/assets/images/fx_preview.png",
                               "malight/assets/images/filters_preview.png",
                               "malight/assets/images/text_preview.png",
                               "malight/assets/images/fonts_preview.png")
                   if n not in names]
    missing_whl = [n for n in ("malight/py.typed", "malight/elements/__init__.py",
                               "malight/board/__init__.py",
                               "malight/pathkit/__init__.py")
                   if n not in names]
    # PyPI 只有一份 README（README.pypi.md），它必须通篇英文 —— 唯一例外是
    # 顶部语言开关那一行的链接文字 ``[简体中文](...)``：填了 [project.urls]
    # Homepage 后，pypi_readme.py 会把它改写成指向仓库中文 README 的绝对地址，
    # 让中文用户能从 PyPI 跳过去。和 README.en.md 的处理口径完全一致。
    switch = re.compile(r"\[\u7b80\u4f53\u4e2d\u6587\]\([^)]*\)")
    cjk = [l for l in meta.split("\n")
           if re.search(r"[\u4e00-\u9fff]", l) and not switch.search(l)]
    if missing_whl:
        raise SystemExit("wheel 缺少必需文件: %r" % missing_whl)
    if missing_img:
        raise SystemExit("wheel 缺少资源目录里的预览图: %r" % missing_img)
    if stray:
        raise SystemExit("wheel 里混进了文档（应只随 sdist 分发）: %r" % stray[:6])
    if stray_img:
        raise SystemExit("wheel 里出现了资源目录以外的图片: %r" % stray_img[:6])
    if cjk:
        raise SystemExit("wheel 元数据（PyPI 页面）里出现了中文: %r" % cjk[:4])
    print("[校验] wheel: py.typed + 子包 + 资源预览图齐全，无 .md，"
          "元数据全英文（语言开关除外）(%d 项)" % len(names))

    with tarfile.open(sd) as t:
        members = t.getnames()
    base = members[0].split("/")[0] + "/"
    short = [m[len(base):] for m in members if m.startswith(base)]
    missing_sd = [n for n in SDIST_DOCS if n not in short]
    # 只数包目录里的模块双语页 —— 仓库根的 README.en.md 也以 .en.md 结尾，
    # 不限定前缀会把 46 vs 46 数成 46 vs 47。
    module = [n for n in short if n.startswith("malight/")]
    zh = [n for n in module if n.endswith(".zh.md")]
    en = [n for n in module if n.endswith(".en.md")]
    if missing_sd:
        raise SystemExit("sdist 缺少文件: %r" % missing_sd)
    if not zh or not en:
        raise SystemExit("sdist 里的模块双语文档不全: zh=%d en=%d" % (len(zh), len(en)))
    if len(zh) != len(en):
        raise SystemExit("zh/en 模块文档数量不一致: %d vs %d" % (len(zh), len(en)))
    print("[校验] sdist: %d 个模块 %s + 生成器/译文表齐全 (%d 项)"
          % (len(zh), "xxx.zh.md/xxx.en.md", len(short)))


def verify_wheel():
    """
    发布前实测：新建干净 venv → 安装 whl → 导入 malight →
    实测绘图 + 滤镜 + 扩展机制 → 确认零核心依赖也能跑。
    """
    artifacts = [p for p in find_artifacts() if p.endswith(".whl")]
    if not artifacts:
        raise SystemExit("dist/ 中没有 whl，无法自检")
    whl = artifacts[-1]   # 取最新（按文件名排序即可，版本单调）
    print(f"[自检] 干净环境中安装 {os.path.basename(whl)}")
    tmp = tempfile.mkdtemp(prefix="malight_verify_")
    try:
        v = venv.EnvBuilder(with_pip=True, clear=True)
        v.create(tmp)
        py = os.path.join(tmp, "Scripts", "python.exe")
        if not os.path.exists(py):                     # 非 Windows
            py = os.path.join(tmp, "bin", "python")
        run([py, "-m", "pip", "install", "-q", "--no-input", whl])
        test = (
            "import inspect, os, typing\n"
            "from malight import Malight, Color, Font, PNGMode\n"
            "from malight.ext import toolkit\n"
            "from malight.pathkit import PathEditor, PathPoint, PathSegment\n"
            "from malight.pathkit import parse_path_d, segments_to_d\n"
            "pen = Malight('smoke', width=200, height=200)\n"
            "pen.circle(100, 100, 60, fill_color='#e63946',\n"
            "           filter=pen.fx.shadow(4, 4, 3))\n"
            "pen.finish()\n"
            "print('smoke ok:', pen.file_path)\n"
            "# 类型提示自检：注解存在、可求值、运行时类型一致\n"
            "assert type(pen.path()).__name__ == 'PathElement'\n"
            "assert type(pen.rect(0, 0, 9, 9)).__name__ == 'RectElement'\n"
            "assert typing.get_type_hints(Malight.circle).get('return') is not None\n"
            "assert inspect.getfile(typing)  # noqa\n"
            "print('type hints ok:', typing.get_type_hints(Malight.path)['return'])\n"
            "# 枚举 + 字符串双写法自检（字体 / 颜色 / 选项值）\n"
            "assert str(Font.SIMHEI) == 'SimHei' and Font.SIMHEI == 'SimHei'\n"
            "assert str(Color.RED).startswith('#')\n"
            "print('enum dual-write ok:', Font.SIMHEI, Color.RED)\n"
            "# pathkit 辅助类自检（看结构 / 拖点 / 存档）\n"
            "p = pen.path(fill_color='none', stroke_color='#333')\n"
            "p.move_to(10, 10).cubic_to((30, -20), (70, -20), (90, 10))\n"
            "ed = PathEditor(p)\n"
            "assert ed.anchor_count and ed.control_count\n"
            "ed.move_anchor(1, 90, 30)\n"
            "ed.move_control(ed.curve_indices()[0], 0, 40, -10)\n"
            "assert 'C' in ed.to_d()\n"
            "print('pathkit ok:', ed.anchor_count, '锚点 /', ed.control_count, '调整点')\n"
            "# py.typed 必须随包发布（PEP 561）\n"
            "import malight as _m\n"
            "_root = os.path.dirname(_m.__file__)\n"
            "assert os.path.exists(os.path.join(_root, 'py.typed')), '缺少 py.typed'\n"
            "for _sub in ('elements', 'board', 'pathkit'):\n"
            "    assert os.path.isdir(os.path.join(_root, _sub)), '缺少子包 ' + _sub\n"
            "print('package layout ok: py.typed + elements/board/pathkit')\n"
            "# 运行时多语言：默认英文，可切中文\n"
            "from malight import t, set_language, get_language, reset_language, is_chinese\n"
            "assert get_language() == 'en', get_language()\n"
            "assert not is_chinese()\n"
            "_en = t('export.ok', kind='SVG', tail='', path='a.svg', size='1 KB')\n"
            "set_language('zh')\n"
            "assert is_chinese()\n"
            "_cn = t('export.ok', kind='SVG', tail='', path='a.svg', size='1 KB')\n"
            "reset_language()\n"
            "assert _en != _cn and 'a.svg' in _en and 'a.svg' in _cn\n"
            "print('i18n ok (default EN, zh switchable)')\n"
            "# 双语文档随 sdist 分发、但不进 wheel：安装目录里不应出现 .md\n"
            "_md = []\n"
            "for _dp, _dn, _fn in os.walk(_root):\n"
            "    _md += [f for f in _fn if f.endswith('.md')]\n"
            "assert not _md, 'wheel 里混进了文档: %r' % _md[:5]\n"
            "print('wheel excludes module docs (.md) as intended')\n"
        )
        r = subprocess.run([py, "-c", test], capture_output=True,
                           text=True, cwd=tmp)
        if r.returncode != 0:
            print(r.stdout); print(r.stderr)
            raise SystemExit("自检失败：安装后的 malight 无法正常绘图")
        print(r.stdout.strip())
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def twine_step(args, offline):
    """twine check / upload。"""
    if not ensure_tool("twine", offline):
        raise SystemExit("需要 twine：pip install twine 后重试")
    run([sys.executable, "-m", "twine"] + args)


def main():
    argv = sys.argv[1:]
    offline = "--offline" in argv
    do_check = "--check" in argv
    do_upload = "--upload" in argv

    version = read_version()
    print(f"=== malight v{version} 打包发布 ===")
    if "--no-docs" in argv:
        print("[文档] --no-docs：跳过文档链路校验（仅本地试打包时用）")
    else:
        refresh_docs()
    if "--no-clean" in argv:
        print("（--no-clean：跳过清理，dist/ 里的旧产物请自行确认）")
    elif "--full-clean" in argv:
        clean(full=True)
    else:
        clean()
    build(with_sdist=not offline, offline=offline)

    artifacts = find_artifacts()
    if not artifacts:
        raise SystemExit("打包失败：dist/ 为空")
    print("\n产物:")
    for p in artifacts:
        print("  ", os.path.relpath(p, ROOT),
              f"({os.path.getsize(p) / 1024:.1f} KB)")

    if any(p.endswith(".tar.gz") for p in artifacts):
        verify_artifacts()
    verify_wheel()

    if do_check:
        twine_step(["check", "dist" + os.sep + "*"], offline)
    if do_upload:
        twine_step(["upload", "dist" + os.sep + "*"], offline)

    print("\n完成。上传 PyPI: pip install -U twine && twine upload dist/*")
    print("（测试环境先传 testpypi 验证：twine upload --repository testpypi dist/*）")


if __name__ == "__main__":
    main()
