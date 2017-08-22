# coding:utf-8
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


def get_content(url, type):  # 获取网页内容
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


def verif_ip(hosts):  # 验证ip有效性
    user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.22 Safari/537.36 SE 2.X MetaSr 1.0'
    headers = {'User-Agent': user_agent}
    proxy = {'https': 'https://%s' % (hosts)}
    log.info(proxy)
    test_url = "https://www.zhihu.com/"
    try:
        request_code = requests(url=test_url, headers=headers, proxies=proxy, timeout=30).status_code
        if request_code == 200:
            log.info('that is ok')
            redis_conn.sadd("ip", hosts)
    except urllib.request.URLError as e:
        log.info(e.reason)


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


if __name__ == '__main__':
    try:
        get_xici_proxy()
    except:
        log.info("西刺代理error")
    try:
        get_kuai_proxy()
    except:
        log.info("快代理error")
    try:
        get_proxyipcenter_proxy()
    except:
        log.info("知乎代理error")
