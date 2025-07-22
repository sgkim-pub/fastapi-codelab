from fastapi import FastAPI
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app):
    print('Starting FastAPI app.')
    yield
    print('Stopping FastAPI app.')

app = FastAPI(lifespan=lifespan)

from app.api.routes.home_routes import homeRouter
app.include_router(homeRouter)
