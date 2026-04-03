const API_BASE = "http://127.0.0.1:8000/api";

export interface BacktestParams {
  instrument: string;
  period: string;
  date_from?: string;
  date_to?: string;
  offset_points: number;
  tp_points: number;
  rr_mode: string;
  custom_sl?: number;
}

export interface DailyResult {
  date: string;
  instrument: string;
  session_high: number;
  session_low: number;
  breakout_direction: "long" | "short" | null;
  entry_price: number | null;
  tp_price: number | null;
  sl_price: number | null;
  result: "win" | "loss" | "no_breakout";
}

export interface Summary {
  total_days: number;
  wins: number;
  losses: number;
  no_breakout: number;
  win_rate: number;
  net_points: number;
  gross_profit: number;
  gross_loss: number;
}

export interface BacktestResponse {
  instrument: string;
  period: string;
  offset_points: number;
  rr_mode: string;
  sl_distance: number;
  tp_distance: number;
  summary: Summary;
  results: DailyResult[];
  message?: string;
}

export async function fetchBacktest(params: BacktestParams): Promise<BacktestResponse> {
  const query = new URLSearchParams();

  query.set("instrument", params.instrument);
  query.set("period", params.period);
  query.set("offset_points", String(params.offset_points));
  query.set("tp_points", String(params.tp_points));
  query.set("rr_mode", params.rr_mode);

  if (params.period === "custom" && params.date_from && params.date_to) {
    query.set("date_from", params.date_from);
    query.set("date_to", params.date_to);
  }

  if (params.rr_mode === "custom" && params.custom_sl !== undefined) {
    query.set("custom_sl", String(params.custom_sl));
  }

  const res = await fetch(`${API_BASE}/backtest/?${query.toString()}`);
  const data = await res.json();

  if (!res.ok) {
    throw new Error(data.error || "Unknown error");
  }

  return data;
}
