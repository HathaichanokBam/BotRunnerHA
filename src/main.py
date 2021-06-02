# import asyncio
from callAPI import checkDevice, checkUnattendedBot, deleteSchedule, deploymentStatus, getSchedule, getToken, runSchedule
from datetime import datetime, timedelta
from time import sleep

url = 'http://10.226.107.101/'
tasks_unsuccess = []
devices = {}
unattendedIDs = {}          # {"ID": "assignTasks_count"}
availableIDs = {}           # {"ID": "assignTasks_count"}
fileIDs = []
timeSchedule = []
tasksInQueue = []
runningTasks = []
isAvailable = True
timeInterval = 900          # 15 minutes

'''
def getFileIDandTime(url, token, id):
    fileIDs, timeSchedule = getSchedule(url, token, id)
    print(timeSchedule)
    if (fileIDs != []):
        for i in fileIDs:
            for j in timeSchedule:
                if (i['id'] == j['id']):
                    date = j['startDate']
                    time = j['startTime'] + ':00'
                    date_time = datetime.strptime(date + " " + time, '%Y-%m-%d %H:%M:%S')
    return fileIDs, timeSchedule, j['startDate'], j['startTime'], date_time
'''

while (True):
    token = getToken(url)
    # print(token)
    tasksInQueue, runningTasks = deploymentStatus(url, token)
    '''
    tasks_unsuccess = auditLog(url, token)
    for task in tasks_unsuccess:
        print(task)
    '''
    # check device & status
    devices = checkDevice(url, token)

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

    # move schedules that in range of time interval to other device
    for task in runningTasks:
        fileIDs, timeSchedule = getSchedule(url, token, task['userId'])
        print(timeSchedule)
        if (fileIDs != []):
            for i in fileIDs:
                for j in timeSchedule:
                    if (i['id'] == j['id']):
                        date = j['startDate']
                        time = j['startTime'] + ':00'
                        date_time = datetime.strptime(date + " " + time, '%Y-%m-%d %H:%M:%S')
                        now = datetime.now()
                        timeCheck = timedelta(seconds=timeInterval)
                        if date_time - now <= timeCheck:
                            if (availableIDs != {}):
                                minAssignTask = 100
                                assignID = 0
                                for availableID in availableIDs:
                                    if availableIDs[availableID] < minAssignTask:
                                        minAssignTask = availableIDs[availableID]

                                        fileIDs_, timeSchedule_ = getSchedule(url, token, availableID)
                                        print(timeSchedule_)
                                        if (fileIDs_ != []):
                                            for x in fileIDs_:
                                                for y in timeSchedule_:
                                                    if (x['id'] == y['id']):
                                                        date_ = y['startDate']
                                                        time_ = y['startTime'] + ':00'
                                                        date_time_ = datetime.strptime(date_ + " " + time_, '%Y-%m-%d %H:%M:%S')
                                                        if date_time_ == date_time:
                                                            print("don't move")
                                                        else:
                                                            assignID = availableID
                                print(assignID)
                                if assignID != 0:
                                    runSchedule(url, token, i["fileID"], i["fileName"], assignID, j['startDate'], j['startTime'])
                                    availableIDs[assignID] += 1
                                    deleteSchedule(url, token, i['id'])
                            else:
                                minAssignTask = 100
                                assignID = 0
                                for unattendedID in unattendedIDs:
                                    if unattendedIDs[unattendedID] < minAssignTask:
                                        minAssignTask = unattendedIDs[unattendedID]

                                        fileIDs_, timeSchedule_ = getSchedule(url, token, unattendedID)
                                        if (fileIDs_ != []):
                                            for x in fileIDs_:
                                                for y in timeSchedule_:
                                                    if (x['id'] == y['id']):
                                                        date_ = y['startDate']
                                                        time_ = y['startTime'] + ':00'
                                                        date_time_ = datetime.strptime(date_ + " " + time_, '%Y-%m-%d %H:%M:%S')
                                                        if date_time_ == date_time:
                                                            print("don't move")
                                                        else:
                                                            assignID = unattendedID
                                print(assignID)
                                if assignID != 0:
                                    runSchedule(url, token, i["fileID"], i["fileName"], assignID, j['startDate'], j['startTime'])
                                    unattendedIDs[assignID] += 1
                                    deleteSchedule(url, token, i['id'])

    '''
    # move queued tasks to available bot
    minAssignTask = 100
    assignID = 0
    print(tasksInQueue)

    for eachTask in tasksInQueue:
        # print(eachTask)
        # print(availableIDs)
        if availableIDs != {}:
            for availableID in availableIDs:            # find ID that has minimum assign tasks
                if availableIDs[availableID] < minAssignTask:
                    minAssignTask = availableIDs[availableID]
                    assignID = availableID

            now = datetime.now()
            date_time = now + timedelta(minutes=1)
            date, time = str(date_time).split(" ")
            runSchedule(url, token, eachTask["fileId"], eachTask["fileName"], assignID, date, time[0:5])
            availableIDs[assignID] += 1
            deleteAutomation(url, token, eachTask)
    '''
    # move schedule for disconnected devices
    if unattendedIDs == {}:
        print("No available bot")
    else:
        if devices["DISCONNECTED"] == []:
            print("No disconnected device")
        else:
            for deviceID in devices["DISCONNECTED"]:
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
                                    runSchedule(url, token, i["fileID"], i["fileName"], assignID, j['startDate'], j['startTime'])
                                else:   # it's possible??
                                    date_time = date_time + timedelta(minutes=10)
                                    date, time = str(date_time).split(" ")
                                    runSchedule(url, token, i["fileID"], i["fileName"], assignID, date, time[0:5])
                                availableIDs[assignID] += 1
                            else:
                                minAssignTask = 100
                                assignID = 0
                                for unattendedID in unattendedIDs:
                                    if unattendedIDs[unattendedID] < minAssignTask:
                                        minAssignTask = unattendedIDs[unattendedID]
                                        assignID = unattendedID

                                if date_time > now:
                                    runSchedule(url, token, i["fileID"], i["fileName"], assignID, j['startDate'], j['startTime'])
                                else:   # it's possible??
                                    date_time = date_time + timedelta(minutes=10)
                                    date, time = str(date_time).split(" ")
                                    runSchedule(url, token, i["fileID"], i["fileName"], assignID, date, time[0:5])
                                unattendedIDs[assignID] += 1

                            deleteSchedule(url, token, i['id'])
            else:
                print("No failed tasks")

    sleep(timeInterval)
