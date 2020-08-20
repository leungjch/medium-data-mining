#standardSQL
SELECT RootDomain, COUNT(*) as freq
FROM `sotorrent-org.2020_03_15.PostVersionUrl`
GROUP BY RootDomain
ORDER BY freq desc

-- Medium is the 70th most common domain linked
-- (44,489 occurrences)