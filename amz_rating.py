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
cursor.execute("select distinct asin from amz_review_task")
tasks = cursor.fetchall()
conn.commit()
tasks = [x[0] for x in tasks]
tasks = ["https://www.amazon.com/dp/"+x for x in tasks]


proxy = get_proxy()

def deal_bussines(html):
    tree = etree.HTML(html)


async def fetch(url,deal_bussines=None):
    try:
        with (await sema):
            conn_tcp = aiohttp.TCPConnector(verify_ssl=False)
            async with aiohttp.ClientSession(connector=conn_tcp) as s:
                async with s.request(url=url, method="GET", headers=headers, proxy=proxy, timeout=20) as r:
                    r = await r.text()
    # except web.HTTPNotFound:
    #     print(web.HTTPNotFound)
    except Exception as exc:
        print(exc)
    else:
        loop = asyncio.get_event_loop()
        loop.run_in_executor(None,deal_bussines,r)
        print("入库 ok")
event_loop = asyncio.get_event_loop()
f = asyncio.wait([fetch(url=task) for task in tasks])
event_loop.run_until_complete(f)




