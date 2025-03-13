import redis
import aiomysql
from app.config.default import DEFAULT_CONFIG
from sqlalchemy import create_engine, Column, Integer, String, Text, Enum, TIMESTAMP, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

mysql_config = DEFAULT_CONFIG["mysql_config"]["connections"]["default"]["credentials"]

DATABASE_URL = f"mysql+pymysql://{mysql_config["user"]}:{mysql_config["password"]}@{mysql_config["host"]}/{mysql_config["database"]}"  # 替换为你的 MySQL 连接信息

engine = create_engine(DATABASE_URL, echo=True)  # echo=True 可查看 SQL 语句
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_redis() -> redis.StrictRedis:
    from app import app_config #延迟引入，避免循环引用
    redis_config = app_config.redis_config
    redis_host = redis_config["host"]
    redis_password = redis_config["password"]
    redis_db = redis_config["db"]
    redis_port = redis_config["port"]
    redis_conn = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db, password=redis_password, decode_responses=True)
    return redis_conn

async def get_db():
    pool = await aiomysql.create_pool(
        host=mysql_config["host"], port=mysql_config["port"], user=mysql_config["user"],
        password=mysql_config["password"], db=mysql_config["database"], charset='utf8mb4', autocommit=True
    )
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            yield cur