from datetime import datetime, timedelta
from typing import Union
from google.oauth2.credentials import Credentials  # type: ignore
from google.auth.transport.requests import Request  # type: ignore
from googleapiclient.discovery import build  # type: ignore
from pydantic.main import BaseModel

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
API_SERVICE_NAME = "calendar"
API_VERSION = "v3"

UPCOMING_EVENTS_DELTA = timedelta(minutes=5)


class CalendarEventStart(BaseModel):
    dateTime: str


class CalendarEventEnd(BaseModel):
    dateTime: str


class CalendarEvent(BaseModel):
    etag: str
    start: CalendarEventStart
    end: CalendarEventEnd
    summary: str


class Calendar:
    tokens_file: str
    credentials: Union[Credentials, None]
    calendar_id: str

    def __init__(self, tokens_file: str, calendar_id: str) -> None:
        self.tokens_file = tokens_file
        self.credentials = None
        self.service = None
        self.calendar_id = calendar_id

    def _get_service(self):
        if self.credentials is None:
            self.credentials = Credentials.from_authorized_user_file(  # type: ignore
                self.tokens_file, SCOPES
            )
            self.service = build("calendar", "v3", credentials=self.credentials)
        if self.credentials.expired:  # type: ignore
            self.credentials.refresh(Request())  # type: ignore
            with open(self.tokens_file, "w+") as f:
                f.write(self.credentials.to_json())  # type: ignore
            self.service = build("calendar", "v3", credentials=self.credentials)
        if self.service is None:
            raise TypeError("service is not initialized")
        return self.service

    def fetch_upcoming_events(self):
        now = datetime.utcnow()
        time_min = (now - timedelta(hours=1)).isoformat() + "Z"
        time_max = (now + timedelta(hours=1)).isoformat() + "Z"
        events_result = (  # type: ignore
            self._get_service()  # type: ignore
            .events()  # type: ignore
            .list(
                calendarId=self.calendar_id,
                singleEvents=True,
                timeMin=time_min,
                timeMax=time_max,
            )
            .execute()
        )
        events = events_result.get("items", [])  # type: ignore
        return [CalendarEvent(**event) for event in events]  # type: ignore
