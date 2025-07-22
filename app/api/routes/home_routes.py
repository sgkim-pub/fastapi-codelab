from fastapi import APIRouter
from fastapi.responses import FileResponse

homeRouter = APIRouter()

@homeRouter.get('/')
def sendIndexPage():
    return FileResponse('app/templates/index.html')

@homeRouter.get('/home')
def sendIndexPage():
    return FileResponse('app/templates/index.html')
