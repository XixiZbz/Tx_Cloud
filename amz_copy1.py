#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import hashlib
import json
import pymysql
import time
from DBUtils.PooledDB import PooledDB
from bs4 import BeautifulSoup
from multiprocessing.dummy import Pool
from util import my_session, USER_AGENTS, mysql_config, headers
import random
from collections import ChainMap
pool = PooledDB(pymysql,mincached =100,blocking=True,maxconnections=102,maxshared=100,**mysql_config)
conn = pool.connection()
cursor = conn.cursor()
s = my_session()
def update_table():
    now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    cursor.execute("select DISTINCT sid,asin1 from product_mws where status = 1")
    conn.commit()
    results = cursor.fetchall()
    for sid, asin in results:
        try:
            cursor.execute(
                "insert into amz_review_task(sid,asin,update_time,creat_time,update_localtime,creat_localtim) values('{}','{}',{},{},'{}','{}')".format(
                    sid, asin, "0", int(time.time()), "0", now))
        except Exception as e :
            print(e)
    conn.commit()
def update_time(sid,asin):
    now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    cursor.execute("UPDATE amz_review_task set update_time = '{}',update_localtime='{}' where sid='{}' and asin='{}'".format(int(time.time()),now,sid,asin))
    conn.commit()
    print("更新数据成功")
def md5(data):
    data = bytes(data,encoding = "utf8")
    m2 = hashlib.md5()
    m2.update(data)
    return m2.hexdigest()
#deley 为设置与上次爬取的时间间隔，单位为小时
def get_asin_sid(delay=0):
    cursor.execute("select asin,sid from amz_review_task where update_time = 0 or {} -update_time >{}".format(int(time.time()),delay*60*60))
    results = cursor.fetchall()
    conn.commit()
    return results
def trans_format(time_string, from_format, to_format='%Y.%m.%d %H:%M:%S'):
    time_struct = time.strptime(time_string, from_format)
    times = time.strftime(to_format, time_struct)
    return times

def my_get(url,proxies=None):
    s.headers.update({"User-Agent":random.choice(USER_AGENTS)})
    while 1:
        try:
            print(url)
            res = s.get(url,timeout=5)#,headers = headers,proxies=proxies,timeout=2)
            if "Robot Check" in res.text:
                print('robot check')
                continue
            break
            # res = requests.get(url,headers=headers)
        except Exception as e:
            print(e)
    return res

def my_post(url,data,proxies=None):
    s.headers.update({"User-Agent": random.choice(USER_AGENTS)})
    while 1:
        try:
            res = s.post(url,data=data,timeout=5)#proxies = proxies,headers=headers)
            if "Robot Check" in res.text:
                print('robot check ')
                continue
            else:
                break
        except:
            pass
    return res
#获取当前页数评论
def get_xhr(page_num,asin):#,proxies,header):
    request_data = "sortBy=recent&reviewerType=all_reviews&formatType=current_format&filterByStar=&pageNumber={}&filterByKeyword=&shouldAppend=undefined&deviceType=desktop&reftag=cm_cr_arp_d_paging_btm_2&pageSize=50&asin={}&scope=reviewsAjax0".format(page_num,asin)
    XHR_res = my_post(url='https://www.amazon.com/ss/customer-reviews/ajax/reviews/get/ref=cm_cr_getr_d_paging_btm_next_5', data=request_data)#,proxies= proxies,headers=header)

    return XHR_res

#解析出总评论数
def rev_num(html):
    soup = BeautifulSoup(html, "html.parser")
    review_num = soup.findAll("span", attrs={'data-hook': "total-review-count"})[0].text
    print(review_num)
    if ',' in review_num:
        review_num = int(review_num.replace(',','')) if review_num else 0
    else:
        return int(review_num)
    return review_num


#解析函数
def parse(ever_page_html):
    soup_result = {}
    soup = BeautifulSoup(ever_page_html, "html.parser")
    soup_result["last_star"] = soup.findAll("span", attrs={'class': "a-icon-alt"})[0].text[0]
    soup_result["author"] = soup.findAll("a", attrs={'data-hook': "review-author"})[0].text
    soup_result["author_id"] = soup.findAll("a", attrs={'data-hook': "review-author"})[0].get("href").split("/")[-2]
    soup_result["last_title"] = soup.findAll("a", attrs={'data-hook': "review-title"})[0].text
    review_date = soup.findAll("span", attrs={'data-hook': "review-date"})[0].text[3:]
    soup_result["review_date"] = trans_format(review_date, '%B %d, %Y', '%Y-%m-%d')
    soup_result["review_id"] = soup.findAll("div", attrs={'data-hook': "review"})[0].get("id")
    soup_result["last_content"] = soup.findAll("span", attrs={'data-hook': "review-body"})[0].text
    is_vp = soup.findAll("span", attrs={'data-hook': "avp-badge"})
    soup_result["is_vp"] = 1 if is_vp else 0
    current_format = soup.findAll("a", attrs={'data-hook': "format-strip"})
    soup_result["current_format"] = current_format[0].text if current_format else ''
    return soup_result


