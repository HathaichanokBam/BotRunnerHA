import requests
import json
from requests.exceptions import HTTPError


def getToken(url):
    jsonData = {
        "username": "aae01",
        "password": "aae01P@ssw0rd"
    }
    try:
        res = requests.post(url + 'v1/authentication', data=json.dumps(jsonData))
        res.raise_for_status()
        res_dict = json.loads(res.text)
        token = res_dict["token"]
        return token
    except HTTPError as err:
        print(err)


def getSchedule(url, token, disconID):
    jsonData = {
        "sort": [
            {
                "field": "zonedNextRunDateTime",
                "direction": "asc"
            }
        ]
    }
    try:
        headers = {"X-Authorization": token}
        res = requests.post(url + 'v1/schedule/automations/list', data=json.dumps(jsonData), headers=headers)
        res.raise_for_status()
    except HTTPError as err:
        status_code = err.response.status_code
        if status_code == 401:
            token = getToken(url)
            headers = {"X-Authorization": token}
            res = requests.post(url + 'v1/schedule/automations/list', data=json.dumps(jsonData), headers=headers)
    fileIDs = []
    timeSchedule = []
    res_dict = json.loads(res.text)
    for i in res_dict["list"]:
        for id in i["runAsUserIds"]:
            if (id == disconID):
                fileIDs.append(i)
                timeSchedule.append({"id": i["id"], "startDate": i["startDate"], "startTime": i["startTime"]})
    return fileIDs, timeSchedule


def checkDevice(url, token):
    jsonData = {}

    try:
        headers = {"X-Authorization": token}
        res = requests.post(url + 'v2/devices/list', data=json.dumps(jsonData), headers=headers)
        res.raise_for_status()
    except HTTPError as err:
        status_code = err.response.status_code
        if status_code == 401:
            token = getToken(url)
            headers = {"X-Authorization": token}
            res = requests.post(url + 'v2/devices/list', data=json.dumps(jsonData), headers=headers)
    res_dict = json.loads(res.text)
    devices = {
        "CONNECTED": [],
        "DISCONNECTED": []
    }
    for i in res_dict["list"]:
        if i["status"] == "CONNECTED":
            devices["CONNECTED"].append(i["defaultUsers"][0]['id'])
        elif i["status"] == "DISCONNECTED":
            devices["DISCONNECTED"].append(i["defaultUsers"][0]['id'])
    return devices


def checkUnattendedBot(url, token, deviceID):
    jsonData = {
        "sort": [
            {
                "field": "username",
                "direction": "asc"
            }
        ],
        "filter": {},
        "fields": [],
        "page": {}
    }

    try:
        headers = {"X-Authorization": token}
        res = requests.post(url + 'v1/devices/runasusers/list', data=json.dumps(jsonData), headers=headers)
        res.raise_for_status()
    except HTTPError as err:
        status_code = err.response.status_code
        if status_code == 401:
            token = getToken(url)
            headers = {"X-Authorization": token}
            res = requests.post(url + 'v1/devices/runasusers/list', data=json.dumps(jsonData), headers=headers)
    res_dict = json.loads(res.text)
    for i in res_dict["list"]:
        if deviceID == i["id"]:
            return deviceID
    return "No Unattended Bot"


def auditLog(url, token):
    try:
        headers = {"X-Authorization": token}
        res = requests.get(url + 'v2/botinsight/data/api/getaudittraildata', headers=headers)
        res.raise_for_status()
    except HTTPError as err:
        status_code = err.response.status_code
        if status_code == 401:
            token = getToken(url)
            headers = {"X-Authorization": token}
            res = requests.get(url + 'v2/botinsight/data/api/getaudittraildata', headers=headers)
    res_dict = json.loads(res.text)
    tasks_unsuccess = []
    for i in res_dict["auditTrailDataList"]:
        if (i["status"] == "Unsuccessful" and i["activityType"] == "DEVICE_NOT_AVAILABLE_TO_ACQUIRE"):
            tasks_unsuccess.append(i["objectName"])
            print(i["objectName"])
            print(i["eventDescription"], "\n")
    return tasks_unsuccess


def deploymentStatus(url, token):
    headers = {"X-Authorization": token}
    jsonData = {}
    try:
        res = requests.post(url + 'v2/activity/list', data=json.dumps(jsonData), headers=headers)
        res.raise_for_status()
    except HTTPError as err:
        status_code = err.response.status_code
        if status_code == 401:
            token = getToken(url)
            headers = {"X-Authorization": token}
            res = requests.post(url + 'v2/activity/list', data=json.dumps(jsonData), headers=headers)
    tasksInQueue = []
    runningTasks = []
    res_dict = json.loads(res.text)
    for i in res_dict['list']:
        if i["status"] == "QUEUED":
            tasksInQueue.append(i)
        elif i['status'] == "UPDATE":
            runningTasks.append(i)
    return tasksInQueue, runningTasks


def runSchedule(url, token, file, userID, date, time):
    jsonData = file.copy()
    entries_to_remove = (
        'id', 'deviceIds', 'description', 'rdpEnabled', 'zonedNextRunDateTime', 'createdBy', 'createdOn',
        'updatedBy', 'updatedOn', 'tenantId', 'runAsUserIds', 'botInput', 'tenantUuid', 'overrideDefaultDevice', 'runElevated')
    for e in entries_to_remove:
        jsonData.pop(e, None)

    jsonData.update({
        "runAsUserIds": [
            str(userID)
        ],
        "startDate": date,
        "startTime": time
    })

    try:
        headers = {"X-Authorization": token}
        res = requests.post(url + 'v1/schedule/automations', data=json.dumps(jsonData), headers=headers)
        res.raise_for_status()
    except HTTPError as err:
        status_code = err.response.status_code
        if status_code == 401:
            token = getToken(url)
            headers = {"X-Authorization": token}
            res = requests.post(url + 'v1/schedule/automations', data=json.dumps(jsonData), headers=headers)
    print(res.text)
    res_dict = json.loads(res.text)
    return res_dict['id']


def deleteSchedule(url, token, id):
    try:
        headers = {"X-Authorization": token}
        res = requests.delete(url + 'v1/schedule/automations/' + str(id), headers=headers)
        res.raise_for_status()
    except HTTPError as err:
        status_code = err.response.status_code
        if status_code == 401:
            token = getToken(url)
            headers = {"X-Authorization": token}
            res = requests.delete(url + 'v1/schedule/automations/' + str(id), headers=headers)
    print(res.text)


'''
def deleteAutomation(url, token, id):
    try:
        headers = {"X-Authorization": token}
        res = requests.delete(url + 'v3/wlm/automations/' + str(id), headers=headers)
        res.raise_for_status()
    except HTTPError as err:
        status_code = err.response.status_code
        if status_code == 401:
            token = getToken(url)
            headers = {"X-Authorization": token}
            res = requests.delete(url + 'v3/wlm/automations/' + str(id), headers=headers)
    print(res.text)
'''
