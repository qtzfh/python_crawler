# -*- coding:utf-8 -*-
import random
import urllib.request
from lxml import etree
import time
import server_connection
import log
import requests
from bs4 import BeautifulSoup

redis_conn = None

if (redis_conn == None):
    redis_conn = server_connection.redis_connect()

ip_all_list = []


def get_url(url, type):  # 国内高匿代理的链接
    if (type == 1 or type == 2):
        url_list = []
        for i in range(1, 5):
            url_new = url + str(i)
            url_list.append(url_new)
        return url_list
    elif (type == 3):
        url_list = []
        for i in range(1, 5):
            url_new = url + "%s.html" % (i)
            url_list.append(url_new)
        return url_list


def get_content(url, type):  # 获取网页内容
    print("url:%s" % (url))
    user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.22 Safari/537.36 SE 2.X MetaSr 1.0'
    headers = {'User-Agent': user_agent}
    if (type == 1):
        req = urllib.request.Request(url=url, headers=headers)
        res = urllib.request.urlopen(req)
        content = res.read()
        return content.decode('utf-8')
    elif (type == 2):
        res = requests.get(url=url, headers=headers)
        return res.text
    elif (type == 3):
        res = requests.get(url=url, headers=headers)
        return res.json()
    elif (type == 4):
        res = requests.get(url=url, headers=headers)
        res.encoding = 'gb2312'
        return res.text


def get_info(content, type):  # 提取网页信息 / ip 端口
    if (type == 1):
        datas_ip = etree.HTML(content).xpath('//table[contains(@id,"ip_list")]/tr/td[2]/text()')
        datas_port = etree.HTML(content).xpath('//table[contains(@id,"ip_list")]/tr/td[3]/text()')
        for i in range(0, len(datas_ip)):
            out = "%s:%s" % (datas_ip[i], datas_port[i])
            ip_all_list.append(out)
    elif (type == 2):
        soup = BeautifulSoup(content)
        for link in soup.find_all("tbody"):
            for tr in link.find_all("tr"):
                datas_ip = tr.find_all("td")[0].text
                datas_port = tr.find_all("td")[1].text
                out = "%s:%s" % (datas_ip, datas_port)
                ip_all_list.append(out)
    elif (type == 3):
        soup = BeautifulSoup(content)
        tbody = soup.find_all("table")[2]
        for tr in tbody.find_all("tr"):
            if (tr.find_all("td")[0].text != "ip"):
                datas_ip = tr.find_all("td")[0].text
                datas_port = tr.find_all("td")[1].text
                out = "%s:%s" % (datas_ip, datas_port)
                ip_all_list.append(out)


def verif_ip(hosts):  # 验证ip有效性
    user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.22 Safari/537.36 SE 2.X MetaSr 1.0'
    headers = {'User-Agent': user_agent}
    proxy = {'https': 'https://%s' % (hosts)}
    log.info(proxy)
    print(proxy)
    test_url = "https://www.zhihu.com/explore"
    try:
        response = requests.get(url=test_url, headers=headers, proxies=proxy, timeout=30)
        request_code = response.status_code
        if request_code == 200:
            log.info('that is ok')
            redis_conn.sadd("ip", hosts)
    except:
        log.info("this is error")


# 获取西刺代理
def get_xici_proxy():
    type = 1
    url = 'http://www.xicidaili.com/nn/'
    url_list = get_url(url, type)
    for i in url_list:
        log.info(i)
        content = get_content(i, type)
        get_info(content, type)
    for data in ip_all_list:
        verif_ip(data)


# 获取快代理
def get_kuai_proxy():
    global ip_all_list
    ip_all_list = []
    type = 2
    url = 'http://www.kuaidaili.com/free/inha/'
    url_list = get_url(url, type)
    for i in url_list:
        log.info(i)
        content = get_content(i, type)
        get_info(content, type)
    for data in ip_all_list:
        verif_ip(data)


# 获取知乎https://zhuanlan.zhihu.com/p/25313283?refer=codelover 代理ip列表
def get_proxyipcenter_proxy():
    global ip_all_list
    ip_all_list = []
    num = 200
    resp = get_content(
        "http://115.159.40.202:8080/proxyipcenter/av?usedSign=&checkUrl=http://free-proxy-list.net/&domain=free-proxy-list.net&num=%s" % (
            num), 3)
    for data in resp['data']['data']:
        out = "%s:%s" % (data['proxyIp'], data['port'])
        ip_all_list.append(out)
    for data in ip_all_list:
        verif_ip(data)


# 66免费代理网站
def get_66_proxy():
    type = 3
    global ip_all_list
    ip_all_list = []
    for i in range(1, 10):
        print("1111")
        url = "http://www.66ip.cn/areaindex_%s/" % (i)
        url_list = get_url(url, type)
        for i in url_list:
            log.info(i)
            content = get_content(i, 4)
            get_info(content, type)
        for data in ip_all_list:
            verif_ip(data)
        time.sleep(15)

# 虫代理
def get_bugng_proxy():
    global ip_all_list
    ip_all_list = []
    url = "http://www.bugng.com/api/getproxy/json?num=80&anonymity=1&type=2"
    resp = get_content(url, 3)
    for data in resp['data']['proxy_list']:
        ip_all_list.append(data)
    for data in ip_all_list:
        verif_ip(data)

if __name__ == '__main__':
    # get_bugng_proxy()
    get_proxyipcenter_proxy()
    # get_xici_proxy()
    # get_66_proxy()
    # get_kuai_proxy()
