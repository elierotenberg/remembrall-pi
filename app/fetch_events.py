from app.lib.config import read_from_env
from app.lib.calendar import Calendar
from os import path, getcwd

if __name__ == "__main__":
    config = read_from_env()
    tokens_file = path.join(getcwd(), config.google.tokens)
    calendar = Calendar(tokens_file=tokens_file, calendar_id=config.google.calendar_id)
    events = calendar.fetch_upcoming_events()
    print(events)