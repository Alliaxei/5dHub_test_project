from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from starlette.responses import RedirectResponse
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
import httpx
import uvicorn

from src.schemas import UrlRequest
from src.storage import URLStorage
from src.models import Base

DATABASE_URL = 'sqlite+aiosqlite:///./shortener.db'


engine = create_async_engine(DATABASE_URL)
async_session = async_sessionmaker(engine, expire_on_commit=False) # Создание фабрики сессий


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Async context manager for FastAPI application lifespan events.

    Creates database, tables on application startup.

    Args:
        app (FastAPI): The FastAPI application instance
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="URL Shortener",
    description="API for URL shortening",
    lifespan=lifespan
)


@app.post("/", status_code=201)
async def shorten_url(url_data: UrlRequest) -> dict:
    """Creates a shortened URL from the provided original URL.

    Args:
        url_data (UrlRequest): Contains the original URL to be shortened

    Returns:
        dict: Dictionary containing the shortened URL

    Raises:
        HTTPException: 500 status code if any server error occurs
    """
    async with async_session() as session:
        try:
            storage = URLStorage(session)
            short_id = await storage.shorten(str(url_data.url))
            return {"short_url": f"http://127.0.0.1:8000/{short_id}"}
        except Exception:
            raise HTTPException(
                status_code=500,
                detail="Internal server error occurred"
            )


@app.get("/{short_id}")
async def redirect_to_original(short_id: str) -> RedirectResponse:
    """Redirects to the original URL associated with the short identifier.

    Args:
        short_id (str): The short URL identifier

    Returns:
        RedirectResponse: 307 redirect response to the original URL

    Raises:
        HTTPException: 404 status code if the short URL is not found
    """
    async with async_session() as session:
        storage = URLStorage(session)
        original_url = await storage.get_original(short_id)
        if not original_url:
            raise HTTPException(status_code=404, detail="URL not found")
        return RedirectResponse(original_url, status_code=307)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True)
