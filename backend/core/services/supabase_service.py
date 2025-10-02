from supabase import create_client, Client
from config.settings import settings
import logging
from typing import Optional, Dict, Any
import uuid

logger = logging.getLogger(__name__)

class SupabaseService:
    def __init__(self):
        try:
            if settings.SUPABASE_URL and settings.SUPABASE_KEY:
                # Initialize Supabase client without problematic options
                self.supabase: Client = create_client(
                    settings.SUPABASE_URL, 
                    settings.SUPABASE_KEY
                )
                self.storage_bucket = settings.SUPABASE_STORAGE_BUCKET
                logger.info("Supabase client initialized successfully")
            else:
                logger.warning("Supabase credentials not provided, service disabled")
                self.supabase = None
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            self.supabase = None
        
    async def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with email and password"""
        if not self.supabase:
            logger.error("Supabase client not initialized")
            return None
        try:
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            return response
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return None
    
    async def register_user(self, email: str, password: str, metadata: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Register new user with email and password"""
        if not self.supabase:
            logger.error("Supabase client not initialized")
            return None
        try:
            response = self.supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": metadata or {}
                }
            })
            return response
        except Exception as e:
            logger.error(f"Registration failed: {e}")
            return None
    
    async def authenticate_with_google(self) -> Dict[str, Any]:
        """Authenticate with Google OAuth"""
        if not self.supabase:
            logger.error("Supabase client not initialized")
            return {"error": "Service unavailable"}
        try:
            response = self.supabase.auth.sign_in_with_oauth({
                "provider": "google",
                "options": {
                    "redirect_to": "http://localhost:3000/dashboard"
                }
            })
            return response
        except Exception as e:
            logger.error(f"Google authentication failed: {e}")
            return {"error": str(e)}
    
    async def upload_audio_file(self, file_content: bytes, file_name: str, user_id: str) -> Optional[str]:
        """Upload audio file to Supabase Storage"""
        if not self.supabase:
            logger.error("Supabase client not initialized")
            return None
        try:
            # Create unique filename
            unique_filename = f"audio/{user_id}/{uuid.uuid4()}_{file_name}"
            
            response = self.supabase.storage.from_(self.storage_bucket).upload(
                unique_filename, 
                file_content,
                {"content-type": "audio/mpeg"}
            )
            
            if response:
                # Get public URL
                public_url = self.supabase.storage.from_(self.storage_bucket).get_public_url(unique_filename)
                return public_url
            return None
            
        except Exception as e:
            logger.error(f"Audio file upload failed: {e}")
            return None
    
    async def upload_image_file(self, file_content: bytes, file_name: str, user_id: str) -> Optional[str]:
        """Upload image file to Supabase Storage"""
        if not self.supabase:
            logger.error("Supabase client not initialized")
            return None
        try:
            # Create unique filename
            unique_filename = f"images/{user_id}/{uuid.uuid4()}_{file_name}"
            
            response = self.supabase.storage.from_(self.storage_bucket).upload(
                unique_filename, 
                file_content,
                {"content-type": "image/jpeg"}
            )
            
            if response:
                # Get public URL
                public_url = self.supabase.storage.from_(self.storage_bucket).get_public_url(unique_filename)
                return public_url
            return None
            
        except Exception as e:
            logger.error(f"Image file upload failed: {e}")
            return None
    
    async def upload_report_file(self, file_content: bytes, file_name: str, user_id: str) -> Optional[str]:
        """Upload PDF report to Supabase Storage"""
        if not self.supabase:
            logger.error("Supabase client not initialized")
            return None
        try:
            # Create unique filename
            unique_filename = f"reports/{user_id}/{uuid.uuid4()}_{file_name}"
            
            response = self.supabase.storage.from_(self.storage_bucket).upload(
                unique_filename, 
                file_content,
                {"content-type": "application/pdf"}
            )
            
            if response:
                # Get public URL
                public_url = self.supabase.storage.from_(self.storage_bucket).get_public_url(unique_filename)
                return public_url
            return None
            
        except Exception as e:
            logger.error(f"Report file upload failed: {e}")
            return None
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete file from Supabase Storage"""
        if not self.supabase:
            logger.error("Supabase client not initialized")
            return False
        try:
            self.supabase.storage.from_(self.storage_bucket).remove([file_path])
            return True
        except Exception as e:
            logger.error(f"File deletion failed: {e}")
            return False

# Global instance
supabase_service = SupabaseService()