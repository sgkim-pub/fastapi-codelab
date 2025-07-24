from datetime import datetime

from app.utils.db import loadQuery
from app.utils.crypto import encrypt, verify
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt

import secrets

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

    async def verifyUserById(self, id, password):
        query = loadQuery("get_userinfo_by_id.sql")

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, (id))
                userinfo = await cur.fetchone()

                if userinfo:
                    check = verify(password, userinfo[2]) 
                else:
                    check = False               

                if check:
                    result = userinfo
                else:
                    result = None

        return result
    
    async def updateUserinfo(self, password, id):
    
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                query = loadQuery('get_userinfo_by_id.sql')
    
                await cur.execute(query, (id))
                userinfo = cur.fetchone()
    
                if userinfo is None:    # no user with given id
                    result = None
                else:
                    baseQuery = loadQuery('update_userinfo_by_id.sql')
    
                    updates = []
                    params = []
    
                    if len(password) > 0:
                        updates.append('`password`=%s')
                        epw = encrypt(password)
                        params.append(epw)
                    else:
                        pass
                    
                    if len(updates) > 0:
                        query = baseQuery + ' ' + ', '.join(updates) + ' WHERE `id`=%s'
    
                        params.append(id)
    
                        await cur.execute(query, tuple(params))
                        await conn.commit() # do not forget 'await'
    
                        query = loadQuery('get_userinfo_by_id.sql')
    
                        await cur.execute(query, (id))
                        userinfo = await cur.fetchone()   # userinfo = (...)
    
                        result = {"id": userinfo[0], "username": userinfo[1], "picture": userinfo[3], "last_login_at": userinfo[4]}
                    else:
                        result = None
    
        return result
    
    async def generateTemporaryPassword(self, userId):
        tempPW = secrets.token_hex(4)   # 4 bytes. 8 characters.
        encryptedPW = encrypt(tempPW)
    
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                baseQuery = loadQuery("update_userinfo_by_id.sql")
    
                query = baseQuery + " " + "`password`=%s" + " WHERE `id`=%s"
    
                await cur.execute(query, (encryptedPW, userId))
                await conn.commit()
    
        return tempPW

    async def getUserinfoByUsername(self, username):
        query = loadQuery("get_userinfo_by_username.sql")

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, (username))
                userinfo = await cur.fetchone()

        # (id, username, password, picture, last_login_at)
        return userinfo