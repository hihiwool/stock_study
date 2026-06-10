from __future__ import annotations

import html
import re
import shutil
from dataclasses import dataclass, field
from datetime import date
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
    group: str  # "company" | "daily" | "dashboard"
    summary: str = ""
    ticker: str = ""
    tv_symbol: str = ""
    market: str = ""           # "코스피" | "나스닥" | "뉴욕"
    status: str = ""           # "핵심 후보" | "성장 후보" | "관찰" | "고위험 관찰" | "후보"
    day_no: int = 0            # daily 노트의 Day 번호
    tags: tuple = field(default_factory=tuple)  # daily 노트가 다룬 종목 키


PAGES = [
    # 대시보드/원칙류
    SourcePage("00_대시보드/프로젝트_방향.md", "프로젝트 방향", "dashboard"),
    SourcePage("00_대시보드/현재_관심종목_상태.md", "현재 관심종목 상태", "dashboard"),
    SourcePage("00_대시보드/누적_투자_원칙.md", "누적 투자 원칙", "dashboard"),
    SourcePage("00_대시보드/체크리스트.md", "체크리스트", "dashboard"),
    # 기업분석
    SourcePage(
        "02_기업분석/삼성전기.md", "삼성전기", "company",
        summary="AI 서버/데이터센터용 FCBGA + 고부가 MLCC 구조적 수혜 가설",
        ticker="009150", tv_symbol="KRX:009150",
        market="코스피", status="핵심 후보",
    ),
    SourcePage(
        "02_기업분석/알파벳.md", "알파벳", "company",
        summary="Search 방어력 + Google Cloud 성장 + 자체 TPU/Gemini",
        ticker="GOOGL", tv_symbol="NASDAQ:GOOGL",
        market="나스닥", status="핵심 후보",
    ),
    SourcePage(
        "02_기업분석/엔비디아.md", "엔비디아", "company",
        summary="AI 데이터센터 Compute + Networking, Blackwell, 중국 리스크",
        ticker="NVDA", tv_symbol="NASDAQ:NVDA",
        market="나스닥", status="핵심 후보",
    ),
    SourcePage(
        "02_기업분석/신세계.md", "신세계", "company",
        summary="백화점 기존점 성장률, 리뉴얼 효과, 면세점 흑자 전환 지속성 확인",
        ticker="004170", tv_symbol="KRX:004170",
        market="코스피", status="관찰",
    ),
    SourcePage(
        "02_기업분석/LS에코에너지.md", "LS에코에너지", "company",
        summary="AI 데이터센터 전력 케이블 사례는 있으나 반복 수주·계약 규모 미확인",
        ticker="229640", tv_symbol="KRX:229640",
        market="코스피", status="후순위 관찰",
    ),
    SourcePage(
        "02_기업분석/블룸에너지.md", "블룸에너지", "company",
        summary="AI 데이터센터 전력 수요 + 분산형 연료전지, Nebius 파트너십",
        ticker="BE", tv_symbol="NYSE:BE",
        market="뉴욕", status="성장 후보",
    ),
    SourcePage(
        "02_기업분석/울프스피드.md", "울프스피드", "company",
        summary="Chapter 11 이후 부채는 줄었지만 기존 주주 희석·마진 회복 리스크 큼",
        ticker="WOLF", tv_symbol="NYSE:WOLF",
        market="뉴욕", status="후순위 관찰",
    ),
    # 데일리
    SourcePage(
        "01_데일리_숙제/Day 1 - 관심종목 등록 및 삼성전기 분석.md",
        "Day 1 · 관심종목 등록 + 삼성전기 분석", "daily",
        summary="AI 수혜주라는 막연한 표현을 검증 가능한 가설로 바꾸는 첫 연습",
        day_no=1, tags=("신세계", "삼성전기", "LS에코에너지", "알파벳", "울프스피드", "블룸에너지"),
    ),
    SourcePage(
        "01_데일리_숙제/Day 2 - 알파벳 분석.md",
        "Day 2 · 알파벳 분석", "daily",
        summary="Search 방어력 + 클라우드 성장 + 자체 TPU 기반 AI 인프라 검증",
        day_no=2, tags=("알파벳",),
    ),
    SourcePage(
        "01_데일리_숙제/Day 3 - 엔비디아 실적 프리뷰.md",
        "Day 3 · 엔비디아 실적 프리뷰", "daily",
        summary="실적 발표 전 데이터센터 매출/가이던스/GM 기준 설정",
        day_no=3, tags=("엔비디아",),
    ),
    SourcePage(
        "01_데일리_숙제/Day 4 - 엔비디아 실적 발표 확인.md",
        "Day 4 · 엔비디아 실적 발표 확인", "daily",
        summary="실제 실적과 사전 기준 비교, Compute·Networking 동반 성장",
        day_no=4, tags=("엔비디아",),
    ),
    SourcePage(
        "01_데일리_숙제/Day 5 - 엔비디아 실적 후 복기.md",
        "Day 5 · 엔비디아 실적 후 복기", "daily",
        summary="좋은 실적과 좋은 매수 타이밍이 다르다는 점 복기",
        day_no=5, tags=("엔비디아",),
    ),
    SourcePage(
        "01_데일리_숙제/Day 6 - 블룸에너지 투자 아이디어 정리.md",
        "Day 6 · 블룸에너지 투자 아이디어", "daily",
        summary="AI 데이터센터 전력 수요 → 블룸에너지 수혜 가설과 리스크 정리",
        day_no=6, tags=("블룸에너지",),
    ),
    SourcePage(
        "01_데일리_숙제/Day 7 - LS에코에너지 확인 데이터.md",
        "Day 7 · LS에코에너지 확인 데이터", "daily",
        summary="60MW AI 데이터센터 케이블 공급과 실적·수급·주가 과열 여부 점검",
        day_no=7, tags=("LS에코에너지",),
    ),
    SourcePage(
        "01_데일리_숙제/Day 8 - 신세계 투자 아이디어 점검.md",
        "Day 8 · 신세계 투자 아이디어 점검", "daily",
        summary="코스피 상승 수혜 가설을 백화점·면세점 실적 개선 데이터로 재검증",
        day_no=8, tags=("신세계",),
    ),
    SourcePage(
        "01_데일리_숙제/Day 9 - 울프스피드 투자 아이디어 점검.md",
        "Day 9 · 울프스피드 투자 아이디어 점검", "daily",
        summary="AI 전력 효율 수혜 가설보다 구조조정·주주 희석·마진 회복 리스크를 우선 점검",
        day_no=9, tags=("울프스피드",),
    ),
    SourcePage(
        "01_데일리_숙제/Day 10 - 삼성전기 2차 체크.md",
        "Day 10 · 삼성전기 2차 체크", "daily",
        summary="AI 부품 수혜 가설과 외국인·기관 수급, 급등 이후 가격 부담을 점검",
        day_no=10, tags=("삼성전기",),
    ),
    SourcePage(
        "01_데일리_숙제/Day 11 - 알파벳 2차 체크.md",
        "Day 11 · 알파벳 2차 체크", "daily",
        summary="Google Cloud 성장과 AI Capex 부담, 주가 눌림 구간을 함께 점검",
        day_no=11, tags=("알파벳",),
    ),
    SourcePage(
        "01_데일리_숙제/Day 12 - 엔비디아 2차 체크.md",
        "Day 12 · 엔비디아 2차 체크", "daily",
        summary="Compute·Networking 성장과 중국 리스크, 실적 이후 주가 반응을 점검",
        day_no=12, tags=("엔비디아",),
    ),
    SourcePage(
        "01_데일리_숙제/Day 13 - 코스피 3종 비교 정리.md",
        "Day 13 · 코스피 3종 비교 정리", "daily",
        summary="삼성전기·신세계·LS에코에너지를 비교해 매수 우선순위와 대기 조건을 정리",
        day_no=13, tags=("삼성전기", "신세계", "LS에코에너지"),
    ),
    SourcePage(
        "01_데일리_숙제/Day 14 - 관심종목 업데이트.md",
        "Day 14 · 관심종목 업데이트", "daily",
        summary="SK하이닉스·LS ELECTRIC·Micron 신규 추가, 울프스피드·LS에코에너지는 후순위 관찰로 조정",
        day_no=14, tags=("SK하이닉스", "LS ELECTRIC", "Micron", "울프스피드", "LS에코에너지"),
    ),
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
    "02_기업분석/신세계.md": "company-shinsegae",
    "02_기업분석/LS에코에너지.md": "company-ls-eco-energy",
    "02_기업분석/블룸에너지.md": "company-bloom-energy",
    "02_기업분석/울프스피드.md": "company-wolfspeed",
    "01_데일리_숙제/Day 1 - 관심종목 등록 및 삼성전기 분석.md": "daily-day-1",
    "01_데일리_숙제/Day 2 - 알파벳 분석.md": "daily-day-2",
    "01_데일리_숙제/Day 3 - 엔비디아 실적 프리뷰.md": "daily-day-3",
    "01_데일리_숙제/Day 4 - 엔비디아 실적 발표 확인.md": "daily-day-4",
    "01_데일리_숙제/Day 5 - 엔비디아 실적 후 복기.md": "daily-day-5",
    "01_데일리_숙제/Day 6 - 블룸에너지 투자 아이디어 정리.md": "daily-day-6",
    "01_데일리_숙제/Day 7 - LS에코에너지 확인 데이터.md": "daily-day-7",
    "01_데일리_숙제/Day 8 - 신세계 투자 아이디어 점검.md": "daily-day-8",
    "01_데일리_숙제/Day 9 - 울프스피드 투자 아이디어 점검.md": "daily-day-9",
    "01_데일리_숙제/Day 10 - 삼성전기 2차 체크.md": "daily-day-10",
    "01_데일리_숙제/Day 11 - 알파벳 2차 체크.md": "daily-day-11",
    "01_데일리_숙제/Day 12 - 엔비디아 2차 체크.md": "daily-day-12",
    "01_데일리_숙제/Day 13 - 코스피 3종 비교 정리.md": "daily-day-13",
    "01_데일리_숙제/Day 14 - 관심종목 업데이트.md": "daily-day-14",
}


