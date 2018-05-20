import zhihu_answer
import zhihu_question
import zhihu_question_info
from datetime import datetime
import time
import requests
import re
import http.cookiejar as cookielib
from PIL import Image
import server_connection
import proxy_ip
import log
import os
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
import pymysql
import certifi

redis_conn = None

if (redis_conn == None):
    redis_conn = server_connection.redis_connect()


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.63 Safari/537.36',
}

phone = "1886xxxxxxxx"
password = "xxxxxx"

session = requests.session()
session.cookies = cookielib.LWPCookieJar(filename='cookies')
try:
    session.cookies.load(ignore_discard=True)
except:
    log.info("Cookie 未能加载")

question_cursor = None


# 封装requests 请求
def request_info(url):
    time.sleep(3)
    try:
        resp = session.get(url, headers=headers, timeout=60,verify=certifi.where())
    except:
        request_info(url)
    return resp


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
    postData = {
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


# 获取所有数据
def get_all_question_list():
    sql = "select id from zhihu_question"
    server_connection.commit(sql)
    global question_cursor
    question_cursor = server_connection.cursor


def get_today_question_list():
    sql = "SELECT * FROM `zhihu_question` where DATE_FORMAT(update_time,'%Y-%m-%d') = CURDATE();"
    server_connection.commit(sql)
    global question_cursor
    question_cursor = server_connection.cursor


# 获取question的execute_type=1的值
def get_question_list_type(type, offset, limit):
    sql = "select id from zhihu_question where is_delete=1 and execute_type=%s limit %s,%s" % (type,
                                                                                               offset, limit)
    server_connection.commit(sql)
    global question_cursor
    question_cursor = server_connection.cursor


# 每天初始化question的执行状态
def init_question_type_everyDay():
    sql = "update zhihu_question set execute_type =1,update_time = NOW() "
    server_connection.commit(sql)


# 将今天的question_id存入redis
def set_question_id():
    get_today_question_list()
    for data in question_cursor.fetchall():
        redis_conn.sadd("question_id", data[0])
    log.info("set question id success")

def init_server_connection():
    server_connection.db = pymysql.connect(server_connection.hosts, "root", "root123", "zhihu_crawler", use_unicode=True, charset="utf8")
    server_connection.cursor = server_connection.db.cursor()
# 每日3.15 运行task获取数据
def task_all_work():
    print(datetime.now())
    init_server_connection()
    init_question_type_everyDay()
    # 获取question_list并且insert
    zhihu_question.insert_question()
    # 获取今天所有的question_id并set到redis用于处理answer
    #set_question_id()
    # 获取question_info 详细信息
    zhihu_question_info.insert_question_info()
    # 获取question_info下的回答内容
    # 回答内容单独处理
    # zhihu_answer.insert_answer_info()
def tick():
    sql = "select id from zhihu_question limit 0,1"
    server_connection.commit(sql)

if __name__ == '__main__':
    if is_login():
        #task_all_work()
        scheduler = BlockingScheduler()
        scheduler.add_job(task_all_work, 'interval', minutes=1440)
        scheduler2 = BackgroundScheduler()
        scheduler2.add_job(tick, 'interval', seconds=30)
        try:
            # scheduler2.start()
            scheduler.start()  # 采用的是阻塞的方式，只有一个线程专职做调度的任务
        except (KeyboardInterrupt, SystemExit):
            # Not strictly necessary if daemonic mode is enabled but should be done if possible
            scheduler.shutdown()
            print('Exit The Job!')
    else:
        login()
