import pymysql
import redis
import log
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'

hosts = "127.0.0.1"

db = pymysql.connect(hosts, "root", "root123", "zhihu_crawler", use_unicode=True, charset="utf8")
cursor = db.cursor()


def commit(sql):
    try:
        # 执行sql语句
        log.info(sql)
        cursor.execute(sql)
        # 提交到数据库执行
        db.commit()
        return cursor
    except(EOFError):
        log.info(EOFError)
        # 如果发生错误则回滚
        db.rollback()


def redis_connect():
    redis_conn = redis.Redis(host=hosts, port=6379, password="")
    return redis_conn
