from fastapi import APIRouter
from fastapi.responses import FileResponse

userRouter = APIRouter(prefix='/user')

@userRouter.get('/signup', status_code=200)
def sendSignupPage():
    return FileResponse('app/templates/signup.html')


# 요청 객체(request 객체)에서 직접 데이터를 읽는 방법
# from fastapi.requests import Request
# from fastapi.responses import JSONResponse
# import json

# @userRouter.post('/signup', status_code=201)
# async def registerUser(request: Request):
#     requestBody = await request.body()

#     print('user_routes.py.registerUser().requestBody:', requestBody)

#     try:
#         bodyJSON = json.loads(requestBody)
#     except:
#         bodyJSON = {"username": '', "password": ''}

#     respJSON = {"username": bodyJSON["username"], "password": bodyJSON["password"]}

#     return JSONResponse(
#         content=respJSON
#         , status_code=201   # 201: created
#     )


# # 요청(request) 바디(body)에 포함된 JSON을 바로 읽을 수 있다.
# from fastapi import Body
# from fastapi.responses import JSONResponse

# @userRouter.post('/signup', status_code=201)
# def registerUser(
#     username: str = Body(...)
#     , password: str = Body(...)
# ):
#     respJSON = {"username": username, "password": password}

#     print('user_routes.py.registerUser().username(JSON):', username)
#     print('user_routes.py.registerUser().password(JSON):', password)

#     return JSONResponse(
#         content=respJSON
#         , status_code=201
#     )


# # 요청 바디에 포함된 JSON을 읽고 Pydantic 라이브러리로 검증한다.
# from pydantic import BaseModel, Field
# from fastapi.responses import JSONResponse

# class SignupInfo(BaseModel):
#     username: str
#     password: str

# # from typing import Annotated

# # class SignupInfo(BaseModel):
# #     username: str
# #     password: Annotated[str, Field(min_length=5)]

# @userRouter.post('/signup', status_code=201)
# def registerUser(signupinfo: SignupInfo):
#     username = signupinfo.username
#     password = signupinfo.password

#     respJSON = {"username": username, "password": password}

#     print('user_routes.py.registerUser().username(Pydantic):', username)
#     print('user_routes.py.registerUser().password(Pydantic):', password)

#     return JSONResponse(
#         content=respJSON
#         , status_code=201
#     )

# 파일이 포함된 요청의 바디를 읽는 경우
from fastapi import UploadFile, Form, File
from secrets import token_hex
import os
from fastapi.responses import JSONResponse

@userRouter.post('/signup', status_code=201)
async def registerUser(
    username: str = Form(...)
    , password: str = Form(...)
    , picture: UploadFile = File(None)
):
    if picture:
        pictureFileName = picture.filename

        fn = token_hex(10)
        ext = os.path.splitext(pictureFileName)[1]
        newPicFileName = fn + ext

        savePath = os.path.join('app/upload', 'user_profile')
        os.makedirs(savePath, exist_ok=True)

        filePath = os.path.join(savePath, newPicFileName)
        print('user_routes.py.registerUser().filePath:', filePath)

        with open(filePath, 'wb') as buffer:
            buffer.write(await picture.read())
    else:
        pictureFileName = None
        newPicFileName = None

    respJSON = {"username": username, "password": password, "picture": pictureFileName}

    print('user_routes.py.registerUser().username:', username)
    print('user_routes.py.registerUser().password:', password)
    print('user_routes.py.registerUser().pictureFileName:', pictureFileName)

    return JSONResponse(
        content=respJSON
        , status_code=201
    )
