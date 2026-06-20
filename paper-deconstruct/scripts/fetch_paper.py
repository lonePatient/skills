#!/usr/bin/env python3
"""获取 arXiv 论文的 LaTeX 源码与官方英文 PDF。

用法：
    python3 fetch_paper.py <arxiv_url_or_id> <output_parent_dir>

向 stdout 输出（每行一个 KEY='value'）：
    WORK_DIR   - 源码目录的绝对路径
    MAIN_TEX   - 相对于 WORK_DIR 的主 .tex 文件路径
    PDF_NAME   - 论文标题
    PDF_NAME_EN - 由标题生成的安全 ASCII 文件名主干
    PDF_EN     - 下载的英文 PDF 绝对路径；若下载失败则为空字符串
"""

import gzip
import html
import os
import re
import shutil
import sys
import tarfile
import unicodedata
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

_RE_ARXIV_ID_FULL = re.compile(
    r"^(?:https?://)?(?:arxiv\.org/(?:abs|pdf)/)?(?:arxiv:)?"
    r"([a-zA-Z.-]+/\d+|\d+\.\d+|\d+)"
    r"(?:v\d+)?"
    r"(?:\.pdf)?$"
)
_RE_DOCCLASS = re.compile(r"\\documentclass")
_RE_INPUT = re.compile(r"\\(?:input|include)\s*\{([^}]+)\}")
_ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}
_RE_CITATION_TITLE = re.compile(
    r'<meta\s+name=["\']citation_title["\']\s+content=["\'](.*?)["\']',
    re.IGNORECASE,
)
_RE_HTML_TITLE = re.compile(
    r"<title>\s*(?:\[[^\]]+\]\s*)?(.*?)\s*</title>",
    re.IGNORECASE | re.DOTALL,
)


def extract_arxiv_id(raw: str) -> str | None:
    """从裸 ID 或 URL 字符串中提取规范的 arXiv ID。

    输入必须是可识别的 arXiv URL 或 ID 形式；对于只是碰巧包含数字的
    任意字符串，不会将其视为 ID。
    """
    raw = raw.strip()
    match = _RE_ARXIV_ID_FULL.match(raw)
    if match:
        return match.group(1)
    return None


def _safe_extractall(tar: tarfile.TarFile, dest: str) -> None:
    """安全解压 tar 归档，防止目录遍历攻击。"""
    dest = os.path.abspath(dest)
    for member in tar.getmembers():
        member_path = os.path.abspath(os.path.join(dest, member.name))
        if not (member_path == dest or member_path.startswith(dest + os.sep)):
            raise ValueError(f"不安全的 tar 成员路径: {member.name!r}")
    tar.extractall(dest)


def _extract_tar_archive(tf: tarfile.TarFile, dest: str) -> None:
    """根据 Python 版本选择安全的 tar 解压方式。"""
    if sys.version_info >= (3, 12):
        tf.extractall(dest, filter="data")
    else:
        _safe_extractall(tf, dest)


def download_and_extract(paper_id: str, work_dir: str) -> list[str]:
    """下载 arXiv e-print 并解压到 ``work_dir``。

    返回相对于 ``work_dir`` 的所有 ``.tex`` 文件路径列表。
    """
    os.makedirs(work_dir, exist_ok=True)
    source_path = os.path.join(work_dir, "source.bin")

    url = f"https://arxiv.org/e-print/{paper_id}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            with open(source_path, "wb") as f:
                shutil.copyfileobj(resp, f)
    except Exception as exc:  # pragma: no cover - 网络异常
        print(f"错误：源码下载失败 {url}\n{exc}", file=sys.stderr)
        sys.exit(1)

    extracted = False
    try:
        if tarfile.is_tarfile(source_path):
            with tarfile.open(source_path) as tf:
                _extract_tar_archive(tf, work_dir)
            extracted = True
    except Exception:
        pass

    if not extracted:
        with open(source_path, "rb") as f:
            header = f.read(4)
        if header == b"%PDF":
            print(
                "错误：arXiv 仅返回 PDF，该论文未提供 LaTeX 源码。"
                "请提供本地 LaTeX 目录或 PDF 文件作为回退。",
                file=sys.stderr,
            )
            sys.exit(1)
        try:
            with gzip.open(source_path, "rb") as gz, open(
                os.path.join(work_dir, "paper.tex"), "wb"
            ) as out:
                shutil.copyfileobj(gz, out)
            extracted = True
        except Exception:
            pass

    if not extracted:
        print(
            "错误：无法识别源码压缩格式。该论文可能没有提供 LaTeX 源码。"
            "请提供本地 LaTeX 目录或 PDF 文件作为回退。",
            file=sys.stderr,
        )
        sys.exit(1)

    os.remove(source_path)

    tex_files = []
    for root, _, files in os.walk(work_dir):
        for name in files:
            if name.endswith(".tex"):
                tex_files.append(
                    os.path.relpath(os.path.join(root, name), work_dir)
                )

    if not tex_files:
        print("错误：源码中未找到任何 .tex 文件。", file=sys.stderr)
        sys.exit(1)

    return tex_files


def find_main_tex(
    work_dir: str, tex_files: list[str]
) -> tuple[str, list[str]]:
    """定位主 LaTeX 文件。

    返回一个元组：主文件的相对路径，以及所有候选主文件（包含
    ``\\documentclass`` 的文件）的相对路径列表。
    """
    candidates = []
    for rel in tex_files:
        path = os.path.join(work_dir, rel)
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except Exception:
            continue
        if _RE_DOCCLASS.search(content):
            candidates.append((rel, content))

    if not candidates:
        print("错误：未找到包含 \\documentclass 的主文件。", file=sys.stderr)
        sys.exit(1)

    if len(candidates) == 1:
        return candidates[0][0], [c[0] for c in candidates]

    main_rel, _ = max(candidates, key=lambda c: len(_RE_INPUT.findall(c[1])))
    return main_rel, [c[0] for c in candidates]


