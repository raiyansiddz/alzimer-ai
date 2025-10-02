"""
Database initialization script for Dementia Detection System
Creates all necessary tables and indexes for PostgreSQL
"""

from core.database.connection import engine, test_connection, text
from core.database.models import Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_all_tables():
    """Create all database tables"""
    try:
        # Test connection first
        if not test_connection():
            raise Exception("Database connection failed")
            
        logger.info("Creating database tables...")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        logger.info("All tables created successfully!")
        
        # Create additional indexes for better performance
        with engine.connect() as conn:
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);",
                "CREATE INDEX IF NOT EXISTS idx_test_sessions_user_id ON test_sessions(user_id);",
                "CREATE INDEX IF NOT EXISTS idx_test_sessions_started_at ON test_sessions(started_at);",
                "CREATE INDEX IF NOT EXISTS idx_test_results_session_id ON test_results(session_id);",
                "CREATE INDEX IF NOT EXISTS idx_test_results_test_name ON test_results(test_name);",
                "CREATE INDEX IF NOT EXISTS idx_reports_user_id ON reports(user_id);",
                "CREATE INDEX IF NOT EXISTS idx_progress_tracking_user_id ON progress_tracking(user_id);",
                "CREATE INDEX IF NOT EXISTS idx_progress_tracking_date ON progress_tracking(date);",
                "CREATE INDEX IF NOT EXISTS idx_reminders_user_id ON reminders(user_id);",
                "CREATE INDEX IF NOT EXISTS idx_llm_analysis_logs_test_result_id ON llm_analysis_logs(test_result_id);",
                "CREATE INDEX IF NOT EXISTS idx_audio_files_user_id ON audio_files(user_id);",
                "CREATE INDEX IF NOT EXISTS idx_image_files_user_id ON image_files(user_id);"
            ]
            
            for index_sql in indexes:
                try:
                    conn.execute(text(index_sql))
                except Exception as e:
                    logger.warning(f"Index creation warning: {e}")
            
            conn.commit()
            
        logger.info("Database indexes created successfully!")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise e

if __name__ == "__main__":
    create_all_tables()