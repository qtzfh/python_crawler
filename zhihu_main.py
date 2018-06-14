from datetime import datetime
import certifi
import pymysql
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
import time
import log
import server_connection
import zhihu_question
import zhihu_question_info

redis_conn = None

if (redis_conn == None):
    redis_conn = server_connection.redis_connect()

def cookies():
    sql = "select cookies from cookies  where type = 'zhihu' limit 0,1"
    server_connection.commit(sql)
    global question_cursor
    question_cursor = server_connection.cursor
    cookies = ""
    for data in question_cursor.fetchall():
        cookies =  data[0]
    return cookies

headers = {
    'cookie':cookies(),
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.63 Safari/537.36',
}

question_cursor = None


# 封装requests 请求
def request_info(url):
    time.sleep(3)
    session = requests.Session()
    resp = session.get(url, headers=headers, timeout=60, verify=certifi.where())
    return resp


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

# 获取大于question_id的值
def get_question_list_type(question_id,offset, limit):
    sql = "select id from zhihu_question where is_delete=1 and id >%s limit %s,%s"%(question_id,offset, limit)
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
    server_connection.db = pymysql.connect(server_connection.hosts, "root", "root123", "zhihu_crawler",
                                           use_unicode=True, charset="utf8")
    server_connection.cursor = server_connection.db.cursor()


# 每日3.15 运行task获取数据
def task_all_work():
    print(datetime.now())
    init_server_connection()
    init_question_type_everyDay()
    # 获取question_list并且insert
    zhihu_question.insert_question()
    # 获取今天所有的question_id并set到redis用于处理answer
    # set_question_id()
    # 获取question_info 详细信息
    zhihu_question_info.insert_question_info()
    # 获取question_info下的回答内容
    # 回答内容单独处理
    # zhihu_answer.insert_answer_info()


def tick():
    # 保持数据库连接
    sql = "select id from zhihu_question limit 0,1 where id = 0"
    server_connection.commit(sql)


def test():
    print("this is test")


if __name__ == '__main__':
    scheduler = BlockingScheduler()
    scheduler.add_job(task_all_work, 'cron', day_of_week='0-6', hour=00, minute=1, second=00)
    scheduler2 = BackgroundScheduler()
    scheduler2.add_job(tick, 'interval', seconds=30)
    try:
        # scheduler2.start()
        scheduler.start()  # 采用的是阻塞的方式，只有一个线程专职做调度的任务
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        scheduler.shutdown()
        print('Exit The Job!')