def slug_for(source: str) -> str:
    if source in SLUG_BY_SOURCE:
        return SLUG_BY_SOURCE[source]
    stem = Path(source).with_suffix("").as_posix()
    slug = re.sub(r"[^0-9A-Za-z가-힣]+", "-", stem).strip("-").lower()
    return quote(slug)


SLUGS = {Path(page.source).with_suffix("").as_posix(): slug_for(page.source) for page in PAGES}
SLUGS.update({Path(page.source).stem: slug_for(page.source) for page in PAGES})


# 빌드 시 한번만 파싱해서 캐시
_SOURCE_CACHE: dict[str, str] = {}


def read_source(page: SourcePage) -> str:
    if page.source in _SOURCE_CACHE:
        return _SOURCE_CACHE[page.source]
    path = VAULT / page.source
    if not path.exists():
        raise FileNotFoundError(f"Missing source file: {path}")
    text = path.read_text(encoding="utf-8")
    _SOURCE_CACHE[page.source] = text
    return text


def extract_date(markdown: str, label: str) -> str:
    """`## 작성일\n2026-05-22` 같은 헤더 다음 줄에서 날짜 추출"""
    m = re.search(rf"^##\s*{re.escape(label)}\s*$", markdown, re.MULTILINE)
    if m:
        rest = markdown[m.end():].lstrip()
        first = rest.split("\n", 1)[0].strip()
        date_m = re.match(r"(\d{4}-\d{2}-\d{2})", first)
        if date_m:
            return date_m.group(1)
    return ""


