from app.lib.color import RGBColor
from app.lib.output_device import OutputDevice
from lifxlan import Light  # type: ignore


class LifxOutputDevice(OutputDevice):
    _light: Light

    def __init__(self, mac_address: str, ip_address: str):
        self._light = Light(mac_addr=mac_address, ip_addr=ip_address)

    def on(self, color: RGBColor):
        print(color.to_lifx_colors())
        self._light.set_power(power="on", rapid=True)  # type: ignore
        self._light.set_color(color=color.to_lifx_colors())  # type: ignore

    def off(self):
        self._light.set_power("off", rapid=True)  # type: ignore
