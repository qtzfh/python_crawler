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
        zhihu_main.get_question_list_by_question_id(question_id, 0, 20)
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


# 获取首页信息
def get_topic_info_first(topic_id):
    url = "https://www.zhihu.com/topic/%s/top-answers" % (str(topic_id))
    resp = common_request.request_get_sleep_one(url)
    soup = BeautifulSoup(resp.text)
    if soup.find_all("strong", {"class": "NumberBoard-itemValue"}) != None and soup.find_all("strong", {
        "class": "NumberBoard-itemValue"}).__len__() > 0:
        follow_num = soup.find_all("strong", {"class": "NumberBoard-itemValue"})[0].string
        question_num = soup.find_all("strong", {"class": "NumberBoard-itemValue"})[1].string
        question_titles = []
        question_ids = []
        # 知乎专栏
        special_titles = []
        special_ids = []
        for title_info in soup.find_all("a", {"data-za-detail-view-element_name": "Title"}):
            if title_info.get('href').find('zhuanlan.zhihu.com') > 0:
                special_titles.append(title_info.string)
                special_id = title_info.get('href').replace('//zhuanlan.zhihu.com/p/', '')
                special_ids.append(special_id)
            else:
                question_id = title_info.get('href').replace('/question/', '')
                question_id = question_id[0:question_id.find("/answer/")]
                question_titles.append(title_info.string)
                question_ids.append(question_id)
        topic_name = soup.title.string.replace('- 知乎', '').strip()
        follow_num = follow_num.replace(',', '')
        question_num = question_num.replace(',', '')
        return topic_name, follow_num, question_num, question_titles, question_ids, special_titles, special_ids
    else:
        return None, 0, 0


# 获取之后的信息
def get_topic_info_next(url):
    resp = common_request.request_get_sleep_one(url)
    resp_json = resp.json()
    is_end = resp_json['paging']['is_end']
    next_url = resp_json['paging']['next']
    datas = resp_json['data']
    question_titles = []
    question_ids = []
    # 知乎专栏
    special_titles = []
    special_ids = []
    for data in datas:
        data_target = data['target']
        if data_target['url'].find('zhuanlan.zhihu.com') > 0:
            special_titles.append(data_target['title'])
            special_ids.append(data_target['url'].replace('http://zhuanlan.zhihu.com/p/',''))
        else:
            question_titles.append(data_target['question']['title'])
            question_ids.append(data_target['question']['url'].replace('http://www.zhihu.com/api/v4/questions/',''))
    return is_end, next_url, question_titles, question_ids, special_titles, special_ids


def insert_question_and_relation(question_titles, question_ids, topic_id):
    if len(question_titles) > 0:
        insert_question_sql = "insert into zhihu_question(id,title,create_time,update_time) values"
        insert_relation_sql = "insert into zhihu_topic_question_relation(topic_id,question_id,create_time,update_time) values"
        for i in range(0, len(question_titles)):
            insert_question_sql += "(%s,'%s',NOW(),NOW())," % (question_ids[i], question_titles[i])
            insert_relation_sql += "(%s,%s,NOW(),NOW())," % (topic_id, question_ids[i])
        insert_question_sql = insert_question_sql[:-1]
        insert_relation_sql = insert_relation_sql[:-1]
        insert_question_sql += "on DUPLICATE key UPDATE update_time=values(update_time)"
        insert_relation_sql += "on DUPLICATE key UPDATE update_time=values(update_time)"
        server_connection.commit(insert_question_sql)
        server_connection.commit(insert_relation_sql)


def insert_special_and_relation(special_titles, special_ids, topic_id):
    if len(special_titles) > 0:
        insert_special_sql = "insert into zhihu_special(special_id,title,create_time,update_time) values"
        insert_special_relation_sql = "insert into zhihu_topic_special_relation(topic_id,special_id,create_time,update_time) VALUES "
        for i in range(0, len(special_titles)):
            insert_special_sql += "(%s,'%s',NOW(),NOW())," % (special_ids[i], special_titles[i])
            insert_special_relation_sql += "(%s,'%s',NOW(),NOW())," % (topic_id, special_ids[i])
        insert_special_sql = insert_special_sql[:-1]
        insert_special_relation_sql = insert_special_relation_sql[:-1]
        insert_special_sql += "on DUPLICATE key UPDATE update_time=values(update_time)"
        insert_special_relation_sql += "on DUPLICATE key UPDATE update_time=values(update_time)"
        server_connection.commit(insert_special_sql)
        server_connection.commit(insert_special_relation_sql)


# 更新topic信息
def update_topic_info(topic_name, follow_num, question_num, topic_id):
    if topic_name != None:
        update_topic_sql = "update zhihu_topic set topic_name=\"%s\",follow_num=%s,question_num=%s,update_time=NOW() where topic_id=%s" % (
            topic_name, follow_num, question_num, topic_id)
        server_connection.commit(update_topic_sql)


def handle_topic_info(topic_id):
    # 处理首页数据
    topic_name, follow_num, question_num, question_titles, question_ids, special_titles, special_ids = get_topic_info_first(
        topic_id)
    # update_topic_info(topic_name, follow_num, question_num, topic_id)
    insert_question_and_relation(question_titles, question_ids, topic_id)
    insert_special_and_relation(special_titles, special_ids, topic_id)
    # 处理首页之后的数据
    offset = 5
    url = "https://www.zhihu.com/api/v4/topics/%s/feeds/essence?include=data[?(target.type=topic_sticky_module)].target.data[?(target.type=answer)].target.content,relationship.is_authorized,is_author,voting,is_thanked,is_nothelp;data[?(target.type=topic_sticky_module)].target.data[?(target.type=answer)].target.is_normal,comment_count,voteup_count,content,relevant_info,excerpt.author.badge[?(type=best_answerer)].topics;data[?(target.type=topic_sticky_module)].target.data[?(target.type=article)].target.content,voteup_count,comment_count,voting,author.badge[?(type=best_answerer)].topics;data[?(target.type=topic_sticky_module)].target.data[?(target.type=people)].target.answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics;data[?(target.type=answer)].target.content,relationship.is_authorized,is_author,voting,is_thanked,is_nothelp;data[?(target.type=answer)].target.author.badge[?(type=best_answerer)].topics;data[?(target.type=article)].target.content,author.badge[?(type=best_answerer)].topics;data[?(target.type=question)].target.comment_count&limit=10&offset=%s" % (
        topic_id, offset)
    while (True):
        is_end, url, question_titles, question_ids, special_titles, special_ids = get_topic_info_next(url)
        offset += 10
        insert_question_and_relation(question_titles, question_ids, topic_id)
        insert_special_and_relation(special_titles, special_ids, topic_id)
        if is_end !=False:
            log.info("break")
            break
        if offset >= 2000:
            log.info("break")
            break


# 根据topic_id，更新话题信息并且获取topic下精华问题
def update_topic_info_and_get_question_info():
    topic_id = 0
    is_end = True
    while (is_end):
        zhihu_main.get_topic_list(topic_id, 0, 20)
        row_count = zhihu_main.question_cursor.rowcount
        if (row_count > 0):
            for topic_id in zhihu_main.question_cursor.fetchall():
                topic_id = topic_id[0]
                try:
                    handle_topic_info(topic_id)
                except(EOFError):
                    log.error(topic_id)
                    log.error(EOFError)
                if (row_count <= 0):
                    is_end = False
                    log.info("break")
        else:
            is_end = False
            log.info("break")


if __name__ == '__main__':
    update_topic_info_and_get_question_info()

