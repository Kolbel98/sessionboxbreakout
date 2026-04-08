import { useState } from "react";
import type { BacktestParams } from "../api";

const INSTRUMENTS = ["DAX", "NQ", "SP500", "DJ"];
const PERIODS = ["yesterday", "this_week", "last_week", "this_month", "custom"];
const RR_MODES = ["1:1", "1:2", "1:3", "2:1", "custom"];
const STRATEGIES = [
  { value: "breakout", label: "Breakout" },
  { value: "reverse", label: "Reverse" },
];

interface Props {
  onSubmit: (params: BacktestParams) => void;
  loading: boolean;
}

export default function BacktestForm({ onSubmit, loading }: Props) {
  const [instrument, setInstrument] = useState("DAX");
  const [period, setPeriod] = useState("this_week");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [offsetPoints, setOffsetPoints] = useState(5);
  const [tpPoints, setTpPoints] = useState(50);
  const [rrMode, setRrMode] = useState("1:2");
  const [customSl, setCustomSl] = useState(25);
  const [strategy, setStrategy] = useState("breakout");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      instrument,
      period,
      date_from: period === "custom" ? dateFrom : undefined,
      date_to: period === "custom" ? dateTo : undefined,
      offset_points: offsetPoints,
      tp_points: tpPoints,
      rr_mode: rrMode,
      custom_sl: rrMode === "custom" ? customSl : undefined,
      strategy,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      {/* Instrument */}
      <div>
        <label className="block text-sm text-gray-400 mb-1">Instrument</label>
        <div className="flex gap-2">
          {INSTRUMENTS.map((i) => (
            <button
              key={i}
              type="button"
              onClick={() => setInstrument(i)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors cursor-pointer ${
                instrument === i
                  ? "bg-indigo-600 text-white"
                  : "bg-gray-800 text-gray-400 hover:bg-gray-700"
              }`}
            >
              {i}
            </button>
          ))}
        </div>
      </div>

      {/* Period */}
      <div>
        <label className="block text-sm text-gray-400 mb-1">Period</label>
        <div className="flex flex-wrap gap-2">
          {PERIODS.map((p) => (
            <button
              key={p}
              type="button"
              onClick={() => setPeriod(p)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors cursor-pointer ${
                period === p
                  ? "bg-indigo-600 text-white"
                  : "bg-gray-800 text-gray-400 hover:bg-gray-700"
              }`}
            >
              {p.replace("_", " ")}
            </button>
          ))}
        </div>
      </div>

      {/* Custom date range */}
      {period === "custom" && (
        <div className="flex gap-4">
          <div className="flex-1">
            <label className="block text-sm text-gray-400 mb-1">From</label>
            <input
              type="date"
              value={dateFrom}
              onChange={(e) => setDateFrom(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm"
              required
            />
          </div>
          <div className="flex-1">
            <label className="block text-sm text-gray-400 mb-1">To</label>
            <input
              type="date"
              value={dateTo}
              onChange={(e) => setDateTo(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm"
              required
            />
          </div>
        </div>
      )}

      {/* TP + Offset */}
      <div className="flex gap-4">
        <div className="flex-1">
          <label className="block text-sm text-gray-400 mb-1">TP (points)</label>
          <input
            type="number"
            value={tpPoints}
            onChange={(e) => setTpPoints(Number(e.target.value))}
            min={1}
            className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm"
            required
          />
        </div>
        <div className="flex-1">
          <label className="block text-sm text-gray-400 mb-1">Offset (points)</label>
          <input
            type="number"
            value={offsetPoints}
            onChange={(e) => setOffsetPoints(Number(e.target.value))}
            min={0}
            className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm"
            required
          />
        </div>
      </div>

      {/* R:R mode */}
      <div>
        <label className="block text-sm text-gray-400 mb-1">Risk : Reward</label>
        <div className="flex flex-wrap gap-2">
          {RR_MODES.map((r) => (
            <button
              key={r}
              type="button"
              onClick={() => setRrMode(r)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors cursor-pointer ${
                rrMode === r
                  ? "bg-indigo-600 text-white"
                  : "bg-gray-800 text-gray-400 hover:bg-gray-700"
              }`}
            >
              {r}
            </button>
          ))}
        </div>
      </div>

      {/* Custom SL */}
      {rrMode === "custom" && (
        <div>
          <label className="block text-sm text-gray-400 mb-1">SL (points)</label>
          <input
            type="number"
            value={customSl}
            onChange={(e) => setCustomSl(Number(e.target.value))}
            min={1}
            className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm"
            required
          />
        </div>
      )}

      {/* Strategy */}
      <div>
        <label className="block text-sm text-gray-400 mb-1">Strategy</label>
        <div className="flex gap-2">
          {STRATEGIES.map((s) => (
            <button
              key={s.value}
              type="button"
              onClick={() => setStrategy(s.value)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors cursor-pointer ${
                strategy === s.value
                  ? "bg-indigo-600 text-white"
                  : "bg-gray-800 text-gray-400 hover:bg-gray-700"
              }`}
            >
              {s.label}
            </button>
          ))}
        </div>
        <p className="text-xs text-gray-500 mt-1">
          {strategy === "breakout"
            ? "Enter when price breaks above/below the session box."
            : "Enter when price touches the session box level (fade/rejection)."}
        </p>
      </div>

      {/* Submit */}
      <button
        type="submit"
        disabled={loading}
        className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium py-3 rounded-lg transition-colors cursor-pointer"
      >
        {loading ? "Running backtest..." : "Run Backtest"}
      </button>
    </form>
  );
}
