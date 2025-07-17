# NotifyNews

네이버 뉴스의 API를 받아와서 구글 스페이스에 올려 놓는 프로그램
config.json 파일을 수정하여 사용할 것

## Features

- 네이버 뉴스 API를 통한 뉴스 검색 및 수집
- 구글 스페이스로 자동 알림 전송
- 중복 뉴스 링크 필터링
- **새로운 기능**: 웹 서버 인터페이스 제공

## Installation

```bash
git clone git@github.com/jsheo96/NotifyNews.git
cd NotifyNews
conda create -y -n notify-news
conda activate notify-news
pip install -r requirements.txt
```

## Configuration

config.json 파일을 원하는 대로 수정하세요:

```json
{
  "query": "검색할 키워드",
  "max_news": 3
}
```

## Usage

### CLI Mode (기존 기능)

```bash
python main.py
```

### Web Server Mode (새로운 기능)

```bash
python main.py webserver
```

웹 서버를 실행하면 `http://localhost:5000`에서 다음 기능들을 사용할 수 있습니다:

- **대시보드**: 실시간 뉴스 상태 확인
- **설정 관리**: 검색 쿼리 및 최대 뉴스 수 설정
- **수동 실행**: 뉴스 수집 및 전송을 수동으로 실행
- **뉴스 조회**: 현재 수집된 뉴스 확인
- **히스토리**: 이전에 전송된 뉴스 링크 히스토리 확인

### API Endpoints

- `GET /api/config` - 현재 설정 조회
- `POST /api/config` - 설정 업데이트
- `GET /api/news` - 현재 뉴스 조회
- `POST /api/fetch-and-send` - 뉴스 수집 및 전송 실행
- `GET /api/history` - 뉴스 히스토리 조회

## Dependencies

- requests
- httplib2
- flask (웹 서버용)
