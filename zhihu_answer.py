import zhihu_main
import log
import server_connection
from binascii import unhexlify
from apscheduler.schedulers.blocking import BlockingScheduler

def get_answer_info(question_id, offset):
    log.info("get_answer_info")
    limit = offset + 5
    url = "https://www.zhihu.com/api/v4/questions/%s/answers?include=data[*].is_normal,admin_closed_comment,reward_info,is_collapsed," \
          "annotation_action,annotation_detail,collapse_reason,is_sticky,collapsed_by,suggest_edit,comment_count,can_comment,content," \
          "editable_content,voteup_count,reshipment_settings,comment_permission,created_time,updated_time,review_info,question,excerpt," \
          "relationship.is_authorized,is_author,voting,is_thanked,is_nothelp,upvoted_followees;data[*].mark_infos[*].url;data[*]" \
          ".author.follower_count,badge[?(type=best_answerer)].topics&offset=%s&limit=%s&sort_by=defaul" % (
              question_id, offset, limit)
    resp = zhihu_main.request_info(url).json()
    sql = "INSERT INTO zhihu_answer_info(id,question_id,agree_num,comment_num,content,url_token,author_name,created_time,create_time,update_time) values"
    try:
        if (resp['data'] != None and resp['data'].__len__() > 0):
            for data in resp['data']:
                agree_num = data['voteup_count']
                comment_num = data['comment_count']
                content = data['content']
                content = content.encode('gbk', 'ignore')
                url_token = data['author']['url_token']
                author_name = data['author']['name']
                created_time = data['created_time']
                answer_id = data['id']
                sql += "(%s,\"%s\",%s,%s,\"%s\",\"%s\",\"%s\",%s,NOW(),NOW())," % (
                    answer_id, question_id, agree_num, comment_num, content.decode('gbk').replace("\"", "'"), url_token,
                    author_name,
                    created_time)
            sql = sql[:-1]
            sql += "on DUPLICATE key UPDATE update_time=values(update_time), author_name=values(author_name), content = VALUES(content),agree_num=values(agree_num),comment_num=values(comment_num),url_token=values(url_token)"
            server_connection.commit(sql)
    except:
        print("error")
    if (resp['paging']['is_end'] == True):
        return True
    else:
        return False


def insert_answer_info():
    log.info("insert_answer_info")
    i = 0
    while (True):
        host = zhihu_main.redis_conn.srandmember("question_id")
        host = host.decode()
        try:
            zhihu_main.redis_conn.srem("question_id", host)
            end = get_answer_info(host, i)
            i = i + 5
            if (end == True):
                log.info("break")
                break
        except Exception:
            log.info(Exception)
            zhihu_main.redis_conn.sadd(host)

if __name__ == '__main__':
    if zhihu_main.is_login():
        scheduler = BlockingScheduler()
        # 每天凌晨3.15执行
        scheduler.add_job(insert_answer_info, 'cron', hour=3, minute=15)
        try:
            scheduler.start()  # 采用的是阻塞的方式，只有一个线程专职做调度的任务
        except (KeyboardInterrupt, SystemExit):
            # Not strictly necessary if daemonic mode is enabled but should be done if possible
            scheduler.shutdown()
            print('Exit The Job!')
    else:
        zhihu_main.login()
