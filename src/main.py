# import asyncio
from callAPI import checkDevice, checkUnattendedBot, deleteSchedule, getSchedule, getToken, runSchedule
from datetime import datetime, timedelta

url = 'http://10.226.107.101/'
tasks_unsuccess = []
devices = {}
fileIDs = []
timeSchedule = []

token = getToken(url)
# print(token)
'''
tasks_unsuccess = auditLog(url, token)
for task in tasks_unsuccess:
    print(task)
'''
devices = checkDevice(url, token)
for deviceID in devices["CONNECTED"]:
    unattendedID = checkUnattendedBot(url, token, deviceID)
    if unattendedID != "No Unattended Bot":
        break

if unattendedID == "No Unattended Bot":
    print("No available bot")
else:
    for deviceID in devices["DISCONNECTED"]:
        fileIDs, timeSchedule = getSchedule(url, token, deviceID)

    for i in fileIDs:
        for j in timeSchedule:
            if (i['id'] == j['id']):
                date = j['startDate']
                time = j['startTime'] + ':00'
                date_time = datetime.strptime(date + " " + time, '%Y-%m-%d %H:%M:%S')
                now = datetime.now()

                if date_time > now:
                    runSchedule(url, token, i["fileID"], i["fileName"], unattendedID, j['startDate'], j['startTime'])
                else:   # it's possible??
                    date_time = date_time + timedelta(minutes=10)
                    date, time = str(date_time).split(" ")
                    runSchedule(url, token, i["fileID"], i["fileName"], unattendedID, date, time[0:5])

                deleteSchedule(url, token, i['id'])
