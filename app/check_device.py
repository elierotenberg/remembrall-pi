from asyncio import get_event_loop
from time import sleep
from signal import pause
from gpiozero.input_devices import Button
from gpiozero.output_devices import RGBLED
from gpiozero.pins.pigpio import PiGPIOFactory
from os import environ
from app.lib.remembrall_device import RemembrallDevice

PIGPIO_ADDR = environ.get("PIGPIO_ADDR")

if __name__ == "__main__":
    pin_factory = PiGPIOFactory(PIGPIO_ADDR)
    rgb_led = RGBLED(red=8, green=24, blue=18, pin_factory=pin_factory)
    button = Button(21, pin_factory=pin_factory)
    device = RemembrallDevice(rgb_led=rgb_led, button=button)
    loop = get_event_loop()
    device.start()
    print("started")
    print("red")
    device.color(1, 0, 0)
    sleep(3)
    print("green")
    device.color(0, 1, 0)
    sleep(3)
    print("blue")
    device.color(0, 0, 1)
    sleep(3)
    print("all")
    device.color(1, 1, 1)
    pause()