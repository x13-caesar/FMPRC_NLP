#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@author: qiangwenxu
"""

import csv
import json
import os
import re
import time

import pandas as pd
import requests
from lxml import etree


## get html from site 
def get_etree(url, encoding='GB2312', headers={
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11) AppleWebKit/601.1.56 (KHTML, like Gecko) Version/9.0 Safari/601.1.56',
    }):
    response = requests.get(url, headers=headers)
    response.encoding = 'GB2312'
    return etree.HTML(response.text)

## get text data and record into file, from contents page url
# base: string, contents page url
# ending: string, specific page url suffix
# datafile: string, file path of text record dataset (cotains three columns: title, date, body)
# log: string, file path of log, recording the last visited article url of each section
def get_data(column, page_suffix, log):
    # Read the log info:
    print('\033[1;34m[!] Loading the log file...\033[0m\n')
    log_json = json.load(open(log, 'r'))
    datafile, base, last_update = log_json[column]

    # Create the csv data file
    if not os.path.exists(datafile):
        data = pd.DataFrame(columns=['title', 'date', 'body'])
        data.to_csv(datafile, index=False)
        print("\033[1;34m[!] No existing data file. A new one has been created!\033[0m")

    updated = False
    url = base + page_suffix
    table = get_etree(url)
    print("\033[1;34m[!] Getting HTML of %s...\033[0m\n" % url)

    pages = table.xpath('/html/body/div[5]/div[1]/div/a/text()')
    posts = table.xpath('/html/body/div[5]/div[1]/ul/li/a/@href') # url
    publish_date = table.xpath('/html/body/div[5]/div[1]/ul/li/i/text()') # issue date

    # Iterate the table
    section_domian = base.split('GB')[0]
    print('[-] Current section domian:', section_domian)
    print('[-] Total posts in current page:', len(posts))
    for suffix, date in zip(posts, publish_date):

        # We've arrived our last visit
        if suffix == last_update:
            print("\033[1;34m[!] The dataset is updated now.\033[0m")
            updated = True
            break
        # If the suffix starts with 'http', it's linked to a post in other column, we can just ignore it.
        if suffix.startswith('http'):
            continue

        post = get_etree(section_domian + suffix)
        print('\033[1;34m[+] Visit URL: %s \033[0m' % (section_domian+suffix))
        title = post.xpath('/html/body/div[7]/div[1]/div/h1/text()')
        # Handle the multiple-line title
        if type(title) == list:
            title = '，'.join(title)
        # Get the article body
        body = ''.join(post.xpath('/html/body/div[7]/div[1]/div/div[2]/p/text()')).strip()
        print('[-] Getting data of article "%s", issue date %s ' % (title, date))
        print('[-] Preview: %s \n' % body[:30])

        # Write into file
        with open(datafile, 'a+', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                title,
                re.sub('年|月', '-', date).replace('日', '').strip('[]'),
                body
            ])

    # Record the latest post url we've scraped if we're in the 1st page
    if page_suffix[:6] == 'index1':
        log_json[column][2] = posts[0]
        with open(log, 'w') as new:
            json.dump(log_json, new, indent=4)

    # If there is a next page, go for it
    if '下一页' in pages and not updated:
        print('\033[1;34m[!] Continue to the next page... \033[0m')
        next_ending = table.xpath('/html/body/div[5]/div[1]/div/a[contains(text(),"下一页")]/@href')
        if next_ending:
            time.sleep(5)
            get_data(column, next_ending[0], log)



def update_text(begin_suffix, log_file, avoid=[]):
    json_data = json.load(open(log_file, 'r'))
    for c in json_data.keys():
        if c in json_data.keys():
            get_data(c, begin_suffix, log_file)
    

def add_column(column_name, data_path, column_base, initial_stop_post, log_file='history.json'):
    json_data = json.load(open(log_file, 'r'))
    json_data[column_name] = (data_path, column_base, initial_stop_post)
    with open(log_file, 'w') as f:
        json.dump(json_data, f, indent=4)

if __name__ == '__main__':
    # The starting page suffix
    BEGIN = 'index1.html'
    LOG = '/Users/qiangwenxu/playground/NewChinaNewspeak/WebCrawler/history.json'

    # Use the following block if you want to add any column
    # Example for new_columns:
    ##  {'专栏名称': ('user/data/abc.csv', "http://theory.people.com.cn/GB/111111/", "")}
    new_columns = {}
    if new_columns:
        for c, (d, base, stop) in new_columns.items():
            add_column(c, d, base, stop)
    
    update_text(BEGIN, LOG)


