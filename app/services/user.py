from datetime import datetime

from app.utils.db import loadQuery
from app.utils.crypto import encrypt

class User():
    def __init__(self):
        from app import pool

        self.pool = pool

    async def createUser(self, username, password, picFileName):
        encryptedPW = encrypt(password)

        query = loadQuery('create_user.sql')

        currentTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        print('user.py.User.createUser.query:', query)

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, (username, encryptedPW, picFileName, 0, currentTime))
            
            await conn.commit()
