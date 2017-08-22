import pymysql
import redis
import log

db = pymysql.connect("127.0.0.1", "root", "root123", "zhihu_crawler", use_unicode=True, charset="utf8")
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
    pool = redis.ConnectionPool(host='127.0.0.1', port=6379)
    redis_conn = redis.Redis(connection_pool=pool)
    return redis_conn
