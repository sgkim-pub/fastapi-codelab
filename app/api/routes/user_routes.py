from fastapi import APIRouter
from fastapi.responses import FileResponse

userRouter = APIRouter(prefix='/user')

@userRouter.get('/signup', status_code=200)
def sendSignupPage():
    return FileResponse('app/templates/signup.html')

