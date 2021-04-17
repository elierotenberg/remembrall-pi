from asyncio import get_event_loop
from gpiozero.input_devices import Button
from .lib.remembrall_device import RemembrallDevice
from gpiozero import LED
from gpiozero.pins.pigpio import PiGPIOFactory
from os import environ

PIGPIO_ADDR = environ.get("PIGPIO_ADDR")


def main():

    pin_factory = PiGPIOFactory(PIGPIO_ADDR)
    white_led = LED(14, pin_factory=pin_factory)
    red_led = LED(15, pin_factory=pin_factory)
    green_led = LED(16, pin_factory=pin_factory)
    button = Button(21, pin_factory=pin_factory)

    remembrall_device = RemembrallDevice(
        white_led=white_led, red_led=red_led, green_led=green_led, button=button
    )
    loop = get_event_loop()
    remembrall_device.start()
    loop.run_forever()


if __name__ == "__main__":
    main()