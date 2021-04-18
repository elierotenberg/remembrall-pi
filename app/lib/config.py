from os import environ, path, getcwd
from pydantic import BaseModel
from toml import load


class GoogleConfig(BaseModel):
    oauth_flask_secret_key: str
    oauth_secrets: str
    tokens: str
    calendar_id: str


class DeviceConfig(BaseModel):
    pigpio_addr: str
    red_pin: int
    green_pin: int
    blue_pin: int
    button_pin: int


class ControllerConfig(BaseModel):
    poll_interval_minutes: int


class Config(BaseModel):
    google: GoogleConfig
    device: DeviceConfig
    controller: ControllerConfig


def read_from_env():
    config_file_env = environ.get("CONFIG_FILE")
    if config_file_env is None:
        raise TypeError("CONFIG_FILE env is not set")
    return Config(**load(path.join(getcwd(), config_file_env)))