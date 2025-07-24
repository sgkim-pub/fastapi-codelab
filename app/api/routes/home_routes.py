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
