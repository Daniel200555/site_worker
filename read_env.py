
import os
from pathlib import Path
from dotenv import load_dotenv, set_key

class ReadEnv:
    def __init__(self):
        self.env_path = Path(__file__).resolve().parent / ".env"
        load_dotenv(self.env_path)
        self.sharepoint_host: str = os.getenv("SHAREPOINT_HOST")
        self.local_state_path: str = os.getenv("LOCAL_STATE_PATH")
        self.master_site_name: str = os.getenv("MASTER_SITE_NAME")
        self.master_lib_guid: str = os.getenv("MASTER_LIB_GUID")
        self.chat_url: str = os.getenv("CHAT_URL")
        self.chat_name = os.getenv("CHAT_ENV")
        self.s3_endpoint_url = os.getenv("S3_ENDPOINT_URL")
        self.s3_access_key_id = os.getenv("S3_ACCESS_KEY_ID")
        self.s3_secret_access_key = os.getenv("S3_SECRET_ACCESS_KEY")
        self.s3_bucket_name = os.getenv("S3_BUCKET_NAME")