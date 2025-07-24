from datetime import datetime, timezone, timedelta

from fastapi import Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt

from app import appCfg

# JWT 토큰의 만료시간을 확인하고 만료시간이 연장된 토큰을 생성하는 함수
def checkAndRefreshJWT(token, duration=timedelta(hours=1)):
    try:
        # 토큰의 만료시간 확인
        payload = jwt.decode(token, appCfg.JWT_SECRET, algorithms=appCfg.JWT_ALGORITHM, options={"verify_exp": True})
        print('middleware.py.checkAndRefreshJWT().decodedToken:{}'.format(payload))
        
        # Unix timestamp를 datetime 객체로 변환하여 표시
        original_exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        print('middleware.py.checkAndRefreshJWT().tokenExpTime:{}'.format(original_exp))
        
        # 새 만료시간 설정
        expire = datetime.now(timezone.utc) + duration
        payload.update({"exp": expire}) # update "exp" field
        print('middleware.py.checkAndRefreshJWT().tokenExpTime(updated):{}\n'.format(payload["exp"]))

        # 새 토큰 생성
        newToken = jwt.encode(payload, appCfg.JWT_SECRET, algorithm=appCfg.JWT_ALGORITHM)

    except jwt.ExpiredSignatureError:
	# 만료시간이 지난 토큰의 경우 새 토큰을 전달하지 않는다.
        payload = jwt.decode(token, appCfg.JWT_SECRET, algorithms=appCfg.JWT_ALGORITHM, options={"verify_exp": False})  # for debugging
        print('middleware.py.checkAndRefreshJWT().decodedToken(expired):{}\n'.format(payload))    # for debugging
        newToken = None

    return newToken

oauth2Scheme = OAuth2PasswordBearer(tokenUrl='/user/login')

# JWT 토큰이 있는 경우 토큰의 유효기간을 처리하는 미들웨어 함수
async def refreshTokenTime(request: Request, call_next):
    print('middleware.py.refreshTokenTime().request.headers:{}'.format(request.headers))

    # JWT 토큰이 있는 경우
    if 'authorization' in request.headers:
        # FastAPI에서 제공하는 OAuth2PasswordBearer 클래스를 이용해 인증토큰을 얻는다.
        token = await oauth2Scheme(request)
        print('middleware.py.refreshTokenTime().request.headers.token:{}'.format(token))

	# 사용자의 요청에 따른 서비스 제공 및 응답 생성
        response = await call_next(request)
    
        print('middleware.py.refreshTokenTime().response.headers(1):{}'.format(response.headers))

        # 토큰의 유효기간을 확인하고 유효한 토큰의 경우 유효기간을 연장한다.
        token = checkAndRefreshJWT(token, duration=timedelta(seconds=20))

        # 유효기간이 연장된 토큰이 생성된 경우
        if token is not None:
            response.headers["access_token"] = token
            response.headers["token_type"] = 'bearer'
        # 토큰의 유효기간이 지난 경우 응답에 새 토큰을 포함시키지 않는다. 클라이언트가 가진 기존 토큰은 유효기간이 지났으므로 사용할 수 없다.
        else:
            pass    # front-end code can do auto logout if no access_token in response.
    # JWT 토큰이 없는 경우 - 로그인 이전
    else:
        response = await call_next(request)

    print('middleware.py.refreshTokenTime().response.headers(2):{}\n'.format(response.headers))

    # 응답을 전달한다.
    return response
