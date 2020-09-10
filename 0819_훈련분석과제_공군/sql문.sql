--댓글에 doc_id 붙이기
UPDATE naver_comment
SET doc_id = (SELECT doc_id FROM naver_news WHERE in_url = naver_comment.url)
WHERE doc_id IS NULL


--기사에 n_comments 붙이기
UPDATE naver_news
SET n_comments = (
	SELECT count(content)
	FROM naver_comment
	WHERE naver_comment.doc_id = naver_news.doc_id


-- 헤드라인
SELECT * 
FROM (
	SELECT ROW_NUMBER ()
	OVER ( 
		PARTITION BY time
		ORDER BY n_comments DESC
		)
	RowNum, press, title, time
	FROM naver_news
	
	)
WHERE RowNum in (1,2)




--주요 댓글
SELECT * 
FROM (
	SELECT ROW_NUMBER ()
	OVER ( 
		PARTITION BY substr(time_written, 0, 11)
		ORDER BY like DESC
		)
	RowNum, title, like, re_reply, content, time_written, sent_score
	FROM naver_comment
	WHERE sent_score > 0
	)
WHERE RowNum in (1,2)


-- 댓글감성현황
SELECT substr(time_written, 0, 11) as time_writ, sum(sent_score>0) as pos, sum(sent_score<0) as neg, sum(sent_score=0) as neu, count(*) as total
FROM naver_comment
GROUP BY substr(time_written, 0, 11)


SELECT naver_news2.title, naver_news2.in_url. naver_news2.ex_url
from naver_news2 left outer join naver_news on
naver_news2.ex_url = naver_news.ex_url
WHERE naver_news.ex_url is null