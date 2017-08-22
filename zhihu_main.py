import zhihu_answer
import zhihu_question
import zhihu_question_info
import datetime
import time
import requests
import re
import http.cookiejar as cookielib
from PIL import Image
import server_connection
import proxy_ip
import log

redis_conn = None

if (redis_conn == None):
    redis_conn = server_connection.redis_connect()


def get_proxy_ip():
    ip = redis_conn.srandmember("ip")
    if (ip == None):
        proxy_ip.__name__
        time.sleep(60)
        ip = redis_conn.srandmember("ip")
    return ip


headers = {
    'Connection': 'Keep-Alive',
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.63 Safari/537.36',
    'Accept-Encoding': 'gzip, deflate,br',
    'Host': 'www.zhihu.com',
    'DNT': '1'
}

phone = "1886xxxxxxx"
password = "xxxxxx"

session = requests.session()
session.cookies = cookielib.LWPCookieJar(filename='cookies')
try:
    session.cookies.load(ignore_discard=True)
except:
    log.info("Cookie 未能加载")

# 封装requests 请求
def request_info(url):
    time.sleep(5)
    # proxy, host = proxies()
    try:
        # resp = session.get(url, headers=headers, proxies=proxy, timeout=60)
        resp = session.get(url, headers=headers, timeout=60)
        # log.info("success:%s" % (host))
    except:
        # log.info("error:%s" % (host))
        # redis_conn.srem("ip", host)
        request_info(url)
    return resp

# 获取代理ip
def proxies():
    host = get_proxy_ip()
    proxies = {
        "https": "%s" % (host),
    }
    log.info(proxies)
    return proxies, host

# 获取xsrf
def get_xsrf(data):
    patten = 'name=\"_xsrf\" value=\"(.*)\"'
    _xsrf = re.findall(patten, data)
    return _xsrf[0]


# 获取验证码
def get_captcha():
    t = str(int(time.time() * 1000))
    captcha_url = 'https://www.zhihu.com/captcha.gif?r=' + t + "&type=login"
    r = request_info(captcha_url)
    with open('captcha.jpg', 'wb') as f:
        f.write(r.content)
        f.close()
    # 用pillow 的 Image 显示验证码
    # 如果没有安装 pillow 到源代码所在的目录去找到验证码然后手动输入
    try:
        im = Image.open('captcha.jpg')
        im.show()
        im.close()
    except:
        log.info(u'请到 %s 目录找到captcha.jpg 手动输入' % os.path.abspath('captcha.jpg'))
    captcha = input("please input the captcha\n>")
    return captcha

def is_login():
    # 通过查看用户个人信息来判断是否已经登录
    url = "https://www.zhihu.com/settings/profile"
    login_code = request_info(url).status_code
    if login_code == 200:
        return True
    else:
        return False

def login():
    resp = request_info("https://www.zhihu.com")
    _xsrf = get_xsrf(resp.text)
    postData = {
        "_xsrf": _xsrf,
        "password": password,
        "phone_num": phone
    }
    response = requests.post("https://www.zhihu.com/login/phone_num", postData, headers=headers)
    # 说明需要验证码才能登陆
    if response.json()['r'] == 1:
        postData["captcha"] = get_captcha()
        response = session.post("https://www.zhihu.com/login/phone_num", data=postData, headers=headers)
        log.info(response.json()['msg'])
    # 保存session到文件中
    session.cookies.save()



# 获取未被爬取的数据
def get_not_today_question_list(offset, limit):
    sql = "select id from zhihu_question where (task_day!=CURDATE() or task_day IS NULL ) and is_delete=1 limit %s,%s" % (
        offset, limit)
    cursor = server_connection.commit(sql)
    global question_cursor
    question_cursor = cursor


# 获取所有数据
def get_all_question_list(offset, limit):
    sql = "select id from zhihu_question where is_delete=1 limit %s,%s" % (
        offset, limit)
    cursor = server_connection.commit(sql)
    global question_cursor
    question_cursor = cursor


# 每日3.15 运行task获取数据
def task_all_work():
    now = datetime.datetime.now()
    sched_time = datetime.datetime(now.year, now.month, now.day, 3, 15, 0)
    tomorrow = sched_time + datetime.timedelta(days=1)
    while True:
        now = datetime.datetime.now()
        if sched_time < now < (sched_time + datetime.timedelta(minutes=2)):
            sched_time = datetime.datetime(tomorrow.year, tomorrow.month, tomorrow.day, 3, 15, 0)
            tomorrow = tomorrow + datetime.timedelta(days=1)
            # 获取question_list并且insert
            zhihu_question.insert_question()
            # 获取question_info 详细信息
            zhihu_question_info.insert_question_info()
            # 获取question_info下的回答内容
            zhihu_answer.insert_answer_info()
            # 运行完之后sleep 5min 保证不会再进入本次循环
            time.sleep(300)
        time.sleep(60)


if __name__ == '__main__':
    if is_login():
        task_all_work()
    else:
        login()
