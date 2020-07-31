from IPython.core.display import display, HTML
from multiprocessing import  Pool
from functools import partial
import numpy as np
import pandas as pd
from textblob import TextBlob
import textstat

from bs4 import BeautifulSoup
import re
import statistics


def parallelize(data, func, num_of_processes=8):
    data_split = np.array_split(data, num_of_processes)
    pool = Pool(num_of_processes)
    data = pd.concat(pool.map(func, data_split))
    pool.close()
    pool.join()
    return data

def run_on_subset(func, data_subset):
    return data_subset.apply(func, axis=1)

def parallelize_on_rows(data, func, num_of_processes=8):
    return parallelize(data, partial(run_on_subset, func), num_of_processes)

# Text from raw HTML
def extract_features_from_html_multiproc(data):
    if pd.notnull(data['StoryHTML']):
               
        # Using beautifulsoup        
        soup = BeautifulSoup(data['StoryHTML'], features="lxml")
        

        
        # Header information (author / title) is stored in <div> tag with no classname attribute
        # It is also the second section tag
        featured_image = False
        
        header = soup.find_all("section") # Header is the second section
        if len(header)>=2:
            if header[1].find_all("img", {"role":"presentation"}):
                featured_image = True

        # First <div> tag is the article itself, remove every other <div> afterwards
        headerDivs = soup.find_all("div", {'class':None})
        if (headerDivs):  
            for div in headerDivs[1:]:
                div.decompose()
        
        # Extract num. images
        img_count = int(len(soup.find_all("img")))
        if featured_image:
            img_count+=1
        
        # Extract Text
        text = soup.text
        
        if text:
            # Textblob for sentiment
            textBlob = TextBlob(text)
            sentiment_polarity = textBlob.sentiment.polarity
            sentiment_subjectivity = textBlob.sentiment.subjectivity
        
            TextSyllableNum = textstat.syllable_count(text)
            TextLexiconNum = textstat.lexicon_count(text, removepunct=True)
            TextSentenceNum = textstat.sentence_count(text)

            ReadabilityFleschEase = textstat.flesch_reading_ease(text)
            ReadabilitySMOG = textstat.smog_index(text)
            ReadabilityFleschKincaid = textstat.flesch_kincaid_grade(text)
            ReadabilityColemanLiau = textstat.coleman_liau_index(text)
            ReadabilityARI = textstat.automated_readability_index(text)
            ReadabilityDaleChall = textstat.dale_chall_readability_score(text)
            ReadabilityDifficultWordsList = textstat.difficult_words_list(text)
            ReadabilityDifficultWordsNum = textstat.difficult_words(text)
            ReadabilityLinsearWriteFormula = textstat.linsear_write_formula(text)
            ReadabilityGunningFog = textstat.gunning_fog(text)
            ReadabilityReadingTime = textstat.reading_time(text)
            ReadabilityConsensus = textstat.text_standard(text, float_output=True)

        else:
            sentiment_polarity = 0
            sentiment_subjectivity = 0

            TextSyllableNum = 0
            TextLexiconNum = 0
            TextSentenceNum = 0

            ReadabilityFleschEase = 0
            ReadabilitySMOG = 0
            ReadabilityFleschKincaid = 0
            ReadabilityColemanLiau = 0
            ReadabilityARI = 0
            ReadabilityDaleChall = 0
            ReadabilityDifficultWordsList = 0
            ReadabilityDifficultWordsNum = 0
            ReadabilityLinsearWriteFormula = 0
            ReadabilityGunningFog = 0
            ReadabilityReadingTime = 0
            ReadabilityConsensus = 0

        
        paragraphs = soup.find_all("p")
        if (paragraphs):
            paragraph_num = len(paragraphs)
        else:
            paragraph_num = 0
            
            
        # Extract bolds
        bolds = soup.find_all("strong")
        if bolds:
            bold_num = len(bolds)
        else:
            bold_num = 0

        
        # Extract italics
        italics = soup.find_all("em")
        if italics:
            italic_num = len(italics)
        else:
            italic_num = 0
            
        # Get unordered and ordered lists
        lists_unordered = soup.find_all("ul")
        if lists_unordered:
            lists_unordered_num = len(lists_unordered)
            lists_unordered_lengths = [len(item.text) for item in lists_unordered] # the length of each item of each list
            lists_unordered_items_sum = sum(lists_unordered_lengths)
            lists_unordered_items_median = statistics.median(lists_unordered_lengths)
            lists_unordered_items_mean = statistics.mean(lists_unordered_lengths)
            lists_unordered_items_std = np.std(lists_unordered_lengths)
            lists_unordered_items_min = min(lists_unordered_lengths)
            lists_unordered_items_max = max(lists_unordered_lengths)
        else:
            lists_unordered_num = 0
            lists_unordered_lengths = 0
            lists_unordered_items_sum = 0
            lists_unordered_items_median = 0
            lists_unordered_items_mean = 0
            lists_unordered_items_std = 0
            lists_unordered_items_min = 0
            lists_unordered_items_max = 0

        lists_ordered = soup.find_all("ol")
        if lists_ordered:
            lists_ordered_num = len(lists_ordered)
            lists_ordered_lengths = [len(item.text) for item in lists_ordered]
            lists_ordered_items_sum = sum(lists_ordered_lengths)
            lists_ordered_items_median = statistics.median(lists_ordered_lengths)
            lists_ordered_items_mean = statistics.mean(lists_ordered_lengths)
            lists_ordered_items_std = np.std(lists_ordered_lengths)
            lists_ordered_items_min = min(lists_ordered_lengths)
            lists_ordered_items_max = max(lists_ordered_lengths)
        else:
            lists_ordered_num = 0
            lists_ordered_lengths = 0
            lists_ordered_items_sum = 0
            lists_ordered_items_median = 0
            lists_ordered_items_mean = 0
            lists_ordered_items_std = 0
            lists_ordered_items_min = 0
            lists_ordered_items_max = 0

        # Extract num. words
        word_count = int(len(soup.text.split()))
        
        # Extract code
        # There are four ways that authors display code in a Medium article, the first two are retrievable.
        # 1) Codeblock: Use ``` ``` which is converted into <pre> tag. Available in data.
        # 2) Inline: <code> tag. Available in data.
        # 3) Import a Gist file. N/A in data since Gists are embedded content which are not captured by Scrapy and would require a deeper request level.
        # 4) Show it as an image. N/A in data since there is no distinguishing tag for "code" images and normal images.
        
        # Extract num. code blocks that use the Medium ``` format (have <pre> tag)
        codeblocks_default = soup.find_all("pre")

        codeblock_raw = [code.text for code in codeblocks_default]
        
        codeblock_num = len(codeblocks_default)
        
        # Get a list of the number of lines of code of each code block
        # Every code block has number of <br> + 1 lines
            # <pre>
            # ....
            # <br>
            # ....
            # </pre>        
        # Then compute basic statistics
        
        codeblock_lengths = [len(codeblock.find_all("br"))+len(codeblock.find_all("span")) for codeblock in codeblocks_default]
        if len(codeblock_lengths) > 0:
            codeblock_length_sum = sum(codeblock_lengths)
            codeblock_length_median = statistics.median(codeblock_lengths)
            codeblock_length_mean = statistics.mean(codeblock_lengths)
            codeblock_length_std = np.std(codeblock_lengths)
            codeblock_length_min = min(codeblock_lengths)
            codeblock_length_max = max(codeblock_lengths)
        else:
            codeblock_length_sum = 0
            codeblock_length_median = 0
            codeblock_length_mean = 0
            codeblock_length_std = 0
            codeblock_length_min = 0
            codeblock_length_max = 0
            
        # Extract number of <code> tags (inline code)
        code_inline = soup.find_all("code")
        code_inline_raw = [code.text for code in code_inline]
        code_inline_num = len(code_inline)

                
        # Extract a list of total links and their URLs
        # We need to filter out Medium's internal links (share post, author profile, etc)
        # These links contain the PostID, so we only collect <a> tags with href not containing PostID
        links_all = soup.find_all("a")
        link_urls = [link.attrs.get('href') for link in links_all if str(data['PostID']) not in link.attrs.get('href')]
        

        # Extract total number of links
        link_count = int(len(link_urls))
        
        # Extract number of highlights
        highlights = soup.find_all("mark")
        highlight_count = int(len(highlights))

        # Extract highlight text
        highlights_text = [hlt.text for hlt in highlights]

        # Extract image count
        # A genuine image does not have alt (used for user logo), so we use this fact to verify image elements
        # Get src and find number of unique URLs to find number of images
