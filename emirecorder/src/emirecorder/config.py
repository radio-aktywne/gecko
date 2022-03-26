import os

from pydantic import BaseModel


class Config(BaseModel):
    port: int = os.getenv("EMIRECORDER_PORT", 31000)
    target_host: str = os.getenv("EMIRECORDER_TARGET_HOST", "localhost")
    target_port: int = os.getenv("EMIRECORDER_TARGET_PORT", 30000)
    target_user: str = os.getenv("EMIRECORDER_TARGET_USER", "readwrite")
    target_password: str = os.getenv("EMIRECORDER_TARGET_PASSWORD", "password")


config = Config()
