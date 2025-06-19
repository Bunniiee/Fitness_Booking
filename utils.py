from datetime import datetime
try:
    from zoneinfo import ZoneInfo
except ImportError:
    from pytz import timezone as ZoneInfo

IST = "Asia/Kolkata"

def convert_ist_to_user_tz(dt: datetime, user_tz: str) -> datetime:
    """
    Convert a datetime from IST to the user's timezone.
    Assumes input dt is in IST.
    """
    try:
        ist_zone = ZoneInfo(IST)
        user_zone = ZoneInfo(user_tz)
        dt_ist = dt.replace(tzinfo=ist_zone)
        return dt_ist.astimezone(user_zone)
    except Exception:
        return dt  # fallback: return as is 