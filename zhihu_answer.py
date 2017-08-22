import zhihu_main
import log
import server_connection
from binascii import unhexlify

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
                url_token = data['author']['url_token']
                author_name = data['author']['name']
                created_time = data['created_time']
                answer_id = data['id']
                sql += "(%s,\"%s\",%s,%s,\"%s\",\"%s\",\"%s\",%s,NOW(),NOW())," % (
                    answer_id,question_id, agree_num, comment_num, content.replace("\"", "'"), url_token, author_name,
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
    offset = 0
    while (True):
        zhihu_main.get_all_question_list(offset, 20)
        if (zhihu_main.question_cursor.rowcount > 0):
            i = 0
            for question in zhihu_main.question_cursor.fetchall():
                while (True):
                    end = get_answer_info(question[0], i)
                    i = i + 5
                    if (end == True):
                        break
            offset = offset + 20
        else:
            break


if __name__ == '__main__':
    if zhihu_main.is_login():
        # 获取question_info下的回答内容
        # insert_answer_info()
        get_answer_info("21175127",670)
    else:
        zhihu_main.login()
