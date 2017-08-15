import requests
import re
import urllib
import http.cookiejar as cookielib
from PIL import Image
import time
import os.path
from bs4 import BeautifulSoup

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
password = "xxxxx"

session = requests.session()
session.cookies = cookielib.LWPCookieJar(filename='cookies')
try:
    session.cookies.load(ignore_discard=True)
except:
    print("Cookie 未能加载")

resp = session.get("https://www.zhihu.com", headers=headers)


# 获取xsrf
def getXsrf(data):
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
        im = Image.open('D:/python_crawler/captcha.jpg')
        im.show()
        im.close()
    except:
        print(u'请到 %s 目录找到captcha.jpg 手动输入' % os.path.abspath('captcha.jpg'))
    captcha = input("please input the captcha\n>")
    return captcha


def login():
    _xsrf = getXsrf(resp.text)
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


def isLogin():
    # 通过查看用户个人信息来判断是否已经登录
    url = "https://www.zhihu.com/settings/profile"
    login_code = session.get(url, headers=headers, allow_redirects=False).status_code
    if login_code == 200:
        return True
    else:
        return False


question_list = []


def getDayHot(day):
    if (day == 0 or day == None):
        # 第一次打开的页面
        resp = session.get("https://www.zhihu.com/explore#daily-hot", headers=headers)
        soup = BeautifulSoup(resp.text)
        for link in soup.find_all("a", {"class": "question_link"}):
            question_list.append((link.get('href'), link.text.replace("\n","")))
    else:
        # 更多选项
        url = "https://www.zhihu.com/node/ExploreAnswerListV2?params={\"offset\": %s,\"type\":\"day\"}" % (day)
        resp = session.get(url, headers=headers)
        soup = BeautifulSoup(resp.text)
        for link in soup.find_all("a", {"class": "question_link"}):
            question_list.append((link.get('href'), link.text.replace("\n","")))


if __name__ == '__main__':
    if isLogin():
        for i in range(1):
            getDayHot(i * 5)
        print(question_list.__len__())
    else:
        login()
