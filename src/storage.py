import secrets

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models import ShortURL


class URLStorage:
    """Storage for managing shortened URLs in database.

    Provides methods to create and retrieve shortened URLs using async SQLAlchemy session.
    """
    def __init__(self, session: AsyncSession):
        """Initialize URLStorage with async database session.

        Args:
            session: Async SQLAlchemy session for database operations
        """
        self.session = session

    async def shorten(self, original_url: str) -> str:
        """Creates or retrieves existing shortened URL for the given original URL.

        Args:
            original_url: The original URL to be shortened

        Returns:
            str: The generated or existing short identifier
        """

       # Check if URL already exists
        query = select(ShortURL).where(ShortURL.original_url == original_url)
        result = await self.session.execute(query)
        existing = result.scalar_one_or_none()

        if existing:
            return existing.short_id

        # Генерация уникального short_id
        while True:
            short_id = secrets.token_urlsafe(6)[:8]  # 8-значный URL-safe token

            query = select(ShortURL).where(ShortURL.short_id == short_id)
            result = await self.session.execute(query)
            if not result.scalar_one_or_none():
                break

        # Create new short URL
        new_url = ShortURL(
            original_url=str(original_url),
            short_id=short_id
        )
        self.session.add(new_url)
        await self.session.commit()

        return short_id

    async def get_original(self, short_id: str) -> str | None:
        """Retrieves original URL for the given short identifier.

        Args:
            short_id: The short identifier to look up

        Returns:
            str: The original URL or None
        """
        query = select(ShortURL.original_url).where(ShortURL.short_id == short_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()