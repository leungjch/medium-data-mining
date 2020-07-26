# -*- coding: utf-8 -*-

# crawl Medium posts

import os
import scrapy
import pandas as pd
import pickle
from bs4 import BeautifulSoup

# max of 9 related tags are displayed on one tag page

class Mediumbot_SE_Spider(scrapy.Spider):
    
    name = 'tagbot-SE'

    str_tag = 'Software-Engineering'
    str_url = 'https://medium.com/tag/' + str_tag
    start_urls = [str_url]
    n = 0
    handle_httpstatus_list = [400, 401, 403, 404, 429, 500, 503]
    
    cols = ['tag_self', 'tag1', 'tag2', 'tag3', 'tag4', 'tag5', 'tag6', 'tag7', 'tag8', 'tag9', 'tag10']

    # df_tag = pd.DataFrame(columns = cols)
    df_tag = pd.read_csv("data_SE.csv")
    print(df_tag.head())
    # graph = {}
    #graph = pickle.load(open("graph_SE.pkl", "rb"))
    print('\nStart crawling:')

    def parse(self, response):
        str_url = response.url
        # self.df_tags.loc
        tag_self = response.css("h1.heading-title.heading-title--bold.u-marginTop0.u-xs-marginTop20::text").get()
        tags_clean = response.css('ul.tags.tags--postTags.tags--light a::text').getall()
        nextLinks = response.css('ul.tags.tags--postTags.tags--light a::attr(href)').extract()
        # print(nextLinks)
        
        tags_clean_df = tags_clean

        # if page has < 10 related tags, pad the remainder with NaN
        while len(tags_clean) < 10:
            tags_clean_df.append("NaN")

        # insert self tag at beginning
        tags_clean_df.insert(0, tag_self)
        tags_clean_df.insert(0, len(self.df_tag))
        #print(tag_self)
        # append new row
        #print( self.df_tag.tail(2).tag_self)
        #print(len(tags_clean_df))
        if tag_self not in self.df_tag.tag_self.unique(): # Very slow/inefficient, I did this to crawl the last 20,000 tags
            print(tags_clean_df)
            self.df_tag.loc[len(self.df_tag)] = tags_clean_df
            # add to graph
            #   
            self.n+=1
        else:
            print("duplicate")
        # save every 20,000 rows
        if self.n%100==0:

            # save data
            self.df_tag.to_csv("data_SE_new.csv") 
            #with open('graph_SE_new.pkl', 'wb') as f:
            #    pickle.dump(self.graph, f, pickle.HIGHEST_PROTOCOL)
        
        for link in nextLinks:
            yield scrapy.Request(link, callback = self.parse)