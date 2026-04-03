import type { Summary } from "../api";

interface Props {
  summary: Summary;
  slDistance: number;
  tpDistance: number;
}

function DonutChart({ wins, losses, noBreakout }: { wins: number; losses: number; noBreakout: number }) {
  const total = wins + losses + noBreakout;
  if (total === 0) return null;

  const radius = 50;
  const circumference = 2 * Math.PI * radius;

  const winPct = wins / total;
  const lossPct = losses / total;
  const noPct = noBreakout / total;

  const winLen = winPct * circumference;
  const lossLen = lossPct * circumference;
  const noLen = noPct * circumference;

  const winOffset = 0;
  const lossOffset = -winLen;
  const noOffset = -(winLen + lossLen);

  return (
    <div className="relative w-40 h-40 mx-auto">
      <svg viewBox="0 0 120 120" className="w-full h-full -rotate-90">
        {/* Win */}
        <circle
          cx="60" cy="60" r={radius}
          fill="none" stroke="#4ade80" strokeWidth="16"
          strokeDasharray={`${winLen} ${circumference - winLen}`}
          strokeDashoffset={winOffset}
        />
        {/* Loss */}
        <circle
          cx="60" cy="60" r={radius}
          fill="none" stroke="#f87171" strokeWidth="16"
          strokeDasharray={`${lossLen} ${circumference - lossLen}`}
          strokeDashoffset={lossOffset}
        />
        {/* No breakout */}
        <circle
          cx="60" cy="60" r={radius}
          fill="none" stroke="#4b5563" strokeWidth="16"
          strokeDasharray={`${noLen} ${circumference - noLen}`}
          strokeDashoffset={noOffset}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-2xl font-bold text-white">{Math.round(winPct * 100)}%</span>
        <span className="text-xs text-gray-500">win rate</span>
      </div>
    </div>
  );
}

export default function SummaryPanel({ summary, slDistance, tpDistance }: Props) {
  return (
    <div className="bg-gray-900/70 backdrop-blur-sm border border-gray-800/50 rounded-2xl p-6 space-y-6">
      {/* TP / SL badges */}
      <div className="flex justify-center gap-3 text-sm">
        <span className="bg-green-900/30 border border-green-800/40 px-4 py-1.5 rounded-lg text-green-400 font-medium">
          TP: {tpDistance} pts
        </span>
        <span className="bg-red-900/30 border border-red-800/40 px-4 py-1.5 rounded-lg text-red-400 font-medium">
          SL: {slDistance} pts
        </span>
      </div>

      {/* Donut + Stats */}
      <div className="flex flex-col sm:flex-row items-center gap-8">
        <DonutChart wins={summary.wins} losses={summary.losses} noBreakout={summary.no_breakout} />

        <div className="grid grid-cols-2 gap-3 flex-1 w-full">
          <StatCard label="Total days" value={summary.total_days} />
          <StatCard label="Wins" value={summary.wins} color="text-green-400" />
          <StatCard label="Losses" value={summary.losses} color="text-red-400" />
          <StatCard label="No breakout" value={summary.no_breakout} color="text-gray-500" />
          <StatCard
            label="Net points"
            value={summary.net_points}
            color={summary.net_points >= 0 ? "text-green-400" : "text-red-400"}
          />
          <StatCard
            label="Win rate"
            value={`${summary.win_rate}%`}
            color={summary.win_rate >= 50 ? "text-green-400" : "text-red-400"}
          />
        </div>
      </div>

      {/* Legend */}
      <div className="flex justify-center gap-6 text-xs text-gray-500">
        <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-green-400 inline-block" /> Wins</span>
        <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-red-400 inline-block" /> Losses</span>
        <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-gray-600 inline-block" /> No breakout</span>
      </div>
    </div>
  );
}

function StatCard({ label, value, color }: { label: string; value: string | number; color?: string }) {
  return (
    <div className="bg-gray-800/50 rounded-xl p-4">
      <p className="text-xs text-gray-500 mb-1">{label}</p>
      <p className={`text-xl font-bold ${color || "text-white"}`}>{value}</p>
    </div>
  );
}
