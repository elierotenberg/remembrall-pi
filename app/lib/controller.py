from datetime import datetime, timedelta
import logging
from time import sleep
from typing import List
from os import getcwd, path
from gpiozero.input_devices import Button  # type: ignore
from gpiozero.output_devices import RGBLED  # type: ignore
from gpiozero.pins.pigpio import PiGPIOFactory  # type: ignore
from app.lib.config import Config
from app.lib.calendar import Calendar, CalendarEvent
from threading import Lock


def get_event_color(calendar_event: CalendarEvent):
    if calendar_event.summary.startswith("R"):
        return (1, 0, 0)
    if calendar_event.summary.startswith("G"):
        return (0, 1, 0)
    if calendar_event.summary.startswith("B"):
        return (0, 0, 1)
    return (1, 1, 1)


class Controller:
    _rgb_led: RGBLED
    _button: Button
    _calendar: Calendar
    _sleep_interval_seconds: int
    _poll_interval: timedelta
    _upcoming_events: List[CalendarEvent]
    _ongoing_events: List[CalendarEvent]
    _dismissed_events: List[CalendarEvent]
    _mutex: Lock

    def __init__(self, config: Config):
        pin_factory = PiGPIOFactory(config.device.pigpio_addr)
        self._rgb_led = RGBLED(
            red=config.device.red_pin,
            green=config.device.green_pin,
            blue=config.device.blue_pin,
            pin_factory=pin_factory,
        )
        self._button = Button(config.device.button_pin, pin_factory=pin_factory)
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
        self._mutex = Lock()

    def _on_push_button(self):
        self._rgb_led.off()
        self._lock("_on_push_button")
        try:
            for event in self._ongoing_events:
                self._dismissed_events.append(event)
            self._ongoing_events.clear()
        finally:
            self._unlock("_on_push_button")

    def _has_event(self, event: CalendarEvent):
        logging.debug(f"has_event? {event.id, event.summary}")
        for upcoming_event in self._upcoming_events:
            if upcoming_event.id == event.id:
                logging.debug("has upcoming event")
                return True
        for ongoing_event in self._ongoing_events:
            if ongoing_event.id == event.id:
                logging.debug("has ongoing event")
                return True
        for dismissed_event in self._dismissed_events:
            if dismissed_event.id == event.id:
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

    def _lock(self, label: str):
        logging.debug(f"LOCK {label}")
        self._mutex.acquire()

    def _unlock(self, label: str):
        logging.debug(f"UNLOCK {label}")
        self._mutex.release()

    def run_forever(self):
        self._button.when_activated = self._on_push_button
        self._rgb_led.off()
        while True:
            logging.debug("tick")
            if self.last_fetched.utcnow() > self.last_fetched + self._poll_interval:
                logging.info("fetch")
                upcoming_events = self._calendar.fetch_upcoming_events()
                self.last_fetched = datetime.utcnow()
                self._lock("run_forever:fetch")
                try:
                    for upcoming_event in upcoming_events:
                        if not self._has_event(upcoming_event):
                            logging.info(f"push event {upcoming_event.summary}")
                            self._upcoming_events.append(upcoming_event)
                finally:
                    self._unlock("run_forever:fetch")
            self._lock("run_forever")
            try:
                next_upcoming_events: List[CalendarEvent] = []
                next_ongoing_events: List[CalendarEvent] = []
                now = datetime.fromisoformat(datetime.utcnow().isoformat() + "+00:00")
                for upcoming_event in self._upcoming_events:
                    event_start = datetime.fromisoformat(upcoming_event.start.dateTime)
                    if event_start < now:
                        logging.info(f"ongoing event {upcoming_event.summary}")
                        next_ongoing_events.append(upcoming_event)
                    else:
                        next_upcoming_events.append(upcoming_event)
                self._upcoming_events = next_upcoming_events
                self._ongoing_events = next_ongoing_events
                most_recent_ongoing_event = self._find_most_recent_ongoing_event()
                if most_recent_ongoing_event is not None:
                    logging.info(
                        f"most_recent_ongoing_event {most_recent_ongoing_event.summary}"
                    )
                    color = get_event_color(most_recent_ongoing_event)
                    self._rgb_led.blink(on_color=color, background=True)  # type: ignore
                else:
                    self._rgb_led.off()
            finally:
                self._unlock("run_forever")

            logging.debug("sleeping")
            sleep(self._sleep_interval_seconds)
