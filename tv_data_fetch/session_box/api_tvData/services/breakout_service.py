from datetime import datetime
from ..models import PriceRecord


# Predefined Risk:Reward ratios
# Format "risk:reward" — defines how SL relates to TP
# e.g. "1:2" means risk 1 part, reward 2 parts → SL = TP / 2
# e.g. "2:1" means risk 2 parts, reward 1 part → SL = TP * 2
# TP is ALWAYS provided by the user manually.
# SL is calculated from TP using the ratio. Only in "custom" mode user sets both.
RR_PRESETS = {
    "1:1": 1.0,   # SL = TP * (1/1) = TP
    "1:2": 0.5,   # SL = TP * (1/2) = TP / 2
    "1:3": 0.333, # SL = TP * (1/3) = TP / 3
    "2:1": 2.0,   # SL = TP * (2/1) = TP * 2
}


def resolve_tp_sl(
    rr_mode: str,
    tp_points: float,
    custom_sl: float = None,
) -> tuple[float, float]:
    """
    Resolves TP and SL distances in points.

    TP is always user-defined (tp_points).
    SL is either:
      - calculated from TP using the R:R ratio (preset mode)
      - user-defined (custom mode)

    Returns (sl_distance, tp_distance) in points.
    """
    if rr_mode == "custom":
        if custom_sl is None:
            raise ValueError("custom mode requires custom_sl")
        return custom_sl, tp_points

    if rr_mode not in RR_PRESETS:
        raise ValueError(f"Unknown rr_mode: {rr_mode}. Available: {list(RR_PRESETS.keys()) + ['custom']}")

    sl_distance = tp_points * RR_PRESETS[rr_mode]
    return sl_distance, tp_points


