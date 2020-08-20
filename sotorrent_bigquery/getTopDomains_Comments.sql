#standardSQL
SELECT RootDomain, COUNT(*) as freq
FROM `sotorrent-org.2020_03_15.CommentUrl`
GROUP BY RootDomain
ORDER BY freq desc

-- Medium is the 52th most common domain linked in comments
-- (12,135 occurrences)