from datetime import datetime

from app.utils.db import loadQuery
from app.utils.crypto import encrypt, verify
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt

class User():
    def __init__(self):
        from app import pool

        self.pool = pool

        from app import appCfg

        self.SECRET_KEY = appCfg.JWT_SECRET
        self.ALGORITHM = appCfg.JWT_ALGORITHM

    async def createUser(self, username, password, picFileName):
        encryptedPW = encrypt(password)

        query = loadQuery('create_user.sql')

        currentTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        print('user.py.User.createUser.query:', query)

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, (username, encryptedPW, picFileName, 0, currentTime))
            
            await conn.commit()

    async def verifyUserByName(self, username, password):
        query = loadQuery('get_userinfo_by_username.sql')

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, (username, ))
                userinfo = await cur.fetchone()

        print('user.py.User.verifyUser().userinfo:', userinfo)  # (id, username, password, last_login_at)

        if userinfo:
            check = verify(password, userinfo[2])
        else:
            check = False

        print('user.py.User.verifyUser().check:', check)

        if check:
            return userinfo
        else:
            return None

    # payload: {"id": '...', "username": '...', "picture": '...', "last_login_at": '...'}
    def createAccessToken(self, payload, duration=timedelta(hours=1)):
        expire = datetime.now(timezone.utc) + duration
        payload.update({"exp": expire}) # append "exp" field

        # payload: {"id": '...', "username": '...', "picture": '...', "last_login_at": '...', "exp": '...'}
        accessToken = jwt.encode(payload, self.SECRET_KEY, algorithm=self.ALGORITHM)

        return accessToken

    def decodeAccessToken(self, token):
        try:
            return jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
        except JWTError:
            return None
