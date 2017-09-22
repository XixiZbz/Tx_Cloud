
import hashlib
import time
import requests
import paramiko

my_app_key = "93137265"
app_secret = "225d0a2e1fc62ed275f487fc9c823693"
mayi_url = 's2.proxy.mayidaili.com'
mayi_port = '8123'
mysql_config = {
    "host":"59ae085c00753.gz.cdb.myqcloud.com",
    "user":"root",
    "password":"%yms%2017",
    "db":"yms_erp_dev",
    #"db":"yms_test",
    "charset":"utf8mb4",
    "port":5902,
}
USER_AGENTS = [
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
    "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
    "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/2.0 Safari/536.11",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; LBBROWSER)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E; LBBROWSER)",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 LBBROWSER",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; QQBrowser/7.0.3698.400)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; 360SE)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",
    "Mozilla/5.0 (iPad; U; CPU OS 4_2_1 like Mac OS X; zh-cn) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8C148 Safari/6533.18.5",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b13pre) Gecko/20110307 Firefox/4.0b13pre",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:16.0) Gecko/20100101 Firefox/16.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
    "Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10"
]


#找群主购买 my_app_key, myappsecret, 以及蚂蚁代理服务器的 mayi_url 地址和 mayi_port 端口
my_app_key = "93137265"
app_secret = "225d0a2e1fc62ed275f487fc9c823693"
mayi_url = 's2.proxy.mayidaili.com'
mayi_port = '8123'
def my_session():
    # 找群主购买 my_app_key, myappsecret, 以及蚂蚁代理服务器的 mayi_url 地址和 mayi_port 端口
    my_app_key = "93137265"
    app_secret = "225d0a2e1fc62ed275f487fc9c823693"
    mayi_url = 's2.proxy.mayidaili.com'
    mayi_port = '8123'

    # 蚂蚁代理服务器地址
    mayi_proxy = {'http': 'http://{}:{}'.format(mayi_url, mayi_port)}

    # 准备去爬的 URL 链接
    url = 'http://1212.ip138.com/ic.asp'

    # 计算签名
    timesp = '{}'.format(time.strftime("%Y-%m-%d %H:%M:%S"))
    codes = app_secret + 'app_key' + my_app_key + 'timestamp' + timesp + app_secret
    sign = hashlib.md5(codes.encode('utf-8')).hexdigest().upper()

    # 拼接一个用来获得蚂蚁代理服务器的「准入」的 header (Python 的 concatenate '+' 比 join 效率高)
    authHeader = 'MYH-AUTH-MD5 sign=' + sign + '&app_key=' + my_app_key + '&timestamp=' + timesp

    # 用 Python 的 Requests 模块。先订立 Session()，再更新 headers 和 proxies
    s = requests.Session()
    s.headers.update({"Host": "www.amazon.com"})
    s.headers.update({
                         "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36"})
    s.headers.update({"Connection": "keep-alive"})
    s.headers.update({
                         "Referer": "https://www.amazon.com/AmazonBasics-Velvet-Hangers-50-Pack-Black/product-reviews/B01BH83OOM/ref=cm_cr_getr_d_paging_btm_1?ie=UTF8&reviewerType=all_reviews&pageNumber=1&sortBy=recent"})
    s.headers.update(
        {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"})
    s.headers.update({"Accept-Encoding": ""})
    s.headers.update({"Origin": "https://www.amazon.com"})
    s.headers.update({"X-Requested-With": "XMLHttpRequest"})
    s.headers.update({"Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"})
    s.headers.update({'Proxy-Authorization': authHeader})
    s.proxies.update(mayi_proxy)
    return s


class proxy_session:
    # 找群主购买 my_app_key, myappsecret, 以及蚂蚁代理服务器的 mayi_url 地址和 mayi_port 端口
    my_app_key = "93137265"
    app_secret = "225d0a2e1fc62ed275f487fc9c823693"
    mayi_url = 's2.proxy.mayidaili.com'
    mayi_port = '8123'

    # 蚂蚁代理服务器地址
    mayi_proxy = {'http': 'http://{}:{}'.format(mayi_url, mayi_port)}

    # 准备去爬的 URL 链接
    url = 'http://1212.ip138.com/ic.asp'

    # 计算签名
    timesp = '{}'.format(time.strftime("%Y-%m-%d %H:%M:%S"))
    codes = app_secret + 'app_key' + my_app_key + 'timestamp' + timesp + app_secret
    sign = hashlib.md5(codes.encode('utf-8')).hexdigest().upper()

    # 拼接一个用来获得蚂蚁代理服务器的「准入」的 header (Python 的 concatenate '+' 比 join 效率高)
    authHeader = 'MYH-AUTH-MD5 sign=' + sign + '&app_key=' + my_app_key + '&timestamp=' + timesp
    headers = {
        "Host": "www.amazon.com",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "*",
        "Origin": "https://www.amazon.com",
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "Connection": "keep-alive",
        'Proxy-Authorization': authHeader,
        # "Referer":"https://www.amazon.com/AmazonBasics-Velvet-Hangers-50-Pack-Black/product-reviews/B01BH83OOM/ref=cm_cr_getr_d_paging_btm_1?ie=UTF8&reviewerType=all_reviews&pageNumber=1&sortBy=recent",
    }
def get_proxy():
    proxies = requests.get('http://123.207.17.216:5000', auth=('admin', 'qgy')).text
    proxy = 'http://{}'.format(proxies)
    return proxy
headers = {
    "Host": "www.amazon.com",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding": "gzip",
    "Origin": "https://www.amazon.com",
    "X-Requested-With": "XMLHttpRequest",
    "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
    "Connection": "keep-alive"}



def get_ssh(ip,username,passwd):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, 20038, username, passwd, timeout=5)
    return ssh

def exec_commands(conn,cmd):
    conn.exec_command(cmd[0])
    time.sleep(0.5)
    conn.exec_command(cmd[1])
    time.sleep(3)
    a,b,c=conn.exec_command(cmd[2])
    results=b.read()
    return results
def change_ip():
    cmd = ['pppoe-stop','pppoe-start','curl http://123.207.17.216:5000/record/qgy']#你要执行的命令列表
    ssh =get_ssh('222.89.190.13','root','nowornever1')
    result = exec_commands(ssh,cmd)
    ssh.close()
    return result
if __name__ == '__main__':
    pass