#评论入库
def my_db(data):
    #cursor = conn.cursor()
    sql = 'INSERT INTO amz_review (sid, asin, review_id, last_star, last_title,last_content,review_md5,author_id,author,review_date,is_vp,status,update_time,create_time,crawl_date,current_format) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
    sql_item = 'INSERT INTO amz_review_item (rid,star,title,content,review_date,create_time,md5) VALUES (%s, %s, %s, %s, %s, %s, %s)'
    try:
        cursor.execute(sql, data)
        cursor.execute("select max(id) from amz_review")
        auto_id = cursor.fetchall()
        item_data =[auto_id[0][0],data[3],data[4],data[5],data[9],int(time.time()),data[6]]
        cursor.execute(sql_item, item_data)
        conn.commit()
    except Exception as e :
        print(e)
        #print("错误数据：",data)
    #cursor.close()

#迭代入库
def deal_data(html,asin,sid):
    now =time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    html_list = html.split("&&&")
    for x in html_list[3:-3]:
        ever_page_html = json.loads(x)[2:]
        soup_result = parse(ever_page_html=ever_page_html[0])
        data = [sid, asin, soup_result["review_id"], soup_result["last_star"], soup_result["last_title"],
                soup_result["last_content"], md5(soup_result["last_star"]+soup_result["last_title"] + soup_result["last_content"]),
                soup_result["author_id"], soup_result["author"], soup_result["review_date"], soup_result["is_vp"], 0,
                int(time.time()), int(time.time()), now,soup_result["current_format"]]
        my_db(data)
def main_handler(each_rev,asin,sid,response_list):
    print("当前页：", each_rev,"  ",asin)
    res = get_xhr(each_rev, asin)
    if len(res.text) < 10000:
        return False
    response_list.append(res)
    print("完成页：",each_rev,"  ",asin)
    return True
# 多进程 处理
def main(asin,sid):
    print(asin ,sid)
    response_list = []
    num = 1
    print(num)
    while 1:
        post_status = main_handler(num,asin,sid,response_list)
        if post_status:
            pass
        else:
            break
        num += 1
    for respon in response_list:
        deal_data(respon.text,asin,sid)
    update_time(sid, asin)
    cursor.execute('select review_id,review_md5 from amz_review where asin = "{}"'.format(asin))
    tasks = cursor.fetchall()
    conn.commit()
    if response_list != None:
        classify(response_list,tasks)
    else:
        return
def get_soup(html):
    soup_dict = {}
    html_list = html.split("&&&")
    for x in html_list[3:-3]:
        ever_page_html = json.loads(x)[2:]
        soup_result = parse(ever_page_html=ever_page_html[0])
        soup_dict[soup_result["review_id"]]= (md5(soup_result["last_star"] + soup_result["last_title"] + soup_result["last_content"]),
                                              soup_result["last_star"],soup_result["last_title"], soup_result["last_content"])

    return soup_dict
def renew(star, title, content, review_id, md5):
    now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    cursor.execute("update amz_review set last_star='{}',last_title='{}',last_content='{}',review_md5='{}',update_time='{}',crawl_date='{}' where review_id='{}'".format(star,pymysql.escape_string(title),pymysql.escape_string(content),md5,int(time.time()),now,review_id))
    conn.commit()
def classify(response_list,tasks):
    new=ChainMap()
    for respon in response_list:
        soup_dict = get_soup(respon.text)
        new = new.new_child(soup_dict)
    base = ChainMap()
    for review_id, md5 in tasks:
        base = base.new_child({review_id: md5})
    for b in base.keys():
        if base.get(b) == new.get(b)[0]:
            pass
        else:
            renew(new.get(b)[1],new.get(b)[2],new.get(b)[3],b,new.get(b)[0])
if __name__ == '__main__':
    pool = Pool(5)
    while 1:
        #update_table()#更新一下数据库
        asins_sids = get_asin_sid(delay=4)
        pool.starmap(main,asins_sids)
        time.sleep(60*60*4)

    # asins_sids = get_asin_sid(delay=0)
    # asin,sid = asins_sids[0]
    # main(asin, sid)
    #time.sleep(60*60*4)