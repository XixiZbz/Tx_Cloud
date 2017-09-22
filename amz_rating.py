import gzip
import random
import re

import aiohttp
import asyncio
import json

from aiohttp import web
import pymysql
import requests
import lxml.etree as tree
from util import mysql_config,headers,get_proxy,my_session,change_ip,USER_AGENTS
from concurrent.futures import ThreadPoolExecutor

api_s = my_session()
conn = pymysql.connect(**mysql_config)
cursor = conn.cursor()


def deal_bussines(html):
    Html = tree.HTML(html)
    result ={}
    pre_star_rating = Html.xpath("//span[@data-hook='rating-out-of-text']/text()")
    if pre_star_rating:
        result['star_rating'] = pre_star_rating[0].split(' ')[0]  # 星级
    else:
        print("无评论")
        result={}
        return result
    result['reviews_num'] =int(Html.xpath("//span[@data-hook='total-review-count']/text()")[0].replace(',',''))   # 评论
    pre_good_reviews_percentage_5 = Html.xpath("//a[contains(@class,'5star hist')]/text()")
    pre_good_reviews_percentage_4 = Html.xpath("//a[contains(@class,'4star hist')]/text()")
    if pre_good_reviews_percentage_5:
        result['good_reviews_percentage_5']= int(Html.xpath("//a[contains(@class,'5star hist')]/text()")[0].split('%')[0]) # 好评率 5星
    else:
        result['good_reviews_percentage_5'] = 0
    if pre_good_reviews_percentage_4:
        result['good_reviews_percentage_4'] = int(Html.xpath("//a[contains(@class,'4star hist')]/text()")[0].split('%')[0]) # 好评率 4星
    else:
        result['good_reviews_percentage_4'] = 0



    find_category_rating=re.findall("#([\d|,]*) in", html) #类目排名
    if len(find_category_rating) >=2 : #取出多个排名，没问题
        find_category = Html.xpath(
            "//*[contains(text(),'See top')]/../../*/text()|//*[contains(text(),'See Top')]/../*/text()")
        if find_category:
            result['category_rating'] = int(re.findall("#([\d|,]*) in", html)[0].replace(',', ""))
            result['category'] = re.findall("in ([\w|\s|\&]*)", Html.xpath(
                "//*[contains(text(),'See top')]/../../*/text()|//*[contains(text(),'See Top')]/../*/text()")[0])[0]
            pre =Html.xpath("string(//th[contains(text(),'Best Seller')]/../td/*)")
            result['details']='\n'.join(re.sub('\n|\s','',pre).split('#')[2:])
        else:
            result['category_rating']=0
            result['category']=''
            pre =Html.xpath("string(//th[contains(text(),'Best Seller')]/../td/*)")
            result['details']='\n'.join(re.sub('\n|\s','',pre).split('#')[2:])
    elif len(find_category_rating) ==1:
        pre = Html.xpath("string(//th[contains(text(),'Best Seller')]/../td/*)")
        pre_details = re.sub('\n|\s','',pre).split('#')
        if len(pre_details) == 2:
           result['category_rating'] = 0
           result['category']=''
           result['details']= re.sub('\n|\s','',pre).split('#')[1]
        else:
            pre_one = Html.xpath("//li[@id='SalesRank']/text()")
            if pre_one:
                pre_one = "".join(pre_one)
                pre_one = re.sub('\n|\s','',pre_one).replace('#','').replace('()','').split('in')
                result['category_rating'] =int(pre_one[0].replace(',',''))
                result['category'] = pre_one[1]
                pre_details = Html.xpath("string(//ul[@class='zg_hrsr'])")
                result['details'] =re.sub("\n|\s",'',''.join(pre_details))
            else:
                pre_one = Html.xpath("string(//*[@id='SalesRank'])")
                pre_category = re.sub("\n|\s", '', pre_one).split('#')
                result['category_rating']=int(pre_category[1].split("in")[0].replace(',',''))
                result['category']=pre_category[1].split("in")[1].replace('(Seetop100)','')
                result['details'] = "".join(pre_category[2:])

    else:
        result['category_rating'] = 0
        result['category'] = ""
        result['details'] =""
    return result
#s = my_session()


conn = pymysql.connect(**mysql_config)
cursor = conn.cursor()
def fetch(tasks):
    task, results,s = tasks
    s.headers.update({'User-Agent':random.choice(USER_AGENTS)})
    print(task)
    url = "https://www.amazon.com/dp/" + task
    print(url)
    s.proxies.update({"http": get_proxy()})
    while 1:
        res = s.get(url)
        if res.status_code == 404:
            return
        elif res.status_code != 200:
            print(res.status_code)
            s.get("http://123.207.17.216:5000/delete")
            s = api_s
            print('IP ban,change IP')
            continue
        else:
            break
    html = res.content.decode('utf-8','ignore')
    result = deal_bussines(html)
    if result!={}:
        db(result, task)
    else:
        print("result = ",results)
        return
def db(result,asin):
    print(result)
    update_sql ="UPDATE mws_product_online_copy set category_rating = {},category='{}',reviews={},good_reviews_percentage='{}',star_rating={},details='{}' where asin1='{}'"
    cursor.execute(update_sql.format(result['category_rating'],result['category'],result['reviews_num'],result['good_reviews_percentage_4']+result['good_reviews_percentage_5'],result['star_rating'],result['details'],asin))
    conn.commit()
    print('update success')
if __name__ == '__main__':
    s = requests.Session()
    s.headers.update({"Accept-Encoding": "gzip"})
    s.headers.update({"Host": "www.amazon.com"})
    s.headers.update({"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"})
    s.headers.update({"Origin": "https://www.amazon.com"})
    s.headers.update({"X-Requested-With": "XMLHttpRequest"})
    s.headers.update({"Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"})
    s.headers.update({"Connection": "keep-alive"})
    cursor.execute("select distinct asin from amz_review_task")
    tasks = cursor.fetchall()
    conn.commit()
    results = []
    pool = ThreadPoolExecutor(max_workers=5)
    # for circle in len(tasks)//5
    tasks = [(x[0],results,s) for x in tasks]
    start = 0
    end = 5
    for num in range(len(tasks)//5+1):
        proxy = get_proxy()
        if proxy == "http://0":
            print("changing ip ")
            change_ip()
            proxy = get_proxy()
            print(proxy)
        pool.map(fetch,tasks[start:end])
        start+=5
        end +=5


