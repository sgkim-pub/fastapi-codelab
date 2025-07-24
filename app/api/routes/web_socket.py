from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse

WSRouter = APIRouter(prefix='/ws')

@WSRouter.get('')
def sendTestPage():
    return FileResponse('app/templates/web_socket_test.html')

@WSRouter.websocket('')
async def echoWS(wsock: WebSocket):
    await wsock.accept()
    await wsock.send_text('Server: {}'.format('ready to receive message.'))

    print('web_socket.py.echoWS().wsock.state:', wsock.client_state)

    try:
        while True:
            data = await wsock.receive_text()
            await wsock.send_text('echo: {}'.format(data))
    except WebSocketDisconnect:
        print('web_socket.py.echoWS().wsock.state:', wsock.client_state)
        print('web_socket.py.echoWS():', 'web socket closed.')
