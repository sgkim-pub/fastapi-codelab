from fastapi import APIRouter
from fastapi.responses import JSONResponse

pathQueryRouter = APIRouter(prefix='/item')

# # path parameter 방식으로 데이터를 받는 경우
# @pathQueryRouter.get('/product/{itemId}')
# def getPathParam(itemId: str):
#     print('path_query_router.py.getPathParam().itemId:', itemId)

#     respJSON = {"itemId": itemId}

#     return JSONResponse(
#         content=respJSON
#         , status_code=200
#     )

# path parameter 방식으로 데이터를 받는 경우 - 파이썬 Annotated 이용
from fastapi import Path
from typing import Annotated

@pathQueryRouter.get('/product/{itemId}')
def getPathParam(itemId: Annotated[str, Path(...)]):
    print('path_query_router.py.getPathParam().itemId:', itemId)

    respJSON = {"itemId": itemId}

    return JSONResponse(
        content=respJSON
        , status_code=200
    )

# # query string 방식으로 데이터를 받는 경우
# from fastapi import Query

# @pathQueryRouter.get('/product')
# def getQueryStrings(
#     itemCategory: str = Query(None)
#     , itemId: str = Query(...)
# ):
#     print('path_query_routes.py.getQueryStrings().itemCategory:', itemCategory)
#     print('path_query_routes.py.getQueryStrings().itemId:', itemId)

#     respJSON = {"itemCategory": itemCategory, "itemId": itemId}

#     return JSONResponse(
#         content=respJSON
#         , status_code=200
#     )

# query string 방식으로 데이터를 받는 경우 - 파이썬 Annotated 이용
from fastapi import Query

@pathQueryRouter.get('/product')
def getQueryStrings(
    itemId: Annotated[str, Query()]
    , itemCategory: Annotated[str|None, Query()] = None
):
    print('path_query_routes.py.getQueryStrings().itemCategory:', itemCategory)
    print('path_query_routes.py.getQueryStrings().itemId:', itemId)

    respJSON = {"itemCategory": itemCategory, "itemId": itemId}

    return JSONResponse(
        content=respJSON
        , status_code=200
    )

