from fastapi import FastAPI

app = FastAPI()

@app.get('/')
def sayHello():
    return {"message": 'Hello, FastAPI!'}

import uvicorn

if __name__ == '__main__':
    uvicorn.run('hello_fastapi:app', host='0.0.0.0', reload=False, port=8000)
