#!/usr/bin/env python3
"""将 LaTeX 源码树中引用的 PDF 图片转换为 PNG 副本。

用法：
    python3 convert_figures.py <work_dir> <main_tex> [--output-dir DIR] [--dpi DPI]

示例：
    python3 convert_figures.py /path/to/paper source/main.tex
"""

import argparse
import json
import os
import re
import sys

# 匹配文件中任意位置的 \input{...} 与 \include{...}。
_RE_INPUT_INCLUDE = re.compile(r"\\(?:input|include)\s*\{([^}]+)\}")

# 匹配 \includegraphics[...]{...}；忽略可选参数。
_RE_INCLUDE_GRAPHICS = re.compile(r"\\includegraphics(?:\s*\[[^\]]*\])?\s*\{([^}]+)\}")


def _norm_rel(path: str, base: str) -> str:
    """返回使用正斜杠规范化的相对路径。"""
    return os.path.normpath(os.path.join(base, path)).replace("\\", "/")


def _is_inside(path: str, work_dir: str) -> bool:
    """若 ``path`` 解析后位于 ``work_dir`` 内部，则返回 ``True``。"""
    path = os.path.abspath(path)
    work_dir = os.path.abspath(work_dir)
    return path == work_dir or path.startswith(work_dir + os.sep)


def walk_tex_files(work_dir: str, main_tex: str) -> list[str]:
    """递归收集从 ``main_tex`` 可达的所有 .tex 文件。

    返回相对于 ``work_dir`` 的路径列表。
    """
    work_dir = os.path.abspath(work_dir)
    main_path = os.path.join(work_dir, main_tex)

    seen: set[str] = set()
    result: list[str] = []
    queue: list[str] = [main_path]

    while queue:
        path = queue.pop(0)
        rel = os.path.relpath(path, work_dir)
        if rel in seen:
            continue
        seen.add(rel)

        if not os.path.isfile(path):
            continue
        result.append(rel)

        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except Exception:
            continue

        current_dir = os.path.dirname(rel) or ""
        for match in _RE_INPUT_INCLUDE.finditer(content):
            ref = match.group(1).strip()
            if not ref:
                continue
            if not ref.endswith(".tex"):
                ref += ".tex"
            child_rel = _norm_rel(ref, current_dir)
            child_path = os.path.join(work_dir, child_rel)
            if child_rel not in seen and _is_inside(child_path, work_dir) and os.path.isfile(child_path):
                queue.append(child_path)

    return result


def extract_graphics(work_dir: str, main_tex: str) -> set[str]:
    r"""提取 ``\includegraphics`` 引用的所有 PDF 图片路径。

    返回相对于 ``work_dir`` 的路径集合。
    """
    tex_files = walk_tex_files(work_dir, main_tex)
    graphics: set[str] = set()

    for rel in tex_files:
        path = os.path.join(work_dir, rel)
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except Exception:
            continue

        current_dir = os.path.dirname(rel) or ""
        for match in _RE_INCLUDE_GRAPHICS.finditer(content):
            ref = match.group(1).strip()
            if not ref or ref.startswith("/") or "://" in ref:
                continue
            full_rel = _norm_rel(ref, current_dir)
            full_path = os.path.join(work_dir, full_rel)
            if full_rel.lower().endswith(".pdf") and _is_inside(full_path, work_dir):
                graphics.add(full_rel)

    return graphics


def convert_pdf_to_png(pdf_path: str, png_path: str, dpi: int) -> bool:
    """将 ``pdf_path`` 的第一页转换为 ``png_path`` 处的 PNG。

    成功返回 ``True``，失败返回 ``False``。
    """
    try:
        import fitz  # PyMuPDF
    except Exception as exc:  # pragma: no cover - 已在 main 中提前捕获
        print(f"无法导入 PyMuPDF: {exc}", file=sys.stderr)
        return False

    os.makedirs(os.path.dirname(png_path) or ".", exist_ok=True)

    try:
        doc = fitz.open(pdf_path)
        page = doc.load_page(0)
        scale = dpi / 72.0
        mat = fitz.Matrix(scale, scale)
        pix = page.get_pixmap(matrix=mat)
        pix.save(png_path)
        doc.close()
        return True
    except Exception as exc:
        print(f"转换失败 {pdf_path}: {exc}", file=sys.stderr)
        return False


def main(argv: list[str]) -> int:
    """命令行入口。"""
    parser = argparse.ArgumentParser(
        description="将 LaTeX 项目中的 PDF 图片转换为 PNG 副本。"
    )
    parser.add_argument("work_dir", help="LaTeX 源码目录")
    parser.add_argument("main_tex", help="相对于 work_dir 的主 .tex 文件")
    parser.add_argument(
        "--output-dir",
        default="figures/png",
        help="PNG 输出目录，相对于 work_dir（默认：figures/png）",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=200,
        help="渲染 DPI（默认：200）",
    )
    args = parser.parse_args(argv[1:])

    work_dir = args.work_dir
    main_tex = args.main_tex

    if not os.path.isdir(work_dir):
        print(f"错误：work_dir 不存在: {work_dir}", file=sys.stderr)
        return 1

    main_tex_abs = os.path.join(work_dir, main_tex)
    if not os.path.isfile(main_tex_abs):
        print(f"错误：main_tex 不存在: {main_tex_abs}", file=sys.stderr)
        return 1

    try:
        import fitz  # noqa: F401
    except ImportError:
        print(
            "错误：未安装 PyMuPDF。请运行：pip install pymupdf",
            file=sys.stderr,
        )
        return 1

    figures = extract_graphics(work_dir, main_tex)
    out_dir = os.path.join(work_dir, args.output_dir)
    os.makedirs(out_dir, exist_ok=True)

    converted = 0
    figure_map: dict[str, str] = {}

    for rel in sorted(figures):
        pdf_path = os.path.join(work_dir, rel)
        if not os.path.isfile(pdf_path):
            print(f"警告：PDF 文件不存在，跳过: {rel}", file=sys.stderr)
            continue

        stem = rel[:-4]  # 去掉 .pdf（已通过小写检查）
        png_rel = _norm_rel(stem + ".png", args.output_dir)
        png_path = os.path.join(work_dir, png_rel)

        if convert_pdf_to_png(pdf_path, png_path, args.dpi):
            converted += 1
            figure_map[rel] = png_rel
        else:
            print(f"警告：跳过转换失败的文件: {rel}", file=sys.stderr)

    map_path = os.path.join(out_dir, "figure_map.json")
    with open(map_path, "w", encoding="utf-8") as f:
        json.dump(figure_map, f, indent=2, ensure_ascii=False)

    print(f"已转换 {converted} 个 PDF 图片。")
    print(f"图片映射表：{os.path.abspath(map_path)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
