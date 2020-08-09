DROP TABLE IF EXISTS naver_news;
CREATE TABLE naver_news (
  doc_id INTEGER PRIMARY KEY,
  press TEXT NOT NULL,
  title TEXT NOT NULL, 
  ex_url TEXT NOT NULL,
  in_url TEXT NOT NULL,
  content TEXT NOT NULL,
  is_relation TEXT NOT NULL,
  master INTEGER,
  time TEXT NOT NULL,
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