def extract_table_value(markdown: str, key: str) -> str:
    """`| 마지막 업데이트 | 2026-05-22 |` 같은 표에서 값 추출"""
    for line in markdown.split("\n"):
        m = re.match(r"^\|\s*" + re.escape(key) + r"\s*\|\s*(.+?)\s*\|", line)
        if m:
            return m.group(1).strip()
    return ""


def company_last_updated(page: SourcePage) -> str:
    md = read_source(page)
    v = extract_table_value(md, "마지막 업데이트")
    if v:
        return v
    return extract_table_value(md, "최초 작성일")


def daily_date(page: SourcePage) -> str:
    md = read_source(page)
    return extract_date(md, "작성일")


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

        heading = re.match(r"^(#{1,6})\s+(.+)$", stripped)
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


# ---------------- 워치리스트 / 상태 헬퍼 ----------------

STATUS_CLASS = {
    "핵심 후보": "core",
    "성장 후보": "growth",
    "관찰": "watch",
    "고위험 관찰": "risk",
    "후보": "candidate",
    "신규 추가": "new",
    "후순위 관찰": "deprioritized",
}

MARKET_CLASS = {
    "코스피": "kospi",
    "나스닥": "nasdaq",
    "뉴욕": "nyse",
}


def parse_watchlist(markdown: str) -> list[dict]:
    """현재 관심종목 상태.md 표 파싱"""
    lines = markdown.replace("\r\n", "\n").split("\n")
    items: list[dict] = []
    for i, line in enumerate(lines):
        if not line.strip().startswith("|"):
            continue
        if i + 1 < len(lines) and "---" in lines[i + 1]:
            continue
        if "---" in line:
            continue
        cells = split_table_row(line)
        if len(cells) < 4:
            continue
        if cells[0].strip() in ("시장", ""):
            continue
        market = cells[0].strip()
        name_raw = cells[1].strip()
        status = cells[2].strip()
        reason = cells[3].strip()

        # [[02_기업분석/삼성전기|삼성전기]] 같은 링크 파싱
        link_m = re.match(r"\[\[([^\]]+)\]\]", name_raw)
        slug = ""
        if link_m:
            inner = link_m.group(1)
            target, _, label = inner.partition("|")
            label = label.strip() or Path(target).stem
            key = Path(target).with_suffix("").as_posix()
            fallback = Path(target).stem
            slug = SLUGS.get(key, "") or SLUGS.get(fallback, "")
            name = label
        else:
            name = name_raw

        items.append({
            "market": market,
            "name": name,
            "status": status,
            "reason": reason,
            "slug": slug,
        })
    return items


# ---------------- 카드/위젯 ----------------

def status_badge(status: str) -> str:
    cls = STATUS_CLASS.get(status, "watch")
    return f'<span class="status-pill status-{cls}">{html.escape(status)}</span>'


def market_badge(market: str) -> str:
    cls = MARKET_CLASS.get(market, "")
    return f'<span class="market-pill market-{cls}">{html.escape(market)}</span>'


def watchlist_strip(items: list[dict]) -> str:
    """상단에 항상 보이는 가로 관심종목 스트립"""
    cards = []
    for it in items:
        title = html.escape(it["name"])
        reason = html.escape(it["reason"])
        market = market_badge(it["market"])
        status = status_badge(it["status"])
        href = f'./articles/{it["slug"]}.html' if it["slug"] else "#"
        clickable = "watch-card" + ("" if it["slug"] else " watch-card--static")
        tag = "a" if it["slug"] else "div"
        cards.append(
            f'<{tag} class="{clickable}"'
            + (f' href="{href}"' if it["slug"] else "")
            + f'><div class="watch-card__top">{market}{status}</div>'
            + f'<div class="watch-card__name">{title}</div>'
            + f'<div class="watch-card__reason">{reason}</div>'
            + f'</{tag}>'
        )
    return (
        '<section class="watchlist-strip" id="watchlist">'
        '<div class="watchlist-strip__header">'
        '<span class="eyebrow">Watchlist</span>'
        '<a class="see-more" href="#watchlist-full">표 형태로 보기 →</a>'
        '</div>'
        f'<div class="watchlist-row">{"".join(cards)}</div>'
        '</section>'
    )


