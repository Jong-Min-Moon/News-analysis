DROP TABLE IF EXISTS naver_news;
CREATE TABLE naver_news (
  doc_id TEXT PRIMARY KEY,
  query TEXT,
  press TEXT NOT NULL,
  title TEXT NOT NULL, 
  ex_url TEXT NOT NULL,
  in_url TEXT NOT NULL,
  content TEXT NOT NULL,
  is_relation TEXT NOT NULL,
  master INTEGER,
  time_written TEXT NOT NULL
);

DROP TABLE IF EXISTS naver_comment;
CREATE TABLE naver_comment (
  doc_id TEXT,
  query TEXT,
	press	TEXT,
	title	TEXT,
	url	TEXT,
	content	TEXT,
	like	INTEGER,
	dislike	INTEGER,
	time_written	TEXT,
	re_reply	INTEGER,
	polar_sum	INTEGER,
	tot	INTEGER,
	sent_score	REAL
);