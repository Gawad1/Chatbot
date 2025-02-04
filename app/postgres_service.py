import psycopg2
from psycopg2 import sql
from .config import settings
import logging

logger = logging.getLogger(__name__)

class PostgresService:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname=settings.postgres_db,
            user=settings.postgres_user,
            password=settings.postgres_password,
            host=settings.postgres_host,
            port=settings.postgres_port
        )
        self.cursor = self.conn.cursor()
        logger.info("Postgres Service initialized")

    def flush_session(self, session_id: str, last_request_timestamp: str, flushed_timestamp: str, summary: str):
        try:
            insert_query = sql.SQL("""
                INSERT INTO chat_sessions (session_id, last_request_timestamp, flushed_timestamp, summary)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (session_id) DO UPDATE SET
                last_request_timestamp = EXCLUDED.last_request_timestamp,
                flushed_timestamp = EXCLUDED.flushed_timestamp,
                summary = EXCLUDED.summary
            """)
            self.cursor.execute(insert_query, (session_id, last_request_timestamp, flushed_timestamp, summary))
            self.conn.commit()
            logger.info(f"Flushed session {session_id} to Postgres")
        except Exception as e:
            logger.error(f"Error flushing session to Postgres: {e}")
            self.conn.rollback()

postgres_service = PostgresService()