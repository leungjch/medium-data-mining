-- Get frequency link references to Medium and Medium publications per month 
-- Shows Medium's explosive growth in the past years
#standardSQL
SELECT
  DATE_TRUNC(DATE(CreationDate), MONTH) as date,
  COUNT(*) as count
FROM sotorrent-org.2020_03_15.Posts
INNER JOIN sotorrent-org.2020_03_15.PostVersionUrl
ON Posts.ParentId = PostVersionUrl.PostId
WHERE RootDomain LIKE '%medium.com%' OR RootDomain LIKE '%towardsdatascience.com%' OR RootDomain LIKE '%codeburst.io%'
GROUP BY date
ORDER BY date ASC