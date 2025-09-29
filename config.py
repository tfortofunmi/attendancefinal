import os
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(BaseSettings):
    SECRET_KEY: str = 'your-secret-key'
    SQLALCHEMY_DATABASE_URI: str = f'sqlite:///{os.path.join(basedir, 'instance/attendance.db')}'
    SQLALCHEMY_TRACK_MODIFICATIONS: Optional[bool] = False
    model_config = SettingsConfigDict(env_file=".env", extra='ignore')

config = Config()
