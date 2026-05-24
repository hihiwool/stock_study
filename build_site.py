from __future__ import annotations

import html
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote


ROOT = Path(__file__).resolve().parent
VAULT = ROOT.parent / "obsidian_vault" / "stock"
PUBLIC = ROOT / "public"
ARTICLES = PUBLIC / "articles"


@dataclass(frozen=True)
class SourcePage:
    source: str
    title: str
    group: str
    summary: str = ""
    ticker: str = ""
    tv_symbol: str = ""


PAGES = [
    SourcePage("00_대시보드/프로젝트_방향.md", "프로젝트 방향", "dashboard"),
    SourcePage("00_대시보드/현재_관심종목_상태.md", "현재 관심종목 상태", "dashboard"),
    SourcePage("00_대시보드/누적_투자_원칙.md", "누적 투자 원칙", "dashboard"),
    SourcePage("00_대시보드/체크리스트.md", "체크리스트", "dashboard"),
    SourcePage("02_기업분석/삼성전기.md", "삼성전기", "company", "AI 서버, 데이터센터, FCBGA, 고부가 MLCC", ticker="009150", tv_symbol="KRX:009150"),
    SourcePage("02_기업분석/알파벳.md", "알파벳", "company", "Search, YouTube, Google Cloud, Gemini, TPU", ticker="GOOGL", tv_symbol="NASDAQ:GOOGL"),
    SourcePage("02_기업분석/엔비디아.md", "엔비디아", "company", "AI 데이터센터, Compute, Networking, Blackwell", ticker="NVDA", tv_symbol="NASDAQ:NVDA"),
    SourcePage("02_기업분석/블룸에너지.md", "블룸에너지", "company", "AI 데이터센터 전력 수요, 분산전원, 연료전지", ticker="BE", tv_symbol="NYSE:BE"),
    SourcePage("01_데일리_숙제/Day 1 - 관심종목 등록 및 삼성전기 분석.md", "Day 1", "daily"),
    SourcePage("01_데일리_숙제/Day 2 - 알파벳 분석.md", "Day 2", "daily"),
    SourcePage("01_데일리_숙제/Day 3 - 엔비디아 실적 프리뷰.md", "Day 3", "daily"),
    SourcePage("01_데일리_숙제/Day 4 - 엔비디아 실적 발표 확인.md", "Day 4", "daily"),
    SourcePage("01_데일리_숙제/Day 5 - 엔비디아 실적 후 복기.md", "Day 5", "daily"),
    SourcePage("01_데일리_숙제/Day 6 - 블룸에너지 투자 아이디어 정리.md", "Day 6", "daily"),
]

SLUG_BY_SOURCE = {
    "00_대시보드/주식_스터디_홈.md": "dashboard-home",
    "00_대시보드/프로젝트_방향.md": "project-direction",
    "00_대시보드/현재_관심종목_상태.md": "watchlist-status",
    "00_대시보드/누적_투자_원칙.md": "investment-principles",
    "00_대시보드/체크리스트.md": "checklist",
    "02_기업분석/삼성전기.md": "company-samsung-electro-mechanics",
    "02_기업분석/알파벳.md": "company-alphabet",
    "02_기업분석/엔비디아.md": "company-nvidia",
    "02_기업분석/블룸에너지.md": "company-bloom-energy",
    "01_데일리_숙제/Day 1 - 관심종목 등록 및 삼성전기 분석.md": "daily-day-1",
    "01_데일리_숙제/Day 2 - 알파벳 분석.md": "daily-day-2",
    "01_데일리_숙제/Day 3 - 엔비디아 실적 프리뷰.md": "daily-day-3",
    "01_데일리_숙제/Day 4 - 엔비디아 실적 발표 확인.md": "daily-day-4",
    "01_데일리_숙제/Day 5 - 엔비디아 실적 후 복기.md": "daily-day-5",
    "01_데일리_숙제/Day 6 - 블룸에너지 투자 아이디어 정리.md": "daily-day-6",
}


