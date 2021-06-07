from callAPI import checkDevice, checkUnattendedBot, deleteSchedule, deploymentStatus, getSchedule, getToken, runSchedule
from datetime import datetime, timedelta
from time import sleep

fileIDs = []
checkFile = {}              # {"ID": [task]}
timeSchedule = []
tasksInQueue = []
runningTasks = []
isAvailable = True
# timeInterval = 900          # 15 minutes

url = 'http://10.226.107.101/'
token = getToken(url)


while(True):
    devices = {}
    unattendedIDs = {}          # {"ID": "assignTasks_count"}
    availableIDs = {}           # {"ID": "assignTasks_count"}

    # check device & status
    devices = checkDevice(url, token)
    tasksInQueue, runningTasks = deploymentStatus(url, token)
    for deviceID in devices["CONNECTED"]:
        isAvailable = True
        unattendedID = checkUnattendedBot(url, token, deviceID)
        if unattendedID != "No Unattended Bot":
            for eachRunningTask in runningTasks:
                if eachRunningTask["userId"] == unattendedID:       # connected & unattended but running task
                    isAvailable = False
                    unattendedIDs[unattendedID] = 0
            if isAvailable:
                availableIDs[unattendedID] = 0                      # connected & unattended & available
    print(availableIDs)
    print(unattendedIDs)
    print(checkFile)

    if checkFile != []:
        for id in checkFile:
            print("test ", id)
            for task in checkFile[id]:
                for i in devices["CONNECTED"]:
                    if i in task['runAsUserIds']:
                        date = task['startDate']
                        time = task['startTime'] + ':00'
                        date_time = datetime.strptime(date + " " + time, '%Y-%m-%d %H:%M:%S')
                        now = datetime.now()
                        if date_time > now:
                            newID = runSchedule(url, token, task, i, task['startDate'], task['startTime'])
                        else:
                            now = datetime.now()
                            date_time = now + timedelta(minutes=10)
                            date, time = str(date_time).split(" ")
                            newID = runSchedule(url, token, task, i, date, time[0:5])
                        deleteSchedule(url, token, id)
        for id in list(checkFile):
            print("del ", id)
            for task in checkFile[id]:
                for i in devices["CONNECTED"]:
                    if i in task['runAsUserIds']:
                        del checkFile[id]

    if unattendedIDs == {} and availableIDs == {}:
        print("No available bot")
    else:
        if devices["DISCONNECTED"] == []:
            print("No disconnected device")
        else:
            for deviceID in devices["DISCONNECTED"]:
                print(deviceID)
                fileIDs, timeSchedule = getSchedule(url, token, deviceID)

                if (fileIDs != []):
                    for i in fileIDs:
                        for j in timeSchedule:
                            if (i['id'] == j['id']):
                                date = j['startDate']
                                time = j['startTime'] + ':00'
                                date_time = datetime.strptime(date + " " + time, '%Y-%m-%d %H:%M:%S')
                                now = datetime.now()

                                if (availableIDs != {}):
                                    minAssignTask = 100
                                    assignID = 0
                                    for availableID in availableIDs:
                                        if availableIDs[availableID] < minAssignTask:
                                            minAssignTask = availableIDs[availableID]
                                            assignID = availableID

                                    if date_time > now:
                                        newID = runSchedule(url, token, i, assignID, j['startDate'], j['startTime'])
                                    else:
                                        now = datetime.now()
                                        date_time = now + timedelta(minutes=10)
                                        date, time = str(date_time).split(" ")
                                        newID = runSchedule(url, token, i, assignID, date, time[0:5])
                                    availableIDs[assignID] += 1
                                    checkFile[newID] = []
                                    checkFile[newID].append(i)
                                else:
                                    minAssignTask = 100
                                    assignID = 0
                                    for unattendedID in unattendedIDs:
                                        if unattendedIDs[unattendedID] < minAssignTask:
                                            minAssignTask = unattendedIDs[unattendedID]
                                            assignID = unattendedID

                                    if date_time > now:
                                        newID = runSchedule(url, token, i, assignID, j['startDate'], j['startTime'])
                                    else:
                                        now = datetime.now()
                                        date_time = now + timedelta(minutes=10)
                                        date, time = str(date_time).split(" ")
                                        newID = runSchedule(url, token, i, assignID, date, time[0:5])
                                    unattendedIDs[assignID] += 1
                                    checkFile[newID] = []
                                    checkFile[newID].append(i)

                                deleteSchedule(url, token, i['id'])
                else:
                    print("No failed tasks")
    sleep(60)