def daily_card(page: SourcePage) -> str:
    slug = slug_for(page.source)
    date = daily_date(page)
    tags_html = "".join(
        f'<span class="chip">{html.escape(t)}</span>' for t in page.tags
    )
    date_html = f'<time class="daily-date">{html.escape(date)}</time>' if date else ""
    tags_attr = html.escape(",".join(page.tags))
    return (
        f'<a class="daily-card" href="./articles/{slug}.html" data-tags="{tags_attr}">'
        f'<div class="daily-card__meta">'
        f'<span class="day-no">Day {page.day_no}</span>'
        f'{date_html}'
        f'</div>'
        f'<h3 class="daily-card__title">{html.escape(page.title.split(" · ", 1)[-1])}</h3>'
        f'<p class="daily-card__summary">{html.escape(page.summary)}</p>'
        f'<div class="daily-card__tags">{tags_html}</div>'
        f'</a>'
    )


def company_row(page: SourcePage) -> str:
    slug = slug_for(page.source)
    updated = company_last_updated(page)
    updated_html = (
        f'<span class="company-row__updated">업데이트 {html.escape(updated)}</span>'
        if updated else ""
    )
    return (
        f'<a class="company-row" href="./articles/{slug}.html">'
        f'<div class="company-row__head">'
        f'<span class="ticker">{html.escape(page.ticker)}</span>'
        f'<span class="company-name">{html.escape(page.title)}</span>'
        f'</div>'
        f'<p class="company-row__summary">{html.escape(page.summary)}</p>'
        f'<div class="company-row__foot">'
        f'{market_badge(page.market)}{status_badge(page.status)}{updated_html}'
        f'</div>'
        f'</a>'
    )


