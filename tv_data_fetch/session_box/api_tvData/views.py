from datetime import datetime, timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services.tv_data_service import TvDataService, INSTRUMENT_MAP
from .services.session_box_service import SessionBoxService
from .services.breakout_service import BreakoutService, RR_PRESETS, resolve_tp_sl
from .services.summary_service import SummaryService


class PriceDataView(APIView):
    """
    GET /api/price-data/?instrument=DAX&period=last_week
    GET /api/price-data/?instrument=NQ&period=custom&date_from=2026-03-01&date_to=2026-03-15
    """

    VALID_PERIODS = {"yesterday", "this_week", "last_week", "this_month", "custom"}

    def get(self, request):
        instrument = request.query_params.get("instrument")
        period = request.query_params.get("period")

        if not instrument:
            return Response({"error": "Missing required parameter: instrument"}, status=status.HTTP_400_BAD_REQUEST)

        if not period:
            return Response({"error": "Missing required parameter: period"}, status=status.HTTP_400_BAD_REQUEST)

        if instrument not in INSTRUMENT_MAP:
            return Response(
                {"error": f"Unknown instrument '{instrument}'. Available: {list(INSTRUMENT_MAP.keys())}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if period not in self.VALID_PERIODS:
            return Response(
                {"error": f"Unknown period '{period}'. Available: {list(self.VALID_PERIODS)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        date_from = None
        date_to = None

        if period == "custom":
            raw_from = request.query_params.get("date_from")
            raw_to = request.query_params.get("date_to")

            if not raw_from or not raw_to:
                return Response(
                    {"error": "period=custom requires date_from and date_to (format: YYYY-MM-DD)"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                date_from = datetime.strptime(raw_from, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                date_to = datetime.strptime(raw_to, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            except ValueError:
                return Response(
                    {"error": "Invalid date format. Use YYYY-MM-DD"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        try:
            service = TvDataService()
            records = service.get_or_fetch_data(instrument, period, date_from, date_to)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"instrument": instrument, "period": period, "count": len(records), "data": records})


class BacktestView(APIView):
    """
    GET /api/backtest/?instrument=DAX&period=this_month&offset_points=5&tp_points=60&rr_mode=1:2
    GET /api/backtest/?instrument=NQ&period=custom&date_from=2026-03-01&date_to=2026-03-28&tp_points=60&rr_mode=custom&custom_sl=25&offset_points=5
    """

    VALID_PERIODS = {"yesterday", "this_week", "last_week", "this_month", "custom"}
    VALID_RR_MODES = set(RR_PRESETS.keys()) | {"custom"}
    VALID_STRATEGIES = {"breakout", "reverse"}

    def get(self, request):
        # --- Validate instrument ---
        instrument = request.query_params.get("instrument")
        if not instrument or instrument not in INSTRUMENT_MAP:
            return Response(
                {"error": f"Missing or unknown instrument. Available: {list(INSTRUMENT_MAP.keys())}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --- Validate period ---
        period = request.query_params.get("period")
        if not period or period not in self.VALID_PERIODS:
            return Response(
                {"error": f"Missing or unknown period. Available: {list(self.VALID_PERIODS)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --- Validate dates for custom period ---
        date_from = None
        date_to = None

        if period == "custom":
            raw_from = request.query_params.get("date_from")
            raw_to = request.query_params.get("date_to")

            if not raw_from or not raw_to:
                return Response(
                    {"error": "period=custom requires date_from and date_to (YYYY-MM-DD)"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                date_from = datetime.strptime(raw_from, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                date_to = datetime.strptime(raw_to, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            except ValueError:
                return Response({"error": "Invalid date format. Use YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST)

        # --- Validate offset_points ---
        try:
            offset_points = float(request.query_params.get("offset_points", 0))
        except (TypeError, ValueError):
            return Response({"error": "offset_points must be a number"}, status=status.HTTP_400_BAD_REQUEST)

        # --- Validate tp_points (always required) ---
        raw_tp = request.query_params.get("tp_points")
        if not raw_tp:
            return Response({"error": "Missing required parameter: tp_points"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            tp_points = float(raw_tp)
        except (TypeError, ValueError):
            return Response({"error": "tp_points must be a number"}, status=status.HTTP_400_BAD_REQUEST)

        # --- Validate RR mode + SL ---
        rr_mode = request.query_params.get("rr_mode", "1:1")
        if rr_mode not in self.VALID_RR_MODES:
            return Response(
                {"error": f"Unknown rr_mode. Available: {list(self.VALID_RR_MODES)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        custom_sl = None

        if rr_mode == "custom":
            try:
                custom_sl = float(request.query_params.get("custom_sl"))
            except (TypeError, ValueError):
                return Response(
                    {"error": "rr_mode=custom requires numeric custom_sl"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        try:
            sl_distance, tp_distance = resolve_tp_sl(rr_mode, tp_points, custom_sl)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # --- Validate strategy ---
        strategy = request.query_params.get("strategy", "breakout")
        if strategy not in self.VALID_STRATEGIES:
            return Response(
                {"error": f"Unknown strategy '{strategy}'. Available: {list(self.VALID_STRATEGIES)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --- Step 1: Ensure data exists in DB ---
        try:
            tv_service = TvDataService()
            tv_service.get_or_fetch_data(instrument, period, date_from, date_to)
        except Exception as e:
            return Response({"error": f"Data fetch failed: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # --- Step 2: Resolve date range ---
        from .services.tv_data_service import resolve_date_range
        start, end = resolve_date_range(period, date_from, date_to)

        # --- Step 3: Get session boxes ---
        session_service = SessionBoxService()
        session_boxes = session_service.get_session_boxes(instrument, start, end)

        if not session_boxes:
            return Response({
                "instrument": instrument,
                "period": period,
                "summary": {},
                "results": [],
                "message": "No trading data found for the given range.",
            })

        # --- Step 4: Evaluate breakouts ---
        symbol_full = f"{INSTRUMENT_MAP[instrument]['exchange']}:{INSTRUMENT_MAP[instrument]['symbol']}"
        breakout_service = BreakoutService()
        daily_results = breakout_service.evaluate_range(
            session_boxes, symbol_full, offset_points, sl_distance, tp_distance, strategy
        )

        # --- Step 5: Summary ---
        summary_service = SummaryService()
        summary = summary_service.calculate(daily_results, sl_distance, tp_distance)

        return Response({
            "instrument": instrument,
            "period": period,
            "offset_points": offset_points,
            "rr_mode": rr_mode,
            "strategy": strategy,
            "sl_distance": sl_distance,
            "tp_distance": tp_distance,
            "summary": summary,
            "results": daily_results,
        })