class BreakoutService:

    def evaluate_day(
        self,
        session_box: dict,
        symbol_full: str,
        offset_points: float,
        sl_distance: float,
        tp_distance: float,
        strategy: str = "breakout",
    ) -> dict:
        """
        Evaluates a single trading day for the chosen strategy.

        strategy="breakout":
          - Waits for the first candle that breaks above session_high (→ long)
            or below session_low (→ short), then enters with TP/SL in that direction.

        strategy="reverse":
          - Waits for the first candle that touches session_high (→ short, fade the high)
            or session_low (→ long, fade the low), then enters in the opposite direction.
          - Entry: at the level itself (± offset), TP away from the level, SL beyond it.

        Returns:
        {
            "date": date,
            "instrument": str,
            "session_high": float,
            "session_low": float,
            "breakout_direction": "long" | "short" | None,
            "entry_price": float | None,
            "tp_price": float | None,
            "sl_price": float | None,
            "result": "win" | "loss" | "no_breakout",
        }
        """
        session_high = session_box["session_high"]
        session_low = session_box["session_low"]
        breakout_start = session_box["breakout_start"]
        breakout_end = session_box["breakout_end"]

        base_result = {
            "date": session_box["date"],
            "instrument": session_box["instrument"],
            "session_high": session_high,
            "session_low": session_low,
            "breakout_direction": None,
            "entry_price": None,
            "tp_price": None,
            "sl_price": None,
            "result": "no_breakout",
        }

        # Get all candles in the breakout window, ordered chronologically
        breakout_candles = list(
            PriceRecord.objects.filter(
                symbol=symbol_full,
                date__gte=breakout_start,
                date__lt=breakout_end,
            ).order_by("date").values("date", "open", "high", "low", "close")
        )

        if not breakout_candles:
            return base_result

        if strategy == "reverse":
            return self._evaluate_reverse(base_result, breakout_candles, session_high, session_low, offset_points, sl_distance, tp_distance)
        else:
            return self._evaluate_breakout(base_result, breakout_candles, session_high, session_low, offset_points, sl_distance, tp_distance)

    def _evaluate_breakout(
        self,
        base_result: dict,
        breakout_candles: list,
        session_high: float,
        session_low: float,
        offset_points: float,
        sl_distance: float,
        tp_distance: float,
    ) -> dict:
        """
        Classic breakout strategy:
        - High broken → LONG entry above session_high + offset
        - Low broken  → SHORT entry below session_low - offset
        """
        # --- Step 1: Find the first breakout candle ---
        breakout_direction = None
        breakout_candle_idx = None

        for idx, candle in enumerate(breakout_candles):
            breaks_high = candle["high"] > session_high
            breaks_low = candle["low"] < session_low

            if breaks_high and breaks_low:
                dist_to_high = abs(candle["open"] - session_high)
                dist_to_low = abs(candle["open"] - session_low)
                breakout_direction = "long" if dist_to_high <= dist_to_low else "short"
                breakout_candle_idx = idx
                break
            elif breaks_high:
                breakout_direction = "long"
                breakout_candle_idx = idx
                break
            elif breaks_low:
                breakout_direction = "short"
                breakout_candle_idx = idx
                break

        if breakout_direction is None:
            return base_result

        # --- Step 2: Calculate entry, TP, SL ---
        if breakout_direction == "long":
            entry_price = session_high + offset_points
            tp_price = entry_price + tp_distance
            sl_price = entry_price - sl_distance
        else:
            entry_price = session_low - offset_points
            tp_price = entry_price - tp_distance
            sl_price = entry_price + sl_distance

        base_result.update({
            "breakout_direction": breakout_direction,
            "entry_price": entry_price,
            "tp_price": tp_price,
            "sl_price": sl_price,
        })

        return self._walk_candles(base_result, breakout_candles, breakout_candle_idx, breakout_direction, tp_price, sl_price)

    def _evaluate_reverse(
        self,
        base_result: dict,
        breakout_candles: list,
        session_high: float,
        session_low: float,
        offset_points: float,
        sl_distance: float,
        tp_distance: float,
    ) -> dict:
        """
        Reverse (fade) strategy:
        - Price touches session_high → SHORT (expect rejection downward)
          Entry: session_high - offset, TP: entry - tp_distance, SL: entry + sl_distance
        - Price touches session_low  → LONG (expect bounce upward)
          Entry: session_low + offset, TP: entry + tp_distance, SL: entry - sl_distance

        First touch wins — if high is touched first, we go short; if low first, we go long.
        If a single candle touches both, pick the level closer to candle open.
        """
        touch_direction = None
        touch_candle_idx = None

        for idx, candle in enumerate(breakout_candles):
            touches_high = candle["high"] >= session_high
            touches_low = candle["low"] <= session_low

            if touches_high and touches_low:
                dist_to_high = abs(candle["open"] - session_high)
                dist_to_low = abs(candle["open"] - session_low)
                touch_direction = "short" if dist_to_high <= dist_to_low else "long"
                touch_candle_idx = idx
                break
            elif touches_high:
                touch_direction = "short"
                touch_candle_idx = idx
                break
            elif touches_low:
                touch_direction = "long"
                touch_candle_idx = idx
                break

        if touch_direction is None:
            return base_result

        # --- Entry, TP, SL for reverse ---
        if touch_direction == "short":
            # Fading the high: sell slightly below session_high
            entry_price = session_high - offset_points
            tp_price = entry_price - tp_distance
            sl_price = entry_price + sl_distance
        else:
            # Fading the low: buy slightly above session_low
            entry_price = session_low + offset_points
            tp_price = entry_price + tp_distance
            sl_price = entry_price - sl_distance

        base_result.update({
            "breakout_direction": touch_direction,
            "entry_price": entry_price,
            "tp_price": tp_price,
            "sl_price": sl_price,
        })

        return self._walk_candles(base_result, breakout_candles, touch_candle_idx, touch_direction, tp_price, sl_price)

    def _walk_candles(
        self,
        base_result: dict,
        candles: list,
        start_idx: int,
        direction: str,
        tp_price: float,
        sl_price: float,
    ) -> dict:
        """
        Walks candles from start_idx forward to determine if TP or SL is hit first.
        Works identically for both breakout and reverse strategies.
        """
        for candle in candles[start_idx:]:
            if direction == "long":
                hits_tp = candle["high"] >= tp_price
                hits_sl = candle["low"] <= sl_price
            else:  # short
                hits_tp = candle["low"] <= tp_price
                hits_sl = candle["high"] >= sl_price

            if hits_tp and hits_sl:
                # Conservative: if both hit in the same candle, count as loss
                base_result["result"] = "loss"
                return base_result

            if hits_tp:
                base_result["result"] = "win"
                return base_result

            if hits_sl:
                base_result["result"] = "loss"
                return base_result

        base_result["result"] = "no_breakout"
        return base_result

    def evaluate_range(
        self,
        session_boxes: list[dict],
        symbol_full: str,
        offset_points: float,
        sl_distance: float,
        tp_distance: float,
        strategy: str = "breakout",
    ) -> list[dict]:
        """
        Evaluates all days in the given session_boxes list.
        """
        return [
            self.evaluate_day(box, symbol_full, offset_points, sl_distance, tp_distance, strategy)
            for box in session_boxes
        ]
