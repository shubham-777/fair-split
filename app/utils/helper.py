from datetime import timezone, datetime


def today_datetime(tz=timezone.utc)-> datetime:
    if not tz:
        tz = timezone.utc
    return datetime.now(tz=tz)