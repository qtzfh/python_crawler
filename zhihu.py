import requests
import re
import urllib
import http.cookiejar as cookielib
from PIL import Image
import time
import os.path
from bs4 import BeautifulSoup
import mysql_commit

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

resp = session.get("https://www.zhihu.com", headers=headers)


# 获取xsrf
def get_xsrf(data):
    patten = 'name=\"_xsrf\" value=\"(.*)\"'
    _xsrf = re.findall(patten, data)
    return _xsrf[0]


# 获取验证码
def get_captcha():
    t = str(int(time.time() * 1000))
    captcha_url = 'https://www.zhihu.com/captcha.gif?r=' + t + "&type=login"
    r = session.get(captcha_url, headers=headers)
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
    login_code = session.get(url, headers=headers, allow_redirects=False).status_code
    if login_code == 200:
        return True
    else:
        return False


question_list = []


def get_day_hot(day):
    if (day == 0 or day == None):
        # 第一次打开的页面
        resp = session.get("https://www.zhihu.com/explore#daily-hot", headers=headers)
        soup = BeautifulSoup(resp.text)
        for link in soup.find_all("a", {"class": "question_link"}):
            question_list.append((link.get('href'), link.text.replace("\n", "").replace("\"", "'")))
    else:
        # 更多选项
        url = "https://www.zhihu.com/node/ExploreAnswerListV2?params={\"offset\": %s,\"type\":\"day\"}" % (day)
        resp = session.get(url, headers=headers)
        if (resp.text == None or resp.text == ""):
            return False
        else:
            soup = BeautifulSoup(resp.text)
            for link in soup.find_all("a", {"class": "question_link"}):
                question_list.append((link.get('href'), link.text.replace("\n", "").replace("\"", "'")))
    return True


# 将href和title保存到数据库
def insert_question():
    sql = "insert into zhihu_question (id,title,href,create_time,update_time) VALUES "
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
        sql += "(\"%s\",\"%s\",\"%s\",NOW(),NOW())," % (
            href["/question/".__len__():href.index("/answer")], title, href[0:href.index("/answer")])
    sql = sql[:-1]
    sql += "ON DUPLICATE KEY UPDATE title = title;"
    mysql_commit.commit(sql)


# 根据href获取每个href的详情
def get_herf_detail(question_id):
    resp = session.get("https://www.zhihu.com/question/%s" % (question_id), headers=headers)
    soup = BeautifulSoup(resp.text)
    # 关注数和浏览数
    answer_num = soup.find_all("h4", {"class": "List-headerText"})[0].text
    answer_num = answer_num[0:answer_num.index("个回答")]
    follow_num = soup.find_all("div", {"class": "NumberBoard-value"})[0].text
    read_num = soup.find_all("div", {"class": "NumberBoard-value"})[1].text
    return (question_id, answer_num, follow_num, read_num)


# 根据数据库的question获取每日数据变化
def task_question_info():
    sql = "select id from zhihu_question"
    cursor = mysql_commit.commit(sql)
    sql = "insert into zhihu_question_info(question_id,answer_num,follow_num,read_num,create_time,update_time) values"
    for question in cursor.fetchall():
        question_info = get_herf_detail(question[0])
        sql += "(%s,%s,%s,%s,NOW(),NOW())," % (
            question_info[0], question_info[1], question_info[2], question_info[3])
    sql = sql[:-1]
    mysql_commit.commit(sql)


if __name__ == '__main__':
    if is_login():
        # insert_question()
        # get_herf_detail()
        task_question_info()
    else:
        login()
