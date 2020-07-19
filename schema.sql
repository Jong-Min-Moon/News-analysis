DROP TABLE IF EXISTS naver_news;
CREATE TABLE naver_news (
  doc_id INTEGER PRIMARY KEY AUTOINCREMENT,
  press TEXT NOT NULL,
  title TEXT NOT NULL, 
  url TEXT NOT NULL,
  content TEXT NOT NULL,
  time TEXT NOT NULL,
  polar_sum INTEGER,
  tot INTEGER,
  sent_score REAL,
  n_comments INTEGER
);

DROP TABLE IF EXISTS naver_comment;
CREATE TABLE naver_comment (
    doc_id INTEGER,
	press	TEXT,
	title	TEXT,
	url	TEXT,
	content	TEXT,
	like	INTEGER,
	dislike	INTEGER,
	time	TEXT,
	re_reply	INTEGER,
	polar_sum	INTEGER,
	tot	INTEGER,
	sent_score	REAL
);