from gpiozero.output_devices import RGBLED  # type: ignore
from gpiozero.pins.pigpio import PiGPIOFactory  # type: ignore
from app.lib.output_device import OutputDevice
from app.lib.color import RGBColor


class GpioRgbLedOutputDevice(OutputDevice):
    _led: RGBLED

    def __init__(
        self, pin_factory: PiGPIOFactory, red_pin: int, green_pin: int, blue_pin: int
    ):
        self._led = RGBLED(
            red=red_pin, green=green_pin, blue=blue_pin, pin_factory=pin_factory
        )

    def on(self, color: RGBColor):
        self._led.blink(  # type: ignore
            on_time=1,
            off_time=1,
            on_color=color.to_gpio_rgb_led_colors(),
            background=True,
        )

    def off(self):
        self._led.off()