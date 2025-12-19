from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os

# ВАЖНО: Внутри Docker 'localhost' — это сам контейнер приложения.
# Чтобы подключиться к соседнему контейнеру с базой, нужно использовать его имя: 'db-db-1'.
# Замените 'mysecretpassword' на тот пароль, который вы используете для базы.

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://admin:password@localhost:5432/lms_db"
)

# echo=True полезно для отладки (показывает SQL запросы в логах), в продакшене можно False
engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session