def tv_widget(page: SourcePage) -> str:
    if not page.tv_symbol:
        return ""

    if page.tv_symbol.startswith("KRX:"):
        url = f"https://finance.naver.com/item/main.naver?code={page.ticker}"
        return (
            '<div class="naver-widget">'
            '<div class="naver-widget__info">'
            f'{market_badge(page.market or "코스피")}'
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


# ---------------- 페이지 셸 ----------------

SITE_URL = "https://stock.howlnode.com"
DEFAULT_DESCRIPTION = "데일리 숙제와 기업분석으로 쌓아가는 주식 스터디 기록"

FAVICON_SVG = (
    "data:image/svg+xml,"
    + quote(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'
        '<rect width="32" height="32" rx="7" fill="#161b22"/>'
        '<path d="M6 21l6-6 4 4 8-9" stroke="#58a6ff" stroke-width="3" '
        'fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
        "</svg>"
    )
)


def page_shell(title: str, body: str, current: str = "", description: str = "") -> str:
    prefix = "../" if current == "article" else ""
    desc = description or DEFAULT_DESCRIPTION
    nav = [
        ("index.html#daily", "데일리"),
        ("index.html#companies", "기업분석"),
        ("index.html#watchlist", "관심종목"),
        ("index.html#principles", "원칙"),
    ]
    nav_html = "".join(f'<a href="{prefix}{href}">{label}</a>' for href, label in nav)
    return f"""<!doctype html>
<html lang="ko">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="theme-color" content="#0d1117">
    <meta name="description" content="{html.escape(desc)}">
    <meta property="og:type" content="website">
    <meta property="og:site_name" content="HowlNode Stock">
    <meta property="og:title" content="{html.escape(title)} | HowlNode Stock">
    <meta property="og:description" content="{html.escape(desc)}">
    <meta property="og:url" content="{SITE_URL}/">
    <title>{html.escape(title)} | HowlNode Stock</title>
    <link rel="icon" href="{FAVICON_SVG}">
    <link rel="stylesheet" href="{prefix}styles.css">
  </head>
  <body>
    <header class="site-header">
      <a class="brand" href="{prefix}index.html">
        <span class="brand-mark">HN</span>
        <span><strong>HowlNode</strong><small>Stock · 투자기록</small></span>
      </a>
      <nav>{nav_html}</nav>
    </header>
    {body}
    <footer class="site-footer">
      <span>HowlNode Stock · 마지막 빌드 {date.today().isoformat()}</span>
      <a href="https://github.com/hihiwool/stock_study" target="_blank" rel="noopener">GitHub</a>
    </footer>
  </body>
</html>
"""


# ---------------- 인덱스 페이지 ----------------

def build_index() -> str:
    company_pages = [p for p in PAGES if p.group == "company"]
    daily_pages = sorted(
        [p for p in PAGES if p.group == "daily"],
        key=lambda p: p.day_no,
        reverse=True,
    )

    # 대시보드 데이터
    watchlist_md = read_source(next(p for p in PAGES if p.source.endswith("현재_관심종목_상태.md")))
    project_md = read_source(next(p for p in PAGES if p.source.endswith("프로젝트_방향.md")))
    principles_md = read_source(next(p for p in PAGES if p.source.endswith("누적_투자_원칙.md")))
    checklist_md = read_source(next(p for p in PAGES if p.source.endswith("체크리스트.md")))

    items = parse_watchlist(watchlist_md)
    strip_html = watchlist_strip(items)

    # 데일리 피드 & 기업분석 리스트
    daily_html = "\n".join(daily_card(p) for p in daily_pages)
    latest_date = next((daily_date(p) for p in daily_pages if daily_date(p)), "")

    # 데일리 종목 필터 (다룬 횟수 많은 순)
    tag_counts: dict[str, int] = {}
    for p in daily_pages:
        for t in p.tags:
            tag_counts[t] = tag_counts.get(t, 0) + 1
    filter_tags = sorted(tag_counts, key=lambda t: (-tag_counts[t], t))
    filter_html = (
        '<div class="feed-filter" id="feed-filter">'
        '<button class="filter-chip is-active" data-tag="">전체</button>'
        + "".join(
            f'<button class="filter-chip" data-tag="{html.escape(t)}">'
            f'{html.escape(t)}<span class="filter-count">{tag_counts[t]}</span></button>'
            for t in filter_tags
        )
        + "</div>"
    )

    company_groups = [
        ("핵심 후보", "core"),
        ("성장 후보", "growth"),
        ("신규 추가", "new"),
        ("후보", "candidate"),
        ("관찰", "watch"),
        ("고위험 관찰", "risk"),
        ("후순위 관찰", "deprioritized"),
    ]
    company_html_parts = []
    for status, _ in company_groups:
        rows = [company_row(p) for p in company_pages if p.status == status]
        if not rows:
            continue
        company_html_parts.append(
            f'<div class="company-group"><h3 class="company-group__title">{status}'
            f'<span class="company-group__count">{len(rows)}</span></h3>'
            f'<div class="company-list">{"".join(rows)}</div></div>'
        )
    companies_html = "\n".join(company_html_parts)

    # 워치리스트 표 (전체 종목, 분석 아직 없는 것 포함)
    watchlist_table = render_markdown(watchlist_md)

    body = f"""
    <main class="home">
      {strip_html}

      <section class="home-grid">
        <section id="daily" class="feed">
          <div class="section-heading">
            <div>
              <p class="eyebrow">Daily Feed</p>
              <h2>데일리 투자 기록</h2>
            </div>
            <span class="feed-meta">최신 {html.escape(latest_date) if latest_date else ""} · 총 {len(daily_pages)}개</span>
          </div>
          {filter_html}
          <div class="feed-list">{daily_html}</div>
        </section>

        <aside id="companies" class="companies-aside">
          <div class="section-heading">
            <div>
              <p class="eyebrow">Company Notes</p>
              <h2>기업분석</h2>
            </div>
            <span class="feed-meta">{len(company_pages)}개</span>
          </div>
          {companies_html}
        </aside>
      </section>

      <section id="watchlist-full" class="section">
        <div class="section-heading">
          <div>
            <p class="eyebrow">Watchlist · Full Table</p>
            <h2>관심종목 전체 상태</h2>
          </div>
        </div>
        <article class="content-card wide">{watchlist_table}</article>
      </section>

      <section id="principles" class="section">
        <div class="section-heading">
          <div>
            <p class="eyebrow">Principles</p>
            <h2>투자 원칙과 체크리스트</h2>
          </div>
        </div>
        <div class="content-grid">
          <article class="content-card">{render_markdown(principles_md)}</article>
          <article class="content-card">{render_markdown(checklist_md)}</article>
        </div>
      </section>

      <section class="section">
        <div class="section-heading">
          <div>
            <p class="eyebrow">Direction</p>
            <h2>프로젝트 방향</h2>
          </div>
        </div>
        <article class="content-card">{render_markdown(project_md)}</article>
      </section>
    </main>
    <script>
    (function () {{
      var filter = document.getElementById("feed-filter");
      if (!filter) return;
      var chips = filter.querySelectorAll(".filter-chip");
      var cards = document.querySelectorAll(".feed-list .daily-card");
      filter.addEventListener("click", function (e) {{
        var chip = e.target.closest(".filter-chip");
        if (!chip) return;
        var tag = chip.dataset.tag;
        chips.forEach(function (c) {{ c.classList.toggle("is-active", c === chip); }});
        cards.forEach(function (card) {{
          var tags = (card.dataset.tags || "").split(",");
          card.classList.toggle("is-hidden", tag !== "" && tags.indexOf(tag) === -1);
        }});
      }});
    }})();
    </script>
"""
    return page_shell("홈", body)


# ---------------- 상세 페이지 ----------------

def related_dailies_for_company(page: SourcePage) -> list[SourcePage]:
    if page.group != "company":
        return []
    return sorted(
        [p for p in PAGES if p.group == "daily" and page.title in p.tags],
        key=lambda p: p.day_no,
        reverse=True,
    )


def related_company_for_daily(page: SourcePage) -> SourcePage | None:
    if page.group != "daily" or not page.tags:
        return None
    name = page.tags[0]
    return next((p for p in PAGES if p.group == "company" and p.title == name), None)


def related_panel(page: SourcePage) -> str:
    if page.group == "company":
        rels = related_dailies_for_company(page)
        if not rels:
            return ""
        items = "".join(
            f'<li><a href="./{slug_for(r.source)}.html">'
            f'<span class="day-no">Day {r.day_no}</span>'
            f'<span>{html.escape(r.title.split(" · ", 1)[-1])}</span>'
            f'<span class="related-date">{html.escape(daily_date(r))}</span>'
            f'</a></li>'
            for r in rels
        )
        return (
            '<aside class="related"><h4>이 종목 관련 데일리</h4>'
            f'<ul class="related-list">{items}</ul></aside>'
        )
    if page.group == "daily":
        company = related_company_for_daily(page)
        if not company:
            return ""
        return (
            '<aside class="related"><h4>관련 기업분석</h4>'
            f'<a class="related-company" href="./{slug_for(company.source)}.html">'
            f'<span class="ticker">{html.escape(company.ticker)}</span>'
            f'<span>{html.escape(company.title)}</span>'
            f'{market_badge(company.market)}{status_badge(company.status)}'
            '</a></aside>'
        )
    return ""


def daily_nav(page: SourcePage) -> str:
    """데일리 글 하단 이전/다음 Day 내비게이션"""
    if page.group != "daily":
        return ""
    dailies = sorted((p for p in PAGES if p.group == "daily"), key=lambda p: p.day_no)
    idx = next(i for i, p in enumerate(dailies) if p.day_no == page.day_no)
    prev_p = dailies[idx - 1] if idx > 0 else None
    next_p = dailies[idx + 1] if idx + 1 < len(dailies) else None

    def link(p: SourcePage, cls: str, arrow_pre: str, arrow_post: str) -> str:
        label = p.title.split(" · ", 1)[-1]
        return (
            f'<a class="daily-nav__link {cls}" href="./{slug_for(p.source)}.html">'
            f'<span class="daily-nav__dir">{arrow_pre}Day {p.day_no}{arrow_post}</span>'
            f'<span class="daily-nav__title">{html.escape(label)}</span>'
            f'</a>'
        )

    prev_html = link(prev_p, "daily-nav__prev", "← ", "") if prev_p else '<span class="daily-nav__spacer"></span>'
    next_html = link(next_p, "daily-nav__next", "", " →") if next_p else '<span class="daily-nav__spacer"></span>'
    return f'<nav class="daily-nav">{prev_html}{next_html}</nav>'


def build_article(page: SourcePage) -> str:
    content = render_markdown(read_source(page), link_prefix="./")
    widget = tv_widget(page)
    related = related_panel(page)
    nav = daily_nav(page)
    body = f"""
    <main class="article-layout">
      <a class="back-link" href="../index.html">← 홈으로</a>
      {widget}
      <article class="article-body">{content}</article>
      {related}
      {nav}
    </main>
"""
    return page_shell(page.title, body, current="article", description=page.summary)


# ---------------- CSS ----------------

def write_styles() -> None:
    css = """
:root{
  --bg:#0d1117;--panel:#161b22;--panel-2:#1c2330;--border:#30363d;--border-soft:#21262d;
  --text:#e6edf3;--muted:#8b949e;--muted-2:#6e7681;
  --accent:#58a6ff;--accent-soft:#1f3a5f;
  --green:#3fb950;--red:#f85149;--yellow:#d29922;--orange:#f0883e;--purple:#a371f7;
}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Apple SD Gothic Neo","Malgun Gothic",sans-serif;padding:16px;font-size:14px;line-height:1.55}
a{color:var(--accent);text-decoration:none}
a:hover{text-decoration:underline}

/* ---------- Header ---------- */
.site-header{position:sticky;top:0;z-index:20;max-width:1320px;margin:0 auto 14px;display:flex;align-items:center;justify-content:space-between;gap:12px;padding:8px 0 12px;border-bottom:1px solid var(--border);background:rgba(13,17,23,.94);backdrop-filter:blur(12px)}
.brand{display:flex;align-items:center;gap:10px;color:var(--text)}
.brand-mark{display:grid;width:34px;height:34px;place-items:center;border:1px solid var(--border);border-radius:8px;background:var(--panel);color:var(--accent);font-size:12px;font-weight:800}
.brand strong,.brand small{display:block;line-height:1.1}
.brand small{margin-top:3px;color:var(--muted);font-size:12px}
.site-header nav{display:flex;flex-wrap:wrap;justify-content:flex-end;gap:6px}
.site-header nav a{padding:6px 11px;border:1px solid transparent;border-radius:6px;color:var(--muted);font-size:13px;font-weight:600}
.site-header nav a:hover{border-color:var(--border);background:var(--panel);color:var(--text);text-decoration:none}

main{width:min(1320px,100%);margin:0 auto}
.home{display:flex;flex-direction:column;gap:18px}

/* ---------- Eyebrow / Section heading ---------- */
.eyebrow{color:var(--accent);font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.06em}
.section-heading{display:flex;align-items:flex-end;justify-content:space-between;gap:12px;margin-bottom:10px}
.section-heading h2{font-size:18px;color:var(--text);margin-top:4px}
.section .section-heading h2{font-size:17px}
.feed-meta{color:var(--muted);font-size:12px;white-space:nowrap}

/* ---------- Watchlist strip ---------- */
.watchlist-strip{background:linear-gradient(180deg,var(--panel) 0%,#141a23 100%);border:1px solid var(--border);border-radius:10px;padding:14px 14px 12px}
.watchlist-strip__header{display:flex;align-items:center;justify-content:space-between;margin-bottom:10px}
.see-more{font-size:12px;color:var(--muted);font-weight:600}
.see-more:hover{color:var(--accent);text-decoration:none}
.watchlist-row{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:8px}
.watch-card{display:flex;flex-direction:column;gap:6px;padding:10px 12px;border-radius:8px;border:1px solid var(--border);background:var(--panel-2);color:var(--text);transition:transform .15s ease,border-color .15s ease}
.watch-card:hover{border-color:var(--accent);transform:translateY(-1px);text-decoration:none}
.watch-card--static{cursor:default}
.watch-card--static:hover{transform:none;border-color:var(--border)}
.watch-card__top{display:flex;gap:6px;flex-wrap:wrap}
.watch-card__name{font-size:15px;font-weight:700}
.watch-card__reason{font-size:12px;color:var(--muted);line-height:1.4}

/* ---------- Status / Market pills ---------- */
.status-pill,.market-pill{display:inline-flex;align-items:center;padding:2px 8px;border-radius:999px;font-size:11px;font-weight:700;letter-spacing:.02em;line-height:1.5}
.status-core{background:#1f3a5f;color:#79c0ff}
.status-growth{background:#1c3a1c;color:#7ee787}
.status-watch{background:#3a2c1c;color:#ffa657}
.status-risk{background:#3a1c1c;color:#ff7b72}
.status-candidate{background:#2a2347;color:#d2a8ff}
.status-new{background:#103138;color:#56d4dd}
.status-deprioritized{background:#21262d;color:#8b949e}
.market-kospi{background:#1c3a1c;color:#7ee787}
.market-nasdaq{background:#1f3a5f;color:#79c0ff}
.market-nyse{background:#2a2347;color:#d2a8ff}

/* ---------- Daily feed filter ---------- */
.feed-filter{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:12px}
.filter-chip{display:inline-flex;align-items:center;gap:5px;padding:5px 11px;border-radius:999px;border:1px solid var(--border);background:var(--panel);color:var(--muted);font-size:12px;font-weight:600;cursor:pointer;font-family:inherit;transition:border-color .15s ease,color .15s ease}
.filter-chip:hover{border-color:var(--accent);color:var(--text)}
.filter-chip.is-active{border-color:var(--accent);background:var(--accent-soft);color:#79c0ff}
.filter-count{display:inline-flex;align-items:center;padding:0 6px;border-radius:999px;background:var(--panel-2);font-size:10.5px;color:var(--muted)}
.filter-chip.is-active .filter-count{background:rgba(121,192,255,.15);color:#79c0ff}
.daily-card.is-hidden{display:none}

/* ---------- Home grid: feed + companies ---------- */
.home-grid{display:grid;grid-template-columns:minmax(0,1.85fr) minmax(280px,1fr);gap:18px;align-items:flex-start}
.feed{min-width:0}
.feed-list{display:flex;flex-direction:column;gap:10px}
.daily-card{display:block;padding:14px 16px;border:1px solid var(--border);border-radius:10px;background:var(--panel);color:var(--text);transition:border-color .15s ease,transform .15s ease;position:relative}
.daily-card:hover{border-color:var(--accent);text-decoration:none;transform:translateY(-1px)}
.daily-card__meta{display:flex;align-items:center;gap:10px;font-size:12px;color:var(--muted);margin-bottom:6px}
.day-no{display:inline-flex;align-items:center;padding:2px 8px;background:var(--accent-soft);color:#79c0ff;border-radius:999px;font-weight:700;font-size:11px;letter-spacing:.04em}
.daily-date{color:var(--muted);font-size:12px;font-variant-numeric:tabular-nums}
.daily-card__title{font-size:16px;color:var(--text);margin:2px 0 6px}
.daily-card__summary{font-size:13px;color:var(--muted);line-height:1.55}
.daily-card__tags{display:flex;gap:6px;flex-wrap:wrap;margin-top:10px}
.chip{display:inline-flex;align-items:center;padding:2px 8px;border-radius:999px;background:var(--panel-2);border:1px solid var(--border);font-size:11px;color:var(--text);font-weight:600}

/* ---------- Companies aside ---------- */
.companies-aside{display:flex;flex-direction:column;gap:14px;position:sticky;top:80px;min-width:0}
.company-group__title{display:flex;align-items:center;gap:8px;font-size:13px;color:var(--muted);margin-bottom:8px;text-transform:uppercase;letter-spacing:.05em}
.company-group__count{display:inline-flex;align-items:center;padding:1px 7px;border-radius:999px;background:var(--panel-2);color:var(--muted);font-size:11px}
.company-list{display:flex;flex-direction:column;gap:8px}
.company-row{display:block;padding:12px 14px;border:1px solid var(--border);border-radius:10px;background:var(--panel);color:var(--text);transition:border-color .15s ease}
.company-row:hover{border-color:var(--accent);text-decoration:none}
.company-row__head{display:flex;align-items:baseline;gap:8px;flex-wrap:wrap;margin-bottom:4px}
.ticker{font-family:'SF Mono',Consolas,Menlo,monospace;font-size:13px;color:var(--accent);font-weight:700;letter-spacing:.04em}
.company-name{font-size:14px;font-weight:700}
.company-row__summary{font-size:12.5px;color:var(--muted);line-height:1.5;margin-bottom:8px}
.company-row__foot{display:flex;gap:6px;align-items:center;flex-wrap:wrap}
.company-row__updated{margin-left:auto;color:var(--muted-2);font-size:11px;font-variant-numeric:tabular-nums}

/* ---------- Section / content-card ---------- */
.section{padding:0}
.content-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.content-card{background:var(--panel);border:1px solid var(--border);border-radius:10px;padding:16px;overflow:hidden}
.content-card.wide{padding:0;overflow:auto}
.content-card.wide table{margin:0}
.content-card h1{font-size:20px;margin-bottom:8px}
.content-card h2,.article-body h2{margin-top:22px;font-size:15px;color:var(--accent)}
.content-card h3,.article-body h3{margin-top:16px;font-size:13.5px;color:var(--text)}
.content-card h4,.article-body h4{margin-top:14px;font-size:13px;color:var(--text);font-weight:700}
.content-card h5,.article-body h5{margin-top:12px;font-size:12px;color:var(--muted);font-weight:700;text-transform:uppercase;letter-spacing:.05em;padding-left:9px;border-left:2px solid var(--accent)}
.content-card h6,.article-body h6{margin-top:10px;font-size:11.5px;color:var(--muted-2);font-weight:600}
.content-card p,.article-body p{color:var(--text);margin-top:8px}
.content-card ul,.content-card ol,.article-body ul,.article-body ol{margin-top:8px}
strong{color:var(--text)}

/* ---------- Tables ---------- */
.table-wrap{width:100%;overflow:auto}
table{width:100%;min-width:720px;border-collapse:collapse;background:var(--panel);font-size:13px}
th,td{padding:9px 12px;border-bottom:1px solid var(--border-soft);text-align:left;vertical-align:top}
th{color:var(--muted);font-weight:600;font-size:12px;background:var(--panel-2)}
tbody tr:last-child td{border-bottom:0}
tbody tr:hover{background:rgba(88,166,255,.04)}

/* ---------- Lists / blockquote / code ---------- */
ul,ol{padding-left:20px}
li{margin:5px 0}
.task-list{list-style:none;padding-left:0}
.task-list input{margin-right:8px;accent-color:var(--accent)}
blockquote{margin:14px 0;padding:12px 14px;border-left:3px solid var(--accent);background:#111a24;border-radius:0 8px 8px 0}
blockquote p{margin:0;color:var(--text);font-weight:600}
code{padding:2px 6px;border-radius:4px;background:var(--bg);border:1px solid var(--border);color:var(--text);font-size:.92em}

/* ---------- Article ---------- */
.article-layout{max-width:980px;padding:14px 0 50px;display:flex;flex-direction:column;gap:14px}
.back-link{display:inline-flex;width:max-content;color:var(--accent);font-weight:700;margin-bottom:0}
.article-body{padding:20px 22px;border:1px solid var(--border);border-radius:10px;background:var(--panel)}
.article-body a,.content-card a{color:var(--accent);font-weight:600}

/* ---------- TV / Naver widgets ---------- */
.tv-widget-wrap{border-radius:10px;overflow:hidden;border:1px solid var(--border);background:var(--panel)}
.naver-widget{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:14px 16px;border-radius:10px;border:1px solid var(--border);background:var(--panel)}
.naver-widget__info{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.naver-widget__ticker{font-family:'SF Mono',Consolas,Menlo,monospace;font-size:15px;font-weight:700;color:var(--accent)}
.naver-widget__name{color:var(--muted);font-size:13px}
.naver-widget__btn{display:inline-flex;align-items:center;padding:6px 12px;border-radius:6px;border:1px solid #235c37;background:#1c3a1c;color:var(--green);font-size:13px;font-weight:700;white-space:nowrap}
.naver-widget__btn:hover{background:#254d2d;text-decoration:none}

/* ---------- Related panel on article pages ---------- */
.related{padding:14px 16px;border:1px solid var(--border);border-radius:10px;background:var(--panel)}
.related h4{font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.06em;margin-bottom:10px}
.related-list{list-style:none;padding:0;display:flex;flex-direction:column;gap:6px}
.related-list a{display:flex;align-items:center;gap:10px;padding:8px 10px;border:1px solid var(--border-soft);border-radius:8px;background:var(--panel-2);color:var(--text)}
.related-list a:hover{border-color:var(--accent);text-decoration:none}
.related-date{margin-left:auto;color:var(--muted);font-size:12px;font-variant-numeric:tabular-nums}
.related-company{display:flex;align-items:center;gap:10px;padding:10px 12px;border:1px solid var(--border-soft);border-radius:8px;background:var(--panel-2);color:var(--text)}
.related-company:hover{border-color:var(--accent);text-decoration:none}

/* ---------- Daily prev/next nav ---------- */
.daily-nav{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.daily-nav__link{display:flex;flex-direction:column;gap:4px;padding:12px 14px;border:1px solid var(--border);border-radius:10px;background:var(--panel);color:var(--text);min-width:0;transition:border-color .15s ease}
.daily-nav__link:hover{border-color:var(--accent);text-decoration:none}
.daily-nav__next{text-align:right;align-items:flex-end}
.daily-nav__dir{font-size:11px;font-weight:700;color:var(--accent);letter-spacing:.04em}
.daily-nav__title{font-size:13px;color:var(--muted);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:100%}
.daily-nav__spacer{visibility:hidden}

/* ---------- Footer ---------- */
.site-footer{width:min(1320px,100%);margin:30px auto 8px;padding-top:14px;border-top:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;gap:10px;color:var(--muted-2);font-size:12px}
.site-footer a{color:var(--muted);font-weight:600}
.site-footer a:hover{color:var(--accent)}

/* ---------- Responsive ---------- */
@media(max-width:1024px){
  .home-grid{grid-template-columns:1fr}
  .companies-aside{position:static}
}
@media(max-width:720px){
  body{padding:10px}
  .site-header{align-items:flex-start;flex-direction:column}
  .site-header nav{justify-content:flex-start}
  .watchlist-row{grid-template-columns:1fr 1fr}
  .content-grid{grid-template-columns:1fr}
  .section-heading h2{font-size:16px}
}
@media(max-width:480px){
  .watchlist-row{grid-template-columns:1fr}
}
"""
    (PUBLIC / "styles.css").write_text(css, encoding="utf-8")


# ---------------- Build ----------------

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
