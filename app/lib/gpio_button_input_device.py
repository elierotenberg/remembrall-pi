from typing import Callable
from gpiozero.input_devices import Button  # type: ignore
from gpiozero.pins.pigpio import PiGPIOFactory  # type: ignore
from app.lib.input_device import InputDevice


class GpioButtonInputDevice(InputDevice):
    _button: Button

    def __init__(self, pin_factory: PiGPIOFactory, pin: int):
        self._button = Button(pin=pin, pin_factory=pin_factory)

    def on_dismiss(self, on_dismiss: Callable[[], None]):
        self._button.when_activated = on_dismiss