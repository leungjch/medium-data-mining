# -*- coding: utf-8 -*-

# crawl Medium posts

# command
# scrapy crawl medium -o df_story.csv -t csv --loglevel WARNING -s JOBDIR=crawls/medium-1

# future crawl
# https://medium.com/sitemap/sitemap.xml

import os
import scrapy
import pandas as pd
from scrapy_splash import SplashRequest
import re
from bs4 import BeautifulSoup
import json
import csv
import functools 
import operator
import time
import logging


class ArticleItem(scrapy.Item):
    StoryIndex = scrapy.Field()
    PostID = scrapy.Field()
    User = scrapy.Field()
    UserURL = scrapy.Field()
    Company = scrapy.Field()
    CompanyURL = scrapy.Field()
    PublishedDate = scrapy.Field()
    ReadingTime = scrapy.Field()
    StoryURL_Story = scrapy.Field()
    StoryTitle = scrapy.Field()
    StoryURL = scrapy.Field()
    TagSource = scrapy.Field()
    Tag1 = scrapy.Field()
    Tag2 = scrapy.Field()
    Tag3 = scrapy.Field()
    Tag4 = scrapy.Field()
    Tag5 = scrapy.Field()
    ClapCount_Card = scrapy.Field()
    ClapCount_Story = scrapy.Field()
    VoterCount = scrapy.Field()
    ResponseNum_Card = scrapy.Field()
    ResponseNum_Story = scrapy.Field()
    isPaywall = scrapy.Field()
    StoryHTML = scrapy.Field()

    # Suppress logging to PostID when article successfully scraped
    def __repr__(self):
        return repr({"Story successfully crawled with": self['StoryURL']})

