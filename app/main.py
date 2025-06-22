import asyncio
import os

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from sqlalchemy import select, func
from .db import init_db, async_session
from .models import Transfer
from .indexer import run_indexer


app = FastAPI(title="Python Web3 Indexer")
Instrumentator().instrument(app).expose(app)

stop_event = asyncio.Event()
indexer_task: asyncio.Task | None = None


@app.on_event("startup")
async def startup():
    global indexer_task
    await init_db()
    loop = asyncio.get_event_loop()
    indexer_task = loop.create_task(run_indexer(stop_event))


@app.on_event("shutdown")
async def shutdown():
    stop_event.set()
    if indexer_task:
        await indexer_task


@app.get("/healthz")
async def health():
    async with async_session() as session:
        # build a proper count(*) query
        stmt = select(func.count()).select_from(Transfer)
        result = await session.execute(stmt)
        total = result.scalar_one()
    return {"ok": True, "events_collected": total}
