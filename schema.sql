DROP TABLE IF EXISTS naver_news;
CREATE TABLE naver_news (
  doc_id TEXT PRIMARY KEY,
  press TEXT NOT NULL,
  title TEXT NOT NULL, 
  url TEXT NOT NULL,
  content TEXT NOT NULL,
  time_written TEXT NOT NULL,
  polar_sum INTEGER,
  tot INTEGER,
  sent_score REAL,
  n_comments INTEGER
);

DROP TABLE IF EXISTS naver_comment;
CREATE TABLE naver_comment (
  doc_id TEXT,
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
