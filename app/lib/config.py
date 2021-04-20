from app.lib.color import RGBColor
from os import environ, path, getcwd
from pydantic import BaseModel
from toml import load


class GoogleConfig(BaseModel):
    oauth_flask_secret_key: str
    oauth_secrets: str
    tokens: str
    calendar_id: str


class RaspberryConfig(BaseModel):
    pigpio_addr: str
    red_pin: int
    green_pin: int
    blue_pin: int
    button_pin: int
    status_pin: int


class LifxConfig(BaseModel):
    mac_address: str
    ip_address: str


class ControllerConfig(BaseModel):
    use_lifx_output: bool
    use_rgb_led_output: bool
    default_color: RGBColor
    sleep_interval_seconds: int
    poll_interval_seconds: int
    poll_interval_minutes: int


class Config(BaseModel):
    google: GoogleConfig
    raspberry: RaspberryConfig
    lifx: LifxConfig
    controller: ControllerConfig
    debug: bool


def read_from_env():
    config_file_env = environ.get("CONFIG_FILE")
    if config_file_env is None:
        raise TypeError("CONFIG_FILE env is not set")
    return Config(**load(path.join(getcwd(), config_file_env)))