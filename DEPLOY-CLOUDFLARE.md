# Cloudflare Tunnel로 로컬 홈페이지 공개하기

이 문서는 `howlnode.com` 아래에 새 홈페이지를 추가할 때 확인하는 작업 순서입니다.

## 개념

Cloudflare Zero Trust의 Tunnel 커넥터가 내 노트북에서 실행 중인 로컬 HTTP 서버로 트래픽을 전달합니다.

예를 들어:

- 외부 접속: `https://stock.howlnode.com`
- Cloudflare Tunnel 전달: `localhost:8788`
- 실제 파일 위치: `stock_homepage/public`

주의: 로컬 HTTP 서버가 새 파일을 만드는 것은 아닙니다. 지정한 폴더의 HTML/CSS/JS 파일을 웹으로 서빙하는 역할입니다.

## 1. 공개할 폴더 준비

프로젝트 루트 전체를 공개하지 말고, 공개 파일만 들어 있는 폴더를 따로 둡니다.

현재 구조:

```text
stock_homepage/
  public/
    index.html
    styles.css
    app.js
    stock/
      index.html
      styles.css
      app.js
  README.md
  DEPLOY-CLOUDFLARE.md
```

Cloudflare로 공개되는 서버 루트는 반드시 `public` 폴더로 잡습니다.

## 2. 로컬 HTTP 서버 실행

PowerShell에서:

```powershell
cd \\100.114.122.72\code_notebook\stock_homepage\public
python -m http.server 8788
```

확인 주소:

```text
http://localhost:8788
```

`README.md`, 작업 메모, 미리보기 이미지 같은 파일이 보이면 안 됩니다. 그런 파일이 보인다면 프로젝트 루트에서 서버를 실행한 것입니다.

## 3. Cloudflare Zero Trust에서 경로 추가

Cloudflare Dashboard에서:

1. Zero Trust로 이동
2. Networks 또는 Tunnels 메뉴로 이동
3. 연결된 커넥터/Tunnel 선택
4. Public Hostnames 또는 게시된 애플리케이션 경로로 이동
5. Add a public hostname 또는 게시된 애플리케이션 경로 추가 클릭

## 4. 서브도메인 방식 추천

여러 홈페이지를 한 도메인에서 운영할 때는 서브도메인 방식이 관리하기 쉽습니다.

`stock.howlnode.com` 예시:

```text
Subdomain: stock
Domain: howlnode.com
Type: HTTP
URL: localhost:8788
```

접속 주소:

```text
https://stock.howlnode.com
```

다른 홈페이지를 추가할 때도 같은 방식으로 나눕니다.

```text
blog.howlnode.com  -> localhost:8790
tools.howlnode.com -> localhost:8791
stock.howlnode.com -> localhost:8788
```

## 5. 경로 방식도 가능

`howlnode.com/stock`처럼 경로로 나누고 싶다면:

```text
Domain: howlnode.com
Path: /stock
Type: HTTP
URL: localhost:8788
```

접속 주소:

```text
https://howlnode.com/stock/
```

이 방식은 로컬 서버 안에도 `/stock/` 경로가 실제로 존재해야 합니다.

현재는 다음 파일이 있으므로 동작합니다.

```text
public/stock/index.html
```

## 6. 보안 체크

공개 전에 확인할 것:

```powershell
Invoke-WebRequest http://localhost:8788/README.md
Invoke-WebRequest http://localhost:8788/DEPLOY-CLOUDFLARE.md
```

둘 다 `404`가 나와야 정상입니다.

홈페이지는 정상이어야 합니다.

```powershell
Invoke-WebRequest http://localhost:8788/
```

`200`이 나오면 정상입니다.

## 7. 문제 생겼을 때

페이지가 안 열리면:

1. 로컬에서 `http://localhost:8788`이 열리는지 확인
2. HTTP 서버를 `public` 폴더에서 실행했는지 확인
3. Cloudflare Tunnel 커넥터가 Connected 상태인지 확인
4. Cloudflare Public Hostname의 URL이 `localhost:8788`인지 확인
5. 포트가 겹치면 다른 포트를 사용하고 Cloudflare 설정도 같이 변경

