#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 21:42:08 2020

@author: qiangwenxu
"""

import os, sys
import urllib
from bs4 import BeautifulSoup as bs
import csv
import json
import time


def getSoup(listPage, headers=agents['MacMozilla']):
    req = urllib.request.Request(url=listPage, headers=headers)
    html = urllib.request.urlopen(req).read()
    soup = bs(html,"lxml")
    return soup


def getPosts(soup, classLabel, entryLabel, url_suffix, end):
    soup = getSoup(listPage)
    posts = soup.find(attrs={"class":classLabel}).find_all(entryLabel)
    titles = [p.find('a').get_text() for p in posts]
    urls = [url_suffix+str(p.find('a').get('href')) for p in posts]
    return titles, urls

def getArticle(url, timeLabel, bodyLabel):
    soup = getSoup(url)
    articleTime = soup.find(attrs={"class":"time"}).find(attrs={"id":"News_Body_Time"}).get_text()
    articleBody = soup.find(attrs={"id":bodyLabel}).get_text()
    return articleTime, articleBody


if __name__ == '__main__':
    section = int(input("What section you want to update?\n[1]重要讲话"))
    dict_Section = {1: 'zyjh_674906/'}
    
    agents = dict()
    agents['MacMozilla'] = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11) AppleWebKit/601.1.56 (KHTML, like Gecko) Version/9.0 Safari/601.1.56'}
    post_suffix = 'https://www.fmprc.gov.cn/web/ziliao_674904/'+dict_Section[section]
    
    with open('last_visited.json', 'rb') as f:
        visited = json.load(f)
        endPost = visited[str(section)]

        allTitles, allPosts = [], []
        for n in range(30):
            N_page = '' if n == 0 else '_'+str(n)
            fmprc_zyjh = 'https://www.fmprc.gov.cn/web/ziliao_674904/zyjh_674906/default'+N_page+'.shtml'
            pageSoup = getSoup(fmprc_zyjh)
            pageTitles, pageUrls = getPosts(pageSoup, "rebox_news", "li", post_suffix)
            allTitles.extend(pageTitles)
            allPosts.extend(pageUrls)
            if endPost in pageSoup: break
    
        fmprc_zyjh_result = []
        for title, url in zip(allTitles, allPosts):
            if url == endPost: break
            articleTime, articleBody = getArticle(url, "News_Body_Time", "News_Body_Txt_A")
            fmprc_zyjh_result.append([title, articleTime, articleBody])
            time.sleep(0.5)

        # 写入爬下来的数据
        with open("fmprc_zyjh.csv","w") as csvfile: 
            writer = csv.writer(csvfile)
            # 先写入columns_name
            writer.writerow(["title","time","body"])
            # 写入多行 用writerows
            writer.writerows(fmprc_zyjh_result)

        visited = json.load(f)
        visited[str(section)] = allPosts[0]
        f.close()

    
    