from emirecorder.config.base import BaseConfig


class Config(BaseConfig):
    host: str = "0.0.0.0"
    port: int = 31000
    target_host: str = "localhost"
    target_port: int = 30000
    target_user: str = "readwrite"
    target_password: str = "password"
    target_bucket: str = "live-recordings"
    timeout: int = 60