#         imgli = soup.find_all("img")
#         newLi = [re.search("\*.+(?![^\.])", img['src']).group(0).split(".", 1)[0] for img in imgli if (img.has_attr('src') and re.search("\*.+(?![^\.])", img['src']) is not None)]
#         if len(newLi) == 0:
#             img_count = len(set([img.attrs['src'] for img in imgli if img.has_attr('src')]))
#         else:
#             img_count = len(set(newLi))-1
    else:
        text = np.NaN
        sentiment_polarity = np.NaN
        sentiment_subjectivity = np.NaN
        
        TextSyllableNum = np.NaN
        TextLexiconNum = np.NaN
        TextSentenceNum = np.NaN

        ReadabilityFleschEase = np.NaN
        ReadabilitySMOG = np.NaN
        ReadabilityFleschKincaid = np.NaN
        ReadabilityColemanLiau = np.NaN
        ReadabilityARI = np.NaN
        ReadabilityDaleChall = np.NaN
        ReadabilityDifficultWordsList = np.NaN
        ReadabilityDifficultWordsNum = np.NaN
        ReadabilityLinsearWriteFormula = np.NaN
        ReadabilityGunningFog = np.NaN
        ReadabilityReadingTime = np.NaN
        ReadabilityConsensus = np.NaN

        word_count = np.NaN
        code_count = np.NaN
        
        img_count = np.NaN
        featured_image = np.NaN
        
        link_count = np.NaN
        link_urls = np.NaN
        
        highlights_text = np.NaN
        highlight_count = np.NaN
        
        code_inline_raw = np.NaN
        code_inline_num = np.NaN
        
        codeblock_raw = np.NaN
        codeblock_num = np.NaN
        codeblock_lengths = np.NaN
        codeblock_length_sum = np.NaN
        codeblock_length_median = np.NaN
        codeblock_length_mean = np.NaN
        codeblock_length_std = np.NaN
        codeblock_length_min = np.NaN
        codeblock_length_max = np.NaN
        
        lists_unordered_num = np.NaN
        lists_unordered_lengths = np.NaN
        lists_unordered_items_sum = np.NaN
        lists_unordered_items_median = np.NaN
        lists_unordered_items_mean = np.NaN
        lists_unordered_items_std = np.NaN
        lists_unordered_items_min = np.NaN
        lists_unordered_items_max = np.NaN

        lists_ordered_num = np.NaN
        lists_ordered_lengths = np.NaN
        lists_ordered_items_sum = np.NaN
        lists_ordered_items_median = np.NaN
        lists_ordered_items_mean = np.NaN
        lists_ordered_items_std = np.NaN
        lists_ordered_items_min = np.NaN
        lists_ordered_items_max = np.NaN
        
        paragraph_num  = np.NaN
        italic_num = np.NaN
        bold_num = np.NaN
    return [text, sentiment_polarity, sentiment_subjectivity, word_count, TextSyllableNum, TextLexiconNum, TextSentenceNum, 
            ReadabilityFleschEase, ReadabilitySMOG, ReadabilityFleschKincaid, ReadabilityColemanLiau, ReadabilityARI, ReadabilityDaleChall, ReadabilityDifficultWordsList, ReadabilityDifficultWordsNum, ReadabilityLinsearWriteFormula, ReadabilityGunningFog, ReadabilityReadingTime, ReadabilityConsensus, 
            featured_image, code_inline_raw, code_inline_num, 
            codeblock_raw, codeblock_num, codeblock_lengths, codeblock_length_sum, codeblock_length_median, codeblock_length_mean, codeblock_length_std, codeblock_length_min, codeblock_length_max, 
            lists_ordered_num, lists_ordered_lengths, lists_ordered_items_sum, lists_ordered_items_median, lists_ordered_items_mean, lists_ordered_items_std, lists_ordered_items_min, lists_ordered_items_max,
            lists_unordered_num, lists_unordered_lengths, lists_unordered_items_sum, lists_unordered_items_median, lists_unordered_items_mean, lists_unordered_items_std, lists_unordered_items_min, lists_unordered_items_max,
            img_count, link_urls, link_count, highlights_text, highlight_count, paragraph_num, italic_num, bold_num]
    
# test = df
# test[['Text', 'WordNum', 'HasFeaturedImage','CodeInlineRaw', 'CodeInlineNum', 'CodeBlockRaw', 'CodeBlockNum', "CodeBlockLengthList", "CodeBlockLengthSum", "CodeBlockLengthMedian", "CodeBlockLengthMean", "CodeBlockLengthMin", "CodeBlockLengthMax", 'ImgNum', 'LinkURLList', 'LinkNum', 'HLightTextList', 'HlightNum']] = df.apply(extract_features_from_html, axis=1, result_type="expand")
# del test['StoryHTML']