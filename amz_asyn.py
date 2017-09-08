#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/9/2 下午10:26
# @Author  : zbz
# @Site    :
# @File    : fuck2.py
# @Software: PyCharm
import aiohttp
import asyncio
import requests
from bs4 import BeautifulSoup
import pymysql
import json
import time
import hashlib
import re
mysql_config = {
    "host":"120.24.51.24",
    "user":"developer",
    "password":"123123",
    "db":"yms_erp_dev",
    "charset":"utf8",
    "port":3306
}
headers_list = {
    "Host":"www.amazon.com",
    "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
    "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding":"",
    "Origin":"https://www.amazon.com",
    "X-Requested-With":"XMLHttpRequest",
    "Content-Type":"application/x-www-form-urlencoded;charset=UTF-8",
    "Connection":"keep-alive",
    "Referer":"https://www.amazon.com/AmazonBasics-Velvet-Hangers-50-Pack-Black/product-reviews/B01BH83OOM/ref=cm_cr_getr_d_paging_btm_1?ie=UTF8&reviewerType=all_reviews&pageNumber=1&sortBy=recent",
           }

sema = asyncio.Semaphore(5)
asin = "B01BH83OOM"
sql = 'INSERT INTO amz_review_comment (star, author_id, review_title, author, review_date,review_id,asin,create_time,vp,review,review_md5) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
start_url ='https://www.amazon.com/product-reviews/{}?reviewerType=all_reviews&sortBy=recent'.format(asin)
url='https://www.amazon.com/ss/customer-reviews/ajax/reviews/get/ref=cm_cr_getr_d_paging_btm_next_5'
soup_result = {}
response_list = []
conn = pymysql.connect(**mysql_config)
cursor = conn.cursor()

proxy = requests.get('http://123.207.17.216:5000', auth=('admin', 'yms_amz')).text
proxies = "http://"+proxy
print(proxies)
#proxies = {"http":"http://"+"222.94.150.39:6666"}

def md5(data):
    data = bytes(data, encoding="utf8")
    m2 = hashlib.md5()
    m2.update(data)
    return m2.hexdigest()



def trans_format(time_string, from_format, to_format='%Y.%m.%d %H:%M:%S'):
    time_struct = time.strptime(time_string, from_format)
    times = time.strftime(to_format, time_struct)
    return times

def my_get(url,proxies,headers = headers_list):
    res = requests.get(url,headers = headers,proxies={"http":proxies},timeout=2)
    if res.status_code == 200:
        return res
    else:
        print(res.text)
        raise OSError


#解析出总评论数
def rev_num(res):
    review_num = re.findall("totalReviewCount\S>([\d|,]+)</span>",res)[0]
    review_num = int(review_num.replace(',','')) if review_num else 0
    return review_num

#解析函数
def parse(ever_page_html):
    soup = BeautifulSoup(ever_page_html, "html.parser")
    soup_result["start"] = soup.findAll("span", attrs={'class': "a-icon-alt"})[0].text[0]
    soup_result["author"] = soup.findAll("a", attrs={'data-hook': "review-author"})[0].text
    soup_result["author_id"] = soup.findAll("a", attrs={'data-hook': "review-author"})[0].get("href").split("/")[-2]
    soup_result["review_title"] = soup.findAll("a", attrs={'data-hook': "review-title"})[0].text
    review_date = soup.findAll("span", attrs={'data-hook': "review-date"})[0].text[3:]
    soup_result["review_date"] = trans_format(review_date, '%B %d, %Y', '%Y-%m-%d')
    soup_result["review_id"] = soup.findAll("div", attrs={'data-hook': "review"})[0].get("id")
    soup_result["review"] = soup.findAll("span", attrs={'data-hook': "review-body"})[0].text
    is_vp = soup.findAll("span", attrs={'data-hook': "avp-badge"})
    soup_result["vp"] = "1" if is_vp else '0'
    return soup_result

#迭代入库
def get_xhr_parse(html,sql):
    sql_many=[]
    now =time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    html_list = html.split("&&&")
    for x in html_list[3:-3]:
        ever_page_html = json.loads(x)[2:]
        soup_result = parse(ever_page_html=ever_page_html[0])
        sql_many.append([soup_result["start"],soup_result["author_id"],soup_result["review_title"],soup_result["author"],soup_result["review_date"],soup_result["review_id"],asin,now,soup_result["vp"],soup_result["review"],md5(soup_result["review_title"]+soup_result["review"])])
    my_db(sql_many,sql)
#异步协程获取内容，返回到res_list内
async def get_xhr(page_num,asin,headers=headers_list,proxies=proxies):
    data = "sortBy=recent&reviewerType=all_reviews&formatType=&filterByStar=&pageNumber={}&filterByKeyword=&shouldAppend=undefined&deviceType=desktop&reftag=cm_cr_arp_d_paging_btm_2&pageSize=50&asin={}&scope=reviewsAjax0".format(page_num,asin)

    with (await sema):
        try:
            async with aiohttp.ClientSession() as s:
                async with s.post(url=url,data=data,headers=headers,proxy=proxies) as r:
                    r = await r.text()
                    response_list.append(r)
        except:
            print('connect error')
    # async with aiohttp.request('post',url=url,data=data,headers=headers,proxy="http://"+"222.94.150.39:6666") as res:
    #     if res.status_code == 200:
    #         response_list.append(await res.text)
    #     else:
    #         raise IOError


#入库语句
def my_db(data):
    try:
        cursor.executemany(sql, data)
        conn.commit()
    except Exception as e :
        print(e)
def handle(param2=None):
    start_res = my_get(start_url,headers = headers_list,proxies =proxies)
    event_loop = asyncio.get_event_loop()
    _rev_num =rev_num(start_res.text)
    print(_rev_num)
    f = asyncio.wait([get_xhr(num,asin,proxies= proxies) for num in range(1,_rev_num//50+2)])
    event_loop.run_until_complete(f)
    for response in response_list:
        get_xhr_parse(response)

handle()





