-- Num. Medium articles in Posts
--  0.13% (50735/37554088)
#standardSQL
SELECT COUNT(*)
FROM `sotorrent-org.2020_03_15.PostVersionUrl`
WHERE Url LIKE '%medium.com%' 
   OR Url LIKE '%towardsdatascience.com%'
   OR Url LIKE '%hackernoon.com%'
   OR Url LIKE '%freecodecamp.com%'
   OR Url LIKE '%codeburst.io%';

-- Num. Medium articles in Comments
-- (0.17%) 13737/8139159
#standardSQL
SELECT COUNT(*)
FROM `sotorrent-org.2020_03_15.CommentUrl`
WHERE Url LIKE '%medium.com%' 
   OR Url LIKE '%towardsdatascience.com%'
   OR Url LIKE '%hackernoon.com%'
   OR Url LIKE '%freecodecamp.com%'
   OR Url LIKE '%codeburst.io%';