def slug_for(source: str) -> str:
    if source in SLUG_BY_SOURCE:
        return SLUG_BY_SOURCE[source]
    stem = Path(source).with_suffix("").as_posix()
    slug = re.sub(r"[^0-9A-Za-z가-힣]+", "-", stem).strip("-").lower()
    return quote(slug)


SLUGS = {Path(page.source).with_suffix("").as_posix(): slug_for(page.source) for page in PAGES}
SLUGS.update({Path(page.source).stem: slug_for(page.source) for page in PAGES})


def read_source(page: SourcePage) -> str:
    path = VAULT / page.source
    if not path.exists():
        raise FileNotFoundError(f"Missing source file: {path}")
    return path.read_text(encoding="utf-8")


def convert_inline(text: str, link_prefix: str = "./articles/") -> str:
    text = html.escape(text)

    def obsidian_link(match: re.Match[str]) -> str:
        raw = html.unescape(match.group(1))
        target, _, label = raw.partition("|")
        target = target.strip()
        label = label.strip() or Path(target).stem
        key = Path(target).with_suffix("").as_posix()
        fallback = Path(target).stem
        slug = SLUGS.get(key) or SLUGS.get(fallback)
        if slug:
            return f'<a href="{link_prefix}{slug}.html">{html.escape(label)}</a>'
        return html.escape(label)

    text = re.sub(r"\[\[([^\]]+)\]\]", obsidian_link, text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    return text


def split_table_row(line: str) -> list[str]:
    cells: list[str] = []
    current: list[str] = []
    depth = 0
    source = line.strip().strip("|")
    index = 0
    while index < len(source):
        char = source[index]
        pair = source[index : index + 2]
        if pair == "[[":
            depth += 1
            current.append(pair)
            index += 2
            continue
        if pair == "]]" and depth:
            depth -= 1
            current.append(pair)
            index += 2
            continue
        if char == "|" and depth == 0:
            cells.append("".join(current).strip())
            current.clear()
            index += 1
            continue
        current.append(char)
        index += 1
    cells.append("".join(current).strip())
    return cells


def is_table(lines: list[str], index: int) -> bool:
    return (
        index + 1 < len(lines)
        and lines[index].strip().startswith("|")
        and lines[index + 1].strip().startswith("|")
        and "---" in lines[index + 1]
    )


def render_table(lines: list[str], index: int, link_prefix: str) -> tuple[str, int]:
    headers = split_table_row(lines[index])
    index += 2
    rows = []
    while index < len(lines) and lines[index].strip().startswith("|"):
        rows.append(split_table_row(lines[index]))
        index += 1

    head_html = "".join(f"<th>{convert_inline(cell, link_prefix)}</th>" for cell in headers)
    body_html = []
    for row in rows:
        cells = "".join(f"<td>{convert_inline(cell, link_prefix)}</td>" for cell in row)
        body_html.append(f"<tr>{cells}</tr>")

    return (
        '<div class="table-wrap"><table><thead><tr>'
        + head_html
        + "</tr></thead><tbody>"
        + "".join(body_html)
        + "</tbody></table></div>",
        index,
    )


def render_markdown(markdown: str, link_prefix: str = "./articles/") -> str:
    lines = markdown.replace("\r\n", "\n").split("\n")
    output: list[str] = []
    list_stack: list[str] = []
    paragraph: list[str] = []
    quote: list[str] = []

    def flush_paragraph() -> None:
        if paragraph:
            output.append("<p>" + convert_inline(" ".join(paragraph).strip(), link_prefix) + "</p>")
            paragraph.clear()

    def flush_quote() -> None:
        if quote:
            output.append(
                "<blockquote>"
                + "".join(f"<p>{convert_inline(q, link_prefix)}</p>" for q in quote)
                + "</blockquote>"
            )
            quote.clear()

    def close_lists(target_indent: int = -1) -> None:
        while list_stack and len(list_stack) - 1 > target_indent:
            output.append(f"</{list_stack.pop()}>")

    index = 0
    while index < len(lines):
        line = lines[index].rstrip()
        stripped = line.strip()

        if not stripped:
            flush_paragraph()
            flush_quote()
            close_lists()
            index += 1
            continue

        if is_table(lines, index):
            flush_paragraph()
            flush_quote()
            close_lists()
            table_html, index = render_table(lines, index, link_prefix)
            output.append(table_html)
            continue

        heading = re.match(r"^(#{1,4})\s+(.+)$", stripped)
        if heading:
            flush_paragraph()
            flush_quote()
            close_lists()
            level = len(heading.group(1))
            output.append(f"<h{level}>{convert_inline(heading.group(2), link_prefix)}</h{level}>")
            index += 1
            continue

        if stripped.startswith(">"):
            flush_paragraph()
            close_lists()
            quote.append(stripped.lstrip("> ").strip())
            index += 1
            continue

        checklist = re.match(r"^(\s*)-\s+\[( |x|X)\]\s+(.+)$", line)
        bullet = re.match(r"^(\s*)[-*]\s+(.+)$", line)
        numbered = re.match(r"^(\s*)\d+\.\s+(.+)$", line)
        list_match = checklist or bullet or numbered
        if list_match:
            flush_paragraph()
            flush_quote()
            indent = len(list_match.group(1)) // 2
            tag = "ol" if numbered else "ul"
            while len(list_stack) <= indent:
                list_stack.append(tag)
                output.append(f'<{tag} class="task-list">' if checklist else f"<{tag}>")
            close_lists(indent)
            if list_stack and list_stack[-1] != tag:
                output.append(f"</{list_stack.pop()}>")
                list_stack.append(tag)
                output.append(f"<{tag}>")
            if checklist:
                checked = " checked" if checklist.group(2).lower() == "x" else ""
                text = checklist.group(3)
                output.append(f'<li><input type="checkbox" disabled{checked}> {convert_inline(text, link_prefix)}</li>')
            else:
                text = list_match.group(2)
                output.append(f"<li>{convert_inline(text, link_prefix)}</li>")
            index += 1
            continue

        close_lists()
        paragraph.append(stripped)
        index += 1

    flush_paragraph()
    flush_quote()
    close_lists()
    return "\n".join(output)


def page_shell(title: str, body: str, current: str = "") -> str:
    nav = [
        ("index.html", "홈"),
        ("index.html#watchlist", "관심종목"),
        ("index.html#companies", "기업분석"),
        ("index.html#daily", "데일리"),
        ("index.html#principles", "원칙"),
    ]
    prefix = "../" if current == "article" else ""
    nav_html = "".join(f'<a href="{prefix}{href}">{label}</a>' for href, label in nav)
    return f"""<!doctype html>
<html lang="ko">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{html.escape(title)} | HowlNode Stock</title>
    <link rel="stylesheet" href="{prefix}styles.css">
  </head>
  <body>
    <header class="site-header">
      <a class="brand" href="{prefix}index.html">
        <span class="brand-mark">HN</span>
        <span><strong>HowlNode</strong><small>Stock Notes</small></span>
      </a>
      <nav>{nav_html}</nav>
    </header>
    {body}
  </body>
</html>
"""


def extract_watchlist(markdown: str) -> str:
    rendered = render_markdown(markdown)
    return rendered


def card(page: SourcePage) -> str:
    slug = slug_for(page.source)
    badge = f'<span class="stock-badge">{html.escape(page.ticker)}</span>' if page.ticker else ""
    summary = f"<p>{html.escape(page.summary)}</p>" if page.summary else ""
    return f'<article class="card"><a href="./articles/{slug}.html"><span>{html.escape(page.group)}</span><h3>{html.escape(page.title)}</h3>{badge}{summary}</a></article>'


def tv_widget(page: SourcePage) -> str:
    if not page.tv_symbol:
        return ""

    if page.tv_symbol.startswith("KRX:"):
        url = f"https://finance.naver.com/item/main.naver?code={page.ticker}"
        return (
            '<div class="naver-widget">'
            '<div class="naver-widget__info">'
            '<span class="naver-widget__market">KOSPI</span>'
            f'<span class="naver-widget__ticker">{html.escape(page.ticker)}</span>'
            f'<span class="naver-widget__name">{html.escape(page.title)}</span>'
            '</div>'
            f'<a class="naver-widget__btn" href="{url}" target="_blank" rel="noopener">네이버 증권에서 보기 →</a>'
            '</div>'
        )

    sym = page.tv_symbol
    return (
        '<div class="tv-widget-wrap">'
        '<div class="tradingview-widget-container">'
        '<div class="tradingview-widget-container__widget"></div>'
        '<script type="text/javascript" '
        'src="https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js" async>'
        '{"width":"100%","height":320,"symbol":"' + sym + '",'
        '"interval":"D","timezone":"Asia/Seoul","theme":"light","style":"1",'
        '"locale":"ko","toolbar_bg":"#ffffff","enable_publishing":false,'
        '"hide_top_toolbar":false,"hide_legend":false,"save_image":false}'
        '</script>'
        '</div>'
        '</div>'
    )


def build_index() -> str:
    project = render_markdown(read_source(PAGES[0]))
    watchlist = extract_watchlist(read_source(PAGES[1]))
    principles = render_markdown(read_source(PAGES[2]))
    checklist = render_markdown(read_source(PAGES[3]))
    company_cards = "\n".join(card(page) for page in PAGES if page.group == "company")
    daily_cards = "\n".join(card(page) for page in PAGES if page.group == "daily")

    body = f"""
    <main>
      <section class="hero compact-hero">
        <div>
          <p class="eyebrow">HowlNode Stock</p>
          <h1>관심 종목과 매매 판단 기록</h1>
          <p>기업별 투자 가설, 실적 이벤트 복기, 매수 판단 기준을 한 화면에서 확인합니다.</p>
        </div>
        <aside class="hero-panel">
          <strong>현재 초점</strong>
          <p>삼성전기, 알파벳, 엔비디아, 블룸에너지를 중심으로 사업 구조·숫자·수급·자리를 점검합니다.</p>
        </aside>
      </section>

      <section id="companies" class="section first-section">
        <div class="section-heading">
          <p class="eyebrow">Company Analysis</p>
          <h2>기업분석</h2>
        </div>
        <div class="card-grid feature-grid">{company_cards}</div>
      </section>

      <section id="daily" class="section">
        <div class="section-heading">
          <p class="eyebrow">Daily Review</p>
          <h2>데일리 기록</h2>
        </div>
        <div class="card-grid daily-grid">{daily_cards}</div>
      </section>

      <section id="watchlist" class="section">
        <div class="section-heading">
          <p class="eyebrow">Watchlist</p>
          <h2>현재 관심종목 상태</h2>
        </div>
        <article class="content-card wide">{watchlist}</article>
      </section>

      <section class="section">
        <div class="section-heading">
          <p class="eyebrow">Direction</p>
          <h2>투자 기록 방향</h2>
        </div>
        <article class="content-card">{project}</article>
      </section>

      <section id="principles" class="content-grid section">
        <article class="content-card">{principles}</article>
        <article class="content-card">{checklist}</article>
      </section>
    </main>
"""
    return page_shell("홈", body)


def build_article(page: SourcePage) -> str:
    content = render_markdown(read_source(page), link_prefix="./")
    widget = tv_widget(page)
    body = f"""
    <main class="article-layout">
      <a class="back-link" href="../index.html">← 홈으로</a>
      {widget}
      <article class="article-body">{content}</article>
    </main>
"""
    return page_shell(page.title, body, current="article")


def write_styles() -> None:
    css = (
        "*{box-sizing:border-box}"
        "body{margin:0;background:#f6f7f9;color:#17202a;font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,\"Segoe UI\",sans-serif;line-height:1.65}"
        "a{color:inherit;text-decoration:none}"
        ".site-header{position:sticky;top:0;z-index:10;display:flex;align-items:center;justify-content:space-between;gap:24px;min-height:72px;padding:14px clamp(18px,5vw,72px);border-bottom:1px solid #dfe4ec;background:rgba(246,247,249,.94);backdrop-filter:blur(14px)}"
        ".brand{display:flex;align-items:center;gap:12px;min-width:190px}"
        ".brand-mark{display:grid;width:40px;height:40px;place-items:center;border-radius:8px;background:#17202a;color:#fff;font-size:13px;font-weight:800}"
        ".brand strong,.brand small{display:block;line-height:1.1}"
        ".brand small{margin-top:4px;color:#667085}"
        ".site-header nav{display:flex;flex-wrap:wrap;justify-content:flex-end;gap:8px}"
        ".site-header nav a{padding:8px 10px;border-radius:8px;color:#667085;font-size:14px;font-weight:700}"
        ".site-header nav a:hover{background:#e9edf3;color:#17202a}"
        "main{width:min(1160px,calc(100% - 40px));margin:0 auto}"
        ".hero{display:grid;grid-template-columns:minmax(0,1.1fr) minmax(300px,.6fr);gap:28px;align-items:end;padding:54px 0 22px}"
        ".compact-hero{min-height:auto}"
        ".hero h1{max-width:820px;margin:0;font-size:clamp(38px,6vw,70px);line-height:1.03}"
        ".hero p{max-width:660px;margin:16px 0 0;color:#667085;font-size:18px}"
        ".eyebrow{margin:0 0 10px;color:#0f766e;font-size:13px;font-weight:800;text-transform:uppercase}"
        ".hero-panel,.content-card,.card{border:1px solid #dfe4ec;border-radius:8px;background:#fff;box-shadow:0 18px 45px rgba(18,24,40,.08)}"
        ".card{overflow:hidden}"
        ".hero-panel{padding:22px}"
        ".hero-panel p{font-size:15px}"
        ".content-grid{display:grid;grid-template-columns:1fr 1fr;gap:22px}"
        ".content-card{padding:24px;overflow:hidden}"
        ".content-card.wide{padding:0}"
        ".section{padding:34px 0}"
        ".first-section{padding-top:18px}"
        ".section-heading{margin-bottom:18px}"
        ".section-heading h2,h2,h3{margin:0;line-height:1.2}"
        "h1,h2,h3,h4{letter-spacing:0}"
        "h1+*,h2+*,h3+*,h4+*{margin-top:14px}"
        ".content-card h1,.article-body h1{font-size:32px}"
        ".content-card h2,.article-body h2{margin-top:28px;font-size:24px}"
        ".content-card h3,.article-body h3{margin-top:22px;font-size:19px}"
        "p,li{color:#344054}"
        "strong{color:#17202a}"
        ".table-wrap{width:100%;overflow:auto}"
        "table{width:100%;min-width:720px;border-collapse:collapse;background:#fff}"
        "th,td{padding:14px 16px;border-bottom:1px solid #dfe4ec;text-align:left;vertical-align:top}"
        "th{color:#667085;font-size:13px;text-transform:uppercase}"
        "td:first-child,th:first-child{padding-left:22px}"
        "tbody tr:last-child td{border-bottom:0}"
        "ul,ol{padding-left:22px}"
        "li{margin:6px 0}"
        ".task-list{list-style:none;padding-left:0}"
        ".task-list input{margin-right:8px}"
        "blockquote{margin:20px 0;padding:14px 18px;border-left:4px solid #0f766e;background:#eef8f6;border-radius:0 8px 8px 0}"
        "blockquote p{margin:0;color:#17202a;font-weight:700}"
        "code{padding:2px 6px;border-radius:6px;background:#eef2f7;color:#17202a}"
        ".card-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px}"
        ".feature-grid .card a{min-height:210px}"
        ".daily-grid{grid-template-columns:repeat(auto-fill,minmax(160px,1fr))}"
        ".daily-grid .card a{min-height:142px}"
        ".card a{display:block;min-height:160px;padding:20px}"
        ".card a:hover{background:#fbfcfe}"
        ".card span{color:#0f766e;font-size:12px;font-weight:800;text-transform:uppercase}"
        ".card h3{margin-top:10px;font-size:24px;overflow-wrap:break-word;word-break:break-word}"
        ".daily-grid .card h3{font-size:20px}"
        ".card p{margin:12px 0 0;color:#667085;overflow-wrap:break-word;word-break:break-word}"
        ".stock-badge{display:inline-block;margin-top:8px;padding:3px 8px;border-radius:4px;"
        "background:#f0faf7;border:1px solid #b6e8d8;color:#0f766e;font-size:11px;font-weight:700;letter-spacing:.03em}"
        ".tv-widget-wrap{margin-bottom:24px;border-radius:8px;overflow:hidden;border:1px solid #dfe4ec}"
        ".naver-widget{display:flex;align-items:center;justify-content:space-between;gap:16px;"
        "margin-bottom:24px;padding:16px 20px;border-radius:8px;border:1px solid #dfe4ec;background:#fff}"
        ".naver-widget__info{display:flex;align-items:center;gap:10px;flex-wrap:wrap}"
        ".naver-widget__market{padding:2px 8px;border-radius:4px;background:#e8f5e9;color:#2e7d32;"
        "font-size:11px;font-weight:700}"
        ".naver-widget__ticker{font-size:15px;font-weight:700;color:#17202a}"
        ".naver-widget__name{color:#667085;font-size:14px}"
        ".naver-widget__btn{display:inline-flex;align-items:center;padding:8px 16px;border-radius:6px;"
        "background:#03c75a;color:#fff;font-size:13px;font-weight:700;white-space:nowrap;flex-shrink:0}"
        ".naver-widget__btn:hover{background:#02b350}"
        ".article-layout{max-width:880px;padding:40px 0 70px}"
        ".back-link{display:inline-flex;margin-bottom:18px;color:#0f766e;font-weight:800}"
        ".article-body{padding:30px;border:1px solid #dfe4ec;border-radius:8px;background:#fff;box-shadow:0 18px 45px rgba(18,24,40,.08)}"
        ".article-body a,.content-card a{color:#0f766e;font-weight:800}"
        "@media(max-width:860px){"
        ".site-header{align-items:flex-start;flex-direction:column}"
        ".site-header nav{justify-content:flex-start}"
        ".hero,.content-grid{grid-template-columns:1fr}"
        ".hero{padding-top:44px}"
        ".hero h1{font-size:44px}}"
        "@media(max-width:560px){"
        "main{width:min(100% - 28px,1160px)}"
        ".card-grid,.daily-grid{grid-template-columns:1fr}"
        ".hero h1{font-size:36px}"
        ".content-card,.article-body{padding:18px}"
        "th,td{padding:12px}}\n"
    )
    (PUBLIC / "styles.css").write_text(css, encoding="utf-8")


def build() -> None:
    if not VAULT.exists():
        raise FileNotFoundError(f"Vault folder not found: {VAULT}")
    if PUBLIC.exists():
        for child in PUBLIC.iterdir():
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()
    else:
        PUBLIC.mkdir(parents=True, exist_ok=True)
    ARTICLES.mkdir(parents=True, exist_ok=True)
    write_styles()
    (PUBLIC / "index.html").write_text(build_index(), encoding="utf-8")
    for page in PAGES:
        slug = slug_for(page.source)
        (ARTICLES / f"{slug}.html").write_text(build_article(page), encoding="utf-8")


if __name__ == "__main__":
    build()
    print(f"Built site from {VAULT}")
    print(f"Output: {PUBLIC}")
