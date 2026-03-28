import pandas as pd
from datetime import datetime, timedelta, timezone
from tvDatafeed import TvDatafeed, Interval
from ..models import PriceRecord

INSTRUMENT_MAP = {
    "DAX":  {"symbol": "FDAX1!", "exchange": "EUREX"},
    "NQ":   {"symbol": "NQ1!",   "exchange": "CME"},
    "DJ":   {"symbol": "YM1!",   "exchange": "CBOT"},
    "SP500":{"symbol": "ES1!",   "exchange": "CME"},
}


def resolve_date_range(period: str, date_from: datetime = None, date_to: datetime = None) -> tuple[datetime, datetime]:
    """
    Resolves a named period or custom range into (start, end) datetime objects (UTC-aware).
    """
    now = datetime.now(tz=timezone.utc)
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)

    if period == "yesterday":
        start = today - timedelta(days=1)
        end = today
    elif period == "this_week":
        start = today - timedelta(days=today.weekday())
        end = now
    elif period == "last_week":
        start = today - timedelta(days=today.weekday() + 7)
        end = start + timedelta(days=7)
    elif period == "last_month":
        first_of_this_month = today.replace(day=1)
        last_month_end = first_of_this_month - timedelta(days=1)
        start = last_month_end.replace(day=1)
        end = first_of_this_month
    elif period == "custom":
        if not date_from or not date_to:
            raise ValueError("custom period requires date_from and date_to")
        start = date_from if date_from.tzinfo else date_from.replace(tzinfo=timezone.utc)
        end = date_to if date_to.tzinfo else date_to.replace(tzinfo=timezone.utc)
    else:
        raise ValueError(f"Unknown period: {period}")

    return start, end


class TvDataService:
    def __init__(self):
        self.tv = TvDatafeed()

    def get_or_fetch_data(self, instrument: str, period: str, date_from: datetime = None, date_to: datetime = None) -> list[dict]:
        """
        Returns price records for the given instrument and period.
        If records are missing for the requested range, fetches them from TvDatafeed,
        saves them to the database, and returns all records in that range.
        """
        if instrument not in INSTRUMENT_MAP:
            raise ValueError(f"Unknown instrument: {instrument}. Available: {list(INSTRUMENT_MAP.keys())}")

        start, end = resolve_date_range(period, date_from, date_to)
        symbol_full = f"{INSTRUMENT_MAP[instrument]['exchange']}:{INSTRUMENT_MAP[instrument]['symbol']}"

        db_records = PriceRecord.objects.filter(
            symbol=symbol_full,
            date__gte=start,
            date__lt=end,
        ).order_by('date')

        days_in_range = max(1, (end - start).days)
        # rough estimate: ~8h of trading per day, 5 days/week -> ~70% of calendar days
        expected_bars = int(days_in_range * 0.7 * (8 * 60 / 5))

        if db_records.count() < max(1, expected_bars // 2):
            df = self.fetch_historical_data(
                symbol=INSTRUMENT_MAP[instrument]['symbol'],
                exchange=INSTRUMENT_MAP[instrument]['exchange'],
                days=days_in_range + 7,
            )
            if df is not None and not df.empty:
                start_ts = pd.Timestamp(start).tz_localize(None)
                end_ts = pd.Timestamp(end).tz_localize(None)
                df_filtered = df[(df.index >= start_ts) & (df.index < end_ts)]
                self.save_historical_data(df_filtered)

            db_records = PriceRecord.objects.filter(
                symbol=symbol_full,
                date__gte=start,
                date__lt=end,
            ).order_by('date')

        return list(db_records.values('date', 'symbol', 'open', 'high', 'low', 'close', 'volume'))

    def fetch_historical_data(self, symbol: str, exchange: str, interval: Interval = Interval.in_5_minute, days: int = 100) -> pd.DataFrame:
        data = self.tv.get_hist(
            symbol=symbol,
            exchange=exchange,
            interval=interval,
            n_bars=self.__days_to_bars(days)
        )
        return data

    def save_historical_data(self, df: pd.DataFrame) -> None:
        """
        Saves rows from a DataFrame to the database.
        Index is assumed to be UTC (as returned by TvDatafeed).
        Skips rows where (symbol, date) already exist.
        """
        if df is None or df.empty:
            return

        records_to_create = []

        for datetime_index, row in df.iterrows():
            symbol = row["symbol"]
            # tvDatafeed returns naive datetimes — we treat them as UTC
            aware_dt = pd.Timestamp(datetime_index).tz_localize(timezone.utc)

            if PriceRecord.objects.filter(symbol=symbol, date=aware_dt).exists():
                continue

            records_to_create.append(
                PriceRecord(
                    symbol=symbol,
                    date=aware_dt,
                    open=row["open"],
                    high=row["high"],
                    low=row["low"],
                    close=row["close"],
                    volume=row["volume"],
                )
            )

        if records_to_create:
            PriceRecord.objects.bulk_create(records_to_create)

    def __days_to_bars(self, days: int, interval_minutes: int = 5) -> int:
        minutes_per_day = 24 * 60
        bars = (minutes_per_day // interval_minutes) * days
        return bars
