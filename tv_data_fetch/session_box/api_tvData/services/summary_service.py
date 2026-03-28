class SummaryService:

    def calculate(self, daily_results: list[dict], sl_distance: float, tp_distance: float) -> dict:
        """
        Aggregates daily backtest results into summary statistics.

        Returns:
        {
            "total_days": int,
            "wins": int,
            "losses": int,
            "no_breakout": int,
            "win_rate": float (percentage),
            "net_points": float,
            "gross_profit": float,
            "gross_loss": float,
        }
        """
        total_days = len(daily_results)
        wins = 0
        losses = 0
        no_breakout = 0
        gross_profit = 0.0
        gross_loss = 0.0

        for result in daily_results:
            if result["result"] == "win":
                wins += 1
                gross_profit += tp_distance
            elif result["result"] == "loss":
                losses += 1
                gross_loss += sl_distance
            else:
                no_breakout += 1

        decided_days = wins + losses
        win_rate = round((wins / decided_days) * 100, 2) if decided_days > 0 else 0.0
        net_points = round(gross_profit - gross_loss, 2)

        return {
            "total_days": total_days,
            "wins": wins,
            "losses": losses,
            "no_breakout": no_breakout,
            "win_rate": win_rate,
            "net_points": net_points,
            "gross_profit": round(gross_profit, 2),
            "gross_loss": round(gross_loss, 2),
        }
