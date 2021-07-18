# 파이썬을 이용한 네이버 뉴스기사 크롤링, 감성분석, 주제분류, 대시보드

## 1. Crawling using Beautifulsoup4

### 특징
* 설정한 키워드로 네이버 뉴스 검색을 한 뒤 뉴스 기사와 댓글을 크롤링
* API를 사용하지 않고 동적 크롤링(beautifulsoup4) 사용: chrome webdriver가 자동으로 네이버 뉴스 검색 결과를 마지막 페이지까지 클릭해 가며 크롤링
* 결과는 sqlite database에 저장(python sqlite3 패키지 사용)
* schedule 패키지를 사용하여 매일 정해진 시간에 자동으로 작업 수행

### 파일 설명
* chromerdiver: 파이썬이 크롤링을 할 때 사용하는 크롬 브라우저. 컴퓨터에 설치된 운영체제 및 크롬 브라우저 버전에 맞는 버전을 사용해야 함
* crawler.py : 네이버 뉴스 및 댓글 크롤링과 감성 분석, 주제 분류를 실행하는 프로그램. **2020년 7월에 작성한 프로그램으로, 현재는 네이버 뉴스의 url 체계가 바뀌어 프로그램이 작동하지 않습니다. 바뀐 url 체계에 맞게 수정하면 작동합니다.**
    - Crawler : 크롤링 수행하는 class
    - add_sent_score: 감성 분석 점수 추가하는 함수. 군산대에서 제작한 한국어 감성점수 사전을 이용해 기사 내 단어의 감성점수 총합을 계산하는 단순한 방식. https://github.com/ehsong/korean-sentiment-analysis
    - Do_LDA : 뉴스 기사를 유사한 내용끼리 묶고 시각화하는 함수. Latent Dirichlet Allocation 알고리즘을 구현한 패키지 tomotopy 사용. 시각화는 t-sne 알고리즘을 구현한 sklearn 사용.
    - tokenize: 문장을 형태소 단위로 분리하는 함수. kiwi, konlpy 패키지 사용.
* requirements.txt : 필요한 패키지 목록.
* news.db : 크롤링한 데이터를 저장하는 sqlite 데이터베이스 파일
* schema.sql : 데이터베이스 포맷을 지정하고 초기화하는 sql 파일
* news_crawl_example.csv : 뉴스 기사 내용 크롤링 결과 예시
* news_crawl_example_2020.05.31.csv : LDA로 뉴스 기사 내용 군집화하고 t-sne로 시각화한 내용 예시. x, y컬럼은 t-sne로 2차원 차원축소한 결과 벡터, label 컬럼은 주제 번호


* pip 다운로드 속도 느릴 때 우분투에서 pip 미러 변경 방법
mkdir ~/.pip
cat <<EOF > ~/.pip/pip.conf
 [global]
 index-url = http://mirror.kakao.com/pypi/simple
 trusted-host=mirror.kakao.com
EOF


## 2. Web app using Dash

### 특징
* 데이터 시각화 라이브러리인 plotly와 웹 어플리케이션 프레임워크 dash를 이용해 크롤링 결과 대시보드 웹앱 작성
* 작성한 웹앱 프로그램(app.py)를 heroku를 이용해 deploy
    - heroku의 무료 플랜을 사용하기 때문에, 접속시 1분 가량 소모됩니다

### 웹앱 링크
https://news-analysis-roka.herokuapp.com/

### 구성
1. 날짜 선택
2. 기사 주제별 감성 분포 막대그래프
* 막대를 클릭하면 해당 주제 기사들의 댓글 현황 그래프가 아래에 생성됨. 그래프의 점 위에 커서를 올리면 댓글 내용 확인 가능
3. 오늘의 댓글 중 좋아요 개수 기준 상위 5개
4. 오늘의 댓글 중 싫어요 개수 기준 상위 5개
5. 특정 키워드 관련 기사 개수 시계열 그래프(구현 안됨)
6. 2번 막대그래프의 파이차트 버전
7. 주제별 주요 어휘 시각화(treemap, wordcloud)
8. 기사 LDA 결과 t-sne로 2차원 시각화
9. 기사 감성 분포 시계열 그래프
10. 댓글 개수 시계열 그래프