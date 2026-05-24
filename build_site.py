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
    label = {"company": "기업", "daily": "기록", "dashboard": "정리"}.get(page.group, page.group)
    return f'<article class="card"><a href="./articles/{slug}.html"><span>{html.escape(label)}</span><h3>{html.escape(page.title)}</h3>{badge}{summary}</a></article>'


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
        '"interval":"D","timezone":"Asia/Seoul","theme":"dark","style":"1",'
        '"locale":"ko","toolbar_bg":"#161b22","enable_publishing":false,'
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
    company_count = sum(1 for page in PAGES if page.group == "company")
    daily_count = sum(1 for page in PAGES if page.group == "daily")
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

      <section class="stats">
        <div class="stat-card">
          <div class="stat-value">{company_count}</div>
          <div class="stat-label">기업분석</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{daily_count}</div>
          <div class="stat-label">데일리 기록</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">4</div>
          <div class="stat-label">핵심 판단 요소</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">10%</div>
          <div class="stat-label">암호화폐 별도 운용</div>
        </div>
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
    css = """
:root{--bg:#0d1117;--panel:#161b22;--panel-2:#0f141b;--border:#30363d;--text:#c9d1d9;--muted:#8b949e;--accent:#58a6ff;--green:#3fb950;--red:#f85149;--yellow:#d29922;--orange:#f0883e}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Apple SD Gothic Neo","Malgun Gothic",sans-serif;padding:16px;font-size:14px;line-height:1.55}
a{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline}
.site-header{position:sticky;top:0;z-index:10;max-width:1280px;margin:0 auto 16px;display:flex;align-items:center;justify-content:space-between;gap:12px;padding:8px 0 12px;border-bottom:1px solid var(--border);background:rgba(13,17,23,.94);backdrop-filter:blur(12px)}
.brand{display:flex;align-items:center;gap:10px;color:var(--text)}.brand-mark{display:grid;width:34px;height:34px;place-items:center;border:1px solid var(--border);border-radius:8px;background:var(--panel);color:var(--accent);font-size:12px;font-weight:800}.brand strong,.brand small{display:block;line-height:1.1}.brand small{margin-top:3px;color:var(--muted);font-size:12px}
.site-header nav{display:flex;flex-wrap:wrap;justify-content:flex-end;gap:6px}.site-header nav a{padding:5px 9px;border:1px solid transparent;border-radius:6px;color:var(--muted);font-size:13px;font-weight:600}.site-header nav a:hover{border-color:var(--border);background:var(--panel);color:var(--text);text-decoration:none}
main{width:min(1280px,100%);margin:0 auto}
.hero{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(300px,.65fr);gap:16px;align-items:stretch;padding:4px 0 16px}.compact-hero{min-height:auto}.hero>div,.hero-panel{background:var(--panel);border:1px solid var(--border);border-radius:8px;padding:16px}.hero h1{max-width:880px;margin:0;font-size:24px;line-height:1.2}.hero p{max-width:760px;margin:10px 0 0;color:var(--muted);font-size:14px}.hero-panel strong{color:var(--accent);font-size:15px}.hero-panel p{font-size:13px}
.eyebrow{margin:0 0 8px;color:var(--accent);font-size:12px;font-weight:700;text-transform:uppercase}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:16px}.stat-card{background:var(--panel);border:1px solid var(--border);border-radius:8px;padding:12px 14px}.stat-value{font-size:22px;font-weight:700;color:var(--accent);line-height:1}.stat-label{font-size:12px;color:var(--muted);margin-top:6px}
.section{padding:0 0 16px}.first-section{padding-top:0}.section-heading{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:10px}.section-heading h2,h2,h3{margin:0;line-height:1.2}.section-heading h2{font-size:15px;color:var(--accent)}h1,h2,h3,h4{letter-spacing:0}h1+*,h2+*,h3+*,h4+*{margin-top:10px}
.content-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}.content-card,.card{background:var(--panel);border:1px solid var(--border);border-radius:8px}.content-card{padding:14px;overflow:hidden}.content-card.wide{padding:0}.content-card h1,.article-body h1{font-size:22px}.content-card h2,.article-body h2{margin-top:22px;font-size:16px;color:var(--accent)}.content-card h3,.article-body h3{margin-top:18px;font-size:14px;color:var(--text)}p,li{color:var(--text)}.content-card p,.article-body p{color:var(--text)}strong{color:var(--text)}
.card-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:10px}.daily-grid{grid-template-columns:repeat(auto-fill,minmax(150px,1fr))}.card{overflow:hidden}.card a{display:block;min-height:132px;padding:14px}.feature-grid .card a{min-height:168px}.daily-grid .card a{min-height:112px}.card a:hover{background:#1f2937;text-decoration:none}.card span{color:var(--muted);font-size:11px;font-weight:700;text-transform:uppercase}.card h3{margin-top:8px;font-size:19px;overflow-wrap:break-word;word-break:break-word}.daily-grid .card h3{font-size:17px}.card p{margin:10px 0 0;color:var(--muted);font-size:13px;overflow-wrap:break-word;word-break:break-word}.stock-badge{display:inline-block;margin-top:8px;padding:2px 8px;border-radius:10px;background:#1c2e3a;color:var(--accent);font-size:11px;font-weight:700;letter-spacing:.03em}
.table-wrap{width:100%;overflow:auto}table{width:100%;min-width:720px;border-collapse:collapse;background:var(--panel);font-size:13px}th,td{padding:8px 10px;border-bottom:1px solid var(--border);text-align:left;vertical-align:top}th{color:var(--muted);font-weight:500;font-size:12px;text-transform:none}tbody tr:last-child td{border-bottom:0}td:first-child{color:var(--muted)}
ul,ol{padding-left:20px}li{margin:5px 0}.task-list{list-style:none;padding-left:0}.task-list input{margin-right:8px;accent-color:var(--accent)}blockquote{margin:16px 0;padding:12px 14px;border-left:3px solid var(--accent);background:#111a24;border-radius:0 8px 8px 0}blockquote p{margin:0;color:var(--text);font-weight:600}code{padding:2px 6px;border-radius:4px;background:var(--bg);border:1px solid var(--border);color:var(--text);font-size:.92em}
.tv-widget-wrap{margin-bottom:16px;border-radius:8px;overflow:hidden;border:1px solid var(--border);background:var(--panel)}.naver-widget{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:16px;padding:14px;border-radius:8px;border:1px solid var(--border);background:var(--panel)}.naver-widget__info{display:flex;align-items:center;gap:9px;flex-wrap:wrap}.naver-widget__market{padding:2px 8px;border-radius:10px;background:#1c3a1c;color:var(--green);font-size:11px;font-weight:700}.naver-widget__ticker{font-size:15px;font-weight:700;color:var(--accent)}.naver-widget__name{color:var(--muted);font-size:13px}.naver-widget__btn{display:inline-flex;align-items:center;padding:6px 12px;border-radius:6px;border:1px solid #235c37;background:#1c3a1c;color:var(--green);font-size:13px;font-weight:700;white-space:nowrap;flex-shrink:0}.naver-widget__btn:hover{background:#254d2d;text-decoration:none}
.article-layout{max-width:960px;padding:18px 0 54px}.back-link{display:inline-flex;margin-bottom:12px;color:var(--accent);font-weight:700}.article-body{padding:18px;border:1px solid var(--border);border-radius:8px;background:var(--panel)}.article-body a,.content-card a{color:var(--accent);font-weight:700}
@media(max-width:900px){body{padding:10px}.site-header{align-items:flex-start;flex-direction:column}.site-header nav{justify-content:flex-start}.hero,.content-grid{grid-template-columns:1fr}.stats{grid-template-columns:repeat(2,1fr)}table{font-size:12px}th,td{padding:7px 8px}}
@media(max-width:560px){.card-grid,.daily-grid{grid-template-columns:1fr}.hero h1{font-size:22px}.content-card,.article-body{padding:14px}.stats{grid-template-columns:1fr 1fr}}
"""
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
