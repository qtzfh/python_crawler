import redis
from DBUtils.PersistentDB import PersistentDB
import pymysql
import log

hosts = '127.0.0.1'
cursor = None

PooL = PersistentDB(
    creator=pymysql,  # 使用链接数据库的模块
    maxusage=None,  # 一个链接最多被使用的次数，None表示无限制
    setsession=[],  # 开始会话前执行的命令
    ping=0,  # ping MySQL服务端,检查服务是否可用
    closeable=False,  # conn.close()实际上被忽略，供下次使用，直到线程关闭，自动关闭链接，而等于True时，conn.close()真的被关闭
    threadlocal=None,  # 本线程独享值的对象，用于保存链接对象
    host=hosts,
    port=3306,
    user='root',
    password='root123',
    database='zhihu_crawler',
    charset='utf8'
)

def commit(sql):
    try:
        conn = PooL.connection()
        db_cursor = conn.cursor()
        log.info(sql)
        db_cursor.execute(sql)
        db_cursor.close()
        conn.close()
        global cursor
        cursor = db_cursor
    except(EOFError):
        log.info(EOFError)


def redis_connect():
    pool = redis.ConnectionPool(host=hosts, port=6379)
    redis_conn = redis.Redis(connection_pool=pool)
    return redis_conn
