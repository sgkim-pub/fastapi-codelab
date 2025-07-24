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
from fastapi import UploadFile, Form, File, Depends
from secrets import token_hex
import os
from fastapi.responses import JSONResponse
from typing import Annotated
from app.services.user import User

@userRouter.post('/signup', status_code=201)
async def registerUser(
    userService: Annotated[User, Depends(User)]
    , username: str = Form(...)
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

    await userService.createUser(username, password, newPicFileName)

    respJSON = {"username": username, "password": password, "picture": pictureFileName}

    print('user_routes.py.registerUser().username:', username)
    print('user_routes.py.registerUser().password:', password)
    print('user_routes.py.registerUser().pictureFileName:', pictureFileName)

    return JSONResponse(
        content=respJSON
        , status_code=201
    )

@userRouter.get('/login', status_code=200)
def sendLoginPage():
    return FileResponse('app/templates/signin.html')

from fastapi.security import OAuth2PasswordRequestForm

# 미들웨어를 이용한 토큰 만료시간 업데이트를 위한 코드
from datetime import timedelta

@userRouter.post('/login', status_code=200)
async def authenticateUser(
    signinUserInfo: Annotated[OAuth2PasswordRequestForm, Depends()]
    , userService: Annotated[User, Depends(User)]
):
    # verify user
    user = await userService.verifyUserByName(signinUserInfo.username, signinUserInfo.password)

    # create a JWT
    if user:
        tokenPayload = {"id": user[0], "username": user[1], "picture": user[3], "last_login_at": user[4]}

        accessToken = userService.createAccessToken(tokenPayload)

        # # 미들웨어를 이용한 토큰 만료시간 업데이트를 위한 코드
        # accessToken = userService.createAccessToken(tokenPayload, duration=timedelta(seconds=20))
    else:
        accessToken = ''

    return {"access_token": accessToken, "token_type": 'bearer'}    # OAuth2 specification

@userRouter.get('/logout', status_code=200)
def logoutUser():
    return FileResponse('app/templates/logout.html')

from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

oauth2Scheme = OAuth2PasswordBearer(tokenUrl='/user/login')

class Passwordinfo(BaseModel):
    password: str

@userRouter.post('/verifyuser', status_code=200)
async def verifyUser(
    token: Annotated[str, Depends(oauth2Scheme)]
    , passwordinfo: Passwordinfo
    , userService: Annotated[User, Depends(User)]
): 
    tokenInfo = userService.decodeAccessToken(token)
    userId = tokenInfo["id"]

    userInfo = await userService.verifyUserById(userId, passwordinfo.password)

    if userInfo is not None:
        jsonResp = {"success": True, "content": ''}
    else:
        jsonResp = {"success": False, "content": ''}

    return JSONResponse(
        content=jsonResp
        , status_code=200
    )

@userRouter.post('/updateinfo', status_code=200)
async def updateUserinfo(
    token: Annotated[str, Depends(oauth2Scheme)]
    , userinfo: Passwordinfo
    , userService: Annotated[User, Depends(User)]
):
    tokenInfo = userService.decodeAccessToken(token)

    result = await userService.updateUserinfo(userinfo.password, tokenInfo["id"])

    if result is not None:
        jsonResp = {"success": True, "content": ''}
    else:
        jsonResp = {"success": False, "content": ''}

    return JSONResponse(
        content=jsonResp
        , status_code=200
    )

@userRouter.get('/updateinfo', status_code=200)
def sendUpdateUserinfoPage():
    return FileResponse('app/templates/update_userinfo.html')

@userRouter.get('/profilepic', status_code=200)
def sendProfilePicPage():
    return FileResponse('app/templates/get_profile_pic.html')

from fastapi.requests import Request

@userRouter.post('/profilepic', status_code=200)
async def sendProfilePicUrl(
    token: Annotated[str, Depends(oauth2Scheme)]
    , userService: Annotated[User, Depends(User)]
    , request: Request
    ):
    print('user_routes.py.sendProfilePicUrl.token:', token)

    tokenInfo = userService.decodeAccessToken(token)
    
    print('user_routes.py.sendProfilePicUrl.tokenInfo:', tokenInfo)

    fileName = tokenInfo["picture"]

    imageURL = request.url_for('profile-pic', path=fileName)    # alias name, additional path
    print('user_routes.py.sendProfilePicUrl.imageURL:', imageURL)

    return JSONResponse(content={"profile_pic_url": str(imageURL)})

@userRouter.get('/resetpw', status_code=200)
def sendResetPwPage():
    return FileResponse('app/templates/resetpw.html')

from app.utils.mail import sendMail
# from fastapi import BackgroundTasks

# class EmailAddress(BaseModel):
#     email: str

# @userRouter.post('/resetpw', status_code=200)
# async def resetAndSendPw(
#     emailAddress: EmailAddress
#     , userService: Annotated[User, Depends(User)]
#     , bgTask: BackgroundTasks
# ):
#     # 1. get email address
#     email = emailAddress.email
#     print("user_routes.py.resetAndSendPw().email:", email)

#     # 2. verify email address
#     userinfo = await userService.getUserinfoByUsername(email)

#     print("user_routes.py.resetAndSendPw().userinfo:", userinfo)

#     if userinfo is not None:
#     # 3. generate a temporary password
#         tempPW = await userService.generateTemporaryPassword(userinfo[0]) 

#         print("user_routes.py.resetAndSendPw().tempPW", tempPW)

#     # 4. send the temporary password via email
#         title = "임시 패스워드"
#         message = """
#         임시 패스워드: {}
#         """.format(tempPW)

#     # 4-a. using blocking method
#         # sendMail("your_mail_account@gmail.com", email, title, message)

#     # 4-b. using FastAPI's BackgroundTasks component
#         print("send email using FastAPI's BackgroundTasks.")
#         bgTask.add_task(sendMail, "your_mail_account@gmail.com", email, title, message)

#         jsonResp = {"success": True, "content": ''}

#         return JSONResponse(
#             content=jsonResp
#             , status_code=200
#         )
#     else: # no corresponding user
#         jsonResp = {"success": False, "content": ''}

#         return JSONResponse(
#             content=jsonResp
#             , status_code=200
#         )

from app.utils.messaging import SendEmailCeleryTask

class EmailAddress(BaseModel):
    email: str

@userRouter.post('/resetpw', status_code=200)
async def resetAndSendPw(
    emailAddress: EmailAddress
    , userService: Annotated[User, Depends(User)]
    # , bgTask: BackgroundTasks
):
    # 1. get email address
    email = emailAddress.email
    print("user_routes.py.resetAndSendPw().email:", email)

    # 2. verify email address
    userinfo = await userService.getUserinfoByUsername(email)

    print("user_routes.py.resetAndSendPw().userinfo:", userinfo)

    if userinfo is not None:
    # 3. generate a temporary password
        tempPW = await userService.generateTemporaryPassword(userinfo[0]) 

        print("user_routes.py.resetAndSendPw().tempPW", tempPW)

    # 4. send the temporary password via email
        title = "임시 패스워드"
        message = """
        임시 패스워드: {}
        """.format(tempPW)

    # 4-a. using blocking method
        # sendMail("your_mail_account@gmail.com", email, title, message)

    # 4-b. using FastAPI's BackgroundTasks component
        # print("send email using FastAPI's BackgroundTasks.")
        # bgTask.add_task(sendMail, "your_mail_account@gmail.com", email, title, message)

    # 4-c. using Celery and RabbitMQ
        print("send email using Celery and RabbitMQ.")
        task = SendEmailCeleryTask().delay("your_mail_account@gmail.com", email, title, message)
        result = task.get()
        print("Celery task result:", result)

        jsonResp = {"success": True, "content": ''}

        return JSONResponse(
            content=jsonResp
            , status_code=200
        )
    else: # no corresponding user
        jsonResp = {"success": False, "content": ''}

        return JSONResponse(
            content=jsonResp
            , status_code=200
        )
