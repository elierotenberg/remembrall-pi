from app.lib.color import RGBColor
from app.lib.output_device import OutputDevice
import lifxlan  # type: ignore
from lifxlan import Light  # type: ignore

INFINITE_CYCLES = 1000000

LOW_BRIGHTNESS = 0
HIGH_BRIGHTNESS = int(65535 / 2)

lifxlan.DEFAULT_ATTEMPTS = 5
lifxlan.DEFAULT_TIMEOUT = 5


class LifxOutputDevice(OutputDevice):
    _light: Light
    _brightness: int

    def __init__(self, mac_address: str, ip_address: str):
        self._light = Light(mac_addr=mac_address, ip_addr=ip_address)

    def on(self, color: RGBColor):
        self._light.set_power("off")  # type: ignore
        self._light.set_power("on")  # type: ignore
        self._light.set_color(color=color.to_lifx_colors(HIGH_BRIGHTNESS))  # type: ignore
        self._light.set_waveform(  # type: ignore
            is_transient=1,
            color=color.to_lifx_colors(LOW_BRIGHTNESS),
            period=2000,
            cycles=INFINITE_CYCLES,
            duty_cycle=0.5,
            waveform=1,
            rapid=True,
        )

    def off(self):
        self._light.set_power("off")  # type: ignore
