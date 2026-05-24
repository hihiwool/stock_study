# Stock Study

Obsidian 주식 노트에서 공개할 내용만 골라 정적 HTML로 변환하는 사이트입니다.

## 구조

```text
public/                 # Cloudflare Pages가 배포할 정적 파일
articles/               # build_site.py가 생성하는 상세 HTML
build_site.py            # Obsidian markdown -> HTML 변환
build_loop.py            # 로컬 자동 재빌드용
workers/stock-study-api.js
wrangler.toml            # Cloudflare Worker 설정
DEPLOY-CLOUDFLARE.md
```

Obsidian 원본 vault 전체는 배포하지 않습니다. 변환 결과인 `public`만 공개합니다.

## 사이트 빌드

```powershell
python .\build_site.py
```

## 로컬 확인

```powershell
cd public
python -m http.server 8788
```

확인 주소:

```text
http://localhost:8788
```

## Cloudflare Pages 권장 설정

- Project name: `stock-study`
- Build command: 비움
- Build output directory: `public`
- Root directory: 비움

Obsidian 원본까지 Git에 넣는 방식으로 바꾸면 Cloudflare Pages의 build command를 `python build_site.py`로 바꿀 수 있습니다. 지금은 원본 vault를 공개 repo에 넣지 않는 전제를 권장합니다.

## Worker

`stock-study-api` Worker는 향후 증권사 API를 프론트엔드에서 직접 호출하지 않기 위한 서버 측 프록시 자리입니다.

현재는 API 키나 계좌 정보가 들어 있지 않습니다.

```text
/health      상태 확인
/broker/*    아직 비활성화된 증권 API 프록시 placeholder
```

증권사 API를 붙일 때는 키를 코드에 넣지 말고 Cloudflare Worker Secret으로 등록해야 합니다.

