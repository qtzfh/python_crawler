import pymysql

db = pymysql.connect("127.0.0.1", "root", "root", "zhihu_crawler", use_unicode=True, charset="utf8")
cursor = db.cursor()


def commit(sql):
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        db.commit()
        return cursor
    except(EOFError):
        print(EOFError)
        # 如果发生错误则回滚
        db.rollback()
