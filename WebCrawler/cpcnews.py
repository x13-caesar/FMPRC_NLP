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



if __name__ == '__main__':

    # '中央文件'栏目
    data_zywj = '/Users/qiangwenxu/playground/NewChinaNewspeak/data/cpcnews_zywj.csv'
    base_zywj = 'http://cpc.people.com.cn/GB/67481/431391/431393/'
    # '重要评论'栏目
    data_zypl = '/Users/qiangwenxu/playground/NewChinaNewspeak/data/cpcnews_zypl.csv'
    base_zypl = 'http://theory.people.com.cn/GB/409499/'
    # '中央精神‘栏目
    data_zyjs = '/Users/qiangwenxu/playground/NewChinaNewspeak/data/cpcnews_zyjs.csv'
    base_zyjs = 'http://dangjian.people.com.cn/GB/394443/'
    # '各地动态'栏目
    data_gddt = '/Users/qiangwenxu/playground/NewChinaNewspeak/data/cpcnews_gddt.csv'
    base_gddt = 'http://dangjian.people.com.cn/GB/219967/'
    # '干部论坛'栏目
    data_gblt = '/Users/qiangwenxu/playground/NewChinaNewspeak/data/cpcnews_gblt.csv'
    base_gblt = 'http://dangjian.people.com.cn/GB/132289/'
    # '评论观点'栏目
    data_plgd = '/Users/qiangwenxu/playground/NewChinaNewspeak/data/cpcnews_plgd.csv'
    base_plgd = 'http://dangjian.people.com.cn/GB/394444/'
    # '学习教育'栏目
    data_xxjy = '/Users/qiangwenxu/playground/NewChinaNewspeak/data/cpcnews_xxjy.csv'
    base_xxjy = 'http://dangjian.people.com.cn/GB/141145/'
    # '专家辅导'栏目
    data_zjfd = '/Users/qiangwenxu/playground/NewChinaNewspeak/data/cpcnews_zjfd.csv'
    base_zjfd = 'http://dangjian.people.com.cn/GB/394323/'
    # '国企党建'栏目
    data_gqdj = '/Users/qiangwenxu/playground/NewChinaNewspeak/data/cpcnews_gqdj.csv'
    base_gqdj = 'http://dangjian.people.com.cn/gq/'
    # '非公党建'栏目
    data_fgdj = '/Users/qiangwenxu/playground/NewChinaNewspeak/data/cpcnews_fgdj.csv'
    base_fgdj = 'http://dangjian.people.com.cn/fg/'
    # '学校党建'栏目
    data_xxdj = '/Users/qiangwenxu/playground/NewChinaNewspeak/data/cpcnews_xxdj.csv'
    base_xxdj = 'http://dangjian.people.com.cn/xx/'
    # '机关党建'栏目
    data_jgdj = '/Users/qiangwenxu/playground/NewChinaNewspeak/data/cpcnews_jgdj.csv'
    base_jgdj = 'http://dangjian.people.com.cn/GB/117094/'
    # '街道社区党建'栏目
    data_jdsqdj = '/Users/qiangwenxu/playground/NewChinaNewspeak/data/cpcnews_jdsqdj.csv'
    base_jdsqdj = 'http://dangjian.people.com.cn/GB/117098/'
    # '军队党建'栏目
    data_jddj = '/Users/qiangwenxu/playground/NewChinaNewspeak/data/cpcnews_jddj.csv'
    base_jddj = 'http://dangjian.people.com.cn/GB/117101/'
    # '农村基层党建'栏目
    data_ncjcdj = '/Users/qiangwenxu/playground/NewChinaNewspeak/data/cpcnews_ncjcdj.csv'
    base_ncjcdj= 'http://dangjian.people.com.cn/GB/117100/'
    # '高层动态'栏目
    data_gcdt = '/Users/qiangwenxu/playground/NewChinaNewspeak/data/cpcnews_gcdt.csv'
    base_gcdt = 'http://cpc.people.com.cn/GB/64093/64094/'
    # '经济社会'栏目
    data_jjsh = '/Users/qiangwenxu/playground/NewChinaNewspeak/data/cpcnews_jjsh.csv'
    base_jjsh = 'http://theory.people.com.cn/GB/49154/'
    # '国际外交'栏目
    data_gjwj = '/Users/qiangwenxu/playground/NewChinaNewspeak/data/cpcnews_gjwj.csv'
    base_gjwj = 'http://theory.people.com.cn/GB/136457/'
    # '学术动态'栏目
    data_xsdt = '/Users/qiangwenxu/playground/NewChinaNewspeak/data/cpcnews_xsdt.csv'
    base_xsdt = 'http://theory.people.com.cn/GB/40534/'
    # '领导活动'栏目
    data_ldhd = '/Users/qiangwenxu/playground/NewChinaNewspeak/data/cpcnews_ldhd.csv'
    base_ldhd = 'http://cpc.people.com.cn/GB/64093/117005/'



    # The log file (keep track of where you've been in each column)
    log_path = '/Users/qiangwenxu/playground/NewChinaNewspeak/WebCrawler/history.json'

    jsonfile = json.load(open(log_path, 'r'))


    # Use the following block if you want to add any column
'''
    jsonfile['领导活动'] = (data_ldhd, base_ldhd, "")
    with open(log_path, 'w') as f:
        json.dump(jsonfile, f, indent=4)
'''

    begin = 'index1.html'
    for c in jsonfile.keys():
        if c in ['高层动态', '经济社会', '国际外交', '学术动态', '领导活动']:
            get_data(c, begin, log_path)
