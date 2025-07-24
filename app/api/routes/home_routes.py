from fastapi import APIRouter
from fastapi.responses import FileResponse

homeRouter = APIRouter()

@homeRouter.get('/')
def sendIndexPage():
    return FileResponse('app/templates/index.html')

@homeRouter.get('/home')
def sendIndexPage():
    return FileResponse('app/templates/index.html')

import asyncio
from pydantic import BaseModel
from fastapi import BackgroundTasks

async def performTask(taskId):
    await asyncio.sleep(3)
    print('{}번 태스크 수행 완료.'.format(taskId))

@homeRouter.get('/bgtask')
def sendBGTestPage():
    return FileResponse('app/templates/bg_test.html')

class TaskInfo(BaseModel):
    taskId: int

@homeRouter.post('/bgtask')
async def createTask(
    taskId: TaskInfo    # to receive JSON data
    , bgTask: BackgroundTasks
):
    bgTask.add_task(performTask, taskId)
    return {"message": '태스크가 생성되었습니다.'}

# from app.utils.messaging import add # 셀러리 태스크 가져오기

# @homeRouter.get('/celeryadd')
# async def celeryAdd():
#     task = add.delay(1, 2)	# add 태스크를 셀러리에 전달

#     result = task.get() # 또는 task.result

#     print('homeRouter.celeryAdd().result:', result)

from app.utils.messaging import AddTask # 셀러리 태스크(클래스) 가져오기

@homeRouter.get('/celeryadd')
async def celeryAdd():
    task = AddTask().delay(5, 6)	# AddTask 태스크를 셀러리에 전달

    result = task.get() # 또는 task.result

    print('homeRouter.celeryAdd().result:', result)
