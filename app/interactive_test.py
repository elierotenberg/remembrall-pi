from app.lib.lifx_output_device import LifxOutputDevice
from gpiozero.input_devices import Button  # type: ignore
from lifxlan.light import Light  # type: ignore
from app.lib.config import read_from_env
from gpiozero.pins.pigpio import PiGPIOFactory  # type: ignore
from gpiozero.output_devices import LED  # type: ignore

if __name__ == "__main__":
    config = read_from_env()
    pin_factory = PiGPIOFactory(config.raspberry.pigpio_addr)
    while True:
        p = input("pin to test (l18 for LED 18, b21 for Button 21, x for Lifx): ")
        kind = p[0]
        if kind == "l":
            pin = int(p[1:])
            print(f"LED {pin}")
            led = LED(pin_factory=pin_factory, pin=pin)
            led.on()
            input("press key to continue...")
            led.off()
            led.close()
        if kind == "b":
            pin = int(p[1:])
            print(f"Button {pin}")
            button = Button(pin_factory=pin_factory, pin=pin)
            print("press button to continue...")
            button.wait_for_active()  # type: ignore
            button.close()
        if kind == "x":
            lifx = LifxOutputDevice(
                mac_address=config.lifx.mac_address,
                ip_address=config.lifx.ip_address,
            )
            print(f"lifx {config.lifx.mac_address}")
            input("press key to power on...")
            lifx.on(config.controller.default_color)
            input("press key to power off...")
            lifx.off()
