from datetime import datetime, timedelta
from time import sleep
from typing import List
from os import getcwd, path
from gpiozero.input_devices import Button  # type: ignore
from gpiozero.output_devices import RGBLED  # type: ignore
from gpiozero.pins.pigpio import PiGPIOFactory  # type: ignore
from app.lib.config import Config
from app.lib.calendar import Calendar, CalendarEvent


def get_event_color(calendar_event: CalendarEvent):
    if calendar_event.summary.startswith("R"):
        return (1, 0, 0)
    if calendar_event.summary.startswith("G"):
        return (0, 1, 0)
    if calendar_event.summary.startswith("B"):
        return (0, 0, 1)
    return (1, 1, 1)


class Controller:
    rgb_led: RGBLED
    button: Button
    calendar: Calendar
    poll_interval: timedelta
    upcoming_events: List[CalendarEvent]
    ongoing_events: List[CalendarEvent]
    dismissed_events: List[CalendarEvent]

    def __init__(self, config: Config):
        pin_factory = PiGPIOFactory(config.device.pigpio_addr)
        self.rgb_led = RGBLED(
            red=config.device.red_pin,
            green=config.device.green_pin,
            blue=config.device.blue_pin,
            pin_factory=pin_factory,
        )
        self.button = Button(config.device.button_pin, pin_factory=pin_factory)
        self.calendar = Calendar(
            tokens_file=path.join(getcwd(), config.google.tokens),
            calendar_id=config.google.calendar_id,
        )
        self.upcoming_events = []
        self.ongoing_events = []
        self.dismissed_events = []
        self.poll_interval = timedelta(minutes=config.controller.poll_interval_minutes)
        self.last_fetched = datetime.utcfromtimestamp(0)

    def _on_push_button(self):
        self.rgb_led.off()
        for event in self.ongoing_events:
            self.dismissed_events.append(event)
        self.ongoing_events.clear()

    def _has_event(self, event: CalendarEvent):
        for upcoming_event in self.upcoming_events:
            if upcoming_event.id == event.id:
                return True
        for ongoing_event in self.ongoing_events:
            if ongoing_event.id == event.id:
                return True
        for dismissed_event in self.dismissed_events:
            if dismissed_event.id == event.id:
                return True
        return False

    def run_forever(self):
        self.button.when_activated = self._on_push_button
        while True:
            print("tick")
            if self.last_fetched.utcnow() > self.last_fetched + self.poll_interval:
                print("fetch")
                upcoming_events = self.calendar.fetch_upcoming_events()
                self.last_fetched = datetime.utcnow()
                for upcoming_event in upcoming_events:
                    if not self._has_event(upcoming_event):
                        print(f"push event {upcoming_event.summary}")
                        self.upcoming_events.append(upcoming_event)
            next_upcoming_events: List[CalendarEvent] = []
            next_ongoing_events: List[CalendarEvent] = []
            now = datetime.fromisoformat(datetime.utcnow().isoformat() + "+00:00")
            for upcoming_event in self.upcoming_events:
                event_start = datetime.fromisoformat(upcoming_event.start.dateTime)
                if event_start < now:
                    print(f"ongoing event {upcoming_event.summary}")
                    next_ongoing_events.append(upcoming_event)
                else:
                    next_upcoming_events.append(upcoming_event)
            self.upcoming_events = next_upcoming_events
            self.ongoing_events = next_ongoing_events
            if len(self.ongoing_events) > 0:
                latest_event = self.ongoing_events[len(self.ongoing_events) - 1]
                print("first_ongoing_event", latest_event.summary)
                color = get_event_color(latest_event)
                self.rgb_led.color = color

            print("sleeping")
            sleep(5)
