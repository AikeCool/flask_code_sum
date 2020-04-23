from flask import request, session, Blueprint, render_template, redirect
import pymysql, datetime, json
from flask_code_sum.utils import helper

blue_detail = Blueprint("user", __name__)


@blue_detail.before_request
def login_detection():
    user_info = session.get("user_info")
    print(user_info)
    if not user_info:
        return redirect("/login")


@blue_detail.route("/user")
def user():
    user_id = session["user_info"]["user_id"]
    # db = pymysql.connect("localhost", "root", "123456", "code_sum")
    # cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
    sql = "select * from user"
    # cursor.execute("select * from user where username=%s and password=%s", (username, pwd))
    # cursor.execute(sql)
    # user_list = cursor.fetchall()
    # cursor.close()
    # db.close()
    user_list = helper.fetch_all(sql, ())

    # 代码总和
    sql = "select user.username, sum(code_line) as code_line from code_stat left join user on code_stat.user_id = user.id group by user_id"
    code_line_sum_list = helper.fetch_all(sql, ())
    info = []
    for code_line_sum in code_line_sum_list:
        info.append([code_line_sum["username"], int(code_line_sum["code_line"])])
    print(info)
    return render_template("user.html", user_list=user_list, info=json.dumps(info))


@blue_detail.route("/user/<int:nid>")
def user_info(nid):
    # db = pymysql.connect("localhost", "root", "123456", "code_sum")
    # cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
    sql = "select * from code_stat where user_id=%s"
    sql_arg = (nid,)
    # cursor.execute(sql, sql_arg)
    # code_log_list = cursor.fetchall()
    # cursor.close()
    # db.close()
    # print(code_log_list)
    code_log_list = helper.fetch_all(sql, sql_arg)
    timer_list = []
    code_line_list = []
    for code_log in code_log_list:
        timer_list.append(str(code_log["timer"]))
        code_line_list.append(code_log["code_line"])

    return render_template("user_info.html", code_log_list=code_log_list, timer_list=json.dumps(timer_list),
                           code_line_list=json.dumps(code_line_list))


@blue_detail.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "GET":
        return render_template("upload.html")

    # 获取文件，判断是不是压缩文件
    from werkzeug.datastructures import FileStorage
    user_id = session["user_info"]["user_id"]
    timer = datetime.date.today()
    file_obj = request.files.get("code_file")
    file_tuple = file_obj.filename.rsplit(".", 1)
    if len(file_tuple) != 2:
        return "请上传zip压缩文件"
    if file_tuple[1] != "zip":
        return "请上传zip压缩文件"

    # 判断今天是否提交过文件
    # db = pymysql.connect("localhost", "root", "123456", "code_sum")
    # cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
    sql = "select * from code_stat where timer=%s and user_id=%s"
    sql_arg = (timer, user_id)
    # cursor.execute(sql, sql_arg)
    # code_stat_obj = cursor.fetchone()
    code_stat_obj = helper.fetch_all(sql, sql_arg)
    if code_stat_obj:
        return "今天已经提交过了，请明天再来"

    # 将文件写入到本地
    import os
    file_path = os.path.join(r"D:\PycharmProjects\untitled\day118\flask_code_sum\flask_code_sum\files",
                             file_obj.filename)
    file_obj.save(file_path)

    # 解压文件
    import shutil, uuid, zipfile
    target_path = os.path.join(r"D:\PycharmProjects\untitled\day118\flask_code_sum\flask_code_sum\files",
                               str(uuid.uuid4()))
    path_info = r"D:\PycharmProjects\untitled\day118\flask_code_sum\flask_code_sum\files\{}".format(file_obj.filename)
    shutil.unpack_archive(path_info, target_path)

    # 遍历解压后的文件
    total_num = 0  # 该压缩文件所有py文件的代码函数
    for base_path, folder_list, file_list in os.walk(target_path):
        """
        base_path:文件路径
        folder_list：路径下的文件夹列表
        file_list：路径下的文件列表
        """
        for file_name in file_list:
            file_path = os.path.join(base_path, file_name)
            file_ext = file_path.rsplit('.', maxsplit=1)
            if len(file_ext) != 2:
                continue
            if file_ext[1] != 'py':
                continue
            file_num = 0
            with open(file_path, 'rb') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith(b'#'):
                        continue
                    file_num += 1
            total_num += file_num

    # 将代码行数存入至数据库
    sql = "insert into code_stat(code_line,timer,user_id)values(%s,%s,%s)"
    arg = (total_num, timer, user_id)
    row = helper.insert(sql, arg)
    # cursor.execute("select * from user where username=%s and password=%s", (username, pwd))
    # arg = (total_num, timer, user_id)
    # cursor.execute(sql, arg)
    # db.commit()
    # cursor.close()
    # db.close()

    return render_template("upload.html", info="ok")
