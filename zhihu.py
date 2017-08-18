# -*- coding:utf-8 -*-
import requests
import re
import http.cookiejar as cookielib
from PIL import Image
import time
import os.path
from bs4 import BeautifulSoup
import mysql_commit
import datetime
import proxy_ip

headers = {
    'Connection': 'Keep-Alive',
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.63 Safari/537.36',
    'Accept-Encoding': 'gzip, deflate,br',
    'Host': 'www.zhihu.com',
    'DNT': '1'
}

phone = "1886xxxxxxx"
password = "xxxxxx"

session = requests.session()
session.cookies = cookielib.LWPCookieJar(filename='cookies')
try:
    session.cookies.load(ignore_discard=True)
except:
    print("Cookie 未能加载")


def proxies():
    host = proxy_ip.get_proxy_ip()
    proxies = {
        "https": "%s" % (host),
    }
    print(proxies)
    return proxies


resp = session.get("https://www.zhihu.com", headers=headers, proxies=proxies())
print(resp)


# 获取xsrf
def get_xsrf(data):
    patten = 'name=\"_xsrf\" value=\"(.*)\"'
    _xsrf = re.findall(patten, data)
    return _xsrf[0]


# 获取验证码
def get_captcha():
    t = str(int(time.time() * 1000))
    captcha_url = 'https://www.zhihu.com/captcha.gif?r=' + t + "&type=login"
    r = session.get(captcha_url, headers=headers, proxies=proxies())
    with open('captcha.jpg', 'wb') as f:
        f.write(r.content)
        f.close()
    # 用pillow 的 Image 显示验证码
    # 如果没有安装 pillow 到源代码所在的目录去找到验证码然后手动输入
    try:
        im = Image.open('captcha.jpg')
        im.show()
        im.close()
    except:
        print(u'请到 %s 目录找到captcha.jpg 手动输入' % os.path.abspath('captcha.jpg'))
    captcha = input("please input the captcha\n>")
    return captcha


def login():
    _xsrf = get_xsrf(resp.text)
    postData = {
        "_xsrf": _xsrf,
        "password": password,
        "phone_num": phone
    }
    response = requests.post("https://www.zhihu.com/login/phone_num", postData, headers=headers)
    # 说明需要验证码才能登陆
    if response.json()['r'] == 1:
        postData["captcha"] = get_captcha()
        response = session.post("https://www.zhihu.com/login/phone_num", data=postData, headers=headers)
        print(response.json()['msg'])
    # 保存session到文件中
    session.cookies.save()


def is_login():
    # 通过查看用户个人信息来判断是否已经登录
    url = "https://www.zhihu.com/settings/profile"
    login_code = session.get(url, headers=headers, allow_redirects=False, proxies=proxies()).status_code
    if login_code == 200:
        return True
    else:
        return False


question_list = []


def get_day_hot(day):
    print("get_day_hot")
    if (day == 0 or day == None):
        # 第一次打开的页面
        resp = session.get("https://www.zhihu.com/explore#daily-hot", headers=headers, proxies=proxies())
        soup = BeautifulSoup(resp.text)
        for link in soup.find_all("a", {"class": "question_link"}):
            question_list.append((link.get('href'), link.text.replace("\n", "").replace("\"", "'")))
    else:
        # 更多选项
        url = "https://www.zhihu.com/node/ExploreAnswerListV2?params={\"offset\": %s,\"type\":\"day\"}" % (day)
        resp = session.get(url, headers=headers, proxies=proxies())
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
    for i in range(question_list.__len__()):
        href = question_list[i][0]
        title = question_list[i][1]
        sql += "(\"%s\",\"%s\",\"%s\",NOW(),NOW(),CURDATE())," % (
            href["/question/".__len__():href.index("/answer")], title, href[0:href.index("/answer")])
    sql = sql[:-1]
    sql += "ON DUPLICATE KEY UPDATE title = values(title),task_day=values(task_day);"
    mysql_commit.commit(sql)


# 根据href获取每个href的详情
def get_href_detail(question_id):
    print("get_href_detail:" + question_id)
    resp = session.get("https://www.zhihu.com/question/%s" % (question_id), headers=headers, proxies=proxies())
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
        mysql_commit.commit(sql)
        return (question_id, 0, 0, 0), False


question_cursor = None

# 获取未被爬取的数据
def get_not_today_question_list(offset, limit):
    sql = "select id from zhihu_question where (task_day!=CURDATE() or task_day IS NULL ) and is_delete=1 limit %s,%s" % (
        offset, limit)
    cursor = mysql_commit.commit(sql)
    global question_cursor
    question_cursor = cursor

# 获取所有数据
def get_all_question_list(offset, limit):
    sql = "select id from zhihu_question where is_delete=1 limit %s,%s" % (
        offset, limit)
    cursor = mysql_commit.commit(sql)
    global question_cursor
    question_cursor = cursor


