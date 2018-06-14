import time
import requests
from bs4 import BeautifulSoup
import log
import server_connection
import zhihu_main

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.63 Safari/537.36',
}


def request_info(url):
    time.sleep(1)
    try:
        resp = requests.get(url, headers=headers, timeout=60, verify=zhihu_main.certifi.where())
    except:
        request_info(url)
    return resp


# 根据href获取每个href的详情
def get_href_detail(question_id):
    log.info("get_href_detail:" + question_id)
    resp = request_info("https://www.zhihu.com/question/%s" % (question_id))
    try:
        topic_ids = []
        if (resp != None and resp != ""):
            soup = BeautifulSoup(resp.text)
            if soup.find_all("button", {"type": "submit"}) != None and soup.find_all("button",
                                                                                     {"type": "submit"}).__len__() > 0:
                resp = zhihu_main.request_info("https://www.zhihu.com/question/%s" % (question_id))
                soup = BeautifulSoup(resp.text)
            if (soup.find_all("h4", {"class": "List-headerText"}) != None and soup.find_all("h4", {
                "class": "List-headerText"}).__len__() > 0):
                # 关注数和浏览数
                topic_links = soup.find_all("a", {"class": "TopicLink"})
                for topic_link in topic_links:
                    topic_ids.append(topic_link.get('href').replace('//www.zhihu.com/topic/',''))
                return topic_ids, True
            else:
                sql = "update zhihu_question set is_delete=0 where id=%s" % (question_id)
                server_connection.commit(sql)
                return topic_ids, False
    except:
        log.info("get_href_detail:error" + question_id)
        return topic_ids, False


# 根据数据库的question获取每日数据变化
def insert_topic_and_relation():
    is_end = True
    question_id = 0
    while (is_end):
        zhihu_main.get_question_list_type(question_id,0,20)
        row_count = zhihu_main.question_cursor.rowcount
        if (row_count > 0):
            sql = "insert into zhihu_topic(topic_id,create_time,update_time) values"
            sql2 = "insert into zhihu_topic_question_relation(topic_id,question_id,create_time,update_time) values"
            for question in zhihu_main.question_cursor.fetchall():
                topic_ids, is_delete = get_href_detail(str(question[0]))
                if (is_delete == True):
                    for topic_id in topic_ids:
                        sql +='(%s,NOW(),NOW()),' % (topic_id)
                        sql2 += '(%s,%s,NOW(),NOW()),' % (topic_id, question[0])
                question_id = question[0]
            sql = sql[:-1]
            sql2 = sql2[:-1]
            sql +='on DUPLICATE key UPDATE update_time=values(update_time)'
            sql2 +='on DUPLICATE key UPDATE update_time=values(update_time)'
            server_connection.commit(sql)
            server_connection.commit(sql2)
            if (row_count <= 10):
                is_end = False
                log.info("break")
        else:
            is_end = False
            log.info("break")


if __name__ == '__main__':
    insert_topic_and_relation()