def _fetch_title_from_abs_page(paper_id: str) -> str | None:
    url = f"https://arxiv.org/abs/{paper_id}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            page = resp.read().decode("utf-8", errors="replace")
    except Exception:
        return None

    for pattern in (_RE_CITATION_TITLE, _RE_HTML_TITLE):
        match = pattern.search(page)
        if not match:
            continue
        title = html.unescape(match.group(1)).strip()
        title = re.sub(r"\s+", " ", title)
        if title:
            return title
    return None


def _fetch_title_from_api(paper_id: str) -> str | None:
    """通过 arXiv API 获取论文标题。"""
    query = urllib.parse.urlencode({"id_list": paper_id})
    url = f"https://arxiv.org/api/query?{query}"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
    except Exception:
        return None

    try:
        root = ET.fromstring(data)
    except ET.ParseError:
        return None

    entry = root.find("atom:entry", _ATOM_NS)
    if entry is None:
        return None
    title_el = entry.find("atom:title", _ATOM_NS)
    if title_el is None:
        return None

    title = " ".join(title_el.itertext()).strip()
    title = re.sub(r"\s+", " ", title)
    return title or None


def fetch_title(paper_id: str) -> str | None:
    """通过 arXiv API 或摘要页面获取论文标题。"""
    title = _fetch_title_from_api(paper_id)
    if title:
        return title
    return _fetch_title_from_abs_page(paper_id)


def _search_arxiv_by_title(title: str) -> str | None:
    """按标题搜索 arXiv，返回最佳匹配论文的 ID。"""
    query = urllib.parse.urlencode(
        {
            "search_query": f'ti:"{title}"',
            "max_results": "1",
            "sortBy": "relevance",
            "sortOrder": "descending",
        }
    )
    url = f"https://arxiv.org/api/query?{query}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
    except Exception:
        return None

    try:
        root = ET.fromstring(data)
    except ET.ParseError:
        return None

    entry = root.find("atom:entry", _ATOM_NS)
    if entry is None:
        return None
    id_el = entry.find("atom:id", _ATOM_NS)
    if id_el is None:
        return None

    id_text = "".join(id_el.itertext()).strip()
    match = _RE_ARXIV_ID_FULL.match(id_text)
    return match.group(1) if match else None


def safe_filename(title: str, fallback: str) -> str:
    """从 ``title`` 生成文件系统安全的 ASCII 文件名主干。

    当标题为空或无法生成可用字符时，回退到 ``fallback``。
    """
    if not title or not str(title).strip():
        return fallback

    s = " ".join(str(title).split())
    # Transliterate to ASCII using NFKD normalization.
    s = unicodedata.normalize("NFKD", s)
    s = s.encode("ascii", "ignore").decode("ascii")
    s = s.replace("/", "-").replace("\\", "-")
    for ch in '<>:"|?*':
        s = s.replace(ch, "_")
    s = re.sub(r"\s+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_").rstrip(".")
    if not s:
        return fallback
    if len(s) > 240:
        s = s[:240].rstrip("_")
    return s


def download_pdf(paper_id: str, dest: str) -> bool:
    """从 arXiv 下载官方英文 PDF。

    若成功将有效 PDF 保存到 ``dest``，则返回 ``True``。
    """
    urls = (
        f"https://export.arxiv.org/pdf/{paper_id}",
        f"https://arxiv.org/pdf/{paper_id}",
        f"https://arxiv.org/pdf/{paper_id}.pdf",
    )
    os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)
    for url in urls:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                data = resp.read()
        except Exception:
            continue
        if data[:4] != b"%PDF":
            continue
        with open(dest, "wb") as f:
            f.write(data)
        return True
    return False


def _sh_var(name: str, value: str) -> str:
    """格式化一行 shell 安全的 ``NAME='value'`` 输出。"""
    escaped = str(value).replace("'", "'\\''")
    return f"{name}='{escaped}'"


def main(argv: list[str]) -> int:
    """命令行入口。"""
    if len(argv) != 3:
        print(
            "用法：python3 fetch_paper.py <arxiv_url_or_id> <output_parent_dir>",
            file=sys.stderr,
        )
        return 2

    raw_input, output_parent_dir = argv[1], argv[2]
    paper_id = extract_arxiv_id(raw_input)
    if not paper_id:
        paper_id = _search_arxiv_by_title(raw_input)
    if not paper_id:
        print(
            f"错误：无法从输入中提取 arXiv ID，也无法通过标题搜索找到论文：{raw_input}",
            file=sys.stderr,
        )
        return 1

    paper_dir = os.path.join(output_parent_dir, paper_id)
    work_dir = os.path.join(paper_dir, "source")

    tex_files = download_and_extract(paper_id, work_dir)
    main_rel, _ = find_main_tex(work_dir, tex_files)
    main_rel = main_rel.replace("\\", "/")
    fallback = os.path.splitext(os.path.basename(main_rel))[0]

    title = fetch_title(paper_id)
    if not title:
        title = fallback

    pdf_name_en = safe_filename(title, fallback)
    pdf_en_path = os.path.join(paper_dir, pdf_name_en + ".pdf")
    pdf_ok = download_pdf(paper_id, pdf_en_path)

    print(_sh_var("WORK_DIR", os.path.abspath(work_dir)))
    print(_sh_var("MAIN_TEX", main_rel))
    print(_sh_var("PDF_NAME", title))
    print(_sh_var("PDF_NAME_EN", pdf_name_en))
    print(_sh_var("PDF_EN", pdf_en_path if pdf_ok else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
