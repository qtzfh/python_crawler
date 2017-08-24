import zhihu_main
import server_connection
import log
from bs4 import BeautifulSoup


# 根据href获取每个href的详情
def get_href_detail(question_id):
    log.info("get_href_detail:" + question_id)
    resp = zhihu_main.request_info("https://www.zhihu.com/question/%s" % (question_id))
    if (resp != None and resp != ""):
        soup = BeautifulSoup(resp.text)
        if (soup.find_all("h4", {"class": "List-headerText"}) != None and soup.find_all("h4", {
            "class": "List-headerText"}).__len__() > 0):
            # 关注数和浏览数
            answer_num = soup.find_all("h4", {"class": "List-headerText"})[0].text
            answer_num = answer_num[0:answer_num.index("个回答")]
            follow_num = soup.find_all("div", {"class": "NumberBoard-value"})[0].text
            read_num = soup.find_all("div", {"class": "NumberBoard-value"})[1].text
            return (question_id, answer_num, follow_num, read_num), True
        else:
            sql = "update zhihu_question set is_delete=0 where id=%s" % (question_id)
            server_connection.commit(sql)
            return (question_id, 0, 0, 0), False


# 根据数据库的question获取每日数据变化
def insert_question_info():
    is_end = True
    while (is_end):
        try:
            zhihu_main.get_question_list_type(1, 0, 20)
            if (zhihu_main.question_cursor.rowcount > 0):
                sql = "insert into zhihu_question_info(question_id,answer_num,follow_num,read_num,create_time,update_time,task_day) values"
                sql2 = "update zhihu_question set execute_type=2 where id in ("
                for question in zhihu_main.question_cursor.fetchall():
                    question_info, is_delete = get_href_detail(question[0])
                    if (is_delete == True):
                        sql += "(%s,%s,%s,%s,NOW(),NOW(),CURDATE())," % (
                            question_info[0], question_info[1], question_info[2], question_info[3])
                        sql2 += "\"%s\"," % (question_info[0])
                sql = sql[:-1]
                sql2 = sql2[:-1]
                sql2 += ")"
                sql += "on DUPLICATE key UPDATE answer_num=values(answer_num), follow_num = VALUES(follow_num),read_num=values(read_num),create_time=values(create_time),update_time=values(update_time)"
                server_connection.commit(sql)
                server_connection.commit(sql2)
                if (zhihu_main.question_cursor.rowcount < 20):
                    is_end = False
                    log.info("break")
            else:
                is_end = False
                log.info("break")
        except:
            log.info("insert_question_info:error")


if __name__ == '__main__':
    if zhihu_main.is_login():
        insert_question_info()
    else:
        zhihu_main.login()
