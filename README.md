# Medium Mining



# Analysis

Contains Jupyter notebooks for exploratory data analysis of the Medium dataset on the tag / archive / story levels.

- **verifyData.ipynb**: 

# Processed Data

Contains small data .csv files. The archive / story level data is too large to host on Github.

- **archive_tagsource.csv**: A list of tags and the number of stories associated with that tag, sorted in alphabetical order.
- **cleantags_final_m10.csv**: The list of tags that were used in crawl_story and crawl_archive. We crawled the first 13,000 tags. 
- **tags_to_complete_jul26.csv**: List of tags that were found to be missing from the df story dataset that were later crawled.
- **distanceDict.csv**: List of all tags crawled, sorted by the shortest distance from the software-engineering tag. We cleaned the file (convert to lower case, replace spaces with hyphen) in **cleantags_final_m10.csv**, which we use in crawl_archive and crawl_story.
- **pathDict.csv**: Tags sorted by shortest distance to software-engineering, with the shortest tag path shown. E.g. "code-coverage" -> "software-development" -> "software-engineering"

# Crawlers

Contains the code for Scrapy spiders.

- **crawl_tag**: Crawl the network of related tags on a Medium tag (e.g. medium.com/tag/software-engineering). 
- **crawl_story**: Crawl the story level of Medium (specifically, everything enclosed within the \<article> tag of the HTML. The spider crawls from tags -> tag archive -> story. We obtained the tags from the crawl_tag spider.
- **crawl_archive**: Crawl only the archive level of Medium. This is favorable to crawling the story level as the story text / raw HTML takes time to fetch. Crawling archive level is 5-10X faster. 