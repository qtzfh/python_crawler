import server_connection
import datetime
import zhihu_main


def getYesterday():
    today = datetime.date.today()
    oneday = datetime.timedelta(days=1)
    yesterday = today - oneday
    return yesterday


# 输出
# 获取昨天的task_id
def get_zhihu_question_info():
    select_sql = "select question_id from zhihu_question_info where read_num<50000 AND follow_num <1000 and " \
                 "answer_num<100 and task_day='%s' and is_delete=1"%(getYesterday())
    server_connection.commit(select_sql)
    question_cursor = server_connection.cursor
    row_count = question_cursor.rowcount
    if row_count > 0:
        delete_question_sql = 'update zhihu_question set is_delete = 0 where id in ('
        delete_question_info_sql = 'update zhihu_question_info set is_delete = 0 where question_id in ('
        for question_id in question_cursor.fetchall():
            delete_question_sql += str(question_id[0]) + ","
            delete_question_info_sql += str(question_id[0]) + ","
        delete_question_sql = delete_question_sql[:-1]
        delete_question_info_sql = delete_question_info_sql[:-1]
        delete_question_sql += ')'
        delete_question_info_sql += ')'
        server_connection.commit(delete_question_sql)
        server_connection.commit(delete_question_info_sql)


if __name__ == '__main__':
    get_zhihu_question_info()
