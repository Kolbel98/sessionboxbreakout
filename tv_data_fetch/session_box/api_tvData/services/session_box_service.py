from datetime import time, datetime, timedelta, timezone
from ..models import PriceRecord


# Session configuration per instrument (all times in UTC)
#
# session_start / session_end — the window we scan for HIGH and LOW
# breakout_start / breakout_end — the window where we look for a breakout
#
# DAX:   session = Asian session   00:00–09:00 UTC → breakout 09:00–16:00 UTC
# NQ:    session = European session 07:00–16:00 UTC → breakout 16:00–21:00 UTC
# SP500: session = European session 07:00–16:00 UTC → breakout 16:00–21:00 UTC
# DJ:    session = European session 07:00–16:00 UTC → breakout 16:00–21:00 UTC

SESSION_CONFIG = {
    "DAX": {
        "session_start": time(0, 0),
        "session_end": time(9, 0),
        "breakout_start": time(9, 0),
        "breakout_end": time(16, 0),
    },
    "NQ": {
        "session_start": time(7, 0),
        "session_end": time(16, 0),
        "breakout_start": time(16, 0),
        "breakout_end": time(21, 0),
    },
    "SP500": {
        "session_start": time(7, 0),
        "session_end": time(16, 0),
        "breakout_start": time(16, 0),
        "breakout_end": time(21, 0),
    },
    "DJ": {
        "session_start": time(7, 0),
        "session_end": time(16, 0),
        "breakout_start": time(16, 0),
        "breakout_end": time(21, 0),
    },
}


class SessionBoxService:

    def get_session_boxes(self, instrument: str, date_from: datetime, date_to: datetime) -> list[dict]:
        """
        For each trading day in the range, calculates the session high/low
        based on the instrument's session config.

        Returns a list of dicts, one per day:
        {
            "date": date,
            "instrument": str,
            "session_high": float,
            "session_low": float,
            "session_start": datetime,
            "session_end": datetime,
            "breakout_start": datetime,
            "breakout_end": datetime,
        }
        """
        if instrument not in SESSION_CONFIG:
            raise ValueError(f"No session config for instrument: {instrument}")

        from .tv_data_service import INSTRUMENT_MAP

        config = SESSION_CONFIG[instrument]
        symbol_full = f"{INSTRUMENT_MAP[instrument]['exchange']}:{INSTRUMENT_MAP[instrument]['symbol']}"

        results = []
        current_date = date_from.date() if isinstance(date_from, datetime) else date_from
        end_date = date_to.date() if isinstance(date_to, datetime) else date_to

        while current_date < end_date:
            session_start_dt = datetime.combine(current_date, config["session_start"], tzinfo=timezone.utc)
            session_end_dt = datetime.combine(current_date, config["session_end"], tzinfo=timezone.utc)
            breakout_start_dt = datetime.combine(current_date, config["breakout_start"], tzinfo=timezone.utc)
            breakout_end_dt = datetime.combine(current_date, config["breakout_end"], tzinfo=timezone.utc)

            session_candles = PriceRecord.objects.filter(
                symbol=symbol_full,
                date__gte=session_start_dt,
                date__lt=session_end_dt,
            ).order_by("date")

            if not session_candles.exists():
                current_date += timedelta(days=1)
                continue

            session_high = session_candles.order_by("-high").first().high
            session_low = session_candles.order_by("low").first().low

            results.append({
                "date": current_date,
                "instrument": instrument,
                "session_high": session_high,
                "session_low": session_low,
                "session_start": session_start_dt,
                "session_end": session_end_dt,
                "breakout_start": breakout_start_dt,
                "breakout_end": breakout_end_dt,
            })

            current_date += timedelta(days=1)

        return results
