import colorsys
from pydantic import BaseModel


class RGBColor(BaseModel):
    red: float
    green: float
    blue: float

    def to_gpio_rgb_led_colors(self):
        return (self.red, self.green, self.blue)

    def to_lifx_colors(self, brightness: int):
        h, s = [
            color * 65535
            for color in colorsys.rgb_to_hsv(self.red, self.green, self.blue)[:2]
        ]
        return (h, s, brightness, 3500)


def from_event_summary(summary: str, default_color: RGBColor):
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
    return default_color
