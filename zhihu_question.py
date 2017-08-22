# -*- coding:utf-8 -*-
from bs4 import BeautifulSoup
import server_connection
import log
import zhihu_main

question_list = []

def get_day_hot(day):
    log.info("get_day_hot")
    if (day == 0 or day == None):
        # 第一次打开的页面
        resp = zhihu_main.request_info("https://www.zhihu.com/explore#daily-hot")
        soup = BeautifulSoup(resp.text)
        for link in soup.find_all("a", {"class": "question_link"}):
            question_list.append((link.get('href'), link.text.replace("\n", "").replace("\"", "'")))
    else:
        # 更多选项
        url = "https://www.zhihu.com/node/ExploreAnswerListV2?params={\"offset\": %s,\"type\":\"day\"}" % (day)
        resp = zhihu_main.request_info(url)
        if (resp.text == None or resp.text == ""):
            return False
        else:
            soup = BeautifulSoup(resp.text)
            for link in soup.find_all("a", {"class": "question_link"}):
                question_list.append((link.get('href'), link.text.replace("\n", "").replace("\"", "'")))
    return True


# 将href和title保存到数据库
def insert_question():
    sql = "insert into zhihu_question (id,title,href,create_time,update_time,task_day) VALUES "
    i = 0
    # 遍历获取所有页面
    while (True):
        i = i + 5
        isEnd = get_day_hot(i)
        if (isEnd == False):
            break
    # 拼装sql
    if (question_list.__len__() > 0):
        for i in range(question_list.__len__()):
            href = question_list[i][0]
            title = question_list[i][1]
            sql += "(\"%s\",\"%s\",\"%s\",NOW(),NOW(),CURDATE())," % (
                href["/question/".__len__():href.index("/answer")], title, href[0:href.index("/answer")])
        sql = sql[:-1]
        sql += "ON DUPLICATE KEY UPDATE title = values(title),task_day=values(task_day);"
        server_connection.commit(sql)

question_cursor = None

if __name__ == '__main__':
    if zhihu_main.is_login():
        insert_question()
    else:
        zhihu_main.login()
