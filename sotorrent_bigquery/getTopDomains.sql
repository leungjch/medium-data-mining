-- Get frequency table of top domains in URLs in Posts
-- Medium is the 70th most common domain linked
-- (44,489 occurrences)
#standardSQL
SELECT RootDomain, COUNT(*) as freq
FROM `sotorrent-org.2020_03_15.PostVersionUrl`
GROUP BY RootDomain
ORDER BY freq desc

-- Get frequency table of top domains in URLs in Comments
-- Medium is the 52th most common domain linked in comments
-- (12,135 occurrences)
#standardSQL
SELECT RootDomain, COUNT(*) as freq
FROM `sotorrent-org.2020_03_15.CommentUrl`
GROUP BY RootDomain
ORDER BY freq desc