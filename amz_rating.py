import aiohttp
import asyncio
from aiohttp import web
import pymysql
import requests
from lxml import etree
from util import mysql_config,headers,get_proxy
sema = asyncio.Semaphore(2)
conn = pymysql.connect(**mysql_config)
cursor = conn.cursor()
def deal_bussines(html):
    tree = etree.HTML(html)
    result ={}
    # 类目排名
    result['category_rating'] = tree.Xpath('')
    # 类目
    result['category']=
    # 评论
    result['reviews'] =
    # 好评率
    result['good_reviews_percentage']=
    # 星级
    result['star_rating']=
    # 销售排行详情
    result['details']
async def fetch(url,deal_bussines=None):

    try:
        with (await sema):
            proxy = get_proxy()
            conn_tcp = aiohttp.TCPConnector(verify_ssl=False)
            async with aiohttp.ClientSession(connector=conn_tcp) as s:
                async with s.request(url=url, method="GET", headers=headers, proxy=proxy, timeout=20) as r:
                    r = await r.text()
    except Exception as exc:
        print(exc)
    else:
        loop = asyncio.get_event_loop()
        loop.run_in_executor(None,deal_bussines,r)
        print("入库 ok")
if __name__ == '__main__':
    cursor.execute("select distinct asin from amz_review_task")
    tasks = cursor.fetchall()
    conn.commit()
    #print(tasks)
    tasks = [x[0] for x in tasks]
    tasks = ["https://www.amazon.com/dp/" + x for x in tasks]
    proxy = get_proxy()
    event_loop = asyncio.get_event_loop()
    f = asyncio.wait([fetch(url=task) for task in tasks[0:1]])
    event_loop.run_until_complete(f)




