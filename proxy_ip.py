# coding:utf-8
import random
import urllib.request
from lxml import etree
import time
import server_connection

redis_conn = None

if (redis_conn == None):
    redis_conn = server_connection.redis_connect()

ip_all_list = []


def get_url(url):  # 国内高匿代理的链接
    url_list = []
    for i in range(1, 2):
        url_new = url + str(i)
        url_list.append(url_new)
    return url_list


def get_content(url):  # 获取网页内容
    user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.22 Safari/537.36 SE 2.X MetaSr 1.0'
    headers = {'User-Agent': user_agent}
    req = urllib.request.Request(url=url, headers=headers)
    res = urllib.request.urlopen(req)
    content = res.read()
    return content.decode('utf-8')


def get_info(content):  # 提取网页信息 / ip 端口
    datas_ip = etree.HTML(content).xpath('//table[contains(@id,"ip_list")]/tr/td[2]/text()')
    datas_port = etree.HTML(content).xpath('//table[contains(@id,"ip_list")]/tr/td[3]/text()')
    for i in range(0, len(datas_ip)):
        out = "%s:%s" % (datas_ip[i], datas_port[i])
        ip_all_list.append(out)


def verif_ip(hosts):  # 验证ip有效性
    user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.22 Safari/537.36 SE 2.X MetaSr 1.0'
    headers = {'User-Agent': user_agent}
    proxy = {'https': 'https://%s' % (hosts)}
    print(proxy)

    proxy_handler = urllib.request.ProxyHandler(proxy)
    opener = urllib.request.build_opener(proxy_handler)
    urllib.request.install_opener(opener)

    test_url = "https://www.zhihu.com/"
    req = urllib.request.Request(url=test_url, headers=headers)
    try:
        res = urllib.request.urlopen(req)
        content = res.read()
        if content:
            print('that is ok')
            redis_conn.sadd("ip", hosts)
    except urllib.request.URLError as e:
        print(e.reason)

# 获取西刺代理
def get_xici_proxy():
    url = 'http://www.xicidaili.com/nn/'
    url_list = get_url(url)
    for i in url_list:
        print(i)
        content = get_content(i)
        get_info(content)
    for data in ip_all_list:
        verif_ip(data)

if __name__ == '__main__':
    get_xici_proxy()
