from app import app
import uvicorn

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', reload=False, port=8000)
