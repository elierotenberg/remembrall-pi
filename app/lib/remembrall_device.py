from gpiozero import LED, Button
from typing import Literal, Union
from signal import pause


class RemembrallDevice:
    white_led: LED
    red_led: LED
    green_led: LED
    button: Button
    state: Union[Literal["off"], Literal["on"]]

    def __init__(
        self, white_led: LED, red_led: LED, green_led: LED, button: Button
    ) -> None:
        self.white_led = white_led
        self.red_led = red_led
        self.green_led = green_led
        self.button = button
        self.state = "off"

    def all_leds(self):
        return [self.white_led, self.red_led, self.green_led]

    def on_push_button(self):
        print("on_push_button", self.state)
        if self.state == "on":
            self.state = "off"
            for led in self.all_leds():
                led.off()
        elif self.state == "off":
            self.state = "on"
            for led in self.all_leds():
                led.on()

    def start(self):
        self.button.when_activated = self.on_push_button
        print("started")