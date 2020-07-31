# Medium Mining
This repo contains the code for preprocessing, analysis, and modelling of the Medium dataset, as well as the Scrapy crawlers used to build the Medium dataset.

# Story Model
Code for building linear/logistic/SVM models and generating a dataset suitable for modelling, and extracting story-level features from HTML.

## Model
- **Story_LinearModel.ipynb**: Notebook for building linear and logistic regression models. 

## Generate_features
- **Story_GetAuthorFeatures.ipynb**, **Story_GetPublicationFeatures.ipynb**, **Story_GetTagFeatures.ipynb**: These notebooks group the story dataset by authors, publications, and tags respectively and generate aggregated features (median, mean, sum, count) for ClapCount, ReadingTime, isPaywall, etc. For example, for publications, this would generate the number (count) of articles that a publication (e.g. Towards Data Science) has, and the mean/median/sum of claps of all articles in that publication, for every publication.  These features are joined onto the article level using pandas.merge. 
- **ExtractFeatures_Story.ipynb**: Extract features from the raw HTML, join features from author/publication/tag level, and generate a new .csv file that is suitable for modelling (removing NaN entries and values, etc).
- **extractFeaturesFunction.py**: Implementation of story-level feature extraction. This had to be placed in a separate .py file as it was required for the multiprocessing library to work.

### Join_data
- **authorStats.csv**, **publicationStats.csv**, **tagStats.csv**: Data grouped by author/publication/tag that is aggregated on various features such as ClapCount, ReadingTime, etc. These files are used by **Story_GetAuthorFeatures.ipynb**, **Story_GetPublicationFeatures.ipynb**, **Story_GetTagFeatures.ipynb** to generate features for the model.

# Archive Analysis

Contains an EDA of Medium on the archive level.

- **Archive_ExploratoryDataAnalysis.ipynb**: Contains an EDA of the Medium archive dataset (27+ million articles), which can also be run on the story level dataset (6 million articles). Explores relationships between tags, reading time, publications, users, etc.


# Preprocessing scripts

Code for processing and generating cleaned data.

- **verifyData.ipynb**: Checks if there were tags less than or equal to distance of 2 from software-engineering that were not crawled. 


# Small Data Files

Contains small data .csv files. The archive / story level data is too large to host on Github.

- **archive_tagsource.csv**: A list of tags and the number of stories associated with that tag, sorted in alphabetical order.
- **cleantags_final_m10.csv**: The list of tags that were used in crawl_story and crawl_archive. We crawled the first 13,000 tags. 
- **tags_to_complete_jul26.csv**: List of tags that were found to be missing from the df_story dataset that were later crawled, after the large scale crawling had been completed.
- **distanceDict.csv**: List of all tags crawled, sorted by the shortest distance from the software-engineering tag. We cleaned the file (convert to lower case, replace spaces with hyphen) in **cleantags_final_m10.csv**, which we use in crawl_archive and crawl_story.
- **pathDict.csv**: Tags sorted by shortest distance to software-engineering, with the shortest tag path shown. E.g. "code-coverage" -> "software-development" -> "software-engineering"
- **df_story_raw_sample.csv**: A sample of the first 100 articles crawled in the raw data form. 

# Crawlers

Contains the code for Scrapy spiders.

- **crawl_tag**: Crawl the network of related tags on a Medium tag (e.g. medium.com/tag/software-engineering). 
- **crawl_story**: Crawl the story level of Medium (specifically, everything enclosed within the \<article> tag of the HTML. The spider crawls from tags -> tag archive -> story. We obtained the tags from the crawl_tag spider.
- **crawl_archive**: Crawl only the archive level of Medium. This is favorable to crawling the story level as the story text / raw HTML takes time to fetch. Crawling archive level is 5-10X faster. 