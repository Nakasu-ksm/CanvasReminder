# coding=utf-8
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMessageBox
import time
from pygame.mixer import music
import pygame
import schedule
from PyQt5.QtCore import Qt
import configparser
import requests
import webbrowser
pygame.init()
config = configparser.ConfigParser() # 类实例化
config.read("config.ini",encoding='utf-8')
assignment = {}
web = config['DEFAULT']['website']
remind = config['TIME']['remindtime']
token = config['DEFAULT']['APITOKEN']
ismusic = config['CONFIG']['RemindMusic']
musicname = config['CONFIG']['RemindMusicName']
Music = music.load(musicname)

headers = {
    'Authorization':"Bearer {}".format(token)
}
app = QApplication(sys.argv)
q = QWidget()
q.setWindowFlag(Qt.WindowStaysOnTopHint)
import json
import datetime
def convert_time_to_str(time):
    if (time < 10):
        time = '0' + str(time)
    else:
        time=str(time)
    return time

def sec_to_data(y):

    h=int(y//3600 % 24)
    d = int(y // 86400)
    m =int((y % 3600) // 60)
    s = round(y % 60,2)
    died = 0
    if d<0:
        died = 1

    h=convert_time_to_str(h)
    m=convert_time_to_str(m)
    s=convert_time_to_str(s)
    d=convert_time_to_str(d)
    # 天 小时 分钟 秒
    if died == 1:
        return "已经超时，请尽快完成！"
    else:
        return d + "天" + h + "小时" + m + "分钟" + s + "秒"


def show_homework(homework,timeStamp, calender_activity,endtime,today,LastLoop):
    if calender_activity == 0:
        if (homework['course_id'] == 226 or homework['course_id'] == 227) :
            dateArray = datetime.datetime.fromtimestamp(endtime)
            homeworkdue = dateArray.strftime("%Y-%m-%d")
            # homeworktime 是当前时间
            if today != homeworkdue:
                return


    #print(homework['plannable']['title'])
    endint = endtime - int(time.mktime(time.localtime()))
    enddate = sec_to_data(endint)
    if ismusic == "True":
        if not music.get_busy():
            music.play()
    if calender_activity == 1:
        reply = QMessageBox.warning(q, '日历项目', '你有日历项目\n名称:' + homework["plannable"][
            'title'] + '\n点击yes进入详情页面！' + "\n结束时间:" + timeStamp+"\n剩余时间:"+enddate, QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            webbrowser.open(homework['html_url'], new=0, autoraise=True)
            # 打开页面


    else:
        if homework['submissions']['submitted'] == True:
            return
        reply = QMessageBox.warning(q, '作业要交了', '你的作业\n作业名:' + homework["plannable"][
            'title'] + '\n要交了\n点击yes进入提交页面！' + "\n上交时间:" + timeStamp+"\n剩余时间:"+enddate, QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            webbrowser.open(web + homework['html_url'], new=0, autoraise=True)
            QMessageBox.information(q, "Canvas作业助手", "加油", QMessageBox.Yes)

            # 打开页面
        else:
            QMessageBox.information(q, "Canvas作业助手", "请尽快提交作业吧" + "\n上交时间:" + timeStamp, QMessageBox.Yes)
    if LastLoop:
        if ismusic == "True":
            # 每个窗口播放歌曲
            if music.get_busy():
                music.stop()

    #sys.exit(0)


def run():
    homeworktime = time.strftime("%Y-%m-%d", time.localtime())
    #print(time.strftime("%Y-%m-%d", time.localtime()))
    # con = sqlite3.connect("canvas.db")
    # cur = con.cursor()
    # cur.execute()
    try:
        getjson = requests.get('{}/api/v1/planner/items?start_date='.format(web)+homeworktime, headers=headers)

    except:
        return

    js = json.loads(getjson.text)
    last = len(js)
    count = 0
    LastLoop = False
    for jsloop in js:
        if last == count+1:
            LastLoop = True
        count = count + 1
        calender_activity = 0
        if jsloop['plannable_type'] == "calendar_event" or jsloop['plannable_type'] == "planner_note":
            # due = jsloop['plannable']['end_at']
            due = jsloop['plannable_date']

            calender_activity = 1
        else:
            try:
                due = jsloop['plannable']['due_at']
                if jsloop['plannable']['due_at'] == None:
                    due = jsloop['plannable_date']


            except:

                continue




        if due:
            timeArray = time.strptime(due, "%Y-%m-%dT%H:%M:%SZ")
            endtime = int(time.mktime(timeArray)) + 28800  # 东八
            dateArray = datetime.datetime.fromtimestamp(endtime)
            timeStamp = dateArray.strftime("%Y年%m月%d日-%H点%M分%S秒")
            if not assignment.get(jsloop['plannable']['id']):
                assignment[jsloop['plannable']['id']] = int(time.mktime(time.localtime()))
                show_homework(jsloop, timeStamp, calender_activity, endtime, homeworktime, LastLoop)
            util_time = int(time.mktime(time.localtime())) - int(assignment[jsloop['plannable']['id']])
            if util_time >= int(remind):
                # 只显示今日的

                assignment[jsloop['plannable']['id']] = int(time.mktime(time.localtime()))
                show_homework(jsloop, timeStamp, calender_activity, endtime, homeworktime, LastLoop)
            else:
                continue









schedule.every(0.01).minutes.do(run)
while True:
    schedule.run_pending()  # run_pending：运行所有可以运行的任务
