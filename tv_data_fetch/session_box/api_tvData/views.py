from datetime import datetime, timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services.tv_data_service import TvDataService, INSTRUMENT_MAP


class PriceDataView(APIView):
    """
    GET /api/price-data/?instrument=DAX&period=last_week
    GET /api/price-data/?instrument=NQ&period=custom&date_from=2026-03-01&date_to=2026-03-15
    """

    VALID_PERIODS = {"yesterday", "this_week", "last_week", "last_month", "custom"}

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