class MediumbotSpider(scrapy.Spider):

    scrapy.utils.log.configure_logging(install_root_handler=False)
    root_logger= logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler('log.txt', 'w', 'utf-8')
    handler.setFormatter(logging.Formatter('%(name)s %(message)s')) 
    root_logger.addHandler(handler)

    name = 'medium'

    # get tags
    tags = []
    # Crawl missed tags
    # with open('cleantags_final_m10.csv', newline='') as f:
    with open('tags_to_complete_jul26.csv', newline='') as f:
        reader = csv.reader(f)
        tags = list(reader)
        # tags = sum(reader,[])
    tags = functools.reduce(operator.iconcat, tags, []) # unnest list

    start_urls = []
    for tag in tags:
        start_urls.append('https://medium.com/tag/' + tag + '/archive')

    handle_httpstatus_list = [400, 401, 403, 404, 429, 500, 503]
    
    count_story = 0
    max_stories = 0

    doneFirstRow = False
    print('\nStart crawling:')

    def parse(self, response):
        str_url = response.url
        list_sub_index = ''

        if response.status in self.handle_httpstatus_list:
            print('\n[ERROR] getting index page failed: ' + str(response.status) + ' at: ' + str_url)
            if response.status == 429:
                self.crawler.engine.pause()
                time.sleep(120) # Wait 2 minutes to renew rate limit
                self.crawler.engine.unpause()

        else:
            is_day_page = False
            
            # is root now
            if re.match("^https:\/\/medium\.com\/tag\/[a-z\-]+\/archive$", str_url):

                # get year
                list_sub_index = response.xpath('//div[@class="timebucket u-inlineBlock u-width50"]//a//@href').extract()
            # is year now
            elif str_url[-4:].isdigit() and (str_url[-12:-5] == 'archive'):
                # get month
                list_sub_index = response.xpath('//div[@class="timebucket u-inlineBlock u-width80"]//a//@href').extract()
            # is month now
            elif str_url[-2:].isdigit() and str_url[-7:-3].isdigit() and (str_url[-15:-8] == 'archive'):
                # get day
                list_sub_index = response.xpath('//div[@class="timebucket u-inlineBlock u-width35"]//a//@href').extract()
            # is day now
            elif str_url[-2:].isdigit() and str_url[-5:-3].isdigit() and str_url[-10:-6].isdigit() and (str_url[-18:-11] == 'archive'):
                is_day_page = True
                # crawl all stories in this index page

                yield scrapy.Request(str_url, callback = self.parse_end_page, dont_filter = True)
            else:
                print('[ERROR] in getting sub-index from current page: ' + str_url)
            # run only when not reaching day page yet
            if is_day_page == False:
                # in one index page there is no sub-index anymore, therefore crawl all stories under this index page are enough
                if len(list_sub_index) == 0:
                    # parse the current page for all stories here
                    # crawl all stories in this index page
                    print("crawling to parse story end page", str_url)

                    yield scrapy.Request(str_url, callback = self.parse_end_page, dont_filter = True)
                # in one index page there are sub-index
                elif len(list_sub_index) > 0:
                    for sub_index in list_sub_index:
                        print("going to indices", sub_index)
                        
                        yield scrapy.Request(sub_index, callback=self.parse)
                else:
                    pass

    # parse for one day's stories or all stories from one period
    def parse_end_page(self, response):
        str_url = response.url
        if response.status in self.handle_httpstatus_list:
            print('\n[ERROR] getting end page failed: ' + str(response.status) + ' at: ' + str_url)
        else:

            print('archive url', str_url, 'with ', len(response.css('div.postArticle')), " stories")
            self.max_stories += len(response.css('div.postArticle'))

            for story in list(set(response.css('div.postArticle'))):
                newArticle = ArticleItem()
                newArticle['TagSource'] = (re.search("\/tag\/(.*?)\/archive", str_url).group(1))

                newArticle['StoryIndex'] = self.count_story
                # StoryTitle
                list_story_title_0 = story.css('div.postArticle-content section div.section-content div h1::text').extract()
                list_story_title_1 = story.css('div.postArticle-content section div.section-content div h3::text').extract()
                list_story_title_2 = story.css('div.postArticle-content section div.section-content div h3 strong::text').extract()
                list_story_title_3 = story.css('div.postArticle-content section div.section-content div h4::text').extract()
                list_story_title_4 = story.css('div.postArticle-content section div.section-content div h4 strong::text').extract()
                list_story_title_5 = story.css('div.postArticle-content section div.section-content div p::text').extract()
                list_story_title_6 = story.css('div.postArticle-content section div.section-content div h3 strong em::text').extract()
                list_story_title_7 = story.css('div.postArticle-content section div.section-content div h4 strong em::text').extract()
                list_story_title = list_story_title_0 + list_story_title_1 + list_story_title_2 + list_story_title_3 + list_story_title_4 + list_story_title_5 + list_story_title_6 + list_story_title_7
                
                if len(list_story_title_0) >= 1:
                    newArticle['StoryTitle'] = list_story_title_0[0]
                elif len(list_story_title_1) >= 1:
                    newArticle['StoryTitle'] = list_story_title_1[0]
                elif len(list_story_title_2) >= 1:
                    newArticle['StoryTitle'] = list_story_title_2[0]
                elif len(list_story_title_3) >= 1:
                    newArticle['StoryTitle'] = list_story_title_3[0]
                elif len(list_story_title_4) >= 1:
                    newArticle['StoryTitle'] = list_story_title_4[0]
                elif len(list_story_title_5) >= 1:
                    newArticle['StoryTitle'] = list_story_title_5[0]
                elif len(list_story_title_6) >= 1:
                    newArticle['StoryTitle'] = list_story_title_6[0]
                elif len(list_story_title_7) >= 1:
                    newArticle['StoryTitle'] = list_story_title_7[0]
                elif len(list_story_title) == 0:
                    newArticle['StoryTitle'] = "NaN"
                    #print('[ERROR] story ', str(self.count_story) + ' at: ' + str_url + ' has no StoryTitle')
                else:
                    print('[ERROR] story ', str(self.count_story) + ' at: ' + str_url + ' has StoryTitle issue in code')

                # StoryURL
                list_story_url = story.css('div a::attr(href)').extract()
                if len(list_story_url) == 0:
                    print('[ERROR] story ', str(self.count_story) + ' at: ' + str_url + ' has no StoryURL')
                    newArticle['StoryURL'] = "NaN"
                elif len(list_story_url) > 0:
                    newArticle['StoryURL'] = list_story_url[-1]
                else:
                    print('[ERROR] story ', str(self.count_story) + ' at: ' + str_url + ' has StoryURL issue in code')
                    newArticle['StoryURL'] = "NaN"

                # User, Company, CompanyURL
                list_user = story.css('div.u-marginBottom15 div div.postMetaInline-authorLockup a::text').extract()
                if len(list_user) == 0:
                    print('[ERROR] story ', str(self.count_story) + ' at: ' + str_url + ' has no User')
                elif len(list_user) == 1:
                    newArticle['User'] = list_user[0]
                elif len(list_user) == 2:
                    newArticle['User'] = list_user[0]
                    newArticle['Company'] =list_user[1]
                    newArticle['CompanyURL'] = story.css('div.u-marginBottom15 div div.postMetaInline-authorLockup a::attr(href)').extract()[1]
                else:
                    print('[ERROR] story ', str(self.count_story) + ' at: ' + str_url + ' has User issue in code')
                
                # Article is paywalled if it has a star icon beside the preview
                list_star = story.css("span.svgIcon.svgIcon--star")
                if len(list_star) == 1:
                    newArticle['isPaywall'] = True
                elif len(list_star) == 0:
                    newArticle['isPaywall'] = False
                else:
                    newArticle['isPaywall'] = "NaN"
                    print('[ERROR] story ', str(self.count_story) + ' at: ' + str_url + ' has Paywall issue in code')

                # UserURL
                list_user_url = story.css('div.u-marginBottom15 div div.postMetaInline-avatar a::attr(href)').extract()
                if len(list_user_url) == 0:
                    print('[ERROR] story ', str(self.count_story) + ' at: ' + str_url + ' has no UserURL')
                elif len(list_user_url) == 1:
                    newArticle['UserURL'] = list_user_url[0]
                else:
                    print('[ERROR] story ', str(self.count_story) + ' at: ' + str_url + ' has UserURL issue in code')
                
                # PublishedDate
                list_published_date = story.css('div.u-marginBottom15 div div.postMetaInline-authorLockup time::attr(datetime)').extract()
                if len(list_published_date) == 0:
                    print('[ERROR] story ', str(self.count_story) + ' at: ' + str_url + ' has no PublishedDate')
                elif len(list_published_date) == 1:
                    newArticle['PublishedDate'] = list_published_date[0]
                else:
                    print('[ERROR] story ', str(self.count_story) + ' at: ' + str_url + ' has PublishedDate issue in code')
                
                # ReadingTime
                # Comments/non stories have no reading time
                list_reading_time = story.css('div.u-marginBottom15 div div.postMetaInline-authorLockup span::attr(title)').extract()
                if len(list_reading_time) == 0:
                    # common for posts that are responses to stories
                    # print('[ERROR] story ', str(self.count_story) + ' at: ' + str_url + ' with title ' + str(list_story_title) +  ' has no ReadingTime')
                    newArticle['ReadingTime'] = "NaN"

                elif len(list_reading_time) == 1:
                    newArticle['ReadingTime'] = list_reading_time[0]
                else:
                    print('[ERROR] story ', str(self.count_story) + ' at: ' + str_url + ' with title ' + str(list_story_title) + ' has ReadingTime issue in code')
                
                # ClapCountNum (estimate)
                list_count = story.css('div.u-paddingTop10 div.u-floatLeft button::text').extract()
                if len(list_count) == 0:
                    newArticle['ClapCount_Card'] = 0
                elif len(list_count) == 1:
                    newArticle['ClapCount_Card'] = list_count[0]
                else:
                    print('[ERROR] story ', str(self.count_story) + ' at: ' + str_url + ' has ClapCount issue in code')

                # Response count (card)
                list_response = story.css("div.u-clearfix.u-paddingTop10 div.buttonSet.u-floatRight a::text").extract()
                if len(list_response) > 0:
                    newArticle['ResponseNum_Card'] = list_response[-1]
                else:
                    newArticle['ResponseNum_Card'] = 0

                copy_count_story = self.count_story
                if len(list_story_url) > 0:
                    yield scrapy.Request(list_story_url[-1], callback=self.parse_story, meta = {'article':newArticle}, dont_filter=True)
                self.count_story = self.count_story + 1

    # parse for one story
    def parse_story(self, response):
        str_url = response.url

        meta_copy = response.meta.copy()
        newArticle = response.meta['article']
        current_index = newArticle['StoryIndex']
        newArticle['StoryURL_Story'] = str_url

        if response.status in self.handle_httpstatus_list:
            print('\n[ERROR] getting story failed: ' + str(response.status) + ' at: ' + str_url)
        else:
            # TODO: Scrape HTML, text, # images, # headings, # codeblocks, # bold, # italics, # links, emoji, quotes, mentions, lists, HIGHLIGHT

            soup = BeautifulSoup(response.body,'html.parser')

            article = soup.find_all("article")
            if len(article) == 1:
                newArticle['StoryHTML'] = str(article)
            else:
                 newArticle['StoryHTML'] = 'NaN'
            # Get tags
            tags_raw = soup.find_all("a", href = re.compile("\/tag\/[a-z\-]+"), text=True)
            if len(tags_raw) <= 0: # Tag must contain at least the TagSource, so if empty list, wrong tag links
                tags_raw = soup.find_all("a", href = re.compile("\/tagged\/[a-z\-]+"), text=True)
            elif len(tags_raw) <= 0:
                tags_raw = soup.find_all("a", href = re.compile("\/tags\/[a-z\-]+"), text=True)
            tags_clean = []
            for raw_tag in tags_raw:
                tag_clean = raw_tag.text.strip().lower().replace(" ", "-") # Get the text from tag and convert to lower case hyphenated
                tags_clean.append(tag_clean)
            while len(tags_clean) < 5:
                tags_clean.append("NaN")

            # Get response number (exact)
            responses = soup.find(lambda tag:tag.name=="span" and "See response" in tag.text)
            if responses:
                responsenum = re.search("\((.*?)\)",responses.text).group(1)
                newArticle['ResponseNum_Story'] = responsenum
            elif soup.find(lambda tag:tag.name=="span" and "Write the first response" in tag.text):
                newArticle['ResponseNum_Story'] = 0
            else:
                newArticle['ResponseNum_Story'] = "NaN"
                # Try to see if it has no responses

            newArticle['Tag1'] = tags_clean[0]
            newArticle['Tag2'] = tags_clean[1]
            newArticle['Tag3'] = tags_clean[2]
            newArticle['Tag4'] = tags_clean[3]
            newArticle['Tag5'] = tags_clean[4]

            # Get number of responses



            # Get PostID
            postId_exists = soup.find("meta", {"name":"parsely-post-id"}, content=True)
            if postId_exists:
                newArticle['PostID'] = postId_exists['content']
                # print("PostID is: ", postId_exists['content'])

                # Get claps and voters
                # Prepare query to simulate request for additional info when clicking clap button (requires postId)
                requestBody = {
                "operationName": "PostVotersDialogQuery",
                "variables": {
                    "postId": postId_exists['content'],
                    "pagingOptions": {
                    "limit": 10
                    }
                },
                "query": "query PostVotersDialogQuery($postId: ID!, $pagingOptions: PagingOptions) {\n  post(id: $postId) {\n    id\n    title\n    clapCount\n    voterCount\n    voters(paging: $pagingOptions) {\n      items {\n        user {\n          id\n          username\n          name\n          bio\n          ...UserAvatar_user\n          ...UserFollowButton_user\n          __typename\n        }\n        clapCount\n        __typename\n      }\n      pagingInfo {\n        next {\n          page\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    ...UserFollowButton_post\n    __typename\n  }\n}\n\nfragment UserAvatar_user on User {\n  username\n  id\n  name\n  imageId\n  mediumMemberAt\n  __typename\n}\n\nfragment UserFollowButton_user on User {\n  ...UserFollowButtonSignedIn_user\n  ...UserFollowButtonSignedOut_user\n  __typename\n}\n\nfragment UserFollowButtonSignedIn_user on User {\n  id\n  isFollowing\n  __typename\n}\n\nfragment UserFollowButtonSignedOut_user on User {\n  id\n  ...SusiClickable_user\n  __typename\n}\n\nfragment SusiClickable_user on User {\n  ...SusiContainer_user\n  __typename\n}\n\nfragment SusiContainer_user on User {\n  ...SignInOptions_user\n  ...SignUpOptions_user\n  __typename\n}\n\nfragment SignInOptions_user on User {\n  id\n  name\n  __typename\n}\n\nfragment SignUpOptions_user on User {\n  id\n  name\n  __typename\n}\n\nfragment UserFollowButton_post on Post {\n  collection {\n    id\n    __typename\n  }\n  ...UserFollowButtonSignedOut_post\n  __typename\n}\n\nfragment UserFollowButtonSignedOut_post on Post {\n  ...SusiClickable_post\n  __typename\n}\n\nfragment SusiClickable_post on Post {\n  id\n  mediumUrl\n  ...SusiContainer_post\n  __typename\n}\n\nfragment SusiContainer_post on Post {\n  id\n  __typename\n}\n"
                }

                yield scrapy.Request("https://medium.com/_/graphql", method='POST', 
                                body=json.dumps(requestBody), callback=self.parse_clap, meta = {'article':newArticle},
                                headers={'Content-Type':'application/json'}, dont_filter=False)

            # in Medium archive but redirects to non-medium domain, filter these articles out later
            # e.g. https://elidourado.com/blog/utopia-infinite-elasticity/
            else:
                print("PostID does not exist for story at ", str_url)
                newArticle['PostID'] = "NaN"
                newArticle['ClapCount_Story'] = "NaN"
                newArticle['VoterCount'] = "NaN"
                yield newArticle

    def parse_clap(self,response):
        try:

            meta_copy = response.meta.copy()
            # current_index = ['StoryIndex_clap']
            current_index = 0

            newArticle = response.meta['article']

            jsonresponse = json.loads(response.body_as_unicode())

            if jsonresponse['data']['post']['voterCount']:
                newArticle['VoterCount'] = jsonresponse['data']['post']['voterCount']
            else:
                newArticle['VoterCount'] = 0

            if jsonresponse['data']['post']['clapCount']:
                newArticle['ClapCount_Story'] = jsonresponse['data']['post']['clapCount']
            else:
                newArticle['ClapCount_Story'] = 0
        except TypeError:
            newArticle['VoterCount'] = 0
            newArticle['ClapCount_Story'] = 0
            print("TypeError occurred in", newArticle['StoryURL'])
        print("Finished story ", newArticle['StoryIndex'], "out of ", self.max_stories, " crawled")

        yield newArticle