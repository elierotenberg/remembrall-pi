import colorsys
from pydantic import BaseModel


def from_event_summary(summary: str):
    if summary.startswith("R"):
        return RGBColor(red=1, green=0, blue=0)
    if summary.startswith("G"):
        return RGBColor(red=0, green=1, blue=0)
    if summary.startswith("B"):
        return RGBColor(red=0, green=0, blue=1)
    if summary.startswith("#"):
        parts = summary.partition(" ")
        hex = parts[0].lstrip("#")
        hlen = len(hex)
        red, green, blue = tuple(
            int(hex[i : i + hlen // 3], 16) for i in range(0, hlen, hlen // 3)
        )
        return RGBColor(red=red / 255, green=green / 255, blue=blue / 255)
    return RGBColor(red=1, blue=1, green=1)


class RGBColor(BaseModel):
    red: float
    green: float
    blue: float

    def to_gpio_rgb_led_colors(self):
        return (self.red, self.green, self.blue)

    def to_lifx_colors(self):
        h, s, v = colorsys.rgb_to_hsv(self.red, self.green, self.blue)
        return ((h * 65535), (s * 65535), (v * 65535), 3500)