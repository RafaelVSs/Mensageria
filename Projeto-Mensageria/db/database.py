from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base 
from core.config import settings


DB_USER = settings.DB_USER
DB_PASSWORD = settings.DB_PASSWORD
DB_NAME = settings.DB_NAME
DB_HOST = settings.DB_HOST
DB_PORT = settings.DB_PORT


SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"



engine = create_async_engine(SQLALCHEMY_DATABASE_URL)


AsyncSessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False,  
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False 
                           
)


Base = declarative_base()


async def get_db() -> AsyncSession: 
    async with AsyncSessionLocal() as db:
        try:
            yield db
        finally:
            await db.close() 


print(f"Conectando ao banco (config): postgresql+asyncpg://{DB_USER}:********@{DB_HOST}:{DB_PORT}/{DB_NAME}")
