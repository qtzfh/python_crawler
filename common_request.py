import time
import requests
import certifi
import log
import server_connection

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.63 Safari/537.36',
}


def request_get_sleep_one(url):
    time.sleep(1)
    try:
        resp = requests.get(url, headers=headers, timeout=60, verify=certifi.where())
        return resp
    except:
        log.error(url)

def cookies():
    sql = "select cookies from cookies  where type = 'zhihu' limit 0,1"
    server_connection.commit(sql)
    question_cursor = server_connection.cursor
    cookies = ""
    for data in question_cursor.fetchall():
        cookies =  data[0]
    return cookies

session_headers = {
    'cookie':cookies(),
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.63 Safari/537.36',
}

# 封装requests 请求
def session_get_sleep_three(url):
    time.sleep(3)
    try:
        session = requests.Session()
        resp = session.get(url, headers=session_headers, timeout=60, verify=certifi.where())
        return resp
    except:
        log.error(url)

