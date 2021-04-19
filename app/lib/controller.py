from app.lib.lifx_output_device import LifxOutputDevice
from app.lib.color import from_event_summary
from app.lib.gpio_rgb_led_output_device import GpioRgbLedOutputDevice
from app.lib.calendar import Calendar, CalendarEvent
from app.lib.config import Config
from app.lib.output_device import OutputDevice
from datetime import datetime, timedelta
from gpiozero.output_devices import LED  # type: ignore
from gpiozero.input_devices import Button  # type: ignore
from gpiozero.pins.pigpio import PiGPIOFactory  # type: ignore
from os import getcwd, path
from time import sleep
from typing import List
import logging


class Controller:
    _output: OutputDevice
    _status_led: LED
    _status_led_state: bool
    _button: Button
    _calendar: Calendar
    _sleep_interval_seconds: int
    _poll_interval: timedelta
    _upcoming_events: List[CalendarEvent]
    _ongoing_events: List[CalendarEvent]
    _dismissed_events: List[CalendarEvent]
    _button_pushed: bool

    def __init__(self, config: Config):
        pin_factory = PiGPIOFactory(config.raspberry.pigpio_addr)
        if config.controller.output_device == "gpio_rgb_led":
            self._output = GpioRgbLedOutputDevice(
                red_pin=config.raspberry.red_pin,
                green_pin=config.raspberry.green_pin,
                blue_pin=config.raspberry.blue_pin,
                pin_factory=pin_factory,
            )
        elif config.controller.output_device == "lifx":
            self._output = LifxOutputDevice(
                mac_address=config.lifx.mac_address, ip_address=config.lifx.ip_address
            )
        else:
            raise TypeError("output_device should be 'gpio_rgb_led' or 'lifx'")
        self._button = Button(config.raspberry.button_pin, pin_factory=pin_factory)
        self._status_led = LED(pin=config.raspberry.status_pin, pin_factory=pin_factory)
        self._calendar = Calendar(
            tokens_file=path.join(getcwd(), config.google.tokens),
            calendar_id=config.google.calendar_id,
        )
        self._upcoming_events = []
        self._ongoing_events = []
        self._dismissed_events = []
        self._poll_interval = timedelta(
            minutes=config.controller.poll_interval_minutes,
            seconds=config.controller.poll_interval_seconds,
        )
        self.last_fetched = datetime.utcfromtimestamp(0)
        self._sleep_interval_seconds = config.controller.sleep_interval_seconds
        self._button_pushed = False

    def _on_push_button(self):
        self._button_pushed = True

    def _has_event(self, event: CalendarEvent):
        logging.debug(f"has_event? {event.etag, event.summary}")
        for upcoming_event in self._upcoming_events:
            if upcoming_event.etag == event.etag:
                logging.debug("has upcoming event")
                return True
        for ongoing_event in self._ongoing_events:
            if ongoing_event.etag == event.etag:
                logging.debug("has ongoing event")
                return True
        for dismissed_event in self._dismissed_events:
            if dismissed_event.etag == event.etag:
                logging.debug("has dismissed event")
                return True
        logging.debug("has not event")
        return False

    def _find_most_recent_ongoing_event(self):
        most_recent_ongoing_event = None
        for this_ongoing_event in self._ongoing_events:
            if most_recent_ongoing_event is None:
                most_recent_ongoing_event = this_ongoing_event
            else:
                most_recent_ongoing_event_start = datetime.fromisoformat(
                    most_recent_ongoing_event.start.dateTime
                )
                this_ongoing_event_start = datetime.fromisoformat(
                    this_ongoing_event.start.dateTime
                )
                if this_ongoing_event_start > most_recent_ongoing_event_start:
                    most_recent_ongoing_event = this_ongoing_event
        return most_recent_ongoing_event

    def run_forever(self):
        self._button.when_activated = self._on_push_button
        self._output.off()
        self._status_led.off()
        self._status_led_state = False
        while True:
            if self._status_led_state:
                self._status_led.off()
                self._status_led_state = False
            else:
                self._status_led.on()
                self._status_led_state = True
            logging.debug(
                f"tick (upcoming: {len(self._upcoming_events)}, ongoing: {len(self._ongoing_events)}, dismissed: {len(self._dismissed_events)})"
            )
            if self._button_pushed:
                self._button_pushed = False
                self._output.off()
                for event in self._ongoing_events:
                    self._dismissed_events.append(event)
                self._ongoing_events.clear()
            if self.last_fetched.utcnow() > self.last_fetched + self._poll_interval:
                logging.info("fetch")
                upcoming_events = self._calendar.fetch_upcoming_events()
                self.last_fetched = datetime.utcnow()
                for upcoming_event in upcoming_events:
                    if not self._has_event(upcoming_event):
                        logging.info(f"push event {upcoming_event.summary}")
                        self._upcoming_events.append(upcoming_event)
            next_upcoming_events: List[CalendarEvent] = []
            now = datetime.fromisoformat(datetime.utcnow().isoformat() + "+00:00")
            for upcoming_event in self._upcoming_events:
                event_start = datetime.fromisoformat(upcoming_event.start.dateTime)
                if event_start < now:
                    logging.info(f"ongoing event {upcoming_event.summary}")
                    self._ongoing_events.append(upcoming_event)
                else:
                    next_upcoming_events.append(upcoming_event)
            self._upcoming_events = next_upcoming_events
            most_recent_ongoing_event = self._find_most_recent_ongoing_event()
            if most_recent_ongoing_event is not None:
                logging.info(
                    f"most_recent_ongoing_event {most_recent_ongoing_event.summary}"
                )
                color = from_event_summary(most_recent_ongoing_event.summary.strip())
                self._output.on(color)

            logging.debug("sleeping")
            sleep(self._sleep_interval_seconds)