# 根据数据库的question获取每日数据变化
def task_question_info():
    print("task_question_info")
    while (True):
        get_not_today_question_list(0, 20)
        if (question_cursor.rowcount > 0):
            sql = "insert into zhihu_question_info(question_id,answer_num,follow_num,read_num,create_time,update_time,task_day) values"
            sql2 = "update zhihu_question set task_day=CURDATE() where id in ("
            for question in question_cursor.fetchall():
                question_info, is_delete = get_href_detail(question[0])
                if (is_delete == True):
                    sql += "(%s,%s,%s,%s,NOW(),NOW(),CURDATE())," % (
                        question_info[0], question_info[1], question_info[2], question_info[3])
                    sql2 += "\"%s\"," % (question_info[0])
            sql = sql[:-1]
            sql2 = sql2[:-1]
            sql2 += ")"
            sql += "on DUPLICATE key UPDATE answer_num=values(answer_num), follow_num = VALUES(follow_num),read_num=values(read_num),create_time=values(create_time),update_time=values(update_time)"
            mysql_commit.commit(sql)
            mysql_commit.commit(sql2)
        else:
            break


def get_answer_info(question_id, offset):
    print("get_answer_info")
    limit = offset + 5
    url = "https://www.zhihu.com/api/v4/questions/%s/answers?include=data[*].is_normal,admin_closed_comment,reward_info,is_collapsed," \
          "annotation_action,annotation_detail,collapse_reason,is_sticky,collapsed_by,suggest_edit,comment_count,can_comment,content," \
          "editable_content,voteup_count,reshipment_settings,comment_permission,created_time,updated_time,review_info,question,excerpt," \
          "relationship.is_authorized,is_author,voting,is_thanked,is_nothelp,upvoted_followees;data[*].mark_infos[*].url;data[*]" \
          ".author.follower_count,badge[?(type=best_answerer)].topics&offset=%s&limit=%s&sort_by=defaul" % (
              question_id, offset, limit)
    resp = session.get(url, headers=headers, proxies=proxies()).json()
    sql = "insert into zhihu_answer_info(id,question_id,agree_num,comment_num,content,url_token,author_name,created_time,create_time,update_time) values"
    if (resp['data'] != None and resp['data'].__len__() > 0):
        for i in range(resp['data'].__len__()):
            agree_num = resp['data'][i]['voteup_count']
            comment_num = resp['data'][i]['comment_count']
            content = resp['data'][i]['content']
            url_token = resp['data'][i]['author']['url_token']
            author_name = resp['data'][i]['author']['name']
            created_time = resp['data'][i]['created_time']
            answer_id = resp['data'][i]['id']
            sql += "(%s,%s,%s,%s,\"%s\",\"%s\",\"%s\",\"%s\",NOW(),NOW())," % (
                answer_id, question_id, agree_num, comment_num, content.replace("\"", "'"), url_token, author_name,
                created_time)
        sql = sql[:-1]
        sql += "on DUPLICATE key UPDATE update_time=values(update_time), author_name=values(author_name), content = VALUES(content),agree_num=values(agree_num),comment_num=values(comment_num),url_token=values(url_token)"
        print(sql)
        mysql_commit.commit(sql)
    if (resp['paging']['is_end'] == True):
        return True
    else:
        return False


def insert_answer_info():
    print("insert_answer_info")
    offset = 0
    while (True):
        get_all_question_list(offset, 20)
        if (question_cursor.rowcount > 0):
            i = 0
            for question in question_cursor.fetchall():
                while (True):
                    end = get_answer_info(question[0], i)
                    i = i + 5
                    if (end == True):
                        break
            offset = offset + 20
        else:
            break


# 每日3.15 运行task获取数据
def task_all_work():
    now = datetime.datetime.now()
    sched_time = datetime.datetime(now.year, now.month, now.day, 3, 15, 0)
    tomorrow = sched_time + datetime.timedelta(days=1)
    print(tomorrow)
    while True:
        now = datetime.datetime.now()
        print(now)
        if sched_time < now < (sched_time + datetime.timedelta(minutes=2)):
            sched_time = datetime.datetime(tomorrow.year, tomorrow.month, tomorrow.day, 3, 15, 0)
            tomorrow = tomorrow + datetime.timedelta(days=1)
            # 获取question_list并且insert
            insert_question()
            # 获取question_info 详细信息
            task_question_info()
            # 获取question_info下的回答内容
            insert_answer_info()
            # 运行完之后sleep 5min 保证不会再进入本次循环
            time.sleep(300)
        time.sleep(60)


if __name__ == '__main__':
    if is_login():
        # 获取question_list并且insert
        insert_question()
        print("insert")
        # 获取question_info 详细信息
        task_question_info()
        print("task_question")
        # 获取question_info下的回答内容
        insert_answer_info()
        print("answer")
    else:
        login()
