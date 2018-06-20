from bs4 import BeautifulSoup
import log
import server_connection
import common_request
import zhihu_main


# 根据href获取每个href的详情
def get_href_detail(question_id):
    log.info("get_href_detail:" + question_id)
    resp = common_request.request_get_sleep_one("https://www.zhihu.com/question/%s" % (question_id))
    try:
        topic_ids = []
        if (resp != None and resp != ""):
            soup = BeautifulSoup(resp.text)
            if soup.find_all("button", {"type": "submit"}) != None and soup.find_all("button",
                                                                                     {"type": "submit"}).__len__() > 0:
                resp = common_request.session_get_sleep_three("https://www.zhihu.com/question/%s" % (question_id))
                soup = BeautifulSoup(resp.text)
            if (soup.find_all("h4", {"class": "List-headerText"}) != None and soup.find_all("h4", {
                "class": "List-headerText"}).__len__() > 0):
                # 关注数和浏览数
                topic_links = soup.find_all("a", {"class": "TopicLink"})
                for topic_link in topic_links:
                    topic_ids.append(topic_link.get('href').replace('//www.zhihu.com/topic/', ''))
                return topic_ids, True
            else:
                sql = "update zhihu_question set is_delete=0 where id=%s" % (question_id)
                server_connection.commit(sql)
                return topic_ids, False
    except:
        log.info("get_href_detail:error" + question_id)
        return topic_ids, False


# 根据数据库的question获取topic
def insert_topic_and_relation():
    is_end = True
    question_id = 0
    while (is_end):
        zhihu_main.get_question_list_type(question_id, 0, 20)
        row_count = zhihu_main.question_cursor.rowcount
        if (row_count > 0):
            sql = "insert into zhihu_topic(topic_id,create_time,update_time) values"
            sql2 = "insert into zhihu_topic_question_relation(topic_id,question_id,create_time,update_time) values"
            for question in zhihu_main.question_cursor.fetchall():
                topic_ids, is_delete = get_href_detail(str(question[0]))
                if (is_delete == True):
                    for topic_id in topic_ids:
                        sql += '(%s,NOW(),NOW()),' % (topic_id)
                        sql2 += '(%s,%s,NOW(),NOW()),' % (topic_id, question[0])
                question_id = question[0]
            sql = sql[:-1]
            sql2 = sql2[:-1]
            sql += 'on DUPLICATE key UPDATE update_time=values(update_time)'
            sql2 += 'on DUPLICATE key UPDATE update_time=values(update_time)'
            server_connection.commit(sql)
            server_connection.commit(sql2)
            if (row_count <= 10):
                is_end = False
                log.info("break")
        else:
            is_end = False
            log.info("break")


def get_topic_info(topic_id):
    url = "https://www.zhihu.com/topic/%s/top-answers" % (str(topic_id))
    resp = common_request.request_get_sleep_one(url)
    soup = BeautifulSoup(resp.text)
    if soup.find_all("strong", {"class": "NumberBoard-itemValue"}) != None and soup.find_all("strong", {
        "class": "NumberBoard-itemValue"}).__len__() > 0:
        follow_num = soup.find_all("strong", {"class": "NumberBoard-itemValue"})[0].string
        question_num = soup.find_all("strong", {"class": "NumberBoard-itemValue"})[1].string
        topic_name = soup.title.string.replace('- 知乎', '').strip()
        follow_num = follow_num.replace(',', '')
        question_num = question_num.replace(',', '')
        return topic_name, follow_num, question_num
    else:
        return None, 0, 0


def update_topic_info(topic_id):
    topic_name, follow_num, question_num = get_topic_info(topic_id)
    if topic_name != None:
        update_topic_sql = "update zhihu_topic set topic_name=\"%s\",follow_num=%s,question_num=%s,update_time=NOW() where topic_id=%s" % (
            topic_name, follow_num, question_num, topic_id)
        server_connection.commit(update_topic_sql)


# 根据topic_id，更新话题信息并且获取topic下精华问题
def update_topic_info_and_get_question_info():
    topic_id = 0
    is_end = True
    while (is_end):
        zhihu_main.get_topic_list(topic_id, 0, 20)
        row_count = zhihu_main.question_cursor.rowcount
        if (row_count > 0):
            for topic_id in zhihu_main.question_cursor.fetchall():
                update_topic_info(topic_id[0])
                topic_id = topic_id[0]
                if (row_count <= 10):
                    is_end = False
                    log.info("break")
        else:
            is_end = False
            log.info("break")


if __name__ == '__main__':
    # insert_topic_and_relation()
    update_topic_info_and_get_question_info()
