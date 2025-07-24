from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.app_config import AppConfig

appCfg = AppConfig('config.json')

import aiomysql

pool = None

async def createConnectionPool(host, portNum, username, password, dbname, minPoolsize, maxPoolsize):
    global pool

    pool = await aiomysql.create_pool(
        host=host
        , port=portNum
        , user=username
        , password=password
        , db=dbname
        , minsize=minPoolsize
        , maxsize=maxPoolsize
    )

async def deleteConnectionPool():
    global pool

    if pool:
        pool.close()
        await pool.wait_closed()
        pool = None


# 참고 - 풀(pool)이 아닌, 하나의 연결만 사용하는 경우
conn = None

async def connectToDB(host, portNum, username, password, dbname):
    global conn

    conn = await aiomysql.connect(
        host=host
        , port=portNum
        , user=username
        , password=password
        , db=dbname
    )

async def disconnectFromDB():
    global conn

    if conn:
        conn.close()
        await conn.ensure_closed()
        conn = None

@asynccontextmanager
async def lifespan(app):
    print('Starting FastAPI app.')
    await createConnectionPool('localhost', 3306, appCfg.DB_USER, appCfg.DB_PASSWORD, appCfg.DB, 1, 10)
    yield
    print('Stopping FastAPI app.')
    await deleteConnectionPool()

app = FastAPI(lifespan=lifespan)

from fastapi.staticfiles import StaticFiles
app.mount('/static/profile/pic', StaticFiles(directory='app/upload/user_profile'), name='profile-pic')

from app.services.middleware import refreshTokenTime
app.middleware('http')(refreshTokenTime)

from app.api.routes.home_routes import homeRouter
app.include_router(homeRouter)

from app.api.routes.user_routes import userRouter
app.include_router(userRouter)

from app.api.routes.path_query_routes import pathQueryRouter
app.include_router(pathQueryRouter)
